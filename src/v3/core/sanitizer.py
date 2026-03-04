"""
Menir Core V5.1 - Integrity Auditor (Ghost Scanner)
An immune system for the Neo4j graph. Scans for nodes left in a fragmented
or corrupted state due to abrupt Event Loop crashes or extraction failures,
quarantining them with a :GHOST_DATA label before the Reconciliation Engine
can ingest them.
"""

import logging

from src.v3.meta_cognition import MenirOntologyManager

logger = logging.getLogger("MenirSanitizer")


class MenirSanitizer:
    def __init__(self, ontology_manager: MenirOntologyManager):
        self.ontology_manager = ontology_manager

    def perform_sanity_check(self, tenant: str) -> dict:
        """
        Executa a varredura estrutural na base grafos para encontrar anomalias de ACID.
        Rotula os nós doentes como :GHOST_DATA para isolamento (Auto-Cura Passiva).
        """
        safe_tenant = tenant.replace("`", "")
        logger.info(f"👻 Iniciando Varredura Fantasma (Sanity Check) para o Tenant: {tenant}")

        # 1. Invoices sem Fornecedor atrelado (Relacionamento ISSUED ausente)
        q_orphan_invoice_vendor = f"""
        MATCH (i:Invoice:`{safe_tenant}`)
        WHERE NOT ()-[:ISSUED]->(i) AND NOT i:GHOST_DATA
        SET i:GHOST_DATA, i.quarantine_reason = "Missing Vendor Relationship"
        RETURN count(i) as isolated
        """

        # 2. Invoices com falha bruta de extração do LLM (Sem Valor Total)
        q_null_amount_invoice = f"""
        MATCH (i:Invoice:`{safe_tenant}`)
        WHERE i.total_amount IS NULL AND NOT i:GHOST_DATA
        SET i:GHOST_DATA, i.quarantine_reason = "Null total_amount"
        RETURN count(i) as isolated
        """

        # 3. Transações Bancárias flutuantes sem Conta (Omission de BankAccount)
        q_orphan_transaction = f"""
        MATCH (tr:Transaction:`{safe_tenant}`)
        WHERE NOT ()-[:HAS_TRANSACTION]->(tr) AND NOT tr:GHOST_DATA
        SET tr:GHOST_DATA, tr.quarantine_reason = "Missing BankAccount Parent"
        RETURN count(tr) as isolated
        """

        report = {"ghost_invoices": 0, "ghost_transactions": 0}

        try:
            with self.ontology_manager.driver.session() as session:
                r1 = session.run(q_orphan_invoice_vendor).single()
                r2 = session.run(q_null_amount_invoice).single()
                r3 = session.run(q_orphan_transaction).single()

                report["ghost_invoices"] = (r1["isolated"] if r1 else 0) + (
                    r2["isolated"] if r2 else 0
                )
                report["ghost_transactions"] = r3["isolated"] if r3 else 0

        except Exception as e:
            logger.error(f"🚨 Falha crítica no Scanner de Fantasmas: {e}")
            return report

        total_ghosts = report["ghost_invoices"] + report["ghost_transactions"]

        if total_ghosts > 0:
            logger.critical(
                f"⚠️ ALERTA DE QUARENTENA: O Sanitizer isolou {total_ghosts} Fragmentos Fantasmas! "
                f"(Invoices Corrompidas: {report['ghost_invoices']} | "
                f"Transactions Órfãs: {report['ghost_transactions']}). "
                f"Uma varredura manual de reparo via UI Synapse é necessária."
            )
        else:
            logger.info(
                "✅ Sanity Check concluído. A integridade do Grafo está em 100%. Nenhum fantasma encontrado."
            )

        return report


if __name__ == "__main__":
    pass
