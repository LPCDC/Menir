#!/usr/bin/env sh
# .githooks/post-commit.sh

echo "[HOOK] Post-commit rodando em $(date)" >> checkpoints/last_hook.log

if git diff-tree --no-commit-id --name-only -r HEAD | grep -q '^cypher/'; then
  echo "[HOOK] Mudança detectada em cypher → checkpoint" >> checkpoints/last_hook.log
  mkdir -p checkpoints
  git diff -U0 HEAD^ HEAD > "checkpoints/$(date +%Y-%m-%d_%H-%M-%S)_diff.patch"
fi
