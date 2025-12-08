# Neo4j Configuration Reference

## Bolt Server Settings

Key Bolt configuration parameters for `neo4j.conf`:

```properties
# Listen address and port for Bolt protocol
server.bolt.listen_address=0.0.0.0:7687

# TLS/Encryption for Bolt
#   DISABLED  - No encryption (unsafe for production)
#   OPTIONAL  - Encryption available but not required
#   REQUIRED  - Encryption mandatory
server.bolt.tls_level=DISABLED

# Bolt connection limits
server.bolt.thread_pool_min_size=10
server.bolt.thread_pool_max_size=400
server.bolt.thread_pool_queue_size=1000
```

## HTTP Server Settings

```properties
# Listen address and port for HTTP/HTTPS
server.http.listen_address=0.0.0.0:7474

# TLS/Encryption for HTTP
server.http.tls_level=DISABLED
```

## Authentication & Authorization

```properties
# Authentication enabled (default: true)
dbms.security.auth_enabled=true

# Default auth file location
dbms.security.auth_store=data/dbms/auth

# Initial password (set on first run)
initial.password=neo4j
```

## Database Location

```properties
# Data directory
server.directories.data=data

# Logs directory
server.directories.logs=logs

# Transaction logs (Write-Ahead Logs)
server.directories.transaction.logs.root=data/transactions
```

## Docker Container Configuration

When running Neo4j in Docker with custom configuration:

```bash
docker run -d \
  --name menir-graph \
  -p 7474:7474 \
  -p 7687:7687 \
  -e NEO4J_server_bolt_listen__address=0.0.0.0:7687 \
  -e NEO4J_server_bolt_tls__level=DISABLED \
  -e NEO4J_AUTH=neo4j/password \
  -v neo4j-data:/data \
  neo4j:5.15-community
```

Environment variables override `neo4j.conf` settings with prefix `NEO4J_` and underscores replacing dots.

Example: `server.bolt.tls_level` → `NEO4J_server_bolt_tls__level` (double underscore for dots)

## Container Status Check

```bash
# List containers
docker ps -a | grep neo4j

# View logs
docker logs menir-graph

# Inspect container
docker inspect menir-graph

# Check ports
netstat -tlnp | grep 7687
```

## Restart Container

```bash
# Start stopped container
docker start menir-graph

# Stop running container
docker stop menir-graph

# Restart container
docker restart menir-graph
```

## Verify Bolt Connectivity

After Neo4j is running:

```bash
export NEO4J_URI="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PWD="<password>"

# Quick check
python3 scripts/neo4j_bolt_check.sh

# Detailed diagnostics
python3 scripts/neo4j_bolt_diagnostic.py

# Full health check
python3 menir_healthcheck_full.py
```
