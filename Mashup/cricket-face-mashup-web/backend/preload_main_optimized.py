import cv2
import numpy as np
import os
import json
from tqdm import tqdm
import time

def preprocess_all_images():
    print("🚀 Starting bulk image preprocessing...")
    
    # Get all images from uploads directory
    upload_dir = "../uploads"
    all_images = [f for f in os.listdir(upload_dir) if f.endswith(('.png', '.jpg', '.PNG', '.JPG'))]
    
    # Create cache directory if not exists
    cache_dir = "../cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    # Load face cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Store all player data
    players_data = []
    
    print(f"📸 Found {len(all_images)} images to process")
    
    # Process each image
    for img_file in tqdm(all_images, desc="Processing images"):
        try:
            # Read image
            img_path = os.path.join(upload_dir, img_file)
            img = cv2.imread(img_path)
            
            if img is None:
                print(f"⚠️ Failed to load {img_file}")
                continue
                
            # Resize to standard size
            img = cv2.resize(img, (350, 350))
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect face
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                print(f"⚠️ No face detected in {img_file}")
                continue
                
            # Get the largest face
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            
            # Save processed data
            player_name = os.path.splitext(img_file)[0]
            cache_file = os.path.join(cache_dir, f"{player_name}.npz")
            
            # Save the processed image and face data
            np.savez_compressed(cache_file,
                image=img,
                face_rect=np.array([x, y, w, h]),
                name=player_name
            )
            
            # Add to players list
            players_data.append({
                'name': player_name,
                'image_file': img_file,
                'cache_file': f"{player_name}.npz",
                'face_rect': [int(x), int(y), int(w), int(h)]
            })
            
        except Exception as e:
            print(f"❌ Error processing {img_file}: {str(e)}")
    
    # Save players data
    with open(os.path.join(cache_dir, 'players_data.json'), 'w') as f:
        json.dump(players_data, f, indent=2)
    
    print(f"✅ Successfully preprocessed {len(players_data)} players!")
    print("💾 All data cached and ready for fast access")
    
    return len(players_data)

if __name__ == "__main__":
    start_time = time.time()
    num_processed = preprocess_all_images()
    end_time = time.time()
    print(f"⏱️ Total processing time: {end_time - start_time:.2f} seconds")
    print(f"⚡ Average time per image: {(end_time - start_time) / num_processed:.2f} seconds")