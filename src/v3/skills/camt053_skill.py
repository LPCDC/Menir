"""
Menir Core V5.1 - Camt053 Banking Skill
Deterministic parser for ISO 20022 camt.053 XML bank statements.
Zero Intelligence (No LLM). Pure Cypher componentization.
"""
import os
import logging
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
            return SkillResult(success=False, nodes_and_edges=[], message="Arquivo XML não encontrado.")
            
        try:
            # 1. Parsing Determinístico (Placeholder estrutural para namespace/etiquetas)
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # Namespace typical de CAMT.053
            ns = {'ns': 'urn:iso:std:iso:20022:tech:xsd:camt.053.001.02'}
            
            transactions = []
            acct_iban = root.findtext(
                './/ns:Acct/ns:Id/ns:IBAN', namespaces=ns
            ) or "UNKNOWN_IBAN"

            for entry in root.findall('.//ns:Ntry', namespaces=ns):
                tx_id = (
                    entry.findtext('ns:NtryRef', namespaces=ns)
                    or entry.findtext('ns:AcctSvcrRef', namespaces=ns)
                    or entry.findtext('ns:AddtlNtryInf', namespaces=ns)
                )
                amount_str = entry.findtext('ns:Amt', namespaces=ns) or "0"
                cd_ind = entry.findtext('.//ns:CdtDbtInd', namespaces=ns) or "CRDT"
                booking_date = (
                    entry.findtext('ns:BookgDt/ns:Dt', namespaces=ns)
                    or (entry.findtext('ns:BookgDt/ns:DtTm', namespaces=ns) or "")[:10]
                )
                remittance = entry.findtext('.//ns:RmtInf/ns:Ustrd', namespaces=ns) or ""
                debtor_iban = entry.findtext('.//ns:Dbtr/ns:FinInstnId/ns:IBAN', namespaces=ns) or ""
                creditor_iban = entry.findtext('.//ns:Cdtr/ns:FinInstnId/ns:IBAN', namespaces=ns) or ""

                try:
                    amount = float(amount_str)
                except ValueError:
                    amount = 0.0

                if cd_ind == "DBIT":
                    amount = -amount

                if tx_id:
                    transactions.append({
                        "tx_id": tx_id,
                        "amount": amount,
                        "currency": "CHF",
                        "booking_date": booking_date or "",
                        "debtor_iban": debtor_iban,
                        "creditor_iban": creditor_iban,
                        "remittance_info": remittance,
                        "acct_iban": acct_iban,
                    })
                else:
                    logger.warning("Entrada sem tx_id ignorada — sem NtryRef nem AcctSvcrRef.")
            
            # 2. Injeção Idempotente no Neo4j
            if transactions:
                self._inject_transactions_into_graph(transactions, tenant)
                
            return SkillResult(
                success=True, 
                nodes_and_edges=[], 
                message=f"Camt053 processado: {len(transactions)} transações injetadas."
            )
            
        except ET.ParseError as e:
            logger.error(f"Erro de Parse XML fatal: {e}")
            return SkillResult(success=False, nodes_and_edges=[], message=f"Formato XML corrompido: {e}")
        except Exception as e:
            logger.error(f"Erro ao processar Camt053: {e}")
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
        
        // 2. A Conta Bancária (A conta cujo extrato estamos lendo - Ponto de Ancoragem)
        // Assume-se neste mock que o debtor ou creditor da nossa visão reflete nossa conta base
        // Iremos generalizar a BankAccount baseada no IBAN do Tenant extraído do cabeçalho do XML.
        // Simulando a extração do cabeçalho para amarrar as transações:
        MERGE (ba:BankAccount:`{safe_tenant}` {{iban: tx.acct_iban}})
        MERGE (t)-[:OWNS_ACCOUNT]->(ba)

        // 3. A Transação de forma Idempotente (Pelo tx_id bancário)
        MERGE (tr:Transaction:`{safe_tenant}` {{tx_id: tx.tx_id}})
        SET tr.amount = tx.amount,
            tr.currency = tx.currency,
            tr.booking_date = tx.booking_date,
            tr.debtor_iban = tx.debtor_iban,
            tr.creditor_iban = tx.creditor_iban,
            tr.remittance_info = tx.remittance_info,
            tr.ingested_at = datetime()
            
        // 4. Aresta de Posse (A BankAccount possui esta Transação)
        MERGE (ba)-[:HAS_TRANSACTION]->(tr)
        """
        
        with self.ontology_manager.driver.session() as session:
            session.run(query, tenant=tenant, transactions=transactions)
            logger.info(f"✅ Injeção Cypher concluída: {len(transactions)} transações bancárias enraizadas no Tenant '{tenant}'.")
