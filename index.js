// Phaser is loaded globally via script tag in index.html

// Start Screen Scene
class StartScene extends Phaser.Scene {
  constructor() {
    super({ key: "StartScene" });
  }

  preload() {
    // Load the same assets as main game for consistency
    this.load.image("pitch", "assets/pitch.jpg");
  }

  create() {
    // Add background pitch with darker overlay for start screen
    const bg = this.add
      .image(this.scale.width / 2, this.scale.height / 2, "pitch")
      .setDisplaySize(this.scale.width, this.scale.height)
      .setAlpha(0.3);

    // Dark overlay for better text readability
    this.add.rectangle(
      this.scale.width / 2,
      this.scale.height / 2,
      this.scale.width,
      this.scale.height,
      0x000000,
      0.6
    );

    // Main title
    const titleSize = Math.min(this.scale.width * 0.12, 60);
    this.add
      .text(this.scale.width / 2, this.scale.height * 0.25, "TAP CRICKET", {
        fontSize: `${titleSize}px`,
        fill: "#ffffff",
        stroke: "#000000",
        strokeThickness: 4,
        fontFamily: "Rubik, sans-serif",
        fontWeight: "700",
        letterSpacing: 3,
      })
      .setOrigin(0.5);

    // Subtitle
    const subtitleSize = Math.min(this.scale.width * 0.05, 24);
    this.add
      .text(
        this.scale.width / 2,
        this.scale.height * 0.35,
        "Test your timing skills!",
        {
          fontSize: `${subtitleSize}px`,
          fill: "#e9fff6",
          fontFamily: "Rubik, sans-serif",
          fontWeight: "400",
        }
      )
      .setOrigin(0.5);

    // Game rules
    const rulesSize = Math.min(this.scale.width * 0.04, 18);
    const rulesText =
      "• You have 5 wickets\n• Tap when ball reaches the crease\n• Perfect timing = Maximum runs\n• Missing the ball = Lost wicket";
    this.add
      .text(this.scale.width / 2, this.scale.height * 0.5, rulesText, {
        fontSize: `${rulesSize}px`,
        fill: "#ffffff",
        fontFamily: "Rubik, sans-serif",
        fontWeight: "400",
        align: "center",
        lineSpacing: 8,
      })
      .setOrigin(0.5);

    // High Score display
    const highScore = Number(localStorage.getItem("tapcricket_highscore") || 0);
    const highScoreSize = Math.min(this.scale.width * 0.045, 22);
    this.add
      .text(
        this.scale.width / 2,
        this.scale.height * 0.65,
        `High Score: ${highScore}`,
        {
          fontSize: `${highScoreSize}px`,
          fill: "#ffd700",
          stroke: "#000000",
          strokeThickness: 2,
          fontFamily: "Rubik, sans-serif",
          fontWeight: "600",
        }
      )
      .setOrigin(0.5);

    // Start button
    const buttonSize = Math.min(this.scale.width * 0.06, 28);
    const startButton = this.add
      .text(this.scale.width / 2, this.scale.height * 0.8, "TAP TO START", {
        fontSize: `${buttonSize}px`,
        fill: "#44ff44",
        stroke: "#000000",
        strokeThickness: 3,
        fontFamily: "Rubik, sans-serif",
        fontWeight: "700",
        letterSpacing: 2,
      })
      .setOrigin(0.5);

    // Button animation
    this.tweens.add({
      targets: startButton,
      alpha: 0.7,
      duration: 800,
      yoyo: true,
      repeat: -1,
      ease: "Power2",
    });

    // Input handling
    this.input.on("pointerdown", () => {
      this.scene.start("TapCricketScene");
    });

    // Handle resize
    this.scale.on("resize", this.handleResize, this);
  }

  handleResize() {
    // Update positions for responsive design
    const width = this.scale.gameSize.width;
    const height = this.scale.gameSize.height;

    // Recreate the scene elements with new dimensions
    this.scene.restart();
  }
}

// Game Over Scene
class GameOverScene extends Phaser.Scene {
  constructor() {
    super({ key: "GameOverScene" });
  }

  init(data) {
    this.finalScore = data.score || 0;
    this.highScore = data.highScore || 0;
    this.isNewHighScore = data.isNewHighScore || false;
  }

  create() {
    // Add background with overlay
    this.add.rectangle(
      this.scale.width / 2,
      this.scale.height / 2,
      this.scale.width,
      this.scale.height,
      0x000000,
      0.8
    );

    // Game Over title
    const titleSize = Math.min(this.scale.width * 0.1, 50);
    this.add
      .text(this.scale.width / 2, this.scale.height * 0.25, "GAME OVER", {
        fontSize: `${titleSize}px`,
        fill: "#ff4444",
        stroke: "#000000",
        strokeThickness: 4,
        fontFamily: "Rubik, sans-serif",
        fontWeight: "700",
        letterSpacing: 2,
      })
      .setOrigin(0.5);

    // All wickets lost message
    const messageSize = Math.min(this.scale.width * 0.045, 22);
    this.add
      .text(
        this.scale.width / 2,
        this.scale.height * 0.35,
        "All 5 wickets lost!",
        {
          fontSize: `${messageSize}px`,
          fill: "#ffffff",
          fontFamily: "Rubik, sans-serif",
          fontWeight: "400",
        }
      )
      .setOrigin(0.5);

    // Final Score
    const scoreSize = Math.min(this.scale.width * 0.08, 40);
    this.add
      .text(
        this.scale.width / 2,
        this.scale.height * 0.45,
        `Final Score: ${this.finalScore}`,
        {
          fontSize: `${scoreSize}px`,
          fill: "#ffffff",
          stroke: "#000000",
          strokeThickness: 3,
          fontFamily: "Rubik, sans-serif",
          fontWeight: "600",
        }
      )
      .setOrigin(0.5);

    // High Score with special styling if it's new
    const highScoreColor = this.isNewHighScore ? "#ffd700" : "#44ff44";
    const highScoreText = this.isNewHighScore
      ? `NEW HIGH SCORE: ${this.highScore}!`
      : `High Score: ${this.highScore}`;

    this.add
      .text(this.scale.width / 2, this.scale.height * 0.55, highScoreText, {
        fontSize: `${scoreSize * 0.8}px`,
        fill: highScoreColor,
        stroke: "#000000",
        strokeThickness: 2,
        fontFamily: "Rubik, sans-serif",
        fontWeight: "600",
      })
      .setOrigin(0.5);

    // New high score celebration
    if (this.isNewHighScore) {
      const celebration = this.add
        .text(
          this.scale.width / 2,
          this.scale.height * 0.62,
          "🎉 CONGRATULATIONS! 🎉",
          {
            fontSize: `${messageSize}px`,
            fill: "#ffd700",
            fontFamily: "Rubik, sans-serif",
            fontWeight: "500",
          }
        )
        .setOrigin(0.5);

      // Celebration animation
      this.tweens.add({
        targets: celebration,
        scale: 1.1,
        duration: 600,
        yoyo: true,
        repeat: -1,
        ease: "Power2",
      });
    }

    // Play Again button
    const buttonSize = Math.min(this.scale.width * 0.06, 28);
    const playAgainButton = this.add
      .text(this.scale.width / 2, this.scale.height * 0.75, "PLAY AGAIN", {
        fontSize: `${buttonSize}px`,
        fill: "#44ff44",
        stroke: "#000000",
        strokeThickness: 3,
        fontFamily: "Rubik, sans-serif",
        fontWeight: "700",
        letterSpacing: 2,
      })
      .setOrigin(0.5);

    // Main Menu button
    const menuButton = this.add
      .text(this.scale.width / 2, this.scale.height * 0.85, "MAIN MENU", {
        fontSize: `${buttonSize * 0.8}px`,
        fill: "#ffffff",
        stroke: "#000000",
        strokeThickness: 2,
        fontFamily: "Rubik, sans-serif",
        fontWeight: "500",
      })
      .setOrigin(0.5);

    // Button animations
    this.tweens.add({
      targets: playAgainButton,
      alpha: 0.7,
      duration: 800,
      yoyo: true,
      repeat: -1,
      ease: "Power2",
    });

    // Input handling
    this.input.on("pointerdown", (pointer) => {
      if (
        Phaser.Geom.Rectangle.Contains(
          playAgainButton.getBounds(),
          pointer.x,
          pointer.y
        )
      ) {
        this.scene.start("TapCricketScene");
      } else if (
        Phaser.Geom.Rectangle.Contains(
          menuButton.getBounds(),
          pointer.x,
          pointer.y
        )
      ) {
        this.scene.start("StartScene");
      }
    });
  }
}

// Main Game Scene
class TapCricketScene extends Phaser.Scene {
  constructor() {
    super({ key: "TapCricketScene" });
  }

  preload() {
    // Load assets (replace with your own images)
    this.load.image("pitch", "assets/pitch.jpg"); // vertical pitch bg
    this.load.image("ball", "assets/ball.png"); // cricket ball

    // Try to load batter sprite sheet, with fallback if missing
    this.batterSpriteMissing = false;

    this.load.on("loaderror", (file) => {
      if (file.key === "batter") {
        console.warn("Batter sprite sheet not found, will use fallback");
        this.batterSpriteMissing = true;
      }
    });

    // Load batter sprite sheet for animations
    this.load.spritesheet("batter", "assets/batter.png", {
      frameWidth: 450, // Estimated - adjust based on actual dimensions
      frameHeight: 600, // Estimated - adjust based on actual dimensions
    });

    // Load wicket sprite sheet
    this.load.spritesheet("wicket", "assets/wicket.png", {
      frameWidth: 540, // Half of 540 since we have 2 frames
      frameHeight: 302,
    });

    // Debug loading
    this.load.on("complete", () => {
      console.log("Wicket sprite sheet loaded:", this.textures.get("wicket"));
    });
    // this.load.image("bat", "assets/bat.png"); // bat sprite (replaced with spritesheet)
  }

  init() {
    // Game state variables
    this.score = 0;
    this.wickets = 0;
    this.maxWickets = 5;
    this.highScore = Number(localStorage.getItem("tapcricket_highscore") || 0);
    this.ballSpeed = 0;
    this.deliveryType = "";
    this.ballHasBounced = false;
    this.activeBall = null;
    this.creaseY = 0;
  }

  create() {
    // Initialize dynamic shadows (disabled temporarily to debug)
    this.shadowOffset = { x: 2, y: 2 };
    // this.time.addEvent({
    //   delay: 100,
    //   callback: this.updateDynamicShadows,
    //   callbackScope: this,
    //   loop: true,
    // });

    // Handle orientation changes
    this.scale.on("resize", this.handleResize, this);
    this.handleResize();

    // Add background pitch
    this.add
      .image(this.scale.width / 2, this.scale.height / 2, "pitch")
      .setDisplaySize(this.scale.width, this.scale.height);

    // Note: Ball asset is now loaded from assets/ball.png

    // Define batting crease position (where ball should be hit)
    this.creaseY = this.scale.height - 150; // Back to original position before batter sprite

    // Add visible batting crease line (simplified)
    try {
      this.creaseGraphics = this.add.graphics();
      this.creaseGraphics.lineBetween(
        this.scale.width * 0.3,
        this.creaseY,
        this.scale.width * 0.7,
        this.creaseY
      );
    } catch (error) {
      console.error("Error creating crease graphics:", error);
      // Fallback: create a simple rectangle instead
      this.creaseGraphics = this.add.rectangle(
        this.scale.width / 2,
        this.creaseY,
        this.scale.width * 0.4,
        4,
        0xffffff,
        0.8
      );
    }

    // Add wicket at bottom (batter's perspective)
    // Create wicket animations with debug logging
    try {
      // Create idle animation
      const idleAnim = this.anims.create({
        key: "wicket-idle",
        frames: this.anims.generateFrameNumbers("wicket", { start: 0, end: 0 }),
        frameRate: 8,
        repeat: -1,
      });
      console.log("Idle animation created:", idleAnim);

      // Create hit animation
      const hitAnim = this.anims.create({
        key: "wicket-hit",
        frames: this.anims.generateFrameNumbers("wicket", { start: 0, end: 7 }),
        frameRate: 20,
        repeat: 0, // Only play once
      });
      console.log("Hit animation created:", hitAnim);

      // Log all available animations
      console.log("All animations:", this.anims.anims.entries);
    } catch (error) {
      console.error("Error creating animations:", error);
    }

    // Add wicket sprite and play animation
    this.stumps = this.add
      .sprite(this.scale.width / 2, this.scale.height - 50, "wicket") // Adjusted Y position
      .setScale(0.6) // Increased scale to make it more visible
      .setDepth(2) // Set a higher depth to bring it to the front
      .setOrigin(0.5, 0.7); // Set origin to bottom center of sprite

    // Debug rectangle to show wicket bounds

    console.log("Wicket position:", {
      x: this.stumps.x,
      y: this.stumps.y,
      originX: this.stumps.originX,
      originY: this.stumps.originY,
      displayHeight: this.stumps.displayHeight,
      displayWidth: this.stumps.displayWidth,
    });

    // For debugging - add a colored rectangle behind the wicket to check its position

    // Start playing the animation
    this.stumps.play("wicket-idle");

    // Add batter sprite with animations or fallback
    this.createBatter();

    // Create batter animations (if sprite sheet loaded)
    if (!this.batterSpriteMissing) {
      this.createBatterAnimations();
    }

    // Ball group
    this.balls = this.physics.add.group();

    // Score display with responsive font size and bottom margin
    const scoreSize = Math.min(this.scale.width * 0.08, 40); // Increased size
    const scoreMarginTop = Math.min(this.scale.width * 0.04, 20); // Top margin
    const scoreMarginBottom = Math.min(this.scale.width * 0.06, 30); // Bottom margin

    this.scoreText = this.add
      .text(this.scale.width * 0.05, scoreMarginTop, "Score: 0", {
        fontSize: `${scoreSize}px`,
        fill: "#ffffff",
        stroke: "#000000",
        strokeThickness: 4, // Increased stroke for better visibility
        fontFamily: "Rubik, sans-serif",
        fontWeight: "700", // Bold weight for main score
        letterSpacing: 1, // Better readability for numbers
      })
      .setScrollFactor(0);

    // High Score display in top right
    const highScoreSize = Math.min(this.scale.width * 0.06, 30);
    this.highScoreText = this.add
      .text(
        this.scale.width * 0.95,
        scoreMarginTop,
        `High: ${this.highScore}`,
        {
          fontSize: `${highScoreSize}px`,
          fill: "#ffd700",
          stroke: "#000000",
          strokeThickness: 3,
          fontFamily: "Rubik, sans-serif",
          fontWeight: "600",
          letterSpacing: 1,
        }
      )
      .setOrigin(1, 0)
      .setScrollFactor(0);

    // Wickets display
    const wicketsSize = Math.min(this.scale.width * 0.05, 24);
    this.wicketsText = this.add
      .text(
        this.scale.width * 0.05,
        scoreMarginTop + scoreSize + 10,
        `Wickets Left: ${this.maxWickets - this.wickets}`,
        {
          fontSize: `${wicketsSize}px`,
          fill: "#ff6b6b",
          stroke: "#000000",
          strokeThickness: 2,
          fontFamily: "Rubik, sans-serif",
          fontWeight: "600",
        }
      )
      .setScrollFactor(0);

    // Delivery type display with enhanced visibility - positioned to avoid overlap
    const deliverySize = Math.min(this.scale.width * 0.06, 28); // Slightly larger
    this.deliveryText = this.add
      .text(this.scale.width / 2, this.scale.height * 0.12, "", {
        fontSize: `${deliverySize}px`,
        fill: "#ffffff", // Default color, will be changed per delivery
        stroke: "#000000",
        strokeThickness: 2, // Thinner stroke for sharper look
        fontFamily: "Rubik, sans-serif",
        fontWeight: "700", // Keep bold for readability
        letterSpacing: 4, // Increased letter spacing for better readability
      })
      .setOrigin(0.5, 0.5) // Center the text
      .setScrollFactor(0);

    // Enhanced touch input handling
    this.input.on("pointerdown", (pointer) => {
      // Store initial touch position
      this.touchStartY = pointer.y;
      this.swingBat();
    });

    this.input.on("pointermove", (pointer) => {
      if (pointer.isDown) {
        // Calculate swipe distance
        const swipeDistance = pointer.y - this.touchStartY;
        // Adjust bat angle based on swipe
        if (Math.abs(swipeDistance) > 10) {
          this.bat.angle = Phaser.Math.Clamp(swipeDistance * 0.5, -60, 60);
        }
      }
    });

    this.input.on("pointerup", () => {
      // Reset bat angle
      this.tweens.add({
        targets: this.bat,
        angle: 0,
        duration: 200,
        ease: "Power2",
      });
    });

    // Start with first ball after a delay
    this.time.delayedCall(2000, () => {
      this.spawnBall();
    });
  }

  createBatter() {
    if (this.batterSpriteMissing || !this.textures.exists("batter")) {
      // Create fallback batter using graphics
      console.log("Creating fallback batter graphics");
      this.createFallbackBatter();
    } else {
      console.log("BATTER FOUND");
      // Use sprite sheet
      this.batter = this.add
        .sprite(
          this.scale.width / 2,
          this.scale.height - 240, // Moved forward (lower Y value = forward on pitch)
          "batter",
          0 // Start with first frame (ready stance)
        )
        .setScale(0.5);
    }
  }

  createFallbackBatter() {
    // Create a simple batter using basic shapes
    this.batter = this.add.container(
      this.scale.width / 2,
      this.scale.height - 240 // Moved forward to match sprite position
    );

    // Head
    const head = this.add.circle(0, -40, 8, 0xffdbac);

    // Body
    const body = this.add.rectangle(0, -20, 12, 30, 0x4169e1);

    // Arms
    const leftArm = this.add.rectangle(-8, -25, 4, 20, 0xffdbac);
    const rightArm = this.add.rectangle(8, -25, 4, 20, 0xffdbac);

    // Legs
    const leftLeg = this.add.rectangle(-4, 0, 6, 25, 0x000080);
    const rightLeg = this.add.rectangle(4, 0, 6, 25, 0x000080);

    // Bat
    this.batterBat = this.add.rectangle(12, -15, 3, 25, 0x8b4513);

    // Add all parts to container
    this.batter.add([
      head,
      body,
      leftArm,
      rightArm,
      leftLeg,
      rightLeg,
      this.batterBat,
    ]);
    this.batter.setScale(0.8);

    // Store original bat position for animations
    this.batterBat.originalRotation = 0;
  }

  createBatterAnimations() {
    // Create different batting animations based on the sprite sheet
    // Adjust frame numbers based on actual sprite sheet layout

    // Ready/Idle stance (frame 0-1, slow loop)
    this.anims.create({
      key: "batter-ready",
      frames: this.anims.generateFrameNumbers("batter", { start: 0, end: 1 }),
      frameRate: 2,
      repeat: -1,
    });

    // Pre-swing preparation (frames 2-3)
    this.anims.create({
      key: "batter-prepare",
      frames: this.anims.generateFrameNumbers("batter", { start: 2, end: 3 }),
      frameRate: 8,
      repeat: 0,
    });

    // Full swing animation (frames 4-7)
    this.anims.create({
      key: "batter-swing",
      frames: this.anims.generateFrameNumbers("batter", { start: 4, end: 7 }),
      frameRate: 12,
      repeat: 0,
    });

    // Follow-through/hit animation (frames 8-9)
    this.anims.create({
      key: "batter-followthrough",
      frames: this.anims.generateFrameNumbers("batter", { start: 8, end: 9 }),
      frameRate: 6,
      repeat: 0,
    });

    // Start with ready stance
    this.batter.play("batter-ready");
  }

  animateFallbackSwing() {
    // Animate the bat swing for fallback batter
    if (this.batterBat) {
      this.tweens.add({
        targets: this.batterBat,
        rotation: -1.2, // Swing bat
        duration: 150,
        ease: "Power2.Out",
        yoyo: true,
        onComplete: () => {
          // Return to original position
          this.batterBat.rotation = this.batterBat.originalRotation;
        },
      });
    }
  }

  scheduleNextBall() {
    // Variable delay between balls (3 to 5 seconds) - only called after current ball is finished
    const delay = Phaser.Math.Between(3000, 5000);
    console.log(`Next ball scheduled in ${delay}ms`);
    this.time.delayedCall(delay, () => {
      console.log("Attempting to spawn next ball");
      this.spawnBall();
    });
  }

  spawnBall() {
    // Don't spawn if there's already an active ball
    if (this.activeBall && this.activeBall.active) {
      console.log("Cannot spawn - ball already active");
      return;
    }

    console.log("Spawning new ball");

    // Ensure batter is in ready stance for new ball
    if (this.batter && this.batter.active && !this.batterSpriteMissing) {
      this.batter.play("batter-ready");
      this.batter.setFrame(0);
    }

    // Determine delivery type and speed
    const deliveryTypes = [
      { type: "Fast", speed: 350, difficulty: 3, runs: 6 },
      { type: "Medium", speed: 250, difficulty: 2, runs: 4 },
      { type: "Slow", speed: 150, difficulty: 1, runs: 2 },
    ];

    const delivery = Phaser.Utils.Array.GetRandom(deliveryTypes);
    this.deliveryType = delivery.type;
    this.ballSpeed = delivery.speed;

    // Display delivery type with enhanced animation and colors
    // Color scheme with enhanced contrast and readability
    const deliveryColors = {
      Fast: { text: "#FF4D4D", stroke: "#800000" }, // Bright red with darker stroke
      Medium: { text: "#FFA726", stroke: "#873600" }, // Softer orange
      Slow: { text: "#66BB6A", stroke: "#1B5E20" }, // Muted green
    };

    const ballColor = deliveryColors[delivery.type];
    this.deliveryText.setText(`${delivery.type} Ball`);
    this.deliveryText.setAlpha(0).setScale(0.8);
    this.deliveryText.setColor(ballColor.text);
    this.deliveryText.setStroke(ballColor.stroke, 3);

    // Entrance animation
    this.tweens.add({
      targets: this.deliveryText,
      alpha: 1,
      scale: 1,
      duration: 300,
      ease: "Back.easeOut",
      onStart: () => {
        // Clean look without shadow
        try {
          if (
            this.deliveryText &&
            this.deliveryText.active &&
            this.deliveryText.scene
          ) {
            this.deliveryText.setShadow(0, 0, "transparent", 0);
          }
        } catch (error) {
          console.error("Error setting delivery text shadow:", error);
        }
      },
    });

    // Exit animation
    this.time.delayedCall(800, () => {
      this.tweens.add({
        targets: this.deliveryText,
        alpha: 0,
        scale: 0.9,
        duration: 400,
        ease: "Back.easeIn",
        onComplete: () => {
          this.deliveryText.setShadow(0, 0, "#000000", 0);
        },
      });
    });

    // Spawn ball at bowler's end (around 400px from top)
    const bowlerPositionY = 400 + Phaser.Math.Between(-20, 20); // Around 400px with variation

    const startX = this.scale.width / 2 + Phaser.Math.Between(-20, 20); // slight variation
    const startY = bowlerPositionY;

    this.activeBall = this.physics.add
      .image(startX, startY, "ball")
      .setScale(0.035);
    this.activeBall.setData("delivery", delivery);
    this.activeBall.setData("hasBounced", false);
    this.activeBall.setData("canHit", false);
    this.balls.add(this.activeBall);

    // Set initial velocity for bowling arc
    const targetX = this.scale.width / 2;
    // Calculate realistic bounce position for good length delivery
    const remainingDistance = this.creaseY - bowlerPositionY;
    const bounceY = bowlerPositionY + remainingDistance * 0.65; // Bounce at good length (65% of remaining distance)

    // Calculate arc trajectory
    this.createBowlingArc(
      this.activeBall,
      startX,
      startY,
      targetX,
      bounceY,
      delivery.speed
    );
  }

  createBowlingArc(ball, startX, startY, targetX, bounceY, speed) {
    // Create a realistic bowling arc using tweens
    const arcHeight = -100; // How high the arc goes
    const duration = 800 - speed + 400; // Faster balls take less time

    // First part: ball travels in arc to bounce point
    this.tweens.add({
      targets: ball,
      x: targetX,
      y: bounceY,
      duration: duration * 0.7,
      ease: "Quad.Out",
      onComplete: () => {
        this.ballBounce(ball, targetX, bounceY, speed);
      },
    });

    // Add slight arc effect by adjusting y position
    this.tweens.add({
      targets: ball,
      y: startY + arcHeight,
      duration: duration * 0.35,
      ease: "Quad.Out",
      yoyo: true,
      repeat: 0,
    });
  }

  ballBounce(ball, bounceX, bounceY, speed) {
    if (!ball.active) return;

    ball.setData("hasBounced", true);
    ball.setData("canHit", true);

    // Bounce effect - ball goes up slightly then continues past batter
    const bounceHeight = 30;
    const finalY = this.scale.height - 200; // Pass closer to batter position

    // Bounce up
    this.tweens.add({
      targets: ball,
      y: bounceY - bounceHeight,
      duration: 150,
      ease: "Quad.Out",
      onComplete: () => {
        // Then down to crease
        this.tweens.add({
          targets: ball,
          y: finalY,
          duration: 200,
          ease: "Quad.In",
          onComplete: () => {
            // Ball continues past crease if not hit
            if (ball.active && ball.getData("canHit")) {
              this.tweens.add({
                targets: ball,
                y: this.scale.height + 50,
                duration: 300,
                ease: "Quad.In",
                onComplete: () => {
                  this.missedBall(ball);
                },
              });
            }
          },
        });
      },
    });
  }

  missedBall(ball) {
    console.log("Ball missed completely - Wicket lost!");

    // Increment wickets lost
    this.wickets += 1;
    this.updateWicketsDisplay();

    // Play wicket hit animation
    if (this.stumps && this.stumps.active) {
      console.log("Attempting to play wicket-hit animation");

      try {
        // Stop any current animation
        this.stumps.stop();

        // Play hit animation (frames only, no position change)
        this.stumps.play("wicket-hit");
        console.log("Current animation:", this.stumps.anims.currentAnim);

        // Handle animation completion
        this.stumps.once("animationcomplete", () => {
          console.log("Hit animation complete, returning to idle");
          this.stumps.play("wicket-idle", true); // Force play idle animation
        });
      } catch (error) {
        console.error("Error playing wicket animation:", error);
      }
    }

    // Show wicket lost feedback
    this.showWicketFeedback();

    if (ball && ball.active) {
      ball.destroy();
    }
    if (this.activeBall === ball) {
      this.activeBall = null;
    }

    // Check if game is over (all wickets lost)
    if (this.wickets >= this.maxWickets) {
      console.log("All wickets lost - Game Over!");
      this.gameOver();
    } else {
      // Continue with next ball
      console.log("Scheduling next ball after wicket loss");
      this.scheduleNextBall();
    }
  }

  swingBat() {
    if (this.batterSpriteMissing || !this.textures.exists("batter")) {
      // Animate fallback batter
      this.animateFallbackSwing();
    } else {
      // Play sprite animation sequence
      this.batter.play("batter-prepare");

      // After preparation, play swing
      this.batter.once("animationcomplete-batter-prepare", () => {
        this.batter.play("batter-swing");
      });

      // After swing, return to ready stance if no hit was successful
      this.batter.once("animationcomplete-batter-swing", () => {
        // Return to ready stance after a brief delay if no other animation is triggered
        this.time.delayedCall(200, () => {
          if (this.batter && this.batter.active) {
            this.batter.play("batter-ready");
          }
        });
      });
    }

    // Check if there's an active ball and provide timing feedback regardless
    if (this.activeBall && this.activeBall.active) {
      const ball = this.activeBall;
      const delivery = ball.getData("delivery");
      const batterY = this.scale.height - 240; // Batter position
      const distanceFromBatter = Math.abs(ball.y - batterY);
      const timingFeedback = this.getTimingFeedback(
        ball.y,
        batterY,
        distanceFromBatter
      );
      const canHit = ball.getData("canHit");

      // Always show timing feedback when player taps
      console.log(`=== SWING ATTEMPT ===`);
      console.log(`Ball Y: ${Math.round(ball.y)}, Batter Y: ${batterY}`);
      console.log(`Distance: ${Math.round(distanceFromBatter)}`);
      console.log(`Timing: ${timingFeedback}`);
      console.log(`Ball can be hit: ${canHit}`);
      console.log(`Ball has bounced: ${ball.getData("hasBounced")}`);
      console.log(
        `Delivery: ${delivery.type} (Difficulty: ${delivery.difficulty})`
      );

      if (canHit) {
        // Ball is in hittable state
        const timingAccuracy = this.calculateTimingAccuracy(
          distanceFromBatter,
          delivery.difficulty
        );
        console.log(`Accuracy: ${Math.round(timingAccuracy * 100)}%`);

        if (timingAccuracy > 0.1) {
          console.log(
            `✅ HIT! (${Math.round(timingAccuracy * 100)}% accuracy)`
          );
          this.hitBall(ball, delivery, timingAccuracy);
        } else {
          console.log(`❌ MISS! You were ${timingFeedback.toLowerCase()}`);
          this.missedSwing(ball);
        }
      } else {
        // Ball is not in hittable state yet (too early)
        if (ball.getData("hasBounced")) {
          console.log(`⚠️ SWING TOO LATE - Ball already past hitting zone`);
        } else {
          console.log(`⚠️ SWING TOO EARLY - Ball hasn't bounced yet`);
        }
      }
    } else {
      // No active ball
      console.log(`❌ NO BALL ACTIVE - Wait for next delivery`);
    }
  }

  calculateTimingAccuracy(distance, difficulty) {
    // Perfect timing when ball is near batter (distance = 0)
    // Much larger timing window for sprite-based gameplay
    const maxDistance = 80 + difficulty * 20; // Very generous timing window
    const accuracy = Math.max(0, 1 - distance / maxDistance);
    return accuracy;
  }

  getTimingFeedback(ballY, batterY, distance) {
    // Determine if player was early, late, or on time
    const battingZoneStart = batterY - 60; // Zone starts 60px before batter
    const battingZoneEnd = batterY + 40; // Zone ends 40px after batter

    if (ballY < battingZoneStart) {
      // Ball hasn't reached the batting zone yet
      const earlyDistance = battingZoneStart - ballY;
      if (earlyDistance > 100) {
        return "WAY TOO EARLY";
      } else if (earlyDistance > 50) {
        return "TOO EARLY";
      } else {
        return "EARLY";
      }
    } else if (ballY > battingZoneEnd) {
      // Ball has passed the batting zone
      const lateDistance = ballY - battingZoneEnd;
      if (lateDistance > 100) {
        return "WAY TOO LATE";
      } else if (lateDistance > 50) {
        return "TOO LATE";
      } else {
        return "LATE";
      }
    } else {
      // Ball is in the batting zone
      const centerDistance = Math.abs(ballY - batterY);
      if (centerDistance < 10) {
        return "PERFECT TIMING";
      } else if (centerDistance < 25) {
        return "GOOD TIMING";
      } else {
        return "OK TIMING";
      }
    }
  }

  hitBall(ball, delivery, accuracy) {
    // Stop all ball tweens
    this.tweens.killTweensOf(ball);

    // Calculate runs based on timing accuracy and delivery type
    let runs = 0;
    if (accuracy > 0.8) {
      runs = delivery.runs; // Perfect timing gets max runs
    } else if (accuracy > 0.6) {
      runs = Math.floor(delivery.runs * 0.7); // Good timing
    } else {
      runs = Math.floor(delivery.runs * 0.3); // Okay timing
    }

    // Update score with animation
    this.score += runs;
    const oldScore = Number(this.scoreText.text.split(": ")[1]);
    this.scoreText.setText(`Score: ${this.score}`);

    // Update high score if necessary
    this.updateHighScore();

    // Animate score change
    if (this.score > oldScore) {
      // Subtle scale and glow effect for score increase
      this.tweens.add({
        targets: this.scoreText,
        scaleX: 1.15,
        scaleY: 1.15,
        duration: 150,
        yoyo: true,
        ease: "Back.easeOut",
        onStart: () => {
          // Add golden glow effect
          try {
            if (
              this.scoreText &&
              this.scoreText.active &&
              this.scoreText.scene
            ) {
              this.scoreText.setShadow(0, 0, "#ffd700", 8, true, true);
            }
          } catch (error) {
            console.error("Error setting score shadow:", error);
          }
        },
        onComplete: () => {
          // Remove glow effect smoothly
          this.tweens.add({
            targets: this.scoreText,
            duration: 200,
            onComplete: () => {
              try {
                if (
                  this.scoreText &&
                  this.scoreText.active &&
                  this.scoreText.scene
                ) {
                  this.scoreText.setShadow(2, 2, "#000000", 2, false);
                }
              } catch (error) {
                console.error("Error removing score shadow:", error);
              }
            },
          });
        },
      });
    }

    // Show runs feedback
    this.showRunsFeedback(runs, accuracy);

    // Realistic cricket ball trajectory based on runs scored
    this.animateBallTrajectory(ball, runs, accuracy);

    // Show successful hit animation
    if (this.batterSpriteMissing || !this.textures.exists("batter")) {
      // Fallback hit celebration - just a little jump
      if (this.batter) {
        this.tweens.add({
          targets: this.batter,
          y: this.batter.y - 10,
          duration: 200,
          yoyo: true,
          ease: "Power2.Out",
        });
      }
    } else {
      this.batter.play("batter-followthrough");
      this.batter.once("animationcomplete-batter-followthrough", () => {
        if (this.batter && this.batter.active) {
          this.batter.play("batter-ready");
          // Ensure we're on the first frame
          this.time.delayedCall(100, () => {
            if (this.batter && this.batter.active) {
              this.batter.setFrame(0);
            }
          });
        }
      });
    }
  }

  missedSwing(ball) {
    // Player swung but missed - ball continues
    console.log("Missed swing!");

    // Complete swing animation even on miss, then return to ready
    this.time.delayedCall(300, () => {
      if (this.batter && this.batter.active) {
        this.batter.play("batter-ready");
        // Ensure we're on the first frame
        this.time.delayedCall(100, () => {
          if (this.batter && this.batter.active) {
            this.batter.setFrame(0);
          }
        });
      }
    });
  }

  showRunsFeedback(runs, accuracy) {
    let feedbackText = "";
    let color = "#ffffff";

    if (runs === 0) {
      feedbackText = "NO RUNS!";
      color = "#ff4444";
    } else if (accuracy > 0.8) {
      feedbackText = `${runs} RUNS! PERFECT!`;
      color = "#44ff44";
    } else if (accuracy > 0.6) {
      feedbackText = `${runs} RUNS! GOOD!`;
      color = "#ffff44";
    } else {
      feedbackText = `${runs} RUNS`;
      color = "#ffffff";
    }

    // Dynamic feedback size based on importance
    const baseFeedbackSize = Math.min(this.scale.width * 0.09, 42);
    const feedbackSize =
      accuracy > 0.8
        ? baseFeedbackSize // Largest for perfect hits
        : accuracy > 0.6
        ? baseFeedbackSize * 0.9 // Slightly smaller for good hits
        : baseFeedbackSize * 0.8; // Smallest for basic hits

    const feedback = this.add
      .text(this.scale.width / 2, this.scale.height * 0.4, feedbackText, {
        fontSize: `${feedbackSize}px`,
        fill: color,
        stroke: "#000000",
        strokeThickness: accuracy > 0.6 ? 4 : 3, // Thicker stroke for better hits
        fontFamily: "Rubik, sans-serif",
        fontWeight: accuracy > 0.8 ? "700" : accuracy > 0.6 ? "500" : "400", // Weight varies by performance
        align: "center",
        letterSpacing: accuracy > 0.8 ? 2 : 1, // More spacing for emphasis on perfect hits
      })
      .setOrigin(0.5);

    // Enhanced feedback animation
    feedback.setScale(0.8).setAlpha(0);

    // Initial pop-in animation
    this.tweens.add({
      targets: feedback,
      scale: 1,
      alpha: 1,
      duration: 200,
      ease: "Back.easeOut",
      onComplete: () => {
        // Add bounce effect for perfect/good hits
        if (accuracy > 0.6) {
          this.tweens.add({
            targets: feedback,
            y: feedback.y - 15,
            duration: 150,
            yoyo: true,
            repeat: 1,
            ease: "Sine.easeInOut",
          });
        }

        // Fade out animation
        this.tweens.add({
          targets: feedback,
          alpha: 0,
          y: feedback.y - 50,
          scale: accuracy > 0.8 ? 1.2 : 0.8,
          duration: accuracy > 0.8 ? 1800 : 1200,
          ease: "Cubic.easeOut",
          delay: 400,
          onComplete: () => feedback.destroy(),
        });
      },
    });

    // Add pulsing glow for perfect hits
    if (accuracy > 0.8) {
      let glowIntensity = 8;
      this.tweens.add({
        targets: { intensity: glowIntensity },
        intensity: 2,
        duration: 600,
        repeat: 2,
        yoyo: true,
        ease: "Sine.easeInOut",
        onUpdate: (tween) => {
          const intensity = tween.getValue();
          try {
            if (feedback && feedback.active && feedback.scene) {
              feedback.setShadow(0, 0, color, intensity, true, true);
            }
          } catch (error) {
            console.error("Error setting feedback shadow:", error);
          }
        },
      });
    }
  }

  // Animate realistic cricket ball trajectory based on runs scored
  animateBallTrajectory(ball, runs, accuracy) {
    // Stop any existing ball tweens
    this.tweens.killTweensOf(ball);

    // Define field zones based on screen dimensions
    const batterX = this.scale.width / 2;
    const batterY = this.scale.height - 240;

    // Define trajectory zones
    const innerField = {
      minDistance: 120,
      maxDistance: 200,
    };

    const boundary = {
      distance: 280,
    };

    const crowd = {
      distance: 350,
      height: -150, // High arc for sixes
    };

    let targetX, targetY, trajectory, duration;

    if (runs === 0) {
      // Ball caught or no runs - very short distance (forward)
      targetX = batterX + Phaser.Math.Between(-30, 30);
      targetY = batterY - Phaser.Math.Between(20, 60); // Forward direction
      trajectory = "ground";
      duration = 400;
    } else if (runs >= 1 && runs <= 3) {
      // 1-3 runs: Inner field, ground shots (left side)
      const angle = Phaser.Math.DegToRad(Phaser.Math.Between(120, 160)); // Left side angles
      const distance = Phaser.Math.Between(
        innerField.minDistance,
        innerField.maxDistance
      );

      targetX = batterX + Math.cos(angle) * distance;
      targetY = batterY + Math.sin(angle) * distance; // Forward
      trajectory = "ground";
      duration = 600;
    } else if (runs === 4) {
      // 4 runs: Boundary shot at 45° or 60° angle (left side)
      const shotAngle = Phaser.Math.Between(0, 1) ? 135 : 120; // 135° or 120° for left side
      const angle = Phaser.Math.DegToRad(shotAngle);

      targetX = batterX + Math.cos(angle) * boundary.distance;
      targetY = batterY + Math.sin(angle) * boundary.distance;
      trajectory = "boundary";
      duration = 800;
    } else if (runs === 5) {
      // 5 runs: Almost a six, high but not quite over boundary (left side)
      const angle = Phaser.Math.DegToRad(Phaser.Math.Between(110, 125)); // Left side

      targetX = batterX + Math.cos(angle) * (boundary.distance + 20);
      targetY = batterY + Math.sin(angle) * (boundary.distance + 20);
      trajectory = "high";
      duration = 900;
    } else if (runs >= 6) {
      // 6 runs: High arc toward top of screen (left side)
      const startAngle = 120; // Start at 120° (left-up)
      const endAngle = 150; // End at 150° (higher left-up)

      // Calculate intermediate and final positions
      const startAngleRad = Phaser.Math.DegToRad(startAngle);
      const endAngleRad = Phaser.Math.DegToRad(endAngle);

      targetX = batterX + Math.cos(endAngleRad) * crowd.distance;
      targetY = batterY + Math.sin(endAngleRad) * crowd.distance; // This will be toward top
      trajectory = "six";
      duration = 1000;
    }

    // Ensure ball stays within screen bounds
    targetX = Phaser.Math.Clamp(targetX, 50, this.scale.width - 50);
    targetY = Phaser.Math.Clamp(targetY, 100, this.scale.height - 100);

    // Animate based on trajectory type
    if (trajectory === "ground") {
      // Low ground shot
      this.tweens.add({
        targets: ball,
        x: targetX,
        y: targetY,
        duration: duration,
        ease: "Quad.Out",
        onComplete: () => {
          this.completeBallAnimation(ball);
        },
      });
    } else if (trajectory === "boundary") {
      // Boundary shot - straight to the left, off screen
      // Make the ball go well beyond the screen boundary
      const offScreenX = -100; // Far left, off screen

      this.tweens.add({
        targets: ball,
        x: offScreenX,
        y: targetY,
        duration: duration,
        ease: "Quad.Out",
        onComplete: () => {
          this.completeBallAnimation(ball);
        },
      });
    } else if (trajectory === "high") {
      // High shot but not quite a six
      const arcHeight = batterY - 80;

      this.tweens.add({
        targets: ball,
        x: targetX,
        duration: duration,
        ease: "Quad.Out",
      });

      this.tweens.add({
        targets: ball,
        y: arcHeight,
        duration: duration * 0.5,
        ease: "Quad.Out",
        onComplete: () => {
          this.tweens.add({
            targets: ball,
            y: targetY,
            duration: duration * 0.5,
            ease: "Quad.In",
            onComplete: () => {
              this.completeBallAnimation(ball);
            },
          });
        },
      });
    } else if (trajectory === "six") {
      // Six - high arc toward top of screen (left side)
      const startAngle = 120;
      const endAngle = 150;
      const startAngleRad = Phaser.Math.DegToRad(startAngle);
      const endAngleRad = Phaser.Math.DegToRad(endAngle);

      // Calculate high arc trajectory points
      const peakDistance = crowd.distance * 0.7;
      const peakX = batterX + Math.cos(startAngleRad) * peakDistance;
      const peakY = batterY - Math.sin(startAngleRad) * peakDistance * 0.8; // High up (negative Y = up)

      // Create high arc that goes toward top of screen
      const finalX = batterX + Math.cos(endAngleRad) * crowd.distance;
      const finalY = batterY - Math.sin(endAngleRad) * crowd.distance; // Toward top (negative Y = up)

      // First phase: Rise high at 120° angle
      this.tweens.add({
        targets: ball,
        x: peakX,
        y: peakY,
        duration: duration * 0.6,
        ease: "Quad.Out",
        onComplete: () => {
          // Second phase: Continue upward arc to top of screen
          this.tweens.add({
            targets: ball,
            x: finalX,
            y: finalY,
            duration: duration * 0.4,
            ease: "Quad.Out",
            onComplete: () => {
              // For sixes, ball disappears into crowd (top of screen)
              this.tweens.add({
                targets: ball,
                alpha: 0,
                scale: 0.5,
                y: finalY - 50, // Move slightly higher as it fades
                duration: 300,
                onComplete: () => {
                  this.completeBallAnimation(ball);
                },
              });
            },
          });
        },
      });
    }
  }

  // Complete ball animation and schedule next ball
  completeBallAnimation(ball) {
    if (ball && ball.active) {
      ball.destroy();
    }
    if (this.activeBall === ball) {
      this.activeBall = null;
    }
    // Always schedule next ball after animation completes
    console.log("Scheduling next ball after hit animation");
    this.scheduleNextBall();
  }

  // Helper method to update wickets display
  updateWicketsDisplay() {
    if (this.wicketsText && this.wicketsText.active && this.wicketsText.scene) {
      const wicketsLeft = this.maxWickets - this.wickets;
      this.wicketsText.setText(`Wickets Left: ${wicketsLeft}`);

      // Change color based on wickets remaining
      if (wicketsLeft <= 1) {
        this.wicketsText.setColor("#ff0000"); // Red for last wicket
      } else if (wicketsLeft <= 2) {
        this.wicketsText.setColor("#ff6600"); // Orange for second-to-last
      } else {
        this.wicketsText.setColor("#ff6b6b"); // Default red
      }
    }
  }

  // Helper method to update high score
  updateHighScore() {
    if (this.score > this.highScore) {
      this.highScore = this.score;
      localStorage.setItem("tapcricket_highscore", String(this.highScore));

      // Update high score display with animation
      if (
        this.highScoreText &&
        this.highScoreText.active &&
        this.highScoreText.scene
      ) {
        this.highScoreText.setText(`High: ${this.highScore}`);

        // Animate new high score
        this.tweens.add({
          targets: this.highScoreText,
          scale: 1.2,
          duration: 200,
          yoyo: true,
          ease: "Back.easeOut",
          onStart: () => {
            try {
              this.highScoreText.setShadow(0, 0, "#ffd700", 6, true, true);
            } catch (error) {
              console.error("Error setting high score shadow:", error);
            }
          },
          onComplete: () => {
            try {
              this.highScoreText.setShadow(2, 2, "#000000", 3, false);
            } catch (error) {
              console.error("Error removing high score shadow:", error);
            }
          },
        });
      }
    }
  }

  // Helper method to show wicket lost feedback
  showWicketFeedback() {
    const feedbackSize = Math.min(this.scale.width * 0.1, 48);
    const feedback = this.add
      .text(this.scale.width / 2, this.scale.height * 0.4, "WICKET LOST!", {
        fontSize: `${feedbackSize}px`,
        fill: "#ff0000",
        stroke: "#000000",
        strokeThickness: 4,
        fontFamily: "Rubik, sans-serif",
        fontWeight: "700",
        align: "center",
        letterSpacing: 2,
      })
      .setOrigin(0.5);

    // Wicket lost animation
    feedback.setScale(0.8).setAlpha(0);

    this.tweens.add({
      targets: feedback,
      scale: 1.2,
      alpha: 1,
      duration: 300,
      ease: "Back.easeOut",
      onComplete: () => {
        // Shake effect
        this.tweens.add({
          targets: feedback,
          x: feedback.x - 5,
          duration: 50,
          yoyo: true,
          repeat: 3,
          onComplete: () => {
            // Fade out
            this.tweens.add({
              targets: feedback,
              alpha: 0,
              y: feedback.y - 50,
              scale: 0.8,
              duration: 1000,
              ease: "Cubic.easeOut",
              delay: 600,
              onComplete: () => feedback.destroy(),
            });
          },
        });
      },
    });
  }

  // Game over method
  gameOver() {
    // Stop any active balls and clear timers
    if (this.activeBall && this.activeBall.active) {
      this.activeBall.destroy();
      this.activeBall = null;
    }

    // Clear all scheduled events
    this.time.removeAllEvents();

    // Check if it's a new high score
    const isNewHighScore =
      this.score > Number(localStorage.getItem("tapcricket_highscore") || 0);

    // Save high score if needed
    if (isNewHighScore) {
      localStorage.setItem("tapcricket_highscore", String(this.score));
    }

    // Transition to game over scene with delay for dramatic effect
    this.time.delayedCall(1500, () => {
      this.scene.start("GameOverScene", {
        score: this.score,
        highScore: this.highScore,
        isNewHighScore: isNewHighScore,
      });
    });
  }

  update() {
    // Clean up balls that have gone off screen
    this.balls.children.each((ball) => {
      if (
        ball.y > this.scale.height + 100 ||
        ball.x < -100 ||
        ball.x > this.scale.width + 100
      ) {
        if (this.activeBall === ball) {
          console.log("Cleaning up off-screen ball, scheduling next");
          this.activeBall = null;
          // Schedule next ball if this was the active ball
          this.scheduleNextBall();
        }
        ball.destroy();
      }
    });

    // Safety check: if no active ball and no balls in scene, ensure we schedule one
    if (!this.activeBall && this.balls.children.size === 0) {
      // Add a longer delay for safety mechanism
      if (!this.safetyTimeout) {
        this.safetyTimeout = this.time.delayedCall(8000, () => {
          console.log(
            "Safety mechanism: No balls detected, spawning emergency ball"
          );
          this.spawnBall();
          this.safetyTimeout = null;
        });
      }
    } else {
      // Cancel safety timeout if we have active balls
      if (this.safetyTimeout) {
        this.safetyTimeout.destroy();
        this.safetyTimeout = null;
      }
    }
  }

  destroy() {
    // Clean up event listeners and timers
    if (this.scale) {
      this.scale.off("resize", this.handleResize, this);
    }

    // Clean up any active timers
    if (this.time) {
      this.time.removeAllEvents();
    }

    super.destroy();
  }

  updateDynamicShadows() {
    // Calculate subtle shadow movement based on time
    const time = this.time.now / 1000;
    const xOffset = Math.cos(time * 2) * 0.5;
    const yOffset = Math.sin(time * 2) * 0.5;

    this.shadowOffset.x = 2 + xOffset;
    this.shadowOffset.y = 2 + yOffset;

    // Apply to score text - check if it exists and is active
    if (this.scoreText && this.scoreText.active && this.scoreText.scene) {
      this.scoreText.setShadow(
        this.shadowOffset.x,
        this.shadowOffset.y,
        "#000000",
        2,
        false
      );
    }

    // Apply to delivery text if visible - check if it exists and is active
    if (
      this.deliveryText &&
      this.deliveryText.active &&
      this.deliveryText.scene &&
      this.deliveryText.alpha > 0
    ) {
      const deliveryGlow =
        (this.deliveryText.style && this.deliveryText.style.shadowColor) ||
        "#000000";
      this.deliveryText.setShadow(
        this.shadowOffset.x,
        this.shadowOffset.y,
        deliveryGlow,
        (this.deliveryText.style && this.deliveryText.style.shadowBlur) || 2,
        true
      );
    }
  }

  handleResize() {
    const width = this.scale.gameSize.width;
    const height = this.scale.gameSize.height;
    const isPortrait = height > width;

    // Update game objects for new orientation - check if they exist and are active
    if (this.scoreText && this.scoreText.active && this.scoreText.scene) {
      const scoreSize = Math.min(width * (isPortrait ? 0.08 : 0.06), 40);
      const scoreMarginTop = Math.min(width * 0.04, 20);

      this.scoreText.setFontSize(scoreSize);
      this.scoreText.setPosition(width * 0.05, scoreMarginTop);
    }

    // Update high score display
    if (
      this.highScoreText &&
      this.highScoreText.active &&
      this.highScoreText.scene
    ) {
      const highScoreSize = Math.min(width * (isPortrait ? 0.06 : 0.05), 30);
      const scoreMarginTop = Math.min(width * 0.04, 20);

      this.highScoreText.setFontSize(highScoreSize);
      this.highScoreText.setPosition(width * 0.95, scoreMarginTop);
    }

    // Update wickets display
    if (this.wicketsText && this.wicketsText.active && this.wicketsText.scene) {
      const wicketsSize = Math.min(width * (isPortrait ? 0.05 : 0.04), 24);
      const scoreSize = Math.min(width * (isPortrait ? 0.08 : 0.06), 40);
      const scoreMarginTop = Math.min(width * 0.04, 20);

      this.wicketsText.setFontSize(wicketsSize);
      this.wicketsText.setPosition(
        width * 0.05,
        scoreMarginTop + scoreSize + 10
      );
    }

    if (
      this.deliveryText &&
      this.deliveryText.active &&
      this.deliveryText.scene
    ) {
      const deliverySize = Math.min(width * (isPortrait ? 0.06 : 0.05), 28);
      this.deliveryText.setFontSize(deliverySize);
      this.deliveryText.setPosition(width / 2, height * 0.12);
    }

    // Update crease position
    this.creaseY = isPortrait ? height - 150 : height - 100;
    if (
      this.creaseGraphics &&
      this.creaseGraphics.active &&
      this.creaseGraphics.scene
    ) {
      try {
        this.creaseGraphics.clear();
        this.creaseGraphics.lineStyle(4, 0xffffff, 0.8);
        this.creaseGraphics.lineBetween(
          width * 0.3,
          this.creaseY,
          width * 0.7,
          this.creaseY
        );
      } catch (error) {
        console.error("Error updating crease graphics:", error);
        // Recreate as rectangle if graphics operations fail
        if (this.creaseGraphics && this.creaseGraphics.destroy) {
          this.creaseGraphics.destroy();
        }
        this.creaseGraphics = this.add.rectangle(
          width / 2,
          this.creaseY,
          width * 0.4,
          4,
          0xffffff,
          0.8
        );
      }
    }

    // Update wicket position and scale
    if (this.stumps && this.stumps.active && this.stumps.scene) {
      this.stumps.setPosition(
        width / 2,
        isPortrait ? height - 50 : height - 40
      );
      this.stumps.setScale(isPortrait ? 0.6 : 0.5);

      // Ensure animation is playing
      if (!this.stumps.anims.isPlaying) {
        this.stumps.play("wicket-idle");
      }

      console.log("Wicket resize:", {
        x: this.stumps.x,
        y: this.stumps.y,
        scale: this.stumps.scale,
        displayHeight: this.stumps.displayHeight,
      });
    }

    // Update batter position
    if (this.batter && this.batter.active && this.batter.scene) {
      this.batter.setPosition(
        width / 2,
        isPortrait ? height - 240 : height - 180 // Updated to match new sprite position
      );
      this.batter.setScale(isPortrait ? 0.5 : 0.4); // Adjusted scale for sprite
    }
  }
}

const config = {
  type: Phaser.AUTO,
  parent: "game",
  physics: {
    default: "arcade",
    arcade: { debug: false },
  },
  scene: [StartScene, TapCricketScene, GameOverScene],
  scale: {
    mode: Phaser.Scale.FIT,
    autoCenter: Phaser.Scale.CENTER_BOTH,
    width: 480,
    height: 800,
    min: {
      width: 320,
      height: 480,
    },
    max: {
      width: 1024,
      height: 2048,
    },
  },
};

const game = new Phaser.Game(config);
