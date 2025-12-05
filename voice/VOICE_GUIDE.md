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
