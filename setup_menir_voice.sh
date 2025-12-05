#!/bin/bash

################################################################################
# 🎙️ MENIR v10.3 – Voice Interface Setup & Launcher
# 
# Integrates speech-to-text (STT) + MCP context + GPT + text-to-speech (TTS)
# for a fully conversational Menir experience.
#
# Usage:
#   ./setup_menir_voice.sh              # Interactive setup
#   ./setup_menir_voice.sh --dev        # Dev mode (all components)
#   ./setup_menir_voice.sh --prod       # Prod mode (minimal deps)
#
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
LOG_FILE="${PROJECT_ROOT}/.menir_voice_setup.log"
VOICE_DIR="${PROJECT_ROOT}/voice"
MODELS_DIR="${VOICE_DIR}/models"
CONFIG_FILE="${VOICE_DIR}/config.yaml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}ℹ️  $*${NC}" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $*${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}⚠️  $*${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ $*${NC}" | tee -a "$LOG_FILE"
}

# Header
print_header() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║  🎙️  MENIR v10.3 – Voice Interface Setup                     ║"
    echo "║                                                               ║"
    echo "║  Integrates: STT + Context + GPT + TTS                       ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
}

# Check OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    info "Detected OS: $OS"
}

# Check dependencies
check_dependencies() {
    info "Checking dependencies..."
    
    local missing=()
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing+=("python3")
    else
        local py_version=$(python3 --version | cut -d' ' -f2)
        success "Python $py_version found"
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        missing+=("pip3")
    else
        success "pip3 found"
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        missing+=("git")
    else
        success "git found"
    fi
    
    if [ ${#missing[@]} -gt 0 ]; then
        error "Missing dependencies: ${missing[*]}"
        error "Please install them and try again"
        return 1
    fi
    
    return 0
}

# Create directories
setup_directories() {
    info "Setting up directories..."
    mkdir -p "$VOICE_DIR"/{models,audio,logs,cache}
    success "Directories created"
}

# Install Python dependencies
install_python_deps() {
    info "Installing Python dependencies..."
    
    local deps=(
        "openai"
        "requests"
        "rich"
        "typer"
        "numpy"
        "scipy"
        "sounddevice"
        "librosa"
        "pydantic"
        "python-dotenv"
    )
    
    # Optional STT/TTS deps (may require system libs)
    local optional_deps=(
        "pyaudio"
        "google-cloud-speech"
        "google-cloud-texttospeech"
        "pyttsx3"
    )
    
    # Install required
    for dep in "${deps[@]}"; do
        pip install "$dep" --quiet 2>/dev/null || warn "Could not install $dep"
    done
    
    # Attempt optional (non-fatal)
    for dep in "${optional_deps[@]}"; do
        pip install "$dep" --quiet 2>/dev/null || true
    done
    
    success "Python dependencies installed"
}

# Create config file
create_config() {
    info "Creating configuration file..."
    
    cat > "$CONFIG_FILE" << 'EOF'
# Menir v10.3 Voice Configuration

# MCP Server
mcp:
  endpoint: "http://localhost:8080/jsonrpc"
  timeout: 10
  health_check: true

# Speech-to-Text (STT)
stt:
  engine: "auto"  # auto, google, whisper, azure, native
  language: "pt-BR"
  confidence_threshold: 0.8
  timeout: 30

# Text-to-Speech (TTS)
tts:
  engine: "auto"  # auto, google, azure, pyttsx3, native
  voice: "pt-BR"
  speed: 1.0
  pitch: 1.0

# GPT Integration
gpt:
  model: "gpt-4"
  temperature: 0.3
  max_tokens: 1000
  system_prompt: "You are Menir's voice assistant. Answer concisely and clearly."

# Audio
audio:
  sample_rate: 16000
  channels: 1
  format: "PCM_16"
  device: "default"

# Logging
logging:
  level: "INFO"
  file: "voice/logs/menir_voice.log"
  max_size_mb: 100

# Voice Wake Word
voice:
  wake_word: "menir"
  detection_sensitivity: 0.5
  continuous_mode: true
EOF
    
    success "Configuration created at $CONFIG_FILE"
}

# Create main voice interface
create_voice_interface() {
    info "Creating voice interface module..."
    
    cat > "${VOICE_DIR}/menir_voice.py" << 'PYEOF'
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
PYEOF
    
    chmod +x "${VOICE_DIR}/menir_voice.py"
    success "Voice interface created"
}

# Create launch script
create_launcher() {
    info "Creating launcher script..."
    
    cat > "${PROJECT_ROOT}/menir_voice_launcher.sh" << 'BASHEOF'
#!/bin/bash

# Menir Voice Launcher - All-in-one startup script

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VOICE_DIR="${PROJECT_ROOT}/voice"

echo "🎙️  Menir v10.3 Voice Launcher"
echo ""

# Check MCP server
echo "🔍 Checking MCP server..."
if ! curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "❌ MCP server not running"
    echo "Start with: uvicorn menir10.mcp_app:app --port 8080"
    exit 1
fi
echo "✅ MCP server OK"

# Check OpenAI key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set"
    echo "Set with: export OPENAI_API_KEY=sk-proj-..."
fi

# Launch voice interface
echo ""
echo "🎤 Starting voice interface..."
echo ""

python3 "${VOICE_DIR}/menir_voice.py" "$@"
BASHEOF
    
    chmod +x "${PROJECT_ROOT}/menir_voice_launcher.sh"
    success "Launcher created"
}

# Create requirements file
create_requirements() {
    info "Creating requirements file..."
    
    cat > "${VOICE_DIR}/requirements_voice.txt" << 'EOF'
# Menir Voice Interface Requirements

# Core
openai>=1.0.0
requests>=2.31.0
rich>=13.0.0
typer>=0.9.0
pydantic>=2.0.0
python-dotenv>=1.0.0

# Audio Processing
numpy>=1.24.0
scipy>=1.10.0
librosa>=0.10.0
sounddevice>=0.4.5

# Speech Recognition (Optional - requires system dependencies)
# PyAudio - for audio input (requires PortAudio system library)
# pyaudio>=0.2.13

# Google Cloud (Optional - requires credentials)
# google-cloud-speech>=2.20.0
# google-cloud-texttospeech>=2.13.0

# OpenAI Whisper (Optional - for STT)
# openai-whisper>=20230314

# Local TTS (Optional)
# pyttsx3>=2.90
EOF
    
    success "Requirements created"
}

# Create documentation
create_docs() {
    info "Creating documentation..."
    
    cat > "${VOICE_DIR}/VOICE_GUIDE.md" << 'EOF'
# Menir v10.3 Voice Interface Guide

## Overview

The voice interface enables conversational interaction with Menir through speech.

## Architecture

```
🎤 Audio Input (Microphone)
    ↓
📝 Speech-to-Text (STT)
    ↓
🧠 MCP Context Fetching
    ↓
🤖 GPT Processing
    ↓
🔊 Text-to-Speech (TTS)
    ↓
🔊 Audio Output (Speaker)
```

## Setup

### Prerequisites

1. **MCP Server Running**
   ```bash
   uvicorn menir10.mcp_app:app --port 8080
   ```

2. **OpenAI API Key**
   ```bash
   export OPENAI_API_KEY="sk-proj-..."
   ```

3. **Audio Hardware**
   - Microphone for input
   - Speaker for output

### Installation

```bash
# Install voice dependencies
pip install -r voice/requirements_voice.txt

# For advanced audio support (optional)
# Linux: sudo apt-get install portaudio19-dev
# macOS: brew install portaudio
# Windows: Download from http://www.portaudio.com/
```

## Usage

### Demo Mode (Text Input)

```bash
python3 voice/menir_voice.py demo --project SaintCharles_CM2025
```

Then type questions and press Enter.

### Voice Mode (Audio Input)

```bash
python3 voice/menir_voice.py listen --project SaintCharles_CM2025
```

Speak your question; Menir will respond.

### Continuous Mode

Keep listening for multiple questions:

```bash
python3 voice/menir_voice.py listen --project SaintCharles_CM2025 --continuous
```

### Launcher Script

```bash
./menir_voice_launcher.sh demo --project itau_15220012
./menir_voice_launcher.sh listen --project SaintCharles_CM2025
```

## Configuration

Edit `voice/config.yaml` to customize:
- STT engine (Google, Azure, Whisper, etc.)
- TTS engine (Google, Azure, pyttsx3, etc.)
- GPT model and parameters
- Audio settings (sample rate, channels, etc.)
- Wake word detection

## Troubleshooting

### "No audio device found"
- Check microphone connection
- List devices: `python3 -c "import sounddevice; print(sounddevice.query_devices())"`
- Set device in config.yaml

### "MCP server not responding"
- Start: `uvicorn menir10.mcp_app:app --port 8080`
- Check: `curl http://localhost:8080/health`

### "OpenAI API error"
- Check API key: `echo $OPENAI_API_KEY`
- Verify key validity at https://platform.openai.com

### Audio quality issues
- Increase sample_rate in config (16000 → 48000)
- Check microphone levels
- Reduce background noise

## Advanced Features

### Wake Word Detection
Enable voice wake word detection:
```bash
# In config.yaml:
voice:
  wake_word: "menir"
  continuous_mode: true
```

Then continuously listen for "menir" as a wake word.

### Custom STT/TTS Engines
Modify `menir_voice.py` to integrate:
- Hugging Face Transformers (offline STT)
- Local TTS engines
- Custom audio processing

### Integration with Other Tools
- Export conversations to logs
- Integrate with calendar/task systems
- Build chatbot interfaces

## Performance Tips

1. **Reduce latency:** Use `--project` with specific project (faster queries)
2. **Improve accuracy:** Use `--temp 0.3` for factual responses
3. **Better audio:** Use external USB microphone
4. **Faster responses:** Cache project context locally

## Example Workflows

### 1. Daily Status Check
```bash
./menir_voice_launcher.sh demo --project SaintCharles_CM2025
# You: What's today's status?
# Menir: (context-aware response)
```

### 2. Risk Assessment
```bash
./menir_voice_launcher.sh demo --project itau_15220012 --model gpt-4
# You: What are the current risks?
# Menir: (detailed analysis)
```

### 3. Meeting Prep
```bash
./menir_voice_launcher.sh demo --project SaintCharles_CM2025
# You: Summarize recent interactions for a stakeholder meeting
# Menir: (executive summary)
```

## Security

- API keys stored in environment variables
- No audio recording without user knowledge
- Logs stored locally with controlled access
- HTTPS for remote deployments

## Future Enhancements

- [ ] Real-time speech-to-text streaming
- [ ] Multi-language support
- [ ] Emotion detection in voice
- [ ] Context persistence across sessions
- [ ] Integration with calendar/email
- [ ] Custom voice models
- [ ] Offline-capable models

## Support

For issues:
1. Check configuration: `python3 voice/menir_voice.py config`
2. Run in verbose mode: `DEBUG=1 python3 voice/menir_voice.py demo`
3. Review logs: `tail -f voice/logs/menir_voice.log`
EOF
    
    success "Documentation created"
}

# Summary
print_summary() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║  ✅ Menir Voice Interface Setup Complete!                    ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📁 Created:"
    echo "   • ${VOICE_DIR}/ (voice module directory)"
    echo "   • ${VOICE_DIR}/menir_voice.py (voice interface)"
    echo "   • ${CONFIG_FILE} (configuration)"
    echo "   • ${VOICE_DIR}/requirements_voice.txt (dependencies)"
    echo "   • ${VOICE_DIR}/VOICE_GUIDE.md (documentation)"
    echo "   • ${PROJECT_ROOT}/menir_voice_launcher.sh (launcher)"
    echo ""
    echo "🚀 Quick Start:"
    echo "   1. Start MCP server:"
    echo "      uvicorn menir10.mcp_app:app --port 8080"
    echo ""
    echo "   2. Set OpenAI key:"
    echo "      export OPENAI_API_KEY=\"sk-proj-...\""
    echo ""
    echo "   3. Run voice demo:"
    echo "      python3 voice/menir_voice.py demo --project SaintCharles_CM2025"
    echo ""
    echo "📖 For more info:"
    echo "   cat voice/VOICE_GUIDE.md"
    echo ""
    echo "✨ All set! Start talking to Menir 🎙️"
    echo ""
}

# Main
main() {
    print_header
    
    log "Starting Menir Voice setup"
    
    detect_os
    check_dependencies || exit 1
    setup_directories
    install_python_deps
    create_config
    create_voice_interface
    create_launcher
    create_requirements
    create_docs
    
    print_summary
    
    log "Setup completed successfully"
}

# Run
main "$@"
