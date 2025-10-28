# LGPD Policy - Menir v5.0

1. Escopo
   - O Menir registra fatos pessoais, financeiros, técnicos e de saúde em grafo Neo4j.
   - O Menir armazena interações com bancos e condomínios para prova jurídica e manutenção patrimonial.

2. Princípios
   - Mínimo necessário: só guardar o que sustenta prova, manutenção, auditoria ou operação.
   - Transparência: toda inserção gera hash e timestamp UTC em logs/zk_audit.jsonl.
   - Criptografia: dados sensíveis ficam locais, chave Fernet definida em .env.local.
   - Auditoria: hashes são publicados em rede blockchain e IPFS privado.

3. Identificadores
   - Nome completo permitido apenas para:
     - Luiz (titular).
     - Instituições formais (ex: Itaú).
   - Terceiros aparecem mascarados (primeiro nome ou genérico).
   - Eventos bancários e condominiais recebem privacy="lgpd_masked".

4. Base legal
   - Prova jurídica bancária (Projeto Itaú).
   - Conservação patrimonial e valorização de ativo imobiliário (Projeto Tivoli).
   - Manutenção predial e acessibilidade (Projeto Iberê).
   - Relato técnico para clientes e parceiros de arquitetura (Projeto Otani).

5. Retenção
   - Dados permanecem enquanto houver risco jurídico ou impacto patrimonial.
   - Remoção exige atualização do grafo e registro em zk_audit.jsonl com novo hash.

6. Responsável interno
   - Luiz (id: luiz).
   - Última atualização UTC: 2025-10-28T13:18:22Z.
