#!/usr/bin/env python3
import argparse
import sys
import os
import subprocess
import json
import logging
from pathlib import Path
import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("menir_cli")

BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"

def run_script(script_name, args=None, cwd=BASE_DIR, env=None):
    """Run a python script from the scripts directory."""
    script_path = SCRIPTS_DIR / script_name
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    current_env = os.environ.copy()
    if env:
        current_env.update(env)
        
    try:
        # We pass stdin/stdout/stderr to allow interaction if needed
        subprocess.check_call(cmd, cwd=cwd, env=current_env)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Script {script_name} failed with exit code {e.returncode}")
        return False
    except OSError as e:
        logger.error(f"Failed to execute {script_name}: {e}")
        return False

def command_start(args):
    """Boot the system and start the MCP server."""
    logger.info("🚀 Starting Menir System...")
    
    # 1. Run Boot Logic (Session creation, Context load)
    # Using existing boot_menir.py logic
    if not run_script("boot_menir.py"):
        logger.error("Boot sequence failed. Aborting.")
        return

    # 2. Start MCP Server in detached/background mode? 
    # Or simplified: if interactive, we might want to keep it running?
    # Spec says "menir start" -> usually implies daemon or long-running.
    # But boot_menir.py is synchronous. mcp_server is long-running.
    
    logger.info("🔌 Launching MCP Server...")
    mcp_path = SCRIPTS_DIR / "mcp_server.py"
    
    # Check if PROD mode variables are set, if not warn
    if os.getenv("MENIR_MODE") == "prod" and not os.getenv("MENIR_MCP_TOKEN"):
        logger.critical("❌ Cannot start in PROD mode without MENIR_MCP_TOKEN. Check .env")
        return

    try:
        # Using interactive start for now so user can see logs
        # Future: --daemon flag
        cmd = [sys.executable, str(mcp_path)]
        subprocess.run(cmd, cwd=BASE_DIR)
    except KeyboardInterrupt:
        logger.info("Stopping MCP Server...")

def command_stop(args):
    """Shutdown the system safely (Backup -> Close Session -> Kill)."""
    logger.info("🛑 Stopping Menir System...")
    
    # 1. Run Backup Routines (Explicitly ensure safety)
    logger.info("💾 Creating Safety Backup...")
    if not run_script("backup_routine.py"):
        logger.warning("⚠️ Backup script reported failure. Proceed carefully.")
        # We don't abort shutdown on backup fail in CLI unless strictly requested,
        # but shutdown_menir.py has its own check.
    
    # 2. Run Shutdown Logic (Interactive Session Closure)
    # shutdown_menir.py is interactive.
    run_script("shutdown_menir.py")
    
    # 3. Kill MCP Server (if running via other means)
    # TODO: Implement PID tracking to kill background server if menir start was daemonized.
    # For now, we assume user Ctrl+C'd the server or we rely on OS to clean up child processes if script exits.

def command_status(args):
    """Show system status (Graph connection, Active Session)."""
    logger.info("📊 Menir System Status")
    
    # Check Active Session
    state_file = BASE_DIR / ".menir_state"
    if state_file.exists():
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
                sid = state.get("current_session_id", "Unknown")
                logger.info(f"🔹 Active Session ID: {sid}")
        except:
            logger.info("🔹 Active Session: Error reading .menir_state")
    else:
        logger.info("🔹 Active Session: None (System Offline)")
        
    # Check Backup Status
    backups = list((BASE_DIR / "backups").glob("menir_backup_*.zip"))
    if backups:
        latest = sorted(backups)[-1]
        logger.info(f"🔹 Latest Backup: {latest.name}")
    else:
        logger.warning("🔹 Backups: None Found!")

def command_health(args):
    """Check health of components (MCP, DB)."""
    logger.info("🩺 System Health Check")
    
    # 1. Check MCP
    try:
        # Default port 5000
        url = "http://127.0.0.1:5000/health"
        resp = requests.get(url, timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            mode = data.get("mode", "UNKNOWN")
            secured = data.get("auth_secured", False)
            icon = "🔒" if secured else "🔓"
            logger.info(f"✅ MCP Server: ONLINE ({mode}) {icon} Secured: {secured}")
        else:
            logger.error(f"❌ MCP Server: Error {resp.status_code}")
    except requests.exceptions.ConnectionError:
        logger.error("❌ MCP Server: OFFLINE (Connection Refused)")
    
    # 2. Check DB (Optional: wrap check_db_auth.py)
    # run_script("check_db_auth.py")

def main():
    parser = argparse.ArgumentParser(description="Menir Unified CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Start
    parser_start = subparsers.add_parser("start", help="Boot system and start services")
    
    # Stop
    parser_stop = subparsers.add_parser("stop", help="Shutdown system and backup")
    
    # Status
    parser_status = subparsers.add_parser("status", help="Show system state")
    
    # Health
    parser_health = subparsers.add_parser("health", help="Check component health")
    
    args = parser.parse_args()
    
    if args.command == "start":
        command_start(args)
    elif args.command == "stop":
        command_stop(args)
    elif args.command == "status":
        command_status(args)
    elif args.command == "health":
        command_health(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
