# -*- coding: utf-8 -*-
"""
master_script.py
Gera/atualiza os arquivos canônicos do Menir, faz commit, push
e registra auditoria com hash do commit.
Requer GitPython (`pip install GitPython`).
"""

import os
import time
from datetime import datetime, timezone
from pathlib import Path
import json
import git
from git.exc import GitCommandError


# ===================== CONFIG LOCAL =====================


REPO_PATH = Path(r"C:\Users\Pichau\Repos\MenirVital")

BRANCH_NAME = os.environ.get(
    "GITHUB_BRANCH",
    "release/menir-aio-v5.0-boot-local",
)

# URL autenticada direta
REMOTE_URL_BASE = "https://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@github.com/LPCDC/Menir.git"

MENIR_STATE_PATH = REPO_PATH / "menir_state.json"
LGPD_POLICY_PATH = REPO_PATH / "lgpd_policy.md"
OUTPUT_CONTRACTS_PATH = REPO_PATH / "output_contracts.md"
PUSH_RUNBOOK_PATH = REPO_PATH / "push_runbook.md"
ZK_AUDIT_DIR = REPO_PATH / "audit"
ZK_AUDIT_PATH = ZK_AUDIT_DIR / "zk_audit.jsonl"

# garante que o repositório local use a URL autenticada
repo = git.Repo(REPO_PATH)
repo.remote("origin").set_url(REMOTE_URL_BASE)



# ===================== HELPERS =====================

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_branch(repo: git.Repo, branch_name: str) -> None:
    try:
        repo.git.checkout(branch_name)
    except GitCommandError:
        repo.git.checkout("-b", branch_name)


def ensure_remote_auth(repo: git.Repo, base_url: str, user: str, pat: str) -> None:
    if pat is None:
        raise RuntimeError("GITHUB_PAT ausente do ambiente")

    # monta a URL autenticada
    # forma: https://USER:TOKEN@github.com/owner/repo.git
    if base_url.startswith("https://"):
        authed_url = base_url.replace(
            "https://",
            f"https://{user}:{pat}@",
            1
        )
    else:
        authed_url = f"https://{user}:{pat}@{base_url}"

    # config remote origin
    if "origin" in [r.name for r in repo.remotes]:
        repo.remotes.origin.set_url(authed_url)
    else:
        repo.create_remote("origin", authed_url)


def write_canonical_files() -> None:
    ZK_AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    menir_state_content = {
        "version": "menir_v5.0",
        "core": {
            "architecture": "hibrido_federado_grafo_vitalicio",
            "neo4j": {
                "uri": os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
                "database": os.environ.get("NEO4J_DATABASE", "neo4j")
            },
            "lgpd_policy_ref": "lgpd_policy.md",
            "zk_audit_log": "audit/zk_audit.jsonl"
        },
        "projects": {
    "banco_itau": { "status": "ativo" },
    "tivoli": { "status": "em_andamento" },
    "ibere": { "status": "pronto_para_assembleia" },
    "otani": { "status": "ativo" }
},
"pending_tasks": {
    "red": [],
    "yellow": [],
    "green": []
},

        "paths": {
            "repo_local": str(REPO_PATH),
            "env_file": str(REPO_PATH / ".env.local"),
            "branch": BRANCH_NAME
        },
        "legal": {
            "lgpd_mode": os.environ.get("LGPD_POLICY_MODE", "mask_third_parties"),
            "owner_fullname_allowed": True,
            "institutions_fullname_allowed": True,
            "third_party_fullname_allowed": False
        },
        "boot_state": {
            "bootnow_version": "v5.0_all_in_one_core_enabled",
            "timestamp_utc": utc_now_iso()
        }
    }

    # substitua o conteúdo completo conforme sua versão, omitido aqui por brevidade.

    # Cria arquivos
    MENIR_STATE_PATH.write_text(json.dumps(menir_state_content, indent=2, ensure_ascii=False), encoding="utf-8")
    # Cria ou atualiza os demais: lgpd_policy.md, output_contracts.md, push_runbook.md
    # … (conteúdos conforme versão anterior)

    if not ZK_AUDIT_PATH.exists():
        ZK_AUDIT_PATH.write_text("", encoding="utf-8")


def commit_and_push(repo: git.Repo) -> str:
    repo.git.add(str(MENIR_STATE_PATH))
    repo.git.add(str(LGPD_POLICY_PATH))
    repo.git.add(str(OUTPUT_CONTRACTS_PATH))
    repo.git.add(str(PUSH_RUNBOOK_PATH))
    repo.git.add(str(ZK_AUDIT_PATH))

    commit_msg = f"bootstrap canonical contract @ {utc_now_iso()} UTC"
    repo.index.commit(commit_msg)
    last_commit = repo.head.commit.hexsha

    delay = 2
    for attempt in range(3):
        try:
            repo.remotes.origin.push(refspec=f"{BRANCH_NAME}:{BRANCH_NAME}")
            return last_commit
        except GitCommandError:
            if attempt == 2:
                raise
            time.sleep(delay)
            delay *= 2
    return last_commit


def append_audit(commit_hash: str) -> None:
    line = {
        "timestamp_utc": utc_now_iso(),
        "action": "bootstrap canonical contract",
        "result": "OK",
        "commit": commit_hash
    }
    with open(ZK_AUDIT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


def main() -> None:
    repo = git.Repo(REPO_PATH)
    ensure_branch(repo, BRANCH_NAME)
    write_canonical_files()
    commit_hash = commit_and_push(repo)
    append_audit(commit_hash)
    print({"status": "OK", "commit": commit_hash})


if __name__ == "__main__":
    main()
