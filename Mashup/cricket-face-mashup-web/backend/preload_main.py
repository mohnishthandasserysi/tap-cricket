from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import base64
import random
from typing import List
import os
import glob
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

print("🚀 PRELOAD Cricket Face Mashup - 4 Test Images!")

class QuizRequest(BaseModel):
    correct_players: List[str]
    total_options: int = 4

# Simple face processor for blending
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
    
    def extract_face_region(self, image: np.ndarray, face_rect):
        """Extract the face region from image"""
        x, y, w, h = face_rect
        # Add some padding around the face
        padding = 0.1
        px = max(0, int(x - w * padding))
        py = max(0, int(y - h * padding))
        pw = min(image.shape[1] - px, int(w * (1 + 2 * padding)))
        ph = min(image.shape[0] - py, int(h * (1 + 2 * padding)))
        
        return image[py:py+ph, px:px+pw], (px, py, pw, ph)
    
    def blend_faces_seamlessly(self, base_image: np.ndarray, face_images: list, face_positions: list):
        """Blend multiple faces into base image using weighted averaging"""
        result = base_image.copy()
        
        if len(face_images) < 2:
            return result
            
        # Find the largest face to use as reference
        areas = [pos[2] * pos[3] for pos in face_positions]
        main_idx = areas.index(max(areas))
        main_pos = face_positions[main_idx]
        
        # Resize all faces to match the main face size
        target_size = (main_pos[2], main_pos[3])
        resized_faces = []
        
        for face_img in face_images:
            if face_img.size > 0:
                resized_face = cv2.resize(face_img, target_size)
                resized_faces.append(resized_face)
        
        if len(resized_faces) < 2:
            return result
            
        # Create blended face using weighted average
        if len(resized_faces) == 2:
            blended_face = cv2.addWeighted(resized_faces[0], 0.6, resized_faces[1], 0.4, 0)
        else:
            # For 3+ faces, blend progressively
            blended_face = cv2.addWeighted(resized_faces[0], 0.5, resized_faces[1], 0.5, 0)
            for i in range(2, len(resized_faces)):
                weight = 1.0 / (i + 1)
                blended_face = cv2.addWeighted(blended_face, 1 - weight, resized_faces[i], weight, 0)
        
        # Create smooth blending mask
        mask = np.zeros(target_size[::-1], dtype=np.uint8)
        center = (target_size[0]//2, target_size[1]//2)
        axes = (target_size[0]//3, target_size[1]//3)
        cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
        mask = cv2.GaussianBlur(mask, (21, 21), 0)
        mask_3d = cv2.merge([mask, mask, mask]) / 255.0
        
        # Place blended face in result image
        x, y, w, h = main_pos
        if x + w <= result.shape[1] and y + h <= result.shape[0]:
            base_region = result[y:y+h, x:x+w]
            blended_region = (blended_face * mask_3d + base_region * (1 - mask_3d)).astype(np.uint8)
            result[y:y+h, x:x+w] = blended_region
        
        return result

app = FastAPI()

# Global face processor instance
face_processor = SimpleFaceProcessor()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pre-loaded players from test_uploads
players_db = []

def preload_test_images():
    """Load the 4 images from test_uploads folder automatically"""
    global players_db
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
    
    loaded_count = 0
    for image_path in image_files:
        try:
            # Read image file as base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Convert to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Load image as numpy array for blending
            nparr = np.frombuffer(image_data, np.uint8)
            cv_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Detect face for blending
            face_rect = face_processor.detect_face(cv_image)
            
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
            
            data_url = f"data:{content_type};base64,{image_base64}"
            
            # Extract player name from filename
            filename = os.path.basename(image_path)
            player_name = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
            
            player = {
                'name': player_name,
                'filename': filename,
                'image_url': data_url,
                'cv_image': cv_image,  # Raw OpenCV image for blending
                'face_rect': face_rect,  # Detected face coordinates
                'face_detected': face_rect is not None
            }
            
            players_db.append(player)
            loaded_count += 1
            print(f"✅ Preloaded: {player_name} ({filename})")
            
        except Exception as e:
            print(f"❌ Error loading {os.path.basename(image_path)}: {e}")
    
    print(f"🎯 Successfully preloaded {loaded_count} players!")
    return loaded_count

# Preload images on startup
loaded_count = preload_test_images()

@app.get("/")
async def root():
    return {
        "message": "Cricket Face Mashup PRELOAD API is running!", 
        "players": len(players_db),
        "status": "ready" if len(players_db) >= 3 else "need_more_players",
        "mode": "preloaded",
        "preloaded_count": loaded_count
    }

@app.get("/players")
async def get_players():
    # Return only JSON-serializable data (exclude cv_image and face_rect)
    serializable_players = []
    for player in players_db:
        serializable_player = {
            'name': player['name'],
            'filename': player['filename'],
            'image_url': player['image_url'],
            'face_detected': player['face_detected']
        }
        serializable_players.append(serializable_player)
    
    return {
        "players": serializable_players,
        "total": len(players_db),
        "ready_to_play": len(players_db) >= 3,
        "preloaded": True
    }

def image_to_base64(image: np.ndarray) -> str:
    """Convert OpenCV image to base64 string"""
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{image_base64}"

@app.post("/create-mashup")
async def create_mashup():
    if len(players_db) < 2:
        raise HTTPException(status_code=400, detail=f"Need at least 2 players. Found {len(players_db)} preloaded.")
    
    # Pick 2 random players from preloaded set for cleaner blending
    selected = random.sample(players_db, 2)
    
    print(f"🎮 Creating mashup with: {[p['name'] for p in selected]}")
    
    try:
        # OPTIMIZED 2-PLAYER BLENDING
        # Get images from the 2 selected players
        img1 = selected[0]['cv_image']
        img2 = selected[1]['cv_image']
        
        # Resize all images to a smaller, more manageable size
        height, width = 350, 350  # Smaller size for better user experience
        img1 = cv2.resize(img1, (width, height)).astype(np.float32)
        img2 = cv2.resize(img2, (width, height)).astype(np.float32)
        
        # RELIABLE HORIZONTAL GRADIENT BLENDING
        # Guaranteed to show both faces clearly
        
        print(f"🔄 Creating gradient blend between {selected[0]['name']} and {selected[1]['name']}")
        
        # Create horizontal gradient from left to right
        # Left side = Player 1, Right side = Player 2, Smooth transition in middle
        
        gradient_mask = np.zeros((height, width), dtype=np.float32)
        
        for x in range(width):
            # Create smooth S-curve transition
            progress = x / (width - 1)  # 0 to 1 from left to right
            
            # Smooth S-curve for natural transition
            if progress < 0.3:
                alpha = 0.0  # Pure Player 1 on left
            elif progress > 0.7:
                alpha = 1.0  # Pure Player 2 on right
            else:
                # Smooth transition in middle 40%
                normalized = (progress - 0.3) / 0.4  # 0 to 1 in transition zone
                alpha = 3 * normalized**2 - 2 * normalized**3  # Smooth S-curve
            
            gradient_mask[:, x] = alpha
        
        # Convert to 3-channel mask
        gradient_mask_3d = cv2.merge([gradient_mask, gradient_mask, gradient_mask])
        
        # Apply the gradient blending
        result = img1 * (1 - gradient_mask_3d) + img2 * gradient_mask_3d
        
        print(f"✅ Gradient blend: {selected[0]['name']} (left) → {selected[1]['name']} (right)")
        
        # CLEAN UP: Remove background and focus on face
        face1_rect = selected[0]['face_rect']
        face2_rect = selected[1]['face_rect']
        
        if face1_rect is not None:
            x1, y1, w1, h1 = face1_rect
            
            # Create a clean face mask with expanded region
            face_mask = np.zeros((height, width), dtype=np.float32)
            
            # Expand face region by 20% for natural look
            padding = 0.2
            expanded_x = max(0, int(x1 - w1 * padding))
            expanded_y = max(0, int(y1 - h1 * padding))
            expanded_w = min(width - expanded_x, int(w1 * (1 + 2 * padding)))
            expanded_h = min(height - expanded_y, int(h1 * (1 + 2 * padding)))
            
            # Create oval face mask
            center_x = expanded_x + expanded_w // 2
            center_y = expanded_y + expanded_h // 2
            
            for i in range(height):
                for j in range(width):
                    # Calculate distance from face center
                    dx = (j - center_x) / (expanded_w / 2)
                    dy = (i - center_y) / (expanded_h / 2)
                    dist = np.sqrt(dx*dx + dy*dy)
                    
                    # Create smooth oval mask
                    if dist <= 1.0:
                        face_mask[i, j] = 1.0
                    elif dist <= 1.3:
                        # Smooth falloff
                        face_mask[i, j] = max(0, 1.0 - (dist - 1.0) / 0.3)
            
            # Apply heavy blur to mask for very smooth edges
            face_mask = cv2.GaussianBlur(face_mask, (21, 21), 0)
            face_mask_3d = cv2.merge([face_mask, face_mask, face_mask])
            
            # Create clean background (neutral gray)
            clean_background = np.full((height, width, 3), [240, 240, 240], dtype=np.float32)
            
            # Combine face with clean background
            result = result * face_mask_3d + clean_background * (1 - face_mask_3d)
            
            print(f"🧹 Applied clean background and face isolation")
        
        # Ensure values are in valid range and convert back to uint8
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        # Apply light smoothing for professional finish
        result = cv2.GaussianBlur(result, (3, 3), 0)
        
        # Convert result to base64
        mashup_base64 = image_to_base64(result)
        
        print(f"✅ Successfully created clean 2-player gradient blend mashup!")
        
        return {
            "success": True,
            "mashup_image": mashup_base64,
            "used_players": [p['name'] for p in selected],
            "base_player": selected[0]['name'],
            "blend_status": "clean_gradient_blend_success"
        }
        
    except Exception as e:
        print(f"❌ Error creating mashup: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to first player's image
        return {
            "success": True,
            "mashup_image": selected[0]['image_url'],
            "used_players": [selected[0]['name']],
            "base_player": selected[0]['name'],
            "blend_status": f"error_fallback: {str(e)}"
        }

@app.post("/generate-quiz")
async def generate_quiz(request: QuizRequest):
    all_names = [p['name'] for p in players_db]
    correct_answer = " + ".join(sorted(request.correct_players))
    
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

# No upload or clear endpoints needed - everything is preloaded!

if __name__ == "__main__":
    import uvicorn
    print("⚡ PRELOAD Cricket Face Mashup API - 4 Test Images Ready!")
    print("🌐 Starting on: http://localhost:8001")
    print("📁 NO UPLOAD NEEDED - Images already loaded!")
    print(f"🎮 Ready to play with {len(players_db)} preloaded players!")
    uvicorn.run(app, host="0.0.0.0", port=8001)
