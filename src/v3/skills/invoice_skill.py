"""
Menir Core V5.1 - Invoice Processing Skill
Extracts accounting data using bimodal NLP/Vision routing and strict Pydantic mathematical validation.
"""

import logging
import os
from typing import Any

from src.v3.core.menir_runner import SkillResult
from src.v3.core.compressor import PayloadCompressor
from google.genai import types as genai_types
from src.v3.core.schemas import InvoiceData
from src.v3.menir_intel import MenirIntel
from src.v3.meta_cognition import MenirOntologyManager

logger = logging.getLogger("InvoiceSkill")

# --- INVOICE SKILL CLASS ---


class InvoiceSkill:
    """
    Skill de processamento de faturas (Swiss Crésus ERP Pipeline).
    """

    def __init__(self, intel: MenirIntel, ontology_manager: MenirOntologyManager):
        self.intel = intel
        self.ontology_manager = ontology_manager

    async def _resolve_vendor_zefix(self, ide_number: str | None, name: str, tenant: str) -> tuple[bool, str]:
        import aiohttp
        import asyncio
        from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

        safe_tenant = tenant.replace("`", "")

        cache_query = f"""
        MATCH (v:Vendor:`{safe_tenant}`)
        WHERE (v.name = $name OR (v.ide_number = $ide AND $ide IS NOT NULL))
          AND v.zefix_queried_at > datetime() - duration('P30D')
        RETURN v.zefix_match AS zefix_match, coalesce(v.zefix_status, 'UNKNOWN') AS zefix_status
        LIMIT 1
        """
        def _check_db():
            with self.ontology_manager.driver.session() as s:
                return s.run(cache_query, ide=ide_number, name=name).single()
                
        cached = await asyncio.to_thread(_check_db)
        if cached:
            return cached["zefix_match"], cached["zefix_status"]

        zefix_match = False
        zefix_status = "NO_MATCH"
        
        class ZefixRateLimitError(Exception): pass

        zefix_url = os.getenv("MENIR_ZEFIX_URL")
        if not zefix_url:
            logger.error("Zefix API URL não configurada no ambiente.")
            return False, "SYSTEM_ERROR"

        @retry(
            wait=wait_exponential(multiplier=1, min=1, max=4),
            stop=stop_after_attempt(3),
            retry=retry_if_exception_type((ZefixRateLimitError, asyncio.TimeoutError, aiohttp.ClientError))
        )
        async def _call_zefix():
            nonlocal zefix_match, zefix_status
            async with aiohttp.ClientSession() as session:
                payload = {"uid": ide_number} if ide_number else {"name": name}
                async with session.post(zefix_url, json=payload, timeout=10) as resp:
                    if resp.status == 429:
                        raise ZefixRateLimitError("Rate limited")
                    if resp.status == 200:
                        data = await resp.json()
                        if data and isinstance(data, list) and len(data) > 0:
                            zefix_match = True
                            zefix_status = "MATCH"
                        else:
                            zefix_match = False
                            zefix_status = "NO_MATCH"
                    else:
                        resp.raise_for_status()

        try:
            await _call_zefix()
        except Exception as e:
            logger.warning(f"Zefix API failed after retries: {e}")
            zefix_match = False
            zefix_status = "RATE_LIMITED"
        
        persist_query = f"""
        MERGE (v:Vendor:`{safe_tenant}` {{name: $name}})
        SET v.ide_number = $ide,
            v.zefix_match = $zefix_match,
            v.zefix_status = $zefix_status,
            v.zefix_queried_at = datetime(),
            v.project = $safe_tenant
        """
        def _save_vendor():
            with self.ontology_manager.driver.session() as s:
                with s.begin_transaction() as tx:
                    tx.run(persist_query, name=name, ide=ide_number, zefix_match=zefix_match, zefix_status=zefix_status, safe_tenant=safe_tenant)
        try:
            await asyncio.to_thread(_save_vendor)
        except Exception as e:
            logger.error(f"Failed to persist Vendor cache: {e}")

        return zefix_match, zefix_status

    async def process_document(self, file_path: str) -> SkillResult:
        import asyncio
        import base64
        import hashlib
        import json

        from pydantic import ValidationError
        from pypdf import PdfReader

        PRODUCTION_READY = os.getenv("MENIR_INVOICE_LIVE", "false").lower() == "true"
        if not PRODUCTION_READY:
            logger.warning(
                "⚠️ InvoiceSkill em modo STUB. Defina MENIR_INVOICE_LIVE=true para ativar."
            )
            return SkillResult(
                success=False,
                nodes_and_edges=[],
                message="STUB_MODE: MENIR_INVOICE_LIVE não ativado.",
            )

        logger.info(f"🧾 Iniciando processamento de Invoice: {file_path}")

        try:
            with open(file_path, "rb") as f:
                file_bytes = f.read()
                file_hash = hashlib.sha256(file_bytes).hexdigest()
        except Exception as e:
            return SkillResult(success=False, nodes_and_edges=[], message=str(e))

        try:
            from datetime import date
            from src.v3.core.schemas.identity import TenantContext
            
            tenant = TenantContext.get() or "BECO"
            placeholder_date = date.today().isoformat()
            active_rules = self.ontology_manager.get_tenant_active_context(tenant, placeholder_date)

            EXTRACTION_PROMPT = """Você é um auditor financeiro suíço. Extraia os dados desta fatura.
Retorne SOMENTE JSON válido, sem texto adicional, sem blocos markdown.
Schema obrigatório:
{
  "vendor_name": "string",
  "doc_type": "string",
  "ide_number": "string ou null",
  "avs_number": "string ou null",
  "language": "fr, de, it, rm, en, pt, ou sq",
  "vendor_iban": "string ou null",
  "currency": "CHF ou EUR",
  "issue_date": "YYYY-MM-DD",
  "subtotal": 0.0,
  "tip_or_unregulated_amount": 0.0,
  "total_amount": 0.0,
  "items": [{"description": "string", "gross_amount": 0.0, "tva_rate_applied": null}],
  "requires_manual_justification": false
}"""

            from typing import Any
            from src.v3.core.pdf_parser import classify_pdf_type, PdfType

            api_contents: list[Any] = []
            img_path = None

            if file_path.lower().endswith(".pdf"):
                logger.info("PDF Classifier: Detectando tipo físico da fatura.")
                try:
                    pdf_type, parts = classify_pdf_type(file_path)
                    logger.info(f"PDF classificado como: {pdf_type.value}")
                    if pdf_type == PdfType.SCANNED:
                        # parts are list of PIL Images
                        prompt = EXTRACTION_PROMPT
                        api_contents.append(prompt)
                        api_contents.extend(parts)
                    else:
                        # parts is a list with one string element (DIGITAL or HYBRID with reorder prompt)
                        prompt = EXTRACTION_PROMPT + "\n\nTEXTO DA FATURA:\n" + "".join(parts)
                        api_contents.append(prompt)
                except Exception as e:
                    logger.warning(f"Classificador PDF falhou ({e}). Tentando fallback SLOW_LANE antigo.")
                    lane = "SLOW_LANE"
            elif file_path.lower().endswith(".txt"):
                logger.info("⚡ FAST_LANE_TXT: Lendo arquivo texto nativo (Fixture).")
                with open(file_path, "r", encoding="utf-8") as f:
                    raw_text = f.read()
                prompt = EXTRACTION_PROMPT + "\n\nTEXTO DA FATURA:\n" + raw_text
                api_contents.append(prompt)
            else:
                lane = "SLOW_LANE"

            # OSL: Se a variável lane for criada por exception no classificador ou por não ser pdf/txt:
            if locals().get("lane") == "SLOW_LANE":
                compressor = PayloadCompressor()
                logger.info("🐢 SLOW_LANE: Redimensionando e enviando arquivo para Gemini Vision.")
                try:
                    optimized_path = await asyncio.to_thread(
                        compressor.compress_for_vision, file_path
                    )
                    prompt = EXTRACTION_PROMPT
                    img_path = optimized_path
                except Exception:
                    logger.exception(
                        f"PayloadCompressor falhou para {file_path}. "
                        f"Abortando SLOW_LANE — enviando para quarentena."
                    )
                    raise

            from datetime import datetime
            placeholder_date = datetime.now()
            active_rules = self.ontology_manager.get_tenant_active_context(tenant, placeholder_date)

            # Passa para a UTI Cognitiva com Pydantic Shield
            # Passamos os api_contents diretamente (se tivermos parts PIL), 
            # Mas wait, structured_inference processa "contents". Vamos ajustar MenirIntel. 
            # Precisaremos injetar support para parts manuais em structured_inference.
            # Por hora enviamos a string concatenada no prompt, ou as imagens.
            
            # Se for SCANNED, temos api_contents. 
            # Em SLOW_LANE, temos img_path. 
            invoice_dict = await self.intel.structured_inference(
                prompt=prompt if locals().get("lane") == "SLOW_LANE" else "", # Passaremos parts via kwargs se MenirIntel aceitar
                image_path=img_path,
                response_schema=None,
                raw_parts=api_contents if "api_contents" in locals() and len(api_contents) > 0 else None
            )
            
            import uuid
            invoice_dict["uid"] = str(uuid.uuid4())
            invoice_dict["project"] = tenant
            invoice_dict["source_document_uid"] = file_hash

            validated = InvoiceData.model_validate(
                invoice_dict, context={"valid_tva_rates": active_rules.get("tva_rates", [])}
            )

            zefix_match, zefix_status = await self._resolve_vendor_zefix(validated.ide_number, validated.vendor_name, tenant)
            
            penalty = 0.0
            if zefix_status == "RATE_LIMITED":
                penalty = 0.10
                logger.warning(f"Fornecedor {validated.vendor_name} não verificado devido a RATE_LIMITED (Zefix). Penalidade: {penalty}")
            elif not zefix_match:
                self._quarantine_document(tenant, file_hash, "VendorNotFoundZefix")
                return SkillResult(
                    success=False,
                    nodes_and_edges=[],
                    message="Confidence score derrubado para < 0.4. Fornecedor não encontrado no Zefix."
                )

            from src.v3.core.persistence import NodePersistenceOrchestrator
            orchestrator = NodePersistenceOrchestrator()
            
            try:
                with self.ontology_manager.driver.session() as session:
                    with session.begin_transaction() as tx:
                        await orchestrator.persist(validated, tx)
            except Exception as e:
                logger.exception(f"Erro transacional ao persistir via orquestrador: {e}")
                if str(e) == "TRANSACTION_ROLLBACK":
                    raise
                self._quarantine_document(tenant, file_hash, "TRANSACTION_ROLLBACK")
                raise Exception("TRANSACTION_ROLLBACK") from e

            msg = f"Fatura processada: {validated.vendor_name} | {validated.total_amount:.2f} {validated.currency}"
            if penalty > 0:
                msg += f" [Penalty Zefix: -{penalty}]"

            return SkillResult(
                success=True,
                nodes_and_edges=[],
                message=msg,
            )

        except json.JSONDecodeError as e:
            logger.exception(f"JSONDecodeError: {e}")
            reason = str(e)
            self.ontology_manager.inject_entropy_anomaly(
                tenant, file_hash, "JSONDecodeError", reason, 1
            )
            self._quarantine_document(tenant, file_hash, f"JSONDecodeError: {reason}")
            return SkillResult(
                success=False, nodes_and_edges=[], message=f"LLM retornou JSON inválido: {e}"
            )

        except ValidationError as e:
            error_count = len(e.errors())
            logger.error(f"ValidationError: {error_count} erros de validação fiduciária")
            self.ontology_manager.inject_entropy_anomaly(
                tenant, file_hash, "MathValidationError", "Campos fiduciários rejeitados (ofuscado por segurança)", error_count
            )
            self._quarantine_document(tenant, file_hash, f"ValidationError: {error_count} falhas estruturais.")
            return SkillResult(
                success=False,
                nodes_and_edges=[],
                message=f"Fatura reprovada em {error_count} regras fiduciárias",
            )

        except Exception as e:
            logger.exception(f"Erro genérico no InvoiceSkill: {e}")
            if str(e) != "TRANSACTION_ROLLBACK":
                self._quarantine_document(tenant, file_hash, f"Exception: {str(e)}")
            return SkillResult(success=False, nodes_and_edges=[], message=f"Falha estrutural: {e}")

    def _quarantine_document(self, tenant: str, file_hash: str, reason: str):
        """Registra explicitamente o motivo exato da falha no Neo4j, movendo o nó para quarentena."""
        safe_tenant = tenant.replace("`", "")
        cypher = f"""
        MERGE (d:Document:`{safe_tenant}` {{file_hash: $file_hash}})
        SET d.status = 'QUARANTINE',
            d.quarantine_reason = $reason,
            d.quarantined_at = datetime()
        """
        try:
            with self.ontology_manager.driver.session() as session:
                session.run(cypher, file_hash=file_hash, reason=reason)
        except Exception as query_exc:
            logger.exception(f"Falha gravíssima ao registrar quarentena do nó no Neo4j: {query_exc}")
