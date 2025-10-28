# 💡 Sugestões de Consolidação & Boas Práticas – Menir / Itaú

## Objetivo
Garantir que os scripts de ingestão e relacionamento (Neo4j) funcionem de forma robusta, auditável, com validações e rollback, para evitar problemas futuros.

---

## 📋 Checklist de Recursos / Itens a Integrar

| Área | Prática recomendada | Arquivo / Local sugerido |
|---|---|---|
| Validação inicial do CSV | Verificar campos obrigatórios (id, doc_id, parte_id, valor, data, tipo) antes de MERGE. Linhas inválidas devem ser descartadas ou logadas. | No script de ingestão (`setup_itau*.cypher`) |
| Criação de nós obrigatórios primeiro | Inserir `Documento` e `Parte` *antes* de processar `Transacao`, para garantir que os relacionamentos terão destino. | Scripts de ingestão dos arquivos CSV desses tipos |
| Relacionamentos faltantes (patch) | Script que identifica transações sem relacionamento (`NOT (t)-[:REFERE_A]...`, `NOT (t)-[:ENVOLVENDO]...`) e cria relacionamentos se os nós existem. | Patch em `projects/Itau/setup_itau_relations_patch.cypher` |
| Validações pós-import | Execução automática de consultas como: contagem de nós, lista de transações relacionadas, verificar IDs correspondentes.Documento/Parte. | `validate_itau_relations.cypher` ou parte do mesmo script |
| Logs ou relatórios de qualidade | Gerar relatório JSON/CSV com número de nós criados, número de relacionamentos criados, proporção de transações sem relacionamento, identificadores faltantes. | `reports/itau_ingest_report.json` |
| Definições de esquema / constraints | Garantir índices e constraints (`UNIQUENESS`) para `Documento.id`, `Parte.id`, `Transacao.id`, etc. | Em `schema.cypher` ou `constraints.cypher` |
| Versionamento de scripts | Manter scripts “versões defeituosas” com marcações ou renomeações como `obsoletos/v1`, `versao_final`, etc., evitar sobrescrita sem revisão. | Diretório `projects/Itau/` ou similar |
| Backup / Rollback | Ter backup dos dados ou snapshots antes de grandes migrações ou mudanças de script. Também scripts de rollback limitado caso seja detectado erro grave. | Documento ou pasta `backups/itau/` ou “rollback” scripts |
| Integração contínua (CI/CD) | Se possível, incluir smoke tests ou pipelines de teste que rodem scripts em instância de teste antes de aplicar em produção. | GitHub Actions / workflow de CI |

---

## ⚙️ Modelo de Arquivos Sugeridos

- `projects/Itau/setup_itau_relations_patch.cypher` — patch para relacionamentos faltantes  
- `projects/Itau/validate_itau_relations.cypher` — conjunto de queries de validação após ingestão  
- `reports/itau_ingest_report.json` — relatório de qualidade pós-execução  
- `schema/constraints_itau.cypher` — constraints/índices para campos chave  
- `backups/itau/rollback_itau_relations.cypher` — script para desfazer (ou limpar relacionamentos) se for necessário

---

## 🔐 Exemplo de Relatório JSON de Qualidade

```json
{
  "timestamp": "2025-09-19TXX:XX:XX-03:00",
  "n_transacoes_totais": 4,
  "n_documentos": 5,
  "n_partes": 2,
  "n_relacionamentos_refere_a": 4,
  "n_relacionamentos_envolvendo": 4,
  "transacoes_sem_documento": [],
  "transacoes_sem_parte": [],
  "erros_detectados": []
}
