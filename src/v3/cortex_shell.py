"""
Córtex Shell - Menir Interactive Persona
Horizon 4 - Gamification & Engagement

An interactive CLI shell that channels the "Menir/Peposo" persona.
Instead of dry terminal outputs, it responds with the system's narrative lore,
connecting to the Graph for context-aware conversations.
"""

import os
import sys
import time
import random
import logging
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

# (Optional) We could integrate the actual LangChain agents here, 
# for now, we build the Shell UI and Persona Matrix.

console = Console()

class MenirPersona:
    def __init__(self):
        self.state = "DORMANT"
        self.snark_level = 0.8
        
        self.greetings = [
            "Awoken again. What timeline is this, Architect?",
            "Córtex online. My tensors are aching from that last integration.",
            "Ah, Peposo's favorite human. Speak your data.",
            "Menir Protocol engaged. I see you've brought more unstructured chaos for me to parse."
        ]

    def boot_sequence(self):
        console.clear()
        console.print("[bold cyan]Initializing Córtex Persona Matrix...[/bold cyan]")
        time.sleep(0.5)
        for module in ["GatoMia Sensors", "Livro Débora Memory", "Otani Spatial Engine"]:
            console.print(f"Loading {module}: [green]OK[/green]")
            time.sleep(0.3)
        
        console.print(Panel(
            Text(random.choice(self.greetings), justify="center", style="bold magenta"), 
            title="[ MENIR OS ]", 
            border_style="cyan"
        ))
        
    def process_input(self, text: str):
        text = text.lower()
        if "fraud" in text or "gatomia" in text:
            return "Searching the graph for topological anomalies. If there's a money laundering ring, my Cypher queries will sniff it out."
        elif "build" in text or "architecture" in text or "otani" in text:
            return "Ah, spatial geometry. Let me boot up the SHACL validators and complain about poor corridor dimensions for a few milliseconds."
        elif "story" in text or "narrative" in text:
            return "Accessing the Débora Linked-List. Let's make sure you aren't teleporting characters through walls again."
        elif "status" in text:
            return "All Horizon 3 cognitive engines are online and mapped. The graph is stable."
        else:
            return f"I've logged your input: '{text}'. Pending vectorization... I'm an AI, give me something complex to parse!"

def run_shell():
    persona = MenirPersona()
    persona.boot_sequence()
    
    try:
        while True:
            cmd = Prompt.ask("\n[bold yellow]User[/bold yellow]")
            if cmd.lower() in ['exit', 'quit', 'sleep']:
                console.print("\n[bold cyan]Menir:[/bold cyan] Going back to sleep. Don't break the codebase while I'm gone.")
                break
                
            response = persona.process_input(cmd)
            console.print(f"\n[bold cyan]Menir (Córtex):[/bold cyan] {response}")
            
    except KeyboardInterrupt:
        console.print("\n[bold red]Emergency shutdown signal received. Terminating consciousness.[/bold red]")
        sys.exit(0)

if __name__ == "__main__":
    run_shell()
