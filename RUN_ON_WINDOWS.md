# Instruções para Rodar no Neo4j Desktop (Windows)

## Pré-requisitos

1. **Neo4j Desktop** rodando na máquina Windows
2. **Python 3.8+** instalado no Windows
3. Credenciais do Neo4j Desktop:
   - URI: `neo4j://127.0.0.1:7687`
   - User: `neo4j`
   - Password: `bvPp561reYBKtaNPwgPG4250tI9RFKcjNKkhoXG5dGc`

## Passo 1: Instalar dependências Python

Abra o PowerShell ou CMD no Windows e execute:

```powershell
pip install neo4j
```

## Passo 2: Configurar variáveis de ambiente

No PowerShell:

```powershell
$env:NEO4J_URI="neo4j://127.0.0.1:7687"
$env:NEO4J_USER="neo4j"
$env:NEO4J_PASSWORD="bvPp561reYBKtaNPwgPG4250tI9RFKcjNKkhoXG5dGc"
$env:NEO4J_DB="neo4j"
```

Ou no CMD:

```cmd
set NEO4J_URI=neo4j://127.0.0.1:7687
set NEO4J_USER=neo4j
set NEO4J_PASSWORD=bvPp561reYBKtaNPwgPG4250tI9RFKcjNKkhoXG5dGc
set NEO4J_DB=neo4j
```

## Passo 3: Executar os scripts (na ordem)

### 3.1 Inicializar o schema

```powershell
python livro_debora_cap1_ingest.py --init-schema
```

**Saída esperada:**
```
[OK] Conectado ao Neo4j (unknown) em neo4j://127.0.0.1:7687
[OK] Schema v2 garantido (constraints + índices).
[DONE] Execução finalizada.
```

### 3.2 Ingerir dados do Capítulo 1

```powershell
python livro_debora_cap1_ingest.py --ensure-core --ingest-builtin
```

**Saída esperada:**
```
[OK] Conectado ao Neo4j (unknown) em neo4j://127.0.0.1:7687
[OK] Work/Chapter/ChapterVersion garantidos. databaseOrigin=unknown
[INFO] Ingerindo Cap. 1 a partir do JSON embutido...
[OK] Ingestão de Cap. 1 concluída.
[DONE] Execução finalizada.
```

### 3.3 Auditar o grafo

```powershell
python audit_livro_debora.py
```

**Saída esperada:**
```
=== NODE COUNTS BY LABEL ===
Work: 1
Chapter: 1
ChapterVersion: 1
Scene: 4
Event: 13
Character: 9
Place: 4
...

=== RELATIONSHIP COUNTS BY TYPE ===
HAS_CHAPTER: 1
VERSION_OF: 1
HAS_SCENE: 4
NEXT_SCENE: 3
SET_IN: 4
APPEARS_IN: 12
OCCURS_IN: 13
NEXT_EVENT: 9
...
```

## Passo 4: Verificar no Neo4j Browser

1. Abra o Neo4j Desktop
2. Clique em "Open" no Neo4j Browser
3. Execute as queries de validação:

```cypher
// Ver estrutura completa
MATCH (w:Work)-[:HAS_CHAPTER]->(c:Chapter)<-[:VERSION_OF]-(v:ChapterVersion)-[:HAS_SCENE]->(s:Scene)
RETURN w.title, c.number, v.versionTag, count(s) AS scenes

// Ver personagens e suas aparições
MATCH (char:Character)-[:APPEARS_IN]->(s:Scene)
RETURN char.name, count(s) AS appearances
ORDER BY appearances DESC

// Ver sequência de eventos na Scene 1
MATCH path = (e:Event)-[:NEXT_EVENT*]->(next:Event)
WHERE e.eventId STARTS WITH 'event_01'
RETURN [n IN nodes(path) | n.summary] AS eventChain
```

## Arquivos necessários

Certifique-se de ter estes arquivos na mesma pasta:

- ✅ `livro_debora_cap1_ingest.py` (ingestão completa)
- ✅ `audit_livro_debora.py` (auditoria do grafo)
- ✅ `setup_livro_debora_schema.py` (opcional, schema alternativo)

## Troubleshooting

### Erro: "neo4j.exceptions.AuthError"
- Verifique se a senha está correta no Neo4j Desktop
- Confirme que o Neo4j está rodando (botão "Start" no Desktop)

### Erro: "Connection refused"
- Confirme que o Neo4j Desktop está ativo
- Verifique se a porta 7687 está aberta

### Erro: "Module not found: neo4j"
- Execute novamente: `pip install neo4j`

## Estrutura dos Dados Ingeridos

- **1 Work**: Better in Manhattan (Débora Vezzali)
- **1 Chapter**: Capítulo 1
- **1 ChapterVersion**: v1.0 com hash de integridade
- **4 Scenes**:
  1. Manhã na casa dos Howell
  2. Chegada à Trailblazer Academy
  3. Aula de Educação Física
  4. Almoço no refeitório
- **13 Events** encadeados com NEXT_EVENT
- **9 Characters**: Caroline, Spencer, Lauren, Matt, Dean, Andy, Olivia, Diretor Smith, Sr. O'Donnel
- **4 Places**: Apartamento, Escola, Ginásio, Refeitório

## Próximos Passos

Após ingestão bem-sucedida:

1. Use `setup_livro_debora_schema.py` para adicionar mais capítulos
2. Explore as queries Cypher para análise narrativa
3. Adicione mais cenas/eventos ao JSON embutido
4. Exporte os dados para backup com Neo4j Desktop

---

**Última atualização:** 2025-12-06  
**Versão Menir:** v11 (Schema v2 com databaseOrigin tracking)
