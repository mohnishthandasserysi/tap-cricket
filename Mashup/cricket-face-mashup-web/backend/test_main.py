from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import cv2
import numpy as np
import os
import random
import base64
from io import BytesIO
from PIL import Image
import glob
from typing import List
import json

app = FastAPI(title="Cricket Face Mashup API - Test Version", version="1.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple face processor without complex dependencies
class SimpleFaceProcessor:
    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.eye_region = (0.15, 0.25, 0.7, 0.4)
        self.nose_region = (0.3, 0.4, 0.4, 0.3)
        self.mouth_region = (0.25, 0.65, 0.5, 0.25)
        
    def detect_face(self, image: np.ndarray):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) == 0:
            return None
        return tuple(max(faces, key=lambda face: face[2] * face[3]))
    
    def extract_face_part(self, image: np.ndarray, face_rect, part_region):
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
        mask = np.zeros(shape[:2], dtype=np.uint8)
        center = (shape[1]//2, shape[0]//2)
        axes = (shape[1]//3, shape[0]//3)
        cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
        mask = cv2.GaussianBlur(mask, (15, 15), 0)
        return mask
    
    def blend_parts(self, base_image: np.ndarray, overlay_part: np.ndarray, position):
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
face_processor = SimpleFaceProcessor()
player_cache = {}

def load_test_images():
    """Load images from test_uploads folder (faster with fewer images)"""
    global player_cache
    
    # Try test_uploads first, then fallback to uploads
    test_folder = "../test_uploads"
    main_folder = "../uploads"
    
    uploads_folder = test_folder if os.path.exists(test_folder) else main_folder
    
    if not os.path.exists(uploads_folder):
        os.makedirs(uploads_folder, exist_ok=True)
        print(f"📁 Created folder: {uploads_folder}")
        return 0
    
    # Get first 20 images only for testing
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.JPG', '*.JPEG', '*.PNG', '*.BMP']
    image_files = []
    
    for extension in image_extensions:
        image_files.extend(glob.glob(os.path.join(uploads_folder, extension)))
    
    # Limit to first 20 images for fast testing
    image_files = image_files[:20]
    
    print(f"📸 Testing with {len(image_files)} images from {uploads_folder}")
    
    loaded_count = 0
    for image_path in image_files:
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                print(f"⚠️  Failed to load: {os.path.basename(image_path)}")
                continue
            
            # Detect face
            face = face_processor.detect_face(image)
            if face is None:
                print(f"⚠️  No face detected: {os.path.basename(image_path)}")
                continue
            
            # Extract player name from filename
            filename = os.path.basename(image_path)
            player_name = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
            
            # Store in cache
            player_cache[player_name] = {
                'image': image,
                'face': face,
                'filename': filename,
                'path': image_path
            }
            
            loaded_count += 1
            print(f"✅ Loaded: {player_name} ({filename})")
            
        except Exception as e:
            print(f"❌ Error loading {os.path.basename(image_path)}: {e}")
    
    print(f"🎯 Successfully loaded {loaded_count}/{len(image_files)} images with faces detected")
    return loaded_count

def image_to_base64(image: np.ndarray) -> str:
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{image_base64}"

# Load test images on startup
print("🚀 Cricket Face Mashup API - TEST VERSION starting...")
print("📁 Loading small set of images for quick testing...")
loaded_images = load_test_images()

@app.get("/")
async def root():
    return {
        "message": "Cricket Face Mashup API - TEST VERSION is running!", 
        "players": len(player_cache),
        "auto_loaded": True,
        "test_mode": True,
        "status": "ready" if len(player_cache) >= 3 else "needs_more_images"
    }

@app.get("/players")
async def get_players():
    players = []
    for name, data in player_cache.items():
        players.append({
            'name': name,
            'filename': data['filename'],
            'image_url': f"/uploads/{data['filename']}",
            'face_detected': True
        })
    return {
        "players": players, 
        "total": len(players),
        "ready_to_play": len(players) >= 3,
        "test_mode": True
    }

@app.post("/create-mashup")
async def create_mashup(num_players: int = 3):
    try:
        if len(player_cache) < num_players:
            raise HTTPException(
                status_code=400, 
                detail=f"Need at least {num_players} players. Found {len(player_cache)}. Add more images to test_uploads folder."
            )
        
        selected_players = random.sample(list(player_cache.items()), num_players)
        base_name, base_data = selected_players[0]
        base_image = base_data['image'].copy()
        base_face = base_data['face']
        used_players = [base_name]
        
        face_parts = [
            (face_processor.eye_region, "eyes"),
            (face_processor.nose_region, "nose"),
            (face_processor.mouth_region, "mouth")
        ]
        
        for i, (part_region, part_name) in enumerate(face_parts):
            if i + 1 < len(selected_players):
                source_name, source_data = selected_players[i + 1]
                source_image = source_data['image']
                source_face = source_data['face']
                
                try:
                    source_part = face_processor.extract_face_part(source_image, source_face, part_region)
                    fx, fy, fw, fh = base_face
                    rx, ry, rw, rh = part_region
                    target_x = int(fx + fw * rx)
                    target_y = int(fy + fh * ry)
                    target_w = int(fw * rw)
                    target_h = int(fh * rh)
                    
                    resized_part = cv2.resize(source_part, (target_w, target_h))
                    base_image = face_processor.blend_parts(base_image, resized_part, (target_x, target_y))
                    
                    if source_name not in used_players:
                        used_players.append(source_name)
                        
                except Exception as e:
                    print(f"Could not blend {part_name}: {e}")
        
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
    try:
        all_player_names = list(player_cache.keys())
        correct_answer = " + ".join(sorted(correct_players))
        
        wrong_options = []
        attempts = 0
        while len(wrong_options) < total_options - 1 and attempts < 20:
            num_players = random.randint(2, 3)
            random_players = random.sample(all_player_names, min(num_players, len(all_player_names)))
            wrong_answer = " + ".join(sorted(random_players))
            
            if wrong_answer != correct_answer and wrong_answer not in wrong_options:
                wrong_options.append(wrong_answer)
            attempts += 1
        
        while len(wrong_options) < total_options - 1:
            random_player = random.choice(all_player_names)
            if random_player not in wrong_options and random_player != correct_answer:
                wrong_options.append(random_player)
        
        all_options = [correct_answer] + wrong_options[:total_options-1]
        random.shuffle(all_options)
        
        return {"success": True, "options": all_options, "correct_answer": correct_answer}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear-players")
async def clear_players():
    global player_cache
    player_cache = {}
    return {"success": True, "message": "All players cleared from memory"}

# Mount static files
try:
    # Try test_uploads first, then uploads
    if os.path.exists("../test_uploads"):
        app.mount("/uploads", StaticFiles(directory="../test_uploads"), name="uploads")
        print("📁 Mounted test_uploads directory")
    else:
        app.mount("/uploads", StaticFiles(directory="../uploads"), name="uploads")
        print("📁 Mounted uploads directory")
except Exception as e:
    print(f"⚠️  Could not mount directory: {e}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Cricket Face Mashup API - TEST VERSION...")
    print("🏏 Backend running on: http://localhost:8000")
    print("🔗 API docs available at: http://localhost:8000/docs")
    print("📁 Using test mode with limited images for fast testing")
    print("🎯 Test players loaded:", len(player_cache))
    uvicorn.run(app, host="0.0.0.0", port=8000)
