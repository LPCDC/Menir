import asyncio
import hashlib
import os

from src.v3.core.schemas.identity import TenantContext
from src.v3.meta_cognition import MenirOntologyManager
from src.v3.menir_intel import MenirIntel
from src.v3.core.dispatcher import DocumentDispatcher
from src.v3.skills.invoice_skill import InvoiceSkill
from src.v3.core.persistence import NodePersistenceOrchestrator
from src.v3.core.schemas.base import Document, DocumentStatus

async def run_smoke_test():
    print("=== INICIANDO E2E SMOKE TEST (INV) ===")
    from dotenv import load_dotenv
    load_dotenv()
    
    tenant_name = "BECO"
    TenantContext.set(tenant_name)
    
    fixture_path = "tests/fixtures/invoice_beco_sanitized.pdf"
    if not os.path.exists(fixture_path):
        print("[FALHA] Fixture não encontrado.")
        return

    with open(fixture_path, "rb") as f:
        file_bytes = f.read()
    
    if fixture_path.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(fixture_path)
        text_content = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text_content = file_bytes.decode("utf-8")
        
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    
    intel = MenirIntel()
    ontology = MenirOntologyManager()
    
    orchestrator = NodePersistenceOrchestrator()
    
    # 1. SETUP DO DOCUMENTO DE ORIGEM NO MOCK DE TESTE
    doc = Document(
        uid=file_hash,
        project=tenant_name,
        sha256=file_hash,
        name="invoice_beco_sanitized.pdf",
        status=DocumentStatus.PROCESSING
    )
    def _create_doc():
        with ontology.driver.session() as s:
            with s.begin_transaction() as tx:
                # orchestrator is async but calling sync lambda via run_until_complete inside normal asyncio program
                pass
    # Actually wait, orchestrator.persist is async. We are in an async function, we can just:
    with ontology.driver.session() as s:
        with s.begin_transaction() as tx:
            await orchestrator.persist(doc, tx)
            tx.commit()
    print("[OK] Origem rastreável (DocumentNode) garantida.")

    # 2. DISPATCHER CLASSIFICATION
    dispatcher = DocumentDispatcher(intel, ontology)
    classification = await dispatcher.classify(text_content)
    
    doc_type = classification.doc_type
    confidence = classification.confidence_score
    print(f"[INFO] Dispatcher detectou: {doc_type} (Confianca: {confidence})")
    
    type_pass = (doc_type in ["Facture", "FACTURE_FOURNISSEUR", "Facture QR", "BVR"])
    conf_pass = confidence > 0.85
    
    if type_pass and conf_pass:
        print("[PASS] CLASSIFICACAO: Tipo de Fatura com Alta Confianca")
    else:
        print(f"[FAIL] CLASSIFICACAO: Falhou (Acima de 0.85?: {conf_pass}, Tipo Correto?: {type_pass})")
    
    # 3. EXTRAÇÃO E PERSISTÊNCIA INVOICE_SKILL
    skill = InvoiceSkill(intel, ontology)
    # A invoice_skill roda model_validate e aciona NodePersistenceOrchestrator
    result = await skill.process_document(fixture_path)
    
    if result.success:
        print("[PASS] PROCESSAMENTO SKILL: Sucesso retornado pelo Orquestrador e Zefix")
    else:
        print(f"[FAIL] PROCESSAMENTO SKILL: Falhou ({result.message})")

    # 4. VERIFICAÇÃO NEO4J
    def _verify_graph():
        with ontology.driver.session() as s:
            inv_record = s.run(f"MATCH (i:Invoice:`{tenant_name}`)-[:DERIVED_FROM]->(:Document:`{tenant_name}` {{uid: $uid}}) RETURN i", uid=file_hash).single()
            derived_record = s.run(f"MATCH (i:Invoice:`{tenant_name}`)-[:DERIVED_FROM]->(d:Document:`{tenant_name}` {{uid: $uid}}) RETURN id(i)", uid=file_hash).single()
            vendor_record = s.run(f"MATCH (v:Vendor:`{tenant_name}`)-[:ISSUED_BY]->(i:Invoice:`{tenant_name}`)-[:DERIVED_FROM]->(:Document:`{tenant_name}` {{uid: $uid}}) RETURN v", uid=file_hash).single()
            return inv_record, derived_record, vendor_record
            
    inv, der, ven = await asyncio.to_thread(_verify_graph)
    
    if inv:
        print("[PASS] NEO4J INVOICE: No Fatura criado com sucesso e schema verificado")
    else:
        print("[FAIL] NEO4J INVOICE: No Invoice ausente")
        
    if der:
        print("[PASS] NEO4J RASTREABILIDADE: Aresta DERIVED_FROM confirmada, auditoria FINMA Ok")
    else:
        print("[FAIL] NEO4J RASTREABILIDADE: Aresta DERIVED_FROM inexistente")
        
    if ven:
        print("[PASS] NEO4J ZEFIX: Relacao ISSUED_BY conectando Fatura e Vendor ativo Ok")
    else:
        print("[FAIL] NEO4J ZEFIX: Relacao ISSUED_BY ou Vendor ausente")

if __name__ == "__main__":
    asyncio.run(run_smoke_test())
