# ✅ Checklist de Boas Práticas — Menir Post-Bootstrap

## 📦 Ambiente & Dependências  
- [ ] `requirements.txt` atualizado com todas as dependências usadas (ex.: neo4j, python-dotenv, numpy, pytest, etc.).  
- [ ] Sempre que adicionar nova dependência, rodar `pip install -r requirements.txt` antes de commit.  
- [ ] Manter o ambiente virtual (ou devcontainer) ativo para isolamento e consistência.  

## 🔌 Banco de Dados Neo4j  
- [ ] Verificar conectividade Neo4j via script sanity (ex.: `scripts/sanity_neo4j_full.py`) sempre que iniciar o container.  
- [ ] Confirmar estrutura de índices/constraints necessários antes de ingestão de dados em lote.  
- [ ] Garantir que credenciais sensíveis (URI, usuário, senha) venham de variáveis de ambiente — nunca hard-coded em código/fonte.  
- [ ] Não versionar dados de instância local (dump DB, volume de dados, logs brutos) — manter `.gitignore` atualizado para evitar vazamento.  

## 🧪 Pipelines & Automação  
- [ ] Scripts de ingestão, exportação, sanity, etc., devem rodar sem erros básicos — garantir testes "smoke test" após mudanças.  
- [ ] Antes de merges ou commits importantes de pipeline, rodar sanity + testes unitários (se houver).  
- [ ] Para qualquer mudança de schema ou estrutura do grafo: registrar changelog no repositório, versionar e comunicar no protocolo de auditoria interno.  

## 🔐 Segurança & Privacidade  
- [ ] Nunca expor PII ou dados sensíveis em repositório público ou commits históricos.  
- [ ] Quando for necessário armazenar dados privados, usar criptografia, hashing ou mascaramento conforme política LGPD.  
- [ ] Logs sensíveis ou dados brutos devem permanecer fora do versionamento — somente metadados auditáveis podem ser versionados.  

## 🧑‍💻 Fluxo de Versionamento & Deploy  
- [ ] Commit + push devem ser feitos com mensagens claras e contextualizadas (ex.: "bootstrap: finalize setup v10.4.1").  
- [ ] Tags de versão (ex.: `v10.4.1-bootstrap`) criadas para marcar milestones importantes (bootstrap, releases, migrações).  
- [ ] Antes de cada nova feature ou pipeline grande: criar branch separado, testar isoladamente, revisar, só depois merge-back.  

## 📄 Documentação & Transparência  
- [ ] README.md sempre atualizado para refletir estado real do setup (devcontainer, comandos, variáveis de ambiente, dependências).  
- [ ] Manter documentação interna (ex.: guia de uso, scripts padrões, convenções) atualizada e versionada.  
- [ ] Para scripts novos ou pipelines: incluir doc-string ou comentário claro explicando propósito, uso esperado, entradas/saídas, pré-requisitos.  

## 🧰 Rotina de Inspeção / Manutenção  
- [ ] Sempre que abrir o projeto: rodar sanity Neo4j + verificar integridade das dependências.  
- [ ] Periodicamente (ex.: mensal) revisar `requirements.txt`, eliminar dependências obsoletas ou não utilizadas.  
- [ ] Fazer backup seguro dos dados, especialmente se usar instância local — preferir instância cloud ou export de dump seguro.  
- [ ] Versionar schema e migrações de dados com cautela, documentando alterações de estrutura e implicações.  

## ✅ Meta de Estado Estável  
Objetivo: manter ambiente em estado de "pronto para desenvolver": dependências instaladas, banco acessível, pipelines testáveis, versionamento limpo, documentação coerente, privacidade garantida — sem pendências estruturais.  
