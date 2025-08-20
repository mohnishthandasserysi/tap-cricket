#!/usr/bin/env python3
"""
Test script for the horizontal face mashup system.
This script demonstrates different configuration settings and their effects.
"""

import cv2
import numpy as np
import json
import os
from horizontal_mashup import HorizontalFaceMashup

def test_basic_mashup():
    """Test basic horizontal mashup functionality."""
    print("🧪 Testing basic horizontal mashup...")
    
    # Initialize processor
    processor = HorizontalFaceMashup()
    
    # Create test images (simple colored rectangles)
    height, width = 350, 350
    
    # Background player (blue - will show eyes)
    img1 = np.full((height, width, 3), (255, 0, 0), dtype=np.uint8)  # Blue
    cv2.putText(img1, "Background Player", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img1, "Eyes Visible", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Foreground player (red - will show mouth/neck)
    img2 = np.full((height, width, 3), (0, 0, 255), dtype=np.uint8)  # Red
    cv2.putText(img2, "Foreground Player", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(img2, "Mouth/Neck Visible", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Create mashup
    result = processor.create_mashup(img1, img2)
    
    # Save result
    output_dir = "../Output/test_horizontal"
    os.makedirs(output_dir, exist_ok=True)
    
    cv2.imwrite(os.path.join(output_dir, "test_background.png"), img1)
    cv2.imwrite(os.path.join(output_dir, "test_foreground.png"), img2)
    cv2.imwrite(os.path.join(output_dir, "test_mashup_basic.png"), result)
    
    print("✅ Basic mashup test completed")
    return result

def test_different_transitions():
    """Test different transition configurations."""
    print("🧪 Testing different transition configurations...")
    
    processor = HorizontalFaceMashup()
    
    # Create test images
    height, width = 350, 350
    img1 = np.full((height, width, 3), (0, 255, 0), dtype=np.uint8)  # Green background
    img2 = np.full((height, width, 3), (255, 0, 255), dtype=np.uint8)  # Magenta foreground
    
    # Test different configurations
    configs = [
        {
            "name": "early_transition",
            "config": {
                "transition": {
                    "start_y_ratio": 0.0,
                    "end_y_ratio": 0.3,
                    "blend_zone_ratio": 0.05,
                    "smoothness": 0.9
                }
            }
        },
        {
            "name": "late_transition",
            "config": {
                "transition": {
                    "start_y_ratio": 0.0,
                    "end_y_ratio": 0.7,
                    "blend_zone_ratio": 0.15,
                    "smoothness": 0.6
                }
            }
        },
        {
            "name": "sharp_transition",
            "config": {
                "transition": {
                    "start_y_ratio": 0.0,
                    "end_y_ratio": 0.5,
                    "blend_zone_ratio": 0.02,
                    "smoothness": 0.3
                }
            }
        },
        {
            "name": "gradual_transition",
            "config": {
                "transition": {
                    "start_y_ratio": 0.0,
                    "end_y_ratio": 0.5,
                    "blend_zone_ratio": 0.25,
                    "smoothness": 0.95
                }
            }
        }
    ]
    
    output_dir = "../Output/test_transitions"
    os.makedirs(output_dir, exist_ok=True)
    
    for config_test in configs:
        print(f"  🔧 Testing {config_test['name']}...")
        
        # Update configuration
        processor.update_config(config_test['config'])
        
        # Create mashup
        result = processor.create_mashup(img1, img2)
        
        # Save result
        filename = f"mashup_{config_test['name']}.png"
        cv2.imwrite(os.path.join(output_dir, filename), result)
        
        # Save alpha mask visualization
        alpha_mask = processor.create_horizontal_transparency_mask(height, width)
        alpha_viz = (alpha_mask * 255).astype(np.uint8)
        alpha_viz = cv2.applyColorMap(alpha_viz, cv2.COLORMAP_JET)
        alpha_filename = f"alpha_{config_test['name']}.png"
        cv2.imwrite(os.path.join(output_dir, alpha_filename), alpha_viz)
    
    print("✅ Transition configuration tests completed")

def test_edge_detection():
    """Test the complete pipeline with edge detection."""
    print("🧪 Testing complete pipeline with edge detection...")
    
    processor = HorizontalFaceMashup()
    
    # Create test images with more complex patterns
    height, width = 350, 350
    
    # Background player with some features
    img1 = np.full((height, width, 3), (100, 150, 200), dtype=np.uint8)
    cv2.circle(img1, (175, 100), 30, (255, 255, 255), -1)  # Eyes
    cv2.circle(img1, (175, 100), 15, (0, 0, 0), -1)
    
    # Foreground player with different features
    img2 = np.full((height, width, 3), (200, 100, 150), dtype=np.uint8)
    cv2.rectangle(img2, (150, 250), (200, 300), (255, 255, 255), -1)  # Mouth/neck
    
    # Test complete pipeline
    result = processor.process_mashup_with_edge_detection(
        img1, img2, 
        player1_name="TestBackground", 
        player2_name="TestForeground"
    )
    
    # Save results
    output_dir = "../Output/test_edge_detection"
    os.makedirs(output_dir, exist_ok=True)
    
    cv2.imwrite(os.path.join(output_dir, "background.png"), img1)
    cv2.imwrite(os.path.join(output_dir, "foreground.png"), img2)
    cv2.imwrite(os.path.join(output_dir, "final_result.png"), result)
    
    print("✅ Edge detection test completed")

def test_config_file_reloading():
    """Test configuration file reloading."""
    print("🧪 Testing configuration file reloading...")
    
    processor = HorizontalFaceMashup()
    
    # Show current config
    print("📋 Current configuration:")
    current_config = processor.get_current_config()
    print(json.dumps(current_config, indent=2))
    
    # Test updating specific parameters
    print("\n🔧 Updating transition parameters...")
    processor.update_config({
        "transition": {
            "start_y_ratio": 0.1,
            "end_y_ratio": 0.6,
            "blend_zone_ratio": 0.08,
            "smoothness": 0.7
        }
    })
    
    print("📋 Updated configuration:")
    updated_config = processor.get_current_config()
    print(json.dumps(updated_config, indent=2))
    
    print("✅ Configuration reloading test completed")

def main():
    """Run all tests."""
    print("🚀 Starting horizontal face mashup tests...\n")
    
    try:
        # Test basic functionality
        test_basic_mashup()
        print()
        
        # Test different transition configurations
        test_different_transitions()
        print()
        
        # Test edge detection pipeline
        test_edge_detection()
        print()
        
        # Test configuration management
        test_config_file_reloading()
        print()
        
        print("🎉 All tests completed successfully!")
        print("📁 Check the Output directory for test results")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
