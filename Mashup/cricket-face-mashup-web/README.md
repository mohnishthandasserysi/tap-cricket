# 🏏 Cricket Face Mashup Challenge

A modern web application that uses AI to blend cricket player faces and challenges users to identify the players in the mashup. Built with React frontend and Python FastAPI backend.

## 🎮 Features

- **🎭 AI Face Blending**: Advanced face detection and blending using OpenCV
- **🏏 Cricket Player Recognition**: Upload your favorite cricket players
- **🎯 Interactive Quiz**: Multiple choice questions with real-time feedback
- **📱 Modern UI**: Beautiful, responsive design with Tailwind CSS
- **⚡ Fast Performance**: Optimized image processing and caching
- **📊 Statistics Tracking**: Score tracking and accuracy metrics

## 🛠️ Tech Stack

### Frontend
- **React 18** - Modern React with hooks
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **React Dropzone** - Drag and drop file uploads
- **Axios** - HTTP client
- **React Hot Toast** - Elegant notifications

### Backend
- **FastAPI** - Modern Python web framework
- **OpenCV** - Computer vision and image processing
- **NumPy** - Numerical computations
- **Pillow** - Image handling
- **Uvicorn** - ASGI server

## 📁 Project Structure

```
cricket-face-mashup-web/
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── App.js          # Main app component
│   │   ├── index.js        # Entry point
│   │   └── index.css       # Tailwind styles
│   ├── public/             # Static files
│   └── package.json        # Dependencies
├── backend/                # Python FastAPI server
│   ├── main.py            # FastAPI application
│   └── requirements.txt   # Python dependencies
├── uploads/               # Uploaded player images
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites
- **Node.js 16+** and **npm** (for frontend)
- **Python 3.8+** and **pip** (for backend)

### 1. Setup Backend

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
python main.py
```

The backend will run on `http://localhost:8000`

### 2. Setup Frontend

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

The frontend will run on `http://localhost:3000`

### 3. Open the Application

Visit `http://localhost:3000` in your web browser.

## 🎮 How to Play

### 1. **Upload Cricket Players**
- Drag and drop cricket player images
- Clear face photos work best
- Upload multiple players at once
- AI will detect faces automatically

### 2. **Start Playing**
- Click "Start First Round" when you have 3+ players
- AI will blend multiple player faces
- Study the mashup carefully

### 3. **Make Your Guess**
- Choose from 4 multiple choice options
- Get instant feedback
- Track your score and accuracy

### 4. **Continue Playing**
- Click "Next Round" for new mashups
- Challenge yourself with more players
- Improve your recognition skills

## 🎨 UI Features

- **Beautiful Gradients**: Modern color schemes and smooth transitions
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Drag & Drop**: Intuitive file upload experience
- **Real-time Feedback**: Instant notifications and status updates
- **Statistics Dashboard**: Track your performance over time
- **Player Gallery**: View uploaded players in grid or list view

## 🔧 API Endpoints

The FastAPI backend provides these endpoints:

- `POST /upload-players` - Upload multiple player images
- `GET /players` - Get list of uploaded players
- `POST /create-mashup` - Create a face mashup
- `POST /generate-quiz` - Generate quiz options
- `DELETE /clear-players` - Clear all players

## 🏗️ Development

### Frontend Development
```bash
cd frontend
npm start          # Start development server
npm run build      # Build for production
npm test          # Run tests
```

### Backend Development
```bash
cd backend
python main.py     # Start with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Setup
- Frontend runs on port 3000
- Backend runs on port 8000
- CORS is configured for local development

## 📸 Image Requirements

### Best Results
- **Clear face photos** with good lighting
- **Front-facing** or slightly angled faces
- **High resolution** (at least 512x512 recommended)
- **Minimal background** distractions

### Supported Formats
- JPG/JPEG
- PNG
- BMP

## 🎯 Game Mechanics

### Face Blending Process
1. **Face Detection**: OpenCV detects faces in uploaded images
2. **Feature Extraction**: Eyes, nose, and mouth regions identified
3. **Alignment**: Features resized and positioned correctly
4. **Blending**: Smooth integration using alpha blending
5. **Mashup Generation**: Combined result with multiple players

### Quiz Generation
- **Random Selection**: 3 players chosen randomly for each mashup
- **Multiple Choice**: 4 options with 1 correct answer
- **Smart Options**: Incorrect answers use other uploaded players
- **Difficulty Scaling**: More players = harder recognition

## 🚀 Deployment

### Frontend (Netlify/Vercel)
```bash
cd frontend
npm run build
# Deploy the build/ folder
```

### Backend (Heroku/Railway)
```bash
cd backend
# Add Procfile: web: uvicorn main:app --host 0.0.0.0 --port $PORT
# Deploy to your platform of choice
```

### Environment Variables
- Update `API_BASE` in frontend for production backend URL
- Configure CORS origins in backend for production frontend URL

## 🎨 Customization

### Styling
- Modify `tailwind.config.js` for custom colors/themes
- Edit `src/index.css` for global styles
- Update component styles in individual files

### Game Logic
- Adjust face blending parameters in `main.py`
- Modify quiz difficulty in mashup generation
- Add new game modes or features

## 🐛 Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version (3.8+ required)
- Install missing dependencies: `pip install -r requirements.txt`
- Verify OpenCV installation

**Frontend won't start:**
- Check Node.js version (16+ required)
- Clear npm cache: `npm cache clean --force`
- Delete node_modules and reinstall: `rm -rf node_modules && npm install`

**Face detection not working:**
- Ensure clear, front-facing face photos
- Check image quality and lighting
- Try different images if faces aren't detected

**CORS errors:**
- Ensure backend is running on port 8000
- Check CORS configuration in `main.py`
- Verify frontend is accessing correct backend URL

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **OpenCV** - Computer vision and face detection
- **React** - Frontend framework
- **FastAPI** - Backend framework
- **Tailwind CSS** - Styling framework

---

**Have fun testing your cricket player recognition skills!** 🏏👁️
