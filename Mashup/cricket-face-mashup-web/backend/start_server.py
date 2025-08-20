#!/usr/bin/env python3
import uvicorn
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    try:
        print("🚀 Starting FastAPI server...")
        uvicorn.run("preload_main:app", host="0.0.0.0", port=8001, reload=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
