#!/usr/bin/env python3
"""
Simple script to run the Celebrity Eye Quiz application.
This script will check dependencies and start the Streamlit app.
"""

import subprocess
import sys
import os


def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'streamlit',
        'mediapipe', 
        'opencv-python',
        'numpy',
        'Pillow'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True


def check_images_folder():
    """Check if images folder exists and has images."""
    if not os.path.exists('images'):
        print("❌ Images folder not found!")
        print("💡 Create an 'images/' folder and add celebrity images")
        return False
    
    image_files = []
    for file in os.listdir('images'):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            image_files.append(file)
    
    if len(image_files) == 0:
        print("❌ No images found in images/ folder!")
        print("💡 Add celebrity images with names like 'virat.jpg', 'shahrukh.jpg'")
        return False
    
    if len(image_files) < 4:
        print(f"⚠️  Only {len(image_files)} images found. Need at least 4 for the quiz.")
        print("💡 Add more celebrity images to the images/ folder")
        return False
    
    print(f"✅ Found {len(image_files)} celebrity images!")
    return True


def run_app():
    """Run the Streamlit application."""
    print("🚀 Starting Celebrity Eye Quiz...")
    print("📝 The app will open in your default browser")
    print("🛑 Press Ctrl+C to stop the app")
    print("-" * 50)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "quiz_app.py"])
    except KeyboardInterrupt:
        print("\n👋 Quiz app stopped. Thanks for playing!")
    except Exception as e:
        print(f"❌ Error starting app: {e}")


def main():
    """Main function to run checks and start the app."""
    print("🎭 Celebrity Eye Quiz - Setup Check")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check images folder
    if not check_images_folder():
        print("\n⚠️  You can still run the app, but it won't work without images.")
        response = input("Continue anyway? (y/n): ").lower().strip()
        if response not in ['y', 'yes']:
            sys.exit(1)
    
    print("\n" + "=" * 40)
    run_app()


if __name__ == "__main__":
    main()
