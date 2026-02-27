"""
Menir CLI - The Unified Operations Center
Horizon 4 - Elegance Update

This single file replaces dozens of obsolete `.bat`, `.ps1` and `menir_*.py`
scripts that littered the repository. 
Uses `typer` to provide a beautiful, readable command interface.
"""

import typer
import subprocess
import sys
import os
from typing import Optional

app = typer.Typer(
    name="Menir CLI",
    help="The Omni-Ingestor and Cognitive Graph OS.",
    add_completion=False,
)

@app.command()
def start_server(port: int = typer.Option(5000, help="Port to bind the MCP server")):
    """
    Subir o MCP Server local para o Cursor/Claude conectar.
    """
    typer.secho(f"🚀 Booting Menir MCP Server on port {port}...", fg=typer.colors.CYAN, bold=True)
    subprocess.run([sys.executable, "src/mcp_server.py"], check=True)

@app.command()
def watch(dir: str = typer.Option("staging/auto_ingest_drop", help="Diretório alvo")):
    """
    Ligar o Watchdog Daemon para auto-ingestão de DropBox/Google Drive.
    """
    typer.secho(f"👀 Menir Watchdog monitoring: {dir}...", fg=typer.colors.MAGENTA, bold=True)
    subprocess.run([sys.executable, "src/v3/menir_watchdog.py", dir], check=True)

@app.command()
def chat():
    """
    Abrir o terminal conversacional do Córtex (A Persona do Menir).
    """
    subprocess.run([sys.executable, "src/v3/cortex_shell.py"], check=True)

@app.command()
def check():
    """
    Realizar o Healthcheck de Arquitetura (Testes Unitários V3 & Conexão AuraDB).
    """
    typer.secho("🩺 Performing Holisitic System Check...", fg=typer.colors.YELLOW, bold=True)
    
    # Run the Horizon 3 tests securely
    try:
        typer.secho("\n--- Step 1: Logic Engine QA ---", fg=typer.colors.CYAN)
        subprocess.run([sys.executable, "-m", "pytest", "tests/test_v3_engines.py", "-v"], check=True)
        typer.secho("✅ Engines Validated.", fg=typer.colors.GREEN)
        
        typer.secho("\n--- Step 2: Bridge Connectivity ---", fg=typer.colors.CYAN)
        from src.v3.menir_bridge import MenirBridge
        bridge = MenirBridge()
        from neo4j.exceptions import ServiceUnavailable, AuthError
        bridge.driver.verify_connectivity()
        typer.secho("✅ Neo4j Connection Established.", fg=typer.colors.GREEN)
        
    except subprocess.CalledProcessError:
        typer.secho("❌ Logic Engine QA Failed. See trace above.", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"❌ Bridge Connectivity Failed: {e}", fg=typer.colors.RED)

if __name__ == "__main__":
    if not os.path.exists("src/v3"):
        typer.secho("CRITICAL: Root structure invalid. Execute this script from the project root.", fg=typer.colors.RED)
        sys.exit(1)
        
    app()
