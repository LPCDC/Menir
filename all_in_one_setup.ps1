param(
    # Caminho local do Menir
    [string]$RepoPath="C:\Users\Pichau\Repos\MenirVital",

    # Branch remoto alvo
    [string]$BranchName="release/menir-aio-v5.0-boot",

    # Repositório remoto GitHub <owner>/<repo>
    [string]$GitHubUserRepo="LPCDC/Menir",

    # Token PAT GitHub com escrita
    # PAT exposto deve ser rotacionado depois. Boas práticas: tokens e segredos expostos precisam ser invalidados e substituídos, porque quem tiver o token pode empurrar commits remotos e acessar recursos. :contentReference[oaicite:1]{index=1}
    [string]$GitHubPAT="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",

    # Nome da tarefa agendada no Windows
    [string]$ScheduleName="Menir_AutoPush",

    # Frequência de push automático em minutos
    [int]$IntervalMinutes=30
)

# Monta URL remota autenticada com PAT
$RemoteUrl="https://$GitHubPAT@github.com/$GitHubUserRepo.git"

# 0. Instalar GitPython (push_agent.py usa isso)
# GitPython permite scriptar git add / commit / push direto em Python via Repo.index.commit() e origin.push(). :contentReference[oaicite:2]{index=2}
Start-Process -FilePath "python.exe" -ArgumentList "-m","pip","install","gitpython" -NoNewWindow -Wait

# 1. Garantir .gitignore
# .env e .env.local não podem ir pro Git porque contêm chaves, tokens e senhas reutilizáveis. A recomendação é colocar .env no .gitignore mesmo em repositório privado. :contentReference[oaicite:3]{index=3}
$gitignorePath = Join-Path $RepoPath ".gitignore"
if (Test-Path $gitignorePath) {
    $gitignoreContent = Get-Content $gitignorePath -Raw
} else {
    $gitignoreContent = ""
    New-Item -ItemType File -Path $gitignorePath | Out-Null
}
$linesToEnsure = @(
    ".env",
    ".env.local",
    "*.env",
    "status/zk_log_digest.json"
)
foreach ($l in $linesToEnsure) {
    if ($gitignoreContent -notmatch [regex]::Escape($l)) {
        Add-Content -Path $gitignorePath -Value $l
    }
}

# 2. Criar .env.local com variáveis sensíveis
$envLocalPath = Join-Path $RepoPath ".env.local"
$envLocal = @"
REPO_PATH=$RepoPath
BRANCH_NAME=$BranchName
REMOTE_URL=$RemoteUrl
COMMIT_PREFIX=[auto-menir]
"@
Set-Content -Path $envLocalPath -Value $envLocal -Encoding UTF8

# 3. Criar pastas status, neo4j, reports se não existirem
$statusDir   = Join-Path $RepoPath "status"
$neo4jDir    = Join-Path $RepoPath "neo4j"
$reportsDir  = Join-Path $RepoPath "reports"
foreach ($d in @($statusDir,$neo4jDir,$reportsDir)) {
    if (!(Test-Path $d)) { New-Item -ItemType Directory -Path $d | Out-Null }
}

# 4. Criar status/status_update.json inicial
# status_update.json vira o "estado oficial" que o Grok vai ler no GitHub. Esse padrão é GitOps: o repositório Git guarda o estado desejado e todo ajuste vai por commit rastreável. :contentReference[oaicite:4]{index=4}
$statusJsonPath = Join-Path $statusDir "status_update.json"
$statusJson = @"
{
  "boot_version": "v5.0",
  "timestamp_brt": "2025-10-27T21:20:00-03:00",
  "schema_change": {
    "neo4j_labels_added": ["EventoBanco", "Transacao"],
    "neo4j_rels_added": ["REFERE_A", "ENVOLVENDO"]
  },
  "open_tasks": [
    "gerar Cypher incremental para novas Transacao Itaú",
    "gerar timeline Itaú limpa para assembleia sem sobrenomes completos"
  ],
  "lgpd_consent": false,
  "security_state": {
    "token_github_rotated": false,
    "push_policy": "manual_approval_required"
  },
  "slowdown_guard": {
    "gpu_temp_c_max": 87,
    "latency_ms_max": 5000,
    "char_count": 90000
  },
  "zk_log_digest": [
    {
      "hash": "SHA256:PLACEHOLDER",
      "action": "timeline_itau_generated",
      "ts_brt": "2025-10-27T20:40:00-03:00"
    }
  ],
  "next_deadline": "2025-10-29T19:30:00-03:00",
  "assembly_context": "Condominio Tivoli retrofit terreo e sindico profissional",
  "itau_context": "Linha do tempo bancaria e efeito patrimonial"
}
"@
Set-Content -Path $statusJsonPath -Value $statusJson -Encoding UTF8

# 5. Criar push_agent.py
# push_agent.py faz add/commit/push sozinho usando GitPython.
# Depois o Windows Task Scheduler roda esse script em intervalo fixo via New-ScheduledTaskAction apontando python.exe com -Argument pro caminho do script. Agendar Python desse jeito é prática direta documentada para Task Scheduler. :contentReference[oaicite:5]{index=5}
$pushAgentPath = Join-Path $RepoPath "push_agent.py"
$pushAgentPy = @"
import os
import time
import datetime
from git import Repo, GitCommandError

def load_env(path=".env.local"):
    env = {}
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env

def push_with_retry(repo, branch, remote_url, max_attempts=5, base_delay=2):
    try:
        origin = repo.remote("origin")
        origin.set_url(remote_url)
    except ValueError:
        origin = repo.create_remote("origin", remote_url)
    except GitCommandError:
        origin = repo.remote("origin")
        origin.set_url(remote_url)

    try:
        repo.git.checkout(branch)
    except GitCommandError as e:
        raise SystemExit(f"Falha no checkout do branch {branch}: {e}")

    for attempt in range(max_attempts):
        try:
            origin.push(refspec=f"{branch}:{branch}")
            print("Push OK")
            return True
        except GitCommandError as e:
            wait_seconds = base_delay * (2 ** attempt)
            print(f"Tentativa {attempt + 1} falhou: {e}. Aguardando {wait_seconds} s")
            time.sleep(wait_seconds)

    raise SystemExit("Push falhou depois de varias tentativas")

def main():
    env = load_env()
    repo_path = env["REPO_PATH"]
    branch = env["BRANCH_NAME"]
    remote_url = env["REMOTE_URL"]
    prefix = env.get("COMMIT_PREFIX", "[auto]")

    repo = Repo(repo_path)
    repo.git.add(all=True)

    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    if repo.is_dirty(index=True, working_tree=True, untracked_files=True):
        msg = f"{prefix} snapshot {timestamp}"
        repo.index.commit(msg)
        print(f"Commit criado: {msg}")
    else:
        print("Nenhuma mudanca para commit")

    push_with_retry(repo, branch, remote_url)

if __name__ == "__main__":
    main()
"@
Set-Content -Path $pushAgentPath -Value $pushAgentPy -Encoding UTF8

# 6. Criar README_SECURITY.md
# Atenção: aqui estava o erro. Agora fechamos com '"@' na coluna 1.
$readmePath = Join-Path $RepoPath "README_SECURITY.md"
$readmeContent = @"
# MENIR SECURITY BASELINE

Status: v5.0 BootNow
Responsavel: Luiz (admin unico)

1. Segredos
- .env.local guarda tokens e nao entra no Git.
- Se token vazar ele deve ser trocado (rotacionado) e o antigo revogado.
  (Boa prática: segredos expostos devem ser rotacionados imediatamente. :contentReference[oaicite:6]{index=6})

2. Commits e push automaticos
- push_agent.py e o unico caminho oficial de commit/push automatico.
- Cada commit usa prefixo [auto-menir] e timestamp ISO.

3. Auditoria
- status/status_update.json publica estado resumido e tarefas abertas.
- zk_log.py guarda log completo local com hash e horario.
- Apenas o resumo zk_log_digest (hash e horario) vai para o Git.

4. LGPD
- Campo lgpd_consent em status/status_update.json controla se nomes completos e dados pessoais aparecem nos relatorios que vao para o repo e para o Grok.
- Se lgpd_consent=false, usar iniciais e remover identificadores diretos.
- A LGPD exige necessidade e minimização: tratar só o mínimo dado pessoal necessário para a finalidade declarada. :contentReference[oaicite:7]{index=7}

5. Branch protegido
- Branch release/menir-aio-v5.0-boot deve ter revisao e checagens antes de merge.
"@
Set-Content -Path $readmePath -Value $readmeContent -Encoding UTF8

# 7. Criar tarefa agendada para rodar push_agent.py periodicamente
# Task Scheduler roda python.exe com -Argument pro script, gatilho recorrente a cada N minutos. :contentReference[oaicite:8]{index=8}
$action = New-ScheduledTaskAction -Execute "python.exe" -Argument "`"$pushAgentPath`""

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes) `
    -RepetitionDuration ([TimeSpan]::MaxValue)

Register-ScheduledTask -TaskName $ScheduleName `
    -Action $action `
    -Trigger $trigger `
    -Description "Auto push Menir" `
    -Force

Write-Output "Setup concluido. Rode python push_agent.py manualmente uma vez e confirme no GitHub."
