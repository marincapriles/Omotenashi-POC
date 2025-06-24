#!/usr/bin/env python3
"""
Run script for Omotenashi POC application.
This script sets up the proper Python path and runs the FastAPI application.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now we can import and run the application
from src.api.main import app
import uvicorn

if __name__ == "__main__":
    print("🏨 Starting Omotenashi Hotel Concierge API...")
    print(f"Project root: {project_root}")
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )