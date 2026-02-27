import os
import sys
import subprocess
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_docker():
    """Verifica e liga o container se necessário."""
    console.print("[dim]..: Verificando Motor Neo4j (Docker)...[/dim]")
    try:
        # Tenta iniciar (se ja estiver rodando, nao da erro)
        subprocess.run(["docker", "start", "menir-db"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        console.print("[bold red]ERRO CRÍTICO:[/bold red] Docker não encontrado no PATH.")
        return False

def show_ontology():
    """Mostra a Hierarquia Visual (First Boot Feel)."""
    tree = Text()
    tree.append("\nESTRUTURA ONTOLÓGICA DETECTADA:\n", style="bold blue")
    tree.append("Luiz (Root)\n", style="white")
    tree.append(" └── Projetos (Menir / MAU)\n", style="cyan")
    tree.append("      └── Narrativas (Débora)\n", style="cyan")
    tree.append("           └── História\n", style="dim")
    tree.append("                └── Caroline (Protagonista)", style="yellow")
    
    console.print(Panel(tree, title="SYSTEM CALIBRATION", border_style="blue"))
    time.sleep(1.5) # Pausa dramática para leitura

def run_main_system():
    """Lança o HUD principal."""
    check_docker()
    
    # Checagem de First Boot (Se token nao existe)
    token_path = os.path.join("user_data", "token.json")
    if not os.path.exists(token_path):
        console.print("[bold yellow]! FIRST BOOT DETECTADO ![/bold yellow]")
        console.print("O Polvo precisa de permissão. O navegador abrirá em breve...")
        time.sleep(2)
    
    show_ontology()
    
    console.print("[bold green]>> ACESSANDO MENIR HUD...[/bold green]")
    time.sleep(1)
    # Roda o main.py substituindo o processo atual
    os.system("python main.py")

def git_sync():
    console.print("[bold cyan]>> INICIANDO PROTOCOLO DE BACKUP (GITHUB)...[/bold cyan]")
    subprocess.run(["git", "add", "."])
    msg = Prompt.ask("[bold]Nome do Save Point (Commit)[/bold]", default="Auto-Sync Menir State")
    subprocess.run(["git", "commit", "-m", msg])
    subprocess.run(["git", "push"])
    console.print("[bold green]>> DADOS SINCRONIZADOS COM A NUVEM.[/bold green]")
    Prompt.ask("Pressione Enter para voltar...")

def reboot_engine():
    console.print("[bold red]>> REINICIANDO MOTOR DE DADOS (DOCKER)...[/bold red]")
    subprocess.run(["docker", "restart", "menir-db"])
    console.print("[bold green]>> MOTOR REINICIADO.[/bold green]")
    time.sleep(1)

def main_menu():
    clear_screen()
    console.print(Panel("[bold white]MENIR OS v7.0[/bold white]\n[dim]Aguardando Sinal de Entrada...[/dim]", style="on black"))
    
    while True:
        cmd = Prompt.ask("[bold blue]>[/bold blue]").strip().lower()

        # DICIONÁRIO DE SINÔNIMOS (A Mágica do NLP Simples)
        if cmd in ["bootow", "ola", "olá", "bom dia", "start", "vai", "menir", "1"]:
            run_main_system()
            break # Sai do loop pq o main.py assume
            
        elif cmd in ["sync", "save", "backup", "sinc", "git", "salvar", "4"]:
            git_sync()
            clear_screen()
            console.print(Panel("[bold white]MENIR OS v7.0[/bold white]\n[dim]Aguardando Sinal de Entrada...[/dim]", style="on black"))

        elif cmd in ["reboot", "reiniciar", "travou", "fix", "docker", "3"]:
            reboot_engine()
            
        elif cmd in ["inbox", "pasta", "arquivos", "drop", "2"]:
            if not os.path.exists("Menir_Inbox"): os.mkdir("Menir_Inbox")
            os.startfile("Menir_Inbox")
            console.print("[dim]Pasta aberta.[/dim]")

        elif cmd in ["exit", "sair", "0"]:
            console.print("[red]Encerrando conexão.[/red]")
            sys.exit()
            
        elif cmd in ["ajuda", "help", "?"]:
            console.print("[yellow]Comandos Válidos:[/yellow] bootow, sync, reboot, inbox, sair")
            
        else:
            console.print("[dim]Sinal não reconhecido. Tente 'bootow' ou 'ajuda'.[/dim]")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        sys.exit()
