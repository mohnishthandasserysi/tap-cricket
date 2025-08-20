#!/usr/bin/env python3
"""
Comprehensive test script for the edge detection system in the horizontal face mashup.
This script tests various edge detection configurations and scenarios.
"""

import cv2
import numpy as np
import json
import os
from horizontal_mashup import HorizontalFaceMashup

def test_basic_edge_detection():
    """Test basic edge detection functionality."""
    print("🧪 Testing basic edge detection...")
    
    processor = HorizontalFaceMashup()
    
    # Create test images with clear features
    height, width = 350, 350
    
    # Background player with eyes
    img1 = np.full((height, width, 3), (100, 150, 200), dtype=np.uint8)
    # Draw eyes
    cv2.circle(img1, (150, 120), 25, (255, 255, 255), -1)  # Left eye
    cv2.circle(img1, (200, 120), 25, (255, 255, 255), -1)  # Right eye
    cv2.circle(img1, (150, 120), 12, (0, 0, 0), -1)        # Left pupil
    cv2.circle(img1, (200, 120), 12, (0, 0, 0), -1)        # Right pupil
    
    # Foreground player with mouth/neck
    img2 = np.full((height, width, 3), (200, 100, 150), dtype=np.uint8)
    # Draw mouth
    cv2.ellipse(img2, (175, 280), (40, 20), 0, 0, 180, (255, 255, 255), -1)
    # Draw neck
    cv2.rectangle(img2, (160, 300), (190, 350), (255, 255, 255), -1)
    
    # Create face rectangles (simulating detected faces)
    face1_rect = (100, 80, 150, 150)  # Background player face
    face2_rect = (120, 200, 110, 150) # Foreground player face
    
    print("  📸 Created test images with eyes and mouth features")
    
    # Test edge detection
    result = processor.process_mashup_with_edge_detection(
        img1, img2, face1_rect, face2_rect,
        player1_name="TestBackground", player2_name="TestForeground"
    )
    
    # Save results
    output_dir = "../Output/test_edge_detection_basic"
    os.makedirs(output_dir, exist_ok=True)
    
    cv2.imwrite(os.path.join(output_dir, "background_with_eyes.png"), img1)
    cv2.imwrite(os.path.join(output_dir, "foreground_with_mouth.png"), img2)
    cv2.imwrite(os.path.join(output_dir, "final_result.png"), result)
    
    print("✅ Basic edge detection test completed")
    return result

def test_edge_detection_configurations():
    """Test different edge detection configurations."""
    print("🧪 Testing different edge detection configurations...")
    
    processor = HorizontalFaceMashup()
    
    # Create test images
    height, width = 350, 350
    img1 = np.full((height, width, 3), (80, 120, 180), dtype=np.uint8)
    img2 = np.full((height, width, 3), (180, 80, 120), dtype=np.uint8)
    
    # Add some features
    cv2.circle(img1, (175, 100), 30, (255, 255, 255), -1)  # Eyes
    cv2.rectangle(img2, (150, 250), (200, 300), (255, 255, 255), -1)  # Mouth
    
    face1_rect = (100, 60, 150, 120)
    face2_rect = (120, 200, 110, 120)
    
    # Test different configurations
    configs = [
        {
            "name": "sensitive_edges",
            "config": {
                "processing": {
                    "canny_edge_low": 30,
                    "canny_edge_high": 200,
                    "face_preservation_strength": 0.5,
                    "edge_enhancement_iterations": 2
                }
            }
        },
        {
            "name": "conservative_edges",
            "config": {
                "processing": {
                    "canny_edge_low": 80,
                    "canny_edge_high": 120,
                    "face_preservation_strength": 0.8,
                    "edge_enhancement_iterations": 1
                }
            }
        },
        {
            "name": "balanced_edges",
            "config": {
                "processing": {
                    "canny_edge_low": 50,
                    "canny_edge_high": 150,
                    "face_preservation_strength": 0.7,
                    "edge_enhancement_iterations": 1
                }
            }
        },
        {
            "name": "strong_face_preservation",
            "config": {
                "processing": {
                    "canny_edge_low": 60,
                    "canny_edge_high": 140,
                    "face_preservation_strength": 0.9,
                    "face_expansion_pixels": 20
                }
            }
        }
    ]
    
    output_dir = "../Output/test_edge_detection_configs"
    os.makedirs(output_dir, exist_ok=True)
    
    for config_test in configs:
        print(f"  🔧 Testing {config_test['name']}...")
        
        # Update configuration
        processor.update_config(config_test['config'])
        
        # Create mashup with edge detection
        result = processor.process_mashup_with_edge_detection(
            img1, img2, face1_rect, face2_rect,
            player1_name="ConfigTest", player2_name="ConfigTest"
        )
        
        # Save result
        filename = f"edge_detection_{config_test['name']}.png"
        cv2.imwrite(os.path.join(output_dir, filename), result)
        
        # Save configuration used
        config_filename = f"config_{config_test['name']}.json"
        with open(os.path.join(output_dir, config_filename), 'w') as f:
            json.dump(processor.get_current_config(), f, indent=2)
    
    print("✅ Edge detection configuration tests completed")

def test_edge_detection_with_noise():
    """Test edge detection with noisy images."""
    print("🧪 Testing edge detection with noisy images...")
    
    processor = HorizontalFaceMashup()
    
    height, width = 350, 350
    
    # Create noisy background
    img1 = np.full((height, width, 3), (100, 150, 200), dtype=np.uint8)
    # Add noise
    noise = np.random.randint(-20, 20, (height, width, 3), dtype=np.int16)
    img1 = np.clip(img1.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # Add eyes
    cv2.circle(img1, (175, 100), 30, (255, 255, 255), -1)
    cv2.circle(img1, (175, 100), 15, (0, 0, 0), -1)
    
    # Create noisy foreground
    img2 = np.full((height, width, 3), (200, 100, 150), dtype=np.uint8)
    # Add noise
    noise = np.random.randint(-20, 20, (height, width, 3), dtype=np.int16)
    img2 = np.clip(img2.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # Add mouth
    cv2.rectangle(img2, (150, 250), (200, 300), (255, 255, 255), -1)
    
    face1_rect = (100, 60, 150, 120)
    face2_rect = (120, 200, 110, 120)
    
    # Test with different noise reduction settings
    noise_configs = [
        {
            "name": "light_noise_reduction",
            "config": {
                "processing": {
                    "gaussian_blur_kernel": [3, 3],
                    "canny_edge_low": 60,
                    "canny_edge_high": 140
                }
            }
        },
        {
            "name": "heavy_noise_reduction",
            "config": {
                "processing": {
                    "gaussian_blur_kernel": [7, 7],
                    "canny_edge_low": 80,
                    "canny_edge_high": 120
                }
            }
        }
    ]
    
    output_dir = "../Output/test_edge_detection_noise"
    os.makedirs(output_dir, exist_ok=True)
    
    for config_test in noise_configs:
        print(f"  🔧 Testing {config_test['name']}...")
        
        processor.update_config(config_test['config'])
        
        result = processor.process_mashup_with_edge_detection(
            img1, img2, face1_rect, face2_rect,
            player1_name="NoiseTest", player2_name="NoiseTest"
        )
        
        filename = f"noise_test_{config_test['name']}.png"
        cv2.imwrite(os.path.join(output_dir, filename), result)
    
    # Save original noisy images for comparison
    cv2.imwrite(os.path.join(output_dir, "noisy_background.png"), img1)
    cv2.imwrite(os.path.join(output_dir, "noisy_foreground.png"), img2)
    
    print("✅ Edge detection noise tests completed")

def test_edge_detection_pipeline_steps():
    """Test individual steps of the edge detection pipeline."""
    print("🧪 Testing individual edge detection pipeline steps...")
    
    processor = HorizontalFaceMashup()
    
    # Create simple test image
    height, width = 350, 350
    test_image = np.full((height, width, 3), (150, 150, 150), dtype=np.uint8)
    
    # Add some geometric shapes for edge detection
    cv2.circle(test_image, (175, 100), 40, (255, 255, 255), -1)  # Circle
    cv2.rectangle(test_image, (150, 200), (200, 250), (255, 255, 255), -1)  # Rectangle
    cv2.line(test_image, (100, 300), (250, 300), (255, 255, 255), 5)  # Line
    
    # Simulate face rectangles
    face_rects = [(100, 60, 150, 120), (120, 180, 110, 120)]
    
    output_dir = "../Output/test_edge_detection_pipeline"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save original test image
    cv2.imwrite(os.path.join(output_dir, "test_image_original.png"), test_image)
    
    # Test each step individually
    print("  🔍 Testing preprocessing...")
    gray = cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    cv2.imwrite(os.path.join(output_dir, "step1_gray.png"), gray)
    cv2.imwrite(os.path.join(output_dir, "step1_blurred.png"), blurred)
    
    print("  🔍 Testing Canny edge detection...")
    edges = cv2.Canny(blurred, 50, 150)
    cv2.imwrite(os.path.join(output_dir, "step2_canny_edges.png"), edges)
    
    print("  🔍 Testing face preservation mask...")
    face_mask = processor._create_face_preservation_mask((height, width), face_rects)
    face_mask_vis = (face_mask * 255).astype(np.uint8)
    cv2.imwrite(os.path.join(output_dir, "step3_face_mask.png"), face_mask_vis)
    
    print("  🔍 Testing edge enhancement...")
    enhanced_edges = processor._enhance_edges(edges, face_mask)
    cv2.imwrite(os.path.join(output_dir, "step4_enhanced_edges.png"), enhanced_edges)
    
    print("  🔍 Testing final result creation...")
    final_result = processor._create_final_result(test_image, enhanced_edges, face_mask)
    cv2.imwrite(os.path.join(output_dir, "step5_final_result.png"), final_result)
    
    print("✅ Edge detection pipeline step tests completed")

def test_edge_detection_performance():
    """Test edge detection performance with different image sizes."""
    print("🧪 Testing edge detection performance...")
    
    processor = HorizontalFaceMashup()
    
    # Test different image sizes
    sizes = [(250, 250), (350, 350), (500, 500), (700, 700)]
    
    output_dir = "../Output/test_edge_detection_performance"
    os.makedirs(output_dir, exist_ok=True)
    
    for size in sizes:
        print(f"  📏 Testing size {size[0]}x{size[1]}...")
        
        height, width = size
        
        # Create test image
        test_image = np.full((height, width, 3), (150, 150, 150), dtype=np.uint8)
        cv2.circle(test_image, (width//2, height//3), width//8, (255, 255, 255), -1)
        cv2.rectangle(test_image, (width//4, height*2//3), (width*3//4, height*5//6), (255, 255, 255), -1)
        
        # Simulate face rectangle
        face_rect = (width//4, height//6, width//2, height//3)
        
        # Update target size in config
        processor.update_config({
            "processing": {
                "target_size": [width, height]
            }
        })
        
        # Time the edge detection
        import time
        start_time = time.time()
        
        result = processor.process_mashup_with_edge_detection(
            test_image, test_image, face_rect, face_rect,
            player1_name="PerfTest", player2_name="PerfTest"
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Save result
        filename = f"performance_test_{width}x{height}.png"
        cv2.imwrite(os.path.join(output_dir, filename), result)
        
        # Save timing info
        timing_info = {
            "size": f"{width}x{height}",
            "processing_time_seconds": processing_time,
            "pixels": width * height
        }
        
        timing_filename = f"timing_{width}x{height}.json"
        with open(os.path.join(output_dir, timing_filename), 'w') as f:
            json.dump(timing_info, f, indent=2)
        
        print(f"    ⏱️ Processing time: {processing_time:.3f} seconds")
    
    print("✅ Edge detection performance tests completed")

def main():
    """Run all edge detection tests."""
    print("🚀 Starting comprehensive edge detection tests...\n")
    
    try:
        # Test basic functionality
        test_basic_edge_detection()
        print()
        
        # Test different configurations
        test_edge_detection_configurations()
        print()
        
        # Test with noise
        test_edge_detection_with_noise()
        print()
        
        # Test pipeline steps
        test_edge_detection_pipeline_steps()
        print()
        
        # Test performance
        test_edge_detection_performance()
        print()
        
        print("🎉 All edge detection tests completed successfully!")
        print("📁 Check the Output directory for detailed test results")
        print("\n📋 Test Summary:")
        print("  - Basic edge detection functionality")
        print("  - Different configuration settings")
        print("  - Noise handling capabilities")
        print("  - Individual pipeline steps")
        print("  - Performance across different image sizes")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
