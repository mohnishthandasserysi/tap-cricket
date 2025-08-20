import Phaser from 'phaser';
import { FaceDetectionService } from './faceDetection.js';
import { GameScene } from './gameScene.js';

// Initialize the face detection service
const faceDetectionService = new FaceDetectionService();

// Extend the GameScene to include our face detection service
class MainGameScene extends GameScene {
    constructor() {
        super();
        this.faceDetectionService = faceDetectionService;
    }
}

// Phaser game configuration
const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    parent: 'game-canvas',
    backgroundColor: 'transparent',
    scale: {
        mode: Phaser.Scale.FIT,
        autoCenter: Phaser.Scale.CENTER_BOTH,
        width: 800,
        height: 600
    },
    scene: MainGameScene
};

// Debug: Check if script is loading
console.log('🚀 Main.js is loading...');

// Initialize the game after face detection models are loaded
async function initGame() {
    console.log('🎮 InitGame function called');
    try {
        const loadingElement = document.getElementById('loading');
        console.log('📄 Loading element found:', loadingElement);
        
        // Load face detection models
        await faceDetectionService.loadModels();
        
        // Hide loading screen
        loadingElement.style.display = 'none';
        
        // Start the Phaser game
        const game = new Phaser.Game(config);
        
        // Make the game globally accessible for debugging
        window.game = game;
        
    } catch (error) {
        console.error('Failed to initialize game:', error);
        document.getElementById('loading').innerHTML = `
            <div>Failed to load face detection models</div>
            <div style="font-size: 16px; margin-top: 10px;">Please refresh the page to try again</div>
        `;
    }
}

// Start the game initialization
console.log('🎯 About to call initGame...');
initGame().catch(error => {
    console.error('💥 InitGame failed:', error);
});
