# Makefile – automações básicas para Menir

.PHONY: healthcheck backup ingest clean-logs full-cycle

# Carregar variáveis de ambiente
ENV_FILE := .env
ifneq ("$(wildcard $(ENV_FILE))","")
  include $(ENV_FILE)
  export $(shell sed 's/=.*//' $(ENV_FILE))
endif

# 1. Health-check do grafo (Neo4j / Aura)
healthcheck:
	@echo "Running Healthcheck..."
	python scripts/menir_healthcheck_cli.py

# 2. Backup (snapshot + export de logs, se aplicável)
backup:
	@echo "Creating Git Backup..."
	git tag backup-$(shell date +%Y%m%d-%H%M%S) || true
	git push origin --tags
	@echo "Backup Git criado."

# 3. Ingestão (exemplo: ingestão de e-mail, documentos, etc.)
ingest:
	@echo "Running Ingestion (Placeholder)..."
	# python ingest/run_ingest_all.py
	@echo "Ingestion complete."

# 4. Limpeza de logs antigos (ex: arquivos de log com mais de 30 dias)
clean-logs:
	@echo "Cleaning old logs..."
	@if exist logs ( forfiles /p "logs" /s /m *.* /d -30 /c "cmd /c del @path" ) else ( echo "Logs directory does not exist." )
	@echo "Logs antigos verificados."

# 5. Full cycle: health-check → ingestão → backup → limpeza de logs
full-cycle: healthcheck ingest backup clean-logs
	@echo "Full cycle Menir concluído."
