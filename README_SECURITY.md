# MENIR SECURITY BASELINE

Status: v5.0 BootNow
Responsavel: Luiz (admin unico)

1. Segredos
- .env.local guarda tokens e nao entra no Git.
- Se token vazar ele deve ser trocado (rotacionado) e o antigo revogado.
  (Boa prÃ¡tica: segredos expostos devem ser rotacionados imediatamente. :contentReference[oaicite:6]{index=6})

2. Commits e push automaticos
- push_agent.py e o unico caminho oficial de commit/push automatico.
- Cada commit usa prefixo [auto-menir] e timestamp ISO.

3. Auditoria
- status/status_update.json publica estado resumido e tarefas abertas.
- zk_log.py guarda log completo local com hash e horario.
- Apenas o resumo zk_log_digest (hash e horario) vai para o Git.

4. LGPD
- Campo lgpd_consent em status/status_update.json controla se nomes completos e dados pessoais aparecem nos relatorios que vao para o repo e para o Grok.
- Se lgpd_consent=false, usar iniciais e remover identificadores diretos.
- A LGPD exige necessidade e minimizaÃ§Ã£o: tratar sÃ³ o mÃ­nimo dado pessoal necessÃ¡rio para a finalidade declarada. :contentReference[oaicite:7]{index=7}

5. Branch protegido
- Branch release/menir-aio-v5.0-boot deve ter revisao e checagens antes de merge.
