---
name: talks-corporativos
description: Workflow para palestras de Ana Caroline sobre Burnout e NR-1. Automatiza pesquisa, briefing no NotebookLM, geração de slides e persistência de aprendizados no grafo SANTOS. Use quando Ana Caroline confirmar uma palestra ou fornecer materiais pós-evento.
---

# Talks Corporativos (Ana Caroline)

## When to use this skill
- Quando Ana Caroline confirmar uma nova palestra com um cliente.
- Quando for necessário preparar briefings, áudios e slides sobre Burnout/NR-1.
- Quando houver gravações ou transcrições de palestras para processar e extrair aprendizados.

## Workflow

### 1. Preparação (Pré-Palestra)
- [ ] **Pesquisa de Cliente**: Investigar setor, tamanho, notícias e cultura organizacional do cliente.
- [ ] **NotebookLM Setup**:
    - [ ] Criar notebook: `mcp notebooklm create-notebook --name "Talks-Corporativos-AnaCaroline"`
    - [ ] Gerar Briefing Executivo (2 páginas).
    - [ ] Gerar Audio Overview (deep_dive format) para deslocamento.
    - [ ] Gerar Tabela de FAQ (Perguntas prováveis + Respostas setoriais).
- [ ] **Slide Deck**: Gerar deck de abertura com dados de burnout específicos do mercado do cliente.

### 2. Captura de Inteligência (Pós-Palestra)
- [ ] **Ingestão de Transcrição**: Processar áudio/texto da palestra.
- [ ] **Extração de Insights**: Identificar decisões, perguntas reais da audiência e pontos de resistência.
- [ ] **Persistência SANTOS**: Criar nós de `Learning` vinculados ao `Client` e `Sector` no grafo SANTOS.

### 3. Distribuição de Conteúdo
- [ ] Gerar Resumo LinkedIn da Ana.
- [ ] Gerar Thread para X.
- [ ] Gerar E-mail de Follow-up para o cliente.

## Instructions

### NotebookLM MCP
Para inicializar o contexto de pesquisa:
```powershell
mcp notebooklm create-notebook --name "Talks-Corporativos-AnaCaroline"
```

### Regras de Grafo (SANTOS)
- **Tenant Context**: Sempre usar `tenant: "SANTOS"`.
- **Isolamento**: Nunca criar arestas diretas para o tenant `BECO`.
- **Nós de Aprendizado**: `(:Learning)` vinculados a `(:Client)` e `(:Sector)` via `[:LEARNED_FROM]`.

## Resources
- **Base Teórica**: Burnout, NR-1, Saúde Mental Corporativa.
- **Grafo de Destino**: [SANTOS](file:///c:/Users/Pichau/Repos/MenirVital/Menir/src/v3/core/persistence.py)
