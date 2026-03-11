import asyncio
import logging
from typing import Any

from src.v3.menir_intel import MenirIntel
from src.v3.core.persistence import NodePersistenceOrchestrator
from src.v3.core.embedding_service import EmbeddingService
from src.v3.core.neo4j_pool import get_shared_driver
from src.v3.core.schemas.identity import locked_tenant_context

from src.v3.core.schemas.personal import (
    CaptureResponse,
    PersonNode,
    ProjectNode,
    LifeEventNode,
    InsightNode,
    GoalNode
)

logger = logging.getLogger("MenirCapture")
logger.setLevel(logging.INFO)

SIMILARITY_MERGE_THRESHOLD = 0.95
SIMILARITY_HITL_THRESHOLD = 0.85

class MenirCapture:
    """
    Skill V2: Captura pessoal e ontologia com desambiguação vetorial de dois estágios (Mem0-like).
    Regras INVIOLÁVEIS:
    1. Desambiguação por grafo antes de criar.
    2. Uma pergunta máxima por input.
    3. Fronteira de tenant física (Cria REFERENCED_FROM cross-tenant).
    4. Gravação exclusiva via NodePersistenceOrchestrator.
    """
    def __init__(self, intel: MenirIntel, orchestrator: NodePersistenceOrchestrator):
        self.intel = intel
        self.orchestrator = orchestrator
        self._ensure_vector_indexes()

    def _ensure_vector_indexes(self):
        driver = get_shared_driver()
        labels = ["PersonNode", "ProjectNode", "LifeEventNode", "InsightNode", "GoalNode"]
        with driver.session() as session:
            for label in labels:
                index_name = f"{label.lower()}_intent_index"
                query = f"""
                CREATE VECTOR INDEX {index_name} IF NOT EXISTS
                FOR (e:{label}) ON (e.embedding)
                OPTIONS {{indexConfig: {{
                    `vector.dimensions`: 768,
                    `vector.similarity_function`: 'cosine'
                }}}}
                """
                try:
                    session.run(query)
                except Exception as e:
                    if "already exists" not in str(e).lower() and "equivalent" not in str(e).lower():
                        logger.warning(f"Aviso ao criar index {index_name}: {e}")

    async def ingest(self, text: str, current_tenant: str = None, media_path: str = None) -> dict:
        import os
        if current_tenant is None:
            current_tenant = os.getenv("MENIR_PERSONAL_TENANT_NAME", "PESSOAL")
        print(f"\\n🧠 Interpretando com MenirIntel no Tenant: {current_tenant}...")
        
        prompt = f"""
        Extraia as principais entidades do seguinte pensamento ou insight pessoal.
        Avalie o 'impact_score' de 1 a 10 para classificar a importância central dessa entidade no texto.
        RETORNE ESTRITAMENTE UM JSON com a seguinte estrutura:
        {{
            "entities": [
                {{
                    "entity_type": "Person" | "Project" | "LifeEvent" | "Insight" | "Goal",
                    "name_or_title": "nome principal",
                    "context": "contexto para desambiguacao",
                    "impact_score": 10
                }}
            ]
        }}
        ---
        "{text}"
        """
        
        contents_to_send = [prompt]
        if media_path and os.path.exists(media_path):
            try:
                if media_path.lower().endswith(('.ogg', '.mp3', '.m4a', '.wav')):
                    print(f"🔊 Anexando nota de voz ao contexto cognitivo...")
                    with open(media_path, "rb") as f:
                        audio_data = f.read()
                    
                    mime_type = "audio/mpeg"
                    if media_path.lower().endswith('.ogg'):
                        mime_type = "audio/ogg"
                    elif media_path.lower().endswith('.wav'):
                        mime_type = "audio/wav"
                        
                    from google.genai import types
                    contents_to_send.append(
                        types.Part.from_bytes(data=audio_data, mime_type=mime_type)
                    )
                else:
                    from PIL import Image
                    img = Image.open(media_path)
                    contents_to_send.append(img)
                    print(f"🖼 Anexando documento visual ao contexto cognitivo...")
            except Exception as e:
                print(f"⚠️ Erro ao carregar media para o Gemini: {e}")
                
        try:
            from google.genai import types
            
            # Use structured output
            response = self.intel.client.models.generate_content(
                model=self.intel.model_id,
                contents=contents_to_send,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.0
                ),
            )
            payload_json = response.text
            payload = CaptureResponse.model_validate_json(payload_json)
        except Exception as e:
            print(f"❌ Erro na extração LLM: {e}")
            return {"success": False}
            
        print(f"✨ Entidades extraídas: {len(payload.entities)}")
        
        # Estrutura de HITL
        hitl_candidates = []
        actions_to_take = [] # list of dicts with entity details
        
        # Etapa 1: Recall Vetorial (Fast Match)
        for entity in payload.entities:
            query_text = f"{entity.name_or_title} {entity.context}"
            label_node = f"{entity.entity_type}Node"
            
            # Buscar no tenant atual
            matches_current = await EmbeddingService.semantic_search(query_text, label_node, current_tenant, top_k=1)
            best_match = matches_current[0] if matches_current else None
            
            if best_match and best_match['score'] >= SIMILARITY_MERGE_THRESHOLD:
                print(f"🔍 Similaridade {best_match['score']:.2f} (>{SIMILARITY_MERGE_THRESHOLD}) - Match exato encontrado em {current_tenant}: {best_match['name']}")
                actions_to_take.append({
                    "action": "MERGE",
                    "entity": entity,
                    "target_uid": best_match['id'],
                    "target_name": best_match['name']
                })
                continue
                
            if best_match and best_match['score'] >= SIMILARITY_HITL_THRESHOLD:
                # Ambiguidade dentro do próprio tenant
                hitl_candidates.append({
                    "action": "HITL_CURRENT",
                    "entity": entity,
                    "target_uid": best_match['id'],
                    "target_name": best_match['name'],
                    "score": best_match['score']
                })
                continue
                
            # Se não encontrou no current_tenant, ou similiaridade < HITL, checar Cross-Tenant BECO (Rule 3)
            # Para este MVP, verificamos "BECO" se estamos no "SANTOS".
            other_tenant = "BECO" if current_tenant == "SANTOS" else "SANTOS"
            matches_other = await EmbeddingService.semantic_search(query_text, label_node, other_tenant, top_k=1)
            best_other = matches_other[0] if matches_other else None
            
            if best_other and best_other['score'] >= SIMILARITY_MERGE_THRESHOLD:
                print(f"🔒 Limite de Tenant Atingido. Entidade '{entity.name_or_title}' existe no {other_tenant} (Score {best_other['score']:.2f}).")
                actions_to_take.append({
                    "action": "VIRTUAL_CROSS",
                    "entity": entity,
                    "target_uid": best_other['id'],
                    "target_name": best_other['name'],
                    "target_tenant": other_tenant
                })
                continue
                
            if best_other and best_other['score'] >= SIMILARITY_HITL_THRESHOLD:
                hitl_candidates.append({
                    "action": "HITL_CROSS",
                    "entity": entity,
                    "target_uid": best_other['id'],
                    "target_name": best_other['name'],
                    "target_tenant": other_tenant,
                    "score": best_other['score']
                })
                continue
                
            # Se chegou aqui, é NOVO (Similaridade muito baixa)
            max_score =  max((best_match['score'] if best_match else 0.0), (best_other['score'] if best_other else 0.0))
            print(f"✨ Nova Entidade Inferida: {entity.entity_type}({entity.name_or_title}). Similaridade Máxima Encontrada: {max_score:.2f} (<{SIMILARITY_HITL_THRESHOLD}).")
            actions_to_take.append({
                "action": "CREATE",
                "entity": entity,
                "trust_score": 0.9 # Seguro pois é inédito
            })
            
        # Etapa 2: Resolução de HITL (Max 1 pergunta)
        pending_hitl_context = None
        if hitl_candidates:
            # Ordena por impacto da entidade central no texto
            hitl_candidates.sort(key=lambda x: x["entity"].impact_score, reverse=True)
            
            prime_candidate = hitl_candidates[0]
            ent = prime_candidate["entity"]
            print(f"⚠️ Ambiguidade Detectada: Extraído {ent.entity_type}({ent.name_or_title})")
            
            pending_hitl_context = prime_candidate
            
            # Tratar os demais HITL como Dúvida Silenciosa
            for rem in hitl_candidates[1:]:
                print(f"⚠️ Ignorando ambiguidade de {rem['entity'].name_or_title} para evitar múltiplas perguntas (Rule 2). Marcando com trust_score = 0.2")
                actions_to_take.append({"action": "CREATE", "entity": rem["entity"], "trust_score": 0.2})
                
        # Persist ALL other actions asyncly
        await self._persist_actions(actions_to_take, current_tenant)
        
        return {"success": True, "hitl": pending_hitl_context}

    async def resolve_hitl(self, hitl_context: dict, approved: bool, current_tenant: str):
        actions_to_take = []
        action_type = hitl_context["action"]
        ent = hitl_context["entity"]
        t_name = hitl_context["target_name"]
        
        if approved:
            if action_type == "HITL_CURRENT":
                actions_to_take.append({"action": "MERGE", "entity": ent, "target_uid": hitl_context["target_uid"], "target_name": t_name})
            else:
                actions_to_take.append({
                    "action": "VIRTUAL_CROSS",
                    "entity": ent,
                    "target_uid": hitl_context["target_uid"],
                    "target_name": t_name,
                    "target_tenant": hitl_context["target_tenant"]
                })
        else:
            actions_to_take.append({"action": "CREATE", "entity": ent, "trust_score": 0.9})
            
        await self._persist_actions(actions_to_take, current_tenant)

    async def _persist_actions(self, actions_to_take: list, current_tenant: str):
        # Corrigindo bloco de execução async para o Orchestrator
        with locked_tenant_context(current_tenant):
            driver = get_shared_driver()
            with driver.session() as session:
                with session.begin_transaction() as tx:
                    for act in actions_to_take:
                        ent = act["entity"]
                        node_obj = None
                        
                        if ent.entity_type == "Person":
                            node_obj = PersonNode(uid="", project=current_tenant, name=act.get("target_name", ent.name_or_title), role_or_context=ent.context, trust_score=act.get("trust_score", 0.9))
                        elif ent.entity_type == "Project":
                            node_obj = ProjectNode(uid="", project=current_tenant, name=act.get("target_name", ent.name_or_title), description=ent.context)
                        elif ent.entity_type == "LifeEvent":
                            node_obj = LifeEventNode(uid="", project=current_tenant, title=act.get("target_name", ent.name_or_title))
                        elif ent.entity_type == "Insight":
                            node_obj = InsightNode(uid="", project=current_tenant, content=act.get("target_name", ent.name_or_title), source_context=ent.context)
                        elif ent.entity_type == "Goal":
                            node_obj = GoalNode(uid="", project=current_tenant, title=act.get("target_name", ent.name_or_title))
                        else:
                            continue
                            
                        if act["action"] == "MERGE":
                            node_obj.uid = act["target_uid"]
                            print(f"✅ UPDATE/MERGE ({ent.entity_type}: {ent.name_or_title}) -> [{current_tenant}]")
                        elif act["action"] == "VIRTUAL_CROSS":
                            node_obj.is_virtual = True
                            node_obj.referenced_tenant = act["target_tenant"]
                            node_obj.referenced_uid = act["target_uid"]
                            print(f"✅ VIRTUAL NODE ({ent.name_or_title}) -> [:REFERENCED_FROM] -> {act['target_tenant']}")
                        elif act["action"] == "CREATE":
                            print(f"✅ CREATE ({ent.entity_type}: {ent.name_or_title}) -> [{current_tenant}]")
                            
                        # Await the persistence
                        await self.orchestrator.persist(node_obj, tx)
                        
                        # Generate Embedding for the newly created/merged node
                        node_text_for_embed = f"{ent.name_or_title} {getattr(node_obj, 'role_or_context', '')} {getattr(node_obj, 'description', '')}"
                        asyncio.create_task(
                            EmbeddingService.embed_and_persist(node_obj.uid, node_text_for_embed, f"{ent.entity_type}Node", current_tenant)
                        )

async def _cli_loop():
    import os
    tenant_name = os.getenv("MENIR_PERSONAL_TENANT_NAME", "PESSOAL")
    intel = MenirIntel()
    orch = NodePersistenceOrchestrator()
    capture = MenirCapture(intel, orch)
    
    print("\n[ MENIR CAPTURE (SANTOS DOMAIN) - INTERACTIVE MODE ]\n")
    while True:
        try:
            await asyncio.sleep(1.0) # wait for background embedding tasks
            line = await asyncio.to_thread(input, "\n[User] > ")
            if not line.strip():
                continue
            if line.strip().lower() in ['exit', 'quit']:
                break
            
            res = await capture.ingest(line, tenant_name)
            if res and res.get("hitl"):
                hc = res["hitl"]
                t_name = hc["target_name"]
                ans = await asyncio.to_thread(input, f"❓ Você está se referindo a '{t_name}'? [Y/N]: ")
                approved = ans.strip().lower() == 'y'
                await capture.resolve_hitl(hc, approved, tenant_name)
                
        except EOFError:
            break
            
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    asyncio.run(_cli_loop())
