import os
import sys
import subprocess

def main():
    print("====================================")
    print("   MENIR CÓRTEX LAUNCHER (v5.2)     ")
    print("====================================")
    print("1. Iniciar Menir Core")
    print("2. Healthcheck do Sistema")
    print("3. Executar Teste de Stress")
    print("4. Sair")
    
    choice = input("\nEscolha uma opção: ")
    
    if choice == "1":
        print("Iniciando Menir...")
        subprocess.run([sys.executable, "-m", "src.v3.menir_cmd"])
    elif choice == "2":
        subprocess.run([sys.executable, "scripts/healthcheck.py"])
    elif choice == "3":
        subprocess.run([sys.executable, "scripts/stress_monkey.py"])
    else:
        print("Encerrando.")
        sys.exit(0)

if __name__ == "__main__":
    main()
