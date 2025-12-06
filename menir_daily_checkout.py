#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Menir — Daily Check-Out Ritual / Save-State Script

Executa: pull, health-check, status, commit, push, tag (opcional)
Ideal para encerrar o dia / sessão no Codespace com segurança
"""

import subprocess
import sys
import json
from datetime import datetime

TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
DATESTR = datetime.now().strftime("%Y%m%d")
CHECKPOINT_TAG = f"checkpoint-{DATESTR}"


def run_cmd(cmd, description="", check=True):
    """Run shell command and return result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=check)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def display_header():
    """Display session header."""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║           Menir Daily Check-Out Ritual                         ║")
    print(f"║           {TIMESTAMP:48} ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()


def step_pull():
    """Step 1: Pull latest changes."""
    print("[1/6] Pulling latest changes from main...")
    code, out, err = run_cmd("git pull origin main")
    if code == 0:
        print("✅ Pull completed")
    else:
        print(f"⚠️  Pull result: {out.strip() or err.strip()}")
    print()


def step_health_check():
    """Step 2: Run health check."""
    print("[2/6] Running full health check...")
    code, out, err = run_cmd("python3 scripts/health_check_full.py")
    print(out)
    if code != 0:
        print(f"⚠️  Health check warning: {err}")
    print()


def step_display_report():
    """Step 3: Display report."""
    print("[3/6] Health check report (first 15 lines):")
    print("---")
    code, out, err = run_cmd("head -15 menir_full_check_report.json")
    print(out)
    print("...")
    print()


def step_git_status():
    """Step 4: Display git status."""
    print("[4/6] Current git status:")
    code, out, err = run_cmd("git status --short")
    if out.strip():
        print(out)
    else:
        print("ℹ️  Working tree clean")
    print()


def step_commit_push():
    """Step 5: Commit and push."""
    print("[5/6] Committing and pushing...")
    code, out, err = run_cmd("git diff --cached --quiet", check=False)
    
    code, out, err = run_cmd("git add .")
    
    # Check if there are changes to commit
    code, out, err = run_cmd("git diff --cached --quiet", check=False)
    if code == 1:  # Changes exist
        commit_msg = f"chore: daily save-state – health check {datetime.now().strftime('%Y-%m-%d')}"
        code, out, err = run_cmd(f'git commit -m "{commit_msg}"')
        if code == 0:
            print("✅ Committed")
            code, out, err = run_cmd("git push origin main")
            print("✅ Pushed to main")
        else:
            print(f"❌ Commit failed: {err}")
    else:
        print("ℹ️  No changes to commit (working tree clean)")
    print()


def step_optional_tag():
    """Step 6: Optional checkpoint tag."""
    print("[6/6] Optional: Create checkpoint tag?")
    print(f"  Command: git tag -a '{CHECKPOINT_TAG}' -m 'Checkpoint {TIMESTAMP}'")
    print()
    
    try:
        user_input = input("  Create checkpoint tag now? (y/N): ").strip().lower()
        if user_input in ['y', 'yes']:
            code, out, err = run_cmd(
                f'git tag -a "{CHECKPOINT_TAG}" -m "Checkpoint {TIMESTAMP}"'
            )
            if code == 0:
                run_cmd(f"git push origin {CHECKPOINT_TAG}")
                print(f"✅ Tag '{CHECKPOINT_TAG}' created and pushed")
            else:
                print(f"⚠️  Tag creation: {err}")
        else:
            print("ℹ️  Skipped checkpoint tag")
    except (EOFError, KeyboardInterrupt):
        print("ℹ️  Skipped checkpoint tag")
    print()


def display_footer():
    """Display completion message."""
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║                   ✅ Check-Out Complete                        ║")
    print("║                                                                ║")
    print("║  Repository is clean and synced. Safe to close Codespace.    ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print()


def main():
    """Run complete check-out ritual."""
    display_header()
    
    step_pull()
    step_health_check()
    step_display_report()
    step_git_status()
    step_commit_push()
    step_optional_tag()
    
    display_footer()
    sys.exit(0)


if __name__ == "__main__":
    main()
