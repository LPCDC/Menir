# Makefile – automações básicas para Menir

.PHONY: healthcheck backup ingest clean-logs full-cycle

# Carregar variáveis de ambiente (se existirem) e exportar
# A sintaxe 'include' é padrão make, mas a exportação de vars de .env
# pode variar. No Windows/PowerShell nem sempre funciona bem via make sem shell Unix.
# Assumimos que o python carrega .env via python-dotenv se necessário, 
# ou que as vars já estão no ambiente. 
ENV_FILE := .env
ifneq ("$(wildcard $(ENV_FILE))","")
  include $(ENV_FILE)
  export $(shell sed 's/=.*//' $(ENV_FILE))
endif

# 1. Health-check do grafo (Neo4j / Aura)
healthcheck:
	python scripts/menir_healthcheck_cli.py

# 2. Backup (snapshot + export de logs, se aplicável)
backup:
	@echo "Creating Git Backup..."
	git tag backup-$(shell date +%Y%m%d-%H%M%S) || true
	git push origin --tags
	@echo "Backup Git criado."

# 3. Ingestão (exemplo: ingestão de e-mail, documentos, etc.)
ingest:
	python ingest/run_ingest_all.py

# 4. Limpeza de logs antigos (ex: arquivos de log com mais de 30 dias)
clean-logs:
	python scripts/clean_logs.py

# 5. Full cycle: health-check → ingestão → backup → limpeza de logs
full-cycle: healthcheck ingest backup clean-logs
	@echo "Full cycle Menir concluído."

# 6. Dump (snapshot do grafo) - Exemplo usando neo4j-admin ou script customizado
dump-graph:
	@echo "Creating Graph Dump..."
	# neo4j-admin database dump neo4j --to-path=./backups
	# ou python scripts/export_graph.py
	@echo "Dump placeholder: configure with your specific backup method (APOC, neo4j-admin, etc)."

# 7. Security Scans
secrets-scan:
	@echo "Checking for Gitleaks..."
	@if ! command -v gitleaks > /dev/null 2>&1; then \
		echo "Gitleaks not found. Install: go install github.com/gitleaks/gitleaks/v8@latest"; \
		exit 1; \
	fi
	@gitleaks detect --source . --exit-code 1 --report-path=gitleaks-report.json || true
	@echo "Gitleaks scan complete. Report: gitleaks-report.json"

truffle-scan:
	@echo "Checking for TruffleHog..."
	@if ! command -v trufflehog > /dev/null 2>&1; then \
		echo "TruffleHog not found. Install: pip install trufflehog3"; \
		exit 1; \
	fi
	@trufflehog filesystem . --since-commit HEAD~50 --entropy=True > trufflehog-report.txt || true
	@echo "TruffleHog scan complete. Report: trufflehog-report.txt"

check-secrets: secrets-scan truffle-scan
	@echo "Full secrets check complete."
