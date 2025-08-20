import cv2
import numpy as np
import json
import os
from typing import Tuple, Optional

class HorizontalFaceMashup:
    def __init__(self, config_path: str = "mashup_config.json"):
        """Initialize the horizontal face mashup processor with configuration."""
        self.config = self._load_config(config_path)
        self._setup_face_cascade()
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Config file {config_path} not found, using defaults")
            return self._get_default_config()
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON in {config_path}, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """Return default configuration if config file is missing/invalid."""
        return {
            "transition": {
                "start_y_ratio": 0.0,
                "end_y_ratio": 0.5,
                "blend_zone_ratio": 0.1,
                "smoothness": 0.8
            },
            "processing": {
                "target_size": [350, 350],
                "gaussian_blur_kernel": [5, 5],
                "canny_edge_low": 50,
                "canny_edge_high": 150,
                "background_white_threshold": 200
            },
            "output": {
                "save_debug_images": True,
                "debug_output_dir": "../Output/debug"
            }
        }
    
    def _setup_face_cascade(self):
        """Setup OpenCV face detection cascade."""
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        if self.face_cascade.empty():
            print("⚠️ Warning: Could not load face cascade classifier")
    
    def detect_face(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect face in image and return bounding rectangle."""
        if self.face_cascade.empty():
            return None
            
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return None
            
        # Return the largest face
        return tuple(max(faces, key=lambda face: face[2] * face[3]))
    
    def extract_face_region(self, image: np.ndarray, face_rect: Tuple[int, int, int, int]) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
        """Extract face region from image."""
        px, py, pw, ph = face_rect
        return image[py:py+ph, px:px+pw], (px, py, pw, ph)
    
    def create_horizontal_transparency_mask(self, height: int, width: int) -> np.ndarray:
        """Create horizontal transparency mask based on configuration."""
        config = self.config["transition"]
        
        start_y = int(height * config["start_y_ratio"])
        end_y = int(height * config["end_y_ratio"])
        blend_zone = int(height * config["blend_zone_ratio"])
        smoothness = config["smoothness"]
        
        # Initialize alpha mask (0 = transparent, 1 = opaque)
        alpha = np.zeros((height, width), dtype=np.float32)
        
        # Top section: fully transparent (shows background player)
        alpha[:start_y, :] = 0.0
        
        # Middle section: gradual transition
        if blend_zone > 0:
            transition_start = max(0, end_y - blend_zone)
            transition_end = min(height, end_y + blend_zone)
            
            for y in range(transition_start, transition_end):
                if y < height:
                    # Create smooth transition using sigmoid-like function
                    progress = (y - transition_start) / (transition_end - transition_start)
                    # Apply smoothness factor
                    if smoothness > 0.5:
                        # More gradual transition
                        alpha[y, :] = np.clip(progress ** (1 / smoothness), 0, 1)
                    else:
                        # Sharper transition
                        alpha[y, :] = np.clip(progress ** (1 / (1 - smoothness)), 0, 1)
        
        # Bottom section: fully opaque (shows foreground player)
        alpha[end_y:, :] = 1.0
        
        return alpha
    
    def apply_canny_edge_detection(self, image: np.ndarray, face_rects: list = None) -> np.ndarray:
        """
        Apply comprehensive Canny edge detection with face preservation and background removal.
        
        Args:
            image: Input composite image with transparency gradient
            face_rects: List of face rectangles to preserve (optional)
        
        Returns:
            Image with edges preserved on white background
        """
        config = self.config["processing"]
        
        # Step 1: Preprocess the composite image
        print("🔍 Step 1: Preprocessing composite image...")
        
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blur_kernel = tuple(config["gaussian_blur_kernel"])
        blurred = cv2.GaussianBlur(gray, blur_kernel, 0)
        
        # Step 2: Apply Canny edge detection
        print("🔍 Step 2: Applying Canny edge detection...")
        edges = cv2.Canny(blurred, config["canny_edge_low"], config["canny_edge_high"])
        
        # Step 3: Create face preservation mask
        print("🔍 Step 3: Creating face preservation mask...")
        face_mask = self._create_face_preservation_mask(image.shape[:2], face_rects)
        
        # Step 4: Enhance and filter edges
        print("🔍 Step 4: Enhancing and filtering edges...")
        enhanced_edges = self._enhance_edges(edges, face_mask)
        
        # Step 5: Create final result with white background
        print("🔍 Step 5: Creating final result...")
        result = self._create_final_result(image, enhanced_edges, face_mask)
        
        return result
    
    def _create_face_preservation_mask(self, image_shape: Tuple[int, int], face_rects: list = None) -> np.ndarray:
        """Create a mask to preserve face regions during edge detection."""
        height, width = image_shape
        mask = np.zeros((height, width), dtype=np.uint8)
        
        if face_rects:
            for face_rect in face_rects:
                if face_rect is not None:
                    x, y, w, h = face_rect
                    # Expand face region based on configuration
                    expansion = config["face_expansion_pixels"]
                    x1 = max(0, x - expansion)
                    y1 = max(0, y - expansion)
                    x2 = min(width, x + w + expansion)
                    y2 = min(height, y + h + expansion)
                    
                    # Create elliptical mask for face region
                    center = ((x1 + x2) // 2, (y1 + y2) // 2)
                    axes = ((x2 - x1) // 2, (y2 - y1) // 2)
                    cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
        
        # Apply Gaussian blur to smooth the mask edges
        mask = cv2.GaussianBlur(mask, (15, 15), 0)
        
        # Normalize to 0-1 range
        mask = mask.astype(np.float32) / 255.0
        
        return mask
    
    def _enhance_edges(self, edges: np.ndarray, face_mask: np.ndarray) -> np.ndarray:
        """Enhance edges while preserving face regions."""
        config = self.config["processing"]
        
        # Dilate edges to make them more prominent
        kernel = np.ones((3, 3), np.uint8)
        dilated_edges = cv2.dilate(edges, kernel, iterations=1)
        
        # Apply morphological operations to clean up edges
        # Remove small noise
        kernel_small = np.ones((2, 2), np.uint8)
        cleaned_edges = cv2.morphologyEx(dilated_edges, cv2.MORPH_CLOSE, kernel_small)
        
        # Enhance edges in face regions
        face_enhanced_edges = cleaned_edges.copy()
        
        # Apply stronger edge enhancement in face regions
        face_preservation_threshold = config["face_preservation_strength"]
        face_region = (face_mask > face_preservation_threshold).astype(np.uint8) * 255
        
        # Find contours in face regions
        contours, _ = cv2.findContours(face_region, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter and enhance important contours
        contour_threshold = config["contour_area_threshold"]
        edge_iterations = config["edge_enhancement_iterations"]
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > contour_threshold:  # Only process significant contours
                # Enhance edges around this contour
                x, y, w, h = cv2.boundingRect(contour)
                roi = cleaned_edges[y:y+h, x:x+w]
                if roi.size > 0:
                    # Apply stronger edge enhancement based on configuration
                    enhanced_roi = cv2.dilate(roi, np.ones((2, 2), np.uint8), iterations=edge_iterations)
                    face_enhanced_edges[y:y+h, x:x+w] = enhanced_roi
        
        return face_enhanced_edges
    
    def _create_final_result(self, original_image: np.ndarray, edges: np.ndarray, face_mask: np.ndarray) -> np.ndarray:
        """Create final result with edges on white background."""
        config = self.config["processing"]
        
        # Create white background
        white_bg = np.full_like(original_image, 255)
        
        # Convert edges to 3-channel
        edge_mask_3d = cv2.merge([edges, edges, edges])
        
        # Create preservation mask for face regions
        face_preservation_mask = face_mask[:, :, np.newaxis]
        
        # Blend original image with white background based on face mask
        # Preserve more of original image in face regions, more white in background
        preserved_regions = original_image * face_preservation_mask
        background_regions = white_bg * (1.0 - face_preservation_mask)
        
        # Combine preserved regions and background
        base_result = preserved_regions + background_regions
        
        # Overlay edges
        # Use edges as a mask to determine where to show edges vs preserved content
        edge_strength = edges.astype(np.float32) / 255.0
        edge_strength_3d = edge_strength[:, :, np.newaxis]
        
        # Create edge overlay (black edges)
        edge_overlay = np.zeros_like(original_image)
        edge_overlay[edges > 0] = [0, 0, 0]  # Black edges
        
        # Blend edges with base result
        final_result = base_result * (1.0 - edge_strength_3d) + edge_overlay * edge_strength_3d
        
        # Ensure values are in valid range
        final_result = np.clip(final_result, 0, 255).astype(np.uint8)
        
        return final_result
    
    def create_mashup(self, img1: np.ndarray, img2: np.ndarray, 
                      face1_rect: Optional[Tuple[int, int, int, int]] = None,
                      face2_rect: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Create horizontal face mashup with transparency gradient."""
        config = self.config["processing"]
        target_size = tuple(config["target_size"])
        
        # Extract face regions if available, otherwise use whole images
        if face1_rect is not None:
            face1, _ = self.extract_face_region(img1, face1_rect)
        else:
            face1 = img1
            
        if face2_rect is not None:
            face2, _ = self.extract_face_region(img2, face2_rect)
        else:
            face2 = img2
        
        # Resize both images to target size
        face1_resized = cv2.resize(face1, target_size).astype(np.float32)
        face2_resized = cv2.resize(face2, target_size).astype(np.float32)
        
        # Create horizontal transparency mask
        height, width = target_size[1], target_size[0]
        alpha_mask = self.create_horizontal_transparency_mask(height, width)
        
        # Convert alpha mask to 3-channel
        alpha_3d = cv2.merge([alpha_mask, alpha_mask, alpha_mask])
        
        # Blend images using alpha mask
        # img1 (background player) * (1 - alpha) + img2 (foreground player) * alpha
        result = (face1_resized * (1.0 - alpha_3d) + face2_resized * alpha_3d)
        
        # Ensure values are in valid range
        result = np.clip(result, 0, 255).astype(np.uint8)
        
        # Apply Gaussian blur to smooth any artifacts
        blur_kernel = tuple(config["gaussian_blur_kernel"])
        result = cv2.GaussianBlur(result, blur_kernel, 0)
        
        return result
    
    def save_debug_images(self, img1: np.ndarray, img2: np.ndarray, 
                         result: np.ndarray, alpha_mask: np.ndarray,
                         player1_name: str, player2_name: str):
        """Save debug images for analysis."""
        if not self.config["output"]["save_debug_images"]:
            return
            
        output_dir = self.config["output"]["debug_output_dir"]
        os.makedirs(output_dir, exist_ok=True)
        
        # Save individual components
        cv2.imwrite(os.path.join(output_dir, f"{player1_name}_background.png"), img1)
        cv2.imwrite(os.path.join(output_dir, f"{player2_name}_foreground.png"), img2)
        cv2.imwrite(os.path.join(output_dir, "alpha_mask.png"), (alpha_mask * 255).astype(np.uint8))
        cv2.imwrite(os.path.join(output_dir, "mashup_before_canny.png"), result)
        
        # Save alpha mask visualization
        alpha_viz = (alpha_mask * 255).astype(np.uint8)
        alpha_viz = cv2.applyColorMap(alpha_viz, cv2.COLORMAP_JET)
        cv2.imwrite(os.path.join(output_dir, "alpha_mask_visualization.png"), alpha_viz)
        
        print(f"✅ Debug images saved to {output_dir}")
    
    def process_mashup_with_edge_detection(self, img1: np.ndarray, img2: np.ndarray,
                                         face1_rect: Optional[Tuple[int, int, int, int]] = None,
                                         face2_rect: Optional[Tuple[int, int, int, int]] = None,
                                         player1_name: str = "Player1", 
                                         player2_name: str = "Player2") -> np.ndarray:
        """Complete mashup pipeline with edge detection and background removal."""
        
        # Step 1: Create the transparency gradient mashup
        print("🎮 Step 1: Creating transparency gradient mashup...")
        result = self.create_mashup(img1, img2, face1_rect, face2_rect)
        
        # Step 2: Prepare face rectangles for edge detection
        print("🎮 Step 2: Preparing face rectangles for edge detection...")
        face_rects = []
        if face1_rect is not None:
            # Convert face1_rect to target size coordinates
            target_size = tuple(self.config["processing"]["target_size"])
            face1_scaled = self._scale_face_rect(face1_rect, img1.shape[:2], target_size)
            face_rects.append(face1_scaled)
        
        if face2_rect is not None:
            # Convert face2_rect to target size coordinates
            target_size = tuple(self.config["processing"]["target_size"])
            face2_scaled = self._scale_face_rect(face2_rect, img2.shape[:2], target_size)
            face_rects.append(face2_scaled)
        
        # Step 3: Apply Canny edge detection for background removal
        print("🎮 Step 3: Applying Canny edge detection...")
        result_with_edges = self.apply_canny_edge_detection(result, face_rects)
        
        # Step 4: Save debug images if enabled
        if self.config["output"]["save_debug_images"]:
            print("🎮 Step 4: Saving debug images...")
            height, width = result.shape[:2]
            alpha_mask = self.create_horizontal_transparency_mask(height, width)
            self.save_debug_images(img1, img2, result, alpha_mask, player1_name, player2_name)
            
            # Also save edge detection debug images
            self._save_edge_detection_debug_images(result, result_with_edges, face_rects)
        
        return result_with_edges
    
    def _scale_face_rect(self, face_rect: Tuple[int, int, int, int], 
                         original_size: Tuple[int, int], 
                         target_size: Tuple[int, int]) -> Tuple[int, int, int, int]:
        """Scale face rectangle from original image size to target size."""
        orig_h, orig_w = original_size
        target_h, target_w = target_size
        
        x, y, w, h = face_rect
        
        # Calculate scaling factors
        scale_x = target_w / orig_w
        scale_y = target_h / orig_h
        
        # Scale coordinates
        new_x = int(x * scale_x)
        new_y = int(y * scale_y)
        new_w = int(w * scale_x)
        new_h = int(h * scale_y)
        
        return (new_x, new_y, new_w, new_h)
    
    def _save_edge_detection_debug_images(self, original_mashup: np.ndarray, 
                                        final_result: np.ndarray, 
                                        face_rects: list):
        """Save additional debug images for edge detection analysis."""
        output_dir = self.config["output"]["debug_output_dir"]
        
        # Save the original mashup before edge detection
        cv2.imwrite(os.path.join(output_dir, "mashup_before_edge_detection.png"), original_mashup)
        
        # Save the final result with edge detection
        cv2.imwrite(os.path.join(output_dir, "final_result_with_edges.png"), final_result)
        
        # Create and save face region visualization
        if face_rects:
            face_viz = original_mashup.copy()
            for i, face_rect in enumerate(face_rects):
                if face_rect is not None:
                    x, y, w, h = face_rect
                    # Draw rectangle around face region
                    cv2.rectangle(face_viz, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(face_viz, f"Face {i+1}", (x, y-10), 
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            cv2.imwrite(os.path.join(output_dir, "face_regions_visualization.png"), face_viz)
        
        print(f"✅ Edge detection debug images saved to {output_dir}")
    
    def update_config(self, new_config: dict):
        """Update configuration parameters."""
        self.config.update(new_config)
        print("✅ Configuration updated")
    
    def get_current_config(self) -> dict:
        """Get current configuration."""
        return self.config.copy()
