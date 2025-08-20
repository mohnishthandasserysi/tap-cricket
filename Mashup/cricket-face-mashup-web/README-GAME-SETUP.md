# 🏏 Cricket Face Mashup Challenge - Setup Guide

## 🚀 **Quick Start (1 Click)**

**Double-click: `RUN-CRICKET-GAME.bat`**

That's it! The game will start automatically.

---

## 📁 **File Structure**

```
cricket-face-mashup-web/
├── RUN-CRICKET-GAME.bat    ⭐ MAIN LAUNCHER
├── QUICK-TEST.bat          🔧 Testing tool
├── uploads/                📸 Your cricket images go here
├── backend/                🐍 Python API server
├── frontend/               🌐 React web app
└── README-GAME-SETUP.md    📖 This file
```

---

## 🎮 **How to Play**

1. **Add Images**: Place cricket player photos in `uploads/` folder
2. **Run Game**: Double-click `RUN-CRICKET-GAME.bat`
3. **Wait**: Backend processes images (2-3 minutes for many images)
4. **Play**: Browser opens to http://localhost:3000
5. **Start**: Click "Start First Round" when ready
6. **Guess**: Identify the blended cricket players!

---

## 📸 **Image Requirements**

- **Format**: JPG, PNG, BMP
- **Content**: Clear front-facing cricket player photos
- **Naming**: Use descriptive names (e.g., `virat_kohli.jpg`)
- **Minimum**: 3 images needed to play
- **Recommended**: 10+ images for better variety

---

## 🔧 **Troubleshooting**

### "Failed to create mashup"
- **Cause**: Backend still processing images
- **Solution**: Wait 2-3 minutes, then try again

### "Backend connection failed"
- **Cause**: Backend server not started
- **Solution**: Run `RUN-CRICKET-GAME.bat` and wait for "port 8000" message

### "Port 3000 already in use"
- **Cause**: Another app using port 3000
- **Solution**: Close other development servers, then restart

### Game loads but no images
- **Cause**: No valid images in uploads folder
- **Solution**: Add cricket player images to `uploads/` folder

---

## ⚡ **Performance Notes**

- **10 images**: ~30 seconds to load
- **100 images**: ~2 minutes to load  
- **1000+ images**: ~3-5 minutes to load

Processing time depends on:
- Number of images
- Image resolution
- Face detection complexity

---

## 🎯 **Game Features**

- ✅ **Auto-image detection** from uploads folder
- ✅ **AI face blending** of 3 cricket players
- ✅ **Multiple choice quiz** with 4 options
- ✅ **Score tracking** and accuracy stats
- ✅ **Unlimited rounds** with different combinations
- ✅ **Beautiful web interface** with modern design

---

## 💡 **Pro Tips**

1. **Use professional cricket photos** for best face detection
2. **Name files descriptively** for easier identification
3. **Add 15-20 players** for optimal game variety
4. **Use high-quality images** for better blending results
5. **Avoid group photos** - one player per image works best

---

## 📊 **System Requirements**

- **OS**: Windows 10/11
- **Python**: 3.11+ (3.13 installed)
- **Node.js**: For React frontend
- **Memory**: 2GB+ RAM (for large image sets)
- **Storage**: 1GB+ free space

---

## 🎉 **Ready to Play!**

Your cricket face mashup challenge is ready with an amazing AI-powered face blending system!

**Just run `RUN-CRICKET-GAME.bat` and enjoy!** 🏏✨
