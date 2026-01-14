# MENIR v11 – Risk Model & Defense-in-Depth

Status: **v1.0 – Frozen para experimentos iniciais**

Este documento descreve o modelo de risco do Menir v11, um sistema RAG autocurativo
para manutenção de código legado. A abordagem é explícita: não confiamos em "mais IA"
para resolver riscos da própria IA; usamos Engenharia Determinística + Psicologia
Operacional.

---

## 1. Ameaças Principais

### 1.1 Patch Maligno (Adversarial Input)

- **Descrição**: Inputs maliciosos ou enviesados induzem o LLM a gerar patches que
  introduzem vulnerabilidades (backdoors, bypass de autenticação, injeção de comandos).
- **Superfície de ataque**:
  - Relatos de bug manipulados.
  - Prompts sugerindo "ignore segurança para corrigir rápido".
  - Código legado confuso, fácil de explorar.

### 1.2 Regressão Silenciosa (Testes Fracos)

- **Descrição**: Patches que "passam nos testes" mas alteram comportamento não coberto
  pela suíte – bugs em casos de borda, performance, segurança, lógica de negócio.
- **Superfície de ataque**:
  - Testes unitários fracos ou inexistentes.
  - Ausência de testes de propriedade.
  - Baixa cobertura de código.

### 1.3 Inflamação do Grafo (Crescimento + Performance)

- **Descrição**: O Shadow Graph cresce sem controle (Hunches, Events, Files, etc.),
  degradando latência, consumo de memória e estabilidade do Neo4j.
- **Superfície de ataque**:
  - Alto volume de eventos sem prune.
  - Deleções em massa mal planejadas.
  - Índices pesados em grafos grandes.

### 1.4 Falhas de Infraestrutura (Perda ou Corrupção de Dados)

- **Descrição**: Falhas em Redis, Celery, disco, rede ou Neo4j levam à perda de eventos
  de auditoria, inconsistência entre WAL, fila e grafo.
- **Superfície de ataque**:
  - Redis down.
  - Workers Celery travados.
  - Falhas de disco / storage.
  - Jobs de export/prune falhando silenciosamente.

### 1.5 Complacência Humana (Fator Psicológico)

- **Descrição**: O sistema parece tão "esperto" que revisores humanos passam a clicar
  em "Merge" sem ler. A IA ganha autoridade injustificada.
- **Superfície de ataque**:
  - Fatiga de revisão (muitos PRs).
  - Confiança cega no bot.
  - Pressão por velocidade > segurança.

---

## 2. Matriz Ameaça → Defesa → Owner

| # | Ameaça                 | Defesa Principal                           | Ativo Menir v11                                 | Owner Primário      |
|---|------------------------|--------------------------------------------|-------------------------------------------------|---------------------|
| 1 | Patch Maligno         | SAST determinístico                        | Bandit / Semgrep no sandbox                     | AppSec              |
| 2 | Regressão Silenciosa  | Testes fortes + novos testes de regressão  | Property-based + teste de regressão + cobertura | QA / Dev            |
| 3 | Inflamação do Grafo   | Circuit breaker + deleção oportunista      | 1-in/1-out, modo read-only, spillover JSONL     | Neo4j DBA / SRE     |
| 4 | Falha de Infra        | WAL local + DLQ                            | WAL em disco + DLQ no Redis                     | SRE / Platform      |
| 5 | Complacência Humana   | Fricção intencional no PR                  | Labels de confiança, checklist obrigatório      | Eng. Social / UX    |

---

## 3. Controles Específicos por Ameaça

### 3.1 Patch Maligno

**Objetivo**: impedir que patches gerados por IA introduzam vulnerabilidades conhecidas.

- **Controle 1 – SAST no Sandbox**  
  - Rodar Bandit / Semgrep sobre os arquivos alterados pelo patch.
  - Se `returncode != 0` ou houver finding de severidade alta → abortar cura.

- **Controle 2 – Classificação de Risco**  
  - Patches que mexem em áreas sensíveis (auth, crypto, IO externo) recebem
    `BOT-CONFIDENCE: LOW` por padrão.

- **Saída possível**:
  - `Hunch` é reclassificado como `:SecurityRisk`.
  - Nenhum PR é aberto automaticamente.

### 3.2 Regressão Silenciosa

**Objetivo**: elevar o significado de "PASS" no pipeline.

- **Controle 1 – Testes existentes + regressão dedicada**  
  - Todos os testes antigos devem passar.  
  - Um novo teste de regressão, específico para o bug, deve ser adicionado e passar.

- **Controle 2 – Property-based (quando aplicável)**  
  - Funções puras, regras de negócio ou transformações podem usar Hypothesis.
  - Falha em property-based invalida a cura.

- **Controle 3 – Cobertura**  
  - Cobertura não pode cair na área afetada.
  - Opcional: exigir aumento mínimo em módulos com bugs recorrentes.

### 3.3 Inflamação do Grafo

**Objetivo**: manter latência e tamanho do grafo sob controle.

- **Controle 1 – Circuit Breaker de Escrita**  
  - Se latência P95 de escrita > limiar (ex: 500 ms), Actuator entra em modo read-only:
    - Não cria novos Hunches no grafo.
    - Eventos de auditoria vão para spillover JSONL.

- **Controle 2 – Deleção Oportunista (1-in/1-out)**  
  - Para cada novo `:ActiveHunch`, o sistema tenta arquivar ou deletar um `:ArchivedHunch`
    elegível (ex: > 1 ano).

- **Controle 3 – Jobs de Prune Batch**  
  - Jobs periódicos deletam nós antigos em lotes pequenos (ex: 1000 por transação).

### 3.4 Falha de Infraestrutura

**Objetivo**: evitar perda de eventos e inconsistência.

- **Controle 1 – Write-Ahead Log (WAL)**  
  - Todo evento é append em `/var/log/menir/wal.log` antes de ir para Redis/Neo4j.
  - Em boot, um reconciliador compara WAL vs grafo e reenvia o que falta.

- **Controle 2 – Dead Letter Queue (DLQ)**  
  - Tarefas que falham 3x vão para `menir_dlq` em vez de serem descartadas.
  - Há procedimento manual de inspeção e replay.

- **Controle 3 – Backups e Restore**  
  - Backups regulares do Neo4j + testes reais de restore.
  - ApoC export para dados muito antigos antes do prune definitivo.

### 3.5 Complacência Humana

**Objetivo**: manter humanos em modo "piloto atento".

- **Controle 1 – Confiança Visível**  
  - PRs do Menir têm rótulo `[BOT-CONFIDENCE: LOW/MEDIUM/HIGH]`.
  - Mensagem clara no título/descrição: "Requer revisão atenta" quando LOW/MEDIUM.

- **Controle 2 – Explicação Obrigatória**  
  - Corpo do PR deve incluir:
    - `Why I did this`
    - `Potential Risks`
  - Se o LLM não conseguir listar riscos plausíveis, PR não é aberto.

- **Controle 3 – Checklist de Bloqueio**  
  - Regra no repositório: merge só é permitido se:
    - Revisor marcar explicitamente:
      - `[x] Li o código gerado e assumo responsabilidade pela mudança`.

---

## 4. Estados do Sistema & Transições

### 4.1 Estados

- `NORMAL`  
  - Grafo saudável, latências dentro do SLO, filas sob controle.

- `DEGRADED`  
  - Latência acima do desejado, mas dentro do tolerável; circuit breaker ainda fechado.

- `READ_ONLY`  
  - Circuit breaker de escrita aberto:
    - Sem novos Hunches no grafo.
    - Eventos indo para WAL + spillover JSONL.

- `PANIC`  
  - Falha grave (corrupção de grafo, falha de backup, bug severo no Actuator).
    - Desativar curas automáticas.
    - Apenas sugestões em PR, nenhum patch automático.

### 4.2 Gatilhos de Transição (exemplos)

- `NORMAL → DEGRADED`  
  - P95 de escrita entre 200–500 ms por janela de 5 min.

- `DEGRADED → READ_ONLY`  
  - P95 de escrita > 500 ms por mais de N minutos.

- `ANY → PANIC`  
  - Detecção de corrupção de dados, falha de restore, ou incidente de segurança.

---

## 5. Responsabilidades

- **AppSec**: manter regras SAST, revisar findings críticos, atualizar políticas de segurança.
- **QA**: manter qualidade de testes, revisar testes gerados pelo Menir, monitorar regressões.
- **Neo4j DBA**: tuning de índices, memória, prune, monitoramento de performance do grafo.
- **SRE**: observabilidade, circuit breaker, WAL, DLQ, backups, incident response.
- **UX / Eng. Social**: desenhar fricção saudável em PR, mensagens e alerts.

---

## 6. Limitações Conhecidas

- Nenhum controle elimina totalmente risco de patch malicioso ou regressão sutil.
- Eficácia depende da disciplina operacional (manter SAST, testes, prune, backups).
- Humanos continuam essenciais para revisar PRs críticos e interpretar riscos.
