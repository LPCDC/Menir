# Avaliação Técnica: Menir v1.1.0 (Architecture Assessment)

**Data**: 10/12/2025
**Escopo**: Menir v1.1.0 (Unified CLI + MCP Server)
**Destinatário**: Engenharia de Sistemas

---

## 1. Pontos Fortes do Design (Híbrido Local/Cloud)

O design atual (Local Python Core + Cloud Neo4j + Local MCP Server) é **extremamente competente** para o caso de uso "Personal OS".

*   **Soberania de Dados (Local First)**: A verdade absoluta está em arquivos locais (`.jsonl`). O grafo é apenas uma *projeção*. Isso significa que se o Neo4j explodir ou ficar caro, seus dados (o journaling) estão salvos em disco simples, legível e portável.
*   **Latência Zero no Boot**: O boot (`boot_now.py`) não depende de rede. Ele sobe, checa o ambiente e libera o terminal instantaneamente. A parte pesada (sync) é desacoplada ou adiada.
*   **Interface Universal (MCP)**: Adotar o **Model Context Protocol** (JSON-RPC) na v1.1 foi a decisão correta. Isso desacopla o "Backend Menir" do "Cliente AI". Hoje é o GPT-4 via script, amanhã pode ser o Claude Desktop, um plugin do VSCode ou um app mobile, todos falando com a porta 5000.
*   **Baixa Complexidade Operacional**: Não há Kubernetes, Docker containers pesados ou microserviços distribuídos. É Python puro e sistema de arquivos. Debuggar é trivial (`cat logs/operations.jsonl`).

## 2. Riscos e Vulnerabilidades Críticas

Apesar de sólido, o sistema é **frágil** em robustez de dados e segurança.

### A. Integridade e Persistência (Risco: ALTO) 🚨
*   **Ponto Único de Falha**: Se o SSD da máquina `OakStation` falhar, os arquivos `data/system/menir_sessions.jsonl` e `menir_tasks.jsonl` desaparecem. Como o Sync é *one-way* (JSONL -> Neo4j), recuperar os dados brutos do Neo4j seria complexo e incompleto.
*   **Dessincronia**: O grafo só é atualizado no `boot` ou `shutdown`. Se o PC desligar abruptamente (queda de luz), o dia de trabalho não é projetado no grafo. O agente (RAG) ficará "cego" para os eventos recentes até o próximo boot manual.

### B. Segurança (Risco: MÉDIO) ⚠️
*   **Localhost Aberto**: O MCP Server roda em `0.0.0.0:5000` (ou localhost) sem autenticação. Qualquer script malicioso rodando na sua máquina pode consultar `/chat` ou `/jsonrpc` e extrair todo o contexto da sua vida.
*   **Secrets em Plaintext**: O `.env` contém credenciais de escrita do banco de produção. Se vazado (ex: por um `git add .` descuidado sem o `.gitignore` correto), compromete o banco inteiro.

### C. Versionamento
*   **Dependência de Disciplina**: O sistema confia que o operador *nunca* vai editar os JSONL na mão e corromper o formato. Não há checksums ou validação rígida na escrita dos logs.

## 3. Requisitos Mínimos para "Produção Pessoal"

Para considerar o sistema confiável (que você pode confiar sua vida profissional), falta:

1.  **Backup Automatizado (Obrigatório)**:
    *   Script que, a cada Shutdown, copia os `.jsonl` para uma pasta de Drive (OneDrive/GDrive) ou faz um `git push` de um repo privado de dados (separado do código).
2.  **Validação de Schema (Obrigatório)**:
    *   O MCP Server já usa Pydantic, mas o `boot_now.py` e `menir_log.py` escrevem dicionários soltos. Falta tipagem forte na escrita dos logs para evitar "sujeira" nos dados.
3.  **Logs de Erro do Servidor**:
    *   Hoje, se o MCP Server cair, ele morre silenciosamente. Precisa de um wrapper (supervisor ou loop `while true`) para garantir que ele reinicie.

## 4. Recomendações de Melhoria (Roadmap)

### Imediato (Semana 1) - "Colete Salva-Vidas"
*   [ ] **Backup Script**: Adicionar passo no `shutdown_menir.py` para zipar a pasta `data/` e copiar para um local seguro.
*   [ ] **Supervisor**: Alterar `BOOT_NOW.cmd` para não rodar python direto, mas um script que relança o servidor se ele cair.

### Médio Prazo (Mês 1) - "Blindagem"
*   **Token Auth**: Adicionar um `Bearer Token` simples no MCP Server.
*   **Scribe Governance**: Terminar a implementação do Scribe para que *toda* escrita no grafo passe por um fluxo de aprovação (Proposal -> Apply), eliminando escritas diretas perigosas.

## 5. Veredito: Aprovo a Migração?

**SIM, COM RESSALVAS.**

A migração para **Backend (Python) + API (MCP) + Agente** é a evolução natural e correta. O modelo antigo (scripts soltos) não escala para agentes autônomos.

**Porém**, não aposente o cérebro humano ainda.
1.  Use o sistema, mas mantenha o `hotfix/v1.1.0-boot-patches` aplicado.
2.  **Não confie no Sync automático** cega e puramente. Verifique o Health (`menir health`) semanalmente.
3.  **Implemente o Backup de JSONL hoje**. É o único risco que não tem volta.

O Menir v1.1.0 está pronto para ser seu copiloto, mas você ainda é o piloto em comando.

---
*Relatório gerado por AI Senior System Architect.*
