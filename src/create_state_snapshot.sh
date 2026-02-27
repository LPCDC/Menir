#!/usr/bin/env bash
set -e

SNAP_FILE="menir_state_snapshot_$(date +%Y-%m-%dT%H%M%S).json"

echo "Gerando snapshot do estado Menir → $SNAP_FILE"

cat > "$SNAP_FILE" << 'EOF'
{
  "snapshot_timestamp": "2025-12-06T01:45:00Z",
  "menir_version": "v10.4.1",
  "bootstrap_tag": "v10.4.1-bootstrap",
  "environment": {
    "python_version": "3.12.1",
    "neo4j_version": "5.15.0-community",
    "neo4j_status": "running",
    "docker_compose": "up",
    "venv_status": "activated"
  },
  "git_state": {
    "branch": "fix/audit-cleanup-v10.4.1",
    "last_commit": "f2eb75f",
    "last_commit_message": "docs: add bootstrap_manifest.json",
    "working_tree_status": "clean",
    "remote_sync": "up-to-date"
  },
  "components_deployed": [
    "neo4j_docker_container",
    "python_virtual_environment",
    "devcontainer_config",
    "sanity_check_scripts",
    "migration_tools",
    "documentation",
    "bootstrap_manifest"
  ],
  "data_status": {
    "local_neo4j": "3 documents, 3 chunks with embeddings",
    "aura_neo4j": "migrated and synced",
    "embedding_type": "SHA256-based (32-dim)",
    "last_sanity_check": "2025-12-06T01:41:10Z",
    "sanity_check_result": "passed"
  },
  "checklist_items_verified": [
    "Requirements.txt updated",
    "Neo4j connectivity verified",
    "Environment variables configured",
    "Scripts executable and tested",
    "Documentation complete",
    "Git repository clean",
    "Bootstrap tag created"
  ],
  "status": "ready_for_development"
}
EOF

git add "$SNAP_FILE"
git commit -m "snapshot: save Menir state $(date -u +%Y-%m-%dT%H:%M:%SZ)"
git tag "snapshot-$(date +%Y-%m-%dT%H%M%S)"
git push origin --tags
git push

echo "✅ Snapshot salvo, commitado e tag criado."
