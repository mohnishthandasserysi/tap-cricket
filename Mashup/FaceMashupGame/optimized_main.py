import cv2
import numpy as np
import os
import random
import sys
from io import StringIO
from clean_utils import CleanMashupGenerator


class OptimizedFaceMashupGame:
    def __init__(self):
        """Initialize the Optimized Face Mashup Game (loads all players once)."""
        self.mashup_generator = CleanMashupGenerator()
        self.score = 0
        self.rounds_played = 0
        self.window_name = "Optimized Face Mashup Game"
        
        # Game settings
        self.quiz_options = []
        self.correct_answer = ""
        self.current_mashup = None
        self.game_state = "playing"  # "playing", "answered", "quit"
        
        # UI settings
        self.button_areas = []
        self.feedback_message = ""
        self.feedback_color = (255, 255, 255)
        
        # OPTIMIZATION: Cache all players at startup
        self.all_players = []  # Will store all loaded players
        self.all_player_names = []  # Will store all player names
        self.players_loaded = False
        
        # Suppress OpenCV warnings
        self.suppress_opencv_warnings()
        
    def suppress_opencv_warnings(self):
        """Suppress OpenCV and PNG warnings."""
        # Suppress libpng warnings
        os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'
        
        # Redirect stderr temporarily during image operations
        self.old_stderr = sys.stderr
    
    def load_all_players_once(self):
        """Load all players once at startup and cache them."""
        if self.players_loaded:
            return True
            
        print("🔄 Loading all players (one-time setup)...")
        print("📸 This may take a moment with 1,641+ players...")
        
        try:
            # Suppress stderr during loading
            sys.stderr = StringIO()
            
            # Load all players once
            self.all_players = self.mashup_generator.load_player_images()
            self.all_player_names = [name for name, _ in self.all_players]
            
            # Restore stderr
            sys.stderr = self.old_stderr
            
            if len(self.all_players) >= 3:
                self.players_loaded = True
                print(f"✅ Successfully loaded {len(self.all_players)} players!")
                print("🚀 Game is now optimized for fast rounds!")
                return True
            else:
                print("❌ Need at least 3 players to play the game")
                return False
                
        except Exception as e:
            sys.stderr = self.old_stderr
            print(f"❌ Error loading players: {e}")
            return False
    
    def create_optimized_mashup(self, num_players: int = 3):
        """Create a mashup using pre-loaded players (no reloading)."""
        if not self.players_loaded:
            raise ValueError("Players not loaded! Call load_all_players_once() first.")
        
        if len(self.all_players) < num_players:
            raise ValueError(f"Need at least {num_players} players, have {len(self.all_players)}")
        
        # Randomly select players from cached list
        selected_players = random.sample(self.all_players, num_players)
        
        # Use first player as base
        base_name, base_image = selected_players[0]
        base_face = self.mashup_generator.face_processor.detect_face(base_image)
        
        if base_face is None:
            # If base player has no detectable face, try another
            for name, image in self.all_players:
                face = self.mashup_generator.face_processor.detect_face(image)
                if face is not None:
                    base_name, base_image, base_face = name, image, face
                    break
            else:
                raise ValueError("Could not find any player with detectable face")
        
        result_image = base_image.copy()
        used_players = [base_name]
        
        print(f"🎭 Creating mashup with base: {base_name}")
        
        # Define face parts to blend
        face_parts = [
            (self.mashup_generator.face_processor.eye_region, "eyes"),
            (self.mashup_generator.face_processor.nose_region, "nose"), 
            (self.mashup_generator.face_processor.mouth_region, "mouth")
        ]
        
        # Try to blend different parts from different players
        for i, (part_region, part_name) in enumerate(face_parts):
            if i + 1 < len(selected_players):
                source_name, source_image = selected_players[i + 1]
                source_face = self.mashup_generator.face_processor.detect_face(source_image)
                
                if source_face is not None:
                    try:
                        # Extract part from source
                        source_part = self.mashup_generator.face_processor.extract_face_part(
                            source_image, source_face, part_region
                        )
                        
                        # Calculate target position on base face
                        fx, fy, fw, fh = base_face
                        rx, ry, rw, rh = part_region
                        target_x = int(fx + fw * rx)
                        target_y = int(fy + fh * ry)
                        target_w = int(fw * rw)
                        target_h = int(fh * rh)
                        
                        # Resize source part to match target size
                        resized_part = self.mashup_generator.face_processor.resize_to_match(
                            source_part, (target_w, target_h)
                        )
                        
                        # Blend onto result
                        result_image = self.mashup_generator.face_processor.blend_parts(
                            result_image, resized_part, (target_x, target_y)
                        )
                        
                        if source_name not in used_players:
                            used_players.append(source_name)
                        
                        print(f"  ✅ Added {part_name} from {source_name}")
                            
                    except Exception as e:
                        print(f"  ⚠️ Could not blend {part_name} from {source_name}: {e}")
                else:
                    print(f"  ⚠️ No face detected in {source_name}")
        
        return result_image, used_players
    
    def generate_optimized_quiz_options(self, correct_players, total_options: int = 4):
        """Generate quiz options using pre-loaded player names."""
        if not self.players_loaded:
            raise ValueError("Players not loaded!")
        
        # Create correct answer string
        correct_answer = " + ".join(sorted(correct_players))
        
        # Generate wrong options using cached player names
        wrong_options = []
        attempts = 0
        while len(wrong_options) < total_options - 1 and attempts < 20:
            # Create random combinations
            num_players = random.randint(2, 3)
            random_players = random.sample(self.all_player_names, min(num_players, len(self.all_player_names)))
            wrong_answer = " + ".join(sorted(random_players))
            
            # Ensure it's different from correct answer and not already added
            if wrong_answer != correct_answer and wrong_answer not in wrong_options:
                wrong_options.append(wrong_answer)
            attempts += 1
        
        # If we don't have enough unique wrong options, pad with single names
        while len(wrong_options) < total_options - 1:
            random_player = random.choice(self.all_player_names)
            if random_player not in wrong_options and random_player != correct_answer:
                wrong_options.append(random_player)
        
        # Combine and shuffle
        all_options = [correct_answer] + wrong_options[:total_options-1]
        random.shuffle(all_options)
        
        return all_options, correct_answer
        
    def create_game_display(self, mashup_image: np.ndarray, options: list, feedback: str = "") -> np.ndarray:
        """Create the game display with mashup image and options."""
        # Resize mashup image to a reasonable size
        display_height = 400
        aspect_ratio = mashup_image.shape[1] / mashup_image.shape[0]
        display_width = int(display_height * aspect_ratio)
        mashup_resized = cv2.resize(mashup_image, (display_width, display_height))
        
        # Create a larger canvas for the full game display
        canvas_width = max(800, display_width + 20)
        canvas_height = display_height + 300  # Extra space for options and UI
        canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 50  # Dark gray background
        
        # Place mashup image at the top center
        x_offset = (canvas_width - display_width) // 2
        y_offset = 20
        canvas[y_offset:y_offset + display_height, x_offset:x_offset + display_width] = mashup_resized
        
        # Add title
        title = "Optimized Face Mashup Game - Fast & Smooth!"
        cv2.putText(canvas, title, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add subtitle
        subtitle = f"({len(self.all_players)} Players Loaded)"
        cv2.putText(canvas, subtitle, (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Add score
        score_text = f"Score: {self.score}/{self.rounds_played}"
        cv2.putText(canvas, score_text, (canvas_width - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Add instruction
        instruction = "Click on the correct combination or press 1-4:"
        cv2.putText(canvas, instruction, (10, display_height + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Create option buttons
        self.button_areas = []
        button_y_start = display_height + 80
        button_height = 40
        button_width = (canvas_width - 60) // 2  # Two columns
        
        for i, option in enumerate(options):
            row = i // 2
            col = i % 2
            
            x = 20 + col * (button_width + 20)
            y = button_y_start + row * (button_height + 10)
            
            # Store button area for click detection
            self.button_areas.append((x, y, x + button_width, y + button_height, option))
            
            # Draw button background
            button_color = (80, 80, 80) if self.game_state == "playing" else (60, 60, 60)
            cv2.rectangle(canvas, (x, y), (x + button_width, y + button_height), button_color, -1)
            cv2.rectangle(canvas, (x, y), (x + button_width, y + button_height), (200, 200, 200), 2)
            
            # Add option text
            text_color = (255, 255, 255)
            font_scale = 0.5
            text_size = cv2.getTextSize(option, cv2.FONT_HERSHEY_SIMPLEX, font_scale, 1)[0]
            text_x = x + (button_width - text_size[0]) // 2
            text_y = y + (button_height + text_size[1]) // 2
            
            cv2.putText(canvas, f"{i+1}. {option}", (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, 1)
        
        # Add feedback message
        if feedback:
            feedback_y = button_y_start + 120
            cv2.putText(canvas, feedback, (20, feedback_y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.feedback_color, 2)
            
            # Add "Press SPACE for next round" or "Press Q to quit"
            if self.game_state == "answered":
                next_instruction = "Press SPACE for next round or Q to quit"
                cv2.putText(canvas, next_instruction, (20, feedback_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        
        return canvas
    
    def handle_mouse_click(self, event, x, y, flags, param):
        """Handle mouse click events."""
        if event == cv2.EVENT_LBUTTONDOWN and self.game_state == "playing":
            # Check if click is within any button area
            for button_area in self.button_areas:
                bx1, by1, bx2, by2, option = button_area
                if bx1 <= x <= bx2 and by1 <= y <= by2:
                    self.process_answer(option)
                    break
    
    def process_answer(self, selected_answer: str):
        """Process the user's answer."""
        self.rounds_played += 1
        self.game_state = "answered"
        
        if selected_answer == self.correct_answer:
            self.score += 1
            self.feedback_message = f"✅ Correct! The mashup included: {self.correct_answer}"
            self.feedback_color = (0, 255, 0)  # Green
        else:
            self.feedback_message = f"❌ Wrong! Correct answer was: {self.correct_answer}"
            self.feedback_color = (0, 0, 255)  # Red
    
    def start_new_round(self):
        """Start a new game round (using pre-loaded players)."""
        try:
            print("🎭 Generating new mashup (instant - no loading!)...")
            
            # Create mashup using cached players (no loading!)
            self.current_mashup, used_players = self.create_optimized_mashup()
            self.quiz_options, self.correct_answer = self.generate_optimized_quiz_options(used_players)
            
            self.game_state = "playing"
            self.feedback_message = ""
            print(f"✅ Created mashup with: {', '.join(used_players)}")
            
        except Exception as e:
            print(f"Error creating mashup: {e}")
            self.feedback_message = f"Error: {str(e)}"
            self.feedback_color = (0, 0, 255)
    
    def run(self):
        """Run the main game loop."""
        print("🎮 Starting Optimized Face Mashup Game!")
        print("⚡ Fast loading - No repeated player loading!")
        
        # LOAD ALL PLAYERS ONCE AT STARTUP
        if not self.load_all_players_once():
            print("❌ Failed to load players. Exiting...")
            return
        
        # Initialize OpenCV window
        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(self.window_name, self.handle_mouse_click)
        
        # Start first round
        self.start_new_round()
        
        print("\n🎯 Game Instructions:")
        print("- Click on the correct player combination")
        print("- Or press keys 1-4 to select options")
        print("- Press SPACE for next round after answering")
        print("- Press Q to quit")
        print(f"- Optimized for {len(self.all_players)} players!")
        print("\n" + "="*50)
        
        # Main game loop
        while True:
            if self.current_mashup is not None:
                # Create and display game screen
                display = self.create_game_display(self.current_mashup, self.quiz_options, self.feedback_message)
                cv2.imshow(self.window_name, display)
            
            # Handle keyboard input
            key = cv2.waitKey(30) & 0xFF
            
            if key == ord('q') or key == 27:  # Q or ESC to quit
                break
            elif key == ord(' ') and self.game_state == "answered":  # Space for next round
                self.start_new_round()  # This is now INSTANT!
            elif self.game_state == "playing" and key in [ord('1'), ord('2'), ord('3'), ord('4')]:
                # Handle number key presses
                option_index = int(chr(key)) - 1
                if 0 <= option_index < len(self.quiz_options):
                    self.process_answer(self.quiz_options[option_index])
        
        # Game over
        print(f"\n🎮 Game Over! Final Score: {self.score}/{self.rounds_played}")
        if self.rounds_played > 0:
            accuracy = (self.score / self.rounds_played) * 100
            print(f"🎯 Accuracy: {accuracy:.1f}%")
        
        cv2.destroyAllWindows()


def main():
    """Main function to run the Optimized Face Mashup Game."""
    print("🎭 Optimized Face Mashup Game")
    print("=" * 35)
    print("⚡ Fast & Smooth - No Repeated Loading!")
    print("🏏 Cricket Player Edition")
    print()
    
    try:
        game = OptimizedFaceMashupGame()
        game.run()
    except KeyboardInterrupt:
        print("\n👋 Game interrupted by user")
    except Exception as e:
        print(f"❌ Game error: {e}")
        print("\n💡 Make sure you have:")
        print("- Player images in the 'players/' folder")
        print("- At least 3 PNG/JPG images")


if __name__ == "__main__":
    main()
