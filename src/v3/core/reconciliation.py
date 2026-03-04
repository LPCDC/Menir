"""
Menir Core V5.1 - Hybrid Reconciliation Engine
Orchestrates Cypher-based matching algorithms to bind Invoices to Bank Transactions.
Establishes Tiers of confidence for accounting auto-reconciliation.
"""

import logging

from src.v3.meta_cognition import MenirOntologyManager

logger = logging.getLogger("ReconciliationEngine")


from src.v3.core.schemas.identity import TenantContext

class ReconciliationEngine:
    def __init__(self, ontology_manager: MenirOntologyManager):
        self.ontology_manager = ontology_manager

    def run_matching_cycle(self):
        """
        Executes the hierarchical Cypher cascading match between Invoices and Transactions.
        """
        tenant = TenantContext.get()
        if not tenant:
            raise ValueError("Reconciliation requires an active TenantContext.")
            
        logger.info(f"🔄 Iniciando Ciclo de Reconciliação para o Tenant: {tenant}")
        self._tier_1_exact_match(tenant)
        self._tier_2_fuzzy_match(tenant)
        logger.info(f"✅ Ciclo de Reconciliação finalizado para {tenant}.")

    def _tier_1_exact_match(self, tenant: str):
        """
        TIER 1 (Exact Match):
        Tolerance of 0.05 on amount, payment within 30 days after invoice issue.
        """
        safe_tenant = tenant.replace("`", "")
        query = f"""
        // TIER 1: EXACT MATCH
        MATCH (t:Tenant {{name: $tenant}})-[:RECEIVED]->(i:Invoice:`{safe_tenant}`)
        WHERE NOT (i)-[:RECONCILED]->() AND NOT (i)-[:RECONCILED_NEEDS_REVIEW]->()
          AND i.total_amount IS NOT NULL AND i.issue_date IS NOT NULL

        MATCH (t)-[:OWNS_ACCOUNT]->(ba:BankAccount)-[:HAS_TRANSACTION]->(tr:Transaction:`{safe_tenant}`)
        WHERE NOT ()-[:RECONCILED]->(tr) AND NOT ()-[:RECONCILED_NEEDS_REVIEW]->(tr)
          AND tr.amount IS NOT NULL AND tr.booking_date IS NOT NULL

        // Constraints
        WITH i, tr, abs(i.total_amount - abs(tr.amount)) AS delta,
             duration.inDays(date(i.issue_date), date(tr.booking_date)).days AS days_diff
               # noqa: W293
        WHERE delta <= 0.05   # noqa: W291
          AND days_diff >= 0   # noqa: W291
          AND days_diff <= 30
          AND i.currency = tr.currency

        // Materialize
        MERGE (i)-[r:RECONCILED]->(tr)
        SET r.confidence = "HIGH", r.delta = delta, r.reconciled_at = datetime()
          # noqa: W293
        RETURN count(r) as matched_count
        """
        with self.ontology_manager.driver.session() as session:
            result = session.run(query, tenant=tenant).single()
            count = result["matched_count"] if result else 0
            logger.info(f"🎯 [TIER 1] Exact Matches encontrados e reconciliados: {count}")

    def _tier_2_fuzzy_match(self, tenant: str):
        """
        TIER 2 (Fuzzy Match):
        Delta up to 5% (to absorb FX rates), payment within 45 days after invoice issue.
        """
        safe_tenant = tenant.replace("`", "")
        query = f"""
        // TIER 2: FUZZY MATCH
        MATCH (t:Tenant {{name: $tenant}})-[:RECEIVED]->(i:Invoice:`{safe_tenant}`)
        WHERE NOT (i)-[:RECONCILED]->() AND NOT (i)-[:RECONCILED_NEEDS_REVIEW]->()
          AND i.total_amount IS NOT NULL AND i.issue_date IS NOT NULL

        MATCH (t)-[:OWNS_ACCOUNT]->(ba:BankAccount)-[:HAS_TRANSACTION]->(tr:Transaction:`{safe_tenant}`)
        WHERE NOT ()-[:RECONCILED]->(tr) AND NOT ()-[:RECONCILED_NEEDS_REVIEW]->(tr)
          AND tr.amount IS NOT NULL AND tr.booking_date IS NOT NULL

        // Constraints
        WITH i, tr, abs(i.total_amount - abs(tr.amount)) AS delta,
             duration.inDays(date(i.issue_date), date(tr.booking_date)).days AS days_diff
               # noqa: W293
        // Fuzzy margin: delta <= 5% of invoice total
        WHERE delta <= (i.total_amount * 0.05)
          AND days_diff >= 0   # noqa: W291
          AND days_diff <= 45
          AND i.currency = tr.currency

        // Materialize
        MERGE (i)-[r:RECONCILED_NEEDS_REVIEW]->(tr)
        SET r.confidence = "MEDIUM", r.delta = delta, r.reconciled_at = datetime()
          # noqa: W293
        RETURN count(r) as matched_count
        """
        with self.ontology_manager.driver.session() as session:
            result = session.run(query, tenant=tenant).single()
            count = result["matched_count"] if result else 0
            logger.info(f"⚠️ [TIER 2] Fuzzy Matches encaminhados para revisão: {count}")

    def get_quarantine_nodes(self) -> dict:
        """
        TIER 3 (Quarantine / Orphans):
        Returns Invoices and Transactions older than 45 days without reconciliation,
        or those with critical extraction failures (missing amounts/dates).
        """
        tenant = TenantContext.get()
        if not tenant:
            raise ValueError("Quarantine scan requires an active TenantContext.")
            
        safe_tenant = tenant.replace("`", "")

        invoice_query = f"""
        MATCH (t:Tenant {{name: $tenant}})-[:RECEIVED]->(i:Invoice:`{safe_tenant}`)
        WHERE NOT (i)-[:RECONCILED]->() AND NOT (i)-[:RECONCILED_NEEDS_REVIEW]->()
        WITH i,   # noqa: W291
             CASE WHEN i.issue_date IS NOT NULL   # noqa: W291
                  THEN duration.inDays(date(i.issue_date), date()).days   # noqa: W291
                  ELSE 999   # noqa: W291
             END AS days_old
        WHERE days_old > 45 OR i.total_amount IS NULL OR i.issue_date IS NULL
        RETURN i {{.*}} AS properties
        """

        tx_query = f"""
        MATCH (t:Tenant {{name: $tenant}})-[:OWNS_ACCOUNT]->(ba:BankAccount)-[:HAS_TRANSACTION]->(tr:Transaction:`{safe_tenant}`)
        WHERE NOT ()-[:RECONCILED]->(tr) AND NOT ()-[:RECONCILED_NEEDS_REVIEW]->(tr)
        WITH tr,   # noqa: W291
             CASE WHEN tr.booking_date IS NOT NULL   # noqa: W291
                  THEN duration.inDays(date(tr.booking_date), date()).days   # noqa: W291
                  ELSE 999   # noqa: W291
             END AS days_old
        WHERE days_old > 45 OR tr.amount IS NULL OR tr.booking_date IS NULL
        RETURN tr {{.*}} AS properties
        """

        from typing import Any
        payload: dict[str, list[dict[str, Any]]] = {"orphaned_invoices": [], "orphaned_transactions": []}

        try:
            with self.ontology_manager.driver.session() as session:
                inv_result = session.run(invoice_query, tenant=tenant)
                payload["orphaned_invoices"] = [r["properties"] for r in inv_result]

                tx_result = session.run(tx_query, tenant=tenant)
                payload["orphaned_transactions"] = [r["properties"] for r in tx_result]
        except Exception as e:
            logger.exception(f"Failed to query quarantine nodes: {e}")

        logger.info(
            f"☣️ [TIER 3] Quarentena isolou {len(payload['orphaned_invoices'])} Invoices e {len(payload['orphaned_transactions'])} Transactions órfãs."
        )
        return payload


if __name__ == "__main__":
    pass
