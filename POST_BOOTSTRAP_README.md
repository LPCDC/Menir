# ✅ Checklist de Boas Práticas — Menir Post-Bootstrap

## 📦 Ambiente & Dependências
- [ ] `requirements.txt` deve estar atualizado com todas as dependências usadas (ex.: neo4j, python-dotenv, numpy, pytest, etc.).
- [ ] Sempre que adicionar nova dependência, rodar `pip install -r requirements.txt` antes de commit.
- [ ] Manter o ambiente virtual (ou devcontainer) ativo para isolamento e consistência.

## 🔌 Banco de Dados Neo4j
- [ ] Verificar conectividade Neo4j via script sanity (ex.: `scripts/sanity_neo4j_full.py`) sempre que iniciar o container.
- [ ] Confirmar presença de índices/constraints necessários antes de ingestão de dados em lote.
- [ ] Garantir que credenciais sensíveis (URI, usuário, senha) venham de variáveis de ambiente — nunca hard-coded.
- [ ] Não versionar dados de instância local (dump DB, volume de dados, logs brutos) — manter `.gitignore` apropriado para evitar vazamento.

## 🧪 Pipelines & Automação  
- [ ] Scripts de ingestão, exportação, sanity, etc., devem rodar sem erros básicos — fazer testes "smoke test" após cada alteração.
- [ ] Antes de merges ou commits importantes de pipeline, rodar sanity + testes unitários (se houver).
- [ ] Quando houver mudança de schema ou estrutura do grafo: registrar changelog no repositório e versionar alterações.

## 🔐 Segurança & Privacidade  
- [ ] Nunca expor PII ou dados sensíveis em repositório público ou commits históricos.
- [ ] Para dados pessoais ou confidenciais, usar criptografia, hashing ou mascaramento conforme política LGPD.
- [ ] Dados sensíveis ou logs brutos devem permanecer fora do versionamento — apenas metadados auditáveis podem ser versionados.

## 🧑‍💻 Fluxo de Versionamento & Deploy  
- [ ] Commit + push devem ser feitos com mensagens claras e contextualizadas (ex.: "bootstrap: finalize setup v10.4.1").
- [ ] Usar tags de versão (ex.: `v10.4.1-bootstrap`) para marcar marcos importantes (bootstrap, releases, migrações).
- [ ] Para novas features ou pipelines maiores: criar branch separada, testar isoladamente, revisar, e só então merge-back para main.

## 📄 Documentação & Transparência  
- [ ] `README.md` deve refletir o estado real do setup (devcontainer, comandos, variáveis de ambiente, dependências).  
- [ ] Manter documentação interna (guias de uso, scripts padrão, convenções) atualizada e versionada.  
- [ ] Para scripts novos ou pipelines, incluir doc-string ou comentário explicativo (propósito, uso, entradas/saídas, pré-requisitos).

## 🧰 Rotina de Inspeção / Manutenção  
- [ ] Sempre que retomar o projeto: rodar sanity Neo4j + verificar integridade das dependências.  
- [ ] Periodicamente (ex.: mensal) revisar `requirements.txt` e remover dependências obsoletas.  
- [ ] Fazer backup seguro dos dados importantes — se usar instância local, considerar migração para instância remota ou dump seguro.  
- [ ] Versionar schema e migrações com cuidado, documentando mudanças estruturais e seus impactos.  

## ✅ Meta de Estado Estável  
Manter o ambiente em estado "pronto para desenvolver": dependências instaladas, banco acessível, pipelines funcionais, versionamento limpo, documentação coerente, privacidade respeitada — tudo sem pendências estruturais.  
