#!/usr/bin/env python3
"""
Run script for StudyWithAI API
"""

import uvicorn
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

def print_startup_messages():
    print("🚀 Starting StudyWithAI API...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🔄 Interactive API docs at: http://localhost:8000/redoc")
    print("⚡ API endpoints at: http://localhost:8000")
    print("\nPress Ctrl+C to stop the server\n")

def main():
    """Run the FastAPI server."""
    # Get port from environment variable or use default
    port = int(os.getenv("API_PORT", "8001"))
    
    try:
        print_startup_messages()
        print(f"Starting StudyWithAI API on port {port}...")
        
        uvicorn.run(
            "api:app",
            host="0.0.0.0",
            port=port,
            reload=True
        )
    except KeyboardInterrupt:
        print("\n👋 StudyWithAI API stopped by user")
    except Exception as e:
        print(f"❌ Error running StudyWithAI API: {e}")

if __name__ == "__main__":
    main()