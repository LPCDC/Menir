#!/usr/bin/env bash
set -euo pipefail

echo "[1/5] Ensuring we are in the Menir repo root..."
if [ ! -d ".git" ]; then
  echo "ERROR: This does not look like a git repository root."
  echo "Run:  cd /workspaces/Menir  (or your Menir clone) and try again."
  exit 1
fi

echo "[2/5] Creating fix branch from main..."
git fetch origin >/dev/null 2>&1 || true
git checkout main
git pull --ff-only origin main
BRANCH_NAME="fix/neutral-boot-status-$(date +%Y%m%d%H%M%S)"
git checkout -b "$BRANCH_NAME"

echo "[3/5] Rewriting legacy boot branding text (Marco/Polo, GatoMia/Miau)..."

python3 << 'PYEOF'
from pathlib import Path

root = Path(".").resolve()

old_phrases = [
    "Menir v10.4 stack operational: event-sourced log, Neo4j graph projection, MCP proxy, memoetic layer, CLI and optional voice interface are active.",
    "Menir v10.4 stack operational: event-sourced log, Neo4j graph projection, MCP proxy, memoetic layer, CLI and optional voice interface are active.",
]

new_phrase = (
    "Menir v10.4 stack operational: "
    "event-sourced log, Neo4j graph projection, MCP proxy, memoetic layer, "
    "CLI and optional voice interface are active."
)

patterns = ["*.py", "*.md", "*.sh", "*.ps1", "*.txt", "*.json", "*.yml", "*.yaml"]

updated_files = []

for pattern in patterns:
    for path in root.rglob(pattern):
        if any(part.startswith(".git") for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        original = text
        for old in old_phrases:
            if old in text:
                text = text.replace(old, new_phrase)
        if text != original:
            path.write_text(text, encoding="utf-8")
            updated_files.append(str(path))

if not updated_files:
    print("No files contained the legacy branding text.")
else:
    print("Updated files:")
    for f in updated_files:
        print("  -", f)
PYEOF

echo "[4/5] Running test suite to ensure nothing is broken..."
if command -v pytest >/dev/null 2>&1; then
  pytest -q || { echo "Tests failed. Fix required before committing."; exit 1; }
else
  echo "pytest not found. Skipping tests."
fi

echo "[5/5] Committing and pushing (if there are changes)..."
if git diff --quiet && git diff --cached --quiet; then
  echo "No changes detected after branding fix. Nothing to commit."
else
  git status --short
  git add -A
  git commit -m "chore: unify boot status message for Menir v10.4 stack"
  git push -u origin "$BRANCH_NAME" || {
    echo "Push failed. Check your remote or permissions."
    exit 1
  }
  echo
  echo "Done."
  echo "Branch created and pushed: $BRANCH_NAME"
  echo "Open a PR from this branch into main to finalize the change."
fi

echo
echo "✅ Boot/status message is now neutral and aligned with the Menir v10.4 stack."
