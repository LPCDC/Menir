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
import os
import jwt
import uuid
import hashlib
from dataclasses import dataclass, field

from aiohttp import web

from src.v3.core.logos import CommandPayload, MenirLogos
from src.v3.core.schemas.identity import TenantContext, locked_tenant_context
from src.v3.mcp_server import MenirMCPServer
from src.v3.skills.document_classifier_skill import DocumentClassifierSkill, DocumentClassification
from src.v3.core.persistence import NodePersistenceOrchestrator
from src.v3.core.schemas.base import Document, QuarantineItem, DocumentStatus

logger = logging.getLogger("MenirSynapse")


@dataclass(order=True)
class PrioritizedCommand:
    priority: int
    timestamp: float
    payload: CommandPayload = field(compare=False)


@web.middleware
async def cors_middleware(request, handler):
    if request.method == "OPTIONS":
        response = web.Response(status=200)
    else:
        try:
            response = await handler(request)
        except web.HTTPException as ex:
            response = ex
    
    # Check if headers exist before modifying
    if hasattr(response, 'headers'):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, PUT, DELETE, PATCH'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        
    return response

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
        self.app = web.Application(middlewares=[cors_middleware])
        
        async def handle_options(request):
            return web.Response(status=200)

        self.app.router.add_route('OPTIONS', '/{tail:.*}', handle_options)
        
        self.app.add_routes(
            [
                web.get("/status", self.handle_status_http),
                web.post("/auth/token", self.handle_auth_token_http),
                web.post("/command", self.handle_command_http),
                web.post("/mcp", self.mcp_server.handle_mcp_request),
                web.get("/api/v3/documents/quarantine", self.handle_get_quarantine),
                web.post("/api/v3/documents/{id}/retry", self.handle_retry_document),
                web.post("/api/export/cresus", self.handle_export_cresus),
                web.post("/api/v3/classify/document", self.handle_classify_document),
                web.get("/api/v3/quarantine/documents", self.handle_get_quarantine_documents),
                web.patch("/api/v3/quarantine/documents/{uid}/accept", self.handle_accept_quarantine_document),
                web.patch("/api/v3/quarantine/documents/{uid}/correct", self.handle_correct_quarantine_document),
            ]
        )
        
        # Telegram Bot Integration (SANTOS Tactical Entry)
        self.tg_bot = None
        self.tg_dp = None
        tg_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if tg_token:
            from aiogram import Bot, Dispatcher
            from aiogram.webhook.aiohttp_server import SimpleRequestHandler
            from aiogram.client.default import DefaultBotProperties
            
            self.tg_bot = Bot(token=tg_token, default=DefaultBotProperties(parse_mode="HTML"))
            self.tg_dp = Dispatcher()
            self._setup_telegram_handlers()
            
            webhook_handler = SimpleRequestHandler(dispatcher=self.tg_dp, bot=self.tg_bot)
            webhook_handler.register(self.app, path="/webhook/telegram")
            logger.info("📱 Webhook do Telegram registrado em /webhook/telegram")
            
            if os.getenv("TELEGRAM_LONG_POLLING") == "1":
                # Only for regression and local testing
                asyncio.create_task(self.tg_dp.start_polling(self.tg_bot))
                logger.info("⚡ Telegram Bot iniciado também em modo LONG POLLING para desenvolvimento.")
                
        self.active_hitls = {}    
        self.http_site = None
        self.socket_server = None

    async def _command_bus_consumer(self):
        """
        Consumer loop do CommandBus.
        Processa comandos enfileirados via HTTP/Socket em background.
        Sem este loop, comandos são validados, parseados (custando tokens)
        e descartados silenciosamente para sempre.
        """
        logger.info("🟢 CommandBus Consumer ativo.")
        while True:
            try:
                priority, cmd = await self.command_bus.get()
                logger.info(f"⚡ CommandBus: executando {cmd.payload.action} (prio={priority})")

                action = cmd.payload.action

                if action == "STATUS_REPORT":
                    # Resposta já enviada no handle_status_http.
                    # Aqui: opcionalmente logar ou persistir snapshot.
                    logger.info("📊 STATUS_REPORT processado.")

                elif action == "PAUSE_INGESTION":
                    await self.runner.pause_ingestion()
                    logger.warning("⏸️  Ingestion PAUSADA via CommandBus.")

                elif action == "RESUME_INGESTION":
                    await self.runner.resume_ingestion()
                    logger.info("▶️  Ingestion RESUMIDA via CommandBus.")

                elif action == "FLUSH_QUARANTINE":
                    await asyncio.to_thread(self.runner.flush_quarantine)
                    logger.info("🗑️  Quarentena liberada via CommandBus.")

                else:
                    logger.warning(f"CommandBus: ação desconhecida ignorada: {action}")

                self.command_bus.task_done()

            except asyncio.CancelledError:
                logger.info("🛑 CommandBus Consumer encerrado.")
                break
            except Exception:
                logger.exception("CommandBus Consumer: erro ao processar comando.")

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

        from typing import cast, Literal
        payload: CommandPayload = await self.logos.interpret_intent(
            raw_input, cast(Literal["CLI_LOCAL", "WEB_UI", "AI_ORACLE", "CRON"], origin), tenant_id=tenant_id
        )

        # Enqueue with strict priority
        priority = self._get_priority_weight(origin)
        cmd = PrioritizedCommand(priority=priority, timestamp=time.time(), payload=payload)

        await self.command_bus.put(cmd)
        logger.info(
            f"📥 [CommandBus] {origin} enviou {payload.action} para Tenant {tenant_id} (Prioridade: {priority})"
        )

        return self._format_response(payload)

    def _setup_telegram_handlers(self):
        from aiogram import types, F
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        from src.v3.skills.menir_capture import MenirCapture
        from src.v3.core.persistence import NodePersistenceOrchestrator
        
        async def _run_capture_task(chat_id: int, text: str, media_path: str, tenant_name: str, message_id: int):
            if not self.logos or not self.logos.intel:
                logger.error("❌ Telegram Logic Error: Logos/Intel offline during capture.")
                return

            with locked_tenant_context(tenant_name):
                try:
                    capture = MenirCapture(self.logos.intel, NodePersistenceOrchestrator())
                    res = await capture.ingest(text=text, current_tenant=tenant_name, media_path=media_path)
                    
                    if res and res.get("success"):
                        if res.get("hitl"):
                            hc = res["hitl"]
                            t_name = hc["target_name"]
                            hitl_id = str(uuid.uuid4())[:8]
                            self.active_hitls[hitl_id] = hc
                            
                            kb = InlineKeyboardMarkup(inline_keyboard=[
                                [
                                    InlineKeyboardButton(text="👍 SIM", callback_data=f"hitl:{hitl_id}:yes"),
                                    InlineKeyboardButton(text="👎 NÃO", callback_data=f"hitl:{hitl_id}:no")
                                ]
                            ])
                            if self.tg_bot:
                                await self.tg_bot.send_message(
                                    chat_id=chat_id,
                                    text=f"❓ Ambiguidade Detectada: Você está se referindo a '{t_name}'?",
                                    reply_markup=kb,
                                    reply_to_message_id=message_id
                                )
                        else:
                            if self.tg_bot:
                                await self.tg_bot.send_message(
                                    chat_id=chat_id, 
                                    text="✅ Entendido. Memória salva no grafo com sucesso.",
                                    reply_to_message_id=message_id
                                )
                    else:
                        if self.tg_bot:
                            await self.tg_bot.send_message(
                                chat_id=chat_id, 
                                text="✅ Entendido. Memória salva no grafo com sucesso.",
                                reply_to_message_id=message_id
                            )
                except Exception as e:
                    logger.error(f"Erro no processamento background Telegram: {e}")
                    if self.tg_bot:
                        await self.tg_bot.send_message(
                            chat_id=chat_id, 
                            text="❌ Ocorreu um problema técnico ao processar sua mensagem. Tente novamente mais tarde.",
                            reply_to_message_id=message_id
                        )
                finally:
                    if media_path and os.path.exists(media_path):
                        try:
                            os.remove(media_path)
                        except:
                            pass

        if not self.tg_dp:
            return

        @self.tg_dp.message(F.text)
        async def handle_tg_text(message: types.Message):
            tenant_name = os.getenv("MENIR_PERSONAL_TENANT_NAME", "PESSOAL")
            text = message.text or ""
            asyncio.create_task(_run_capture_task(message.chat.id, text, "", tenant_name, message.message_id))
            
        @self.tg_dp.message(F.photo)
        async def handle_tg_photo(message: types.Message):
            tenant_name = os.getenv("MENIR_PERSONAL_TENANT_NAME", "PESSOAL")
            caption = message.caption or "Analise esta imagem em busca de detalhes importantes."
            
            photo = message.photo[-1] if message.photo else None
            if not photo or not self.tg_bot:
                return

            file = await self.tg_bot.get_file(photo.file_id)
            os.makedirs("tmp_media", exist_ok=True)
            local_path = f"tmp_media/{photo.file_id}.jpg"
            await self.tg_bot.download_file(file.file_path, local_path)
            
            asyncio.create_task(_run_capture_task(message.chat.id, caption, local_path, tenant_name, message.message_id))
            
        @self.tg_dp.message(F.voice)
        async def handle_tg_voice(message: types.Message):
            tenant_name = os.getenv("MENIR_PERSONAL_TENANT_NAME", "PESSOAL")
            text = "Analise o áudio anexado para extrair entidades e insights e transcreva seu conteúdo principal caso seja necessário para contexto."
            
            voice = message.voice
            if not voice or not self.tg_bot: return
            
            file = await self.tg_bot.get_file(voice.file_id)
            os.makedirs("tmp_media", exist_ok=True)
            local_path = f"tmp_media/{voice.file_id}.ogg"
            await self.tg_bot.download_file(file.file_path, local_path)
            
            
            asyncio.create_task(_run_capture_task(message.chat.id, text, local_path, tenant_name, message.message_id))
            
        @self.tg_dp.callback_query(F.data.startswith('hitl:'))
        async def handle_tg_hitl_callback(callback: types.CallbackQuery):
            if not callback.data:
                return
            parts = callback.data.split(':')
            if len(parts) != 3:
                return
            hitl_id = parts[1]
            answer = parts[2]
            
            hc = self.active_hitls.get(hitl_id)
            if not hc:
                if callback.message and hasattr(callback.message, "edit_text"):
                    await callback.message.edit_text("❌ Contexto expirado ou já resolvido.")
                return
                
            tenant_name = os.getenv("MENIR_PERSONAL_TENANT_NAME", "PESSOAL")
            
            with locked_tenant_context(tenant_name):
                try:
                    capture = MenirCapture(self.logos.intel if self.logos else None, NodePersistenceOrchestrator())
                    approved = (answer == 'yes')
                    await capture.resolve_hitl(hc, approved, tenant_name)
                    
                    if approved:
                        if callback.message and hasattr(callback.message, "edit_text"):
                            await callback.message.edit_text(f"✅ Confirmado (SIM). Memória '{hc.get('target_name')}' amarrada ao grafo.")
                    else:
                        if callback.message and hasattr(callback.message, "edit_text"):
                            await callback.message.edit_text("✅ Negado (NÃO). Uma nova entidade autônoma foi criada no grafo.")
                    
                    del self.active_hitls[hitl_id]
                except Exception as e:
                    logger.error(f"Erro no HITL telegram callback: {e}")
                    await callback.answer("❌ Erro ao processar resolução.", show_alert=True)
            
            await callback.answer()

    # --- HTTP INTERFACE (WEB_UI / AI) ---
    async def handle_auth_token_http(self, request):
        data = await request.json()
        username = data.get("username", "")
        password = data.get("password", "")

        beco_user = os.getenv("MENIR_MOCK_USER_BECO")
        beco_pass = os.getenv("MENIR_MOCK_PASS_BECO")
        santos_user = os.getenv("MENIR_MOCK_USER_SANTOS")
        santos_pass = os.getenv("MENIR_MOCK_PASS_SANTOS")

        if beco_user and username == beco_user and password == beco_pass:
            return web.json_response({"token": "BECO_ENTERPRISE_JWT"})
        elif santos_user and username == santos_user and password == santos_pass:
            return web.json_response({"token": "SANTOS_LIFE_JWT"})
        
        return web.json_response({"error": "Unauthorized"}, status=401)

    async def handle_status_http(self, request):
        """
        Endpoint de status. Guard explícito para concurrency_limit
        que após v2 é uma @property lazy — não um Semaphore direto.
        """
        try:
            limit = self.runner.concurrency_limit._value
        except Exception:
            limit = "Unknown"

        try:
            is_healthy = await asyncio.to_thread(self.runner.ontology_manager.check_system_health)
            degraded = not is_healthy
        except Exception:
            degraded = True

        status_text = "DEGRADED" if degraded else "ONLINE"

        return web.json_response({
            "status": status_text,
            "concurrency_slots_available": limit,
            "command_queue_size": self.command_bus.qsize(),
            "degraded": degraded,
        })

    async def handle_command_http(self, request):
        auth_header = request.headers.get("Authorization", "")
        # Cryptographic Namespace Routing (Context Isolation)
        token = auth_header.replace("Bearer ", "").strip()
        jwt_secret = os.getenv("MENIR_JWT_SECRET")
        if not jwt_secret:
            logger.error("Vazamento de segurança evitado: MENIR_JWT_SECRET não configurado! Isolation lock active.")
            return web.json_response({"error": "System Configuration Error"}, status=500)
        target_tenant = "BECO"
        
        try:
            if token:
                payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
                target_tenant = payload.get("tenant_id", "BECO")
        except jwt.PyJWTError:
            strict_auth = os.getenv("MENIR_STRICT_AUTH", "false").lower() == "true"
            if strict_auth:
                 return web.json_response({"error": "Invalid JWT Token. Isolation lock active."}, status=401)
            else:
                 logger.warning("Falha de validação JWT no CommandBus. Assumindo BECO. (STRICT_AUTH=false)")
                 if "SANTOS" in token:
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

    async def handle_get_quarantine(self, request):
        """Standard GET for Quarantine nodes (v1 compatible)"""
        target_tenant = await self._get_tenant_from_request(request)
        with locked_tenant_context(target_tenant):
            with self.runner.ontology_manager.driver.session() as session:
                query = f"MATCH (d:QuarantineItem:`{target_tenant}` {{status: 'PENDING'}}) " \
                        "RETURN d.uid AS id, d.name AS name, d.file_hash AS file_hash, " \
                        "d.quarantine_reason AS reason, d.quarantined_at AS date, " \
                        "d.trust_score AS trust_score, d.routing_decision AS routing_decision"
                result = session.run(query)
                data = [record.data() for record in result.all()]
                return web.json_response(data)

    async def handle_retry_document(self, request):
        doc_id = request.match_info['id']
        data = await request.json()
        target_tenant = TenantContext.get() or "BECO"
        safe_tenant = target_tenant.replace("`", "")
        
        action = data.get("action", "reinject")
        corrected_fields = data.get("corrected_fields", {})
        
        if action == "reject":
            query_update = f"""
            MATCH (d:Document:`{safe_tenant}` {{uid: $uid}})
            SET d.status = 'REJECTED',
                d.correction_by = 'human',
                d.correction_at = datetime()
            RETURN d
            """
        else: # reinject
            # Add corrected_json to be picked up by the pipeline
            corrected_json = json.dumps(corrected_fields) if corrected_fields else "{}"
            query_update = f"""
            MATCH (d:Document:`{safe_tenant}` {{uid: $uid}})
            SET d.status = 'PENDING',
                d.human_feedback = $feedback,
                d.correction_by = 'human',
                d.correction_at = datetime()
            RETURN d
            """
            
        def _update():
            with self.runner.ontology_manager.driver.session() as s:
                params = {"uid": doc_id}
                if action != "reject":
                    params["feedback"] = corrected_json
                res = s.run(query_update, **params).single()
                return dict(res["d"]) if res else None
                
        doc = await asyncio.to_thread(_update)
        if not doc:
             return web.json_response({"error": "No document found"}, status=404)
             
        return web.json_response({"success": True, "message": "Document marked as PENDING and flagged for retry."})

    async def handle_export_cresus(self, request):
        target_tenant = TenantContext.get() or "BECO"
        
        try:
            from src.v3.core.cresus_exporter import CresusExporter
            exporter = CresusExporter(self.runner.ontology_manager)
            
            export_path = await exporter.export_reconciled(tenant=target_tenant)
            if not export_path:
                return web.Response(status=204)
                
            return web.json_response({"success": True, "file_path": export_path})
        except Exception as e:
            logger.exception("Cresus Export Failed")
            return web.json_response({"error": str(e)}, status=500)


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

    async def handle_classify_document(self, request):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "").strip()
        jwt_secret = os.getenv("MENIR_JWT_SECRET")
        target_tenant = "BECO"
        
        try:
            if token and jwt_secret:
                payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
                target_tenant = payload.get("tenant_id", "BECO")
        except jwt.PyJWTError:
             # Fallback logic mirroring handle_command_http
             if os.getenv("MENIR_STRICT_AUTH", "false").lower() == "true":
                 return web.json_response({"error": "Unauthorized"}, status=401)
             if "SANTOS" in token:
                 target_tenant = "SANTOS"

        reader = await request.multipart()
        field = await reader.next()
        if not field or field.name != 'file':
            return web.json_response({"error": "Missing 'file' field"}, status=400)

        filename = field.filename or "uploaded_document.pdf"
        os.makedirs("tmp_uploads", exist_ok=True)
        file_path = os.path.join("tmp_uploads", f"{uuid.uuid4()}_{filename}")
        
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "wb") as f:
            while True:
                chunk = await field.read_chunk()
                if not chunk:
                    break
                f.write(chunk)
                sha256_hash.update(chunk)
        
        file_sha = sha256_hash.hexdigest()

        try:
            classifier = DocumentClassifierSkill(self.logos.intel)
            classification, trust_score, routing_target = await classifier.classify_document(file_path)
            
            # TrustScore Logic (Task 8)
            is_quarantine = routing_target == "QUARANTINE"
            persisted_uid = None
            
            with locked_tenant_context(target_tenant):
                orchestrator = NodePersistenceOrchestrator()
                with self.runner.ontology_manager.driver.session() as session:
                    if is_quarantine:
                        node = QuarantineItem(
                            uid=str(uuid.uuid4()),
                            project=target_tenant,
                            name=filename,
                            file_hash=file_sha,
                            reason="LOW_CONFIDENCE",
                            quarantined_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            document_type=classification.document_type,
                            confidence=classification.confidence,
                            trust_score=trust_score,
                            routing_decision=routing_target,
                            language=classification.language,
                            origin="UPLOAD"
                        )
                    else:
                        node = Document(
                            uid=str(uuid.uuid4()),
                            project=target_tenant,
                            sha256=file_sha,
                            name=filename,
                            source=f"Upload via synapse.py",
                            origin="UPLOAD",
                            status=DocumentStatus.PENDING
                        )
                        node.metadata = {
                            "suggested_client": classification.suggested_client_name,
                            "document_type": classification.document_type,
                            "confidence": classification.confidence,
                            "language": classification.language
                        }
                    
                    persisted_uid = await orchestrator.persist(node, session)

            return web.json_response({
                "uid": persisted_uid,
                "document_type": classification.document_type,
                "suggested_client_name": classification.suggested_client_name,
                "confidence": classification.confidence,
                "language": classification.language,
                "path_to_quarantine": is_quarantine
            })
            
        except Exception as e:
            logger.exception(f"Erro ao classificar documento {filename}")
            return web.json_response({"error": str(e)}, status=500)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    async def _get_tenant_from_request(self, request):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "").strip()
        jwt_secret = os.getenv("MENIR_JWT_SECRET")
        target_tenant = "BECO"
        try:
            if token and jwt_secret:
                payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
                target_tenant = payload.get("tenant_id", "BECO")
        except jwt.PyJWTError:
             if os.getenv("MENIR_STRICT_AUTH", "false").lower() == "true":
                 raise web.HTTPUnauthorized()
             if "SANTOS" in token:
                 target_tenant = "SANTOS"
        return target_tenant

    async def handle_get_quarantine_documents(self, request):
        """GET list of nodes in quarentena for this tenant."""
        target_tenant = await self._get_tenant_from_request(request)
        with locked_tenant_context(target_tenant):
            with self.runner.ontology_manager.driver.session() as session:
                query = f"MATCH (q:QuarantineItem:`{target_tenant}` {{status: 'PENDING'}}) " \
                        "RETURN q { .*, date: q.quarantined_at } AS q"
                result = session.run(query)
                items = [record.data()["q"] for record in result.all()]
                return web.json_response(items)

    async def handle_accept_quarantine_document(self, request):
        uid = request.match_info.get("uid")
        try:
            target_tenant = await self._get_tenant_from_request(request)
            with locked_tenant_context(target_tenant):
                orchestrator = NodePersistenceOrchestrator()
                with self.runner.ontology_manager.driver.session() as session:
                    # 1. Fetch item
                    q_fetch = f"MATCH (q:QuarantineItem:`{target_tenant}` {{uid: $uid}}) RETURN q"
                    res = session.run(q_fetch, uid=uid).single()
                    if not res:
                        return web.json_response({"error": "NotFound"}, status=404)
                    
                    q_data = res.data()["q"]
                    
                    # 2. Map to Document
                    new_doc = Document(
                        uid=str(uuid.uuid4()),
                        project=target_tenant,
                        sha256=q_data["file_hash"],
                        name=q_data["name"],
                        source=f"Promoted from quarantine {uid}",
                        origin="UPLOAD",
                        status=DocumentStatus.PENDING
                    )
                    new_doc.metadata = {
                        "suggested_client": q_data.get("suggested_client"),
                        "document_type": q_data.get("document_type"),
                        "confidence": q_data.get("confidence"),
                        "language": q_data.get("language")
                    }
                    
                    # 3. Persist
                    persisted_uid = await orchestrator.persist(new_doc, session)
                    
                    # 4. Mark Accepted
                    q_mark = f"MATCH (q:QuarantineItem:`{target_tenant}` {{uid: $uid}}) SET q.status = 'ACCEPTED'"
                    session.run(q_mark, uid=uid)
                    
            return web.json_response({"status": "ACCEPTED", "promoted_uid": persisted_uid})
        except Exception as e:
            logger.exception(f"Erro ao aceitar documento {uid}")
            return web.json_response({"error": str(e)}, status=500)

    async def handle_correct_quarantine_document(self, request):
        uid = request.match_info.get("uid")
        try:
            body = await request.json()
            corrected_client = body.get("client_name")
            if not corrected_client:
                 return web.json_response({"error": "Missing client_name"}, status=400)

            target_tenant = await self._get_tenant_from_request(request)
            with locked_tenant_context(target_tenant):
                orchestrator = NodePersistenceOrchestrator()
                with self.runner.ontology_manager.driver.session() as session:
                    # 1. Fetch item
                    q_fetch = f"MATCH (q:QuarantineItem:`{target_tenant}` {{uid: $uid}}) RETURN q"
                    res = session.run(q_fetch, uid=uid).single()
                    if not res:
                        return web.json_response({"error": "NotFound"}, status=404)
                    
                    q_data = res.data()["q"]
                    
                    # 2. Map to Document with correction
                    new_doc = Document(
                        uid=str(uuid.uuid4()),
                        project=target_tenant,
                        sha256=q_data["file_hash"],
                        name=q_data["name"],
                        source=f"Corrected from quarantine {uid}",
                        origin="UPLOAD",
                        status=DocumentStatus.PENDING
                    )
                    new_doc.metadata = {
                        "suggested_client": corrected_client, # OVERRIDDEN
                        "document_type": q_data.get("document_type"),
                        "confidence": 1.0, # Now high trust because human corrected it
                        "language": q_data.get("language")
                    }
                    
                    # 3. Persist
                    persisted_uid = await orchestrator.persist(new_doc, session)
                    
                    # 4. Mark Accepted (Fixed/Corrected)
                    q_mark = f"MATCH (q:QuarantineItem:`{target_tenant}` {{uid: $uid}}) SET q.status = 'CORRECTED'"
                    session.run(q_mark, uid=uid)
                    
            return web.json_response({"status": "CORRECTED", "promoted_uid": persisted_uid})
        except Exception as e:
            logger.exception(f"Erro ao corrigir documento {uid}")
            return web.json_response({"error": str(e)}, status=500)
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
