# MENIR_INTERNAL – Menir-10

Comandos principais (raiz do repositório):

- BootNow (Codespace): `python scripts/boot_now.py`
- Tests: `pytest -q && python -m unittest discover -v`
- Export (exemplo): `python menir10_export.py --help`
- Daily report (exemplo): `python scripts/menir10_daily_report.py`

Ambientes:
- Codespace: `/workspaces/Menir`
- PC: `C:\Users\Pichau\Repos\Menir`

Git:
- Atualizar: `git pull origin main`
- Commit: `git add . && git commit -m "Atualiza MENIR_INTERNAL"`
- Push: `git push origin main`

cat << 'EOF' > MENIR_INTERNAL.md
# MENIR_INTERNAL – Manual mínimo do Menir-10

## 1. Estado atual (Menir-10 v5.x)

- Repositório canônico: `LPCDC/Menir` (branch `main`).
- O que está ATIVO hoje:
	- `scripts/boot_now.py`  
		- Registra eventos de boot em `logs/operations.jsonl`.
		- Já está coberto por testes (pytest/unittest OK).
	- Módulos `menir10_export`, `menir10_insights`, `menir10_daily_report`  
		- Testes passando, prontos para trabalhar com **logs de interações** em JSONL
			(ex.: `menir10_interactions.jsonl`), quando esse logger existir.
- O que AINDA NÃO está implementado:
	- Memory Server / FastAPI / Neo4j (RISK-001, RISK-002, etc.).
	- Logger automático de interações GPT → `menir10_interactions.jsonl`.
	- Qualquer consulta obrigatória ao grafo antes da resposta do GPT.

Resumo: hoje o Menir-10 já funciona como **camada de boot + logging auditável**.
O grafo Neo4j e o “oráculo de riscos” entram no Capítulo 2.

---

## 2. Uso diário mínimo (PC ou Codespaces)

### 2.1. Boot por projeto

Dentro da pasta do repositório:

```bash
cd /workspaces/Menir
export MENIR_PROJECT_ID=tivoli   # (no Windows: set MENIR_PROJECT_ID=tivoli)
python scripts/boot_now.py

EOF
