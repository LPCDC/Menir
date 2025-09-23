# LibLabs — Governance Checklist (v0.1)
**Path:** projects/LibLabs/governance/liblabs_governance_checklist_v0.1.md  
**Gerado:** 2025-09-23  
**Autor:** Menir (LibLabs) — consolidado a partir de AIA 2024 + análises locais

---

## Objetivo
Checklist operacional e de risco para adoção de IA em escritórios de arquitetura e para o produto/serviço "Playbook de Adoção LibLabs". Serve também como pré-condição para material comercial.

---

## Principais riscos (priorizados)
1. **Imprecisão técnica / erro de cálculo** — risco alto (ex.: orçamentos, specs).  
2. **Vazamento / tratamento inadequado de dados (LGPD)** — risco alto.  
3. **Viés e exclusão projetual** — risco médio-alto.  
4. **Corrupção de arquivos BIM / Revit** (ações automáticas mal testadas) — risco alto.  
5. **Dependência de fornecedor/terceiro** (API fechada, modelo em nuvem) — risco médio.  
6. **Expectativa de cliente vs entrega automatizada** — risco médio.

---

## Controles obrigatórios (mínimos)
- [ ] **Auth & Acesso**: manter `dbms.security.auth_enabled=true`. Gestão de credenciais em cofre (ex.: HashiCorp Vault / Azure KeyVault) — **proibição** de commits de senhas.
- [ ] **Backup antes de tudo**: snapshot + export completo do .rvt/.rfa/.adsk antes de rodar automações em Revit/BIM.
- [ ] **Ambiente de teste**: toda automação deve ser validada em cópia do projeto (sandbox) antes de rodar em produção.
- [ ] **Auditoria**: log de auditoria para todas as ações automáticas (apoc.log, application logs ou DB logs).
- [ ] **Validação humana**: todo output crítico (orçamento, spec, cálculo de egressos) requer revisão humana marcada como `:verified_by`.
- [ ] **Política LGPD**: coletar somente o mínimo necessário; manter registro de consentimento; anonimizar dados quando possível.
- [ ] **Rate limits / throttling**: limitar chamadas a APIs externas; retries com backoff; circuit breaker.
- [ ] **Versão do modelo e rastreabilidade**: registrar `model_id`, `model_version`, `prompt_hash` para cada ação automatizada.
- [ ] **Test suite**: unit + integration tests para scripts (PowerShell/.py/.cs) com exit codes claros.

---

## Processos (passo-a-passo resumido)
### Deploy piloto (quick wins)
1. Mapear 3 tarefas: (A) geração de drafts de especificação, (B) pesquisas rápidas de fornecedores, (C) assets visuais conceituais.  
2. Criar sandbox do projeto (copiar .rvt/.ifc) → ativar logs.  
3. Rodar automação com `--dry-run` (se aplicável).  
4. Validação humana e ajuste de prompt.  
5. Registrar resultado e métricas (tempo ganho, erros detectados).

### Escala
1. Após 2 projetos validados, habilitar automação para 1 equipe inteira com SLO de revisão.  
2. Implementar verificação contínua de qualidade (QA pipeline).

---

## Métricas de sucesso (KPI)
- Tempo médio poupado por tarefa (target 20–30% em 6 meses).  
- Erros detectados por 100 automações (target <1).  
- Porcentagem de outputs validados por humano (target 100% para outputs críticos).  
- Adoção na equipe (% pessoas treinadas, target 100% em 6 meses).  

---

## Artefatos obrigatórios (para cada piloto)
- `playbook_pilot_<cliente>_vX.md` (passo-a-passo + pré-requisitos)  
- `audit_log_<cliente>_YYYYMMDD.csv`  
- `model_record_<timestamp>.json` (model_id, prompt, prompt_hash, inputs masked)  
- `cypher_ingest` contendo claims / doc refs (ex.: claims_ingest.cypher)

---

## Comandos operacionais (exemplos)
**Adicionar arquivo de governance no repo (PowerShell)**  
```powershell
# cria pasta e escreve o arquivo (rodar na raiz do repo)
$path = "projects\LibLabs\governance\liblabs_governance_checklist_v0.1.md"
New-Item -ItemType Directory -Force -Path (Split-Path $path) | Out-Null
# (cole o conteúdo do arquivo manualmente) ou use Set-Content para gravar
