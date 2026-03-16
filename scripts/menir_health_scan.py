import os
import sys
import subprocess
import datetime
from pathlib import Path

# Tentativa de importar dependências do projeto para checar BD
try:
    from src.v3.meta_cognition import MenirOntologyManager
    HAS_NEO4J = True
except ImportError:
    HAS_NEO4J = False

RED_ZONE_FILES = {
    "src/v3/skills/invoice_skill.py",
    "src/v3/core/cresus_exporter.py",
    "src/v3/core/reconciliation.py",
    "src/v3/extensions/astro/genesis.py",
    "src/v3/core/schemas/identity.py",
    "src/v3/menir_bridge.py",
    "src/v3/core/synapse.py",
    "src/v3/skills/document_classifier_skill.py",
}

def check_mypy():
    print("Executando Mypy (aguarde)...")
    try:
        # Run mypy on src/v3
        result = subprocess.run(
            ["python", "-m", "mypy", "src/v3"], 
            capture_output=True, text=True
        )
        # Parse error count from output
        out = result.stdout + result.stderr
        errors = 0
        for line in out.splitlines():
            if "Found" in line and "errors in" in line:
                return line.strip()
        return "Sem erros detectados" if result.returncode == 0 else "Falha ao ler mypy"
    except Exception as e:
        return f"Mypy scan falhou: {e}"

def check_dead_sdks():
    dead_sdks = ["google-generativeai", "vertexai", "text-embedding-004"]
    found = []
    # Usar grep ou subprocess para buscar no src/
    try:
        for sdk in dead_sdks:
            res = subprocess.run(["git", "grep", sdk, "src/"], capture_output=True, text=True)
            if res.stdout.strip():
                found.append(sdk)
    except Exception:
        pass
    
    return found if found else ["Nenhum SDK obsoleto detectado ativamente no git."]

def check_modified_risks():
    try:
        res = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        changed = []
        for line in res.stdout.splitlines():
            if len(line) > 3:
                filepath = line[3:].strip().replace("\\", "/")
                if filepath in RED_ZONE_FILES:
                    changed.append(filepath)
        return changed if changed else ["Nenhum arquivo de risco modificado."]
    except Exception:
        return ["Erro ao checar git status."]

def check_neo4j_health():
    if not HAS_NEO4J:
        return "MenirOntologyManager indisponível (dependência Neo4j não carregada no script)."
    
    import concurrent.futures

    def _connect():
        manager = MenirOntologyManager()
        result = manager.check_system_health()
        manager.close()
        return result

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_connect)
            try:
                is_healthy = future.result(timeout=5)
                return "ONLINE (Nós vitais ativos)" if is_healthy else "DEGRADADO (Falhas detectadas)"
            except concurrent.futures.TimeoutError:
                print("⚠️  [HealthScan] Neo4j não respondeu em 5s — hook continua sem bloquear.")
                return "TIMEOUT (Neo4j indisponível — commit não bloqueado)"
    except Exception as e:
        return f"OFFLINE ou Erro de conexão: {e}"

def get_current_fingerprint():
    state_file = "MENIR_STATE.md"
    if not os.path.exists(state_file):
        return "FINGERPRINT_MISSING"
    with open(state_file, "r", encoding="utf-8") as f:
        for line in f:
            stripped_line = line.strip()
            if stripped_line.startswith("MENIR-P"):
                return stripped_line
    return "FINGERPRINT_NOT_FOUND"

def generate_session_brief(status_only=False):
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    fingerprint = get_current_fingerprint()
    mypy_status = check_mypy()
    dead_sdks = check_dead_sdks()
    risks = check_modified_risks()
    neo4j_status = check_neo4j_health()
    
    status_summary = (
        f"Fingerprint : {fingerprint}\n"
        f"Mypy Count  : {mypy_status}\n"
        f"SDKs Mortas : {', '.join(dead_sdks)}\n"
        f"Zona Velh.  : {', '.join(risks) if risks else 'Limpo'}\n"
        f"Neo4j Graph : {neo4j_status}\n"
    )
    
    if status_only:
        print("=== MENIR VITAL STATUS ===")
        print(status_summary)
        return

    brief_content = f"""# MENIR SESSION BRIEF
> Gerado em: {now}

## 1. ESTADO ATUAL (SNAPSHOT)
```text
{status_summary}
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
"""

    with open("SESSION_BRIEF.md", "w", encoding="utf-8") as f:
        f.write(brief_content)
        
    print(f"✅ SESSION_BRIEF.md gerado com sucesso.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--status-only", action="store_true", help="Printa apenas 5 linhas de status.")
    parser.add_argument("--generate-brief", action="store_true", help="Gera o SESSION_BRIEF.md arquivo.")
    
    args = parser.parse_args()
    
    if args.status_only:
        generate_session_brief(status_only=True)
    else:
        generate_session_brief(status_only=False)
