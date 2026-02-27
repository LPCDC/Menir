import sys
sys.path.append("/app")
from menir_core.governance.sanitizer import LGPDSanitizer

def test_sanitization():
    sanitizer = LGPDSanitizer()
    samples = [
        "Transferência de R$ 500,00 para Joao Silva referente a aluguel.",
        "Pix recebido de Maria Eduarda Souza.",
        "Boleto pago por Carlos Drummond de Andrade no vencimento.",
        "Ted enviada para conta de Pedro Alvares Cabral.",
        "Saque efetuado por Ana Clara."
    ]
    
    print(f"--- Sanitizer Dry Run ---")
    for s in samples:
        masked = sanitizer.mask_pii(s)
        print(f"Original: {s}")
        print(f"Masked:   {masked}")
        print("-" * 20)

if __name__ == "__main__":
    test_sanitization()
