from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import base64
import random
from typing import List
import os

print("🚀 Starting INSTANT Cricket Face Mashup - No Processing!")

app = FastAPI(title="Cricket Face Mashup - INSTANT")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage - NO IMAGE PROCESSING
players_db = []

@app.get("/")
async def root():
    return {
        "message": "Cricket Face Mashup INSTANT API is running!", 
        "players": len(players_db),
        "status": "ready",
        "mode": "instant_no_processing"
    }

@app.post("/upload-players")
async def upload_players(files: List[UploadFile] = File(...)):
    global players_db
    
    uploaded = []
    for file in files:
        if file.content_type and file.content_type.startswith('image/'):
            content = await file.read()
            image_base64 = base64.b64encode(content).decode('utf-8')
            data_url = f"data:{file.content_type};base64,{image_base64}"
            
            player_name = file.filename.split('.')[0].replace('_', ' ').title()
            
            player = {
                'name': player_name,
                'filename': file.filename,
                'image_url': data_url,
                'face_detected': True  # Always true for instant mode
            }
            
            players_db.append(player)
            uploaded.append(player)
            print(f"📸 Uploaded: {player_name}")
    
    return {
        "success": True,
        "message": f"Uploaded {len(uploaded)} players",
        "players": uploaded,
        "total_players": len(players_db)
    }

@app.get("/players")
async def get_players():
    return {
        "players": players_db,
        "total": len(players_db),
        "ready_to_play": len(players_db) >= 3
    }

@app.post("/create-mashup")
async def create_mashup():
    if len(players_db) < 3:
        raise HTTPException(status_code=400, detail="Need at least 3 players")
    
    # INSTANT: Just pick 3 random players, use first one's image as "mashup"
    selected = random.sample(players_db, 3)
    
    print(f"🎮 Creating mashup with: {[p['name'] for p in selected]}")
    
    return {
        "success": True,
        "mashup_image": selected[0]['image_url'],  # Use first player's image
        "used_players": [p['name'] for p in selected],
        "base_player": selected[0]['name']
    }

@app.post("/generate-quiz")
async def generate_quiz(correct_players: List[str]):
    all_names = [p['name'] for p in players_db]
    correct_answer = " + ".join(sorted(correct_players))
    
    # Generate 3 wrong answers quickly
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

@app.delete("/clear-players")
async def clear_players():
    global players_db
    players_db = []
    return {"success": True, "message": "All players cleared"}

if __name__ == "__main__":
    import uvicorn
    print("⚡ INSTANT Cricket Face Mashup API")
    print("🌐 Starting IMMEDIATELY on: http://localhost:8000")
    print("📁 No image processing - INSTANT startup!")
    print("🎮 Upload images and play immediately!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
