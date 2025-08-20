import cv2
import dlib
import numpy as np
import os
import random
from typing import List, Tuple, Optional
import requests


class FaceProcessor:
    def __init__(self, predictor_path: str = "models/shape_predictor_68_face_landmarks.dat"):
        """Initialize the face processor with dlib models."""
        self.detector = dlib.get_frontal_face_detector()
        self.predictor_path = predictor_path
        
        # Download predictor if not exists
        if not os.path.exists(predictor_path):
            self.download_landmark_model()
        
        self.predictor = dlib.shape_predictor(predictor_path)
        
        # Landmark indexes for different face parts
        self.EYES_POINTS = list(range(36, 48))  # 36-47
        self.NOSE_POINTS = list(range(27, 36))  # 27-35
        self.MOUTH_POINTS = list(range(48, 68))  # 48-67
        
    def download_landmark_model(self):
        """Download the dlib 68-point landmark model."""
        print("Downloading dlib 68-point landmark model...")
        url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
        
        # Create models directory if it doesn't exist
        os.makedirs("models", exist_ok=True)
        
        try:
            # Download the compressed file
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            compressed_path = "models/shape_predictor_68_face_landmarks.dat.bz2"
            with open(compressed_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract the compressed file
            import bz2
            with bz2.BZ2File(compressed_path, 'rb') as f_in:
                with open(self.predictor_path, 'wb') as f_out:
                    f_out.write(f_in.read())
            
            # Remove compressed file
            os.remove(compressed_path)
            print("✅ Landmark model downloaded successfully!")
            
        except Exception as e:
            print(f"❌ Error downloading landmark model: {e}")
            print("Please download manually from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
            raise
    
    def detect_landmarks(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Detect facial landmarks in an image."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)
        
        if len(faces) == 0:
            return None
        
        # Use the largest face if multiple faces detected
        face = max(faces, key=lambda rect: rect.width() * rect.height())
        landmarks = self.predictor(gray, face)
        
        # Convert to numpy array
        points = np.array([[p.x, p.y] for p in landmarks.parts()])
        return points
    
    def get_face_part_region(self, image: np.ndarray, landmarks: np.ndarray, 
                           part_points: List[int], padding: int = 10) -> Tuple[np.ndarray, np.ndarray]:
        """Extract a specific face part region with padding."""
        if landmarks is None:
            raise ValueError("No landmarks detected")
        
        # Get points for the specific face part
        part_landmarks = landmarks[part_points]
        
        # Calculate bounding box with padding
        x_min = max(0, np.min(part_landmarks[:, 0]) - padding)
        x_max = min(image.shape[1], np.max(part_landmarks[:, 0]) + padding)
        y_min = max(0, np.min(part_landmarks[:, 1]) - padding)
        y_max = min(image.shape[0], np.max(part_landmarks[:, 1]) + padding)
        
        # Extract region
        region = image[y_min:y_max, x_min:x_max]
        
        # Adjust landmark coordinates relative to the extracted region
        adjusted_landmarks = part_landmarks.copy()
        adjusted_landmarks[:, 0] -= x_min
        adjusted_landmarks[:, 1] -= y_min
        
        return region, adjusted_landmarks
    
    def create_mask_from_landmarks(self, shape: Tuple[int, int], landmarks: np.ndarray) -> np.ndarray:
        """Create a mask from landmark points."""
        mask = np.zeros(shape[:2], dtype=np.uint8)
        hull = cv2.convexHull(landmarks)
        cv2.fillPoly(mask, [hull], 255)
        return mask
    
    def resize_and_align_part(self, source_region: np.ndarray, source_landmarks: np.ndarray,
                            target_landmarks: np.ndarray, target_shape: Tuple[int, int]) -> Tuple[np.ndarray, np.ndarray]:
        """Resize and align a face part to match target dimensions."""
        # Calculate transformation matrix
        source_center = np.mean(source_landmarks, axis=0)
        target_center = np.mean(target_landmarks, axis=0)
        
        # Calculate scale factor
        source_size = np.linalg.norm(np.max(source_landmarks, axis=0) - np.min(source_landmarks, axis=0))
        target_size = np.linalg.norm(np.max(target_landmarks, axis=0) - np.min(target_landmarks, axis=0))
        scale = target_size / source_size if source_size > 0 else 1.0
        
        # Create transformation matrix
        M = cv2.getRotationMatrix2D(tuple(source_center), 0, scale)
        M[0, 2] += target_center[0] - source_center[0]
        M[1, 2] += target_center[1] - source_center[1]
        
        # Apply transformation
        transformed_region = cv2.warpAffine(source_region, M, (target_shape[1], target_shape[0]))
        transformed_landmarks = cv2.transform(source_landmarks.reshape(-1, 1, 2), M).reshape(-1, 2)
        
        return transformed_region, transformed_landmarks
    
    def blend_face_part(self, base_image: np.ndarray, part_image: np.ndarray, 
                       part_landmarks: np.ndarray, blend_type: str = 'seamless') -> np.ndarray:
        """Blend a face part onto the base image."""
        try:
            if blend_type == 'seamless':
                # Create mask for seamless cloning
                mask = self.create_mask_from_landmarks(part_image.shape, part_landmarks)
                
                # Calculate center for seamless cloning
                center = tuple(map(int, np.mean(part_landmarks, axis=0)))
                
                # Ensure center is within bounds
                center = (
                    max(mask.shape[1]//2, min(base_image.shape[1] - mask.shape[1]//2, center[0])),
                    max(mask.shape[0]//2, min(base_image.shape[0] - mask.shape[0]//2, center[1]))
                )
                
                # Perform seamless cloning
                result = cv2.seamlessClone(part_image, base_image, mask, center, cv2.NORMAL_CLONE)
                return result
            else:
                # Simple alpha blending
                mask = self.create_mask_from_landmarks(base_image.shape, part_landmarks)
                mask_3channel = cv2.merge([mask, mask, mask]) / 255.0
                
                result = base_image.copy()
                overlay_region = part_image * mask_3channel + base_image * (1 - mask_3channel)
                result[mask > 0] = overlay_region[mask > 0]
                return result.astype(np.uint8)
                
        except Exception as e:
            print(f"Warning: Blending failed ({e}), using simple overlay")
            # Fallback to simple overlay
            result = base_image.copy()
            mask = self.create_mask_from_landmarks(base_image.shape, part_landmarks)
            result[mask > 0] = part_image[mask > 0]
            return result


class MashupGenerator:
    def __init__(self, players_folder: str = "players"):
        """Initialize the mashup generator."""
        self.players_folder = players_folder
        self.face_processor = FaceProcessor()
        
    def load_player_images(self) -> List[Tuple[str, np.ndarray]]:
        """Load all player images from the players folder."""
        images = []
        
        if not os.path.exists(self.players_folder):
            raise FileNotFoundError(f"Players folder '{self.players_folder}' not found!")
        
        for filename in os.listdir(self.players_folder):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                filepath = os.path.join(self.players_folder, filename)
                image = cv2.imread(filepath)
                if image is not None:
                    # Get player name from filename
                    player_name = os.path.splitext(filename)[0].replace('_', ' ').title()
                    images.append((player_name, image))
        
        return images
    
    def create_mashup(self, num_players: int = 3) -> Tuple[np.ndarray, List[str]]:
        """Create a face mashup from random players."""
        player_images = self.load_player_images()
        
        if len(player_images) < num_players:
            raise ValueError(f"Need at least {num_players} player images, found {len(player_images)}")
        
        # Randomly select players
        selected_players = random.sample(player_images, num_players)
        player_names = [name for name, _ in selected_players]
        
        # Use first player as base
        base_name, base_image = selected_players[0]
        base_landmarks = self.face_processor.detect_landmarks(base_image)
        
        if base_landmarks is None:
            raise ValueError(f"Could not detect face in base image: {base_name}")
        
        result_image = base_image.copy()
        used_players = [base_name]
        
        # Define face parts to blend
        face_parts = [
            (self.face_processor.EYES_POINTS, "eyes"),
            (self.face_processor.NOSE_POINTS, "nose"),
            (self.face_processor.MOUTH_POINTS, "mouth")
        ]
        
        # Randomly assign different face parts from different players
        for i, (part_points, part_name) in enumerate(face_parts):
            if i + 1 < len(selected_players):
                source_name, source_image = selected_players[i + 1]
                source_landmarks = self.face_processor.detect_landmarks(source_image)
                
                if source_landmarks is not None:
                    try:
                        # Extract face part from source
                        source_region, source_part_landmarks = self.face_processor.get_face_part_region(
                            source_image, source_landmarks, part_points
                        )
                        
                        # Get target landmarks for alignment
                        target_part_landmarks = base_landmarks[part_points]
                        
                        # Resize and align the part
                        aligned_region, aligned_landmarks = self.face_processor.resize_and_align_part(
                            source_region, source_part_landmarks, target_part_landmarks, result_image.shape
                        )
                        
                        # Blend the part onto result image
                        result_image = self.face_processor.blend_face_part(
                            result_image, aligned_region, aligned_landmarks
                        )
                        
                        if source_name not in used_players:
                            used_players.append(source_name)
                            
                    except Exception as e:
                        print(f"Warning: Could not blend {part_name} from {source_name}: {e}")
        
        return result_image, used_players
    
    def generate_quiz_options(self, correct_players: List[str], total_options: int = 4) -> List[str]:
        """Generate quiz options including correct and incorrect answers."""
        player_images = self.load_player_images()
        all_player_names = [name for name, _ in player_images]
        
        # Create correct answer string
        correct_answer = " + ".join(sorted(correct_players))
        
        # Generate wrong options
        wrong_options = []
        for _ in range(total_options - 1):
            # Create random combinations
            num_players = random.randint(2, 3)
            random_players = random.sample(all_player_names, num_players)
            wrong_answer = " + ".join(sorted(random_players))
            
            # Ensure it's different from correct answer and not already added
            if wrong_answer != correct_answer and wrong_answer not in wrong_options:
                wrong_options.append(wrong_answer)
        
        # If we don't have enough unique wrong options, pad with single names
        while len(wrong_options) < total_options - 1:
            random_player = random.choice(all_player_names)
            if random_player not in wrong_options and random_player != correct_answer:
                wrong_options.append(random_player)
        
        # Combine and shuffle
        all_options = [correct_answer] + wrong_options[:total_options-1]
        random.shuffle(all_options)
        
        return all_options, correct_answer


def test_face_processing():
    """Test function for face processing capabilities."""
    try:
        processor = FaceProcessor()
        print("✅ Face processor initialized successfully!")
        
        mashup_gen = MashupGenerator()
        print("✅ Mashup generator initialized successfully!")
        
        # Test loading images
        players = mashup_gen.load_player_images()
        print(f"✅ Loaded {len(players)} player images")
        
        if len(players) >= 3:
            # Test creating a mashup
            mashup, used_players = mashup_gen.create_mashup()
            print(f"✅ Created mashup using: {', '.join(used_players)}")
            
            # Test generating quiz options
            options, correct = mashup_gen.generate_quiz_options(used_players)
            print(f"✅ Generated quiz options: {options}")
            print(f"✅ Correct answer: {correct}")
        else:
            print("⚠️  Need at least 3 player images to test mashup creation")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_face_processing()
