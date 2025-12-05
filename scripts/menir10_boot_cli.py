#!/usr/bin/env python
import os
import sys
import subprocess

def main() -> None:
    project_id = os.getenv("MENIR_PROJECT_ID")
    if not project_id:
        print(
            "ERRO: MENIR_PROJECT_ID não definido.\n"
            "Exemplo:\n"
            "  export MENIR_PROJECT_ID=tivoli\n"
            "  python scripts/menir10_boot_cli.py",
            file=sys.stderr,
        )
        sys.exit(1)

    # Encaminha para o boot_now.py original
    cmd = [sys.executable, "scripts/boot_now.py"]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
