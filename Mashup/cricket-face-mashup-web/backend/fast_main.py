from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import os
import json
import base64
import random

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to store cached data
players_data = []
cache_dir = "../cache"

def load_cached_data():
    """Load all preprocessed data into memory"""
    global players_data
    
    print("🚀 Loading cached player data...")
    
    # Load players data
    with open(os.path.join(cache_dir, 'players_data.json'), 'r') as f:
        players_data = json.load(f)
    
    print(f"✅ Loaded {len(players_data)} players from cache!")
    return len(players_data)

@app.on_event("startup")
async def startup_event():
    """Initialize the server with cached data"""
    num_players = load_cached_data()
    print(f"🎯 Server ready with {num_players} players!")

@app.get("/players")
async def get_players():
    """Return list of all players"""
    return players_data

@app.post("/create-mashup")
async def create_mashup(player_names: list):
    """Create a mashup of two players using cached data"""
    if len(player_names) != 2:
        raise HTTPException(status_code=400, detail="Exactly 2 player names required")
        
    try:
        # Find players in cache
        player1 = next((p for p in players_data if p['name'] == player_names[0]), None)
        player2 = next((p for p in players_data if p['name'] == player_names[1]), None)
        
        if not player1 or not player2:
            raise HTTPException(status_code=404, detail="Player(s) not found")
            
        # Load cached npz files
        data1 = np.load(os.path.join(cache_dir, player1['cache_file']))
        data2 = np.load(os.path.join(cache_dir, player2['cache_file']))
        
        img1 = data1['image']
        img2 = data2['image']
        
        # Create vertical gradient blend
        height, width = img1.shape[:2]
        alpha = np.zeros((height, width), dtype=np.float32)
        
        # Create gradient with sharp transition
        mid_point = height // 2
        blend_zone = 25  # pixels for transition
        
        alpha[:mid_point - blend_zone] = 1.0
        alpha[mid_point + blend_zone:] = 0.0
        for i in range(blend_zone * 2):
            pos = mid_point - blend_zone + i
            if pos >= 0 and pos < height:
                alpha[pos, :] = 1.0 - (i / (blend_zone * 2.0))
        
        # Convert to 3-channel alpha
        alpha_3d = cv2.merge([alpha, alpha, alpha])
        
        # Blend images
        result = (img2 * alpha_3d + img1 * (1.0 - alpha_3d)).astype(np.uint8)
        
        # Convert to base64
        _, buffer = cv2.imencode('.png', result)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return {
            "success": True,
            "mashup_image": f"data:image/png;base64,{img_base64}",
            "used_players": player_names
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-quiz")
async def generate_quiz(player_names: list):
    """Generate quiz options for a mashup"""
    if len(player_names) != 2:
        raise HTTPException(status_code=400, detail="Exactly 2 player names required")
        
    # Create correct answer
    correct = f"{player_names[0]} + {player_names[1]}"
    
    # Generate 3 wrong options
    all_names = [p['name'] for p in players_data]
    options = []
    
    while len(options) < 3:
        name1 = random.choice(all_names)
        name2 = random.choice(all_names)
        option = f"{name1} + {name2}"
        
        if option != correct and option not in options:
            options.append(option)
    
    # Add correct answer and shuffle
    options.append(correct)
    random.shuffle(options)
    
    return {
        "success": True,
        "correct": correct,
        "options": options
    }