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

    def _inject_into_graph(self, data: InvoiceData, file_hash: str, vendor_verified: bool):
        """
        Materializa a ontologia em memória (InvoiceData) no motor Neo4j.
        Transação Cypher rigorosa com idempotência via MERGE.
        """
        # Pass items directly to Cypher UNWIND
        line_items_list = [item.model_dump() for item in data.items]

        from src.v3.core.schemas.identity import TenantContext
        
        tenant = TenantContext.get()
        if not tenant:
            raise ValueError("Isolamento violado. Nenhum Tenant ativo configurado.")
            
        safe_tenant = tenant.replace("`", "")

        query = f"""
        // 1. Fornecedor (Vendor) - (Já criado/atualizado pelo Zefix Cache)
        MATCH (v:Vendor:`{safe_tenant}` {{name: $vendor_name}})

        // 2. Fatura (Invoice) - Idempotência absoluta pelo HASH do arquivo
        MERGE (i:Invoice:`{safe_tenant}` {{file_hash: $file_hash}})
        SET i.issue_date = $issue_date,
            i.total_amount = $total_amount,
            i.currency = $currency,
            i.subtotal = $subtotal,
            i.tips = $tips,
            i.requires_justification = $requires_justification,
            i.ingested_at = datetime()

        // 3. Relacionamento Invoice -> Emitido Por -> Fornecedor
        MERGE (i)-[r:ISSUED_BY]->(v)
        SET r.verified = $vendor_verified

        // 4. Relacionamento Tenant -> Recebe -> Fatura
        MERGE (t:Tenant {{name: $tenant_safe}})
        MERGE (t)-[:RECEIVED]->(i)

        // 5. Itens de Linha (LineItems) Reais Relacionais
        WITH i, safe_tenant
        UNWIND $line_items_list AS item
        MERGE (li:LineItem:`{safe_tenant}` {{invoice_hash: $file_hash, description: item.description}})
        SET li.gross_amount = item.gross_amount,
            li.tva_rate_applied = item.tva_rate_applied,
            li.project = $tenant_safe
        MERGE (i)-[:CONTAINS]->(li)
        """

        params: dict[str, Any] = {
            "tenant_safe": safe_tenant,
            "vendor_name": data.vendor_name,
            "vendor_verified": vendor_verified,
            "ide_number": data.ide_number,
            "avs_number": data.avs_number,
            "vendor_iban": data.vendor_iban,
            "file_hash": file_hash,
            "issue_date": data.issue_date,
            "total_amount": data.total_amount,
            "currency": data.currency,
            "subtotal": data.subtotal,
            "tips": data.tip_or_unregulated_amount,
            "requires_justification": data.requires_manual_justification,
            "line_items_list": line_items_list,
        }

        with self.ontology_manager.driver.session() as session:
            session.run(query, **params)
            logger.info(
                f"✅ Fatura injetada no Grafo (Fornecedor: {data.vendor_name}, Total: {data.total_amount:.2f} {data.currency})"
            )

    async def _resolve_vendor_zefix(self, ide_number: str | None, name: str, tenant: str) -> bool:
        import aiohttp
        import asyncio

        safe_tenant = tenant.replace("`", "")

        cache_query = f"""
        MATCH (v:Vendor:`{safe_tenant}`)
        WHERE v.name = $name OR (v.ide_number = $ide AND $ide IS NOT NULL)
        RETURN v.zefix_match AS zefix_match
        LIMIT 1
        """
        def _check_db():
            with self.ontology_manager.driver.session() as s:
                return s.run(cache_query, ide=ide_number, name=name).single()
                
        cached = await asyncio.to_thread(_check_db)
        if cached:
            return cached["zefix_match"]

        zefix_match = False
        async with aiohttp.ClientSession() as session:
            try:
                payload = {{"uid": ide_number}} if ide_number else {{"name": name}}
                async with session.post("https://www.zefix.admin.ch/ZefixPublicREST/api/v1/company/search", json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data and isinstance(data, list) and len(data) > 0:
                            zefix_match = True
            except Exception as e:
                logger.warning(f"Zefix API failed: {{e}}")
        
        persist_query = f"""
        MERGE (v:Vendor:`{safe_tenant}` {{name: $name}})
        SET v.ide_number = $ide,
            v.zefix_match = $zefix_match,
            v.zefix_queried_at = datetime(),
            v.project = $safe_tenant
        """
        def _save_vendor():
            with self.ontology_manager.driver.session() as s:
                s.run(persist_query, name=name, ide=ide_number, zefix_match=zefix_match, safe_tenant=safe_tenant)
        await asyncio.to_thread(_save_vendor)

        return zefix_match

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
            compressor = PayloadCompressor()
            api_contents: list[Any]
            lane = "FAST_LANE" if file_path.lower().endswith(".pdf") else "SLOW_LANE"

            if lane == "FAST_LANE":
                logger.info("⚡ FAST_LANE: Extraindo texto nativo via pypdf.")
                reader = PdfReader(file_path)
                raw_text = "\n".join(page.extract_text() or "" for page in reader.pages)
                prompt = EXTRACTION_PROMPT + "\n\nTEXTO DA FATURA:\n" + raw_text
                img_path = None
            else:
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

            # Passa para a UTI Cognitiva com Pydantic Shield (sem passar a classe para forçar context validation local)
            invoice_dict = await self.intel.structured_inference(
                prompt=prompt,
                image_path=img_path,
                response_schema=None
            )

            validated = InvoiceData.model_validate(
                invoice_dict, context={"valid_tva_rates": active_rules.get("tva_rates", [])}
            )

            zefix_match = await self._resolve_vendor_zefix(validated.ide_number, validated.vendor_name, tenant)
            if not zefix_match:
                self._quarantine_document(tenant, file_hash, "VendorNotFoundZefix")
                return SkillResult(
                    success=False,
                    nodes_and_edges=[],
                    message="Confidence score derrubado para < 0.4. Fornecedor não encontrado no Zefix."
                )

            self._inject_into_graph(validated, file_hash, zefix_match)

            return SkillResult(
                success=True,
                nodes_and_edges=[],
                message=f"Fatura processada: {validated.vendor_name} | {validated.total_amount:.2f} {validated.currency}",
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
            reason_details = str(e.errors())
            self.ontology_manager.inject_entropy_anomaly(
                tenant, file_hash, "MathValidationError", e.json(), error_count
            )
            self._quarantine_document(tenant, file_hash, f"ValidationError: {reason_details}")
            return SkillResult(
                success=False,
                nodes_and_edges=[],
                message=f"Fatura reprovada em {error_count} regras fiduciárias",
            )

        except Exception as e:
            logger.exception(f"Erro genérico no InvoiceSkill: {e}")
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
