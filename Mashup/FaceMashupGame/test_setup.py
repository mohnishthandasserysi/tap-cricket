#!/usr/bin/env python3
"""
Test script to verify Face Mashup Game setup and dependencies.
Run this before playing the game to ensure everything is working.
"""

import sys
import os


def test_imports():
    """Test if all required packages are available."""
    print("🔍 Testing Python package imports...")
    
    required_packages = {
        'cv2': 'opencv-python',
        'dlib': 'dlib', 
        'numpy': 'numpy',
        'requests': 'requests'
    }
    
    missing_packages = []
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
            print(f"  ✅ {pip_name}")
        except ImportError:
            print(f"  ❌ {pip_name} - MISSING")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All packages imported successfully!")
    return True


def test_face_processor():
    """Test face processing initialization."""
    print("\n🤖 Testing face processor initialization...")
    
    try:
        from utils import FaceProcessor
        processor = FaceProcessor()
        print("✅ Face processor initialized successfully!")
        
        # Check if landmark model exists
        if os.path.exists(processor.predictor_path):
            print("✅ Dlib landmark model found!")
        else:
            print("⚠️  Dlib landmark model will be downloaded on first run")
        
        return True
        
    except Exception as e:
        print(f"❌ Face processor failed: {e}")
        return False


def test_players_folder():
    """Test players folder and images."""
    print("\n📁 Testing players folder...")
    
    players_folder = "players"
    
    if not os.path.exists(players_folder):
        print("❌ Players folder not found!")
        print("💡 Create a 'players/' folder and add celebrity images")
        return False
    
    # Check for image files
    image_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    image_files = []
    
    for file in os.listdir(players_folder):
        if file.lower().endswith(image_extensions):
            image_files.append(file)
    
    print(f"📸 Found {len(image_files)} image files:")
    for img in image_files:
        player_name = os.path.splitext(img)[0].replace('_', ' ').title()
        print(f"  - {player_name} ({img})")
    
    if len(image_files) < 3:
        print("\n⚠️  Need at least 3 player images to play the game!")
        print("💡 Add more images to the 'players/' folder")
        return False
    
    print(f"✅ Players folder ready with {len(image_files)} images!")
    return True


def test_mashup_generation():
    """Test mashup generation capability."""
    print("\n🎭 Testing mashup generation...")
    
    try:
        from utils import MashupGenerator
        generator = MashupGenerator()
        
        # Try to load player images
        players = generator.load_player_images()
        print(f"📸 Loaded {len(players)} player images")
        
        if len(players) >= 3:
            print("✅ Sufficient players for mashup generation!")
            
            # Test creating a simple mashup (this might take a moment)
            print("🔄 Testing mashup creation (this may take a few seconds)...")
            try:
                mashup, used_players = generator.create_mashup()
                print(f"✅ Successfully created mashup using: {', '.join(used_players)}")
                
                # Test quiz options generation
                options, correct = generator.generate_quiz_options(used_players)
                print(f"✅ Generated quiz options: {len(options)} options")
                
                return True
                
            except Exception as e:
                print(f"⚠️  Mashup creation test failed: {e}")
                print("💡 This might be due to face detection issues - try different player images")
                return False
        else:
            print("⚠️  Not enough players for mashup testing")
            return False
            
    except Exception as e:
        print(f"❌ Mashup generator failed: {e}")
        return False


def run_full_test():
    """Run all tests and provide setup status."""
    print("🎮 Face Mashup Game - Setup Test")
    print("=" * 40)
    
    tests = [
        ("Package Imports", test_imports),
        ("Face Processor", test_face_processor), 
        ("Players Folder", test_players_folder),
        ("Mashup Generation", test_mashup_generation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST SUMMARY")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(tests)}")
    
    if passed == len(tests):
        print("\n🎉 All tests passed! You're ready to play!")
        print("🚀 Run the game with: python main.py")
    else:
        print(f"\n⚠️  {len(tests) - passed} test(s) failed. Please fix the issues above.")
        
        if passed >= 2:  # At least imports and face processor work
            print("💡 You can still try running the game, but it might not work perfectly")
    
    return passed == len(tests)


if __name__ == "__main__":
    run_full_test()
