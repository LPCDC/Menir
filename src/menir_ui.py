from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.align import Align
from datetime import datetime
import time

# Tenta importar o módulo do Drive, se falhar, cria mock
try:
    from src.drive_hub import get_drive_status, check_inbox_stats
except ImportError:
    try:
        # Fallback if src is in path directly
        from drive_hub import get_drive_status, check_inbox_stats
    except ImportError:
        def get_drive_status(): return "OFFLINE (No Driver)"
        def check_inbox_stats(): return {"new_files": 0, "status": "Simulated"}

console = Console()

def make_layout():
    """Define o grid do Dashboard."""
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=3),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="chat_area", ratio=2),
        Layout(name="sidebar", ratio=1)
    )
    return layout

def get_header_content():
    """Gera o cabeçalho dinâmico."""
    time_str = datetime.now().strftime("%H:%M")
    # AQUI ESTAVA O ERRO: Usamos Align/Panel em vez de somar Text + Panel
    content = Text(f"MENIR OS v6.0 | VITAL SYSTEM | {time_str}", style="bold white on blue", justify="center")
    return content

def get_sidebar_content():
    """Gera o painel lateral com status do Drive."""
    stats = check_inbox_stats()
    drive_status = get_drive_status()
    
    status_text = Text()
    status_text.append(f"\n📡 Drive Radar: ", style="bold")
    status_text.append(f"{drive_status}\n", style="green" if "ONLINE" in str(drive_status) else "red")
    
    status_text.append(f"📥 Inbox Queue: ", style="bold")
    status_text.append(f"{stats.get('new_files', 0)} files\n", style="cyan")
    
    status_text.append(f"\n👁️ Active Lens:\n", style="bold")
    status_text.append(f"• Strategic (MAU)\n")
    status_text.append(f"• Technical (Menir)\n")
    
    return Panel(status_text, title="SYSTEM CONTEXT", border_style="blue")

def run_shell():
    """Loop principal da UI."""
    layout = make_layout()
    
    # Header estático por enquanto
    layout["header"].update(Panel(get_header_content(), style="blue"))
    
    # Mensagem de boas vindas no chat
    welcome_msg = Text("Console Initialized.\nDrive Connected.\nWaiting for input...", style="green")
    layout["chat_area"].update(Panel(welcome_msg, title="Live Feed"))

    # Inicia o Live Display
    with Live(layout, refresh_per_second=4, screen=True):
        while True:
            # Atualiza Sidebar em tempo real
            layout["sidebar"].update(get_sidebar_content())
            time.sleep(1)

if __name__ == "__main__":
    run_shell()
