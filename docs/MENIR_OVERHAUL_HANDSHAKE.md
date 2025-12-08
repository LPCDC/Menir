# MENIR OVERHAUL — HANDSHAKE CANÔNICO

**Status:** ATIVO  
**Última atualização:** 2025-12-08  
**Branch-alvo:** menir-overhaul  
**Modo:** EXECUÇÃO DIRETA (sem fase educacional)  

---

## 🔗 Origem

Este overhaul nasce da consolidação das análises:
- Auditoria estrutural completa do repositório
- Relatório Gemini Deep Research
- Análise de multi-projeto, ingestão, CI/CD, QA e governança

---

## 📊 Estado Atual

**Fase atual:** IMPLEMENTAÇÃO IMEDIATA

**Entradas travadas para implementação:**

1. **Limpeza de repositório**
   - Remove: Menir2, zips, resíduos de testes antigos
   - Consolida: estrutura de diretórios em padrão único

2. **Refactor de ingestão → pipeline em estágios (JSONL)**
   - Substitui JSON embutido por JSONL streaming
   - Implementa stages: parse → validate → ingest → audit
   - Suporta cancel/rollback por etapa

3. **Introdução obrigatória de MENIR_PROJECT_ID**
   - Todas operações exigem projeto rastreado
   - ENV var ou comando-line arg obrigatório
   - Rastreia origem + permissões

4. **Particionamento lógico multi-projeto por label**
   - Cada projeto: Project label + índice
   - Queries isolam por `WHERE (n:Project {id: $pid})`
   - Facilita multi-tenancy futuro

5. **Reparação do CI/CD (pr_checks.yml)**
   - Fix: lint, test, schema validation
   - Bloqueia merge sem health check ✅
   - Auto-tag releases no merge main

6. **Criação de QA semântico por Cypher + pytest**
   - Testes estruturais de schema
   - Validação de relacionamentos críticos
   - Cobertura mínima 80% de paths

7. **Preparação para Vector Search (fase futura)**
   - Armazena embeddings em ChunkEmbedding nodes
   - Cypher: `MATCH (c:Chunk)-[:HAS_EMBEDDING]->(e:ChunkEmbedding)`
   - Documentação de API pronta

---

## 🎯 Regra de Ouro

Qualquer **BOOT NOW** futuro que detecte este arquivo deve:

1. **Assumir que o usuário NÃO quer explicações longas.**
2. **Continuar diretamente no ponto de implementação.**
3. **Operar como "MENIR OVERHAUL MODE".**

---

## 📋 Checklist de Implementação

- [ ] Limpeza de repositório
- [ ] Refactor ingestão (JSONL stages)
- [ ] MENIR_PROJECT_ID obrigatório
- [ ] Multi-projeto particionado
- [ ] CI/CD reparado
- [ ] QA semântico implementado
- [ ] Vector Search pronto

---

## 🔐 Assinatura

```
Luiz + Menir
2025-12-08
```

Versão: 1.0-overhaul-bootstrap
