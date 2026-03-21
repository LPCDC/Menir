# MENIR SESSION BRIEF
> Gerado em: 2026-03-21 04:16:41 UTC

## 1. ESTADO ATUAL (SNAPSHOT)
```text
Fingerprint : MENIR-P47-20260321-HARDENING-SEMGREP-ISOLATION
Mypy Count  : Falha ao ler mypy
SDKs Mortas : vertexai, text-embedding-004
Zona Velh.  : src/v3/core/cresus_exporter.py, src/v3/core/synapse.py, src/v3/extensions/astro/genesis.py, src/v3/menir_bridge.py, src/v3/skills/document_classifier_skill.py, src/v3/skills/invoice_skill.py
Neo4j Graph : OFFLINE ou Erro de conexão: 'AsyncSession' object does not support the context manager protocol

```

## 2. FILA DE EXECUÇÃO (CLASSIFICADA)

### 🟢 V1 - PRONTOS PARA AG (Sem Autorização Necessária)
- Instalação dos `menir_aliases.sh` (Concluído)
- Ajustes de tipagem MyPy faltantes pelo sistema
- Finalização da migração do log de sessões no Neo4j (Sprint 1C)
- Criação de novos tests end-to-end locais

### 🟡 V2 - AGUARDANDO ARQUITETO (Claude)
- Batch 3: Deprecação oficial da SDK GenAI e migração `tenant_id` -> ContextVar.
- Proposta de schema PESSOAL para a Camada 2A (menir_capture).

### 🔴 V0 - AGUARDANDO LUIZ (Hard Lock)
- Batch 4: Ativação operacional da `invoice_skill.py`.
- Definição em `.env` das variáveis de invoice live.

## 3. PROPOSTA DE SESSÃO
**Prioridade Máxima (BECO Runway):** Destravar o Batch 3 (V2) para preparar o sistema para lidar rigorosamente com os logs através de ContextVars, seguido imediatamente do destravamento operacional (Batch 4 - V0) autorizando o `invoice_skill`.
