from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
import cv2
import numpy as np
import os
import random
import base64
from io import BytesIO
from PIL import Image
import aiofiles
from typing import List, Dict, Any
import json

app = FastAPI(title="Cricket Face Mashup API", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for serving images
app.mount("/uploads", StaticFiles(directory="../uploads"), name="uploads")

class FaceProcessor:
    def __init__(self):
        """Initialize the face processor with OpenCV."""
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Define face part regions
        self.eye_region = (0.15, 0.25, 0.7, 0.4)
        self.nose_region = (0.3, 0.4, 0.4, 0.3)
        self.mouth_region = (0.25, 0.65, 0.5, 0.25)
        
    def detect_face(self, image: np.ndarray):
        """Detect the largest face in an image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return None
        
        largest_face = max(faces, key=lambda face: face[2] * face[3])
        return tuple(largest_face)
    
    def extract_face_part(self, image: np.ndarray, face_rect, part_region):
        """Extract a face part based on region percentages."""
        fx, fy, fw, fh = face_rect
        rx, ry, rw, rh = part_region
        
        x = int(fx + fw * rx)
        y = int(fy + fh * ry)
        w = int(fw * rw)
        h = int(fh * rh)
        
        x = max(0, min(x, image.shape[1] - w))
        y = max(0, min(y, image.shape[0] - h))
        w = min(w, image.shape[1] - x)
        h = min(h, image.shape[0] - y)
        
        return image[y:y+h, x:x+w]
    
    def create_simple_mask(self, shape):
        """Create a simple elliptical mask for blending."""
        mask = np.zeros(shape[:2], dtype=np.uint8)
        center = (shape[1]//2, shape[0]//2)
        axes = (shape[1]//3, shape[0]//3)
        cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
        mask = cv2.GaussianBlur(mask, (15, 15), 0)
        return mask
    
    def blend_parts(self, base_image: np.ndarray, overlay_part: np.ndarray, position):
        """Blend a face part onto the base image."""
        x, y = position
        h, w = overlay_part.shape[:2]
        
        if x + w > base_image.shape[1] or y + h > base_image.shape[0]:
            return base_image
        
        mask = self.create_simple_mask((h, w))
        mask_3d = cv2.merge([mask, mask, mask]) / 255.0
        
        base_region = base_image[y:y+h, x:x+w]
        blended_region = overlay_part * mask_3d + base_region * (1 - mask_3d)
        
        result = base_image.copy()
        result[y:y+h, x:x+w] = blended_region.astype(np.uint8)
        
        return result

# Global instances
face_processor = FaceProcessor()
player_cache = {}  # Cache for loaded players

def load_image_from_upload(file_content: bytes) -> np.ndarray:
    """Load image from uploaded file content."""
    nparr = np.frombuffer(file_content, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image

def image_to_base64(image: np.ndarray) -> str:
    """Convert OpenCV image to base64 string."""
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{image_base64}"

@app.get("/")
async def root():
    return {"message": "Cricket Face Mashup API is running!"}

@app.post("/upload-players")
async def upload_players(files: List[UploadFile] = File(...)):
    """Upload multiple player images."""
    try:
        uploaded_players = []
        
        for file in files:
            if not file.content_type.startswith('image/'):
                continue
                
            # Read file content
            content = await file.read()
            
            # Load and validate image
            image = load_image_from_upload(content)
            if image is None:
                continue
                
            # Detect face
            face = face_processor.detect_face(image)
            if face is None:
                continue
                
            # Get player name from filename
            player_name = os.path.splitext(file.filename)[0].replace('_', ' ').title()
            
            # Save to uploads directory
            file_path = f"../uploads/{file.filename}"
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            # Cache the player data
            player_cache[player_name] = {
                'image': image,
                'face': face,
                'filename': file.filename,
                'path': file_path
            }
            
            uploaded_players.append({
                'name': player_name,
                'filename': file.filename,
                'face_detected': True
            })
        
        return {
            "success": True,
            "message": f"Uploaded {len(uploaded_players)} players",
            "players": uploaded_players,
            "total_players": len(player_cache)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/players")
async def get_players():
    """Get list of all uploaded players."""
    players = []
    for name, data in player_cache.items():
        players.append({
            'name': name,
            'filename': data['filename'],
            'image_url': f"/uploads/{data['filename']}"
        })
    
    return {
        "players": players,
        "total": len(players)
    }

@app.post("/create-mashup")
async def create_mashup(num_players: int = 3):
    """Create a face mashup from random players."""
    try:
        if len(player_cache) < num_players:
            raise HTTPException(
                status_code=400, 
                detail=f"Need at least {num_players} players, have {len(player_cache)}"
            )
        
        # Select random players
        selected_players = random.sample(list(player_cache.items()), num_players)
        
        # Use first player as base
        base_name, base_data = selected_players[0]
        base_image = base_data['image'].copy()
        base_face = base_data['face']
        
        used_players = [base_name]
        
        # Define face parts to blend
        face_parts = [
            (face_processor.eye_region, "eyes"),
            (face_processor.nose_region, "nose"),
            (face_processor.mouth_region, "mouth")
        ]
        
        # Blend different parts from different players
        for i, (part_region, part_name) in enumerate(face_parts):
            if i + 1 < len(selected_players):
                source_name, source_data = selected_players[i + 1]
                source_image = source_data['image']
                source_face = source_data['face']
                
                try:
                    # Extract part from source
                    source_part = face_processor.extract_face_part(
                        source_image, source_face, part_region
                    )
                    
                    # Calculate target position on base face
                    fx, fy, fw, fh = base_face
                    rx, ry, rw, rh = part_region
                    target_x = int(fx + fw * rx)
                    target_y = int(fy + fh * ry)
                    target_w = int(fw * rw)
                    target_h = int(fh * rh)
                    
                    # Resize source part to match target size
                    resized_part = cv2.resize(source_part, (target_w, target_h))
                    
                    # Blend onto result
                    base_image = face_processor.blend_parts(
                        base_image, resized_part, (target_x, target_y)
                    )
                    
                    if source_name not in used_players:
                        used_players.append(source_name)
                        
                except Exception as e:
                    print(f"Could not blend {part_name} from {source_name}: {e}")
        
        # Convert result to base64
        mashup_base64 = image_to_base64(base_image)
        
        return {
            "success": True,
            "mashup_image": mashup_base64,
            "used_players": used_players,
            "base_player": base_name
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-quiz")
async def generate_quiz(correct_players: List[str], total_options: int = 4):
    """Generate quiz options for the mashup."""
    try:
        all_player_names = list(player_cache.keys())
        
        if len(all_player_names) < total_options:
            raise HTTPException(
                status_code=400,
                detail=f"Need at least {total_options} players for quiz options"
            )
        
        # Create correct answer
        correct_answer = " + ".join(sorted(correct_players))
        
        # Generate wrong options
        wrong_options = []
        attempts = 0
        while len(wrong_options) < total_options - 1 and attempts < 20:
            num_players = random.randint(2, 3)
            random_players = random.sample(all_player_names, min(num_players, len(all_player_names)))
            wrong_answer = " + ".join(sorted(random_players))
            
            if wrong_answer != correct_answer and wrong_answer not in wrong_options:
                wrong_options.append(wrong_answer)
            attempts += 1
        
        # Fill remaining slots if needed
        while len(wrong_options) < total_options - 1:
            random_player = random.choice(all_player_names)
            if random_player not in wrong_options and random_player != correct_answer:
                wrong_options.append(random_player)
        
        # Combine and shuffle
        all_options = [correct_answer] + wrong_options[:total_options-1]
        random.shuffle(all_options)
        
        return {
            "success": True,
            "options": all_options,
            "correct_answer": correct_answer
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear-players")
async def clear_players():
    """Clear all uploaded players."""
    global player_cache
    player_cache = {}
    
    # Also delete uploaded files
    uploads_dir = "../uploads"
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                os.remove(os.path.join(uploads_dir, filename))
    
    return {"success": True, "message": "All players cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
