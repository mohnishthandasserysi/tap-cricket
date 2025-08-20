from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import base64
import random
from typing import List
import os
import glob
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

print("🚀 OPTIMIZED PRELOAD Cricket Face Mashup - 4 Test Images!")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-loaded players from test_uploads
players_db = []

def load_single_image(image_path):
    """Load a single image file with optimized processing"""
    try:
        # Read image file as base64
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Only convert to base64 once when requested, not at startup
        # Store raw bytes for now to speed up startup
        
        # Determine content type
        ext = os.path.splitext(image_path)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            content_type = 'image/jpeg'
        elif ext == '.png':
            content_type = 'image/png'
        elif ext == '.bmp':
            content_type = 'image/bmp'
        else:
            content_type = 'image/jpeg'
        
        # Extract player name from filename
        filename = os.path.basename(image_path)
        player_name = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
        
        player = {
            'name': player_name,
            'filename': filename,
            'image_data': image_data,  # Store raw bytes instead of base64
            'content_type': content_type,
            'face_detected': True  # Assume true for preloaded images
        }
        
        print(f"✅ Preloaded: {player_name} ({filename}) - {len(image_data)} bytes")
        return player
        
    except Exception as e:
        print(f"❌ Error loading {os.path.basename(image_path)}: {e}")
        return None

def preload_test_images_optimized():
    """Load the 4 images from test_uploads folder with parallel processing"""
    global players_db
    start_time = time.time()
    
    test_folder = "../test_uploads"
    
    if not os.path.exists(test_folder):
        print(f"❌ Test folder not found: {test_folder}")
        return 0
    
    # Get all image files
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG', '*.BMP']
    image_files = []
    
    for extension in image_extensions:
        image_files.extend(glob.glob(os.path.join(test_folder, extension)))
    
    print(f"📸 Found {len(image_files)} test images")
    
    # Load images in parallel using ThreadPoolExecutor
    loaded_count = 0
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all image loading tasks
        future_to_path = {executor.submit(load_single_image, path): path for path in image_files}
        
        # Collect results as they complete
        for future in future_to_path:
            player = future.result()
            if player:
                players_db.append(player)
                loaded_count += 1
    
    load_time = time.time() - start_time
    print(f"🎯 Successfully preloaded {loaded_count} players in {load_time:.2f} seconds!")
    return loaded_count

def convert_to_data_url(player):
    """Convert player image data to data URL (only when needed)"""
    if 'image_url' not in player:
        # Convert raw bytes to base64 only when requested
        image_base64 = base64.b64encode(player['image_data']).decode('utf-8')
        player['image_url'] = f"data:{player['content_type']};base64,{image_base64}"
        # Remove raw bytes to save memory
        del player['image_data']
    return player

# Preload images on startup with optimization
loaded_count = preload_test_images_optimized()

@app.get("/")
async def root():
    return {
        "message": "Cricket Face Mashup OPTIMIZED PRELOAD API is running!", 
        "players": len(players_db),
        "status": "ready" if len(players_db) >= 3 else "need_more_players",
        "mode": "optimized_preloaded",
        "preloaded_count": loaded_count,
        "optimization": "parallel_loading_lazy_base64"
    }

@app.get("/players")
async def get_players():
    # Convert to data URLs only when requested
    players_with_urls = []
    for player in players_db:
        player_copy = player.copy()
        convert_to_data_url(player_copy)
        players_with_urls.append(player_copy)
    
    return {
        "players": players_with_urls,
        "total": len(players_db),
        "ready_to_play": len(players_db) >= 3,
        "preloaded": True,
        "optimized": True
    }

@app.post("/create-mashup")
async def create_mashup():
    if len(players_db) < 3:
        raise HTTPException(status_code=400, detail=f"Need at least 3 players. Found {len(players_db)} preloaded.")
    
    # Pick 3 random players from preloaded set
    selected = random.sample(players_db, 3)
    
    # Convert to data URL for the selected player
    mashup_player = selected[0].copy()
    convert_to_data_url(mashup_player)
    
    print(f"🎮 Creating mashup with: {[p['name'] for p in selected]}")
    
    return {
        "success": True,
        "mashup_image": mashup_player['image_url'],
        "used_players": [p['name'] for p in selected],
        "base_player": selected[0]['name']
    }

@app.post("/generate-quiz")
async def generate_quiz(correct_players: List[str]):
    all_names = [p['name'] for p in players_db]
    correct_answer = " + ".join(sorted(correct_players))
    
    # Generate 3 wrong answers from preloaded players
    wrong_options = []
    for _ in range(3):
        if len(all_names) >= 2:
            wrong_players = random.sample(all_names, min(2, len(all_names)))
            wrong_answer = " + ".join(sorted(wrong_players))
            if wrong_answer != correct_answer and wrong_answer not in wrong_options:
                wrong_options.append(wrong_answer)
    
    # Fill with single names if needed
    while len(wrong_options) < 3:
        random_name = random.choice(all_names)
        if random_name not in wrong_options and random_name != correct_answer:
            wrong_options.append(random_name)
    
    all_options = [correct_answer] + wrong_options[:3]
    random.shuffle(all_options)
    
    print(f"🎯 Quiz: {correct_answer} vs {wrong_options}")
    
    return {
        "success": True,
        "options": all_options,
        "correct_answer": correct_answer
    }

# Health check endpoint for the optimized script
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "players_loaded": len(players_db),
        "ready": len(players_db) >= 3,
        "optimization": "active"
    }

if __name__ == "__main__":
    import uvicorn
    print("⚡ OPTIMIZED PRELOAD Cricket Face Mashup API - 4 Test Images Ready!")
    print("🌐 Starting on: http://localhost:8001")
    print("📁 NO UPLOAD NEEDED - Images already loaded!")
    print(f"🎮 Ready to play with {len(players_db)} preloaded players!")
    print("🚀 OPTIMIZATIONS: Parallel loading + Lazy base64 conversion")
    uvicorn.run(app, host="0.0.0.0", port=8001)
