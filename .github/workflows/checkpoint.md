# Checkpoint — Menir_Meta
Data: 2025-09-18T06:37:45.893873

## Evento Registrado
- Organização das tasks encavaladas com IDs indexados
- Nova task: Booklet da Família Otani (Projeto Render → Tânia)

## Tasks Encavaladas (indexadas e sem limite)

🔥 Críticas
- T001 Confirmar publicação GitHub Pages → `https://lpcdc.github.io/Menir/` precisa estar acessível (nodes.csv, rels.csv, log).
- T002 Testar `LOAD CSV` no Neo4j com esses arquivos públicos (validar ingestão no grafo).

🟢 Em curso
- T003 Registrar eventos no `menir_meta_log.jsonl` a cada marco (uma linha por evento).
- T004 Consolidar checkpoints (nodes.csv/rels.csv) para ingestão contínua.
- T005 Implementar workflow `pages-csv.yml` no repo público e manter sincronizado.
- T006 Estruturar segregação de repos (main.need público / projetos privados).
- T007 Fazer booklet da Família Otani (redação elaborada para o projeto Render).

🟡 Pausadas / atenção
- T008 Ativar APOC (import/load/periodic) com configurações seguras (`neo4j.conf`).
- T009 Definir padrão de commits (`meta: …`, `graph: …`, `proj:<nome>: …`).
- T010 Montar README QuickStart definitivo com instruções de uso (para repo público).
- T011 Registrar intenção de produto: “Menir totalmente na nuvem” (tokens + Pages + APOC + Graphiti).
- T012 Plano detalhado de reorganização de arquivos/repos (público vs privado).
