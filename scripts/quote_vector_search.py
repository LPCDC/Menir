#!/usr/bin/env python3
# scripts/quote_vector_search.py

import sys
from pathlib import Path

# Add parent directory to path for menir_core imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from menir_core.quote_vector_search import cli_main

if __name__ == "__main__":
    cli_main()

