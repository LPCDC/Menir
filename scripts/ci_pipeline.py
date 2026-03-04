import subprocess
import sys
import datetime

def run_command(command, description):
    print(f"\n=> {description}")
    print(f"Running: {' '.join(command)}")
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
    if result.returncode == 0:
        print(f"   ✅ {description} PASSED.")
        print(result.stdout)
    else:
        print(f"   ❌ {description} FAILED.")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)

def main():
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print("=========================================================")
    print(f"[{current_date}] INITIATING MENIR CI PIPELINE")
    print("=========================================================")

    # 1. Ruff Check
    run_command([sys.executable, "-m", "ruff", "check", "src/v3/", "tests/"], "[1/3] Strict Linter (Ruff)")

    # 2. MyPy Check
    run_command([sys.executable, "-m", "mypy", "-p", "src.v3"], "[2/3] Static Type Checker (MyPy)")

    # 3. PyTest
    run_command([sys.executable, "-m", "pytest", "tests/v3/", "-v"], "[3/3] Test Suite Validation (PyTest)")

    print("\n=========================================================")
    print(f"[{current_date}] CI PIPELINE COMPLETED SUCCESSFULLY (EXIT 0)")
    print("=========================================================")

if __name__ == "__main__":
    main()
