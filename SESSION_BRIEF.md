# MENIR SESSION BRIEF
> Gerado em: 2026-03-18 16:37:57 UTC

## 1. ESTADO ATUAL (SNAPSHOT)
```text
Fingerprint : MENIR-P46-20260317-MENIR_CAPTURE_REFINED
Mypy Count  : Falha ao ler mypy
SDKs Mortas : vertexai, text-embedding-004
Zona Velh.  : Nenhum arquivo de risco modificado.
Neo4j Graph : ONLINE (Nós vitais ativos)

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
