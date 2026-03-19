"""
Menir Core V5.1 - Camt053 Banking Skill
Deterministic parser for ISO 20022 camt.053 XML bank statements.
Zero Intelligence (No LLM). Pure Cypher componentization.
"""

import logging
import os
import xml.etree.ElementTree as ET

from src.v3.core.menir_runner import SkillResult
from src.v3.meta_cognition import MenirOntologyManager

logger = logging.getLogger("Camt053Skill")


class Camt053Skill:
    """
    Skill de processamento determinístico para extratos bancários Suíços (Camt.053).
    A extração é estanque à falha e guiada puramente pela ontologia do XML, sem I.A.
    """

    def __init__(self, ontology_manager: MenirOntologyManager):
        self.ontology_manager = ontology_manager

    async def process_statement(self, file_path: str, tenant: str = "BECO") -> SkillResult:
        """
        Lê e parseia o extrato XML determinístico.
        """
        logger.info(f"🏦 Iniciando Parse Bancário Camt.053: {file_path}")

        if not os.path.exists(file_path):
            return SkillResult(
                success=False, nodes_and_edges=[], message="Arquivo XML não encontrado."
            )

        try:
            import hashlib
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            return SkillResult(success=False, nodes_and_edges=[], message=str(e))

        try:
            # 1. Parsing Determinístico (Placeholder estrutural para namespace/etiquetas)
            tree = ET.parse(file_path)
            root = tree.getroot()

            # Namespace flexivel
            ns_uri = root.tag.split("}")[0][1:] if "}" in root.tag else "urn:iso:std:iso:20022:tech:xsd:camt.053.001.02"
            ns = {"ns": ns_uri}

            transactions = []
            acct_iban = root.findtext(".//ns:Acct/ns:Id/ns:IBAN", namespaces=ns) or "UNKNOWN_IBAN"

            for entry in root.findall(".//ns:Ntry", namespaces=ns):
                tx_id = (
                    entry.findtext("ns:NtryRef", namespaces=ns)
                    or entry.findtext(".//ns:AcctSvcrRef", namespaces=ns)
                    or entry.findtext("ns:AddtlNtryInf", namespaces=ns)
                    or str(uuid.uuid4())[:8]
                )
                amount_str = entry.findtext("ns:Amt", namespaces=ns) or "0"
                cd_ind = entry.findtext(".//ns:CdtDbtInd", namespaces=ns) or "CRDT"
                booking_date = (
                    entry.findtext("ns:BookgDt/ns:Dt", namespaces=ns)
                    or (entry.findtext("ns:BookgDt/ns:DtTm", namespaces=ns) or "")[:10]
                    or entry.findtext("ns:Dt", namespaces=ns)
                )
                remittance = entry.findtext(".//ns:RmtInf/ns:Ustrd", namespaces=ns) or ""
                
                # Capturar Devedor (Foco no Ultimate Debtor para faturas)
                debtor_name = (
                    entry.findtext(".//ns:RltdPties/ns:UltmtDbtr/ns:Nm", namespaces=ns)
                    or entry.findtext(".//ns:RltdPties/ns:Dbtr/ns:Nm", namespaces=ns)
                    or ""
                )

                try:
                    amount = float(amount_str)
                except ValueError:
                    amount = 0.0

                if cd_ind == "DBIT":
                    amount = -amount

                transactions.append(
                    {
                        "tx_id": tx_id,
                        "amount": amount,
                        "currency": "CHF",
                        "booking_date": booking_date or "",
                        "debtor_name": debtor_name,
                        "remittance_info": remittance,
                        "acct_iban": acct_iban,
                    }
                )

            # 2. Injeção Idempotente no Neo4j
            if transactions:
                try:
                    self._inject_transactions_into_graph(transactions, tenant)
                except Exception as e:
                    if str(e) == "TRANSACTION_ROLLBACK":
                        self._quarantine_document(tenant, file_hash, "TRANSACTION_ROLLBACK")
                        return SkillResult(
                            success=False, nodes_and_edges=[], message="Injeção falhou: TRANSACTION_ROLLBACK"
                        )
                    raise

            return SkillResult(
                success=True,
                nodes_and_edges=[],
                message=f"Camt053 processado: {len(transactions)} transações injetadas.",
            )

        except ET.ParseError as e:
            logger.exception(f"Erro de Parse XML fatal: {e}")
            return SkillResult(
                success=False, nodes_and_edges=[], message=f"Formato XML corrompido: {e}"
            )
        except Exception as e:
            logger.exception(f"Erro ao processar Camt053: {e}")
            return SkillResult(success=False, nodes_and_edges=[], message=f"Erro estrutural: {e}")

    def _inject_transactions_into_graph(self, transactions: list, tenant: str):
        """
        Materializa as transações contábeis no Neo4j.
        Cria o nó (Transaction) e o atrela à (BankAccount), que por sua vez se atrela ao (Tenant).
        Totalmente idempotente.
        """
        safe_tenant = tenant.replace("`", "")

        query = f"""
        UNWIND $transactions AS tx
        
        // 1. O Tenant
        MERGE (t:Tenant {{name: $tenant}})
        
        // 2. A Conta Bancária
        MERGE (ba:BankAccount:`{safe_tenant}` {{iban: tx.acct_iban}})
        MERGE (t)-[:OWNS_ACCOUNT]->(ba)

        // 3. A Transacao de forma Idempotente (Pelo tx_id bancario)
        MERGE (tr:Transaction:`{safe_tenant}` {{tx_id: tx.tx_id}})
        SET tr.amount = tx.amount,
            tr.currency = tx.currency,
            tr.booking_date = tx.booking_date,
            tr.debtor_name = tx.debtor_name,
            tr.remittance_info = tx.remittance_info,
            tr.ingested_at = datetime()
            
        // 4. Aresta de Posse (A BankAccount possui esta Transação)
        MERGE (ba)-[:HAS_TRANSACTION]->(tr)
        """

        try:
            with self.ontology_manager.driver.session() as session:
                with session.begin_transaction() as tx:
                    tx.run(query, tenant=tenant, transactions=transactions)
            logger.info(
                f"Injection Cypher concluida: {len(transactions)} transacoes bancarias enraizadas no Tenant '{tenant}'."
            )
        except Exception as e:
            logger.exception(f"Erro transacional ao injetar no Neo4j: {e}")
            raise Exception("TRANSACTION_ROLLBACK")

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
