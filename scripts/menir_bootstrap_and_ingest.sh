#!/usr/bin/env bash
# Menir Bootstrap and Ingest Pipeline for Itau Project.
#
# This is the orchestration script for the complete Itau data ingestion pipeline.
#
# Prerequisites:
# - Neo4j running and accessible
# - .env file configured with proper credentials
# - Raw data files in appropriate directories
#
# Pipeline stages:
# 1. Pre-check: Neo4j connectivity and health
# 2. Normalization: Convert raw data to JSONL
# 3. Ingestion: Load normalized data into Neo4j graph
# 4. Reporting: Generate audit reports and snapshots
# 5. Post-check: Verify ingestion success
#
# Environment (loaded from .env):
#   NEO4J_URI, NEO4J_USER, NEO4J_PWD, NEO4J_DB
#   MENIR_PROJECT_ID
#   DATA_ROOT, LOGS, REPORTS, SNAPSHOT
#   RAW_EMAILS, NORM_EMAILS
#   RAW_EXTRATOS, NORM_EXTRATOS
#   RAW_WHATS, NORM_WHATS
#   DOCS

set -e

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env file not found. Copy .env.template to .env and configure."
    exit 1
fi

echo "========================================"
echo "Menir Itau Bootstrap & Ingest Pipeline"
echo "========================================"
echo "Project: ${MENIR_PROJECT_ID}"
echo "Neo4j: ${NEO4J_URI}"
echo ""

# ============================================================================
# Stage 1: Pre-checks
# ============================================================================
echo "[1] Pre-checks: Neo4j connectivity and health"
echo ""

python3 scripts/neo4j_bolt_diagnostic.py || {
    echo "❌ Neo4j connectivity check failed"
    exit 1
}

python3 menir_healthcheck_full.py > "${LOGS}/health_before.json" || {
    echo "❌ Health check failed"
    exit 1
}

echo "✓ Pre-checks passed"
echo ""

# ============================================================================
# Stage 2: Normalization (Raw → JSONL)
# ============================================================================
echo "[2] Normalization: Converting raw data to JSONL"
echo ""

# TODO: Implement these normalization tools
# tools/itau_email_to_jsonl.py --input "$RAW_EMAILS/*.mbox" --output "$NORM_EMAILS/itau_emails.jsonl"
# tools/itau_extrato_to_jsonl.py --input "$RAW_EXTRATOS/*.pdf" --output "$NORM_EXTRATOS/extratos.jsonl"
# tools/whatsapp_txt_to_jsonl.py --input "$RAW_WHATS/*" --output "$NORM_WHATS/whatsapp_messages.jsonl"
# tools/docs_to_manifest.py --input "$DOCS/*" --output "$DOCS/itau_docs_manifest.json"

echo "⚠ Normalization tools not yet implemented (see TODO markers above)"
echo ""

# ============================================================================
# Stage 3: Ingestion (JSONL → Neo4j Graph)
# ============================================================================
echo "[3] Ingestion: Loading normalized data into Neo4j"
echo ""

# TODO: Implement these ingestion scripts
# python3 scripts/menir_ingest_email_itau.py \
#     --input "$NORM_EMAILS/itau_emails.jsonl" \
#     --project "$MENIR_PROJECT_ID"

# python3 scripts/menir_ingest_extratos_itau.py \
#     --input "$NORM_EXTRATOS/extratos.jsonl" \
#     --project "$MENIR_PROJECT_ID"

# python3 scripts/menir_ingest_whatsapp_itau.py \
#     --input "$NORM_WHATS/whatsapp_messages.jsonl" \
#     --project "$MENIR_PROJECT_ID"

# python3 scripts/menir_ingest_docs_itau.py \
#     --input "$DOCS/itau_docs_manifest.json" \
#     --project "$MENIR_PROJECT_ID"

echo "⚠ Ingestion scripts not yet implemented (see TODO markers above)"
echo ""

# ============================================================================
# Stage 4: Reporting
# ============================================================================
echo "[4] Reporting: Generating audit reports and snapshots"
echo ""

# TODO: Implement these reporting tools
# python3 scripts/menir_generate_itau_report.py --project "$MENIR_PROJECT_ID" --output "$REPORTS/itau_boot_report.md"
# python3 scripts/menir_snapshot.py --project "$MENIR_PROJECT_ID" --output "$SNAPSHOT"

echo "⚠ Reporting tools not yet implemented (see TODO markers above)"
echo ""

# ============================================================================
# Stage 5: Post-checks
# ============================================================================
echo "[5] Post-checks: Verifying ingestion success"
echo ""

python3 menir_healthcheck_full.py > "${LOGS}/health_after.json" || {
    echo "❌ Post-ingestion health check failed"
    exit 1
}

echo "✓ Post-checks passed"
echo ""

echo "========================================"
echo "✅ Menir Itau pipeline completed"
echo "========================================"
echo "Logs: ${LOGS}"
echo "Reports: ${REPORTS}"
echo "Snapshot: ${SNAPSHOT}"
echo ""
echo "Next steps:"
echo "  1. Implement normalization tools in tools/ directory"
echo "  2. Implement ingestion scripts in scripts/ directory"
echo "  3. Implement reporting tools in scripts/ directory"
echo "  4. Place raw data files in appropriate data/itau/* directories"
echo "  5. Re-run this script to execute full pipeline"
