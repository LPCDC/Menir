import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Any
from src.v3.menir_intel import MenirIntel
from src.v3.menir_bridge import MenirBridge
from src.v3.core.schemas.identity import TenantContext

logger = logging.getLogger("QuestionEngine")

async def generate_question(user_input: str, user_uid: str) -> Optional[str]:
    """
    Motor de perguntas inteligentes para o domínio SANTOS.
    Decide se o Menir deve fazer uma pergunta de follow-up baseada em gaps no grafo ou sinais do DecisionHub.
    """
    try:
        tenant = TenantContext.get()
        if not tenant:
            raise RuntimeError("question_engine chamado fora de contexto galvânico")

        intel = MenirIntel()
        bridge = MenirBridge()

        # 1. Extrair entidades mencionadas
        entities = await _extract_entities(intel, user_input)
        if not entities and not await _has_urgent_signals(bridge, tenant):
            return None

        # 2. Buscar gaps nas entidades conhecidas
        gaps = await _find_gaps(bridge, tenant, entities)

        # 3. Consultar DecisionHub por sinais urgentes
        signals = await _get_urgent_signals(bridge, tenant)

        # 4. Formular pergunta final
        if not gaps and not signals:
            return None

        return await _formulate_question(intel, user_input, gaps, signals)

    except RuntimeError as e:
        logger.error(f"Erro de Contexto: {e}")
        raise e
    except Exception as e:
        logger.exception(f"Erro ao gerar pergunta inteligente: {e}")
        return None

async def _extract_entities(intel: MenirIntel, user_input: str) -> List[str]:
    prompt = f"""
    Extraia nomes de Pessoas, Projetos, Lugares ou Conceitos mencionados no texto abaixo.
    Retorne apenas uma lista de strings. Se nada for encontrado, retorne uma lista vazia [].
    TEXTO: "{user_input}"
    """
    try:
        # Usando inference estruturada básica para obter lista
        entities = await intel.structured_inference(prompt, response_schema=None)
        if isinstance(entities, list):
            return [str(e) for e in entities]
        return []
    except Exception:
        return []

async def _find_gaps(bridge: MenirBridge, tenant: str, entities: List[str]) -> List[dict]:
    if not entities:
        return []

    # Threshold de 30 dias para "stale"
    stale_date = (datetime.now() - timedelta(days=30)).isoformat()

    def _sync_query():
        gaps = []
        query = f"""
        MATCH (n)-[:BELONGS_TO_TENANT]->(t:Tenant {{name: $tenant}})
        WHERE any(label IN labels(n) WHERE label IN ['Person', 'Project', 'Insight', 'Goal'])
          AND (n.name IN $entities OR n.content IN $entities OR n.title IN $entities)
        RETURN n, labels(n)[0] as label
        """
        
        with bridge.driver.session() as session:
            result = session.run(query, tenant=tenant, entities=entities)
            for record in result:
                node = record["n"]
                label = record["label"]
                
                # Gap detection logic
                node_gaps = []
                
                # 1. Campos nulos/vazios
                if label == "Person" and not node.get("role_or_context"):
                    node_gaps.append("missing role_or_context")
                if label == "Project" and not node.get("description"):
                    node_gaps.append("missing description")
                
                # 2. Dados desatualizados (>30 dias)
                updated_at = node.get("updated_at") or node.get("created_at")
                if updated_at:
                    try:
                        dt_val = str(updated_at)
                        if dt_val < stale_date:
                            node_gaps.append("stale information")
                    except Exception:
                        pass
                else:
                    node_gaps.append("stale information") # Se não tem data, assumimos gap

                if node_gaps:
                    gaps.append({
                        "entity": node.get("name") or node.get("title") or node.get("content"),
                        "label": label,
                        "gaps": node_gaps
                    })
        return gaps
    
    return await asyncio.to_thread(_sync_query)

async def _has_urgent_signals(bridge: MenirBridge, tenant: str) -> bool:
    def _sync_query():
        # Check rápido para ver se vale a pena continuar se não houver entidades
        query = f"""
        MATCH (s:Signal)-[:AFFECTS]->(hub:DecisionHub)-[:BELONGS_TO_TENANT]->(t:Tenant {{name: $tenant}})
        WITH s, duration.inDays(datetime(s.created_at), datetime()).days AS days_passed
        WITH s, (s.initial_score * exp(-s.decay_lambda * days_passed)) AS priority
        WHERE priority > 0.6
        RETURN count(s) > 0 as has_urgent
        """
        try:
            with bridge.driver.session() as session:
                res = session.run(query, tenant=tenant).single()
                return res["has_urgent"] if res else False
        except Exception:
            return False
            
    return await asyncio.to_thread(_sync_query)

async def _get_urgent_signals(bridge: MenirBridge, tenant: str) -> List[dict]:
    def _sync_query():
        query = f"""
        MATCH (s:Signal)-[:AFFECTS]->(hub:DecisionHub)-[:BELONGS_TO_TENANT]->(t:Tenant {{name: $tenant}})
        WITH s, duration.inDays(datetime(s.created_at), datetime()).days AS days_passed
        WITH s, (s.initial_score * exp(-s.decay_lambda * days_passed)) AS priority
        WHERE priority > 0.6
        RETURN s.signal_type as type, s.description as desc, priority
        ORDER BY priority DESC
        LIMIT 3
        """
        signals = []
        try:
            with bridge.driver.session() as session:
                result = session.run(query, tenant=tenant)
                for r in result:
                    signals.append(dict(r))
        except Exception:
            pass
        return signals

    return await asyncio.to_thread(_sync_query)

async def _formulate_question(intel: MenirIntel, user_input: str, gaps: List[dict], signals: List[dict]) -> Optional[str]:
    context_str = f"INPUT USUÁRIO: {user_input}\n\n"
    if gaps:
        context_str += "GAPS NO GRAFO:\n"
        for g in gaps:
            context_str += f"- Entidade '{g['entity']}' ({g['label']}): {', '.join(g['gaps'])}\n"
    
    if signals:
        context_str += "\nSINAIS URGENTES DO DECISIONHUB:\n"
        for s in signals:
            context_str += f"- {s['type']} (Prioridade: {s['priority']:.2f}): {s['desc']}\n"

    prompt = f"""
    ### CONTEXTO DO GRAFO MENIR (SANTOS) ###
    {context_str}
    
    ### TAREFA ###
    Baseado no input do usuário e nos gaps/sinais acima, formule uma ÚNICA pergunta em Português Brasileiro.
    REGRAS:
    - A pergunta deve ser específica ao contexto, nunca genérica.
    - Máximo de uma frase.
    - Nunca pergunte sobre sentimentos ou estados emocionais.
    - Se houver sinal urgente no DecisionHub, priorize-o se ele for relevante para o futuro do usuário.
    - Se nada for suficientemente importante, retorne apenas "NONE".
    """
    
    try:
        question = await intel.structured_inference(prompt, response_schema=None)
        if isinstance(question, str) and question.upper() != "NONE":
            return question.strip()
        return None
    except Exception:
        return None
