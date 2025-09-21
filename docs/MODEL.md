# MODEL.md (MENIR — Neo4j Gold)

## Labels
- Projeto, Documento, Pessoa, Conta, Transacao

## Relationships
- (Documento)-[:REFERE_A]->(Projeto)
- (Transacao)-[:ENVOLVENDO]->(Pessoa|Conta)
- (Documento)-[:ANEXA]->(Documento)
- (Documento {doc_type:'email'})-[:REPLY_TO]->(Documento)

## Campos essenciais
- Documento: id, doc_type, mime, sha256, tlsh, source, created_at, uri, project_slug, status, (message_id/in_reply_to/references)
- Transacao: id, data, valor, moeda, ref_banco, descricao

## Constraints/Índices (já padronizados)
- UNIQUE: Projeto.slug, Documento.id, Transacao.id, Pessoa.id, Conta.id
- Índices auxiliares: Transacao.data (se necessário)
