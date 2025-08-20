#!/usr/bin/env python3
"""
Simple configuration editor for the horizontal face mashup system.
This script provides an interactive way to modify the mashup_config.json file.
"""

import json
import os
import sys

CONFIG_FILE = "mashup_config.json"

def load_config():
    """Load the current configuration file."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Config file {CONFIG_FILE} not found, creating default...")
        return get_default_config()
    except json.JSONDecodeError:
        print(f"⚠️ Invalid JSON in {CONFIG_FILE}, creating default...")
        return get_default_config()

def get_default_config():
    """Return default configuration."""
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

def save_config(config):
    """Save configuration to file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Configuration saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")

def print_config(config, section=None):
    """Print configuration in a readable format."""
    if section:
        if section in config:
            print(f"\n📋 {section.upper()} SETTINGS:")
            print("-" * 40)
            for key, value in config[section].items():
                print(f"  {key}: {value}")
        else:
            print(f"❌ Section '{section}' not found in configuration")
    else:
        print("\n📋 CURRENT CONFIGURATION:")
        print("=" * 50)
        for section_name, section_data in config.items():
            print(f"\n{section_name.upper()}:")
            print("-" * 30)
            for key, value in section_data.items():
                print(f"  {key}: {value}")

def edit_transition_settings(config):
    """Edit transition settings interactively."""
    print("\n🔧 EDITING TRANSITION SETTINGS")
    print("=" * 40)
    
    transition = config["transition"]
    
    print(f"\nCurrent values:")
    print(f"  start_y_ratio: {transition['start_y_ratio']} (0.0 = top of image)")
    print(f"  end_y_ratio: {transition['end_y_ratio']} (0.5 = middle of image)")
    print(f"  blend_zone_ratio: {transition['blend_zone_ratio']} (0.1 = 10% of height)")
    print(f"  smoothness: {transition['smoothness']} (0.0 = sharp, 1.0 = very smooth)")
    
    print(f"\nQuick presets:")
    print("  1. Early transition (eyes to mouth)")
    print("  2. Late transition (more eyes, less mouth)")
    print("  3. Sharp transition (clear cut)")
    print("  4. Gradual transition (smooth blend)")
    print("  5. Custom values")
    
    choice = input("\nChoose option (1-5): ").strip()
    
    if choice == "1":
        # Early transition
        transition.update({
            "start_y_ratio": 0.0,
            "end_y_ratio": 0.3,
            "blend_zone_ratio": 0.05,
            "smoothness": 0.9
        })
        print("✅ Applied early transition preset")
        
    elif choice == "2":
        # Late transition
        transition.update({
            "start_y_ratio": 0.0,
            "end_y_ratio": 0.7,
            "blend_zone_ratio": 0.15,
            "smoothness": 0.6
        })
        print("✅ Applied late transition preset")
        
    elif choice == "3":
        # Sharp transition
        transition.update({
            "start_y_ratio": 0.0,
            "end_y_ratio": 0.5,
            "blend_zone_ratio": 0.02,
            "smoothness": 0.3
        })
        print("✅ Applied sharp transition preset")
        
    elif choice == "4":
        # Gradual transition
        transition.update({
            "start_y_ratio": 0.0,
            "end_y_ratio": 0.5,
            "blend_zone_ratio": 0.25,
            "smoothness": 0.95
        })
        print("✅ Applied gradual transition preset")
        
    elif choice == "5":
        # Custom values
        try:
            print("\nEnter custom values:")
            transition["start_y_ratio"] = float(input("  start_y_ratio (0.0-1.0): "))
            transition["end_y_ratio"] = float(input("  end_y_ratio (0.0-1.0): "))
            transition["blend_zone_ratio"] = float(input("  blend_zone_ratio (0.0-0.5): "))
            transition["smoothness"] = float(input("  smoothness (0.0-1.0): "))
            print("✅ Applied custom values")
        except ValueError:
            print("❌ Invalid input, keeping current values")
    else:
        print("❌ Invalid choice, keeping current values")

def edit_processing_settings(config):
    """Edit processing settings interactively."""
    print("\n🔧 EDITING PROCESSING SETTINGS")
    print("=" * 40)
    
    processing = config["processing"]
    
    print(f"\nCurrent values:")
    print(f"  target_size: {processing['target_size']}")
    print(f"  gaussian_blur_kernel: {processing['gaussian_blur_kernel']}")
    print(f"  canny_edge_low: {processing['canny_edge_low']}")
    print(f"  canny_edge_high: {processing['canny_edge_high']}")
    print(f"  face_preservation_strength: {processing.get('face_preservation_strength', 0.7)}")
    print(f"  edge_enhancement_iterations: {processing.get('edge_enhancement_iterations', 1)}")
    print(f"  contour_area_threshold: {processing.get('contour_area_threshold', 100)}")
    print(f"  face_expansion_pixels: {processing.get('face_expansion_pixels', 10)}")
    
    print(f"\nQuick presets:")
    print("  1. High quality (slower)")
    print("  2. Balanced (default)")
    print("  3. Fast (lower quality)")
    print("  4. Edge detection focused")
    print("  5. Face preservation focused")
    print("  6. Custom values")
    
    choice = input("\nChoose option (1-6): ").strip()
    
    if choice == "1":
        # High quality
        processing.update({
            "target_size": [500, 500],
            "gaussian_blur_kernel": [7, 7],
            "canny_edge_low": 30,
            "canny_edge_high": 200,
            "face_preservation_strength": 0.8,
            "edge_enhancement_iterations": 2,
            "contour_area_threshold": 80,
            "face_expansion_pixels": 15
        })
        print("✅ Applied high quality preset")
        
    elif choice == "2":
        # Balanced
        processing.update({
            "target_size": [350, 350],
            "gaussian_blur_kernel": [5, 5],
            "canny_edge_low": 50,
            "canny_edge_high": 150,
            "face_preservation_strength": 0.7,
            "edge_enhancement_iterations": 1,
            "contour_area_threshold": 100,
            "face_expansion_pixels": 10
        })
        print("✅ Applied balanced preset")
        
    elif choice == "3":
        # Fast
        processing.update({
            "target_size": [250, 250],
            "gaussian_blur_kernel": [3, 3],
            "canny_edge_low": 80,
            "canny_edge_high": 120,
            "face_preservation_strength": 0.6,
            "edge_enhancement_iterations": 1,
            "contour_area_threshold": 150,
            "face_expansion_pixels": 5
        })
        print("✅ Applied fast preset")
        
    elif choice == "4":
        # Edge detection focused
        processing.update({
            "target_size": [400, 400],
            "gaussian_blur_kernel": [3, 3],
            "canny_edge_low": 30,
            "canny_edge_high": 200,
            "face_preservation_strength": 0.5,
            "edge_enhancement_iterations": 3,
            "contour_area_threshold": 50,
            "face_expansion_pixels": 8
        })
        print("✅ Applied edge detection focused preset")
        
    elif choice == "5":
        # Face preservation focused
        processing.update({
            "target_size": [400, 400],
            "gaussian_blur_kernel": [7, 7],
            "canny_edge_low": 60,
            "canny_edge_high": 140,
            "face_preservation_strength": 0.9,
            "edge_enhancement_iterations": 1,
            "contour_area_threshold": 200,
            "face_expansion_pixels": 25
        })
        print("✅ Applied face preservation focused preset")
        
    elif choice == "6":
        # Custom values
        try:
            print("\nEnter custom values:")
            size = int(input("  target_size (width): "))
            processing["target_size"] = [size, size]
            blur = int(input("  gaussian_blur_kernel (odd number): "))
            processing["gaussian_blur_kernel"] = [blur, blur]
            processing["canny_edge_low"] = int(input("  canny_edge_low: "))
            processing["canny_edge_high"] = int(input("  canny_edge_high: "))
            processing["face_preservation_strength"] = float(input("  face_preservation_strength (0.0-1.0): "))
            processing["edge_enhancement_iterations"] = int(input("  edge_enhancement_iterations: "))
            processing["contour_area_threshold"] = int(input("  contour_area_threshold: "))
            processing["face_expansion_pixels"] = int(input("  face_expansion_pixels: "))
            print("✅ Applied custom values")
        except ValueError:
            print("❌ Invalid input, keeping current values")
    else:
        print("❌ Invalid choice, keeping current values")

def edit_output_settings(config):
    """Edit output settings interactively."""
    print("\n🔧 EDITING OUTPUT SETTINGS")
    print("=" * 40)
    
    output = config["output"]
    
    print(f"\nCurrent values:")
    print(f"  save_debug_images: {output['save_debug_images']}")
    print(f"  debug_output_dir: {output['debug_output_dir']}")
    
    print(f"\nOptions:")
    print("  1. Enable debug images")
    print("  2. Disable debug images")
    print("  3. Change debug directory")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == "1":
        output["save_debug_images"] = True
        print("✅ Debug images enabled")
        
    elif choice == "2":
        output["save_debug_images"] = False
        print("✅ Debug images disabled")
        
    elif choice == "3":
        new_dir = input("  New debug directory: ").strip()
        if new_dir:
            output["debug_output_dir"] = new_dir
            print(f"✅ Debug directory changed to: {new_dir}")
    else:
        print("❌ Invalid choice, keeping current values")

def main():
    """Main configuration editor."""
    print("🔧 Horizontal Face Mashup Configuration Editor")
    print("=" * 50)
    
    # Load current configuration
    config = load_config()
    
    while True:
        print("\n" + "=" * 50)
        print("MAIN MENU")
        print("=" * 50)
        print("1. View current configuration")
        print("2. Edit transition settings")
        print("3. Edit processing settings")
        print("4. Edit output settings")
        print("5. Save and exit")
        print("6. Exit without saving")
        
        choice = input("\nChoose option (1-6): ").strip()
        
        if choice == "1":
            print_config(config)
            
        elif choice == "2":
            edit_transition_settings(config)
            
        elif choice == "3":
            edit_processing_settings(config)
            
        elif choice == "4":
            edit_output_settings(config)
            
        elif choice == "5":
            save_config(config)
            print("\n🎉 Configuration saved! You can now restart the server to apply changes.")
            break
            
        elif choice == "6":
            print("\n⚠️ Exiting without saving changes.")
            break
            
        else:
            print("❌ Invalid choice, please try again")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()
