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
	# python ingest/run_ingest_all.py
	@echo "Ingest placeholder: adjust Makefile to point to real script."

# 4. Limpeza de logs antigos (ex: arquivos de log com mais de 30 dias)
clean-logs:
	python scripts/clean_logs.py

# 5. Full cycle: health-check → ingestão → backup → limpeza de logs
full-cycle: healthcheck ingest backup clean-logs
	@echo "Full cycle Menir concluído."
