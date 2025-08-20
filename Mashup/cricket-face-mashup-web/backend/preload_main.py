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
        # OPTIMIZED 2-PLAYER BLENDING (REVERTED TO WORKING VERSION)
        # Get images from the 2 selected players
        img1 = selected[0]['cv_image']
        img2 = selected[1]['cv_image']
        
        # Get the face regions from the images
        face1_rect = selected[0]['face_rect']
        face2_rect = selected[1]['face_rect']
        
        if face1_rect is not None and face2_rect is not None:
            # Extract just the face regions
            x1, y1, w1, h1 = face1_rect
            x2, y2, w2, h2 = face2_rect
            
            # Add some padding around faces
            padding = 0.2  # 20% padding
            x1 = max(0, int(x1 - w1 * padding))
            y1 = max(0, int(y1 - h1 * padding))
            w1 = min(img1.shape[1] - x1, int(w1 * (1 + 2 * padding)))
            h1 = min(img1.shape[0] - y1, int(h1 * (1 + 2 * padding)))
            
            x2 = max(0, int(x2 - w2 * padding))
            y2 = max(0, int(y2 - h2 * padding))
            w2 = min(img2.shape[1] - x2, int(w2 * (1 + 2 * padding)))
            h2 = min(img2.shape[0] - y2, int(h2 * (1 + 2 * padding)))
            
            # Extract complete face regions
            face1 = img1[y1:y1+h1, x1:x1+w1]
            face2 = img2[y2:y2+h2, x2:x2+w2]
            print(f"🔍 Using complete face regions for vertical stack")
            
            # Save the complete faces
            output_dir = "../Output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save the complete faces that will be used for top and bottom
            cv2.imwrite(os.path.join(output_dir, "top.png"), cv2.convertScaleAbs(face2))  # face2 goes on top
            cv2.imwrite(os.path.join(output_dir, "bottom.png"), cv2.convertScaleAbs(face1))  # face1 goes on bottom
            print(f"✅ Saved complete faces to Output directory: top.png ({selected[1]['name']}) and bottom.png ({selected[0]['name']})")
            
            # Now resize the faces to target size
            target_size = (350, 350)
            img1 = cv2.resize(face1, target_size).astype(np.float32)
            img2 = cv2.resize(face2, target_size).astype(np.float32)
        else:
            # If face detection failed, resize whole images
            target_size = (350, 350)
            img1 = cv2.resize(img1, target_size).astype(np.float32)
            img2 = cv2.resize(img2, target_size).astype(np.float32)
            
            # Save resized whole images for verification (fallback case)
            output_dir = "../Output"
            os.makedirs(output_dir, exist_ok=True)
            cv2.imwrite(os.path.join(output_dir, "top.png"), cv2.convertScaleAbs(img2))  # img2 goes on top
            cv2.imwrite(os.path.join(output_dir, "bottom.png"), cv2.convertScaleAbs(img1))  # img1 goes on bottom
            print(f"✅ Saved resized images to Output directory (face detection failed): top.png ({selected[1]['name']}) and bottom.png ({selected[0]['name']})")
        
        print(f"🎮 Creating VERTICAL STACK: {selected[0]['name']} (top) + {selected[1]['name']} (bottom)")
        print(f"🔍 Image shapes - img1: {img1.shape}, img2: {img2.shape}")
        
        print("🔍 Creating vertical stack with complete faces")
        
        # Create a vertical gradient blend
        print("🔍 Creating vertical gradient blend between faces")
        
        # Create alpha mask for vertical blending
        height = target_size[1]
        width = target_size[0]
        alpha = np.zeros((height, width), dtype=np.float32)
        
        # Create vertical gradient (top to bottom)
        for i in range(height):
            alpha[i, :] = 1.0 - (i / (height - 1.0))
        
        # Make the transition more obvious in the middle
        blend_zone = 50  # pixels for transition
        mid_point = height // 2
        alpha[:mid_point - blend_zone] = 1.0
        alpha[mid_point + blend_zone:] = 0.0
        for i in range(blend_zone * 2):
            pos = mid_point - blend_zone + i
            if pos >= 0 and pos < height:
                alpha[pos, :] = 1.0 - (i / (blend_zone * 2.0))
        
        # Convert to 3-channel alpha
        alpha_3d = cv2.merge([alpha, alpha, alpha])
        
        # Blend images
        result = (img2 * alpha_3d + img1 * (1.0 - alpha_3d))
        print(f"🔍 TEST - Explicitly placing img2 ({selected[1]['name']}) on TOP and img1 ({selected[0]['name']}) on BOTTOM")
        
        print(f"🔍 Stacked result shape: {result.shape}")
        print(f"🔍 Top half: {selected[1]['name']}, Bottom half: {selected[0]['name']}")
        
        # Ensure values are in valid range and convert back to uint8
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        # Apply very light gaussian blur to smooth any remaining artifacts
        result = cv2.GaussianBlur(result, (5, 5), 0)
        
        # Convert result to base64
        mashup_base64 = image_to_base64(result)
        
        print(f"✅ Successfully created VERTICAL STACK mashup!")
        print(f"✅ Top: {selected[1]['name']}, Bottom: {selected[0]['name']}")
        
        return {
            "success": True,
            "mashup_image": mashup_base64,
            "used_players": [p['name'] for p in selected],
            "base_player": selected[0]['name'],
            "blend_status": "vertical_stack_with_face_alignment_success"
        }
        
    except Exception as e:
        print(f"❌ Error creating mashup: {e}")
        import traceback
        traceback.print_exc()
        
        # IMPROVED FALLBACK: Always create a blend, never return original image
        try:
            # Get images from the 2 selected players
            img1 = selected[0]['cv_image']
            img2 = selected[1]['cv_image']
            
            # Resize to standard size
            height, width = 350, 350
            img1 = cv2.resize(img1, (width, height)).astype(np.float32)
            img2 = cv2.resize(img2, (width, height)).astype(np.float32)
            
            # VERTICAL STACK as final fallback
            print("⚠️ Using VERTICAL STACK as final fallback")
            print(f"⚠️ Stacking {selected[0]['name']} (top) + {selected[1]['name']} (bottom)")
            
            # Create simple vertical stack without face alignment  
            gap_size = 10  # Small gap between images
            result_height = height * 2 + gap_size
            result = np.ones((result_height, width, 3), dtype=np.float32) * 255  # White background
            
            # TEST: Explicitly place img2 on top and img1 on bottom in fallback
            result[0:height, :, :] = img2  # img2 on top
            result[height + gap_size:height + gap_size + height, :, :] = img1  # img1 on bottom
            print(f"🔍 FALLBACK TEST - Explicitly placing img2 ({selected[1]['name']}) on TOP and img1 ({selected[0]['name']}) on BOTTOM")
            
            print(f"🔍 FALLBACK - Stacked result shape: {result.shape}")
            
            # Ensure values are in valid range and convert back to uint8
            result = np.clip(result, 0, 255).astype(np.uint8)
            
            # Apply light gaussian blur
            result = cv2.GaussianBlur(result, (5, 5), 0)
            
            # Convert result to base64
            mashup_base64 = image_to_base64(result)
            
            return {
                "success": True,
                "mashup_image": mashup_base64,
                "used_players": [p['name'] for p in selected],
                "base_player": selected[0]['name'],
                "blend_status": f"vertical_stack_fallback_after_error: {str(e)}"
            }
            
        except Exception as fallback_error:
            print(f"❌ Even fallback failed: {fallback_error}")
            # Only as absolute last resort, return an error response
            raise HTTPException(
                status_code=500,
                detail=f"Face mashup failed: {str(e)}. Fallback also failed: {str(fallback_error)}"
            )

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
