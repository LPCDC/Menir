# Menir – BootNow Codespace (Grafo + Vetores)

Este diretório configura um ambiente completo do Menir em Codespaces:

- **Neo4j 5.15 (Docker Compose)** – banco de grafo com persistência em volumes.
- **Módulo de embeddings (`menir_core.embeddings`)** – backend de embedding plugável.
- **Seed de dados fictício** – pessoas, cidades, livros, tópicos e ~12 citações ricas.
- **Busca vetorial de citações** – `quote_vector_search` com ranking por similaridade.
- **Ingestão de documentos** – `graph_ingest` cria `Project → Document → Chunk` com vetores.

O objetivo: ter um "BootNow" de desenvolvimento que, com **um comando**, levanta Neo4j, semeia um grafo de teste e valida o pipeline de vetores.

---

## 1. Pré-requisitos

No Codespace:

- Docker e `docker compose` funcionais (padrão do Codespaces).
- Python 3.12 já disponível.
- Porta `7687` (Bolt) e `7474` (HTTP) livres dentro do container.

---

## 2. BootNow de desenvolvimento (um comando)

Script principal:

```bash
./scripts/menir_bootnow_codespace.sh
```

Esse script executa:

1. **Cria `.env`** com credenciais Neo4j (se não existir)
2. **Ativa/cria `.venv`** e instala dependências do `requirements.txt`
3. **Reseta Neo4j** (`docker compose down -v` + `up -d`)
4. **Aguarda conectividade** (HTTP 7474 + Bolt 7687)
5. **Executa seed** (`menir/seeds/sample_seed.py`) com dados de teste
6. **Roda smoke tests** (conexão, vector pipeline, embed_and_store)
7. **Demo de busca vetorial** com query exemplo

**Saída esperada:**
```
🎉 BOOTNOW CODESPACE CONCLUÍDO.
Menir + Neo4j + vetores prontos para uso.
```

---

## 3. Estrutura do grafo após seed

### Nós criados:
- **6 pessoas** (Luiz, Débora, Caroline, Mentor Fantasma, Crítico Anônimo, Editora Paciente)
- **3 cidades** (Santos, São Paulo, Guarujá)
- **5 livros** (Livro da Débora, Cadernos de Bordo, Ensaios de Caroline, etc.)
- **6 tópicos** (memória, culpa, liberdade, escrita, arquitetura, cotidiano)
- **12 citações** (quotes de 50-100 palavras cada)

### Relacionamentos:
- `Person -[:LIVES_IN]-> City`
- `Person -[:WROTE]-> Book`
- `Person -[:MENTORS]-> Person`
- `Person -[:SAID]-> Quote`
- `Book -[:HAS_QUOTE]-> Quote`
- `Quote -[:MENTIONS_TOPIC]-> Topic`

---

## 4. Busca vetorial de citações

### CLI:

```bash
python scripts/quote_vector_search.py "memória e culpa" --top-k 5
```

### Como módulo Python:

```python
from menir_core.quote_vector_search import search_quotes

results = search_quotes("memória e culpa", top_k=5)
for sim, quote in results:
    print(f"{sim:.4f} | {quote['id']} | {quote['topics']}")
    print(f"  {quote['text'][:100]}...")
```

### Como funciona:
1. Carrega todas as `Quote` do Neo4j com seus tópicos
2. Gera embedding da query usando `menir_core.embeddings.embed_text()`
3. Gera embedding de cada citação (usando mesmo backend)
4. Calcula similaridade de cosseno entre query e todas as citações
5. Retorna top-K citações ranqueadas por similaridade

**Backend atual:** `DummyHashEmbedding` (SHA256 determinístico, 32 dimensões)  
**Backend futuro:** Trocar por OpenAI, Groq, Gemini ou modelo local implementando `EmbeddingBackend`

---

## 5. Ingestão de documentos

### Ingerir texto direto:

```python
from menir_core.graph_ingest import ingest_document

n_chunks = ingest_document(
    doc_id="meu_doc_001",
    title="Meu Documento",
    full_text="Texto longo aqui... será dividido em chunks de ~800 chars."
)
print(f"Documento ingerido com {n_chunks} chunks")
```

### Ingerir arquivo markdown:

```python
from menir_core.graph_ingest import ingest_markdown_file

n_chunks = ingest_markdown_file(
    path="docs/exemplo.md",
    doc_id="docs_exemplo_md",  # opcional
    title="Exemplo Markdown"    # opcional
)
```

### Estrutura criada no grafo:

```
(Project {id: MENIR_PROJECT_ID})
  ↑ [:PART_OF]
(Document {id: doc_id, title: "...", created_at, updated_at})
  → [:HAS_CHUNK] →
(Chunk {id: "doc_id::chunk::0", index: 0, text: "...", embedding: [...], created_at, updated_at})
  → [:PART_OF] → Document
```

Cada `Chunk` tem:
- `embedding` (LIST<FLOAT>) gerado via `menir_core.embeddings.embed_text()`
- `text` com até 800 caracteres
- `index` sequencial dentro do documento

---

## 6. Módulo de embeddings plugável

Arquivo: `menir_core/embeddings.py`

### Interface:

```python
class EmbeddingBackend(abc.ABC):
    dim: int
    
    @abc.abstractmethod
    def embed(self, text: str) -> List[float]:
        raise NotImplementedError
```

### Backend padrão (dummy):

```python
class DummyHashEmbedding(EmbeddingBackend):
    """SHA256-based deterministic embeddings (32-dim)"""
    def embed(self, text: str) -> List[float]:
        # Usa SHA256 para gerar vetor reproduzível
        ...
```

### Trocar backend:

```python
from menir_core import embeddings

# Exemplo: backend OpenAI (não implementado ainda)
class OpenAIEmbedding(embeddings.EmbeddingBackend):
    def __init__(self):
        self.dim = 1536  # text-embedding-3-small
    
    def embed(self, text: str) -> List[float]:
        import openai
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

# Trocar globalmente:
embeddings._default_backend = OpenAIEmbedding()
```

Toda função que usa `embed_text()` passará a usar o novo backend automaticamente.

---

## 7. Testes e validação

### Smoke tests (incluídos no bootnow):

```bash
python menir_core/test_neo4j_connection.py    # ✅ Conexão OK
python menir_core/test_vector_pipeline.py     # ✅ Similaridades: 0.99, 0.77, -1.00
python menir_core/embed_and_store.py          # ✅ Store/retrieve test chunks
```

### Teste manual do seed:

```bash
python menir/seeds/sample_seed.py
# Saída: 6 pessoas, 3 cidades, 5 livros, 6 tópicos, 12 citações
```

### Teste manual de ingestão:

```bash
python menir_core/graph_ingest.py
# Saída: "Ingestão concluída com 1 chunks."
```

---

## 8. Configuração (.env)

O script `menir_bootnow_codespace.sh` cria automaticamente um `.env` com:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=menir123
MENIR_PROJECT_ID=livro_debora_cap1
```

Todos os scripts Python usam essas variáveis via `os.getenv()`.

---

## 9. Docker Compose (Neo4j)

Arquivo: `docker-compose.yml`

```yaml
services:
  menir-graph:
    image: neo4j:5.15-community
    container_name: menir-graph
    ports:
      - "7474:7474"   # HTTP
      - "7687:7687"   # Bolt
    environment:
      - NEO4J_AUTH=neo4j/menir123
    volumes:
      - menir-neo4j-data:/data
      - menir-neo4j-logs:/logs

volumes:
  menir-neo4j-data:
  menir-neo4j-logs:
```

**Configuração minimalista:**
- Sem APOC plugins (causavam boot loops)
- Sem memory overrides (validação rejeitava)
- Sem healthcheck (simplificado para estabilidade)
- Sem env_file (inline AUTH mais confiável)

**Gerenciar Neo4j:**

```bash
docker compose up -d              # Iniciar
docker compose down               # Parar (preserva volumes)
docker compose down -v            # Parar + apagar dados
docker compose logs -f menir-graph  # Ver logs
```

---

## 10. Workflow típico de desenvolvimento

### Setup inicial:
```bash
./scripts/menir_bootnow_codespace.sh
```

### Explorar dados:
```bash
# Browser Neo4j: http://localhost:7474
# User: neo4j, Password: menir123

# Cypher queries:
MATCH (p:Person)-[:SAID]->(q:Quote)-[:MENTIONS_TOPIC]->(t:Topic)
RETURN p.name, q.text, collect(t.name) AS topics
LIMIT 5
```

### Buscar citações:
```bash
python scripts/quote_vector_search.py "liberdade e escrita" --top-k 3
```

### Ingerir novo documento:
```python
from menir_core.graph_ingest import ingest_markdown_file
n = ingest_markdown_file("docs/meu_artigo.md")
print(f"{n} chunks criados")
```

### Buscar chunks por similaridade (TODO):
```python
# Futura funcionalidade:
from menir_core.chunk_search import search_chunks
results = search_chunks("Como funciona o Menir?", top_k=5)
```

---

## 11. Arquivos principais

```
/workspaces/Menir/
├── docker-compose.yml              # Neo4j container config
├── .env                            # Credenciais (auto-gerado)
├── requirements.txt                # Dependências Python
├── scripts/
│   ├── menir_bootnow_codespace.sh  # ⭐ Script principal de setup
│   └── quote_vector_search.py      # Wrapper CLI para busca
├── menir_core/
│   ├── embeddings.py               # ⭐ Backend de embeddings plugável
│   ├── graph_ingest.py             # ⭐ Ingestão de documentos
│   ├── quote_vector_search.py      # ⭐ Busca vetorial de quotes
│   ├── test_neo4j_connection.py    # Smoke test
│   ├── test_vector_pipeline.py     # Smoke test
│   └── embed_and_store.py          # Smoke test
└── menir/seeds/
    └── sample_seed.py              # ⭐ Seed de dados fictício
```

---

## 12. Próximos passos

- [ ] Implementar `chunk_search.py` para buscar em `Document → Chunk` com vetores
- [ ] Trocar `DummyHashEmbedding` por backend real (OpenAI/Groq/local)
- [ ] Adicionar filtros por `Project`, `Topic` na busca vetorial
- [ ] Implementar cache de embeddings no Neo4j para evitar recomputação
- [ ] Criar CLI unificado `menir query "texto"` que busca em quotes + chunks
- [ ] Adicionar suporte a metadados customizados nos chunks (autor, data, tags)

---

## 13. Troubleshooting

### Neo4j não inicia:
```bash
docker compose logs menir-graph  # Ver erros
docker compose down -v           # Reset completo
docker compose up -d             # Tentar novamente
```

### ImportError ao rodar scripts:
```bash
source .venv/bin/activate         # Ativar ambiente virtual
pip install -r requirements.txt   # Reinstalar dependências
```

### Busca retorna 0 resultados:
```bash
python menir/seeds/sample_seed.py  # Re-executar seed
# Verificar no Neo4j Browser: MATCH (q:Quote) RETURN count(q)
```

### Embeddings inconsistentes:
O `DummyHashEmbedding` é determinístico mas muda se trocar o texto.
Para embeddings estáveis, use backend real (OpenAI, etc.).

---

## 14. Referências

- **Neo4j Python Driver**: https://neo4j.com/docs/api/python-driver/current/
- **Neo4j Docker**: https://neo4j.com/docs/operations-manual/current/docker/
- **Vector Embeddings**: Conceitos de similaridade de cosseno e busca semântica

---

**Menir v10.4.1** – Sistema de memória pessoal com grafos e vetores.  
Desenvolvido por Luiz para Débora e comunidade Menir.
