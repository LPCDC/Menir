#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neo4j Bolt connection diagnostic.

Provides step-by-step diagnostics:
1. Driver creation
2. Connectivity verification
3. Trivial query execution

Usage:
  python3 neo4j_bolt_diagnostic.py
    (uses environment variables)
  
  python3 neo4j_bolt_diagnostic.py \
    --uri bolt://localhost:7687 \
    --user neo4j \
    --password menir123 \
    --db neo4j

Environment Variables (if --uri not provided):
  NEO4J_URI   - Bolt URI (default: bolt://localhost:7687)
  NEO4J_USER  - Username (default: neo4j)
  NEO4J_PWD   - Password (default: empty)
  NEO4J_DB    - Database (default: neo4j)

Exit code:
  0 - all steps successful
  1 - connection or query failed
"""

import os
import sys
import argparse
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError, Neo4jError


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Neo4j Bolt connection diagnostic",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--uri",
        default=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        help="Bolt URI (default: bolt://localhost:7687)"
    )
    
    parser.add_argument(
        "--user",
        default=os.getenv("NEO4J_USER", "neo4j"),
        help="Username (default: neo4j)"
    )
    
    parser.add_argument(
        "--password",
        default=os.getenv("NEO4J_PWD", ""),
        help="Password (default: empty)"
    )
    
    parser.add_argument(
        "--db",
        default=os.getenv("NEO4J_DB", "neo4j"),
        help="Database name (default: neo4j)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    return parser.parse_args()


# Get configuration from args or environment
args = parse_arguments()
URI = args.uri
USER = args.user
PWD = args.password
DB = args.db
VERBOSE = args.verbose


def attempt_connect():
    """Attempt connection with diagnostic output."""
    if VERBOSE:
        print(f"[DEBUG] Conectando a: {URI}")
        print(f"[DEBUG] Username: {USER}")
        print(f"[DEBUG] Database: {DB}")
    
    try:
        driver = GraphDatabase.driver(URI, auth=(USER, PWD))
        if VERBOSE:
            print("[1] Driver criado com sucesso")
        else:
            print("[1] ✓ Driver criado")
        
        driver.verify_connectivity()
        if VERBOSE:
            print("[2] verify_connectivity OK")
        else:
            print("[2] ✓ Conectividade verificada")
            
    except (ServiceUnavailable, AuthError, Neo4jError) as e:
        print(f"[ERROR] Não conseguiu conectar ao Bolt: {type(e).__name__}")
        if VERBOSE:
            print(f"[ERROR] Detalhes: {e}")
        return False

    try:
        with driver.session(database=DB) as s:
            result = s.run("RETURN 1 AS v").single()
            val = result["v"] if result else None
            if VERBOSE:
                print(f"[3] Query trivial executada, retornou: {val}")
            else:
                print("[3] ✓ Query trivial OK")
    except Neo4jError as e:
        print(f"[ERROR] Erro ao executar query trivial: {type(e).__name__}")
        if VERBOSE:
            print(f"[ERROR] Detalhes: {e}")
        return False
    finally:
        driver.close()

    print("✅ Conexão Bolt + transação: OK")
    return True


if __name__ == "__main__":
    ok = attempt_connect()
    sys.exit(0 if ok else 1)
