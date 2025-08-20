from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import os
import random
import base64
from typing import List, Dict, Any
import json

from horizontal_mashup import HorizontalFaceMashup

app = FastAPI(title="Cricket Face Mashup API - Horizontal Version", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the horizontal face mashup processor
mashup_processor = HorizontalFaceMashup()

# Global storage for preloaded players
players_db = []

def image_to_base64(image: np.ndarray) -> str:
    """Convert OpenCV image to base64 string."""
    _, buffer = cv2.imencode('.jpeg', image, [cv2.IMWRITE_JPEG_QUALITY, 95])
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{image_base64}"

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global players_db
    
    # Load preloaded player images
    preload_dir = "../test_uploads"
    if os.path.exists(preload_dir):
        print(f"🔍 Scanning {preload_dir} for player images...")
        
        for filename in os.listdir(preload_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                file_path = os.path.join(preload_dir, filename)
                
                try:
                    # Load image
                    cv_image = cv2.imread(file_path)
                    if cv_image is None:
                        print(f"⚠️ Could not load {filename}")
                        continue
                    
                    # Detect face
                    face_rect = mashup_processor.detect_face(cv_image)
                    
                    # Extract player name from filename
                    player_name = os.path.splitext(filename)[0]
                    
                    player_data = {
                        'name': player_name,
                        'cv_image': cv_image,
                        'face_rect': face_rect,
                        'filename': filename
                    }
                    
                    players_db.append(player_data)
                    print(f"✅ Loaded {player_name} - Face detected: {face_rect is not None}")
                    
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")
    
    print(f"🎮 Preloaded {len(players_db)} players")

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Cricket Face Mashup API - Horizontal Version", "status": "running"}

@app.get("/players")
async def get_players():
    """Return list of all preloaded players."""
    return {
        "players": [{"name": p["name"], "has_face": p["face_rect"] is not None} for p in players_db],
        "total": len(players_db)
    }

@app.get("/config")
async def get_config():
    """Get current mashup configuration."""
    return mashup_processor.get_current_config()

@app.post("/config")
async def update_config(new_config: Dict[str, Any]):
    """Update mashup configuration."""
    try:
        mashup_processor.update_config(new_config)
        return {"success": True, "message": "Configuration updated", "config": mashup_processor.get_current_config()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")

@app.post("/create-mashup")
async def create_mashup():
    """Create a horizontal face mashup from random players."""
    if len(players_db) < 2:
        raise HTTPException(status_code=400, detail=f"Need at least 2 players. Found {len(players_db)} preloaded.")
    
    # Pick 2 random players from preloaded set
    selected = random.sample(players_db, 2)
    
    print(f"🎮 Creating horizontal mashup with: {[p['name'] for p in selected]}")
    
    try:
        # Get images and face data from the 2 selected players
        img1 = selected[0]['cv_image']  # Background player
        img2 = selected[1]['cv_image']  # Foreground player
        face1_rect = selected[0]['face_rect']
        face2_rect = selected[1]['face_rect']
        
        print(f"🎮 Background player: {selected[0]['name']} (eyes visible)")
        print(f"🎮 Foreground player: {selected[1]['name']} (mouth/neck visible)")
        
        # Create the horizontal mashup with edge detection
        result = mashup_processor.process_mashup_with_edge_detection(
            img1=img1,
            img2=img2,
            face1_rect=face1_rect,
            face2_rect=face2_rect,
            player1_name=selected[0]['name'],
            player2_name=selected[1]['name']
        )
        
        # Convert result to base64
        mashup_base64 = image_to_base64(result)
        
        print(f"✅ Successfully created horizontal mashup!")
        print(f"✅ Background: {selected[0]['name']}, Foreground: {selected[1]['name']}")
        
        return {
            "success": True,
            "mashup_image": mashup_base64,
            "used_players": [p['name'] for p in selected],
            "background_player": selected[0]['name'],
            "foreground_player": selected[1]['name'],
            "blend_status": "horizontal_transparency_gradient_success",
            "config": mashup_processor.get_current_config()
        }
        
    except Exception as e:
        print(f"❌ Error creating mashup: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/create-mashup-custom")
async def create_mashup_custom(player_names: List[str], config_overrides: Dict[str, Any] = None):
    """Create a custom mashup with specific players and optional config overrides."""
    if len(player_names) != 2:
        raise HTTPException(status_code=400, detail="Exactly 2 player names required")
    
    # Find players by name
    player1 = next((p for p in players_db if p['name'] == player_names[0]), None)
    player2 = next((p for p in players_db if p['name'] == player_names[1]), None)
    
    if not player1 or not player2:
        raise HTTPException(status_code=404, detail="One or both players not found")
    
    try:
        # Apply config overrides if provided
        if config_overrides:
            mashup_processor.update_config(config_overrides)
            print(f"🔧 Applied config overrides: {config_overrides}")
        
        # Create the mashup
        result = mashup_processor.process_mashup_with_edge_detection(
            img1=player1['cv_image'],
            img2=player2['cv_image'],
            face1_rect=player1['face_rect'],
            face2_rect=player2['face_rect'],
            player1_name=player1['name'],
            player2_name=player2['name']
        )
        
        # Convert result to base64
        mashup_base64 = image_to_base64(result)
        
        return {
            "success": True,
            "mashup_image": mashup_base64,
            "used_players": player_names,
            "background_player": player1['name'],
            "foreground_player": player2['name'],
            "config": mashup_processor.get_current_config()
        }
        
    except Exception as e:
        print(f"❌ Error creating custom mashup: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "players_loaded": len(players_db),
        "face_processor_ready": not mashup_processor.face_cascade.empty(),
        "config_loaded": bool(mashup_processor.config)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
