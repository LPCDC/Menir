# MENIR ARCHITECT BRIEF

**FINGERPRINT ATUAL:** MENIR-P46-20260317-MENIR_CAPTURE_REFINED

## ONDE ESTAMOS
O detector bimodal interativo separando nativamente PDFs digitais das digitalizações ruidosas foi construído e ligado ao coração da inteligência. O "Abismo 0" (Classificação e Roteamento) está agora parcialmente resolvido com a integração da REST API V3 e o Dashboard de Quarentena Premium. Todos os escudos protetivos de chaves duras foram limpos da malha neural, consolidando um núcleo de teste auditado. O sistema agora opera em escala real BECO: 500 clientes, 6 idiomas detectados.

## BLOQUEADORES ATIVOS
- **A Adoção do Scanner Físico**: Fixture PDF real da Nicole ainda não processada.
- **A Entrega Contábil**: `cresus_exporter.py` não revisado contra o formato .cre real utilizado pela fiduciária atual.

## AG AGUARDA RESPOSTA
- Nenhuma pendência arquitetural ativa e sem resposta.

## DISTÂNCIA DO PRODUTO REAL
1. **Loop de falha humano**: resolvido. Dashboard de quarentena com aceite e correção em um clique está operacional. Nicole tem interface.
2. **Entrega ao Crésus**: MVP funcional. Exporter idempotente com endpoint REST ativo. Bloqueador restante é validação contra formato .cre real com dados da Nicole.
3. **Onboarding**: ainda exige engenheiro. Não resolvido.
4. **Ingestão móvel**: Telegram com voz ativo para SANTOS. BECO pendente por durabilidade.
5. **Memory decay**: parcialmente resolvido. rank_relevance com decaimento exponencial implementado no SANTOS via query-time math.

## SANTOS INTELLIGENCE LAYER
- **Signal cross-tenant**: Signal cross-tenant com threshold e decay implementados.
- **DecisionHub**: Agregando sinais de fontes heterogêneas para priorização.
- **Question Engine**: Ativo — uma pergunta por input baseada em gaps do grafo.
- **Próxima Fronteira**: Conectar DecisionHub ao SESSION_BRIEF.

## MEMÓRIA PERMANENTE
**Visão em dois anos.** 
Nicole deixa de ser processadora de PDFs e vira consultora de negócios. O Menir é fantasma na operação — documentos entram por email ou scanner, o grafo lê, o TrustScore avalia, o Crésus recebe o XML limpo. Nicole só entra para julgar anomalias na quarentena. Para Luiz, o Menir é o Chief of Staff que cura a amnésia de contexto: entrega informação antes de ser pedida e conecta conversas de meses atrás com decisões de hoje. Para o terceiro usuário — um diretor de clínica, um profissional independente, qualquer pessoa com complexidade cognitiva alta — o sistema moldou-se ao cérebro dele, não o contrário.

**O único resultado inegociável.** 
Se o runway acabar amanhã, o único resultado que valida tudo é o Relatório de Horas Fantasmas rodando na BECO com dados reais — provar que uma camada de inteligência com grafos elimina o trabalho de entrada de dados de uma fiduciária suíça, não cria interface mais bonita para esse trabalho. Isso é o que o mercado ainda não viu.

**O princípio oculto.** 
A interface é o inimigo. O Menir precisa ser invisível sempre que possível. Entrada onde a pessoa já vive — áudio, email, scanner. Output onde o processo já termina — Crésus, briefing no celular. UI existe apenas para exceções e quarentena. O dia que o Menir tentar prender o usuário dentro de um software clássico, ele vira mais um SaaS genérico e perde a alma.

## MEMÓRIA TÁTICA & PRECEDENTES (V5.2)
1. **Precedente Zona Vermelha**: Qualquer skill que persista dados diretamente no grafo BECO (ex: `document_classifier_skill.py`, `synapse.py`) deve ser incluída no Hard Lock do git-hook.
2. **Cofre Active Fetcher**: `menir_active_fetcher` opera sob nota de conformidade FINMA; qualquer alteração em seu motor de extração exige auditoria de rastro.
3. **Anti-SOP Graph**: Gemini está instruído a nunca injetar SOPs (Standard Operating Procedures) como nós de dados puros; eles devem ser interpretados como metatags de aresta para manter a pureza ontológica.

**A regra de física.** 
Isolamento galvânico via ContextVar não se burla nunca — nem para teste rápido. Misturou tenant, o sistema morre. Não é convenção de código. É a integridade do produto.
