# 🎭 Celebrity Eye Quiz

A fun interactive quiz game that shows you cropped eye regions of celebrities and challenges you to guess who they are! Built with Python, Streamlit, and MediaPipe.

## Features

- **Face Detection**: Uses MediaPipe FaceMesh to detect faces and extract eye regions
- **Precise Eye Cropping**: Crops exactly around the eye area including eyebrows
- **Interactive Quiz**: Multiple choice questions with randomized options
- **Score Tracking**: Keep track of your correct answers
- **Easy to Extend**: Add more celebrities by simply adding their images

## Project Structure

```
celebrity_eye_quiz/
├── face_cropper.py      # MediaPipe face detection and eye cropping logic
├── quiz_app.py          # Streamlit UI and game logic
├── run_quiz.py          # Easy startup script with dependency checks
├── requirements.txt     # Python dependencies
├── images/              # Celebrity images folder
│   └── README.md       # Instructions for adding images
└── README.md           # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Add Celebrity Images

1. Place celebrity images in the `images/` folder
2. Name each file after the celebrity (e.g., `virat.jpg`, `shahrukh.jpg`)
3. Supported formats: `.jpg`, `.jpeg`, `.png`, `.bmp`
4. Need at least 4 images to play the quiz

Example image naming:
- `virat.jpg` → "Virat" in the quiz
- `shah_rukh.jpg` → "Shah Rukh" in the quiz
- `alia.jpg` → "Alia" in the quiz

### 3. Run the Application

```bash
# Option 1: Using the helper script (recommended)
python run_quiz.py

# Option 2: Direct run
streamlit run quiz_app.py
```

The app will open in your browser at `http://localhost:8501`

## How to Play

1. **Start the Quiz**: The app will randomly select a celebrity image
2. **View the Eyes**: You'll see a cropped image showing only the eye region
3. **Make Your Guess**: Click on one of the 4 multiple choice options
4. **Get Feedback**: See if you were correct and what the right answer was
5. **Continue Playing**: Click "Next Question" to continue
6. **Track Your Score**: Your score is displayed at the top

## Technical Details

### Eye Landmark Detection

The app uses specific MediaPipe FaceMesh landmark indexes to crop the eye region:

- **Left Eye**: 33, 133, 160, 159, 158, 157, 173
- **Right Eye**: 362, 263, 387, 386, 385, 384, 398

### Face Cropping Process

1. Load image using OpenCV
2. Convert to RGB format
3. Process with MediaPipe FaceMesh
4. Extract eye landmark coordinates
5. Calculate bounding box around both eyes
6. Add padding for eyebrows and area above nose
7. Crop and return the eye region

### Game Logic

1. Random celebrity selection each round
2. Eye cropping using MediaPipe
3. Generate 3 wrong answers from other celebrities
4. Shuffle answer options
5. Score tracking and feedback

## Dependencies

- **streamlit**: Web app framework
- **mediapipe**: Face detection and landmark detection
- **opencv-python**: Image processing
- **numpy**: Numerical operations
- **Pillow**: Image handling

## Troubleshooting

### "No face detected" Error
- Ensure the celebrity's face is clearly visible in the image
- Try using higher resolution images
- Make sure the face is not too small or at an extreme angle

### "Need at least 4 images" Error
- Add more celebrity images to the `images/` folder
- Ensure images have proper file extensions (.jpg, .jpeg, .png, .bmp)

### App Won't Start
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Ensure you're running from the correct directory
- Check that Python 3.7+ is being used

## Extending the Game

### Adding More Celebrities
1. Add more images to the `images/` folder
2. Follow the naming convention (filename = celebrity name)
3. The game will automatically include them in future rounds

### Customizing Difficulty
- Modify the eye landmark indexes in `face_cropper.py` for different cropping regions
- Adjust padding values for tighter or looser crops
- Add more wrong answer options by modifying the options generation logic

### Adding Features
- Score persistence across sessions
- Timer for each question
- Different difficulty levels
- Celebrity categories (Bollywood, Hollywood, etc.)

## License

This project is open source and available under the MIT License.
