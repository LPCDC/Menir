# pause_session.ps1
# Fecha a sessão atual:
# 1. roda BootNow
# 2. commita snapshot técnico no main
# 3. captura fatos operacionais (ex: Tivoli / Bia / Carol)
# 4. gera Cypher pro Neo4j
# 5. commita e faz push
# 6. imprime BOOT RESUME pra você colar na próxima janela

function Escape-Cypher([string]$s) {
    if ($null -eq $s) { return "" }
    return $s.Replace("'", "\'")
}

Write-Host "=== 1. Boot técnico ==="

# timestamp UTC ISO8601
$ts = (Get-Date).ToUniversalTime().ToString("s") + "Z"

# roda boot_now.py e captura JSON de status
$bootOut = python scripts/boot_now.py
Write-Host "boot_now.py output:"
Write-Host $bootOut

# guarda último json bruto em arquivo para auditoria humana
"{$bootOut}" | Out-File -FilePath "last_boot_now.json" -Encoding UTF8

Write-Host "=== 2. Git snapshot técnico ==="

# garante main atualizado
git checkout main | Out-Null
git pull origin main | Out-Null

# stage de artefatos de estado
git add logs/operations.jsonl artifacts/itau/checkpoint.md scripts/boot_now.py 2>$null

# commit (pode ser vazio se nada mudou além do log já comitado)
$commitMsg = "chore(boot): snapshot $ts"
git commit -m "$commitMsg" --allow-empty | Out-Null

# push direto pro main
git push origin main | Out-Null

Write-Host "Snapshot técnico commitado e enviado."

Write-Host "=== 3. Captura de fato operacional humano ==="
Write-Host "Informe o estado do mundo (Tivoli, Bia, prazo etc)."
Write-Host "Se não quiser preencher agora só aperta Enter em tudo. Isso ainda gera o arquivo Cypher."

$proj          = Read-Host "Projeto (ex: tivoli)"
$resumo        = Read-Host "Resumo do que aconteceu (ex: Bia travada ontem, precisa medir muro etc)"
$bloqueios     = Read-Host "Bloqueios principais (ex: falta medir altura muro garagem/lateral/fundo)"
$prazoSketch   = Read-Host "Prazo sketch (YYYY-MM-DD) ex: 2025-10-30"
$prazoCAD      = Read-Host "Prazo CAD indicativo (YYYY-MM-DD) ex: 2025-11-03"
$participantes = Read-Host "Participantes chave separados por vírgula (ex: Bia, Carol, Luiz Paulo)"

# saneia strings pra usar em Cypher com aspas simples
$proj_s          = Escape-Cypher $proj
$resumo_s        = Escape-Cypher $resumo
$bloqueios_s     = Escape-Cypher $bloqueios
$prazoSketch_s   = $prazoSketch
$prazoCAD_s      = $prazoCAD
$participantes_s = Escape-Cypher $participantes

# gera Cypher para Neo4j
$cypherContent = @"
// Sessão operacional $ts

MERGE (p:Projeto {id: '$proj_s'})
SET
  p.nome = '$proj_s',
  p.status = 'em_andamento',
  p.atualizado = datetime('$ts');

MERGE (e:Evento {
  id:'$proj_s-$ts',
  ts:'$ts'
})
SET
  e.resumo        = '$resumo_s',
  e.bloqueios     = '$bloqueios_s',
  e.prazo_sketch  = '$prazoSketch_s',
  e.prazo_cad     = '$prazoCAD_s',
  e.participantes = '$participantes_s',
  e.atualizado    = datetime('$ts');

MERGE (e)-[:REFERE_A]->(p);

// Consulta rápida:
MATCH (proj:Projeto {id:'$proj_s'})<-[:REFERE_A]-(ev:Evento)
RETURN
  ev.ts            AS ts,
  ev.resumo        AS resumo,
  ev.bloqueios     AS bloqueios,
  ev.prazo_sketch  AS prazo_sketch,
  ev.prazo_cad     AS prazo_cad,
  ev.participantes AS participantes
ORDER BY ts DESC;
"@

# garante pasta
$coreDir = "projects/Core"
if (!(Test-Path $coreDir)) {
    New-Item -ItemType Directory -Path $coreDir | Out-Null
}

# nome de arquivo cypher com data limpa
$tsFile = $ts.Replace(":", "").Replace("-", "").Replace("T","_").Replace("Z","Z")
$cypherFile = "$coreDir/session_${proj}_$tsFile.cypher"
$cypherContent | Out-File -FilePath $cypherFile -Encoding UTF8

Write-Host "Cypher operacional gerado em $cypherFile"

Write-Host "=== 4. Commit do Cypher e push ==="

git add "$cypherFile" | Out-Null
$featMsg = "feat($proj): status operacional $ts"
git commit -m "$featMsg" --allow-empty | Out-Null
git push origin main | Out-Null

Write-Host "Cypher commitado e enviado."

Write-Host "=== 5. BOOT RESUME para próxima janela ==="
Write-Host ""
Write-Host "Cole isto como primeira mensagem na PRÓXIMA conversa nova:"
Write-Host ""
# pega hash do main atual
$lastHash = git rev-parse HEAD

$bootResume = @"
BOOT RESUME
branch_base: main
ultimo_commit_main: $lastHash
ultimo_boot_now_json: $bootOut
pendencias_abertas:
  - $bloqueios
  - sketch até $prazoSketch
  - CAD indicativo até $prazoCAD
  - acompanhamento projeto $proj
"@

$bootResume | Tee-Object -FilePath "BOOT_RESUME_$ts.txt"

Write-Host $bootResume
Write-Host ""
Write-Host "Salvo também em BOOT_RESUME_$ts.txt"

Write-Host "=== Fim. Você pode fechar a janela. ==="
