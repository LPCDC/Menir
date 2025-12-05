#!/usr/bin/env python3
"""
Menir v10.3 – CLI + GPT Integration Tool

Ask questions about your Menir projects with automatic context injection.
Queries the MCP JSON-RPC proxy to fetch project interactions, metadata, and insights.
Then sends enriched prompt to OpenAI GPT for reasoning and response.

Usage:
    ./ask_menir.py "What's the status of Saint Charles?" -p SaintCharles_CM2025
    ./ask_menir.py "List all risk flags" -p itau_15220012 --model gpt-4
    ./ask_menir.py "Summarize recent interactions" --project itau_15220012 --limit 50

Environment:
    OPENAI_API_KEY: Your OpenAI API key (required)
    MCP_ENDPOINT: MCP server URL (default: http://localhost:8080/jsonrpc)

Requirements:
    - MCP server running (uvicorn menir10.mcp_app:app --port 8080)
    - OpenAI API key configured
"""

import os
import sys
import json
import requests
from typing import Optional
from datetime import datetime, timezone

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.spinner import Spinner
from openai import OpenAI, APIError, APIConnectionError

# Configuration
MCP_ENDPOINT = os.getenv("MCP_ENDPOINT", "http://localhost:8080/jsonrpc")
MCP_TIMEOUT = 10
GPT_DEFAULT_MODEL = "gpt-4"
GPT_DEFAULT_TEMP = 0.3

# Rich console for styled output
console = Console()

# Typer CLI app
app = typer.Typer(
    name="menir-ask",
    help="Ask questions about Menir projects with automatic context injection",
    rich_markup_mode="rich",
)


class MCPClient:
    """JSON-RPC client for Menir MCP proxy."""
    
    def __init__(self, endpoint: str = MCP_ENDPOINT):
        self.endpoint = endpoint
        self.session = requests.Session()
    
    def _request(self, method: str, params: Optional[dict] = None) -> dict:
        """Make JSON-RPC 2.0 request to MCP server."""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1,
        }
        
        try:
            response = self.session.post(
                self.endpoint,
                json=payload,
                timeout=MCP_TIMEOUT,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            result = response.json()
            
            # Check for JSON-RPC error
            if "error" in result:
                raise RuntimeError(f"MCP error: {result['error']['message']}")
            
            return result.get("result", {})
        
        except requests.exceptions.ConnectionError:
            raise RuntimeError(
                f"Cannot connect to MCP server at {self.endpoint}. "
                "Ensure it's running: uvicorn menir10.mcp_app:app --port 8080"
            )
        except requests.exceptions.Timeout:
            raise RuntimeError(f"MCP server timeout (>{MCP_TIMEOUT}s)")
        except Exception as e:
            raise RuntimeError(f"MCP error: {str(e)}")
    
    def get_context(
        self,
        project_id: str,
        limit: int = 20,
        include_markdown: bool = True,
    ) -> str:
        """Fetch project context (interactions + metadata + markdown)."""
        result = self._request(
            "context",
            {
                "project_id": project_id,
                "limit": limit,
                "include_markdown": include_markdown,
            }
        )
        return result.get("markdown_context", "")
    
    def get_project_summary(self, project_id: str) -> dict:
        """Fetch project summary (stats, dates, intent distribution)."""
        return self._request("project_summary", {"project_id": project_id})
    
    def list_projects(self, top_n: Optional[int] = None) -> list:
        """List all projects."""
        params = {}
        if top_n:
            params["top_n"] = top_n
        result = self._request("list_projects", params)
        return result.get("projects", [])
    
    def search_interactions(
        self,
        project_id: Optional[str] = None,
        intent_profile: Optional[str] = None,
        limit: int = 20,
    ) -> list:
        """Search interactions with filters."""
        params = {"limit": limit}
        if project_id:
            params["project_id"] = project_id
        if intent_profile:
            params["intent_profile"] = intent_profile
        result = self._request("search_interactions", params)
        return result.get("results", [])
    
    def health_check(self) -> bool:
        """Check if MCP server is healthy."""
        try:
            self._request("ping")
            return True
        except Exception:
            return False


class GPTClient:
    """OpenAI GPT client with Menir context awareness."""
    
    def __init__(self, model: str = GPT_DEFAULT_MODEL):
        self.model = model
        self.client = OpenAI()  # Uses OPENAI_API_KEY env var
    
    def ask(
        self,
        prompt: str,
        system_prompt: str = "You are Menir's reasoning assistant. "
                             "Answer questions based on the provided project context. "
                             "Be concise, actionable, and cite specific interactions or data.",
        temperature: float = GPT_DEFAULT_TEMP,
    ) -> str:
        """Send prompt to GPT and return response."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content
        except APIConnectionError:
            raise RuntimeError("Cannot connect to OpenAI API. Check your internet connection.")
        except APIError as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")


def build_enriched_prompt(
    user_question: str,
    project_id: str,
    context: str,
    summary: Optional[dict] = None,
) -> str:
    """Build enriched prompt with project context."""
    prompt = f"""
[PROJECT CONTEXT]
Project ID: {project_id}
"""
    
    if summary:
        prompt += f"""
Status: {summary.get("status", "unknown")}
Category: {summary.get("category", "unknown")}
Total Interactions: {summary.get("interaction_count", 0)}
First Interaction: {summary.get("first_interaction", "unknown")}
Last Interaction: {summary.get("last_interaction", "unknown")}
Intent Profile Distribution: {json.dumps(summary.get("intent_profile_distribution", {}), indent=2)}
"""
    
    prompt += f"""
[INTERACTION HISTORY]
{context}

[USER QUESTION]
{user_question}
"""
    return prompt.strip()


@app.command()
def ask(
    question: str = typer.Argument(
        ...,
        help="Question to ask about the project"
    ),
    project: str = typer.Option(
        "itau_15220012",
        "--project",
        "-p",
        help="Project ID to query"
    ),
    limit: int = typer.Option(
        20,
        "--limit",
        "-l",
        help="Max interactions to include in context"
    ),
    model: str = typer.Option(
        GPT_DEFAULT_MODEL,
        "--model",
        "-m",
        help="GPT model to use (gpt-4, gpt-4-turbo, gpt-3.5-turbo, etc)"
    ),
    temperature: float = typer.Option(
        GPT_DEFAULT_TEMP,
        "--temp",
        "-t",
        help="Temperature for GPT (0.0-2.0)"
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Show detailed logs and prompt"
    ),
):
    """Ask a question about a Menir project with automatic context injection."""
    
    # Initialize clients
    mcp = MCPClient()
    gpt = GPTClient(model=model)
    
    # Check MCP server health
    console.print("[cyan]🔍 Checking MCP server...[/cyan]")
    if not mcp.health_check():
        console.print(
            "[red]❌ MCP server is not responding.[/red]\n"
            "[yellow]Start it with:[/yellow]\n"
            "  uvicorn menir10.mcp_app:app --host 0.0.0.0 --port 8080"
        )
        raise typer.Exit(code=1)
    console.print("[green]✅ MCP server is healthy[/green]")
    
    # Fetch project context
    console.print(f"[cyan]📚 Fetching context for project:[/cyan] [bold]{project}[/bold]")
    
    try:
        with console.status("[bold cyan]Loading context..."):
            context = mcp.get_context(project, limit=limit, include_markdown=True)
            summary = mcp.get_project_summary(project)
        
        console.print(
            f"[green]✅ Loaded {summary.get('interaction_count', 0)} interactions[/green]"
        )
    
    except RuntimeError as e:
        console.print(f"[red]❌ Error fetching context: {e}[/red]")
        raise typer.Exit(code=1)
    
    # Build enriched prompt
    enriched_prompt = build_enriched_prompt(
        question,
        project,
        context,
        summary,
    )
    
    if verbose:
        console.print("\n[dim]── ENRICHED PROMPT ──[/dim]")
        syntax = Syntax(enriched_prompt, "markdown", theme="monokai", line_numbers=True)
        console.print(syntax)
        console.print("[dim]── END PROMPT ──[/dim]\n")
    
    # Ask GPT
    console.print(f"[cyan]🤖 Asking {model}...[/cyan]")
    
    try:
        with console.status("[bold cyan]Thinking..."):
            response = gpt.ask(enriched_prompt, temperature=temperature)
    
    except RuntimeError as e:
        console.print(f"[red]❌ GPT error: {e}[/red]")
        raise typer.Exit(code=1)
    
    # Display response
    console.print("\n")
    console.print(
        Panel(
            response,
            title=f"[bold cyan]🧠 Menir Response ({model})[/bold cyan]",
            border_style="cyan",
            expand=False,
        )
    )
    
    # Footer
    console.print(f"\n[dim]Project: {project} | Model: {model} | Interactions: {summary.get('interaction_count', 0)}[/dim]")


@app.command()
def projects(
    top_n: int = typer.Option(
        None,
        "--top",
        "-n",
        help="Show only top N projects by interaction count"
    ),
):
    """List all registered Menir projects."""
    
    mcp = MCPClient()
    
    console.print("[cyan]📋 Fetching projects...[/cyan]")
    
    try:
        with console.status("[bold cyan]Loading..."):
            projects_list = mcp.list_projects(top_n=top_n)
    
    except RuntimeError as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(code=1)
    
    # Display projects
    console.print(f"\n[bold]Projects ({len(projects_list)} total):[/bold]\n")
    
    for i, proj in enumerate(projects_list, 1):
        status = proj.get("status", "unknown")
        status_color = "green" if status == "ativo" else "yellow"
        
        console.print(
            f"  [{i}] [bold cyan]{proj['project_id']}[/bold cyan] "
            f"({proj.get('name', 'N/A')})\n"
            f"      Status: [{status_color}]{status}[/{status_color}] | "
            f"Interactions: [bold]{proj['interaction_count']}[/bold]"
        )


@app.command()
def status(
    project: str = typer.Argument(
        ...,
        help="Project ID to check status"
    ),
):
    """Get detailed status for a project."""
    
    mcp = MCPClient()
    
    console.print(f"[cyan]📊 Fetching status for:[/cyan] [bold]{project}[/bold]")
    
    try:
        with console.status("[bold cyan]Loading..."):
            summary = mcp.get_project_summary(project)
    
    except RuntimeError as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(code=1)
    
    # Display status
    console.print(f"\n[bold cyan]Project Status: {project}[/bold cyan]\n")
    
    status_info = f"""
Name:          {summary.get('name', 'N/A')}
Status:        {summary.get('status', 'unknown')}
Category:      {summary.get('category', 'unknown')}
Interactions:  {summary.get('interaction_count', 0)}
First:         {summary.get('first_interaction', 'N/A')}
Last:          {summary.get('last_interaction', 'N/A')}

Intent Profile Distribution:
"""
    
    for intent, count in summary.get("intent_profile_distribution", {}).items():
        status_info += f"  • {intent}: {count}\n"
    
    console.print(Panel(status_info, border_style="cyan", expand=False))


@app.command()
def search(
    query: str = typer.Argument(
        ...,
        help="Search term"
    ),
    project: str = typer.Option(
        None,
        "--project",
        "-p",
        help="Filter by project ID"
    ),
    intent: str = typer.Option(
        None,
        "--intent",
        "-i",
        help="Filter by intent profile"
    ),
    limit: int = typer.Option(
        10,
        "--limit",
        "-l",
        help="Max results to return"
    ),
):
    """Search interactions across projects."""
    
    mcp = MCPClient()
    
    console.print("[cyan]🔍 Searching interactions...[/cyan]")
    
    try:
        with console.status("[bold cyan]Searching..."):
            results = mcp.search_interactions(
                project_id=project,
                intent_profile=intent,
                limit=limit,
            )
    
    except RuntimeError as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(code=1)
    
    # Filter by query text if provided
    if query:
        results = [
            r for r in results
            if query.lower() in json.dumps(r).lower()
        ]
    
    # Display results
    console.print(f"\n[bold]Found {len(results)} interactions:[/bold]\n")
    
    for i, interaction in enumerate(results, 1):
        console.print(
            f"  [{i}] [bold cyan]{interaction.get('project_id', 'unknown')}[/bold cyan] "
            f"({interaction.get('intent_profile', 'unknown')})\n"
            f"      ID: {interaction.get('interaction_id', 'N/A')}\n"
            f"      Created: {interaction.get('created_at', 'N/A')}\n"
            f"      Content: {interaction.get('metadata', {}).get('content', 'N/A')[:80]}...\n"
        )


if __name__ == "__main__":
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Interrupted by user[/yellow]")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print(f"\n[red]❌ Unexpected error: {e}[/red]")
        if os.getenv("DEBUG"):
            import traceback
            traceback.print_exc()
        raise typer.Exit(code=1)
