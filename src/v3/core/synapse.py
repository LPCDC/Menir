"""
Menir Core V5.1 - Control Plane (MenirSynapse) & Command Mesh
A Multi-Input Command Bus. Listens simultaneously on an HTTP port (for UI/AI)
and a raw TCP Socket (for CLI). It runs NLP prompts via MenirLogos and
queues executions in a globally ordered Priority Queue to protect the Runner.
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field

from aiohttp import web

from src.v3.core.logos import CommandPayload, MenirLogos
from src.v3.core.schemas.identity import TenantContext, locked_tenant_context
from src.v3.mcp_server import MenirMCPServer

logger = logging.getLogger("MenirSynapse")


@dataclass(order=True)
class PrioritizedCommand:
    priority: int
    timestamp: float
    payload: CommandPayload = field(compare=False)


class MenirSynapse:
    def __init__(self, runner, intel_instance=None):
        """
        Injects Runner reference for introspection and MenirIntel for NLP parsing.
        """
        self.runner = runner
        self.logos = MenirLogos(intel_instance) if intel_instance else None

        # Concurrency Shield: Per-Tenant Isolation (MAX_CONCURRENT_COMMANDS = 50)
        self.tenant_semaphores = {"BECO": asyncio.Semaphore(50), "SANTOS": asyncio.Semaphore(50)}

        # Primary Async Priority Queue
        from typing import Any
        self.command_bus: asyncio.PriorityQueue[Any] = asyncio.PriorityQueue()

        # Secondary Interface: WebMCP Autonomous Agents
        self.mcp_server = MenirMCPServer(self.runner)

        # AIOHTTP Application
        self.app = web.Application()
        self.app.add_routes(
            [
                web.get("/status", self.handle_status_http),
                web.post("/auth/token", self.handle_auth_token_http),
                web.post("/command", self.handle_command_http),
                web.post("/mcp", self.mcp_server.handle_mcp_request),
            ]
        )
        self.http_site = None
        self.socket_server = None

    def _get_semaphore(self, tenant_id: str) -> asyncio.Semaphore:
        """Retrieves or creates the Concurrency Shield for the specific Tenant."""
        if tenant_id not in self.tenant_semaphores:
            self.tenant_semaphores[tenant_id] = asyncio.Semaphore(50)
        return self.tenant_semaphores[tenant_id]

    def _get_priority_weight(self, origin: str) -> int:
        """
        Defines priority weighting.
        0 = CLI_LOCAL (Immediate interruption)
        1 = AI_ORACLE (System Supervisor)
        2 = WEB_UI (Standard prioritization)
        """
        mapping = {"CLI_LOCAL": 0, "AI_ORACLE": 1, "WEB_UI": 2, "CRON": 3}
        return mapping.get(origin, 99)

    def _format_response(self, payload: CommandPayload) -> str:
        """Sintetiza a resposta baseada em quem perguntou."""
        if payload.origin == "CLI_LOCAL":
            # Response formatting for CLI_LOCAL
            return f"\n[CLI ACK] {payload.command_id}\nACTION: {payload.action}\nCONFIDENCE: {payload.confidence_score * 100}%\nRATIONALE: {payload.rationale}\nSTATUS: Enqueued with Priority {self._get_priority_weight(payload.origin)}\n"
        elif payload.origin == "AI_ORACLE":
            # Optimized Hash response
            return f"ACK_HASH:{payload.command_id}|{payload.action}"
        else:
            # Canonical JSON response for frontends
            return json.dumps(payload.model_dump())

    async def _queue_command(self, raw_input: str, origin: str) -> str:
        """
        Core NLP intent to Bus enqueueing.
        Relies on IoC TenantContext for Galvanic Isolation.
        """
        if not self.logos:
            return "ERROR: MenirLogos offline (No MenirIntel instance provided)."

        tenant_id = TenantContext.get()
        if not tenant_id:
            logger.error("❌ CRITICAL: No TenantContext active during command queuing.")
            return "ERROR: Internal Security Breach (No Tenant Context)."

        payload: CommandPayload = await self.logos.interpret_intent(
            raw_input, origin, tenant_id=tenant_id
        )

        # Enqueue with strict priority
        priority = self._get_priority_weight(origin)
        cmd = PrioritizedCommand(priority=priority, timestamp=time.time(), payload=payload)

        await self.command_bus.put(cmd)
        logger.info(
            f"📥 [CommandBus] {origin} enviou {payload.action} para Tenant {tenant_id} (Prioridade: {priority})"
        )

        return self._format_response(payload)

    # --- HTTP INTERFACE (WEB_UI / AI) ---
    async def handle_auth_token_http(self, request):
        data = await request.json()
        username = data.get("username", "")
        password = data.get("password", "")

        # Mock authentication mapping for Galvanic Isolation Demonstration
        if username == "beco" and password == "admin":
            return web.json_response({"token": "BECO_ENTERPRISE_JWT"})
        elif username == "santos" and password == "admin":
            return web.json_response({"token": "SANTOS_LIFE_JWT"})
        
        return web.json_response({"error": "Unauthorized"}, status=401)

    async def handle_status_http(self, request):
        limit = (
            self.runner.concurrency_limit._value
            if hasattr(self.runner, "concurrency_limit")
            else "Unknown"
        )
        return web.json_response(
            {
                "status": "ONLINE",
                "concurrency_slots": limit,
                "command_queue_size": self.command_bus.qsize(),
            }
        )

    async def handle_command_http(self, request):
        auth_header = request.headers.get("Authorization", "")
        # Cryptographic Namespace Routing (Context Isolation)
        target_tenant = "BECO"  # Core Fiduciary Defaults
        if auth_header.endswith("SANTOS_LIFE_JWT"):
            target_tenant = "SANTOS"

        data = await request.json()
        raw_intent = data.get("intent", "")
        origin = data.get("origin", "WEB_UI")

        with locked_tenant_context(target_tenant):
            try:
                async with self._get_semaphore(target_tenant):
                    response_str = await asyncio.wait_for(
                        self._queue_command(raw_input=raw_intent, origin=origin), timeout=30.0
                    )
            except TimeoutError:
                logger.error(
                    f"⏱️ EXECUTION TIMEOUT: Payload from {origin} to {target_tenant} breached 30s TTL."
                )
                return web.Response(
                    status=504,
                    text=json.dumps(
                        {"error": "Timeout", "message": "Command execution exceeded 30s TTL."}
                    ),
                    content_type="application/json",
                )

        if origin == "WEB_UI":
            return web.Response(text=response_str, content_type="application/json")
        else:
            return web.Response(text=response_str)

    # --- SOCKET INTERFACE (CLI_LOCAL) ---
    async def handle_socket_client(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        """Escuta o terminal local do NAS via TCP Raw Socket"""
        addr = writer.get_extra_info("peername")
        logger.info(f"🔌 CLI Conectada a partir de {addr}")

        writer.write(b"Menir V5.1 Root CLI. Awaiting Command: \n")
        await writer.drain()

        while True:
            data = await reader.readline()
            if not data:
                break

            raw_intent = data.decode("utf-8").strip()
            if raw_intent.lower() in ["exit", "quit"]:
                break

            if raw_intent:
                with locked_tenant_context("BECO"):
                    try:
                        async with self._get_semaphore("BECO"):
                            response = await asyncio.wait_for(
                                self._queue_command(raw_intent, origin="CLI_LOCAL"), timeout=30.0
                            )
                        writer.write(response.encode("utf-8"))
                    except TimeoutError:
                        logger.error("⏱️ EXECUTION TIMEOUT: CLI_LOCAL breached 30s TTL.")
                        writer.write(b"ERROR: Execution Timeout (30s). Command aborted.\n")
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
        self.http_site = web.TCPSite(runner_app, "0.0.0.0", http_port)
        await self.http_site.start()
        logger.info(f"🌐 Synapse HTTP Mesh rodando em 0.0.0.0:{http_port}")

        # 2. Boot Raw Socket (CLI)
        self.socket_server = await asyncio.start_server(
            self.handle_socket_client, "127.0.0.1", socket_port
        )
        logger.info(f"💻 Synapse CLI Socket rodando em 127.0.0.1:{socket_port}")
