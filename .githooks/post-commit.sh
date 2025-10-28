#!/bin/sh
# .githooks/post-commit.sh
# Hook Git pós-commit – roda no Bash

ts=$(date +"%Y-%m-%d_%H-%M-%S")
hash=$(git rev-parse --short HEAD)
author=$(git log -1 --pretty=format:'%an')
msg=$(git log -1 --pretty=format:'%s')

checkpointDir="checkpoints"
logFile="$checkpointDir/last_hook.log"
checkpointFile="$checkpointDir/${ts}_${hash}.diff"

mkdir -p "$checkpointDir"

echo "[HOOK] Commit $hash by $author → '$msg' em $ts" >> "$logFile"

if git diff-tree --no-commit-id --name-only -r HEAD | grep -q '^cypher/'; then
    git diff HEAD^ HEAD > "$checkpointFile"
    echo "[HOOK] Checkpoint salvo: $checkpointFile" >> "$logFile"

    cypher-shell -a "neo4j+s://085c38f7.databases.neo4j.io" \
        -u "neo4j" \
        -p "bvPp561reYBKtaNPwgPG4250tI9RFKcjNKkhoXG5dGc" \
        -f "cypher/validate_claims_final.cypher" >> "$logFile" 2>&1
else
    echo "[HOOK] Sem mudanças em cypher/, sem checkpoint" >> "$logFile"
fi
