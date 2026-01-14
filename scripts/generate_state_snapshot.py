#!/usr/bin/env python3
"""
generate_state_snapshot.py — Generate a timestamped state snapshot of Menir.
Captures current environment, git status, Neo4j health, and deployment state.
"""

import json
import subprocess
import datetime
import os
import sys

def run_command(cmd, shell=False):
    """Execute a command and return output or None if it fails."""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception as e:
        print(f"⚠️ Error running command: {cmd}", file=sys.stderr)
        return None

def get_git_info():
    """Gather git repository information."""
    return {
        "branch": run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"]),
        "last_commit": run_command(["git", "rev-parse", "--short", "HEAD"]),
        "last_commit_message": run_command(["git", "log", "-1", "--pretty=%B"]),
        "working_tree_clean": run_command(["git", "status", "--porcelain"]) == "",
        "remote_url": run_command(["git", "config", "--get", "remote.origin.url"]),
        "tags": run_command(["git", "tag", "-l"], shell=True)
    }

def get_python_info():
    """Gather Python environment information."""
    return {
        "version": run_command(["python3", "--version"]),
        "executable": run_command(["python3", "-c", "import sys; print(sys.executable)"]),
        "venv_active": "VIRTUAL_ENV" in os.environ,
        "venv_path": os.environ.get("VIRTUAL_ENV", "not set")
    }

def get_neo4j_info():
    """Gather Neo4j status information."""
    neo4j_info = {
        "uri": os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
        "docker_status": run_command(["docker", "ps", "--filter", "name=menir-graph", "--format", "{{.State}}"], shell=True),
    }
    
    # Try to run sanity check in silent mode
    sanity_result = run_command(["python3", "scripts/sanity_neo4j_full.py"], shell=True)
    neo4j_info["sanity_check_passed"] = sanity_result is not None
    
    return neo4j_info

def get_requirements_info():
    """Get information about installed requirements."""
    try:
        result = subprocess.run(
            ["pip", "list", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            packages = json.loads(result.stdout)
            return {
                "total_packages": len(packages),
                "key_packages": {pkg["name"]: pkg["version"] for pkg in packages if pkg["name"] in [
                    "neo4j", "numpy", "pytest", "fastapi", "pydantic", "python-dotenv"
                ]}
            }
    except Exception as e:
        print(f"⚠️ Error getting requirements: {e}", file=sys.stderr)
    
    return {"total_packages": "unknown", "key_packages": {}}

def generate_snapshot():
    """Generate comprehensive state snapshot."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    
    snapshot = {
        "menir_version": "v10.4.1",
        "timestamp": timestamp,
        "snapshot_type": "automatic",
        "git": get_git_info(),
        "python": get_python_info(),
        "neo4j": get_neo4j_info(),
        "dependencies": get_requirements_info(),
        "environment": {
            "cwd": os.getcwd(),
            "platform": run_command(["uname", "-a"]),
            "user": os.environ.get("USER", "unknown"),
            "shell": os.environ.get("SHELL", "unknown")
        }
    }
    
    # Generate timestamped filename
    timestamp_compact = timestamp.replace(":", "").replace("-", "").replace("Z", "")
    fname = f"menir_state_snapshot_{timestamp_compact}.json"
    
    # Write snapshot to file
    with open(fname, "w") as f:
        json.dump(snapshot, f, indent=2)
    
    print(f"✅ Snapshot gerado: {fname}")
    return fname, snapshot

if __name__ == "__main__":
    try:
        fname, snapshot = generate_snapshot()
        print(f"📋 Estado capturado em {snapshot['timestamp']}")
        print(f"🔍 Detalhes:")
        print(f"   - Branch: {snapshot['git'].get('branch', 'unknown')}")
        print(f"   - Commit: {snapshot['git'].get('last_commit', 'unknown')}")
        print(f"   - Neo4j: {'✅ Operacional' if snapshot['neo4j'].get('sanity_check_passed') else '⚠️ Offline'}")
        print(f"   - Packages: {snapshot['dependencies'].get('total_packages', 'unknown')}")
    except Exception as e:
        print(f"❌ Erro ao gerar snapshot: {e}", file=sys.stderr)
        sys.exit(1)
