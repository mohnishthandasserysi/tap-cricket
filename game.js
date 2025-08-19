class PenaltyShooter {
    constructor() {
        this.initializeGame();
        this.setupEventListeners();
        this.loadSounds();
    }

    initializeGame() {
        // Game state
        this.score = 0;
        this.attempts = 5;
        this.highScore = parseInt(localStorage.getItem('penaltyHighScore')) || 0;
        this.isGameOver = false;
        this.isShooting = false;
        this.isPowerCharging = false;
        this.selectedZone = null;
        this.powerLevel = 0;

        // DOM Elements
        this.scoreElement = document.getElementById('score');
        this.attemptsElement = document.getElementById('attempts');
        this.highScoreElement = document.getElementById('highscore');
        this.shootButton = document.getElementById('shoot-btn');
        this.restartButton = document.getElementById('restart-btn');
        this.goalkeeper = document.querySelector('.goalkeeper');
        this.ball = document.querySelector('.ball');
        this.powerMeter = document.querySelector('.power-meter');
        this.powerFill = document.querySelector('.power-fill');
        this.targetGrid = document.querySelector('.goal-target-grid');
        this.messageElement = document.getElementById('game-message');

        // Update display
        this.updateDisplay();
        this.highScoreElement.textContent = this.highScore;
    }

    setupEventListeners() {
        // Button controls
        this.shootButton.addEventListener('click', () => this.startPowerCharge());
        this.restartButton.addEventListener('click', () => this.restartGame());

        // Target zone selection
        document.querySelectorAll('.target-zone').forEach(zone => {
            zone.addEventListener('click', () => this.selectZone(zone.dataset.zone));
        });

        // Keyboard controls
        document.addEventListener('keyup', (e) => {
            if (e.code === 'Space' && this.isPowerCharging) {
                this.shoot();
            }
        });
    }

    loadSounds() {
        this.sounds = {
            cheer: document.getElementById('crowd-cheer'),
            aww: document.getElementById('crowd-aww'),
            kick: document.getElementById('ball-kick')
        };

        // Set volume levels
        Object.values(this.sounds).forEach(sound => {
            sound.volume = 0.5;
        });
    }

    startPowerCharge() {
        if (this.isGameOver || this.isShooting) return;

        this.isPowerCharging = true;
        this.shootButton.textContent = 'HOLD SPACE TO CHARGE';
        this.powerMeter.classList.add('active');
        this.targetGrid.classList.add('active');

        // Power charging animation
        let increasing = true;
        this.powerInterval = setInterval(() => {
            if (increasing) {
                this.powerLevel += 2;
                if (this.powerLevel >= 100) increasing = false;
            } else {
                this.powerLevel -= 2;
                if (this.powerLevel <= 0) increasing = true;
            }
            this.powerFill.style.width = `${this.powerLevel}%`;
        }, 20);
    }

    selectZone(zoneIndex) {
        if (!this.isPowerCharging) return;
        
        this.selectedZone = parseInt(zoneIndex);
        document.querySelectorAll('.target-zone').forEach(zone => {
            zone.classList.remove('selected');
        });
        document.querySelector(`[data-zone="${zoneIndex}"]`).classList.add('selected');
    }

    async shoot() {
        if (!this.selectedZone && this.selectedZone !== 0) {
            this.showMessage('Select a target zone!', 'error');
            return;
        }

        clearInterval(this.powerInterval);
        this.isPowerCharging = false;
        this.isShooting = true;
        this.attempts--;

        // Hide power meter and target grid
        this.powerMeter.classList.remove('active');
        this.targetGrid.classList.remove('active');
        this.updateDisplay();

        // Calculate shot parameters
        const power = this.powerLevel;
        const zonePositions = [
            {x: -150, y: 300}, {x: 0, y: 320}, {x: 150, y: 300},
            {x: -120, y: 250}, {x: 0, y: 270}, {x: 120, y: 250},
            {x: -90, y: 200}, {x: 0, y: 220}, {x: 90, y: 200}
        ];

        const targetPos = zonePositions[this.selectedZone];
        const accuracy = (power > 40 && power < 80) ? 0.9 : 0.5;

        // Add randomness based on power and accuracy
        const actualX = targetPos.x + (Math.random() - 0.5) * (100 - accuracy * 100);
        
        // Play kick sound
        this.sounds.kick.play();

        // Animate ball
        this.ball.style.setProperty('--shoot-x', `${actualX}px`);
        this.ball.classList.add('shooting');

        // Goalkeeper movement
        await this.delay(200);
        const goalkeeperMove = Math.random();
        const goalkeeperX = (goalkeeperMove * 300 - 150);
        
        this.goalkeeper.style.transform = `translateX(${goalkeeperX}px)`;
        this.goalkeeper.classList.add(goalkeeperX < 0 ? 'diving-left' : 'diving-right');

        // Determine if goal is scored
        await this.delay(1000);
        const isGoal = Math.abs(actualX - goalkeeperX) > 60 && power > 20;

        if (isGoal) {
            this.score++;
            this.showMessage('GOAL!', 'success');
            this.sounds.cheer.play();
        } else {
            this.showMessage(power < 20 ? 'Too weak!' : 'SAVED!', 'error');
            this.sounds.aww.play();
        }

        // Reset positions
        await this.delay(1500);
        this.resetPositions();

        // Check game over
        if (this.attempts === 0) {
            this.gameOver();
        }

        this.isShooting = false;
        this.shootButton.textContent = 'TAKE SHOT';
    }

    showMessage(text, type) {
        this.messageElement.textContent = text;
        this.messageElement.className = `game-message ${type} show`;
        
        setTimeout(() => {
            this.messageElement.classList.remove('show');
        }, 1500);
    }

    resetPositions() {
        this.ball.classList.remove('shooting');
        this.ball.style.transform = 'translateX(-50%)';
        this.goalkeeper.style.transform = 'translateX(-50%)';
        this.goalkeeper.classList.remove('diving-left', 'diving-right');
        this.selectedZone = null;
        this.powerLevel = 0;
        this.powerFill.style.width = '0%';
        
        document.querySelectorAll('.target-zone').forEach(zone => {
            zone.classList.remove('selected');
        });
    }

    gameOver() {
        this.isGameOver = true;
        this.shootButton.style.display = 'none';
        this.restartButton.style.display = 'block';

        if (this.score > this.highScore) {
            this.highScore = this.score;
            localStorage.setItem('penaltyHighScore', this.highScore);
            this.highScoreElement.textContent = this.highScore;
            this.showMessage(`NEW HIGH SCORE: ${this.score}!`, 'success');
        } else {
            this.showMessage(`GAME OVER! SCORE: ${this.score}`, 'error');
        }
    }

    restartGame() {
        this.score = 0;
        this.attempts = 5;
        this.isGameOver = false;
        this.isShooting = false;
        this.shootButton.style.display = 'block';
        this.restartButton.style.display = 'none';
        this.shootButton.textContent = 'TAKE SHOT';
        this.resetPositions();
        this.updateDisplay();
    }

    updateDisplay() {
        this.scoreElement.textContent = this.score;
        this.attemptsElement.textContent = this.attempts;
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize game when page loads
window.addEventListener('load', () => {
    new PenaltyShooter();
});