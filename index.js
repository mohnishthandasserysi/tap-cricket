// Phaser is loaded globally via script tag in index.html

class TapCricketScene extends Phaser.Scene {
  constructor() {
    super({ key: "TapCricketScene" });
  }

  preload() {
    // Load assets (replace with your own images)
    this.load.image("pitch", "assets/pitch.jpg"); // vertical pitch bg
    this.load.image("ball", "assets/ball.png"); // cricket ball
    // this.load.image("stumps", "assets/stumps.png"); // stumps image (bottom)
    // this.load.image("bat", "assets/bat.png"); // bat sprite
  }

  init() {
    // Game state variables
    this.score = 0;
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
    this.creaseY = this.scale.height - 150;

    // Add visible batting crease line (simplified)
    try {
      this.creaseGraphics = this.add.graphics();
      this.creaseGraphics.lineStyle(4, 0xffffff, 0.8);
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

    // Add stumps at bottom (batter's perspective) - temporary rectangle
    this.stumps = this.add.rectangle(
      this.scale.width / 2,
      this.scale.height - 80,
      40,
      60,
      0x8b4513
    );

    // Add bat near stumps - temporary rectangle
    this.bat = this.add.rectangle(
      this.scale.width / 2,
      this.scale.height - 120,
      8,
      40,
      0xdeb887
    );

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

    // Delivery type display with enhanced visibility
    const deliverySize = Math.min(this.scale.width * 0.06, 28); // Slightly larger
    this.deliveryText = this.add
      .text(this.scale.width * 0.05, this.scale.height * 0.08, "", {
        fontSize: `${deliverySize}px`,
        fill: "#ffffff", // Default color, will be changed per delivery
        stroke: "#000000",
        strokeThickness: 2, // Thinner stroke for sharper look
        fontFamily: "Rubik, sans-serif",
        fontWeight: "700", // Keep bold for readability
        letterSpacing: 4, // Increased letter spacing for better readability
      })
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

    // Timer: spawn balls with varying intervals
    this.scheduleNextBall();
  }

  scheduleNextBall() {
    // Variable delay between balls (1.5 to 3 seconds)
    const delay = Phaser.Math.Between(1500, 3000);
    this.time.delayedCall(delay, () => {
      this.spawnBall();
      this.scheduleNextBall();
    });
  }

  spawnBall() {
    // Don't spawn if there's already an active ball
    if (this.activeBall && this.activeBall.active) {
      return;
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
    const bounceY = bowlerPositionY + remainingDistance * 0.6; // Bounce at good length (60% of remaining distance)

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

    // Bounce effect - ball goes up slightly then continues to crease
    const bounceHeight = 30;
    const finalY = this.creaseY;

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
    if (ball && ball.active) {
      ball.destroy();
    }
    if (this.activeBall === ball) {
      this.activeBall = null;
    }
    // Could add "missed" feedback here
  }

  swingBat() {
    // Bat swing animation
    this.tweens.add({
      targets: this.bat,
      angle: -45,
      duration: 100,
      yoyo: true,
    });

    // Check if there's an active ball that can be hit
    if (
      this.activeBall &&
      this.activeBall.active &&
      this.activeBall.getData("canHit")
    ) {
      const ball = this.activeBall;
      const delivery = ball.getData("delivery");

      // Calculate timing accuracy based on ball position relative to crease
      const distanceFromCrease = Math.abs(ball.y - this.creaseY);
      const timingAccuracy = this.calculateTimingAccuracy(
        distanceFromCrease,
        delivery.difficulty
      );

      if (timingAccuracy > 0.3) {
        // Minimum threshold to hit
        this.hitBall(ball, delivery, timingAccuracy);
      } else {
        this.missedSwing(ball);
      }
    }
  }

  calculateTimingAccuracy(distance, difficulty) {
    // Perfect timing when ball is exactly at crease (distance = 0)
    // Accuracy decreases with distance and difficulty
    const maxDistance = 30 + difficulty * 10; // Harder balls have smaller timing window
    const accuracy = Math.max(0, 1 - distance / maxDistance);
    return accuracy;
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

    // Ball hit animation
    const hitAngle = Phaser.Math.DegToRad(Phaser.Math.Between(-60, -30));
    const hitPower = 200 + accuracy * 300;

    ball.setVelocity(
      Math.cos(hitAngle) * hitPower,
      Math.sin(hitAngle) * hitPower
    );

    // Remove ball after hit animation
    this.time.delayedCall(1000, () => {
      if (ball && ball.active) {
        ball.destroy();
      }
      if (this.activeBall === ball) {
        this.activeBall = null;
      }
    });
  }

  missedSwing(ball) {
    // Player swung but missed - ball continues
    console.log("Missed swing!");
  }

  showRunsFeedback(runs, accuracy) {
    let feedbackText = "";
    let color = "#ffffff";

    if (runs === 0) {
      feedbackText = "MISS!";
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

  update() {
    // Clean up balls that have gone off screen
    this.balls.children.each((ball) => {
      if (
        ball.y > this.scale.height + 100 ||
        ball.x < -100 ||
        ball.x > this.scale.width + 100
      ) {
        if (this.activeBall === ball) {
          this.activeBall = null;
        }
        ball.destroy();
      }
    });
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

    if (
      this.deliveryText &&
      this.deliveryText.active &&
      this.deliveryText.scene
    ) {
      const deliverySize = Math.min(width * (isPortrait ? 0.045 : 0.03), 24);
      this.deliveryText.setFontSize(deliverySize);
      this.deliveryText.setPosition(width * 0.05, height * 0.08);
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

    // Update stumps position
    if (this.stumps && this.stumps.active && this.stumps.scene) {
      this.stumps.setPosition(
        width / 2,
        isPortrait ? height - 80 : height - 60
      );
      this.stumps.setSize(isPortrait ? 40 : 30, isPortrait ? 60 : 45);
    }

    // Update bat position
    if (this.bat && this.bat.active && this.bat.scene) {
      this.bat.setPosition(width / 2, isPortrait ? height - 120 : height - 90);
      this.bat.setSize(isPortrait ? 8 : 6, isPortrait ? 40 : 30);
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
  scene: [TapCricketScene],
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
