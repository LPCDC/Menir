"""
Menir Core V5.1 - Crésus Exporter
Synthesizes the [:RECONCILED] edges of the Neo4j Graph into a perfectly
compliant, tab-separated, CRLF-terminated text file for the Swiss Crésus ERP.
"""

import asyncio
import logging
import os
import json
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger("CresusExporter")

# Hardcoded Mappings conforming to Architect rule
TVA_CODE_MAP = {
    8.1: "I81",
    3.8: "I38",
    2.6: "I26"
}

class CresusExporter:
    def __init__(self, ontology_manager):
        self.ontology_manager = ontology_manager

    def _get_account_mapping(self, tenant: str, type_acc: str) -> str:
        """
        Placeholder logic for the main bank account mappings.
        """
        if type_acc == "DEBIT":
            return "1020"  # Banco
        return "3400"  # Default Fornecedor (Will be overridden by node property)

    def _format_swiss_date(self, iso_date_str: str) -> str:
        """Converte YYYY-MM-DD (Neo4j native) para DD.MM.YYYY (Crésus Form)."""
        if not iso_date_str:
            return ""
        try:
            d = datetime.strptime(iso_date_str.split("T")[0], "%Y-%m-%d")
            return d.strftime("%d.%m.%Y")
        except Exception:
            # Fallback tolerante se já vier bizarro, ou falhar no cast
            parts = iso_date_str.split("-")
            if len(parts) == 3:
                return f"{parts[2]}.{parts[1]}.{parts[0]}"
            return iso_date_str

    async def export_reconciled(self, tenant: str, export_dir: str = "Menir_Cresus_Out") -> str | None:
        """
        Queries the Graph for Reconciled Transactions and streams them to a .txt file.
        Utilizes aiofiles to prevent blocking the Event Loop during I/O Disk writing.
        """
        import aiofiles

        # O Ponto Cego de Performance: Nós vamos delegar o tráfego da rede do Driver Neo4j
        # para uma thread síncrona, e aguardar os resultados.
        records = await asyncio.to_thread(self._fetch_reconciled_graph, tenant)

        if not records:
            logger.info(f"🚫 [CresusExporter] Nenhuma fatura nova reconciliada para {tenant}.")
            return None

        os.makedirs(export_dir, exist_ok=True)
        filename = f"import_cresus_{tenant}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        filepath = os.path.join(export_dir, filename)

        logger.info(f"🗃️ [CresusExporter] Escrevendo {len(records)} lançamentos em I/O Assíncrono.")

        # AIOFILES protege a fila do Watchdog contra Disk I/O Bottlenecks
        async with aiofiles.open(filepath, mode="w", encoding="utf-8", newline="") as f:
            for r in records:
                swiss_date = self._format_swiss_date(r.get("issue_date", ""))
                compte_debit = self._get_account_mapping(tenant, "DEBIT")
                
                cresus_account_id = r.get("cresus_account_id")
                compte_credit = cresus_account_id if cresus_account_id else "3400"
                
                piece = str(r.get("vendor_name", ""))[:10]
                libelle = f"Facture {r.get('vendor_name', '')} / {swiss_date}"
                
                if not cresus_account_id:
                    libelle += " [REVIEW_ACCOUNT]"
                
                items_json_str = r.get("line_items_json", "[]")
                try:
                    items = json.loads(items_json_str) if items_json_str else []
                except Exception:
                    items = []

                if not items:
                    # Fallback single line without TVA mapping if JSON is missing
                    montant_str = f"{r.get('total_amount', 0.0):.2f}"
                    line = f"{swiss_date}\t{compte_debit}\t{compte_credit}\t{piece}\t{libelle}\t{montant_str}\t\t\t\t1\t\t\r\n"
                    await f.write(line)
                    continue

                # Agrupamento inteligente por alíquota (TVA groups)
                tva_groups: dict[float, float] = defaultdict(float)
                for item in items:
                    tva_rate = item.get("tva_rate_applied")
                    tva_rate = float(tva_rate) if tva_rate is not None else 0.0
                    tva_groups[tva_rate] += float(item.get("gross_amount", 0.0))
                
                for tva_rate, amount in tva_groups.items():
                    if amount == 0:
                        continue
                        
                    tva_code = TVA_CODE_MAP.get(tva_rate, "")
                    montant_str = f"{amount:.2f}"
                    
                    # Colunas do formato étendu epsitec (.txt TSV)
                    # 1. Date (DD.MM.YYYY)
                    # 2. Débit
                    # 3. Crédit
                    # 4. Pièce
                    # 5. Libellé
                    # 6. Montant (Brut)
                    # 7. TVA Opt (vazio)
                    # 8. Monnaie (vazio)
                    # 9. Cours (vazio)
                    # 10. Net/Brut (1 = Brut)
                    # 11. Empty
                    # 12. Code TVA (ex: I81)
                    line = f"{swiss_date}\t{compte_debit}\t{compte_credit}\t{piece}\t{libelle}\t{montant_str}\t\t\t\t1\t\t{tva_code}\r\n"
                    await f.write(line)

            # O TODO de :[RECONCILED] para {exported: True} se mantém.

        logger.info(f"✅ [CresusExporter] Arquivo TSV Extended (TVA) gerado: {filepath}")

        # Marcar aresta [:RECONCILED] como exported=True para garantir idempotência.
        # Apenas chamado após a escrita do arquivo confirmar sucesso.
        edge_ids = [r["edge_id"] for r in records if r.get("edge_id")]
        if edge_ids:
            await asyncio.to_thread(self._mark_exported, edge_ids)

        return filepath

    def _fetch_reconciled_graph(self, tenant: str) -> list:
        """Synchronous Worker running inside asyncio.to_thread"""
        # Notice we extract the invoice amount just to be sure, and the vendor properties
        query = """
        // SECURITY: Parameter $tenant is injected strictly by isolated ContextVar upstream.
        // It never comes from direct user input.
        MATCH (t:Tenant {name: $tenant})-[:RECEIVED]->(i:Invoice)-[r:RECONCILED]->(tr:Transaction)
        MATCH (v:Vendor)-[:ISSUED]->(i)
        WHERE r.exported IS NULL
        RETURN i.issue_date AS issue_date,
               i.total_amount AS total_amount,
               i.line_items_json AS line_items_json,
               v.name AS vendor_name,
               v.cresus_account_id AS cresus_account_id,
               elementId(r) AS edge_id
        """
        try:
            with self.ontology_manager.driver.session() as session:
                result = session.run(query, tenant=tenant)
                # Cast the driver iterable to a native RAM list to free the pool
                return [record.data() for record in result]
        except Exception as e:
            logger.exception(f"Failed Cypher Reconciled Extraction: {e}")
            return []

    def _mark_exported(self, edge_ids: list[str]) -> None:
        """Flags :RECONCILED edges as exported to guarantee idempotência.
        Runs synchronously inside asyncio.to_thread after successful file write.
        """
        query = """
        UNWIND $edge_ids AS eid
        MATCH ()-[r:RECONCILED]->() WHERE elementId(r) = eid
        SET r.exported = true, r.exported_at = datetime()
        """
        try:
            with self.ontology_manager.driver.session() as session:
                session.run(query, edge_ids=edge_ids)
            logger.info(f"📦 [CresusExporter] {len(edge_ids)} arestas [:RECONCILED] marcadas como exported=True.")
        except Exception as e:
            logger.exception(f"Failed to mark edges as exported: {e}")


if __name__ == "__main__":
    pass
