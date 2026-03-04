#!/bin/bash
# scripts/ci_pipeline.sh
# Menir Phase 41 - Automated CI/CD validation
# Must return exit code 0 on success, terminating the pipeline otherwise.

set -e # Exit immediately if any command returns a non-zero status

CURRENT_DATE=$(date "+%Y-%m-%d %H:%M:%S")
echo "========================================================="
echo "[$CURRENT_DATE] INITIATING MENIR CI PIPELINE"
echo "========================================================="

echo "\n=> [1/3] Running Strict Linter (Ruff) on src/v3/ and tests/"
# Check for syntactical/complexity constraints
ruff check src/v3/ tests/
echo "   ✅ Ruff Check PASSED."

echo "\n=> [2/3] Running Static Type Checker (MyPy) on src/v3/"
mypy
echo "   ✅ MyPy Check PASSED."

echo "\n=> [3/3] Running Test Suite Validation (PyTest isolated context)"
# Ensure strictly required test markers are mapped
python -m pytest tests/v3/ -v
echo "   ✅ PyTest Execution PASSED."

echo "\n========================================================="
echo "[$CURRENT_DATE] CI PIPELINE COMPLETED SUCCESSFULLY (EXIT 0)"
echo "========================================================="
