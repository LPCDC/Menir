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

# Email normalization
if [ -d "$RAW_EMAILS" ] && [ "$(ls -A "$RAW_EMAILS")" ]; then
    echo "Processing emails from $RAW_EMAILS..."
    python3 tools/itau_email_to_jsonl.py \
        --input "$RAW_EMAILS" \
        --output "$NORM_EMAILS" \
        --project-id "$MENIR_PROJECT_ID" || {
        echo "⚠ Email normalization warning (continuing...)"
    }
    echo "✓ Email normalization completed"
else
    echo "⚠ No raw emails found in $RAW_EMAILS (skipping)"
fi
echo ""

# WhatsApp normalization
if [ -d "$RAW_WHATS" ] && [ "$(ls -A "$RAW_WHATS")" ]; then
    echo "Processing WhatsApp messages from $RAW_WHATS..."
    python3 tools/whatsapp_txt_to_jsonl.py \
        --input "$RAW_WHATS" \
        --output "$NORM_WHATS" \
        --project-id "$MENIR_PROJECT_ID" || {
        echo "⚠ WhatsApp normalization warning (continuing...)"
    }
    echo "✓ WhatsApp normalization completed"
else
    echo "⚠ No raw WhatsApp messages found in $RAW_WHATS (skipping)"
fi
echo ""

# Bank statement normalization (extratos)
if [ -d "$RAW_EXTRATOS" ] && [ "$(ls -A "$RAW_EXTRATOS")" ]; then
    echo "Processing bank statements from $RAW_EXTRATOS..."
    python3 tools/itau_extrato_to_jsonl.py \
        --input "$RAW_EXTRATOS" \
        --output "$NORM_EXTRATOS" \
        --project-id "$MENIR_PROJECT_ID" || {
        echo "⚠ Bank statement normalization warning (continuing...)"
    }
    echo "✓ Bank statement normalization completed"
else
    echo "⚠ No raw bank statements found in $RAW_EXTRATOS (skipping)"
fi
echo ""

# Document manifest generation
if [ -d "$DOCS" ] && [ "$(ls -A "$DOCS")" ]; then
    echo "Generating document manifest from $DOCS..."
    python3 tools/docs_to_manifest.py \
        --input "$DOCS" \
        --output "$DOCS/manifest.json" || {
        echo "⚠ Document manifest warning (continuing...)"
    }
    echo "✓ Document manifest generated"
else
    echo "⚠ No documents found in $DOCS (skipping)"
fi
echo ""

# ============================================================================
# Stage 3: Ingestion (JSONL → Neo4j Graph)
# ============================================================================
echo "[3] Ingestion: Loading normalized data into Neo4j"
echo ""

# Email ingestion
if [ -f "$NORM_EMAILS/emails.jsonl" ]; then
    echo "Ingesting emails from $NORM_EMAILS/emails.jsonl..."
    python3 scripts/menir_ingest_email_itau.py \
        --input "$NORM_EMAILS/emails.jsonl" \
        --project-id "$MENIR_PROJECT_ID" || {
        echo "⚠ Email ingestion warning (continuing...)"
    }
    echo "✓ Email ingestion completed"
else
    echo "⚠ No normalized emails found (skipping)"
fi
echo ""

# Bank statement ingestion
if [ -f "$NORM_EXTRATOS/transactions.jsonl" ]; then
    echo "Ingesting transactions from $NORM_EXTRATOS/transactions.jsonl..."
    python3 scripts/menir_ingest_extratos_itau.py \
        --input "$NORM_EXTRATOS/transactions.jsonl" \
        --project-id "$MENIR_PROJECT_ID" || {
        echo "⚠ Transaction ingestion warning (continuing...)"
    }
    echo "✓ Transaction ingestion completed"
else
    echo "⚠ No normalized transactions found (skipping)"
fi
echo ""

# WhatsApp ingestion
if [ -f "$NORM_WHATS/messages.jsonl" ]; then
    echo "Ingesting WhatsApp messages from $NORM_WHATS/messages.jsonl..."
    python3 scripts/menir_ingest_whatsapp_itau.py \
        --input "$NORM_WHATS/messages.jsonl" \
        --project-id "$MENIR_PROJECT_ID" || {
        echo "⚠ WhatsApp ingestion warning (continuing...)"
    }
    echo "✓ WhatsApp ingestion completed"
else
    echo "⚠ No normalized WhatsApp messages found (skipping)"
fi
echo ""

# Document ingestion
if [ -f "$DOCS/manifest.json" ]; then
    echo "Ingesting documents from $DOCS/manifest.json..."
    python3 scripts/menir_ingest_docs_itau.py \
        --input "$DOCS/manifest.json" \
        --project-id "$MENIR_PROJECT_ID" || {
        echo "⚠ Document ingestion warning (continuing...)"
    }
    echo "✓ Document ingestion completed"
else
    echo "⚠ No document manifest found (skipping)"
fi
echo ""

# ============================================================================
# Stage 4: Reporting
# ============================================================================
echo "[4] Reporting: Generating audit reports and snapshots"
echo ""

# Generate health report and audit trail
echo "Generating audit trail..."
python3 menir_healthcheck_full.py > "${LOGS}/health_after.json" 2>&1 || {
    echo "⚠ Health report generation warning (continuing...)"
}

# Optional: Generate CSV audit exports for each normalized stage
if [ -f "$NORM_EMAILS/emails.jsonl" ]; then
    echo "Recording email ingestion metrics..."
    wc -l "$NORM_EMAILS/emails.jsonl" > "${REPORTS}/email_ingest_summary.txt"
fi

if [ -f "$NORM_EXTRATOS/transactions.jsonl" ]; then
    echo "Recording transaction ingestion metrics..."
    wc -l "$NORM_EXTRATOS/transactions.jsonl" > "${REPORTS}/transaction_ingest_summary.txt"
fi

if [ -f "$NORM_WHATS/messages.jsonl" ]; then
    echo "Recording WhatsApp ingestion metrics..."
    wc -l "$NORM_WHATS/messages.jsonl" > "${REPORTS}/whatsapp_ingest_summary.txt"
fi

echo "✓ Reporting completed"
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
echo ""
echo "Summary:"
echo "  Project: $MENIR_PROJECT_ID"
echo "  Logs: ${LOGS}"
echo "  Reports: ${REPORTS}"
echo ""
echo "Health check files:"
echo "  Before: ${LOGS}/health_before.json"
echo "  After: ${LOGS}/health_after.json"
echo ""
echo "Next steps:"
echo "  1. Review health_before.json vs health_after.json"
echo "  2. Run test suite: pytest tests/test_neo4j_basics.py -v"
echo "  3. Query graph: cypher-shell -u \$NEO4J_USER -p \$NEO4J_PWD -a \$NEO4J_URI"
echo ""
