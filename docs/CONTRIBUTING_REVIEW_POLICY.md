# Política de Revisão e Qualidade — Menir System

**Data**: 10/12/2025
**Escopo**: Todo código mergeado na `main`.

> **Nota sobre Templates**:
> *   **PRs Comuns**: O template padrão é aplicado automaticamente.
> *   **PRs de Infra/Segurança**: Adicione `?template=infra_security.md` na URL de criação do PR para carregar o checklist rigoroso.

---

## 1. Princípios de Engenharia

1.  **Soberania Primeiro**: O código nunca deve exfiltrar dados (`data/`) sem consentimento explícito e auditado.
2.  **Logs são Sagrados**: Se uma feature crítica não loga em `logs/operations.jsonl`, ela está incompleta.
3.  **Falhe Seguro (Fail-Safe)**: Em dúvida (token inválido, disco cheio), o sistema deve parar e proteger os dados, nunca corrompê-los.

---

## 2. Regras de Pull Request

### 2.1. Testes Obrigatórios
Todo PR deve passar pelo **Smoke Test** (`scripts/verify_release.py`) se tocar em:
*   Inicialização (`boot_now`, `mcp_server`).
*   Segurança (Auth, `check_db_auth`).
*   Dados (Backup, Sync).

### 2.2. Segurança e Credenciais
*   **Proibido**: Commitar `.env`, chaves de API, ou senhas hardcoded.
*   **Obrigatório**: Usar `os.getenv()` com falha explícita se a variável for crítica em ambiente PROD.

### 2.3. Code Cleanliness
*   Remova `print("debug...")` antes do merge. Use `logging` ou o sistema de logs estruturado.
*   Comentários devem explicar o *Porquê*, não o *Como* (o código já diz o como).

---

## 3. Matriz de Aprovação

| Tipo de Mudança | Exigência |
| :--- | :--- |
| **Feature / UI** | 1 Reviewer + Teste Manual |
| **Infra / Auth / Backup** | **2 Reviewers** (ou 2 rodadas de validação) + Smoke Test Logado |
| **Documentação** | Auto-merge permitido se trivial |

---
*A qualidade do Menir reflete a confiança que podemos depositar nele como nosso "Segundo Cérebro".*
