# Security Policy — Menir (versão intermediária)

## 🎯 Objetivo  
Definir diretrizes de segurança, integridade e governança para o repositório Menir, cobrindo credenciais, backup, desenvolvimento seguro, tratamento de dados e controles mínimos necessários.

---

## 🔐 Credenciais e Segredos  
- Credenciais sensíveis (URI, usuário, senha de banco, tokens, chaves) **não devem** ser versionadas no repositório. Use variáveis de ambiente ou cofre de segredos externo.
- Mantenha um arquivo `.env.example` com placeholders e use `.env` (ou equivalente) local — `.env` deve estar listado no `.gitignore`.  
- Periodicamente (ex: a cada 6–12 meses) revise e rode rotação de credenciais, especialmente se o sistema contiver dados sensíveis ou for acessível externamente.  

---

## 🧑‍💻 Boas práticas de desenvolvimento e revisão de código  

- Use práticas de codificação segura (input sanitization, validação, tratamento de erros, “defensive programming”) para mitigar vulnerabilidades comuns.
- Evite commits que misturem funcionalidades e mudanças de segurança ou configuração — mantenha commits pequenos, claros e com escopo definido.  
- Antes de push ou merge: revisar o diff, garantir que não há credenciais embutidas, dados sensíveis, ou artefatos desnecessários.  
- **Git Hooks**: Recomenda-se instalar o hook de `pre-commit` local para bloquear segredos acidentais.
  - Instale gitleaks e depois rode: `.\scripts\setup_hooks.ps1`
- Se usar dependências externas, mantenha-as atualizadas e monitore vulnerabilidades (dependabot, scanner de dependências, etc.).

---

## 🔄 Backup, Logs e Persistência de Dados  

- Implemente backup regular da base de dados / grafo (dump, exportação ou snapshot), logs e metadados — preferencialmente de forma automatizada.
- Armazene backups em local seguro, separado do repositório principal (drive criptografado, storage externo, cofre offline etc.).  
- Verifique periodicamente a integridade dos backups (testes de restauração, consistência dos dados após restore).
- Limite acesso aos backups e logs apenas a usuários autorizados (princípio de menor privilégio).

---

## 🧩 Tratamento de Dados Pessoais / Dados Sensíveis (quando aplicável)  

Se o sistema armazenar dados sensíveis ou pessoais:

- Classifique os dados conforme sensibilidade ou criticidade, definindo nível de proteção apropriado para cada categoria.
- Proteja dados em trânsito e, se possível, em repouso (uso de criptografia, comunicação segura).  
- Aplique restrições de acesso: only-need-to-know, logging de acesso, controle de permissões.
- Documente finalidade, responsabilidade, tempo de retenção e descarte seguro — para garantir rastreabilidade e conformidade.  

---

## 🧪 Governança de Vulnerabilidades & Incidentes  

- Adicione este arquivo `SECURITY.md` ao repositório (raiz, docs/ ou `.github/`) — facilita visibilidade da política de segurança.
- Defina processo de relato de vulnerabilidades: endereço de contato, prazos estimados de resposta, processo de correção, versionamento de release corrigido.  
- Mantenha histórico de versões da política de segurança e atualize após mudanças significativas no sistema, dependências ou infraestrutura.  

---

## ✅ Privilégios e Controle de Acesso  

- Adote o princípio de **menor privilégio** (least privilege): cada usuário ou serviço deve ter apenas o acesso essencial para sua função.
- Para repositórios hospedados (ex: GitHub), use autenticação forte, controle de permissões e, se possível, funcionalidades de segurança da plataforma (scan de segredos, code scanning, etc.)
- Evite expor segredos em histórico de commits ou logs públicos; garanta que pushes públicos não contenham dados sensíveis.

---

## 📄 Documentação & Transparência  

- Mantenha README, `.env.example`, e `SECURITY.md` atualizados em cada versão significativa do projeto.  
- Documente decisões importantes de segurança (criptografia usada, política de backup, controle de acesso, ciclo de vida de dados, padrões de codificação).  
- Se houver colaboradores, comunique claramente a política de segurança e responsabilidades.
