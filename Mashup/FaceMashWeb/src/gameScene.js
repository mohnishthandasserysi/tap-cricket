import { celebrities, getRandomCelebrities, getCelebrityById, shuffleArray, loadCelebrityImage, celebritiesPromise } from './celebrityData.js';

export class GameScene extends Phaser.Scene {
    constructor() {
        super({ key: 'GameScene' });
    }

    preload() {
        // Game state
        this.score = 0;
        this.currentCelebrity = null;
        this.usedCelebrities = new Set();
        this.gameState = 'loading'; // loading, playing, showing_result, game_over
        this.choices = [];
        this.correctAnswer = null;
        
        // UI elements
        this.scoreElement = document.getElementById('score');
        this.choicesContainer = document.getElementById('choices');
        this.choiceButtons = [];
        for (let i = 0; i < 4; i++) {
            this.choiceButtons.push(document.getElementById(`choice-${i}`));
        }

        // Load all celebrity images
        celebrities.forEach((celebrity, index) => {
            this.load.image(`celebrity-${celebrity.id}`, celebrity.image);
        });

        // Add event listeners for choice buttons
        this.choiceButtons.forEach((button, index) => {
            button.addEventListener('click', () => {
                this.selectAnswer(index);
            });
        });
    }

    create() {
        // Set up the game canvas
        this.cameras.main.setBackgroundColor('transparent');
        
        // Create text objects for game over screen
        this.gameOverText = this.add.text(400, 250, '', {
            fontSize: '32px',
            fill: '#ffffff',
            align: 'center',
            stroke: '#000000',
            strokeThickness: 2
        }).setOrigin(0.5).setVisible(false);

        this.finalScoreText = this.add.text(400, 300, '', {
            fontSize: '24px',
            fill: '#ffffff',
            align: 'center',
            stroke: '#000000',
            strokeThickness: 2
        }).setOrigin(0.5).setVisible(false);

        this.restartText = this.add.text(400, 350, 'Click here to play again', {
            fontSize: '20px',
            fill: '#ffff00',
            align: 'center',
            stroke: '#000000',
            strokeThickness: 2
        }).setOrigin(0.5).setVisible(false).setInteractive({ useHandCursor: true });

        this.restartText.on('pointerdown', () => {
            this.restartGame();
        });

        // Start the first round
        this.startNewRound();
    }

    update() {
        // Update score display
        this.scoreElement.textContent = this.score;
    }

    async startNewRound() {
        // Wait for celebrities to be discovered if needed
        if (celebrities.length === 0) {
            console.log('🔄 Waiting for celebrity discovery to complete...');
            try {
                await celebritiesPromise;
                console.log('✅ Celebrity discovery complete, starting game');
            } catch (error) {
                console.error('❌ Celebrity discovery failed:', error);
                this.showNoImagesMessage();
                return;
            }
        }
        
        // Check if we have any celebrities at all
        if (celebrities.length === 0) {
            this.showNoImagesMessage();
            return;
        }

        // For large datasets (1600+), limit game to reasonable number of rounds
        const maxRounds = Math.min(celebrities.length, 20); // Max 20 rounds per game
        if (this.usedCelebrities.size >= maxRounds) {
            this.gameOver();
            return;
        }

        this.gameState = 'loading';
        this.hideChoices();

        try {
            // Pick a random celebrity that hasn't been used
            const availableCelebrities = celebrities.filter(c => !this.usedCelebrities.has(c.id));
            const randomIndex = Math.floor(Math.random() * availableCelebrities.length);
            this.currentCelebrity = availableCelebrities[randomIndex];
            this.usedCelebrities.add(this.currentCelebrity.id);

            // Load the celebrity's image URL (lazy loading)
            console.log('📸 Loading image for celebrity:', this.currentCelebrity.name);
            const imageUrl = await loadCelebrityImage(this.currentCelebrity);
            
            if (!imageUrl) {
                console.error('❌ Failed to load image URL for:', this.currentCelebrity.name);
                // Skip this celebrity and try another
                this.usedCelebrities.delete(this.currentCelebrity.id);
                const scene = this;
                setTimeout(() => {
                    scene.startNewRound();
                }, 100);
                return;
            }

            // Process the image to get cropped eyes
            console.log('🔍 Processing image:', imageUrl);
            console.log('👤 Celebrity name:', this.currentCelebrity.name);
            const processedImage = await this.faceDetectionService.processImageForGame(imageUrl);
            console.log('✅ Processed image result:', processedImage);

            // Create texture from cropped image
            const textureKey = `cropped-${this.currentCelebrity.id}`;
            console.log('Creating texture with key:', textureKey);
            if (this.textures.exists(textureKey)) {
                this.textures.remove(textureKey);
                console.log('Removed existing texture');
            }
            
            try {
                console.log('🎨 Cropped image data preview:', processedImage.croppedImage.substring(0, 100) + '...');
                console.log('🎨 Cropped image data length:', processedImage.croppedImage.length);
                
                // Alternative method: Create an Image element first, then add to Phaser
                const img = new Image();
                img.onload = async () => {
                    console.log('🎨 Image element loaded, dimensions:', img.width, 'x', img.height);
                    
                    // Create texture from loaded image element
                    this.textures.addImage(textureKey, img);
                    console.log('🎨 Texture created from Image element');
                    
                    // Verify the texture
                    const texture = this.textures.get(textureKey);
                    console.log('🎨 Texture verification:', texture);
                    if (texture && texture.source[0]) {
                        console.log('🎨 Texture size:', texture.source[0].width, 'x', texture.source[0].height);
                    }
                    
                    // Create the Phaser image now that texture is ready
                    await this.createPhaserImage(textureKey);
                };
                
                img.onerror = async (error) => {
                    console.error('🎨 Failed to load image element:', error);
                    // Fallback to base64 method
                    this.textures.addBase64(textureKey, processedImage.croppedImage);
                    console.log('🎨 Used fallback base64 texture creation');
                    
                    // Create Phaser image with fallback texture
                    await this.createPhaserImage(textureKey);
                };
                
                img.src = processedImage.croppedImage;
                
            } catch (error) {
                console.error('Error creating texture:', error);
                throw error;
            }

            // The Phaser image will be created in the texture onload callback

            // Game logic will be handled in createPhaserImage after texture is ready

        } catch (error) {
            console.error('Error processing celebrity image:', error);
            // Skip this celebrity and try the next one
            this.usedCelebrities.delete(this.currentCelebrity.id);
            const scene = this;
            setTimeout(() => {
                scene.startNewRound();
            }, 100);
        }
    }

    async createPhaserImage(textureKey) {
        console.log('🖼️ Creating Phaser image with texture:', textureKey);
        
        // Clear previous image
        if (this.currentImage) {
            this.currentImage.destroy();
        }

        // Add a smaller white background behind the image
        if (this.imageBackground) {
            this.imageBackground.destroy();
        }
        this.imageBackground = this.add.rectangle(400, 200, 400, 250, 0xffffff)
            .setOrigin(0.5)
            .setDepth(-1) // Behind the image
            .setStrokeStyle(2, 0x333333); // Add a subtle border
            
        console.log('🖼️ Added white background for visibility');

        // Create the Phaser image with more reasonable scaling
        this.currentImage = this.add.image(400, 200, textureKey)
            .setOrigin(0.5)
            .setScale(3) // More reasonable scale - not filling entire area
            .setDepth(1); // In front of background
            
        console.log('🖼️ Phaser image created:', this.currentImage);
        console.log('🖼️ Image texture:', this.currentImage.texture);
        console.log('🖼️ Image dimensions:', this.currentImage.width, 'x', this.currentImage.height);
        
        // Ensure visibility
        this.currentImage.setVisible(true);
        
        console.log('🖼️ Image should now be visible at 400,200');

        // Show choices after image is ready
        await this.generateChoices();
        this.showChoices();
        this.gameState = 'playing';
    }

    async generateChoices() {
        // Get up to 3 random incorrect celebrities (or whatever we have available)
        const incorrectChoices = getRandomCelebrities(this.currentCelebrity.id, 3);
        
        // Create choices array with correct answer
        this.choices = [this.currentCelebrity, ...incorrectChoices];
        
        // If we don't have enough celebrities for 4 choices, that's okay
        // The game will work with however many we have
        
        // Shuffle the choices
        this.choices = shuffleArray(this.choices);
        
        // Find the correct answer index
        this.correctAnswer = this.choices.findIndex(c => c.id === this.currentCelebrity.id);
        
        console.log('🎯 Generated choices:', this.choices.map(c => c.name));
    }

    showChoices() {
        this.choicesContainer.style.display = 'grid';
        
        this.choiceButtons.forEach((button, index) => {
            if (index < this.choices.length) {
                // Show button if we have a choice for this index
                button.textContent = this.choices[index].name;
                button.className = 'choice-button'; // Reset classes
                button.disabled = false;
                button.style.display = 'block';
            } else {
                // Hide button if we don't have enough choices
                button.style.display = 'none';
            }
        });
    }

    hideChoices() {
        this.choicesContainer.style.display = 'none';
    }

    selectAnswer(selectedIndex) {
        if (this.gameState !== 'playing') return;

        this.gameState = 'showing_result';
        
        // Disable all buttons
        this.choiceButtons.forEach(button => {
            button.disabled = true;
        });

        const isCorrect = selectedIndex === this.correctAnswer;

        if (isCorrect) {
            this.score++;
            this.choiceButtons[selectedIndex].className = 'choice-button correct';
            this.showResultMessage('Correct!', 'correct');
        } else {
            this.choiceButtons[selectedIndex].className = 'choice-button incorrect';
            this.choiceButtons[this.correctAnswer].className = 'choice-button correct';
            this.showResultMessage(`Wrong! The correct answer was ${this.currentCelebrity.name}`, 'incorrect');
        }

        // Move to next round after 2 seconds
        const scene = this;
        setTimeout(() => {
            scene.hideResultMessage();
            scene.startNewRound();
        }, 2000);
    }

    showResultMessage(message, type) {
        // Remove existing result message
        const existingMessage = document.querySelector('.result-message');
        if (existingMessage) {
            existingMessage.remove();
        }

        // Create new result message
        const messageElement = document.createElement('div');
        messageElement.className = `result-message ${type}`;
        messageElement.textContent = message;
        
        document.getElementById('game-container').appendChild(messageElement);
    }

    hideResultMessage() {
        const messageElement = document.querySelector('.result-message');
        if (messageElement) {
            messageElement.remove();
        }
    }

    gameOver() {
        this.gameState = 'game_over';
        this.hideChoices();

        if (this.currentImage) {
            this.currentImage.destroy();
        }

        // Show game over screen
        const maxRounds = Math.min(celebrities.length, 20);
        this.gameOverText.setText('Game Over!').setVisible(true);
        this.finalScoreText.setText(`Final Score: ${this.score}/${maxRounds}`).setVisible(true);
        this.restartText.setVisible(true);
    }

    restartGame() {
        // Reset game state
        this.score = 0;
        this.usedCelebrities.clear();
        this.gameState = 'loading';

        // Hide game over screen
        this.gameOverText.setVisible(false);
        this.finalScoreText.setVisible(false);
        this.restartText.setVisible(false);

        // Clear any existing images
        if (this.currentImage) {
            this.currentImage.destroy();
        }

        // Start new game
        this.startNewRound();
    }

    showNoImagesMessage() {
        // Clear any existing content
        if (this.currentImage) {
            this.currentImage.destroy();
        }

        // Show helpful message
        this.noImagesText = this.add.text(400, 150, 'No Images Found!', {
            fontSize: '32px',
            fill: '#ff6b6b',
            align: 'center',
            stroke: '#000000',
            strokeThickness: 2
        }).setOrigin(0.5);

        this.instructionsText = this.add.text(400, 200, 'Add images to: public/images/', {
            fontSize: '20px',
            fill: '#ffffff',
            align: 'center',
            stroke: '#000000',
            strokeThickness: 1
        }).setOrigin(0.5);

        this.formatText = this.add.text(400, 240, 'Supported: PNG, JPG, JPEG', {
            fontSize: '16px',
            fill: '#ffffff',
            align: 'center',
            stroke: '#000000',
            strokeThickness: 1
        }).setOrigin(0.5);

        this.namingText = this.add.text(400, 280, 'Common naming: 1.jpg, 2.jpg, image_1.png, etc.', {
            fontSize: '14px',
            fill: '#ffff00',
            align: 'center',
            stroke: '#000000',
            strokeThickness: 1
        }).setOrigin(0.5);

        this.refreshText = this.add.text(400, 320, 'Check browser console for detailed discovery logs', {
            fontSize: '14px',
            fill: '#ffff00',
            align: 'center',
            stroke: '#000000',
            strokeThickness: 1
        }).setOrigin(0.5);
    }
}
