import os
import time
import datetime
from git import Repo, GitCommandError

def load_env(path=".env.local"):
    env = {}
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()
    return env

def push_with_retry(repo, branch, remote_url, max_attempts=5, base_delay=2):
    try:
        origin = repo.remote("origin")
        origin.set_url(remote_url)
    except ValueError:
        origin = repo.create_remote("origin", remote_url)
    except GitCommandError:
        origin = repo.remote("origin")
        origin.set_url(remote_url)

    try:
        repo.git.checkout(branch)
    except GitCommandError as e:
        raise SystemExit(f"Falha no checkout do branch {branch}: {e}")

    for attempt in range(max_attempts):
        try:
            origin.push(refspec=f"{branch}:{branch}")
            print("Push OK")
            return True
        except GitCommandError as e:
            wait_seconds = base_delay * (2 ** attempt)
            print(f"Tentativa {attempt + 1} falhou: {e}. Aguardando {wait_seconds} s")
            time.sleep(wait_seconds)

    raise SystemExit("Push falhou depois de varias tentativas")

def main():
    env = load_env()
    repo_path = env["REPO_PATH"]
    branch = env["BRANCH_NAME"]
    remote_url = env["REMOTE_URL"]
    prefix = env.get("COMMIT_PREFIX", "[auto]")

    repo = Repo(repo_path)
    repo.git.add(all=True)

    timestamp = datetime.datetime.now().isoformat(timespec="seconds")
    if repo.is_dirty(index=True, working_tree=True, untracked_files=True):
        msg = f"{prefix} snapshot {timestamp}"
        repo.index.commit(msg)
        print(f"Commit criado: {msg}")
    else:
        print("Nenhuma mudanca para commit")

    push_with_retry(repo, branch, remote_url)

if __name__ == "__main__":
    main()
