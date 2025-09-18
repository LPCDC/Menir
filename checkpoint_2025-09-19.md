# 📑 Menir Checkpoint — Itaú + Sara Guarani
**Data:** 2025-09-19  
**Estado:** Público / Neo4j Aura validado / CI ativo  

---

## ⚙️ Projetos Ativos
### Itaú (Proposta Judicial)
- Arquivos:  
  - `itau_documentos.csv`  
  - `itau_transacoes.csv`  
  - `itau_partes.csv`  
- Setup: `setup_itau_relations.cypher`  
- Status: Dataset público e validado no Aura.  
- Auditorias:  
  - Relações de partes e documentos  
  - Transações de maior valor  

### Sara Guarani (Locação)
- Arquivos:  
  - `sara_guarani.csv`  
- Setup: `setup_sara_guarani.cypher`  
- Status: Dataset criado, pronto para commit/push.  
- Auditorias:  
  - Contratos por parte  
  - Contratos de maior valor  

---

## 🚀 Funcionalidades Menir ativas
- Energy-Aware Routing (Cypher/GDS com fallback)  
- Explainable Layers (subgrafos de justificativa)  
- Blockchain Auditing (hashing SHA-256 via APOC)  
- CI GitHub Actions (aplicando schema/constraints)  

---

## 🔐 Privacidade
- Nenhum dado sensível publicado.  
- Apenas datasets de **teste estruturado** estão no GitHub Pages.  
- Safe para colaboração externa.  

---

## 🔜 Próximos Passos
1. Commit/push do pacote **Sara Guarani** (`sara_guarani.csv` + `setup_sara_guarani.cypher`).  
2. Gerar auditorias mais sofisticadas (inadimplência / padrões de transação).  
3. Ingestão Render (Família Otani) como próximo case real.  
