# Proxy for Uvicorn execution (Standard for Project IDX / Render / Cloud Run)
# This allows 'uvicorn main:app' to work from root without complex path args

import sys
from pathlib import Path

# Add the scripts directory to python path so we can import menir_server
sys.path.append(str(Path(__file__).parent / "scripts"))

from menir_server import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
