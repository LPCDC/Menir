# 🔎 Verificação de Dependências (Dependency Checkers)

Para garantir que seu ambiente está pronto antes de rodar ingestão, auditoria ou o pipeline completo do Menir, há dois scripts disponíveis:

## Comparação

| Modo / Script | Objetivo | Quando usar | Comando |
|--------------|----------|-------------|---------|
| **Local / Desenvolvimento** (`check_dependencies_local.py`) | Verifica apenas presença mínima das bibliotecas principais (ex: `neo4j`) | Ao rodar localmente (Codespace / DEV) ou após criar/atualizar o ambiente Python | `python scripts/check_dependencies_local.py` |
| **Completo / Pré-CI** (`check_dependencies.py`) | Pode (futuramente) incluir checagem de versões mínimas, presença de libs extras como `pandas`, `python-dotenv` etc. | Antes de rodar o pipeline completo, ingestão, auditoria ou deploy via CI/CD | `python scripts/check_dependencies.py` |

> 💡 A ideia é ter uma verificação rápida e permissiva para desenvolvimento cotidiano, sem burocracia — e uma verificação mais rigorosa quando for para uso sério, produção ou automação via CI/CD.

---

## Como proceder

### 1. Ao clonar ou configurar o ambiente pela primeira vez

```bash
# Instalar dependências mínimas
pip install -r requirements.txt

# Ou, manualmente (ex: neo4j, pandas, python-dotenv):
pip install neo4j pandas python-dotenv
```

### 2. Verificar o ambiente (modo local)

```bash
python scripts/check_dependencies_local.py
```

**Esperado:** Será listado cada pacote e seu status (✔ OK ou ✘ FALTA).

### 3. Se estiver faltando alguma dependência

O script vai sugerir o comando `pip install ...` com os pacotes ausentes. Rode esse comando.

### 4. Antes de rodar o pipeline completo

```bash
python scripts/check_dependencies.py
```

(Atualmente funciona igual ao local, mas pode evoluir para checagens mais rigorosas.)

---

## Exemplo de execução

```bash
$ python scripts/check_dependencies_local.py
🔧 Verificando dependências do ambiente (modo local / permissivo)...

✔ OK — pacote 'neo4j' está instalado.

✅ Todas dependências mínimas presentes.
```

Se faltar algum pacote:

```bash
$ python scripts/check_dependencies_local.py
🔧 Verificando dependências do ambiente (modo local / permissivo)...

✔ OK — pacote 'neo4j' está instalado.
✘ FALTA — pacote 'pandas' NÃO está instalado.

⚠️ Dependências faltando:
   - pandas

Para instalar, rode:
    pip install pandas

$ pip install pandas
# ... (instalação)

$ python scripts/check_dependencies_local.py
✔ OK — pacote 'neo4j' está instalado.
✔ OK — pacote 'pandas' está instalado.

✅ Todas dependências mínimas presentes.
```

---

## Customização

Ambos scripts usam a lista `REQUIRED_PACKAGES` em seu topo. Para adicionar novos pacotes, edite-a:

```python
REQUIRED_PACKAGES = [
    "neo4j",
    "pandas",
    "python-dotenv",
    # adicione aqui conforme necessário
]
```

Depois rode o checker novamente para validar.
