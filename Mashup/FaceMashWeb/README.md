# Guess the Celebrity - Eyes Edition

A fun Phaser 3 game that uses AI face detection to show only the eye region of celebrities. Players must guess which celebrity they're looking at based on their eyes alone!

## Features

- **AI-Powered Face Detection**: Uses face-api.js (TensorFlow.js) to detect facial landmarks
- **Eye Region Cropping**: Automatically crops images to show only the eyes and eyebrows area
- **Interactive Quiz**: Multiple choice questions with 4 options
- **Score Tracking**: Keep track of correct answers
- **Responsive Design**: Works on desktop and mobile devices
- **Beautiful UI**: Modern glassmorphism design with smooth animations

## Tech Stack

- **Vite**: Fast build tool and dev server
- **Phaser 3**: 2D game framework for rendering and interactions
- **face-api.js**: TensorFlow.js wrapper for face detection and landmark analysis
- **Modern CSS**: Glassmorphism design with responsive layout

## Setup Instructions

### 1. Install Dependencies
```bash
npm install
```

### 2. Add Celebrity Images
Place images in the `/public/images/` folder. The game will **automatically detect all image files** and use them!

**Supported Formats:**
- **PNG**, **JPG**, **JPEG** - all formats supported
- Handles **1600+ images** efficiently with performance optimizations

**Naming Convention:**
- Use descriptive filenames like: `john-doe.jpg`, `jane_smith.png`, `celebrity-name.jpeg`
- The game automatically converts filenames to display names (e.g., `john-doe.jpg` → "John Doe")
- Supports hyphens, underscores, and spaces in filenames

**Image Requirements:**
- Format: **PNG, JPG, or JPEG**
- Size: At least 400x400 pixels for best face detection  
- Clear frontal face view with good lighting
- Single person in the image

**Optimized for Large Datasets:**
- Supports **1600+ images** without performance issues
- **Lazy loading**: Images loaded on-demand to prevent memory issues
- Games limited to 20 rounds for optimal experience  
- **Smart memory management**: Only loads images when needed for gameplay
- **No coding required!** Just drop image files in the folder and refresh the browser.

### 3. Run the Development Server
```bash
npm run dev
```

The game will open in your browser at `http://localhost:3000`

## How It Works

1. **Face Detection**: The game loads face-api.js models to detect faces and facial landmarks
2. **Eye Extraction**: Using 68-point facial landmarks, it identifies:
   - Left and right eye regions
   - Eyebrow areas
   - Top portion of the nose bridge
3. **Image Cropping**: Creates a bounding box around the eyes area with padding
4. **Game Logic**: 
   - Randomly selects a celebrity
   - Shows the cropped eye region
   - Generates 4 multiple choice options
   - Tracks score and manages game flow

## Facial Landmarks Used

The game uses these facial landmark indexes for eye region detection:
- **Left Eye**: [33, 133, 160, 159, 158, 144, 145, 153]
- **Right Eye**: [362, 263, 387, 386, 385, 373, 374, 380]
- **Left Eyebrow**: [70-105 range]
- **Right Eyebrow**: [336-350 range]
- **Nose Bridge**: [168-197 range]

## Project Structure

```
├── public/
│   ├── images/          # Celebrity images
│   ├── models/          # face-api.js AI models
│   └── index.html       # Main HTML file
├── src/
│   ├── main.js          # Entry point
│   ├── gameScene.js     # Phaser game logic
│   ├── faceDetection.js # Face-api.js wrapper
│   └── celebrityData.js # Celebrity data
├── package.json
├── vite.config.js
└── README.md
```

## Game Flow

1. **Loading**: Downloads and initializes face detection models
2. **Round Start**: Randomly picks an unused celebrity
3. **Image Processing**: Detects face landmarks and crops eye region
4. **Question Display**: Shows cropped eyes with 4 name options
5. **Answer Selection**: Player clicks their choice
6. **Result Display**: Shows correct/incorrect with score update
7. **Next Round**: Continues until all celebrities are used
8. **Game Over**: Shows final score with restart option

## Customization

### Adding More Celebrities
1. **Simply drop PNG files** into `/public/images/`
2. **Refresh your browser** - that's it!
3. The game automatically detects new files and creates celebrity data
4. **No code changes needed!** The system is fully dynamic

### Modifying Eye Detection
Adjust the landmark indexes and padding in `src/faceDetection.js` to change how the eye region is cropped.

### Styling Changes
Modify the CSS in `index.html` to customize the appearance.

## Development Commands

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build

## Browser Compatibility

- Modern browsers with WebGL support
- Chrome, Firefox, Safari, Edge (latest versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### Models Not Loading
- Check that `/public/models/` contains all the face-api.js model files
- Ensure proper CORS settings if hosting remotely

### Face Detection Issues
- Use clear, well-lit photos with frontal face view
- Ensure single person per image
- Minimum 400x400 pixel resolution recommended

### Performance Issues
- Consider reducing image sizes
- Use JPG format for smaller file sizes
- Ensure good internet connection for model downloads

## License

MIT License - Feel free to use and modify for your projects!
