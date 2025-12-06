#!/bin/bash
# -*- coding: utf-8 -*-
#
# Menir — Daily Check-Out Ritual / Save-State Script
# 
# Executa: pull, health-check, status, commit, push, tag (opcional)
# Ideal para encerrar o dia / sessão no Codespace com segurança

set -e

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S UTC")
DATESTR=$(date +"%Y%m%d")
CHECKPOINT_TAG="checkpoint-$DATESTR"

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           Menir Daily Check-Out Ritual                         ║"
echo "║           $TIMESTAMP                 ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Pull
echo "[1/6] Pulling latest changes from main..."
git pull origin main
echo "✅ Pull completed"
echo ""

# Step 2: Health check
echo "[2/6] Running full health check..."
python3 scripts/health_check_full.py
echo ""

# Step 3: Display report
echo "[3/6] Health check report:"
echo "---"
cat menir_full_check_report.json | head -20
echo "..."
echo ""

# Step 4: Git status
echo "[4/6] Current git status:"
git status --short || true
echo ""

# Step 5: Commit and push
echo "[5/6] Committing and pushing..."
git add .
if git diff --cached --quiet; then
    echo "ℹ️  No changes to commit (working tree clean)"
else
    git commit -m "chore: daily save-state – health check $(date +%Y-%m-%d)"
    git push origin main
    echo "✅ Changes committed and pushed"
fi
echo ""

# Step 6: Optional checkpoint tag
echo "[6/6] Optional: Create checkpoint tag?"
echo "  Command: git tag -a '$CHECKPOINT_TAG' -m 'Checkpoint $TIMESTAMP'"
echo ""
read -p "  Create checkpoint tag now? (y/N): " -r REPLY
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git tag -a "$CHECKPOINT_TAG" -m "Checkpoint $TIMESTAMP"
    git push origin "$CHECKPOINT_TAG"
    echo "✅ Tag '$CHECKPOINT_TAG' created and pushed"
else
    echo "ℹ️  Skipped checkpoint tag"
fi
echo ""

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                   ✅ Check-Out Complete                        ║"
echo "║                                                                ║"
echo "║  Repository is clean and synced. Safe to close Codespace.    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
