// Phaser is loaded globally via script tag in index.html

class TapCricketScene extends Phaser.Scene {
  constructor() {
    super({ key: "TapCricketScene" });
  }

  preload() {
    // Load assets (replace with your own images)
    this.load.image("pitch", "assets/pitch.jpg"); // vertical pitch bg
    // this.load.image("stumps", "assets/stumps.png"); // stumps image (bottom)
    // this.load.image("ball", "assets/ball.png"); // cricket ball
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
    // Add background pitch
    this.add
      .image(this.scale.width / 2, this.scale.height / 2, "pitch")
      .setDisplaySize(this.scale.width, this.scale.height);

    // Create temporary graphics for missing assets
    this.createTemporaryAssets();

    // Define batting crease position (where ball should be hit)
    this.creaseY = this.scale.height - 150;

    // Add visible batting crease line
    this.creaseGraphics = this.add.graphics();
    this.creaseGraphics.lineStyle(4, 0xffffff, 0.8);
    this.creaseGraphics.lineBetween(
      this.scale.width * 0.3,
      this.creaseY,
      this.scale.width * 0.7,
      this.creaseY
    );

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

    // Score display
    this.scoreText = this.add.text(16, 16, "Score: 0", {
      fontSize: "24px",
      fill: "#ffffff",
      stroke: "#000000",
      strokeThickness: 2,
    });

    // Delivery type display
    this.deliveryText = this.add.text(16, 50, "", {
      fontSize: "18px",
      fill: "#ffff00",
      stroke: "#000000",
      strokeThickness: 2,
    });

    // Input tap = swing bat
    this.input.on("pointerdown", () => {
      this.swingBat();
    });

    // Timer: spawn balls with varying intervals
    this.scheduleNextBall();
  }

  createTemporaryAssets() {
    // Create a circular texture for the ball
    const ballGraphics = this.add.graphics();
    ballGraphics.fillStyle(0xff0000);
    ballGraphics.fillCircle(10, 10, 10);
    ballGraphics.generateTexture("tempBall", 20, 20);
    ballGraphics.destroy();
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

    // Display delivery type
    this.deliveryText.setText(`${delivery.type} Ball`);
    this.deliveryText.setAlpha(1);
    this.tweens.add({
      targets: this.deliveryText,
      alpha: 0,
      duration: 1000,
      delay: 500,
    });

    // Spawn ball at bowler's end (top of screen)
    const startX = this.scale.width / 2 + Phaser.Math.Between(-30, 30); // slight variation
    const startY = 50;

    this.activeBall = this.physics.add
      .image(startX, startY, "tempBall")
      .setScale(0.8);
    this.activeBall.setData("delivery", delivery);
    this.activeBall.setData("hasBounced", false);
    this.activeBall.setData("canHit", false);
    this.balls.add(this.activeBall);

    // Set initial velocity for bowling arc
    const targetX = this.scale.width / 2;
    const bounceY = this.creaseY - 50; // Bounce just before the crease

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

    // Update score
    this.score += runs;
    this.scoreText.setText(`Score: ${this.score}`);

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

    const feedback = this.add
      .text(this.scale.width / 2, this.scale.height / 2, feedbackText, {
        fontSize: "24px",
        fill: color,
        stroke: "#000000",
        strokeThickness: 2,
      })
      .setOrigin(0.5);

    // Animate feedback
    this.tweens.add({
      targets: feedback,
      alpha: 0,
      y: feedback.y - 50,
      duration: 1500,
      onComplete: () => feedback.destroy(),
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
          this.activeBall = null;
        }
        ball.destroy();
      }
    });
  }
}

const config = {
  type: Phaser.AUTO,
  width: 480,
  height: 800, // tall orientation
  physics: {
    default: "arcade",
    arcade: { debug: false },
  },
  scene: [TapCricketScene],
};

const game = new Phaser.Game(config);
