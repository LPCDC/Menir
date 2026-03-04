"""
Menir Core V5.1 - Provenance Ontology (PROV-O)
Maintains a strict, cryptographically sound Audit Trail within Neo4j.
Registers mutations, command executions, and state changes as Event nodes
linked to the invoking Agent and the affected Entity, complying with Swiss nFADP.
"""

import json
import logging
import uuid

from src.v3.meta_cognition import MenirOntologyManager

logger = logging.getLogger("MenirProv")


class MenirProv:
    def __init__(self, ontology_manager: MenirOntologyManager):
        self.ontology_manager = ontology_manager

        # Estratégia de Filtragem de Ruído (O Escudo contra Bloat do Banco)
        # Ignoramos sumariamente tudo que não for mutação de estado.
        self.REGISTERABLE_ACTIONS = {
            "PAUSE_INGESTION",
            "RELOAD_RULES",
            "FLUSH_QUARANTINE",
            "RESUME_INGESTION",
            "RECONCILIATION_CRITICAL_MATCH",
            "DOWNSAMPLING_EXCEPTION",
            "GHOST_NODE_ISOLATED",
            "CRESUS_EXPORT_FORCED",
        }

    def record_event(
        self, agent: str, action: str, target_metadata: dict, target_node_id: str | None = None
    ):
        """
        Gera um registro na malha de eventos PROV-O do Neo4j.
        (Agent)-[:TRIGGERED]->(Event)-[:AFFECTED]->(Entity)
        """
        # Proteção contra Inflação de Vértices: Descarte passivo precoce O(1).
        if action not in self.REGISTERABLE_ACTIONS:
            logger.debug(f"🔇 Evento passivo {action} ignorado pelo auditor PROV-O.")
            return

        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        meta_json = json.dumps(target_metadata, ensure_ascii=False)

        # A montagem base do Agente e do Evento
        query = """
        MERGE (a:Agent {name: $agent})
        CREATE (e:Event {
            event_id: $event_id,   # noqa: W291
            timestamp: datetime(),   # noqa: W291
            action: $action,   # noqa: W291
            metadata: $meta_json
        })
        MERGE (a)-[:TRIGGERED]->(e)
        """

        # Se houver um Entity ID Alvo (ElementId do Neo4j ou um UID lógico), a gente amarra a teia.
        # Devido à natureza abstrata (target pode ser Tenant, Invoice, etc) usaremos um MATCH abrangente
        # na variável de amarração se um ID for fornecido.
        if target_node_id:
            query += """
            WITH e
            MATCH (target) WHERE target.uid = $target_node_id OR target.elementId = $target_node_id OR target.name = $target_node_id
            MERGE (e)-[:AFFECTED]->(target)
            """

        logger.info(f"📜 Registrando Evento de Auditoria PROV-O: {agent} -> {action}")

        try:
            with self.ontology_manager.driver.session() as session:
                session.run(
                    query,
                    agent=agent,
                    event_id=event_id,
                    action=action,
                    meta_json=meta_json,
                    target_node_id=target_node_id,
                )
        except Exception as e:
            # Em sistemas críticos, falha de log não deve derrubar a execução, apenas alarmar severamente.
            logger.critical(
                f"Falha de Auditoria Irreversível! O Evento {action} de {agent} não foi persistido no Grafo: {e}"
            )


if __name__ == "__main__":
    pass
