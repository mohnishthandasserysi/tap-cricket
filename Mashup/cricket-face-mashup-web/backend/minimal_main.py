from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import base64
import random
from typing import List

print("🚀 Starting Cricket Face Mashup - Minimal Version...")

app = FastAPI(title="Cricket Face Mashup API - Minimal")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage
players_db = []

@app.get("/")
async def root():
    return {
        "message": "Cricket Face Mashup API is running!", 
        "players": len(players_db),
        "status": "ready" if len(players_db) >= 3 else "need_more_players"
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
                'face_detected': True
            }
            
            players_db.append(player)
            uploaded.append(player)
    
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
    
    # Simple mashup - just pick 3 random players
    selected = random.sample(players_db, 3)
    
    # Use the first player's image as the "mashup"
    return {
        "success": True,
        "mashup_image": selected[0]['image_url'],
        "used_players": [p['name'] for p in selected],
        "base_player": selected[0]['name']
    }

@app.post("/generate-quiz")
async def generate_quiz(correct_players: List[str]):
    all_names = [p['name'] for p in players_db]
    correct_answer = " + ".join(sorted(correct_players))
    
    # Generate wrong answers
    wrong_options = []
    for _ in range(3):
        wrong_players = random.sample(all_names, min(3, len(all_names)))
        wrong_answer = " + ".join(sorted(wrong_players))
        if wrong_answer != correct_answer and wrong_answer not in wrong_options:
            wrong_options.append(wrong_answer)
    
    # Fill if needed
    while len(wrong_options) < 3:
        wrong_options.append(random.choice(all_names))
    
    all_options = [correct_answer] + wrong_options[:3]
    random.shuffle(all_options)
    
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
    print("🏏 Cricket Face Mashup API - Minimal Version")
    print("🌐 Starting on: http://localhost:8000")
    print("📁 This version uses manual upload (no auto-loading)")
    print("✅ Ready for testing!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
