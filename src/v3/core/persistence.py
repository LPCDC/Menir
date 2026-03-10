import asyncio
import uuid
from typing import Any

from src.v3.core.schemas.identity import TenantContext
from src.v3.core.schemas.base import BaseNode, Document
from src.v3.core.schemas.financial import InvoiceData
from src.v3.core.schemas.operational import (
    ClientNode, EmployeeNode, TaxDossierNode, InsuranceNode, SalarySlipNode, TVADeclarationNode
)

class OrphanNodeError(Exception):
    """Exceção levantada quando um nó não tem documento de origem rastreável."""
    pass

class NodePersistenceOrchestrator:
    """
    Camada única de persistência.
    As skills devem apenas extrair e retornar nós Pydantic válidos.
    O orquestrador cuida do MERGE Cypher, Tenant Isolation e Rastreabilidade (FINMA).
    """

    async def persist(self, node: BaseNode, tx: Any) -> str:
        tenant_id = TenantContext.get()
        if not tenant_id:
            raise ValueError("Isolamento violado. Nenhum Tenant ativo configurado.")
            
        safe_tenant = tenant_id.replace("`", "")

        origin_uid = getattr(node, "source_document_uid", None)

        if not isinstance(node, Document):
            if not origin_uid:
                raise OrphanNodeError(f"Nó {type(node).__name__} rejeitado. Falta source_document_uid para rastreabilidade FINMA.")
                
            def _check_doc():
                q = f"MATCH (d:Document:`{safe_tenant}` {{uid: $uid}}) RETURN d"
                return tx.run(q, uid=origin_uid).single()
                
            doc_record = await asyncio.to_thread(_check_doc)
            if not doc_record:
                raise OrphanNodeError(f"Origem fantasma! DocumentNode com uid '{origin_uid}' não existe no grafo.")

        if not hasattr(node, "uid") or not node.uid:
            node.uid = str(uuid.uuid4())

        await self._merge_node(node, safe_tenant, tx)

        def _apply_governance():
            tenant_q = f"""
            MATCH (n:`{safe_tenant}` {{uid: $uid}})
            MERGE (t:Tenant {{name: $tenant_safe}})
            MERGE (n)-[:BELONGS_TO_TENANT]->(t)
            """
            tx.run(tenant_q, uid=node.uid, tenant_safe=safe_tenant)
            
            if not isinstance(node, Document) and origin_uid:
                derived_q = f"""
                MATCH (n:`{safe_tenant}` {{uid: $n_uid}})
                MATCH (d:Document:`{safe_tenant}` {{uid: $doc_uid}})
                MERGE (n)-[:DERIVED_FROM]->(d)
                """
                tx.run(derived_q, n_uid=node.uid, doc_uid=origin_uid)
                
        await asyncio.to_thread(_apply_governance)

        return node.uid

    async def _merge_node(self, node: BaseNode, safe_tenant: str, tx: Any):
        if isinstance(node, Document):
            q = f"""
            MERGE (n:Document:`{safe_tenant}` {{uid: $uid}})
            SET n.file_hash = $sha256,
                n.name = $name,
                n.source = $source,
                n.status = $status,
                n.project = $project
            """
            await asyncio.to_thread(lambda: tx.run(q, uid=node.uid, sha256=node.sha256, name=node.name, source=node.source, status=node.status.value, project=safe_tenant))

        elif isinstance(node, ClientNode):
            q = f"MERGE (n:ClientNode:`{safe_tenant}` {{uid: $uid}}) SET n.name = $name, n.client_type = $client_type, n.ide_number = $ide_number, n.address = $address, n.project = $project"
            await asyncio.to_thread(lambda: tx.run(q, uid=node.uid, name=node.name, client_type=node.client_type, ide_number=node.ide_number, address=node.address, project=safe_tenant))

        elif isinstance(node, EmployeeNode):
            q = f"MERGE (n:EmployeeNode:`{safe_tenant}` {{uid: $uid}}) SET n.full_name = $full_name, n.avs_number = $avs_number, n.role = $role, n.hiring_date = $hiring_date, n.project = $project"
            await asyncio.to_thread(lambda: tx.run(q, uid=node.uid, full_name=node.full_name, avs_number=node.avs_number, role=node.role, hiring_date=node.hiring_date, project=safe_tenant))

        elif isinstance(node, TaxDossierNode):
            q = f"MERGE (n:TaxDossierNode:`{safe_tenant}` {{uid: $uid}}) SET n.year = $year, n.tax_authority = $tax_authority, n.status = $status, n.project = $project"
            await asyncio.to_thread(lambda: tx.run(q, uid=node.uid, year=node.year, tax_authority=node.tax_authority, status=node.status, project=safe_tenant))

        elif isinstance(node, InsuranceNode):
            q = f"MERGE (n:InsuranceNode:`{safe_tenant}` {{uid: $uid}}) SET n.policy_number = $policy_number, n.provider_name = $provider_name, n.insurance_type = $insurance_type, n.project = $project"
            await asyncio.to_thread(lambda: tx.run(q, uid=node.uid, policy_number=node.policy_number, provider_name=node.provider_name, insurance_type=node.insurance_type, project=safe_tenant))

        elif isinstance(node, SalarySlipNode):
            q = f"MERGE (n:SalarySlipNode:`{safe_tenant}` {{uid: $uid}}) SET n.period = $period, n.gross_salary = $gross_salary, n.net_salary = $net_salary, n.avs_deduction = $avs_deduction, n.lpp_deduction = $lpp_deduction, n.project = $project"
            await asyncio.to_thread(lambda: tx.run(q, uid=node.uid, period=node.period, gross_salary=node.gross_salary, net_salary=node.net_salary, avs_deduction=node.avs_deduction, lpp_deduction=node.lpp_deduction, project=safe_tenant))

        elif isinstance(node, TVADeclarationNode):
            q = f"MERGE (n:TVADeclarationNode:`{safe_tenant}` {{uid: $uid}}) SET n.period = $period, n.total_sales = $total_sales, n.tva_collected = $tva_collected, n.tva_deductible = $tva_deductible, n.amount_due = $amount_due, n.project = $project"
            await asyncio.to_thread(lambda: tx.run(q, uid=node.uid, period=node.period, total_sales=node.total_sales, tva_collected=node.tva_collected, tva_deductible=node.tva_deductible, amount_due=node.amount_due, project=safe_tenant))

        elif isinstance(node, InvoiceData):
            q = f"""
            MERGE (n:Invoice:`{safe_tenant}` {{uid: $uid}})
            SET n.vendor_name = $vendor_name,
                n.doc_type = $doc_type,
                n.ide_number = $ide_number,
                n.avs_number = $avs_number,
                n.language = $language,
                n.vendor_iban = $vendor_iban,
                n.currency = $currency,
                n.issue_date = $issue_date,
                n.subtotal = $subtotal,
                n.tips = $tips,
                n.total_amount = $total_amount,
                n.requires_justification = $requires_justification,
                n.project = $project
            
            WITH n
            MATCH (v:Vendor:`{safe_tenant}` {{name: $vendor_name}})
            MERGE (v)-[:ISSUED_BY]->(n)
            """
            items_list = [i.model_dump() for i in node.items]
            q_items = f"""
            MATCH (n:Invoice:`{safe_tenant}` {{uid: $uid}})
            UNWIND $items_list AS item
            MERGE (li:LineItem:`{safe_tenant}` {{invoice_uid: $uid, description: item.description}})
            SET li.gross_amount = item.gross_amount,
                li.tva_rate_applied = item.tva_rate_applied,
                li.project = $project
            MERGE (n)-[:CONTAINS]->(li)
            """
            def _run_inv():
                tx.run(q, uid=node.uid, vendor_name=node.vendor_name, doc_type=node.doc_type, ide_number=node.ide_number,
                            avs_number=node.avs_number, language=node.language, vendor_iban=node.vendor_iban,
                            currency=node.currency, issue_date=node.issue_date, subtotal=node.subtotal,
                            tips=node.tip_or_unregulated_amount, total_amount=node.total_amount,
                            requires_justification=node.requires_manual_justification, project=safe_tenant)
                tx.run(q_items, uid=node.uid, items_list=items_list, project=safe_tenant)
            await asyncio.to_thread(_run_inv)
        else:
            raise ValueError(f"Orquestrador não sabe persistir o nó do tipo: {type(node).__name__}")
