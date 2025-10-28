# Push Runbook - release/menir-aio-v5.0-boot-local

Objetivo
Publicar o estado canônico do Menir (estado do grafo, LGPD, contratos de saída e auditoria) no GitHub.

Pré-requisitos
- .env.local preenchido com:
  - GITHUB_PAT (token com escrita no repo LPCDC/Menir)
  - NEO4J_* (URI, user, pass, database)
  - FERNET_KEY
  - credenciais Open Banking
  - IPFS privado e blockchain (CONTRACT_ADDR, WALLET, PRIVATE_KEY)
  - variáveis SlowdownGuard
- Ambiente Python "menir" ativo (E:\Conda\envs\menir).

Passos
1. PowerShell
$env:GITHUB_PAT = "<PAT>"
$env:GITHUB_REPO_URL = "https://github.com/LPCDC/Menir.git"
$env:GITHUB_BRANCH = "release/menir-aio-v5.0-boot-local"
$env:NEO4J_URI = "bolt://localhost:7687"
$env:NEO4J_DATABASE = "neo4j"
$env:LGPD_POLICY_MODE = "mask_third_parties"
$env:SLOWDOWNGUARD_CHAR_THRESHOLD = "80000"
$env:SLOWDOWNGUARD_LATENCY_MS = "2500"
$env:GPU_ALERT_THRESHOLD_C = "86"

2. Executar
& "E:\Conda\envs\menir\python.exe" "C:\Users\Pichau\Repos\MenirVital\master_script.py"

3. Saída esperada
{'status': 'OK', 'commit': '<hash>'}

4. Conferir no GitHub se menir_state.json, lgpd_policy.md, output_contracts.md, push_runbook.md e logs/zk_audit.jsonl foram atualizados.

Última atualização runbook: 2025-10-28T13:18:22Z UTC.
