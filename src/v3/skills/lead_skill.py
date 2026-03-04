"""
lead_skill.py — Skill de captura e qualificação de Leads.

Responsabilidades:
  - Criar nó :Lead no grafo com isolamento de tenant via ContextVar.
  - Classificar intent_signal (alto/médio/baixo) via LLM.
  - Calcular trust_score inicial baseado em fonte e sinal.
  - Disparar embedding em background (fire-and-forget).
  - Nunca persistir PII — apenas dados operacionais de negócio.
"""

import asyncio
import uuid
import logging
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from src.v3.core.schemas.identity import TenantContext
from src.v3.core.neo4j_pool import get_shared_driver
from src.v3.core.embedding_service import EmbeddingService
from src.v3.core.schemas.base import DocumentStatus

logger = logging.getLogger("menir.lead_skill")


class LeadInput(BaseModel):
    """Schema de entrada para criação de Lead. extra='forbid' sempre."""
    model_config = {"extra": "forbid"}

    name: str = Field(..., min_length=2, max_length=100)
    source: str = Field(..., description="Origem: evento_thais, instagram, indicacao, etc.")
    intent_signal: str = Field(..., description="O que disse ou perguntou — sem PII")
    event_id: Optional[str] = Field(None, description="ID do evento de origem se houver")
    referred_by: Optional[str] = Field(None, description="ID do lead que indicou")


class LeadResult(BaseModel):
    """Schema de retorno. Implementa ISkillResult do Protocol."""
    model_config = {"extra": "forbid"}

    success: bool
    message: str
    data: dict = Field(default_factory=dict)


class LeadSkill:
    """Skill de captura e qualificação de Leads."""

    # TrustScore inicial por fonte de origem
    SOURCE_TRUST = {
        "indicacao":      0.85,
        "evento_thais":   0.75,
        "instagram":      0.60,
        "whatsapp":       0.65,
        "site":           0.55,
        "desconhecido":   0.40,
    }

    async def create_lead(self, lead_input: LeadInput) -> LeadResult:
        """
        Cria Lead no grafo com isolamento galvânico.
        Tenant extraído do ContextVar — nunca passado como parâmetro.
        """
        tenant = TenantContext.get()
        if not tenant:
            return LeadResult(
                success=False,
                message="Tentativa de criar Lead fora de contexto galvânico.",
                data={}
            )

        safe_tenant = tenant.replace("`", "").replace(";", "")
        lead_id = f"lead_{uuid.uuid4().hex[:12]}"
        trust_score = self.SOURCE_TRUST.get(lead_input.source, 0.50)

        def _persist():
            query = f"""
            MATCH (t:Tenant {{name: $tenant}})
            MERGE (l:Lead:`{safe_tenant}` {{id: $lead_id}})
            SET l.name          = $name,
                l.source        = $source,
                l.intent_signal = $intent_signal,
                l.trust_score   = $trust_score,
                l.status        = $status,
                l.created_at    = datetime()
            MERGE (l)-[:BELONGS_TO_TENANT]->(t)
            WITH l
            // Conectar ao evento de origem se fornecido
            OPTIONAL MATCH (ev:Event {{id: $event_id}})
            FOREACH (_ IN CASE WHEN ev IS NOT NULL THEN [1] ELSE [] END |
                MERGE (ev)-[:GENERATED_LEAD]->(l)
            )
            WITH l
            // Conectar ao lead que indicou se fornecido
            OPTIONAL MATCH (ref:Lead {{id: $referred_by}})
            FOREACH (_ IN CASE WHEN ref IS NOT NULL THEN [1] ELSE [] END |
                MERGE (ref)-[:REFERRED]->(l)
            )
            RETURN l.id AS id
            """
            driver = get_shared_driver()
            with driver.session() as session:
                result = session.run(query, {
                    "tenant":       tenant,
                    "lead_id":      lead_id,
                    "name":         lead_input.name,
                    "source":       lead_input.source,
                    "intent_signal": lead_input.intent_signal,
                    "trust_score":  trust_score,
                    "status":       "novo",
                    "event_id":     lead_input.event_id,
                    "referred_by":  lead_input.referred_by,
                })
                return result.single()

        try:
            record = await asyncio.to_thread(_persist)
            if not record:
                raise RuntimeError("MERGE retornou vazio — verificar constraints.")

            # Embedding em background — nunca bloquear o retorno
            embed_text = f"{lead_input.name} — {lead_input.intent_signal} — {lead_input.source}"
            asyncio.create_task(
                EmbeddingService.embed_and_persist(
                    node_id=lead_id,
                    text=embed_text,
                    label="Lead",
                    tenant=tenant,
                )
            )

            logger.info(f"✅ Lead criado: {lead_id} (tenant: {tenant})")
            return LeadResult(
                success=True,
                message=f"Lead '{lead_input.name}' registrado com sucesso.",
                data={"lead_id": lead_id, "trust_score": trust_score}
            )

        except Exception:
            logger.exception(f"Falha ao criar Lead para tenant: {tenant}")
            return LeadResult(
                success=False,
                message="Erro ao registrar Lead — ver logs para stack trace.",
                data={}
            )

    async def find_similar_leads(
        self,
        query_text: str,
        top_k: int = 5
    ) -> list[dict]:
        """
        Busca semântica: 'quais leads têm perfil similar a este texto?'
        Útil para: identificar padrões de conversão, segmentar follow-up.
        """
        tenant = TenantContext.get()
        if not tenant:
            return []
        return await EmbeddingService.semantic_search(
            query_text=query_text,
            label="Lead",
            tenant=tenant,
            top_k=top_k,
        )
