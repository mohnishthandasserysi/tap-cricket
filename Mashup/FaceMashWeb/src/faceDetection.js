import * as faceapi from 'face-api.js';

export class FaceDetectionService {
    constructor() {
        this.modelsLoaded = false;
        this.modelPath = '/models';
    }

    async loadModels() {
        if (this.modelsLoaded) return;

        try {
            console.log('Loading face detection models...');
            
            // Load the required models for face detection and landmarks
            await Promise.all([
                faceapi.nets.tinyFaceDetector.loadFromUri(this.modelPath),
                faceapi.nets.faceLandmark68Net.loadFromUri(this.modelPath),
                faceapi.nets.faceRecognitionNet.loadFromUri(this.modelPath)
            ]);

            console.log('Face detection models loaded successfully');
            this.modelsLoaded = true;
        } catch (error) {
            console.error('Error loading face detection models:', error);
            throw error;
        }
    }

    async detectFaceWithLandmarks(imageElement) {
        if (!this.modelsLoaded) {
            throw new Error('Face detection models not loaded');
        }

        try {
            // Detect face with landmarks
            const detection = await faceapi
                .detectSingleFace(imageElement, new faceapi.TinyFaceDetectorOptions())
                .withFaceLandmarks();

            if (!detection) {
                throw new Error('No face detected in image');
            }

            return detection;
        } catch (error) {
            console.error('Error detecting face:', error);
            throw error;
        }
    }

    cropEyesRegion(imageElement, landmarks) {
        console.log('🔍 Starting eye region cropping...');
        
        // Get landmark points for eyes region ONLY
        const leftEye = landmarks.getLeftEye();
        const rightEye = landmarks.getRightEye();
        const leftEyebrow = landmarks.getLeftEyeBrow();
        const rightEyebrow = landmarks.getRightEyeBrow();
        
        console.log('👁️ Left eye points:', leftEye.length);
        console.log('👁️ Right eye points:', rightEye.length);
        console.log('🤨 Left eyebrow points:', leftEyebrow.length);
        console.log('🤨 Right eyebrow points:', rightEyebrow.length);

        // Calculate bounding box for JUST the eyes region (no nose)
        const eyePoints = [...leftEye, ...rightEye, ...leftEyebrow, ...rightEyebrow];
        
        if (eyePoints.length === 0) {
            console.error('❌ No eye points detected!');
            throw new Error('No eye landmarks detected');
        }
        
        const minX = Math.min(...eyePoints.map(p => p.x));
        const maxX = Math.max(...eyePoints.map(p => p.x));
        const minY = Math.min(...eyePoints.map(p => p.y));
        const maxY = Math.max(...eyePoints.map(p => p.y));

        console.log('📏 Eye region bounds:', { minX, maxX, minY, maxY });

        // Add moderate padding around JUST the eyes
        const padding = 30; // Moderate padding for just eyes
        const cropX = Math.max(0, minX - padding);
        const cropY = Math.max(0, minY - padding);
        const cropWidth = Math.min(imageElement.width - cropX, maxX - minX + padding * 2);
        const cropHeight = Math.min(imageElement.height - cropY, maxY - minY + padding * 2);
        
        // Ensure reasonable size for eyes only
        const finalWidth = Math.max(cropWidth, 120);
        const finalHeight = Math.max(cropHeight, 80);
        
        console.log('✂️ Crop dimensions:', { cropX, cropY, cropWidth, cropHeight });
        console.log('📐 Final dimensions:', { finalWidth, finalHeight });

        // Create canvas for cropping
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        canvas.width = finalWidth;
        canvas.height = finalHeight;

        // Draw the cropped region, centered in the larger canvas
        const offsetX = (finalWidth - cropWidth) / 2;
        const offsetY = (finalHeight - cropHeight) / 2;
        
        // Fill with white background first
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, finalWidth, finalHeight);
        
        // Draw the cropped region
        ctx.drawImage(
            imageElement,
            cropX, cropY, cropWidth, cropHeight,
            offsetX, offsetY, cropWidth, cropHeight
        );

        return canvas;
    }

    async processImageForGame(imagePath) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.crossOrigin = 'anonymous';
            
            console.log(`🖼️ Loading image: ${imagePath}`);
            
            img.onload = async () => {
                console.log(`✅ Image loaded: ${imagePath}, dimensions: ${img.width}x${img.height}`);
                try {
                    // Perform face detection on the image
                    console.log('🔍 Starting face detection...');
                    const detection = await this.detectFaceWithLandmarks(img);
                    console.log('✅ Face detection successful, cropping eyes...');
                    
                    const croppedCanvas = this.cropEyesRegion(img, detection.landmarks);
                    const dataURL = croppedCanvas.toDataURL('image/png');
                    console.log('✅ Eye cropping completed');
                    
                    resolve({
                        croppedImage: dataURL,
                        originalImage: imagePath,
                        detection: detection,
                        isFallback: false
                    });
                    
                } catch (error) {
                    console.error(`❌ Face detection failed for ${imagePath}:`, error.message);
                    
                    // Skip this image - don't use fallbacks, just reject
                    reject(new Error(`Face detection failed: ${error.message}`));
                }
            };

            img.onerror = (error) => {
                console.error(`❌ Failed to load image: ${imagePath}`, error);
                reject(new Error(`Failed to load image: ${imagePath}`));
            };

            img.src = imagePath;
        });
    }
}
