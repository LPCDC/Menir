# MENIR — Plano Geral (MarcoPolo + Visual + Resumos)
**Objetivo:** boot padrão por “Marco” com resposta “Polo” (painel-resumo), camada visual leve, e consultas com resumos/limites por padrão.

## Camada Visual
- **NeoDash** conectado ao **Neo4j Aura** (recomendado).
- **Bloom** opcional (ver compatibilidade com Aura/versões; usar via deep links se necessário).

## Diretrizes de Consultas
- Usar `OPTIONAL MATCH` + `COLLECT[..limite..]` + `LIMIT` nos painéis.
- Evitar agregações gigantes sem filtros (lembrar: `LIMIT` não reduz custo de agregação pesada).

## Carga de Dados
- CSVs públicos (GitHub Pages/S3/etc.) para `LOAD CSV` no Aura.

## Auditoria
- Hash com `apoc.util.sha256([mensagem])` para assinar execuções críticas.

## Processo Operacional
- Sempre que pedir commit/push, o assistente fornece **Summary exato**.
- Gatilho de boot: **“Marco”** → resposta **“Polo”** (projetos, reflexões, pendências, ajustes).
- Minimizar sua ação: passos claros, prontos pra colar.
