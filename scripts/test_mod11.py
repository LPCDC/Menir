from src.v3.skills.invoice_skill import InvoiceData, InvoiceLineItem
from pydantic import ValidationError

def run_tests():
    print("--- 🔬 Iniciando Auditoria MOD11 Suíça ---")
    
    test_cases = [
        ("Google Switzerland GmbH", "CHE-109.322.551", True),
        ("Credit Suisse (Invalid UID format)", "CHE-106.832.652", False),
        ("PostFinance (Invalid UID format)", "CHE-107.037.149", False),
        ("Alucinação de LLM 1", "CHE-109.322.552", False),
        ("Sintaxe com TVA Opcional", "CHE-116.320.051 TVA", False) # 116.320.051 throws Check=10, invalid
    ]

    for vendor, uid, expected_valid in test_cases:
        try:
            # We initialize a mock compliant InvoiceData payload to test the validator
            InvoiceData(
                vendor_name=vendor,
                vendor_uid=uid,
                currency="CHF",
                issue_date="2024-05-15",
                subtotal=100.0,
                tip_or_unregulated_amount=0.0,
                total_amount=100.0,
                items=[InvoiceLineItem(description="Test", gross_amount=100.0)]
            )
            result = True
            msg = "Passou na Validação"
        except ValidationError as e:
            result = False
            msg = str(e).replace('\n', ' | ')

        if result == expected_valid:
            print(f"✅ [SUCCESS] {vendor} ({uid}) | Comportamento esperado atingido. (Valid={result})")
        else:
            print(f"❌ [FAILURE] {vendor} ({uid}) | Anomalia nas Expectativas! Esperado={expected_valid}, Resultado={result} | Msg: {msg}")

if __name__ == "__main__":
    run_tests()
