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

from app.utils.logging import configure_logging


if __name__ == "__main__":
    configure_logging()
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info",
        log_config=None,
    )
