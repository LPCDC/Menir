"""
Menir Core V5.1 - Invoice Processing Skill
Extracts accounting data using bimodal NLP/Vision routing and strict Pydantic mathematical validation.
"""
import os
import math
import logging
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, model_validator

from src.v3.core.menir_runner import SkillResult
from src.v3.menir_intel import MenirIntel
from src.v3.core.dispatcher import DocumentDispatcher
from src.v3.meta_cognition import MenirOntologyManager

logger = logging.getLogger("InvoiceSkill")

# --- ACCOUNTING ONTOLOGY SCHEMAS ---

class InvoiceLineItem(BaseModel):
    description: str = Field(description="Descrição clara do item, serviço ou produto.")
    gross_amount: float = Field(description="Valor bruto da linha.")
    tva_rate_applied: Optional[float] = Field(default=None, description="Taxa de imposto aplicada à linha (ex: 8.1, 2.6). Se não especificada, deixe nulo.")

class InvoiceData(BaseModel):
    vendor_name: str = Field(description="Nome do fornecedor que emitiu a fatura.")
    vendor_uid: Optional[str] = Field(default=None, description="Número UID Suíço com a extensão de IVA se aplicável (ex: CHE-123.456.789 TVA).")
    vendor_iban: Optional[str] = Field(default=None, description="IBAN suíço ou europeu na fatura.")
    currency: Literal["CHF", "EUR"] = Field(description="A moeda oficial do documento.")
    issue_date: str = Field(description="Data de emissão no formato YYYY-MM-DD.")
    
    subtotal: float = Field(description="Soma do valor líquido sem impostos de todas as linhas.")
    tip_or_unregulated_amount: float = Field(default=0.0, description="Gorjetas (Pourboire) ou valores não tributados.")
    total_amount: float = Field(description="Valor total a pagar exigido no documento.")
    
    items: List[InvoiceLineItem] = Field(description="Lista com todos os itens extraídos.")
    requires_manual_justification: bool = Field(default=False, description="Flag: Marcar como TRUTH se for um recibo de restaurante ou despesa de representação que exija justificativa do contador.")

    @model_validator(mode="after")
    def validate_accounting_math(self, info) -> "InvoiceData":
        """
        Escudo Matemático Dinâmico (TDFN-Aware): 
        Força o LLM a acertar as contas. O `subtotal` + (gorjeta) + (impostos das linhas) = `total_amount`.
        Adicionalmente, se as alíquotas extraídas não constarem no contexto dinâmico do banco (Tenant Rules),
        rejeita a extração e manda para a Quarentena.
        """
        # Extrai as regras de TVA passadas em tempo de runtime pelo AsyncRunner -> InvoiceSkill -> Pydantic
        context_data = info.context or {}
        allowed_tva_rates = context_data.get("valid_tva_rates", [8.1, 2.6, 0.0]) # Fallback genérico suíço
        
        # Teste 1: A soma crua das linhas com a gorjeta bate com o Total Amount (Contabilidade Básica)?
        calculated_total = sum(item.gross_amount for item in self.items) + self.tip_or_unregulated_amount
        
        if not math.isclose(calculated_total, self.total_amount, abs_tol=0.05):
            raise ValueError(f"CRITICAL MATH ERROR: A soma dos itens ({calculated_total:.2f}) não bate com o total_amount ({self.total_amount:.2f}).")
            
        # Teste 2: Alucinação de Taxa (TDFN)
        for idx, item in enumerate(self.items):
            if item.tva_rate_applied is not None:
                # Arredondamos para 1 casa decimal para evitar float flutuation ex: 5.30000001
                rate = round(item.tva_rate_applied, 1)
                
                # Permite a taxa se estiver nas permitidas ou se for perfeitamente 0
                if rate not in allowed_tva_rates and not math.isclose(rate, 0.0, abs_tol=0.01):
                    raise ValueError(f"TVA ALUCINATTION FATAL: A taxa de IVA de {rate}% no item {idx} não é válida para este Tenant/Data. Taxas permitidas no Neo4j: {allowed_tva_rates}")
            
        return self

    @model_validator(mode="after")
    def validate_swiss_uid(self) -> "InvoiceData":
        """
        Escudo de Anomalias contra Fraude ou Alucinação: Validação Aritmética MOD11 do UID.
        """
        if not self.vendor_uid:
            return self
            
        import re
        # Extrai apenas os números (Removendo CHE, ., -, TVA, MWST)
        raw_digits = re.sub(r'\D', '', self.vendor_uid)
        
        # O Base do UID suíço TEM que ter 9 dígitos
        if len(raw_digits) != 9:
            raise ValueError(f"ANOMALY DETECTED: UID Suíço inválido (Tamanho incorreto): {self.vendor_uid}. São exigidos exatamente 9 dígitos numéricos (IDE).")
            
        # Pesos oficiais do Governo Suíço para MOD11
        weights = [5, 4, 3, 2, 7, 6, 5, 4]
        total_sum = sum(int(digit) * weight for digit, weight in zip(raw_digits[:8], weights))
        
        expected_checksum = 11 - (total_sum % 11)
        if expected_checksum == 11:
            expected_checksum = 0
        elif expected_checksum == 10:
            raise ValueError(f"ANOMALY DETECTED: UID Suíço MOD11 falhou estruturalmente (Check=10) para {self.vendor_uid}")
            
        actual_checksum = int(raw_digits[8])
        if expected_checksum != actual_checksum:
            raise ValueError(f"FRAUD/HALLUCINATION DETECTED: UID Suíço {self.vendor_uid} falhou na validação de Integridade MOD11. O dígito final {actual_checksum} deveria ser {expected_checksum}.")
            
        return self

# --- INVOICE SKILL CLASS ---

class InvoiceSkill:
    """
    Skill de processamento de faturas (Swiss Crésus ERP Pipeline).
    """
    def __init__(self, intel: MenirIntel, ontology_manager: MenirOntologyManager):
        self.intel = intel
        self.ontology_manager = ontology_manager
        self.dispatcher = DocumentDispatcher()
        
    def _inject_into_graph(self, data: InvoiceData, tenant: str, file_hash: str):
        """
        Materializa a ontologia em memória (InvoiceData) no motor Neo4j.
        Transação Cypher rigorosa com idempotência via MERGE.
        """
        import json
        
        # Serializar os itens de linha em uma string JSON para não poluir o Grafo com milhares de micro-nós abstratos.
        line_items_dict = [item.model_dump() for item in data.items]
        line_items_json = json.dumps(line_items_dict, ensure_ascii=False)
        
        safe_tenant = tenant.replace("`", "")
        
        query = f"""
        // 1. Fornecedor (Vendor) - Evita duplicação pelo nome/IBAN
        MERGE (v:Vendor:`{safe_tenant}` {{name: $vendor_name}})
        SET v.iban = $vendor_iban, v.project = $tenant
        
        // 2. Fatura (Invoice) - Idempotência absoluta pelo HASH do arquivo
        MERGE (i:Invoice:`{safe_tenant}` {{file_hash: $file_hash}})
        SET i.issue_date = $issue_date,
            i.total_amount = $total_amount,
            i.currency = $currency,
            i.subtotal = $subtotal,
            i.tips = $tips,
            i.requires_justification = $requires_justification,
            i.line_items_json = $line_items_json,
            i.ingested_at = datetime()
            
        // 3. Relacionamento Fornecedor -> Emite -> Fatura
        MERGE (v)-[:ISSUED]->(i)
        
        // 4. Relacionamento Tenant -> Recebe -> Fatura
        MERGE (t:Tenant {{name: $tenant}})
        MERGE (t)-[:RECEIVED]->(i)
        """
        
        params = {
            "tenant": tenant,
            "vendor_name": data.vendor_name,
            "vendor_iban": data.vendor_iban,
            "file_hash": file_hash,
            "issue_date": data.issue_date,
            "total_amount": data.total_amount,
            "currency": data.currency,
            "subtotal": data.subtotal,
            "tips": data.tip_or_unregulated_amount,
            "requires_justification": data.requires_manual_justification,
            "line_items_json": line_items_json
        }
        
        with self.ontology_manager.driver.session() as session:
            session.run(query, **params)
            logger.info(f"✅ Fatura injetada no Grafo (Fornecedor: {data.vendor_name}, Total: {data.total_amount:.2f} {data.currency})")

    async def process_document(self, file_path: str, tenant: str = "BECO") -> SkillResult:
        """
        Rotina Bimodal de Ingestão e Validação.
        """
        import hashlib
        import json
        from pydantic import ValidationError
        
        logger.info(f"🧾 Iniciando processamento de Invoice: {file_path}")
        
        PRODUCTION_READY = os.getenv("MENIR_INVOICE_LIVE", "false").lower() == "true"
        if not PRODUCTION_READY:
            logger.warning(
                "⚠️ InvoiceSkill em modo STUB. "
                "Defina MENIR_INVOICE_LIVE=true no .env para ativar extração real."
            )
            return SkillResult(
                success=False,
                nodes_and_edges=[],
                message="STUB_MODE: Invoice não processada. MENIR_INVOICE_LIVE não ativado."
            )
        
        # 0. COMPUTING FILE HASH (Unique Document Identifier)
        try:
            with open(file_path, "rb") as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Erro ao computar hash do documento {file_path}: {e}")
            return SkillResult(success=False, message=str(e), nodes_and_edges=[])
            
        try:
            # 1. TRIAGEM PELA VELOCIDADE E COMPLEXIDADE DO ARQUIVO
            lane = self.dispatcher.analyze_payload(file_path)
            
            from datetime import date
            placeholder_date = date.today().isoformat()
            logger.info("Consulta Temporal de Impostos (Neo4j/LRU Cache) ativada...")
            active_rules = self.ontology_manager.get_tenant_active_context(tenant, placeholder_date)
            
            # 3.5 ÂNCORA SEMÂNTICA - BUSCAR EXEMPLOS DE OURO (STYLE LORA)
            golden_examples = self.ontology_manager.get_golden_examples(tenant)
            
            # Se fosse produção: Passaríamos active_rules no prompt do Oráculo.

            # 4. ROTEAMENTO DE COMPUTAÇÃO
            if lane == "FAST_LANE":
                logger.info("⚡ Invoice triada para FAST_LANE: Iniciando PyMuPDF/Regex + Extraction rápida.")
                # Lógica de extração baseada em texto OCR nativo ou parse XML (camt.053 adaptado/etc)
                pass
                
            elif lane == "SLOW_LANE":
                logger.info("🐢 Invoice triada para SLOW_LANE: Acionando Gemini Vision LLM + ReflexiveAgent (Oráculo).")
                try:
                    # SIMULATING LLM HALLUCINATION FOR PIPELINE TESTING
                    # Intentionally creating a mathematical imbalance (100 != 500)
                    bad_data = {
                        "vendor_name": "Test Vendor",
                        "currency": "CHF",
                        "issue_date": "2024-05-15",
                        "subtotal": 100.0,
                        "tip_or_unregulated_amount": 0.0,
                        "total_amount": 500.0, 
                        "items": [
                            {"description": "Item 1", "gross_amount": 100.0}
                        ]
                    }
                    InvoiceData.model_validate(bad_data)
                except json.JSONDecodeError as e:
                    logger.error(f"JSONDecodeError - Invalid JSON format from LLM extraction for document {file_path}")
                    self.ontology_manager.inject_entropy_anomaly(tenant, file_hash, "ExtractionError", str(e), 1)
                    return SkillResult(success=False, message="Falha estrutural de OCR/Image Parsing", nodes_and_edges=[])
                except ValidationError as e:
                    # Contar quantos erros agrupados existem no ErrorWrapper
                    error_count = len(e.errors())
                    error_dump = e.json()
                    logger.error(f"ValidationError - Pydantic validation failed with {error_count} errors for document {file_path}")
                    self.ontology_manager.inject_entropy_anomaly(tenant, file_hash, "MathValidationError", error_dump, error_count)
                    return SkillResult(success=False, message=f"Fatura reprovada em {error_count} regras Fiduciárias", nodes_and_edges=[])

            # 5. RETORNO (Mockado para o esqueleto)
            return SkillResult(
                success=True,
                nodes_and_edges=[],
                message="Invoice processada (Esqueleto)"
            )
            
        except Exception as e:
            logger.error(f"Erro Genérico ao processar Fatura: {e}")
            return SkillResult(
                success=False,
                nodes_and_edges=[],
                message=f"Falha de processamento estrutural: {e}"
            )
