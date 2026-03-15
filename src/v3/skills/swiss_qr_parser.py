"""
Menir Core V5.1 - Swiss QR Parser (SIX v2.3 Standard)
Zero dependencias (Neo4j, FastAPI, Gemini). Módulo Puro de Domínio Contábil.
"""

from decimal import Decimal, InvalidOperation

class SwissQRParserError(Exception):
    pass

class SwissQRParser:
    def __init__(self):
        pass

    def parse(self, raw_payload: str) -> dict:
        lines = [line.strip('\r\n') for line in raw_payload.split('\n')]
        
        if len(lines) < 30:
            raise SwissQRParserError("Payload QR irregular ou incompleto. Falta linhas minimas.")
            
        # 1-3. Header
        qr_type = lines[0]
        version = lines[1]
        coding = lines[2]
        
        if qr_type != "SPC" or version != "0201" or coding != "1":
            raise SwissQRParserError("Header invalido. Esperado SPC 0201 1")
            
        # 4. Beneficiary Account
        account = lines[3]
        
        # 5-11. Creditor
        creditor_addr_type = lines[4]
        if creditor_addr_type != "S":
            raise SwissQRParserError("SIX v2.3 Error: Somente enderecos estruturados (Type S) sao aceitos para Creditor.")
            
        creditor = {
            "address_type": creditor_addr_type,
            "name": lines[5],
            "street": lines[6],
            "building_number": lines[7],
            "postal_code": lines[8],
            "town": lines[9],
            "country": lines[10]
        }
        
        # 12-18. Ultimate Creditor (Opcional - Avanca indices)
        # 19-20. Payment Amount and Currency
        amount_str = lines[18]
        try:
            amount = Decimal(amount_str) if amount_str else Decimal("0.0")
        except InvalidOperation:
            raise SwissQRParserError(f"Valor do titulo (Amount) invalido: {amount_str}")
            
        currency = lines[19]
        
        # 21-27. Debtor
        debtor_addr_type = lines[20]
        if debtor_addr_type and debtor_addr_type != "S":
            raise SwissQRParserError("SIX v2.3 Error: Somente enderecos estruturados (Type S) sao aceitos para Debtor.")
            
        debtor = {
            "address_type": debtor_addr_type,
            "name": lines[21],
            "street": lines[22],
            "building_number": lines[23],
            "postal_code": lines[24],
            "town": lines[25],
            "country": lines[26]
        }
        
        # 28-29. Reference
        reference_type = lines[27]
        reference = lines[28]
        
        if reference_type not in ("QRR", "SCOR", "NON"):
            raise SwissQRParserError(f"Reference type {reference_type} desconhecido.")
            
        # 30+. Unstructured message / Billing info / Trailer
        unstructured_message = lines[29] if len(lines) > 29 else ""
        trailer = lines[30] if len(lines) > 30 else ""
        billing_info = lines[31] if len(lines) > 31 else ""
        
        if trailer and trailer != "EPD":
            raise SwissQRParserError(f"Trailer invalido. Esperado EPD, recebido {trailer}")
        
        
        # Validacao compulsoria
        self.validate_mod11(account, raise_error=True)
        
        return {
            "account": account,
            "creditor": creditor,
            "amount": amount,
            "currency": currency,
            "debtor": debtor,
            "reference_type": reference_type,
            "reference": reference,
            "unstructured_message": unstructured_message,
            "billing_info": billing_info
        }

    def validate_mod11(self, iban: str, raise_error: bool = False) -> bool:
        """
        Validates the QR-IBAN using the ISO 7064 MOD97-10 standard.
        Algorithm:
        1. Move first 4 characters to the end.
        2. Replace letters A-Z with 10-35.
        3. Check mod 97 == 1.
        """
        if len(iban) < 5:
            if raise_error:
                raise SwissQRParserError("QR-IBAN muito curto para validacao MOD11.")
            return False

        # 1. Puxa os 4 primeiros pro final
        arranged = iban[4:] + iban[:4]

        # 2. Converte letras em numeros
        numeric_str = ""
        for char in arranged:
            if char.isdigit():
                numeric_str += char
            elif char.isalpha():
                numeric_str += str(ord(char.upper()) - ord('A') + 10)
            else:
                if raise_error:
                    raise SwissQRParserError(f"Caractere invalido no QR-IBAN: {char}")
                return False

        # 3. Calcula Modulo 97
        try:
            checksum = int(numeric_str) % 97
        except ValueError:
            if raise_error:
                    raise SwissQRParserError("Erro no processamento numerico do QR-IBAN.")
            return False

        is_valid = (checksum == 1)

        if not is_valid and raise_error:
            raise SwissQRParserError(f"Falha na validacao MOD11 (ISO 7064) do QR-IBAN: {iban}")

        return is_valid
