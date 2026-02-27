#!/usr/bin/env python3
"""
quick_snapshot.py — Lightweight state snapshot generator.
Alternative to generate_state_snapshot.py with minimal dependencies.
"""

import os
import json
import subprocess
import datetime
import sys

def get_git_info():
    """Get git repository information."""
    try:
        branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        ).stdout.strip()
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        ).stdout.strip()
        tags = subprocess.run(
            ["git", "tag", "--points-at", commit],
            capture_output=True,
            text=True,
            timeout=5
        ).stdout.strip().splitlines()
        return {
            "branch": branch,
            "commit": commit,
            "tags": tags if tags else []
        }
    except Exception as e:
        print(f"⚠️ Error getting git info: {e}", file=sys.stderr)
        return {}

def get_venv_info():
    """Get virtual environment information."""
    return {
        "venv": os.getenv("VIRTUAL_ENV", None),
        "python_version": subprocess.run(
            ["python", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        ).stdout.strip()
    }

def get_deps():
    """Get installed dependencies."""
    try:
        from importlib.metadata import distributions
        packages = {d.metadata['Name']: d.version for d in distributions()}
        return packages
    except ImportError:
        try:
            import pkg_resources
            packages = {p.project_name: p.version for p in pkg_resources.working_set}
            return packages
        except ImportError:
            print("⚠️ Could not import package metadata", file=sys.stderr)
            return {}

def get_neo4j_status():
    """Check if Neo4j is running."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=menir-graph", "--format", "{{.State}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "running" if "running" in result.stdout else "not_running"
    except Exception:
        return "unknown"

def generate_snapshot():
    """Generate lightweight state snapshot."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    
    snapshot = {
        "menir_version": "v10.4.1",
        "snapshot_type": "lightweight",
        "timestamp_utc": timestamp,
        "git": get_git_info(),
        "venv": get_venv_info(),
        "neo4j_docker": get_neo4j_status(),
        "dependencies_count": len(get_deps() or {}),
        "environment": {
            "cwd": os.getcwd(),
            "user": os.getenv("USER", "unknown")
        }
    }
    
    # Generate timestamped filename
    fname = f"menir_state_snapshot_{timestamp.replace(':', '').replace('-', '').replace('Z', '')}.json"
    
    # Write snapshot to file
    with open(fname, "w") as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"✅ Snapshot generated: {fname}")
    print(f"📋 Details:")
    print(f"   - Branch: {snapshot['git'].get('branch', 'unknown')}")
    print(f"   - Commit: {snapshot['git'].get('commit', 'unknown')[:8]}")
    print(f"   - Tags: {', '.join(snapshot['git'].get('tags', [])) or 'none'}")
    print(f"   - Neo4j: {snapshot.get('neo4j_docker', 'unknown')}")
    print(f"   - Dependencies: {snapshot.get('dependencies_count', 'unknown')}")
    
    return fname

if __name__ == "__main__":
    try:
        fname = generate_snapshot()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error generating snapshot: {e}", file=sys.stderr)
        sys.exit(1)
