import logging
import asyncio
from typing import Any
from src.v3.core.schemas.personal import PersonalGraphPayload
from src.v3.menir_intel import MenirIntel
from src.v3.meta_cognition import MenirOntologyManager
from src.v3.core.schemas.identity import TenantContext

logger = logging.getLogger("MenirCapture")

class MenirCapture:
    """
    Skill V2: Captura pessoal e ontologia com desambiguação vetorial.
    Sprint 2A Requirement:
    - Camada 1: Lowercase + Strip via Pydantic validator (PersonalGraphPayload)
    - Camada 2: Neo4j Vector Index Cosine > 0.92 pré-MERGE
    """
    def __init__(self, intel: MenirIntel, ontology_manager: MenirOntologyManager):
        self.intel = intel
        self.ontology_manager = ontology_manager
        self._init_personal_vector_index()

    def _init_personal_vector_index(self):
        query = """
        CREATE VECTOR INDEX personal_vectors IF NOT EXISTS
        FOR (e:PersonalEntity) ON (e.embedding)
        OPTIONS {indexConfig: {
            `vector.dimensions`: 768,
            `vector.similarity_function`: 'cosine'
        }}
        """
        try:
            with self.ontology_manager.driver.session() as session:
                session.run(query)
                logger.info("✅ Native Vector Index 'personal_vectors' garantido para MenirCapture.")
        except Exception as e:
            if "already exists" in str(e).lower() or "equivalent" in str(e).lower():
                pass
            else:
                logger.warning(f"Aviso na inicialização do Vector Index Pessoal: {e}")

    async def _safe_vector_search(self, embedding: list[float], tenant_safe: str, min_score: float = 0.92) -> dict | None:
        """
        Consulta o Vector Index das Entidades Pessoais usando GDS Vector native.
        """
        query = f"""
        CALL db.index.vector.queryNodes('personal_vectors', 1, $embedding)
        YIELD node, score
        WHERE score >= $min_score AND '{tenant_safe}' IN labels(node)
        RETURN node.name as name, labels(node) as labels, score
        """
        def _run():
            with self.ontology_manager.driver.session() as session:
                return session.run(query, embedding=embedding, min_score=min_score).single()
        
        result = await asyncio.to_thread(_run)
        if result:
            return {"name": result["name"], "score": result["score"]}
        return None

    async def ingest_insight(self, raw_text: str) -> dict[str, Any]:
        tenant = TenantContext.get()
        if not tenant:
            raise ValueError("Isolamento violado. Nenhum Tenant ativo configurado para Captura Pessoal.")
            
        safe_tenant = tenant.replace("`", "")

        logger.info(f"🧠 [MenirCapture] Processando Insight Pessoal para Tenant {tenant}")
        
        prompt = f"""Extraia a ontologia do seguinte pensamento ou insight pessoal:
---
\"{raw_text}\"
---
Extraia o mais puramente possível focando em substantivos limpos ou entidades curtas."""

        payload: PersonalGraphPayload = await self.intel.structured_inference(
            prompt=prompt,
            response_schema=PersonalGraphPayload
        )

        # Injeção Cypher com Camada 2
        nodes_dispatched = []
        requires_disambiguation_count = 0

        # Mapeamento do nome gerado para o nome real consolidado no banco (se desambiguado)
        name_resolution_map = {}

        for entity in payload.entities:
            # Pydantic já garantiu: lower() + strip().
            entity_name = entity.name
            
            # Gera embedding da entidade
            embedding = await asyncio.to_thread(self.intel.generate_embedding, entity_name)
            
            # Checagem de Similaridade Vetorial (Cosine > 0.92)
            similar_node = await self._safe_vector_search(embedding, safe_tenant, min_score=0.92)
            
            async def _merge_cypher(sim, emb):
                with self.ontology_manager.driver.session() as session:
                    if sim and sim["name"].lower() != entity_name:
                        # Acima do limiar (0.92), mas nome não é exatamente idêntico (ex: "maternidade" vs "maternidades")
                        # Liga o conceito existente com a Flag V0, NÃO cria nó novo.
                        existing_name = sim["name"]
                        q_disambiguate = f"""
                        MATCH (e:PersonalEntity:`{safe_tenant}` {{name: $existing_name}})
                        SET e.needs_v0_review = true, e.last_ambiguous_alias = $name
                        SET e:NEEDS_DISAMBIGUATION
                        """
                        session.run(q_disambiguate, existing_name=existing_name, name=entity_name)
                        logger.warning(f"⚠️ Ambiguidade Detectada: '{entity_name}' é 0.92+ similar a '{existing_name}'. Nó existente linkado com Flag V0.")
                        return existing_name, True
                    else:
                        # Inserção Normal Segura (Abaixo do limiar ou Match Exato onde Cypher MERGE funde tranquilamente)
                        q_normal = f"""
                        MERGE (e:PersonalEntity:{entity.entity_type}:`{safe_tenant}` {{name: $name}})
                        SET e.embedding = $emb
                        """
                        if entity.description:
                            q_normal = q_normal.replace("SET e.embedding = $emb", "SET e.embedding = $emb, e.description = $desc")
                        session.run(q_normal, name=entity_name, emb=emb, desc=entity.description)
                        return entity_name, False

            final_name, disambiguated = await _merge_cypher(similar_node, embedding)
            name_resolution_map[entity.name] = final_name
            nodes_dispatched.append(final_name)
            if disambiguated:
                requires_disambiguation_count += 1
        
        # Conecta os Edges usando o Mapa de Resolução
        for rel in payload.relationships:
            resolved_source = name_resolution_map.get(rel.source_name, rel.source_name)
            resolved_target = name_resolution_map.get(rel.target_name, rel.target_name)
            
            safe_rel_type = rel.relation_type.replace("`", "").replace(" ", "_").upper()
            
            q_rel = f"""
            MATCH (a:PersonalEntity:`{safe_tenant}` {{name: $src}})
            MATCH (b:PersonalEntity:`{safe_tenant}` {{name: $tgt}})
            MERGE (a)-[r:`{safe_rel_type}`]->(b)
            SET r.project = $tenant_safe
            """
            
            def _run_rel():
                with self.ontology_manager.driver.session() as session:
                    session.run(q_rel, src=resolved_source, tgt=resolved_target, tenant_safe=safe_tenant)
            
            await asyncio.to_thread(_run_rel)

        return {
            "success": True,
            "nodes_processed": len(nodes_dispatched),
            "edges_processed": len(payload.relationships),
            "ambiguities_flagged_V0": requires_disambiguation_count,
            "message": f"Extração Pessoal V2 completa: {len(nodes_dispatched)} entidades ({requires_disambiguation_count} p/ V0)."
        }
