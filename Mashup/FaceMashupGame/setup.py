#!/usr/bin/env python3
"""
Setup script for Face Mashup Game.
This will install dependencies and download required models.
"""

import subprocess
import sys
import os
import requests
import bz2


def install_requirements():
    """Install required Python packages."""
    print("📦 Installing Python packages...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ All packages installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False


def download_dlib_model():
    """Download the dlib 68-point landmark model."""
    model_path = "models/shape_predictor_68_face_landmarks.dat"
    
    if os.path.exists(model_path):
        print("✅ Dlib landmark model already exists!")
        return True
    
    print("📥 Downloading dlib 68-point landmark model...")
    print("   This is a one-time download (~68 MB)")
    
    url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
    
    try:
        # Create models directory
        os.makedirs("models", exist_ok=True)
        
        # Download compressed file
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        compressed_path = "models/shape_predictor_68_face_landmarks.dat.bz2"
        
        # Download with progress
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(compressed_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r   Progress: {progress:.1f}%", end="", flush=True)
        
        print("\n📂 Extracting model...")
        
        # Extract the compressed file
        with bz2.BZ2File(compressed_path, 'rb') as f_in:
            with open(model_path, 'wb') as f_out:
                f_out.write(f_in.read())
        
        # Remove compressed file
        os.remove(compressed_path)
        
        print("✅ Dlib landmark model downloaded and extracted!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to download model: {e}")
        print("💡 You can download manually from:")
        print("   http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
        print("   Extract to: models/shape_predictor_68_face_landmarks.dat")
        return False


def create_sample_folder_structure():
    """Create sample folder structure and instructions."""
    print("📁 Setting up folder structure...")
    
    # Ensure players folder exists
    os.makedirs("players", exist_ok=True)
    print("✅ Players folder created!")
    
    # Check if players folder is empty
    if not os.listdir("players"):
        print("\n💡 IMPORTANT: Add player images to get started!")
        print("   1. Add at least 3 celebrity/player images to the 'players/' folder")
        print("   2. Name them like: cristiano_ronaldo.jpg, lionel_messi.jpg, etc.")
        print("   3. Supported formats: .jpg, .jpeg, .png, .bmp")
        print("   4. Use clear, front-facing photos for best results")


def main():
    """Main setup function."""
    print("🎭 Face Mashup Game - Setup")
    print("=" * 30)
    
    setup_steps = [
        ("Installing Python packages", install_requirements),
        ("Downloading dlib model", download_dlib_model),
        ("Setting up folders", create_sample_folder_structure)
    ]
    
    success_count = 0
    
    for step_name, step_func in setup_steps:
        print(f"\n{step_name}...")
        try:
            if step_func():
                success_count += 1
            else:
                print(f"⚠️  {step_name} failed but continuing...")
        except Exception as e:
            print(f"❌ {step_name} crashed: {e}")
    
    print("\n" + "=" * 30)
    print("📊 SETUP SUMMARY")
    print("=" * 30)
    
    if success_count == len(setup_steps):
        print("🎉 Setup completed successfully!")
        print("\n🚀 Next steps:")
        print("   1. Add player images to the 'players/' folder")
        print("   2. Run: python test_setup.py (to verify)")
        print("   3. Run: python main.py (to play!)")
    else:
        print(f"⚠️  Setup partially completed ({success_count}/{len(setup_steps)} steps)")
        print("\n💡 You can still try running the game:")
        print("   python test_setup.py - to check what's working")
        print("   python main.py - to attempt playing")
    
    print("\n📖 For detailed instructions, see README.md")


if __name__ == "__main__":
    main()
