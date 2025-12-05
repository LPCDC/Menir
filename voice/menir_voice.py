#!/usr/bin/env python3
"""
Menir v10.3 Voice Interface

Integrates STT + MCP context + GPT + TTS for conversational Menir.

Usage:
    python3 menir_voice.py --project SaintCharles_CM2025
    python3 menir_voice.py --mode continuous
    python3 menir_voice.py --wake-word "hey menir"
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

# Setup paths
VOICE_DIR = Path(__file__).parent
PROJECT_ROOT = VOICE_DIR.parent

sys.path.insert(0, str(PROJECT_ROOT))

from ask_menir import MCPClient, GPTClient, build_enriched_prompt

console = Console()
app = typer.Typer(name="menir-voice", help="Voice interface for Menir")


class VoiceProcessor:
    """Placeholder for voice processing logic."""
    
    def __init__(self, config_path: str = str(VOICE_DIR / "config.yaml")):
        self.config_path = config_path
        self.mcp = MCPClient()
        self.gpt = GPTClient()
    
    def listen(self, timeout: int = 10) -> Optional[str]:
        """Capture speech from microphone."""
        console.print("[cyan]🎤 Listening...[/cyan]")
        console.print("[dim](STT engine not yet implemented)[/dim]")
        return None
    
    def transcribe(self, audio_data) -> str:
        """Convert audio to text."""
        console.print("[cyan]📝 Transcribing...[/cyan]")
        return "(transcription placeholder)"
    
    def speak(self, text: str) -> None:
        """Convert text to speech and play."""
        console.print(f"[cyan]🔊 Speaking:[/cyan] {text}")
        console.print("[dim](TTS engine not yet implemented)[/dim]")
    
    def process_conversation(self, user_input: str, project_id: str) -> str:
        """Full conversation: listen → transcribe → query → respond → speak."""
        # Get context
        try:
            context = self.mcp.get_context(project_id, limit=20)
            summary = self.mcp.get_project_summary(project_id)
        except Exception as e:
            console.print(f"[red]MCP Error: {e}[/red]")
            context = ""
            summary = {}
        
        # Build prompt
        prompt = build_enriched_prompt(
            user_input,
            project_id,
            context,
            summary
        )
        
        # Get GPT response
        try:
            response = self.gpt.ask(prompt)
        except Exception as e:
            response = f"Error: {str(e)}"
        
        return response


@app.command()
def listen(
    project: str = typer.Option("itau_15220012", "--project", "-p"),
    continuous: bool = typer.Option(False, "--continuous", "-c"),
):
    """Listen for voice input and respond."""
    processor = VoiceProcessor()
    
    console.print(f"[cyan]🎙️  Voice Interface for project:[/cyan] [bold]{project}[/bold]")
    console.print("[dim]Note: Voice engines (STT/TTS) require additional setup[/dim]\n")
    
    try:
        while True:
            # Listen for speech
            audio = processor.listen(timeout=10)
            if not audio:
                if not continuous:
                    break
                continue
            
            # Transcribe
            text = processor.transcribe(audio)
            console.print(f"[green]📖 You:[/green] {text}\n")
            
            # Process
            response = processor.process_conversation(text, project)
            console.print(f"[cyan]🧠 Menir:[/cyan] {response}\n")
            
            # Speak
            processor.speak(response)
            
            if not continuous:
                break
    
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Interrupted[/yellow]")


@app.command()
def demo(
    project: str = typer.Option("itau_15220012", "--project", "-p"),
):
    """Demo mode: read text input and respond (no audio)."""
    processor = VoiceProcessor()
    
    console.print(f"[cyan]🎙️  Voice Demo for project:[/cyan] [bold]{project}[/bold]")
    console.print("[dim]Type questions (Ctrl+C to exit)[/dim]\n")
    
    try:
        while True:
            # Read input
            user_input = console.input("[green]You:[/green] ")
            if not user_input.strip():
                continue
            
            # Process
            response = processor.process_conversation(user_input, project)
            console.print(f"[cyan]🧠 Menir:[/cyan] {response}\n")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Interrupted[/yellow]")


@app.command()
def config():
    """Show configuration."""
    config_file = VOICE_DIR / "config.yaml"
    if config_file.exists():
        console.print_file(str(config_file))
    else:
        console.print("[red]Config file not found[/red]")


if __name__ == "__main__":
    app()
