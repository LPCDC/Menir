// ============================================================
// BLOCO 1: FRONTEIRA DO TENANT
// ============================================================

MERGE (t:Tenant {name: "SANTOS"})
SET t.description = "Instância operacional — Projeto A Beleza do Equilíbrio",
    t.created_at  = datetime(),
    t.version     = "1.0.0";


// ============================================================
// BLOCO 2: ENTIDADE PRINCIPAL (operacional — sem PII)
// ============================================================

MERGE (ana:Person:Estrategista:SANTOS {id: "ana_caroline_001"})
SET ana.name         = "Ana Caroline Albuquerque",
    ana.role         = "Estrategista Comportamental",
    ana.city         = "Santos/SP",
    ana.trust_score  = 1.0
WITH ana
MATCH (t:Tenant {name: "SANTOS"})
MERGE (ana)-[:BELONGS_TO_TENANT]->(t);


// ============================================================
// BLOCO 3: PROJETO CENTRAL
// ============================================================

MERGE (proj:Project:SANTOS {id: "projeto_beleza_equilibrio"})
SET proj.name        = "A Beleza do Equilíbrio",
    proj.category    = "Desenvolvimento Comportamental e Liderança",
    proj.status      = "ACTIVE",
    proj.created_at  = datetime()
WITH proj
MATCH (t:Tenant {name: "SANTOS"})
MATCH (ana:Person {id: "ana_caroline_001"})
MERGE (proj)-[:BELONGS_TO_TENANT]->(t)
MERGE (ana)-[:OWNS_PROJECT]->(proj);


// ============================================================
// BLOCO 4: HIERARQUIA DE PRODUTOS
// ============================================================

// Diagnóstico / Captação (top of funnel)
MERGE (p0:Product:SANTOS {id: "produto_diagnostico"})
SET p0.name         = "Questionário de Auditoria de Polaridade",
    p0.tier         = "lead_gen",
    p0.description  = "Diagnóstico de nível de exaustão e desconexão do feminino",
    p0.format       = "online_questionario"
WITH p0
MATCH (t:Tenant {name: "SANTOS"})
MATCH (proj:Project {id: "projeto_beleza_equilibrio"})
MERGE (p0)-[:BELONGS_TO_TENANT]->(t)
MERGE (proj)-[:HAS_PRODUCT]->(p0);

// Low-ticket
MERGE (p1:Product:SANTOS {id: "produto_calibracao_express"})
SET p1.name         = "Sessão de Calibração Express",
    p1.tier         = "low_ticket",
    p1.description  = "Primeira intervenção prática — reequilíbrio de polaridade",
    p1.format       = "sessao_individual"
WITH p1
MATCH (t:Tenant {name: "SANTOS"})
MATCH (proj:Project {id: "projeto_beleza_equilibrio"})
MATCH (p0:Product {id: "produto_diagnostico"})
MERGE (p1)-[:BELONGS_TO_TENANT]->(t)
MERGE (proj)-[:HAS_PRODUCT]->(p1)
MERGE (p0)-[:LEADS_TO]->(p1);

// Mid/High-ticket
MERGE (p2:Product:SANTOS {id: "produto_mentoria_beleza"})
SET p2.name         = "Mentoria A Beleza do Equilíbrio",
    p2.tier         = "high_ticket",
    p2.description  = "Integração profunda das polaridades — liderança e feminino",
    p2.format       = "mentoria_individual_continuada"
WITH p2
MATCH (t:Tenant {name: "SANTOS"})
MATCH (proj:Project {id: "projeto_beleza_equilibrio"})
MATCH (p1:Product {id: "produto_calibracao_express"})
MERGE (p2)-[:BELONGS_TO_TENANT]->(t)
MERGE (proj)-[:HAS_PRODUCT]->(p2)
MERGE (p1)-[:LEADS_TO]->(p2);

// Workshops práticos
MERGE (p3:Product:SANTOS {id: "produto_laboratorio_sensorial"})
SET p3.name         = "Laboratórios Sensoriais",
    p3.tier         = "workshop",
    p3.description  = "Intervenção física — passagem do conceito para o corpo",
    p3.modalities   = ["Ikebana", "Dança", "Pintura", "Artes Manuais"],
    p3.format       = "grupo_presencial"
WITH p3
MATCH (t:Tenant {name: "SANTOS"})
MATCH (proj:Project {id: "projeto_beleza_equilibrio"})
MERGE (p3)-[:BELONGS_TO_TENANT]->(t)
MERGE (proj)-[:HAS_PRODUCT]->(p3);


// ============================================================
// BLOCO 5: PÚBLICOS-ALVO
// ============================================================

MERGE (b2c:TargetAudience:SANTOS {id: "audience_b2c_mulheres"})
SET b2c.type        = "B2C",
    b2c.profile     = "Mulheres sobrecarregadas pelo mito da guerreira",
    b2c.channel     = "Salões de beleza / Instagram / indicação",
    b2c.pain_point  = "Exaustão, controle excessivo, perda de vitalidade"
WITH b2c
MATCH (t:Tenant {name: "SANTOS"})
MATCH (proj:Project {id: "projeto_beleza_equilibrio"})
MERGE (b2c)-[:BELONGS_TO_TENANT]->(t)
MERGE (proj)-[:TARGETS]->(b2c);

MERGE (b2b:TargetAudience:SANTOS {id: "audience_b2b_empreendedoras"})
SET b2b.type        = "B2B",
    b2b.profile     = "Empreendedoras e líderes corporativas",
    b2b.region      = "Baixada Santista",
    b2b.channel     = "Hubs de negócios / eventos / NR-1 compliance",
    b2b.pain_point  = "Burnout, passivo trabalhista, esgotamento de equipes"
WITH b2b
MATCH (t:Tenant {name: "SANTOS"})
MATCH (proj:Project {id: "projeto_beleza_equilibrio"})
MERGE (b2b)-[:BELONGS_TO_TENANT]->(t)
MERGE (proj)-[:TARGETS]->(b2b);


// ============================================================
// BLOCO 6: COMPLIANCE B2B (argumento regulatório)
// ============================================================

MERGE (cr:ComplianceRule:SANTOS {id: "compliance_nr1_burnout"})
SET cr.name         = "NR-1 e Lei 14.457/22",
    cr.jurisdiction = "Brasil",
    cr.risk         = "Passivo trabalhista por burnout e riscos psicossociais",
    cr.applicability = "B2B — empresas com quadro de funcionários"
WITH cr
MATCH (t:Tenant {name: "SANTOS"})
MATCH (b2b:TargetAudience {id: "audience_b2b_empreendedoras"})
MERGE (cr)-[:BELONGS_TO_TENANT]->(t)
MERGE (b2b)-[:MITIGATES_RISK_VIA]->(cr);


// ============================================================
// BLOCO 7: FRAMEWORK CONCEITUAL
// ============================================================

MERGE (c1:Concept:SANTOS {id: "conceito_polaridade"})
SET c1.name         = "Polaridade da Energia",
    c1.description  = "Tensão criativa entre Animus (ação) e Feminino Receptivo (Terra)"
WITH c1
MATCH (t:Tenant {name: "SANTOS"})
MATCH (proj:Project {id: "projeto_beleza_equilibrio"})
MERGE (c1)-[:BELONGS_TO_TENANT]->(t)
MERGE (proj)-[:UTILIZES_CONCEPT]->(c1);

MERGE (c2:Concept:SANTOS {id: "conceito_animus_hipertrofiado"})
SET c2.name         = "Animus Hipertrofiado",
    c2.description  = "Excesso de racionalidade e ação — masculino tóxico internalizado",
    c2.symptom      = "Neurose do controle, exaustão, anestesia emocional"
WITH c2
MATCH (t:Tenant {name: "SANTOS"})
MATCH (c1:Concept {id: "conceito_polaridade"})
MERGE (c2)-[:BELONGS_TO_TENANT]->(t)
MERGE (c1)-[:HAS_POLARITY]->(c2);

MERGE (c3:Concept:SANTOS {id: "conceito_feminino_receptivo"})
SET c3.name         = "Feminino Receptivo / Terra",
    c3.description  = "Espaço criativo interior — intuição, nutrição, presença",
    c3.metaphor     = "O útero como espaço vazio e fértil"
WITH c3
MATCH (t:Tenant {name: "SANTOS"})
MATCH (c1:Concept {id: "conceito_polaridade"})
MERGE (c3)-[:BELONGS_TO_TENANT]->(t)
MERGE (c1)-[:HAS_POLARITY]->(c3);


// ============================================================
// BLOCO 8: CANAL DISTRIBUIÇÃO — HUB THAIS
// ============================================================

MERGE (hub:Channel:SANTOS {id: "canal_hub_thais"})
SET hub.name        = "Hub Empreendedoras Thais",
    hub.type        = "B2B_parceria",
    hub.region      = "Baixada Santista",
    hub.format      = "Encontros / palestras / rodas de conversa"
WITH hub
MATCH (t:Tenant {name: "SANTOS"})
MATCH (b2b:TargetAudience {id: "audience_b2b_empreendedoras"})
MERGE (hub)-[:BELONGS_TO_TENANT]->(t)
MERGE (hub)-[:SERVES]->(b2b);


// ============================================================
// BLOCO 9: CONSTRAINTS DE INTEGRIDADE
// ============================================================

CREATE CONSTRAINT santos_lead_id IF NOT EXISTS
FOR (l:Lead) REQUIRE l.id IS UNIQUE;

CREATE CONSTRAINT santos_event_id IF NOT EXISTS
FOR (e:Event) REQUIRE e.id IS UNIQUE;

CREATE CONSTRAINT santos_product_id IF NOT EXISTS
FOR (p:Product) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT santos_person_id IF NOT EXISTS
FOR (p:Person) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT santos_tenant_name IF NOT EXISTS
FOR (t:Tenant) REQUIRE t.name IS UNIQUE;
