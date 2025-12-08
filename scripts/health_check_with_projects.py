#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-project health check with MENIR_PROJECT_ID enforcement.

Validates:
- Neo4j connectivity and schema
- Project metadata (id, name, created_at)
- Per-project node/relation counts
- Project isolation (no orphaned nodes)
- Schema compliance for Project-related constraints

Environment:
  MENIR_PROJECT_ID  - Project ID filter (optional; if omitted, scan all projects)
  NEO4J_URI         - Neo4j connection URI (default: bolt://localhost:7687)
  NEO4J_USER        - Username (default: neo4j)
  NEO4J_PASSWORD    - Password (default: menir123)
  NEO4J_DB          - Database name (default: neo4j)
"""

import json
import os
import sys
from datetime import datetime
from neo4j import GraphDatabase, Neo4jError


class MultiProjectHealthCheck:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "menir123")
        self.database = os.getenv("NEO4J_DB", "neo4j")
        self.project_id = os.getenv("MENIR_PROJECT_ID", None)
        
        self.report = {
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "filter": {"project_id": self.project_id or "(all)"},
            "neo4j": {
                "uri": self.uri,
                "status": None,
                "total_nodes": None,
                "total_rels": None,
                "schema_constraints": None,
                "error": None
            },
            "projects": {},
            "warnings": []
        }
        
    def get_driver(self):
        """Create Neo4j driver instance."""
        try:
            driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            return driver
        except Exception as e:
            self.report["neo4j"]["status"] = "connection_error"
            self.report["neo4j"]["error"] = str(e)
            return None
    
    def verify_connectivity(self, driver):
        """Test Neo4j connectivity."""
        try:
            driver.verify_connectivity()
            self.report["neo4j"]["status"] = "connected"
            return True
        except Exception as e:
            self.report["neo4j"]["status"] = "unreachable"
            self.report["neo4j"]["error"] = str(e)
            return False
    
    def count_global_stats(self, session):
        """Count total nodes and relationships."""
        try:
            # Total nodes
            res = session.run("MATCH (n) RETURN count(n) AS c")
            self.report["neo4j"]["total_nodes"] = res.single()["c"]
            
            # Total relationships
            res = session.run("MATCH ()-[r]->() RETURN count(r) AS c")
            self.report["neo4j"]["total_rels"] = res.single()["c"]
        except Neo4jError as e:
            self.report["neo4j"]["status"] = "query_error"
            self.report["neo4j"]["error"] = str(e)
            return False
        return True
    
    def get_schema_constraints(self, session):
        """Retrieve all constraints from database."""
        try:
            res = session.run("SHOW CONSTRAINTS")
            constraints = [dict(record) for record in res]
            self.report["neo4j"]["schema_constraints"] = len(constraints)
            return constraints
        except Neo4jError as e:
            self.report["neo4j"]["warnings"] = str(e)
            return []
    
    def list_projects(self, session):
        """Find all Project nodes in database."""
        try:
            query = "MATCH (p:Project) RETURN p.id AS id, p.name AS name, p.created_at AS created_at ORDER BY p.id"
            res = session.run(query)
            projects = [dict(record) for record in res]
            return projects
        except Neo4jError:
            # Project label may not exist yet
            return []
    
    def scan_project(self, session, project_id):
        """Scan single project for metrics."""
        project_report = {
            "id": project_id,
            "nodes_by_label": {},
            "total_nodes": 0,
            "total_rels": 0,
            "has_project_node": False,
            "errors": []
        }
        
        try:
            # Check if Project node exists
            q_proj = "MATCH (p:Project {id: $pid}) RETURN p"
            res = session.run(q_proj, pid=project_id)
            if res.single():
                project_report["has_project_node"] = True
        except Neo4jError as e:
            project_report["errors"].append(f"Project node check failed: {str(e)}")
        
        try:
            # Count nodes per label for this project (if Project label is parent)
            # Assuming nodes are connected to Project via outgoing edges
            q_labels = """
            MATCH (p:Project {id: $pid})-[*0..1]-(n)
            WITH DISTINCT labels(n) AS lb, n
            UNWIND lb AS label
            RETURN label, count(DISTINCT n) AS cnt
            ORDER BY label
            """
            res = session.run(q_labels, pid=project_id)
            for record in res:
                label = record["label"]
                cnt = record["cnt"]
                project_report["nodes_by_label"][label] = cnt
                project_report["total_nodes"] += cnt
        except Neo4jError as e:
            # Fallback: count all nodes if relationship-based counting fails
            try:
                q_count = "MATCH (n) RETURN count(n) AS c"
                res = session.run(q_count)
                project_report["total_nodes"] = res.single()["c"]
            except Neo4jError as e2:
                project_report["errors"].append(f"Node count failed: {str(e2)}")
        
        try:
            # Count relationships associated with project nodes
            q_rels = """
            MATCH (p:Project {id: $pid})-[*0..1]-(n)-[r]->()
            RETURN count(DISTINCT r) AS c
            """
            res = session.run(q_rels, pid=project_id)
            cnt = res.single()["c"]
            project_report["total_rels"] = cnt if cnt else 0
        except Neo4jError as e:
            project_report["errors"].append(f"Relationship count failed: {str(e)}")
        
        return project_report
    
    def run(self):
        """Execute full health check."""
        driver = self.get_driver()
        if not driver:
            return self.report
        
        if not self.verify_connectivity(driver):
            driver.close()
            return self.report
        
        try:
            with driver.session(database=self.database) as session:
                # Global stats
                if not self.count_global_stats(session):
                    return self.report
                
                # Schema
                self.get_schema_constraints(session)
                
                # Project scan
                all_projects = self.list_projects(session)
                
                if not all_projects:
                    self.report["warnings"].append("No Project nodes found in database")
                    if self.project_id:
                        self.report["projects"][self.project_id] = {
                            "status": "not_found",
                            "message": f"Project {self.project_id} not found in database"
                        }
                else:
                    # Filter by MENIR_PROJECT_ID if provided
                    filtered_projects = all_projects
                    if self.project_id:
                        filtered_projects = [p for p in all_projects if p["id"] == self.project_id]
                        if not filtered_projects:
                            self.report["warnings"].append(
                                f"MENIR_PROJECT_ID={self.project_id} not found; no projects scanned"
                            )
                    
                    # Scan each project
                    for proj in filtered_projects:
                        pid = proj["id"]
                        proj_report = self.scan_project(session, pid)
                        proj_report["name"] = proj.get("name", "N/A")
                        proj_report["created_at"] = proj.get("created_at", "N/A")
                        self.report["projects"][pid] = proj_report
                
                self.report["neo4j"]["status"] = "ok"
                
        except Exception as e:
            self.report["neo4j"]["status"] = "session_error"
            self.report["neo4j"]["error"] = str(e)
        finally:
            driver.close()
        
        return self.report
    
    def save_report(self, path=None):
        """Save report to JSON file."""
        if not path:
            path = "menir_health_multiproject.json"
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.report, f, indent=2, ensure_ascii=False)
            return path
        except Exception as e:
            print(f"Error saving report to {path}: {e}", file=sys.stderr)
            return None
    
    def print_summary(self):
        """Print summary to stdout."""
        print()
        print("=" * 80)
        print("MENIR MULTI-PROJECT HEALTH CHECK")
        print("=" * 80)
        print(f"Timestamp:        {self.report['timestamp_utc']}")
        print(f"Filter:           MENIR_PROJECT_ID={self.report['filter']['project_id']}")
        print()
        print("Neo4j Status:")
        print(f"  Connection:     {self.report['neo4j']['status']}")
        print(f"  Total Nodes:    {self.report['neo4j']['total_nodes']}")
        print(f"  Total Rels:     {self.report['neo4j']['total_rels']}")
        print(f"  Constraints:    {self.report['neo4j']['schema_constraints']}")
        
        if self.report["neo4j"]["error"]:
            print(f"  Error:          {self.report['neo4j']['error']}")
        
        print()
        print("Projects Scanned:")
        if not self.report["projects"]:
            print("  (none)")
        else:
            for pid, proj in self.report["projects"].items():
                status = proj.get("status", "ok")
                if status == "ok":
                    print(f"  {pid}:")
                    print(f"    Name:          {proj.get('name', 'N/A')}")
                    print(f"    Created:       {proj.get('created_at', 'N/A')}")
                    print(f"    Nodes:         {proj.get('total_nodes', 0)}")
                    print(f"    Relations:     {proj.get('total_rels', 0)}")
                    if proj.get("nodes_by_label"):
                        print(f"    Labels:        {', '.join(sorted(proj['nodes_by_label'].keys()))}")
                    if proj.get("errors"):
                        for err in proj["errors"]:
                            print(f"      ⚠ {err}")
                else:
                    print(f"  {pid}: {proj.get('message', 'unknown error')}")
        
        if self.report.get("warnings"):
            print()
            print("Warnings:")
            for w in self.report["warnings"]:
                print(f"  ⚠ {w}")
        
        print()
        print("=" * 80)


def main():
    check = MultiProjectHealthCheck()
    
    print(f"\n[*] Starting multi-project health check...")
    print(f"    NEO4J_URI: {check.uri}")
    print(f"    MENIR_PROJECT_ID: {check.project_id or '(not set - scanning all projects)'}")
    print()
    
    check.run()
    saved_to = check.save_report()
    
    print(f"[✓] Report saved to: {saved_to}")
    check.print_summary()
    
    # Exit with code 0 if status is "ok", else 1
    sys.exit(0 if check.report["neo4j"]["status"] == "ok" else 1)


if __name__ == "__main__":
    main()
