"""
Menir Core V5.1 - Control Plane (MenirSynapse) & Command Mesh
A Multi-Input Command Bus. Listens simultaneously on an HTTP port (for UI/AI) 
and a raw TCP Socket (for CLI). It runs NLP prompts via MenirLogos and
queues executions in a globally ordered Priority Queue to protect the Runner.
"""
import time
import json
import logging
import asyncio
from typing import Optional
from dataclasses import dataclass, field
from aiohttp import web

from src.v3.core.logos import MenirLogos, CommandPayload

logger = logging.getLogger("MenirSynapse")

@dataclass(order=True)
class PrioritizedCommand:
    priority: int
    timestamp: float
    payload: CommandPayload = field(compare=False)

class MenirSynapse:
    def __init__(self, runner, intel_instance=None):
        """
        Injeta a referência do Runner para introspecção e do Intel para o Córtex NLP.
        """
        self.runner = runner
        self.logos = MenirLogos(intel_instance) if intel_instance else None
        
        # O Fio Condutor: Queue Assíncrona Prioritizada
        self.command_bus = asyncio.PriorityQueue()
        
        # AIOHTTP Application
        self.app = web.Application()
        self.app.add_routes([
            web.get('/status', self.handle_status_http),
            web.post('/command', self.handle_command_http)
        ])
        self.http_site = None
        self.socket_server = None

    def _get_priority_weight(self, origin: str) -> int:
        """
        Hierarquia Absoluta.
        0 = CLI_LOCAL (Root NAS, Interrupção imediata)
        1 = AI_ORACLE (Supervisor de Sistema)
        2 = WEB_UI (Contador Fiduciário - Espera na fila)
        """
        mapping = {"CLI_LOCAL": 0, "AI_ORACLE": 1, "WEB_UI": 2, "CRON": 3}
        return mapping.get(origin, 99)

    def _format_response(self, payload: CommandPayload) -> str:
        """Sintetiza a resposta baseada em quem perguntou."""
        if payload.origin == "CLI_LOCAL":
            # Retorno para o Bash/SSH do Administrador Pano
            return f"\n[CLI ACK] {payload.command_id}\nACTION: {payload.action}\nCONFIDENCE: {payload.confidence_score*100}%\nRATIONALE: {payload.rationale}\nSTATUS: Enqueued with Priority {self._get_priority_weight(payload.origin)}\n"
        elif payload.origin == "AI_ORACLE":
            # Retorno otimizado (Hash) para Agentes API
            return f"ACK_HASH:{payload.command_id}|{payload.action}"
        else:
            # Retorno canônico JSON para FrontEnd / WEB_UI
            return json.dumps(payload.model_dump())

    async def _queue_command(self, raw_input: str, origin: str, tenant_id: str = "BECO") -> str:
        """
        O Núcleo de Processamento de Intenção Logos -> Bus.
        """
        if not self.logos:
            return "ERROR: Logos Cortex offline (No MenirIntel instance provided)."
            
        payload: CommandPayload = await self.logos.interpret_intent(raw_input, origin, tenant_id=tenant_id)
        
        # Encapsula na matriz de prioridade e despacha para o event_loop
        priority = self._get_priority_weight(origin)
        cmd = PrioritizedCommand(priority=priority, timestamp=time.time(), payload=payload)
        
        await self.command_bus.put(cmd)
        logger.info(f"📥 [CommandBus] {origin} enviou {payload.action} para Tenant {tenant_id} (Prioridade: {priority})")
        
        return self._format_response(payload)

    # --- HTTP INTERFACE (WEB_UI / AI) ---
    async def handle_status_http(self, request):
        limit = self.runner.concurrency_limit._value if hasattr(self.runner, 'concurrency_limit') else "Unknown"
        return web.json_response({
            "status": "ONLINE",
            "concurrency_slots": limit,
            "command_queue_size": self.command_bus.qsize()
        })

    async def handle_command_http(self, request):
        auth_header = request.headers.get('Authorization', '')
        # Cryptographic Namespace Routing (Context Isolation)
        tenant_context = "BECO" # Core Fiduciary Defaults
        if auth_header.endswith("SANTOS_LIFE_JWT"):
            tenant_context = "SANTOS"
            
        data = await request.json()
        raw_intent = data.get("intent", "")
        origin = data.get("origin", "WEB_UI")
        
        response_str = await self._queue_command(raw_intent, origin, tenant_id=tenant_context)
        
        if origin == "WEB_UI":
            return web.Response(text=response_str, content_type='application/json')
        else:
            return web.Response(text=response_str)

    # --- SOCKET INTERFACE (CLI_LOCAL) ---
    async def handle_socket_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Escuta o terminal local do NAS via TCP Raw Socket"""
        addr = writer.get_extra_info('peername')
        logger.info(f"🔌 CLI Conectada a partir de {addr}")
        
        writer.write(b"Menir V5.1 Root CLI. Awaiting Command: \n")
        await writer.drain()
        
        while True:
            data = await reader.readline()
            if not data:
                break
                
            raw_intent = data.decode('utf-8').strip()
            if raw_intent.lower() in ['exit', 'quit']:
                break
                
            if raw_intent:
                response = await self._queue_command(raw_intent, origin="CLI_LOCAL")
                writer.write(response.encode('utf-8'))
                await writer.drain()
                
        logger.info("🔌 CLI Desconectada.")
        writer.close()
        await writer.wait_closed()

    # --- SERVER SPAWNERS ---
    async def start_servers(self, http_port=8080, socket_port=8081):
        """Inicializa as frentes Bimodais e retorna controle ao Event Loop"""
        # 1. Boot HTTP
        runner_app = web.AppRunner(self.app)
        await runner_app.setup()
        self.http_site = web.TCPSite(runner_app, '0.0.0.0', http_port)
        await self.http_site.start()
        logger.info(f"🌐 Synapse HTTP Mesh rodando em 0.0.0.0:{http_port}")
        
        # 2. Boot Raw Socket (CLI)
        self.socket_server = await asyncio.start_server(
            self.handle_socket_client, '127.0.0.1', socket_port
        )
        logger.info(f"💻 Synapse CLI Socket rodando em 127.0.0.1:{socket_port}")
