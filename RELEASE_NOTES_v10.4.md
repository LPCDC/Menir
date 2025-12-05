# Menir v10.4 Release Notes

**Release Date:** December 5, 2025  
**Version:** 10.4  
**Status:** Production Ready ✅

---

## Overview

Menir v10.4 introduces the **Memoetic Layer**, a deterministic narrative pattern extraction system. This release adds powerful text analysis capabilities to the Menir platform, enabling users to analyze project history, identify recurring themes, and generate narrative "voices" from interaction logs.

---

## 🆕 New Features

### 1. Memoetic Layer (`menir10/memoetic.py`)
- **Extract Patterns**: Analyze JSONL logs to identify term frequencies and narrative patterns
- **Voice Synthesis**: Generate deterministic descriptions of project narrative style
- **Meme Listing**: Identify recurring linguistic themes and concepts
- **Zero LLM**: All analysis is deterministic—no external API calls

### 2. Memoetic CLI (`menir10/memoetic_cli.py`)
- `--mode summary`: Profile view with top terms and sample quotes
- `--mode voice`: Narrative style description
- `--mode memes`: Recurring themes with frequency filtering
- Standalone tool for CLI users

### 3. Enhanced Documentation
- **QUICKSTART.md**: Step-by-step installation and usage guide
- **MEMOETIC_GUIDE.md**: Comprehensive API documentation
- Clear examples and workflows for all major use cases

---

## 🔧 Technical Improvements

### Bug Fixes
- Fixed `menir10_boot.py` to use dynamic `LOG_PATH` reference for test compatibility
- Resolved logging path issues in boot interaction helpers

### Test Coverage
- **41 tests** across 6 test modules
- **76% code coverage** (1016 lines analyzed)
- All core features validated

### Code Quality
- Deterministic algorithms for narrative analysis
- Tolerant JSONL parsing (handles missing fields, blank lines)
- Unicode and accented character support (PT/EN mixed)

---

## 📦 Package Contents

### Core Modules (menir10/)
- `memoetic.py` - Narrative pattern extraction
- `memoetic_cli.py` - CLI interface
- `mcp_server.py` - MCP JSON-RPC server
- `mcp_app.py` - FastAPI wrapper
- `menir10_boot.py` - Boot sequence management
- `menir10_log.py` - JSONL interaction logging
- `menir10_state.py` - State management
- `menir10_export.py` - Neo4j Cypher export
- `menir10_insights.py` - Project insights

### Test Suite (tests/)
- `test_memoetic.py` - Memoetic layer tests (4 tests)
- `test_mcp_server.py` - MCP server tests (21 tests)
- `test_menir10_boot.py` - Boot tests (4 tests)
- `test_menir10_daily_report.py` - Report tests (2 tests)
- `test_menir10_export.py` - Export tests (4 tests)
- `test_menir10_insights.py` - Insights tests (6 tests)

### Documentation
- `README.md` - Main documentation
- `QUICKSTART.md` - Installation and usage guide
- `MEMOETIC_GUIDE.md` - API reference
- `VOICE_GUIDE.md` - Voice interface setup

### Utilities
- `menir_final_smoketest.sh` - Validation script
- `requirements.txt` - Python dependencies
- `pytest.ini` - Test configuration

---

## 🚀 Quick Start

### Installation
```bash
git clone https://github.com/LPCDC/Menir.git
cd Menir
git checkout v10.4
pip install -r requirements.txt
```

### Usage
```bash
# Analyze project narrative
python -m menir10.memoetic_cli --project personal --mode voice

# See summary with top terms
python -m menir10.memoetic_cli --project personal --mode summary

# List recurring themes
python -m menir10.memoetic_cli --project personal --mode memes
```

### Run Tests
```bash
pytest -q          # Quick run (41 tests)
pytest -v          # Verbose output
coverage report    # Coverage summary
```

---

## 📊 Quality Metrics

| Metric | Value |
|--------|-------|
| **Test Coverage** | 76% (1016 lines) |
| **Tests Passing** | 41/41 ✅ |
| **Core Modules** | 7 |
| **Test Modules** | 6 |
| **Package Size** | 152 KB (compressed) |
| **Files in Package** | 115 |

---

## 🔄 Migration from v10.3

No breaking changes. Menir v10.4 is fully backward compatible with v10.3.

**New in v10.4:**
- `menir10/memoetic.py` module
- `menir10/memoetic_cli.py` CLI tool
- Updated documentation

**To upgrade:**
```bash
git pull origin main
pip install -r requirements.txt
pytest -q  # Verify all tests pass
```

---

## 🐛 Known Limitations

1. **Single Language Processing**: Treats all text as one language. Multi-language support planned for v11.
2. **No Semantic Clustering**: Identifies terms but not semantic concepts (future enhancement).
3. **No Temporal Analysis**: Does not track theme evolution over time.
4. **Static Stopwords**: Hardcoded stopword list; external configuration coming in v11.

---

## 🗺️ Roadmap

### v10.5 (Planned)
- Multi-language stopword support
- Semantic clustering with embeddings
- Temporal pattern analysis

### v11.0 (Q1 2026)
- Neo4j graph visualization enhancements
- Advanced narrative analytics
- Real-time pattern detection

---

## 📝 Release Artifacts

- **GitHub Release**: Full source + release notes
- **Distribution Package**: `Menir_v10.4-custom_full.tar.gz` (152 KB)
  - Includes: source, tests, docs, coverage report
- **Docker Image** (optional): Available at Docker Hub

---

## 🎯 Testing & Validation

All features validated with:
```bash
./menir_final_smoketest.sh
```

Checks:
- ✅ Repository structure
- ✅ Test suite (41/41 passing)
- ✅ Memoetic CLI functionality
- ✅ Cypher export
- ✅ Coverage report
- ✅ Release package integrity

---

## 📄 License

MIT License (see LICENSE file)

---

## 🙏 Contributors

- Menir Team
- Open source contributors

---

## 📞 Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Documentation**: See README.md and QUICKSTART.md

---

**Thank you for using Menir v10.4!** 🎉

For questions, feature requests, or bug reports, please visit:  
https://github.com/LPCDC/Menir

