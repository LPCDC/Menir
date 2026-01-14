# Menir v10.4 – Quick How-To (Local or New Machine)

## 1. Unpack the full release package

```bash
tar -xzf Menir_v10.4-custom_full.tar.gz
cd Menir
```

---

## 2. Set up Python environment

### Option A: Using venv (Recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Option B: Using Conda

```bash
conda create -n menir python=3.12
conda activate menir
pip install -r requirements.txt
```

---

## 3. Quick validation (run smoke test)

```bash
chmod +x menir_final_smoketest.sh
./menir_final_smoketest.sh
```

**Expected output:**
```
✅ MENIR v10.4 SMOKE TEST PASSED
• Tests: 41/41 PASSING
• Coverage: 76%
• Package: 152K (115 files)
```

---

## 4. Use the Memoetic Layer (Main Feature)

### Analyze project voice

```bash
python -m menir10.memoetic_cli --project personal --mode voice
```

**Output example:**
```
Project 'personal' currently has 24 logged interactions. 
Its vocabulary tends to revolve around: menir, project, feature, test.
It is mostly composed of short, direct notes.
The language shows high lexical variety, suggesting exploratory thinking.
```

### See top terms and sample quotes

```bash
python -m menir10.memoetic_cli --project personal --mode summary
```

**Output includes:**
- Total interactions
- Top 20 terms with frequency
- Sample quotes from logs

### Find recurring themes ("memes")

```bash
python -m menir10.memoetic_cli --project personal --mode memes
```

**Output:**
```
Recurring terms (freq >= 3):
  menir: 15
  project: 8
  feature: 5
Sample quotes:
 - "Implemented memoetic layer for narrative analysis"
```

---

## 5. Run the full test suite

```bash
pytest -q                    # Quick run (41 tests)
pytest -v                    # Verbose (show each test)
pytest tests/test_memoetic.py -v   # Just memoetic tests
```

---

## 6. Generate coverage report

```bash
coverage run -m pytest
coverage html -d coverage_report
open coverage_report/index.html  # macOS
# or: xdg-open coverage_report/index.html  # Linux
# or: start coverage_report/index.html  # Windows
```

---

## 7. Export logs to Neo4j (Cypher)

### Generate Cypher from interaction logs

```bash
python menir10_export.py export-cypher logs/menir10_interactions.jsonl > menir_export.cypher
```

### Import into Neo4j

```bash
cypher-shell -u neo4j -p password < menir_export.cypher
```

Or paste content into **Neo4j Browser** at `http://localhost:7687`

---

## 8. View documentation

```bash
# Quick start guide
cat QUICKSTART.md

# Memoetic layer API reference
cat MEMOETIC_GUIDE.md

# Release notes
cat RELEASE_NOTES_v10.4.md
```

---

## 9. Start the MCP Server (Optional)

The Menir platform includes a **Model Context Protocol** (MCP) server for JSON-RPC integration.

```bash
uvicorn menir10.mcp_app:app --host 0.0.0.0 --port 8080
```

**Test the server:**

```bash
curl -X POST http://localhost:8080/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "method": "ping", "id": 1}'
```

**Expected response:**
```json
{"jsonrpc": "2.0", "id": 1, "result": {"status": "pong"}}
```

---

## 10. Common workflows

### Workflow 1: Daily Note-Taking

```bash
# Log a note
python ask_menir.py "Completed feature X, merged to main"

# Later, analyze the theme
python -m menir10.memoetic_cli --project personal --mode voice
```

### Workflow 2: Project Analysis

```bash
# Check project status
python -m menir10.memoetic_cli --project itau_15220012 --mode summary

# Identify dominant themes
python -m menir10.memoetic_cli --project itau_15220012 --mode memes
```

### Workflow 3: Team Distribution

```bash
# Prepare release package
tar -czf Menir_v10.4_backup_$(date +%Y%m%d).tar.gz .

# Share with team
scp Menir_v10.4_backup_*.tar.gz team@server:/backups/
```

---

## 🐛 Troubleshooting

### Error: `No module named 'menir10'`

**Solution:** Ensure you're running from the repo root:
```bash
cd /path/to/Menir
python -m menir10.memoetic_cli --project personal --mode summary
```

### Error: `OPENAI_API_KEY not set`

**Solution:** Only needed if using `ask_menir.py` (which requires GPT). For memoetic analysis, it's not needed.

To set it:
```bash
export OPENAI_API_KEY="sk-..."
python ask_menir.py "your query"
```

### Tests fail with import errors

**Solution:** Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
pytest -q
```

### Coverage report not generated

**Solution:** Install coverage tools:
```bash
pip install coverage pytest-cov
coverage run -m pytest
coverage html
```

---

## ✅ Verification Checklist

Before using Menir in production:

- [ ] Unpacked the release package
- [ ] Created virtual environment
- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Ran smoke test (`./menir_final_smoketest.sh`)
- [ ] Tested memoetic CLI (at least one mode)
- [ ] Reviewed documentation
- [ ] Ran full test suite (`pytest -q`)
- [ ] Generated coverage report
- [ ] (Optional) Started and tested MCP server

---

## 📚 Further Reading

| Document | Purpose |
|----------|---------|
| `QUICKSTART.md` | Step-by-step setup guide |
| `MEMOETIC_GUIDE.md` | Complete API documentation |
| `RELEASE_NOTES_v10.4.md` | What's new in v10.4 |
| `README.md` | General project info |
| `VOICE_GUIDE.md` | Voice interface setup |

---

## 🎯 Next Steps

1. **For Local Development:**
   - Clone the repo
   - Set up venv
   - Run tests
   - Start coding

2. **For Team Distribution:**
   - Unpack release package
   - Share with team members
   - Each member follows steps 1-3

3. **For Production Deployment:**
   - Use the `.tar.gz` package
   - Deploy to server
   - Run smoke test on server
   - Configure environment variables (if needed)

4. **For GitHub Release:**
   - Upload `Menir_v10.4-custom_full.tar.gz` to GitHub Releases
   - Add release notes
   - Mark as latest version

---

## 💡 Tips & Tricks

### Run a quick memoetic analysis

```bash
python -m menir10.memoetic_cli --project $(whoami) --mode voice
```

### Watch tests on save (requires pytest-watch)

```bash
pip install pytest-watch
ptw
```

### Generate a project report

```bash
python -c "
from menir10.memoetic import extract_memoetics
p = extract_memoetics('personal')
print(f'Project: {p.project_id}')
print(f'Interactions: {p.total_interactions}')
print(f'Top terms: {p.top_terms[:5]}')
"
```

### Backup your logs

```bash
cp logs/menir10_interactions.jsonl logs/backup_$(date +%Y%m%d_%H%M%S).jsonl
```

---

## 📞 Support

- **Issues**: Report on GitHub
- **Docs**: See README.md and QUICKSTART.md
- **Community**: GitHub Discussions

---

**Enjoy using Menir v10.4!** 🚀
