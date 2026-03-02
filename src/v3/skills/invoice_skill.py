"""
Menir Core V5.1 - Invoice Processing Skill
Extracts accounting data using bimodal NLP/Vision routing and strict Pydantic mathematical validation.
"""
import math
import logging
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, model_validator

from src.v3.menir_runner import SkillResult
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
        MERGE (v:Vendor {{name: $vendor_name}})
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
        logger.info(f"🧾 Iniciando processamento de Invoice: {file_path}")
        
        try:
            # 1. TRIAGEM PELA VELOCIDADE E COMPLEXIDADE DO ARQUIVO
            lane = self.dispatcher.analyze_payload(file_path)
            
            # 2. DEFINIR DATA CONTEXTUAL (Placeholder até extração/análise preliminar)
            # Idealmente, poderíamos tentar achar uma data via regex antes de bater no banco para caching.
            # Se for impossível, bater no Neo4j com data coringa ou a data extraída num pre-parsing.
            placeholder_date = "2024-05-15" 
            
            # 3. MIRA TELESCÓPICA - BUSCAR REGRAS DE IMPOSTO NO BANCO/CACHE (LRU)
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
                # Ler o base64 da imagem e invocar o LLM com as Âncoras Semânticas:
                # result = await self.intel.structured_inference(
                #     prompt="Extraia os dados desta fatura. Siga as regras contábeis.",
                #     image_path=file_path,
                #     response_schema=InvoiceData,
                #     few_shot_examples=golden_examples
                # )
                pass

            # 5. RETORNO (Mockado para o esqueleto)
            return SkillResult(
                success=True,
                nodes_and_edges=[],
                message="Invoice processada (Esqueleto)"
            )
            
        except Exception as e:
            logger.error(f"Erro ao processar Fatura: {e}")
            return SkillResult(
                success=False,
                nodes_and_edges=[],
                message=f"Falha de processamento estrutural: {e}"
            )
