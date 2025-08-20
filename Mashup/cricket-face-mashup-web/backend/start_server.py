import uvicorn
import os
import sys
import time
from preload_main_optimized import preprocess_all_images

def main():
    # Check if cache exists and is up to date
    cache_dir = "../cache"
    cache_exists = os.path.exists(cache_dir) and os.path.exists(os.path.join(cache_dir, 'players_data.json'))
    
    if not cache_exists:
        print("🔄 No cache found, running preprocessing...")
        preprocess_all_images()
    
    print("🚀 Starting FastAPI server...")
    uvicorn.run("fast_main:app", host="0.0.0.0", port=8001, reload=False)

if __name__ == "__main__":
    main()