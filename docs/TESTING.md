# Menir Testing Infrastructure

## Overview

The Menir test suite validates Neo4j connectivity, data persistence, and schema integrity before and after data ingestion. All tests are automated via `pytest` and are environment-configurable.

**Test Suite Location:** `tests/test_neo4j_basics.py`
**Total Tests:** 8 tests across 4 test classes
**Coverage:**
- TestConnection: Connectivity (1 test)
- TestPersistence: Create + persistence (2 tests)  
- TestDataIntegrity: Duplicates, orphans, project existence (3 tests)
- TestSchemaConstraints: Constraint validation (2 tests)

---

## Prerequisites

### 1. Python Environment
```bash
# Configure Python (one-time)
configure_python_environment("/workspaces/Menir")

# Install dependencies
install_python_packages(["neo4j", "pytest"], "/workspaces/Menir")
```

### 2. Neo4j Instance

The tests **require a running Neo4j 5.15+ instance** accessible via Bolt protocol.

#### Option A: Docker Compose (Recommended for CI/CD)
```bash
cd /workspaces/Menir
docker-compose up -d neo4j
```

**Wait for health check:**
```bash
docker-compose ps  # Check STATUS = "healthy"
sleep 10  # Allow Neo4j to stabilize
```

#### Option B: Standalone Docker
```bash
docker run -d \
  --name neo4j-menir \
  -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/menir123 \
  -e NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
  neo4j:5.15-community
```

#### Option C: Local Neo4j (macOS/Linux)
```bash
# Download from https://neo4j.com/download-center/
# Extract and run:
./neo4j-enterprise-5.15.0/bin/neo4j start
# Configure auth via neo4j browser: http://localhost:7474
```

---

## Running Tests

### Quick Start
```bash
cd /workspaces/Menir
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PWD="menir123"
export NEO4J_DB="neo4j"

pytest tests/test_neo4j_basics.py -v
```

### Environment Configuration

Tests use these environment variables (with defaults):

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEO4J_URI` | `bolt://localhost:7687` | Bolt protocol connection |
| `NEO4J_USER` | `neo4j` | Authentication user |
| `NEO4J_PWD` | `menir123` | Authentication password |
| `NEO4J_DB` | `neo4j` | Database name |

### Test Execution Options

**Verbose output (recommended):**
```bash
pytest tests/test_neo4j_basics.py -v
```

**Show print statements:**
```bash
pytest tests/test_neo4j_basics.py -v -s
```

**Run specific test class:**
```bash
pytest tests/test_neo4j_basics.py::TestConnection -v
pytest tests/test_neo4j_basics.py::TestDataIntegrity -v
```

**Run specific test:**
```bash
pytest tests/test_neo4j_basics.py::TestPersistence::test_create_persistence_node -v
```

**Coverage report:**
```bash
pytest tests/test_neo4j_basics.py --cov=tests --cov-report=html
# Open htmlcov/index.html in browser
```

---

## Test Descriptions

### TestConnection (1 test)
**Purpose:** Verify Neo4j connectivity via trivial query

**Test:** `test_connection`
- Creates session, executes `RETURN 1 AS v`
- Verifies response equals 1
- **Failure Cause:** Neo4j unreachable, wrong credentials, network issue

---

### TestPersistence (2 tests)
**Purpose:** Verify data persists across driver reconnections

**Test:** `test_create_persistence_node`
- Creates Document node with timestamp, subject, body, tags
- Immediately reads it back
- Verifies timestamp is set
- **Failure Cause:** Neo4j crash, write permission issue

**Test:** `test_read_persistence_node_after_reconnect`
- Creates Document node in one session
- Closes session/driver
- Opens new driver and session
- Reads node back
- **Failure Cause:** Data not persisted, driver resets state unexpectedly

---

### TestDataIntegrity (3 tests)
**Purpose:** Validate data quality guardrails

**Test:** `test_no_duplicate_email_docs`
- Counts Document nodes with duplicate `message_id` values
- Asserts count = 0
- **Runs After Ingest:** Detects duplicate email ingestion

**Test:** `test_project_nodes_exist`
- Verifies all 6 anchor projects exist
- Returns count of Project nodes
- **Failure Cause:** Bootstrap failed or projects deleted

**Test:** `test_no_orphaned_documents`
- Queries for Document nodes NOT linked to a Project
- Asserts count = 0
- **Runs After Ingest:** Ensures all ingested docs have project link

---

### TestSchemaConstraints (2 tests)
**Purpose:** Verify schema integrity constraints

**Test:** `test_project_id_constraint_exists`
- Checks for UNIQUENESS constraint on Project.id
- **Failure Cause:** Schema not bootstrapped

**Test:** `test_project_id_uniqueness`
- Attempts to create duplicate Project nodes with same ID
- Expects second create to fail with constraint error
- **Failure Cause:** Constraint missing or misconfigured

---

## Expected Results

### Pre-Ingest (Fresh Database)
```
test_connection PASSED
test_create_persistence_node PASSED
test_read_persistence_node_after_reconnect PASSED
test_no_duplicate_email_docs PASSED (0 duplicates)
test_project_nodes_exist PASSED (6 projects)
test_no_orphaned_documents PASSED (0 orphans)
test_project_id_constraint_exists PASSED
test_project_id_uniqueness PASSED

========== 8 passed in 2.34s ==========
```

### Post-Ingest (After Email JSONL Ingestion)
```
test_connection PASSED
test_create_persistence_node PASSED
test_read_persistence_node_after_reconnect PASSED
test_no_duplicate_email_docs PASSED (0 duplicates)  ← Validates no re-ingestion
test_project_nodes_exist PASSED (6 projects)
test_no_orphaned_documents PASSED (0 orphans)        ← All docs linked
test_project_id_constraint_exists PASSED
test_project_id_uniqueness PASSED

========== 8 passed in 2.40s ==========
```

---

## Troubleshooting

### Error: "Connection refused" / "ServiceUnavailable"

**Cause:** Neo4j not running or wrong port
```bash
# Check if Neo4j is running
docker ps | grep neo4j
# or
lsof -i :7687

# Start if stopped
docker-compose up -d neo4j
# Wait 10 seconds
sleep 10
```

### Error: "Couldn't authenticate"

**Cause:** Wrong credentials
```bash
# Verify credentials in docker-compose.yml or Neo4j config
# Default: user=neo4j, password=menir123
export NEO4J_PWD="correct_password"
pytest tests/test_neo4j_basics.py -v
```

### Error: "test_project_nodes_exist FAILED"

**Cause:** Bootstrap not run or projects deleted
```bash
# Re-run bootstrap
python scripts/menir_bootstrap_schema_and_projects.py
```

### Error: "test_no_orphaned_documents FAILED"

**Cause:** Documents ingested without project link
```bash
# Check HAS_DOC relationship in ingestion script
# All Document nodes should have: Document-[:HAS_DOC]->Project
```

---

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Neo4j Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      neo4j:
        image: neo4j:5.15-community
        env:
          NEO4J_AUTH: neo4j/menir123
          NEO4J_ACCEPT_LICENSE_AGREEMENT: "yes"
        options: >-
          --health-cmd "cypher-shell -u neo4j -p menir123 'RETURN 1'"
          --health-interval 5s
          --health-timeout 5s
          --health-retries 10
        ports:
          - 7687:7687

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          python -m pip install neo4j pytest
      
      - name: Run tests
        env:
          NEO4J_URI: bolt://localhost:7687
          NEO4J_USER: neo4j
          NEO4J_PWD: menir123
          NEO4J_DB: neo4j
        run: |
          pytest tests/test_neo4j_basics.py -v
```

---

## Development Workflow

### 1. Pre-Ingest Testing
```bash
# Verify environment is clean and schema ready
pytest tests/test_neo4j_basics.py -v

# Expected: All 8 tests pass, 0 documents
```

### 2. Ingest Data
```bash
# Run normalization tools
python tools/itau_email_to_jsonl.py \
  --input data/itau/email/raw \
  --output data/itau/email/normalized

# Run ingestion
python scripts/menir_ingest_email_itau.py \
  --input data/itau/email/normalized/emails.jsonl \
  --project-id ITAU_15220012
```

### 3. Post-Ingest Testing
```bash
# Verify no duplicates, all docs linked
pytest tests/test_neo4j_basics.py::TestDataIntegrity -v

# Check full health
python menir_healthcheck_full.py
```

---

## Cleanup

### Clear Test Data
```bash
# Remove menir_test_suite tagged nodes (created by test fixture)
cypher-shell -u neo4j -p menir123 \
  'MATCH (n {menir_test_tag: "menir_test_suite"}) DETACH DELETE n'
```

### Reset Database
```bash
# Delete all nodes (caution!)
docker exec neo4j-menir cypher-shell -u neo4j -p menir123 \
  'MATCH (n) DETACH DELETE n'

# Re-bootstrap schema
python scripts/menir_bootstrap_schema_and_projects.py
```

---

## References

- **Test Suite:** `/workspaces/Menir/tests/test_neo4j_basics.py`
- **Bootstrap Script:** `/workspaces/Menir/scripts/menir_bootstrap_schema_and_projects.py`
- **Health Check:** `/workspaces/Menir/menir_healthcheck_full.py`
- **Docker Compose:** `/workspaces/Menir/docker-compose.yml`
- **Neo4j Config:** `/workspaces/Menir/docs/NEO4J_CONFIG.md`
