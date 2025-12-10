# Menir v1.1 Production Hardening Specification

**Autor**: Lead Systems Engineer
**Data**: 10/12/2025
**Objetivo**: Elevar Menir de "Laboratório" para "Produção Pessoal" (Robustez e Segurança).

---

## 1. Design de Backup Automatizado (`shutdown_menir.py`)

A estratégia é **Snapshot Local Rotativo**. Não dependeremos de APIs de nuvem (AWS S3/GDrive) no código para manter a soberania local, mas criaremos arquivos fáceis de serem syncados passivamente.

*   **Gatilho**: Executado automaticamente ao final do script `shutdown_menir.py`, **antes** de matar os processos.
*   **Origem**: Pasta `data/system/` (onde vivem `menir_sessions.jsonl`, `menir_tasks.jsonl`).
*   **Destino**: Pasta `backups/` na raiz do projeto (deve ser criada se não existir).
*   **Formato**: Arquivo ZIP nomeado `menir_backup_YYYYMMDD_HHMMSS.zip`.
*   **Retenção**: Manter apenas os últimos 30 backups locais para economizar espaço.

**Snippet de Implementação (`scripts/backup_routine.py`):**
```python
import shutil
import os
import glob
from datetime import datetime

def perform_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_dir = "data/system"
    target_dir = "backups"
    archive_name = os.path.join(target_dir, f"menir_backup_{timestamp}")
    
    os.makedirs(target_dir, exist_ok=True)
    
    # 1. Criar Zip
    shutil.make_archive(archive_name, 'zip', source_dir)
    print(f"✅ Backup created: {archive_name}.zip")
    
    # 2. Rotação (Manter 30)
    archives = sorted(glob.glob(os.path.join(target_dir, "*.zip")))
    while len(archives) > 30:
        oldest = archives.pop(0)
        os.remove(oldest)
        print(f"🧹 Rotated old backup: {oldest}")
```

---

## 2. Segurança: Bearer Token Auth (`mcp_app.py`)

O MCP Server deixará de ser público. Implementaremos um middleware de autenticação via Header padrão HTTP.

*   **Configuração**:
    *   No arquivo `.env`: `MENIR_MCP_TOKEN=sk-menir-secreto-12345`
    *   Se a variável não existir, o servidor **aborta o startup** (fail-safe).
*   **Mecanismo**: `FastAPI Dependency`.
*   **Validação**: Comparação segura (constant-time) do header `Authorization: Bearer <token>`.

**Snippet de Implementação:**
```python
from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    expected_token = os.getenv("MENIR_MCP_TOKEN")
    if not expected_token:
        raise HTTPException(status_code=500, detail="Server misconfigured: No Auth Token")
        
    if not secrets.compare_digest(credentials.credentials, expected_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials

# Uso:
@app.post("/jsonrpc", dependencies=[Security(verify_token)])
async def jsonrpc_handler(...):
```

---

## 3. Integridade de Dados: Schema Log Canônico

Para garantir que o histórico seja reprocessável, definimos um Schema Rígido. Nada entra no `.jsonl` se não passar por esse validador.

*   **Tecnologia**: `Pydantic` (já no stack).
*   **Localização**: `menir_core/schemas/log_schema.py`.

**Especificação do Schema:**
```python
from pydantic import BaseModel, ConfigDict, Field
from typing import Dict, Any, Optional
from datetime import datetime

class LogAction(str, Enum):
    BOOT = "boot_now"
    SHUTDOWN = "shutdown"
    TASK_CREATE = "task_create"
    PROJECT_FOCUS = "project_focus"
    # ...

class MenirLogEntry(BaseModel):
    model_config = ConfigDict(extra='forbid') # Rejeita campos "lixo"
    
    ts: str = Field(..., description="ISO8601 UTC Timestamp")
    session_id: str
    action: LogAction
    payload: Dict[str, Any]
    hash: Optional[str] = None # Hash SHA256 do payload anterior + atual (Blockchain-lite)
    
    # Validador de TS
    @field_validator('ts')
    @classmethod
    def validate_ts_iso(cls, v: str) -> str:
        try:
             datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
             raise ValueError("Timestamp must be ISO8601")
        return v
```

---

## 4. Roadmap de Execução (3 Fases)

Aqui está o plano para sair do modo "Laboratório" e ir para "Produção".

### FASE 1: Segurança Imediata (Hoje) 🛡️
**Foco**: Impedir perda de dados e fechar a porta aberta.
1.  [ ] Adicionar `MENIR_MCP_TOKEN` no `.env`.
2.  [ ] Implementar Middleware de Auth no `mcp_app.py`.
3.  [ ] Criar função de Backup Zip no `shutdown_menir.py`.
4.  [ ] Validar fluxo: Boot -> Uso -> Shutdown -> Backup criado.

### FASE 2: Integridade Estrutural (Semana 1) 🏗️
**Foco**: Garantir que os dados sejam à prova de bala.
1.  [ ] Criar módulo `menir_core.schemas`.
2.  [ ] Refatorar `menir10_log.py` para usar modelos Pydantic na escrita.
3.  [ ] Migrar logs antigos (script `migrate_logs.py`) para o formato canônico se necessário.

### FASE 3: Governança (Mês 1) 📜
**Foco**: Controle sobre mudanças no grafo.
1.  [ ] Finalizar `The Scribe` (Engine de Propostas).
2.  [ ] Impedir escrita direta no Neo4j (exceto pelo Scribe).
3.  [ ] Dashboard simples de "Review de Logs" (Streamlit ou HTML gerado).

---
*Plano pronto para execução imediata (Fase 1).*
