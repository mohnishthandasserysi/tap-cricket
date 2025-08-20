# Guess the Celebrity - Setup Guide

## Quick Start

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```

3. **Open in browser:** The game will automatically open at `http://localhost:3000`

## Current Status

✅ **Working Features:**
- Complete Phaser 3 game framework
- Face-api.js integration with model loading
- Eye region detection and cropping
- Multiple choice quiz system
- Score tracking and game flow
- Responsive mobile-friendly UI
- Fallback system for demo mode

## Current Status

The game is now configured to **automatically detect PNG images** from the `/public/images/` directory. You currently have these images:
- `Aadil_Rashid.png` → "Aadil Rashid"
- `Abhijeet_Malik.png` → "Abhijeet Malik"  
- `Abhishek_KS.png` → "Abhishek KS"
- `Abhishek_Singh.png` → "Abhishek Singh"

The game will use **real face detection** on these images!

## Adding Real Celebrity Photos

The game **automatically detects all PNG files** in the `/public/images/` directory!

1. **Simply add PNG files** to `/public/images/` with any descriptive filename:
   - `brad-pitt.png`
   - `jennifer_lawrence.png`
   - `leonardo_dicaprio.png`
   - `scarlett-johansson.png`
   - Any PNG file works!

2. **Automatic name conversion:**
   - `brad-pitt.png` → "Brad Pitt"
   - `jennifer_lawrence.png` → "Jennifer Lawrence"  
   - `robert-downey-jr.png` → "Robert Downey Jr"
   - Supports hyphens, underscores, and mixed case

3. **Photo requirements:**
   - Format: **PNG only** (for dynamic detection)
   - Size: Minimum 400x400 pixels
   - Clear frontal face view
   - Good lighting
   - Single person per image

4. **How to use:**
   - Drop PNG files in `/public/images/`
   - Refresh your browser
   - Game automatically detects and loads new images!

5. **Where to find photos:**
   - Wikimedia Commons (copyright-free)
   - Official publicity photos
   - Professional headshots
   - Stock photo sites with proper licensing

## How It Works

### Face Detection Process:
1. **Model Loading**: Downloads TensorFlow.js models for face detection
2. **Face Detection**: Locates faces using tiny face detector
3. **Landmark Detection**: Identifies 68 facial landmarks
4. **Eye Region Extraction**: Crops area from eyebrows to nose bridge
5. **Game Display**: Shows cropped eye region in Phaser canvas

### Game Flow:
1. **Loading Screen**: Downloads face detection models
2. **Round Start**: Randomly selects unused celebrity
3. **Image Processing**: Detects face and crops eye region
4. **Quiz Display**: Shows cropped eyes with 4 name choices
5. **Answer Feedback**: Displays correct/incorrect with score update
6. **Next Round**: Continues until all celebrities used
7. **Game Over**: Shows final score with restart option

## Technical Architecture

### Files Structure:
```
├── src/
│   ├── main.js          # Entry point and game initialization
│   ├── gameScene.js     # Phaser game logic and UI
│   ├── faceDetection.js # Face-api.js wrapper service
│   └── celebrityData.js # Celebrity data and utilities
├── public/
│   ├── images/          # Celebrity photos (add your own)
│   ├── models/          # Pre-loaded face-api.js models
│   └── index.html       # Main HTML with embedded CSS
```

### Key Technologies:
- **Vite**: Fast build tool and dev server
- **Phaser 3**: 2D game framework
- **face-api.js**: TensorFlow.js for face detection
- **Modern CSS**: Glassmorphism responsive design

## Troubleshooting

### Common Issues:

**"Models not loading"**
- Check internet connection
- Verify `/public/models/` contains all model files
- Check browser console for CORS errors

**"No face detected"**
- Use clear, well-lit frontal photos
- Ensure single person per image
- Try higher resolution images (400x400+)

**"Game not starting"**
- Check browser console for JavaScript errors
- Ensure all dependencies installed (`npm install`)
- Try refreshing the page

### Performance Tips:
- Use JPG format for smaller file sizes
- Optimize images to ~500KB each
- Good internet connection for model downloads
- Modern browser with WebGL support

## Customization

### Adding More Celebrities:
1. Add image files to `/public/images/`
2. Update `celebrities` array in `src/celebrityData.js`
3. Include both `image` and `fallback` paths

### Modifying Eye Detection:
- Edit landmark indexes in `src/faceDetection.js`
- Adjust padding around eye region
- Customize cropping rectangle size

### Styling Changes:
- Modify CSS in `index.html`
- Update Phaser text styles in `src/gameScene.js`
- Change color schemes and animations

## Development Commands

```bash
npm run dev     # Start development server
npm run build   # Build for production  
npm run preview # Preview production build
```

## Browser Support

- Chrome, Firefox, Safari, Edge (latest versions)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Requires WebGL support for Phaser 3

---

**Ready to play!** The game is fully functional in demo mode. Add real celebrity photos to unlock the full face detection experience!
