# Pull Request — Menir (Infra / Segurança / Produção) ���

## ��� Contexto / Motivação  
Descreva objetivo: hardening, backup, logging, auth, deploy seguro, migração, etc.

## ✅ Alterações realizadas  
- [ ] Explicação das mudanças no pipeline, infraestrutura ou segurança  
- [ ] Justificativa técnica clara  
- [ ] Backward compatibility preservada ou migração documentada  

## ��� Checklist Crítico de Segurança & Robustez  

### Persistência & Backup  
- [ ] Backup automático ou manual testado com sucesso  
- [ ] Rotação / retenção de backups verificada  
- [ ] Logs escritos em formato canonical e íntegros  

### Autenticação & Acesso  
- [ ] Tokens, segredos e variáveis sensíveis só via `.env` ou Secrets — nenhum hard-coded  
- [ ] Configuração de auth verificada (modo LAB vs PROD)  
- [ ] Teste de acesso sem token / com token inválido retorna erro (401)  

### Operação / Deploy / Compatibilidade  
- [ ] Scripts de startup/shutdown funcionam em todos os ambientes suportados  
- [ ] Testes de health endpoint e logging funcionais  
- [ ] Documentação atualizada (guia ops, README, instruções de restore)  

## ��� Testes & Verificação Manual  
Descreva como reproduzir — backup, health, auth, logs, restore, etc.

## ��� Migração / Impactos Retroativos (se houver)  
Descreva impacto em dados existentes, necessidade de migração ou comunicação a usuários.

## Observações / Dúvidas pendentes  
<descreva aqui>
