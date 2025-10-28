# MENIR — Plano Geral (MarcoPolo + GatoMia + Visual + Resumos)

**Objetivo:**  
Garantir boot padrão por **“Marco”** (resposta “Polo”) ou **“Gato Mia”** (resposta “Miau”), entregando painel-resumo com projetos, reflexões, pendências e ajustes.  
Unir camada visual leve (NeoDash) com consultas sempre resumidas/seguras, e manter auditoria mínima.

---

## Camada Visual
- **NeoDash** conectado ao **Neo4j Aura** (recomendado).  
- **Bloom** opcional (via Desktop/App, conforme compatibilidade).  
- Dashboards salvos no banco → painel **MarcoPolo/GatoMia**.

---

## Diretrizes de Consultas
- Usar `OPTIONAL MATCH` + `COLLECT[..limite..]` + `LIMIT` nos painéis.  
- Evitar agregações gigantes sem filtros (lembrar: `LIMIT` não reduz custo de agregação pesada).  
- Sempre fornecer fallback (“sem projetos ativos”, etc.) para que **o Polo/Miau nunca falhe**.

---

## Carga de Dados
- CSVs devem estar públicos (GitHub Pages/S3/etc.) para `LOAD CSV` no Aura.  
- Garantir privilégio `LOAD` ativo na instância.

---

## Auditoria
- Hash com `apoc.util.sha256([mensagem])` para assinar execuções críticas.  
- Registrar logs de reflexões e ajustes de parâmetros no grafo (`Reflexao` → `Parametro`).

---

## Alias de Ativação
- **“Marco”** → resposta: **“Polo”** (painel-resumo).  
- **“Gato Mia”** → resposta: **“Miau”** (mesma função, versão lúdica/brasileira).  
- Ambos acionam o mesmo seed/dashboard.

---

## Processo Operacional
- Sempre que houver commit/push, o assistente fornecerá **Summary exato** para colar no GitHub Desktop.  
- Minimizar esforço do usuário: passos claros, comandos prontos, sem retrabalho.  
- Checkpoints periódicos (`checkpoint.md`) para consolidar estado.  

---
