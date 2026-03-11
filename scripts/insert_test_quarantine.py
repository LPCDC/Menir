from src.v3.meta_cognition import MenirOntologyManager
o = MenirOntologyManager()
with o.driver.session() as s:
    s.run("MERGE (d:Document:BECO {uid:'dummy_12345'}) SET d.status='QUARANTINE', d.name='invoice_test_123.pdf', d.file_hash='test_hash', d.quarantined_at=datetime(), d.quarantine_reason='Missing TVA number'")
print("Mock quarantine document injected.")
