#!/usr/bin/env python
"""
Run the TheOrchestrator FastAPI server.

This script starts the Uvicorn server on localhost:8000 with auto-reload enabled.
Make sure to activate the virtual environment first:
    .\activate.ps1 (Windows)
    source activate.sh (Linux/macOS)

Then run:
    python run.py
"""

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
