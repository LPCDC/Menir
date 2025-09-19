# Checkpoint — Menir_Meta
Data: 2025-09-18T04:54:00.442392

## Evento Registrado
- Primeira execução bem-sucedida do gatilho 'Marco → Civil da internet'
- Impacto: validação do ciclo de estado em múltiplas janelas

# Checkpoint — Menir (MarcoPolo + Gato Mia)
📅 Data: 2025-09-20  
🔑 Versão: v1.0 dos gatilhos unificados

---

## Triggers Ativos
- **Marco** → resposta: **Polo**  
- **Polo** → resposta: **Polo**  
- **Marco Polo** (junto) → resposta: **Polo**  
- **Gato** → resposta: **Miau**  
- **Mia** → resposta: **Miau**  
- **Gato Mia** (junto) → resposta: **Miau**

Todos os triggers acionam o **painel-resumo unificado** (MarcoPolo/GatoMia).

---

## Arquivos Ativos
- `MENIR_PLAN.md` → plano geral (visual, auditoria, queries resumidas, alias incluído).  
- `projects/MarcoPolo/marcopolo_dashboard_seed.cypher` → seed original (MarcoPolo).  
- `projects/MarcoPolo/gatomia_dashboard_seed.cypher` → seed alias (GatoMia).  

---

## Camada Visual
- **NeoDash** no Neo4j Aura (principal).  
- **Bloom** opcional.  
- Dashboards salvos no banco como “MarcoPolo/GatoMia”.

---

## Diretrizes Técnicas
- Consultas: usar `OPTIONAL MATCH` + `COLLECT[..]` + `LIMIT` → respostas sempre seguras, nunca vazias.  
- CSVs: devem estar públicos (GitHub Pages / S3).  
- Auditoria: opcional com `apoc.util.sha256`.

---

## Estado da Instalação
- Repo atualizado com `MENIR_PLAN.md`.  
- Seeds `marcopolo_dashboard_seed.cypher` e `gatomia_dashboard_seed.cypher` criados.  
- Pronto para migrar de chat: basta abrir nova janela e dizer **“Marco”** ou **“Gato Mia”** → resposta **Polo/Miau** + resumo completo.

---

## Últimos Commits (sync GitHub → MENIR)
- [2025-09-20] gatomia: rename MarcoPolo → Gatomi + add dashboard
- [2025-09-20] reflexive: seed mínimo (constraints básicos)
- [2025-09-19] proj:Itau fix setup_itau_relations

✅ Este checkpoint garante que o Menir retome exatamente deste ponto em qualquer nova janela.
