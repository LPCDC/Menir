# Menir v10.4 — Quick Install & Usage Guide

## What is Menir

Menir is a personal memory-machine:
- logs your interactions, projects, notes, drafts
- builds a contextual graph and a "narrative memory" layer
- lets you query, explore and analyze your creative life

With version 10.4 you get:
- MCP Server (JSON-RPC + FastAPI)
- CLI tools (`ask_menir.py`, `memoetic_cli.py`)
- Memoetic Layer: narrative-pattern extraction, voice and theme analysis
- Voice interface (optional)
- Export tools for Neo4j, versioning via Git

---

## 🌐 Requirements

- Python 3.10+
- pip
- (Optional but strongly recommended) A shell with Bash support

Optional dependencies (for voice, GPT, graph export):
- `ffmpeg`, `portaudio`, `vosk` (for voice)
- `openai` (for GPT integration)
- `neo4j` (for graph export)

---

## 🚀 Quick Start

### 1. Clone or Download the Repo

```bash
git clone https://github.com/LPCDC/Menir.git
cd Menir
git checkout v10.4
```

### 2. Set Up Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure Environment Variables

Create a `.env` file in the repo root:

```bash
MENIR_PROJECT_ID=personal
OPENAI_API_KEY=sk-...  # if you want GPT integration
```

---

## 📝 Usage

### Via CLI — Ask Menir

Interact with Menir using the `ask_menir.py` CLI:

```bash
python ask_menir.py "What are the top projects I'm working on?"
```

This will:
1. Log your question to `logs/menir10_interactions.jsonl`
2. Query the Menir knowledge base
3. Return a contextual answer

### Via CLI — Memoetic Analysis

Analyze narrative patterns and themes in your project history:

```bash
# Show profile summary (term frequencies, sample quotes)
python -m menir10.memoetic_cli --project personal --mode summary

# Show project's "voice" (deterministic narrative description)
python -m menir10.memoetic_cli --project personal --mode voice

# List recurring themes ("memes") with frequency
python -m menir10.memoetic_cli --project personal --mode memes

# Use a custom log file
python -m menir10.memoetic_cli --project itau_15220012 --log-file logs/custom.jsonl --mode voice
```

**Output Examples:**

```
$ python -m menir10.memoetic_cli --project itau_15220012 --mode voice

Project 'itau_15220012' currently has 4 logged interactions. 
Its vocabulary tends to revolve around: itaú, teste, via, troca, mails. 
It is mostly composed of short, direct notes. 
The language shows high lexical variety, suggesting exploratory thinking.
```

### Via MCP Server (Optional)

Start the MCP server on port 8080:

```bash
bash scripts/deploy_menir.sh
```

Once running, you can:
- Make JSON-RPC calls to the server
- Use Claude or other MCP clients to interact with Menir
- Export logs and interact via FastAPI endpoints

---

## 📊 Data Structure

### Interaction Logs

Menir stores interactions as JSONL (one JSON object per line) in `logs/menir10_interactions.jsonl`:

```json
{
  "interaction_id": "uuid-string",
  "project_id": "personal",
  "intent_profile": "note",
  "created_at": "2025-12-05T12:00:00+00:00",
  "updated_at": "2025-12-05T12:00:00+00:00",
  "flags": {},
  "metadata": {
    "stage": "single",
    "status": "ok",
    "content": "Worked on memoetic layer integration"
  }
}
```

### Memoetic Profile

The memoetic layer analyzes logs and extracts:
- **Top Terms**: Frequently occurring words (filtered by stopwords)
- **Voice**: A deterministic description of the project's narrative style
- **Memes**: Recurring linguistic patterns and themes
- **Sample Quotes**: Representative snippets from the log

---

## 🧪 Testing

Run the test suite to verify installation:

```bash
pytest -q
```

Run specific tests:

```bash
pytest tests/test_memoetic.py -v          # Memoetic layer tests
pytest tests/test_menir10_boot.py -v      # Boot sequence tests
```

---

## 🔧 Configuration

### Project ID

Set your default project via environment:

```bash
export MENIR_PROJECT_ID=my_project
```

Or pass it directly to CLI tools:

```bash
python -m menir10.memoetic_cli --project my_project --mode summary
```

### Log File Location

By default, logs are stored in `logs/menir10_interactions.jsonl`.

To use a custom location:

```bash
python -m menir10.memoetic_cli --project personal --log-file /path/to/custom.jsonl --mode voice
```

### OpenAI Integration

To enable GPT-based features:

```bash
export OPENAI_API_KEY="sk-..."
```

Then use `ask_menir.py` or other AI-enabled tools.

---

## 📚 Key Files & Modules

| Path | Purpose |
|------|---------|
| `menir10/memoetic.py` | Core memoetic analysis (term extraction, voice synthesis) |
| `menir10/memoetic_cli.py` | CLI for memoetic analysis |
| `ask_menir.py` | Main CLI for asking questions to Menir |
| `menir10/mcp_server.py` | MCP JSON-RPC server |
| `menir10/mcp_app.py` | FastAPI wrapper for MCP |
| `logs/menir10_interactions.jsonl` | Interaction log (JSONL format) |
| `tests/test_memoetic.py` | Memoetic layer tests |
| `requirements.txt` | Python dependencies |

---

## 🎯 Common Workflows

### Workflow 1: Daily Note-Taking

```bash
# Log a quick note
python ask_menir.py "Met with team about Q1 roadmap"

# Later, analyze the theme
python -m menir10.memoetic_cli --project personal --mode voice
```

### Workflow 2: Project Analysis

```bash
# Analyze a specific project
python -m menir10.memoetic_cli --project itau_15220012 --mode summary

# See what themes dominate
python -m menir10.memoetic_cli --project itau_15220012 --mode memes
```

### Workflow 3: Export & Archive

```bash
# Export logs to Neo4j (if configured)
python menir10/menir10_export.py

# Tag a release
git tag -a v10.4-snapshot -m "Personal knowledge snapshot"
git push origin --tags
```

---

## 🐛 Troubleshooting

**Import Error: `No module named 'menir10'`**

Ensure you're running Python commands from the repo root:

```bash
cd /path/to/Menir
python -m menir10.memoetic_cli --project personal --mode summary
```

**No interactions logged**

Check if `logs/menir10_interactions.jsonl` exists and has content:

```bash
wc -l logs/menir10_interactions.jsonl
head -5 logs/menir10_interactions.jsonl
```

**MCP Server won't start**

Verify dependencies are installed:

```bash
pip install mcp fastapi uvicorn
```

Then check port 8080 is free:

```bash
lsof -i :8080
```

**OpenAI API errors**

Ensure your `OPENAI_API_KEY` is valid and set:

```bash
echo $OPENAI_API_KEY
```

---

## 📖 Further Reading

- **Memoetic Layer**: See `MEMOETIC_GUIDE.md` for detailed documentation
- **MCP Protocol**: See `menir10/mcp_server.py` for server implementation
- **Model & Schema**: See `docs/MODEL.md` for data structures
- **Contributing**: See `CONTRIBUTING.md` to report issues or contribute

---

## 🎉 Next Steps

1. **Log your first interaction**: `python ask_menir.py "Hello Menir"`
2. **Analyze patterns**: `python -m menir10.memoetic_cli --project personal --mode voice`
3. **Explore the codebase**: Check out `menir10/memoetic.py` for the analysis engine
4. **Start a project**: Use `MENIR_PROJECT_ID` to organize by topic

---

**Version**: v10.4  
**Last Updated**: December 5, 2025  
**License**: See `LICENSE` file  
**Repository**: https://github.com/LPCDC/Menir
