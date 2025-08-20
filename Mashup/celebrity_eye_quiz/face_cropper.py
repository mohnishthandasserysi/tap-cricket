import cv2
import mediapipe as mp
import numpy as np
from PIL import Image


class FaceCropper:
    def __init__(self):
        """Initialize the FaceCropper with Mediapipe FaceMesh."""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
        
        # Define eye landmark indexes as specified
        self.left_eye_landmarks = [33, 133, 160, 159, 158, 157, 173]
        self.right_eye_landmarks = [362, 263, 387, 386, 385, 384, 398]
    
    def get_eye_bounding_box(self, landmarks, image_width, image_height):
        """
        Calculate bounding box for both eyes combined.
        
        Args:
            landmarks: Mediapipe face landmarks
            image_width: Width of the image
            image_height: Height of the image
            
        Returns:
            tuple: (x_min, y_min, x_max, y_max) bounding box coordinates
        """
        # Get all eye landmark points
        all_eye_points = []
        
        # Add left eye points
        for idx in self.left_eye_landmarks:
            landmark = landmarks.landmark[idx]
            x = int(landmark.x * image_width)
            y = int(landmark.y * image_height)
            all_eye_points.append((x, y))
        
        # Add right eye points
        for idx in self.right_eye_landmarks:
            landmark = landmarks.landmark[idx]
            x = int(landmark.x * image_width)
            y = int(landmark.y * image_height)
            all_eye_points.append((x, y))
        
        # Calculate bounding box
        x_coords = [point[0] for point in all_eye_points]
        y_coords = [point[1] for point in all_eye_points]
        
        x_min = min(x_coords)
        x_max = max(x_coords)
        y_min = min(y_coords)
        y_max = max(y_coords)
        
        # Add padding to include eyebrows and area just above nose
        padding_x = int((x_max - x_min) * 0.2)
        padding_y_top = int((y_max - y_min) * 0.5)  # More padding on top for eyebrows
        padding_y_bottom = int((y_max - y_min) * 0.3)  # Less padding on bottom
        
        x_min = max(0, x_min - padding_x)
        x_max = min(image_width, x_max + padding_x)
        y_min = max(0, y_min - padding_y_top)
        y_max = min(image_height, y_max + padding_y_bottom)
        
        return x_min, y_min, x_max, y_max
    
    def crop_eyes_from_image(self, image_path):
        """
        Crop the eye region from a celebrity image.
        
        Args:
            image_path: Path to the celebrity image
            
        Returns:
            PIL Image or None: Cropped eye region image, None if face not detected
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                print(f"Error: Could not load image from {image_path}")
                return None
            
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image_height, image_width = image_rgb.shape[:2]
            
            # Process image with FaceMesh
            results = self.face_mesh.process(image_rgb)
            
            if not results.multi_face_landmarks:
                print(f"No face detected in {image_path}")
                return None
            
            # Get the first (and should be only) face landmarks
            face_landmarks = results.multi_face_landmarks[0]
            
            # Get eye bounding box
            x_min, y_min, x_max, y_max = self.get_eye_bounding_box(
                face_landmarks, image_width, image_height
            )
            
            # Crop the eye region
            cropped_eyes = image_rgb[y_min:y_max, x_min:x_max]
            
            # Convert to PIL Image
            pil_image = Image.fromarray(cropped_eyes)
            
            return pil_image
            
        except Exception as e:
            print(f"Error processing image {image_path}: {str(e)}")
            return None
    
    def crop_eyes_from_pil_image(self, pil_image):
        """
        Crop the eye region from a PIL Image.
        
        Args:
            pil_image: PIL Image object
            
        Returns:
            PIL Image or None: Cropped eye region image, None if face not detected
        """
        try:
            # Convert PIL to numpy array
            image_rgb = np.array(pil_image)
            image_height, image_width = image_rgb.shape[:2]
            
            # Process image with FaceMesh
            results = self.face_mesh.process(image_rgb)
            
            if not results.multi_face_landmarks:
                print("No face detected in the provided image")
                return None
            
            # Get the first (and should be only) face landmarks
            face_landmarks = results.multi_face_landmarks[0]
            
            # Get eye bounding box
            x_min, y_min, x_max, y_max = self.get_eye_bounding_box(
                face_landmarks, image_width, image_height
            )
            
            # Crop the eye region
            cropped_eyes = image_rgb[y_min:y_max, x_min:x_max]
            
            # Convert to PIL Image
            pil_image = Image.fromarray(cropped_eyes)
            
            return pil_image
            
        except Exception as e:
            print(f"Error processing PIL image: {str(e)}")
            return None


def test_face_cropper():
    """Test function for the FaceCropper class."""
    cropper = FaceCropper()
    
    # Test with a sample image (you can uncomment and modify path for testing)
    # result = cropper.crop_eyes_from_image("images/sample.jpg")
    # if result:
    #     result.show()
    #     print("Eye cropping successful!")
    # else:
    #     print("Eye cropping failed!")
    
    print("FaceCropper initialized successfully!")


if __name__ == "__main__":
    test_face_cropper()
