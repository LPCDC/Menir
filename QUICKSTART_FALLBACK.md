# Quick Start — Fallback Docker ↔ Neo4j Desktop

## 30-segundo TL;DR

```bash
# Setup (one-time)
cp .env.template .env
nano .env  # edit if needed

# Run (automatic fallback)
bash scripts/menir_startup.sh
```

**What happens:**
- Detects Docker availability
- Starts Neo4j (container or local)
- Tests connectivity
- Runs full pipeline (normalize + ingest + health check)

---

## Command Reference

### Test Fallback Implementation
```bash
bash scripts/test_startup_fallback.sh
# Expected: ✅ 10/10 tests pass
```

### Run Pipeline (Auto-detect Docker/Local)
```bash
bash scripts/menir_startup.sh
# Expected: 6 stages complete, health check JSON output
```

### Manual Connectivity Test
```bash
python3 scripts/neo4j_bolt_diagnostic.py \
  --uri bolt://localhost:7687 \
  --user neo4j \
  --password menir123 \
  --db neo4j
# Expected: [1] [2] [3] ✅ all steps pass
```

### Health Check
```bash
python3 menir_healthcheck_full.py | jq
# Expected: JSON with node/relation counts
```

---

## Architecture

```
scripts/menir_startup.sh
├─ Stage 1: Load .env
├─ Stage 2: Detect Docker (DOCKER_MODE=true/false)
├─ Stage 3: Start Neo4j (container or local)
├─ Stage 4: Test Connectivity
├─ Stage 5: Run Pipeline (bootstrap_and_ingest.sh)
│  ├─ Pre-check (health before)
│  ├─ Normalization (email, whatsapp, extratos, docs)
│  ├─ Ingestion (Document/Event nodes)
│  ├─ Reporting (metrics)
│  └─ Post-check (health after)
└─ Stage 6: Final Health Check → menir_health_status.json
```

---

## Scenarios

### Docker Available (Codespaces, CI/CD)
```bash
bash scripts/menir_startup.sh
# → Detects Docker ✓
# → docker-compose up -d neo4j ✓
# → Container Neo4j ✓
# → Pipeline runs ✓
```

### Docker Unavailable (Local Desktop)
```bash
neo4j start  # start manually
bash scripts/menir_startup.sh
# → Detects Docker unavailable ✓
# → Fallback to localhost:7687 ✓
# → Same pipeline runs ✓
```

---

## Files Created/Updated

| File | Type | Purpose |
|------|------|---------|
| `scripts/menir_startup.sh` | ✨ NEW | Main orchestration (6 stages) |
| `scripts/neo4j_bolt_diagnostic.py` | 🔧 ENHANCED | CLI args + verbose logging |
| `scripts/menir_bootstrap_and_ingest.sh` | 📋 COMPLETED | All TODO markers replaced |
| `scripts/test_startup_fallback.sh` | ✅ NEW | 10 integration tests |
| `docker-compose.yml` | 🐳 UPDATED | menir service command |
| `docs/DOCKER_FALLBACK.md` | 📖 NEW | Full documentation (450+ lines) |

---

## Environment Variables

**From `.env` (required):**
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PWD=menir123
NEO4J_DB=neo4j
MENIR_PROJECT_ID=ITAU_15220012
```

**Set by startup script:**
```bash
DOCKER_MODE=true/false
```

---

## Troubleshooting

**"Arquivo .env não encontrado"**
```bash
cp .env.template .env
nano .env  # configure credentials
```

**"Falha na conexão com Neo4j"**
```bash
# Check if Neo4j is running
neo4j status
neo4j start

# Test directly
python3 scripts/neo4j_bolt_diagnostic.py --verbose
```

**"Neo4j container not starting"**
```bash
docker-compose down -v
docker-compose up -d neo4j
sleep 10
bash scripts/menir_startup.sh
```

---

## Expected Output

### Success (Docker Mode)
```
[menir_startup] Docker detectado — modo CONTAINER ativado
[menir_startup] Aguardando Neo4j subir...
[menir_startup] ✓ Neo4j container iniciado
✅ Conexão Bolt + transação: OK
[2] Normalization: Converting raw data...
[3] Ingestion: Loading normalized data...
✅ Menir Itau pipeline completed
```

### Success (Local Mode)
```
[menir_startup] Docker não detectado — modo LOCAL ativado
[menir_startup] Verifique se Neo4j Desktop está rodando...
✅ Conexão Bolt + transação: OK
[2] Normalization: Converting raw data...
[3] Ingestion: Loading normalized data...
✅ Menir Itau pipeline completed
```

---

## Validation

```bash
# Run all 10 tests
bash scripts/test_startup_fallback.sh

# Expected output:
# ✓ TEST 1: Script exists
# ✓ TEST 2: Syntax valid
# ✓ TEST 3: Functions present
# ✓ TEST 4: Docker detection
# ✓ TEST 5: .env handling
# ✓ TEST 6: Diagnostics ready
# ✓ TEST 7: Tools integrated
# ✓ TEST 8: docker-compose updated
# ✓ TEST 9: Directories ready
# ✓ TEST 10: Docs complete
# ✅ 10/10 TESTES PASSANDO
```

---

## Next Steps

1. **Test the implementation:**
   ```bash
   bash scripts/test_startup_fallback.sh  # validate everything
   ```

2. **Run with Docker (if available):**
   ```bash
   bash scripts/menir_startup.sh
   ```

3. **Or run with local Neo4j Desktop:**
   ```bash
   neo4j start
   bash scripts/menir_startup.sh
   ```

4. **Check results:**
   ```bash
   cat menir_health_status.json | jq '.summary'
   ```

---

## Documentation

- **docs/DOCKER_FALLBACK.md** — Full guide (450+ lines)
- **docs/TESTING.md** — Test suite reference
- **docs/IMPLEMENTATION_STATUS.md** — Project status
- **tools/README.md** — Normalization tools
