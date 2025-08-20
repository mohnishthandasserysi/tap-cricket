# 🎭 Face Mashup Game

A fun computer vision game that creates blended faces from multiple celebrity/player images and challenges you to guess which players are in the mashup!

## 🎮 How It Works

The game uses advanced face detection and blending techniques to:
1. **Detect facial landmarks** using dlib's 68-point face detection
2. **Extract face parts** (eyes, nose, mouth) from different player images
3. **Blend them seamlessly** onto a base face using OpenCV's seamless cloning
4. **Challenge you** to guess which players contributed to the mashup

## 🎯 Game Features

- **Realistic Face Blending**: Uses computer vision to create natural-looking mashups
- **Multiple Choice Quiz**: 4 options to choose from each round
- **Score Tracking**: Keep track of your accuracy across rounds
- **Interactive UI**: Click buttons or use keyboard shortcuts
- **Customizable**: Add your own player images easily

## 📁 Project Structure

```
FaceMashupGame/
├── main.py                    # Main game file - run this to play
├── utils.py                   # Face processing and blending utilities
├── requirements.txt           # Python dependencies
├── models/                    # Dlib landmark models (auto-downloaded)
│   └── shape_predictor_68_face_landmarks.dat
├── players/                   # Player/celebrity images
│   ├── README.md             # Instructions for adding images
│   ├── player1.jpg           # Add your player images here
│   ├── player2.jpg
│   └── ...
└── README.md                 # This file
```

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `opencv-python` - Computer vision and image processing
- `dlib` - Face detection and landmark prediction
- `numpy` - Numerical operations
- `requests` - For downloading the landmark model

### 2. Download Face Landmark Model

The game will **automatically download** the dlib 68-point facial landmark model on first run. 

**Manual download** (if automatic fails):
1. Download: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
2. Extract to: `models/shape_predictor_68_face_landmarks.dat`

### 3. Add Player Images

1. Place player/celebrity images in the `players/` folder
2. Name them descriptively: `cristiano_ronaldo.jpg`, `lionel_messi.jpg`, etc.
3. **Minimum 3 images required**, 5-6 recommended for variety

**Image requirements:**
- Clear, front-facing faces
- Good lighting and resolution
- Supported formats: `.jpg`, `.jpeg`, `.png`, `.bmp`

### 4. Run the Game

```bash
python main.py
```

## 🎮 How to Play

1. **Start the game** - A blended face mashup will appear
2. **Analyze the image** - Look for features from different players
3. **Make your guess** - Click on one of the 4 multiple choice options
4. **Get feedback** - See if you were correct and learn the right answer
5. **Continue playing** - Press SPACE for the next round
6. **Quit anytime** - Press Q to exit

### Controls
- **Mouse**: Click on answer buttons
- **Keyboard**: Press 1-4 to select options
- **SPACE**: Next round (after answering)
- **Q/ESC**: Quit game

## 🔬 Technical Details

### Face Processing Pipeline

1. **Face Detection**: Uses dlib's HOG-based face detector
2. **Landmark Extraction**: 68-point facial landmark detection
3. **Feature Segmentation**: Extract specific regions:
   - **Eyes**: Landmarks 36-47
   - **Nose**: Landmarks 27-35  
   - **Mouth**: Landmarks 48-67
4. **Alignment**: Resize and align features to match target face
5. **Blending**: Use OpenCV's seamless cloning for natural results

### Mashup Creation Process

1. **Select base player** (provides face structure)
2. **Choose 2-3 additional players** for feature donation
3. **Extract and align features** (eyes from player A, nose from player B, etc.)
4. **Seamlessly blend** all features onto the base face
5. **Generate quiz options** with correct and incorrect combinations

## 🛠️ Advanced Configuration

### Customizing Face Parts

Edit the landmark ranges in `utils.py`:

```python
self.EYES_POINTS = list(range(36, 48))    # Eyes region
self.NOSE_POINTS = list(range(27, 36))    # Nose region  
self.MOUTH_POINTS = list(range(48, 68))   # Mouth region
```

### Adjusting Blending Quality

Modify blending parameters in the `blend_face_part` method:
- **Seamless cloning**: Most realistic (default)
- **Alpha blending**: Faster but less natural
- **Simple overlay**: Fastest but basic

### Adding More Players

1. Save new images to `players/` folder
2. Follow naming convention: `firstname_lastname.jpg`
3. Game automatically includes new players

## 🐛 Troubleshooting

### Common Issues

**"No face detected" errors:**
- Ensure faces are clearly visible and well-lit
- Try different angles or higher resolution images
- Check that faces aren't too small in the image

**"Need at least 3 player images":**
- Add more images to the `players/` folder
- Verify file extensions are supported (.jpg, .jpeg, .png, .bmp)

**Blending artifacts:**
- Use higher quality source images
- Ensure faces are similar sizes and angles
- Try different players if specific combinations don't work well

**Installation issues:**
- **dlib compilation errors**: 
  - Windows: Install Visual Studio Build Tools
  - Mac: `brew install cmake`
  - Linux: `sudo apt-get install cmake`
- **OpenCV issues**: Try `pip install opencv-python-headless`

### Performance Tips

- **Use smaller images** (resize to ~800px width) for faster processing
- **Limit to 5-8 players** for optimal quiz variety vs. performance
- **Close other applications** during gameplay for smoother experience

## 🎯 Game Strategies

### For Players
- **Study facial features** - Learn to recognize distinctive eyes, noses, mouths
- **Look for blending seams** - Sometimes visible at feature boundaries
- **Consider proportions** - Face shape usually comes from the base player

### For Better Mashups
- **Use diverse faces** - Different ethnicities, ages, and features blend better
- **Quality matters** - High-resolution, well-lit photos produce better results
- **Similar poses** - Front-facing images work best for alignment

## 🔮 Future Enhancements

Potential improvements and features:
- **Difficulty levels** (more/fewer players in mashup)
- **Timer-based challenges**
- **Leaderboards and statistics**
- **Custom face part selection**
- **Real-time webcam mashups**
- **Team vs. team multiplayer**

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **dlib**: Face detection and landmark prediction
- **OpenCV**: Computer vision and image processing
- **Davis King**: Creator of dlib and the 68-point face predictor

## 🤝 Contributing

Feel free to contribute by:
- Adding more robust face detection
- Improving blending algorithms
- Creating better UI/UX
- Adding new game modes
- Optimizing performance

---

**Have fun playing and testing your face recognition skills!** 🎭👁️
