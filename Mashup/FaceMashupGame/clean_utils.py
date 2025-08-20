import cv2
import numpy as np
import os
import random
import warnings
from typing import List, Tuple, Optional


# Suppress libpng warnings about sRGB profiles
warnings.filterwarnings("ignore", category=UserWarning)
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'


class CleanFaceProcessor:
    def __init__(self):
        """Initialize the face processor with OpenCV's built-in face detection."""
        # Load OpenCV's pre-trained face cascade
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Define approximate regions as percentages of face rectangle
        # These are rough estimates without precise landmark detection
        self.eye_region = (0.15, 0.25, 0.7, 0.4)    # x%, y%, w%, h% of face
        self.nose_region = (0.3, 0.4, 0.4, 0.3)     # x%, y%, w%, h% of face  
        self.mouth_region = (0.25, 0.65, 0.5, 0.25) # x%, y%, w%, h% of face
        
    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect the largest face in an image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return None
        
        # Return the largest face
        largest_face = max(faces, key=lambda face: face[2] * face[3])
        return tuple(largest_face)
    
    def extract_face_part(self, image: np.ndarray, face_rect: Tuple[int, int, int, int], 
                         part_region: Tuple[float, float, float, float]) -> np.ndarray:
        """Extract a face part based on region percentages."""
        fx, fy, fw, fh = face_rect
        rx, ry, rw, rh = part_region
        
        # Calculate actual coordinates
        x = int(fx + fw * rx)
        y = int(fy + fh * ry)  
        w = int(fw * rw)
        h = int(fh * rh)
        
        # Ensure coordinates are within image bounds
        x = max(0, min(x, image.shape[1] - w))
        y = max(0, min(y, image.shape[0] - h))
        w = min(w, image.shape[1] - x)
        h = min(h, image.shape[0] - y)
        
        return image[y:y+h, x:x+w]
    
    def resize_to_match(self, source_part: np.ndarray, target_size: Tuple[int, int]) -> np.ndarray:
        """Resize a face part to match target dimensions."""
        return cv2.resize(source_part, target_size)
    
    def create_simple_mask(self, shape: Tuple[int, int]) -> np.ndarray:
        """Create a simple elliptical mask for blending."""
        mask = np.zeros(shape, dtype=np.uint8)
        center = (shape[1]//2, shape[0]//2)
        axes = (shape[1]//3, shape[0]//3)
        cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
        
        # Apply Gaussian blur for smoother edges
        mask = cv2.GaussianBlur(mask, (15, 15), 0)
        return mask
    
    def blend_parts(self, base_image: np.ndarray, overlay_part: np.ndarray, 
                   position: Tuple[int, int]) -> np.ndarray:
        """Blend a face part onto the base image."""
        x, y = position
        h, w = overlay_part.shape[:2]
        
        # Ensure overlay fits within base image
        if x + w > base_image.shape[1] or y + h > base_image.shape[0]:
            return base_image
        
        # Create mask for smooth blending
        mask = self.create_simple_mask((h, w))
        mask_3d = cv2.merge([mask, mask, mask]) / 255.0
        
        # Extract the region to blend
        base_region = base_image[y:y+h, x:x+w]
        
        # Blend using alpha compositing
        blended_region = overlay_part * mask_3d + base_region * (1 - mask_3d)
        
        # Apply blended region back to base image
        result = base_image.copy()
        result[y:y+h, x:x+w] = blended_region.astype(np.uint8)
        
        return result


def safe_imread(filepath: str) -> Optional[np.ndarray]:
    """Safely read an image file, suppressing PNG warnings."""
    try:
        # Temporarily redirect stderr to suppress libpng warnings
        import sys
        from io import StringIO
        
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        
        # Read the image
        image = cv2.imread(filepath)
        
        # Restore stderr
        sys.stderr = old_stderr
        
        return image
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


class CleanMashupGenerator:
    def __init__(self, players_folder: str = "players"):
        """Initialize the clean mashup generator."""
        self.players_folder = players_folder
        self.face_processor = CleanFaceProcessor()
        
    def load_player_images(self) -> List[Tuple[str, np.ndarray]]:
        """Load all player images from the players folder."""
        images = []
        
        if not os.path.exists(self.players_folder):
            raise FileNotFoundError(f"Players folder '{self.players_folder}' not found!")
        
        print("📸 Loading player images...")
        for filename in os.listdir(self.players_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                filepath = os.path.join(self.players_folder, filename)
                
                # Use safe imread to suppress warnings
                image = safe_imread(filepath)
                
                if image is not None:
                    # Get player name from filename
                    player_name = os.path.splitext(filename)[0].replace('_', ' ').title()
                    images.append((player_name, image))
                    print(f"  ✅ Loaded: {player_name}")
                else:
                    print(f"  ❌ Failed to load: {filename}")
        
        print(f"📊 Total loaded: {len(images)} players")
        return images
    
    def create_simple_mashup(self, num_players: int = 3) -> Tuple[np.ndarray, List[str]]:
        """Create a simple face mashup."""
        player_images = self.load_player_images()
        
        if len(player_images) < num_players:
            raise ValueError(f"Need at least {num_players} player images, found {len(player_images)}")
        
        # Randomly select players
        selected_players = random.sample(player_images, num_players)
        
        # Use first player as base
        base_name, base_image = selected_players[0]
        base_face = self.face_processor.detect_face(base_image)
        
        if base_face is None:
            raise ValueError(f"Could not detect face in base image: {base_name}")
        
        result_image = base_image.copy()
        used_players = [base_name]
        
        print(f"🎭 Creating mashup with base: {base_name}")
        
        # Define face parts to blend
        face_parts = [
            (self.face_processor.eye_region, "eyes"),
            (self.face_processor.nose_region, "nose"), 
            (self.face_processor.mouth_region, "mouth")
        ]
        
        # Try to blend different parts from different players
        for i, (part_region, part_name) in enumerate(face_parts):
            if i + 1 < len(selected_players):
                source_name, source_image = selected_players[i + 1]
                source_face = self.face_processor.detect_face(source_image)
                
                if source_face is not None:
                    try:
                        # Extract part from source
                        source_part = self.face_processor.extract_face_part(
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
                        resized_part = self.face_processor.resize_to_match(
                            source_part, (target_w, target_h)
                        )
                        
                        # Blend onto result
                        result_image = self.face_processor.blend_parts(
                            result_image, resized_part, (target_x, target_y)
                        )
                        
                        if source_name not in used_players:
                            used_players.append(source_name)
                        
                        print(f"  ✅ Added {part_name} from {source_name}")
                            
                    except Exception as e:
                        print(f"  ⚠️ Could not blend {part_name} from {source_name}: {e}")
                else:
                    print(f"  ⚠️ No face detected in {source_name}")
        
        return result_image, used_players
    
    def generate_quiz_options(self, correct_players: List[str], total_options: int = 4) -> Tuple[List[str], str]:
        """Generate quiz options including correct and incorrect answers."""
        player_images = self.load_player_images()
        all_player_names = [name for name, _ in player_images]
        
        # Create correct answer string
        correct_answer = " + ".join(sorted(correct_players))
        
        # Generate wrong options
        wrong_options = []
        attempts = 0
        while len(wrong_options) < total_options - 1 and attempts < 20:
            # Create random combinations
            num_players = random.randint(2, 3)
            random_players = random.sample(all_player_names, min(num_players, len(all_player_names)))
            wrong_answer = " + ".join(sorted(random_players))
            
            # Ensure it's different from correct answer and not already added
            if wrong_answer != correct_answer and wrong_answer not in wrong_options:
                wrong_options.append(wrong_answer)
            attempts += 1
        
        # If we don't have enough unique wrong options, pad with single names
        while len(wrong_options) < total_options - 1:
            random_player = random.choice(all_player_names)
            if random_player not in wrong_options and random_player != correct_answer:
                wrong_options.append(random_player)
        
        # Combine and shuffle
        all_options = [correct_answer] + wrong_options[:total_options-1]
        random.shuffle(all_options)
        
        return all_options, correct_answer


def test_clean_face_processing():
    """Test function for clean face processing."""
    try:
        print("🧪 Testing Clean Face Processor...")
        processor = CleanFaceProcessor()
        print("✅ Clean face processor initialized successfully!")
        
        mashup_gen = CleanMashupGenerator()
        print("✅ Clean mashup generator initialized successfully!")
        
        # Test loading images
        players = mashup_gen.load_player_images()
        
        if len(players) >= 3:
            # Test creating a mashup
            print("\n🎭 Testing mashup creation...")
            mashup, used_players = mashup_gen.create_simple_mashup()
            print(f"✅ Created mashup using: {', '.join(used_players)}")
            
            # Test generating quiz options
            options, correct = mashup_gen.generate_quiz_options(used_players)
            print(f"✅ Generated quiz options: {len(options)} options")
            print(f"✅ Correct answer: {correct}")
            
            print("\n🎯 Ready to play! No more warnings!")
        else:
            print("⚠️  Need at least 3 player images to test mashup creation")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_clean_face_processing()
