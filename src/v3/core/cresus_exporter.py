"""
Menir Core V5.1 - Crésus Exporter
Synthesizes the [:RECONCILED] edges of the Neo4j Graph into a perfectly
compliant, tab-separated, CRLF-terminated text file for the Swiss Crésus ERP.
"""

import asyncio
import logging
import os
from datetime import datetime

logger = logging.getLogger("CresusExporter")


class CresusExporter:
    def __init__(self, ontology_manager):
        self.ontology_manager = ontology_manager

    def _get_account_mapping(self, tenant: str, type_acc: str) -> str:
        """
        Placeholder logic for account numbering mapping.
        (Awaiting client mappings CSV).
        """
        if type_acc == "DEBIT":
            return "1020"  # Exemplo: Banco
        return "3400"  # Exemplo: Fornecedores

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
        async with aiofiles.open(filepath, mode="w", encoding="utf-8") as f:
            # Write Headers (opcional no Cresus, mas as vezes exigido dependendo da mascara, usaremos os dados cru)
            # A Ordem Mestra: [Date (DD.MM.YYYY), Compte Débit, Compte Crédit, Pièce, Libellé, Montant]
            for r in records:
                swiss_date = self._format_swiss_date(r["issue_date"])
                compte_debit = self._get_account_mapping(tenant, "DEBIT")
                compte_credit = self._get_account_mapping(tenant, "CREDIT")
                # Piece é opcional ou numero da nota. Usaremos o Node ElementId short ou nome do Fornecedor.
                piece = r["vendor_name"][:10]
                libelle = f"Facture {r['vendor_name']} / {swiss_date}"
                montant = f"{r['amount']:.2f}"

                # A Linha de Cristal (CRLF \r\n explicitly forced here by text format mapping)
                # Formação do TabSeparated.
                line = f"{swiss_date}\t{compte_debit}\t{compte_credit}\t{piece}\t{libelle}\t{montant}\r\n"

                await f.write(line)

            # TODO: Idealmente, neste loop, marcaríamos a aresta [:RECONCILED] com um status: EXPORTED: True
            # para não puxá-las amanhã de novo. A tese fica estabelecida no Grafo por enquanto.

        logger.info(f"✅ [CresusExporter] Arquivo gerado puramente em TXT Legacy: {filepath}")
        return filepath

    def _fetch_reconciled_graph(self, tenant: str) -> list:
        """Synchronous Worker running inside asyncio.to_thread"""
        safe_tenant = tenant.replace("`", "")
        # Notice we extract the invoice amount just to be sure, and the vendor properties
        query = f"""
        MATCH (t:Tenant {{name: $tenant}})-[:RECEIVED]->(i:Invoice:`{safe_tenant}`)-[r:RECONCILED]->(tr:Transaction:`{safe_tenant}`)
        MATCH (v:Vendor)-[:ISSUED]->(i)
        // Add safeguard to only pick un-exported, mocked for now
        // WHERE r.exported IS NULL
        RETURN i.issue_date AS issue_date,   # noqa: W291
               tr.amount AS amount,   # noqa: W291
               v.name AS vendor_name
        """
        try:
            with self.ontology_manager.driver.session() as session:
                result = session.run(query, tenant=tenant)
                # Cast the driver iterable to a native RAM list to free the pool
                return [record.data() for record in result]
        except Exception as e:
            logger.exception(f"Failed Cypher Reconciled Extraction: {e}")
            return []


if __name__ == "__main__":
    pass
