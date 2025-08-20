import cv2
import numpy as np
import os
import random
import sys
from io import StringIO
from clean_utils import CleanMashupGenerator


class CleanFaceMashupGame:
    def __init__(self):
        """Initialize the Clean Face Mashup Game (no PNG warnings)."""
        self.mashup_generator = CleanMashupGenerator()
        self.score = 0
        self.rounds_played = 0
        self.window_name = "Clean Face Mashup Game"
        
        # Game settings
        self.quiz_options = []
        self.correct_answer = ""
        self.current_mashup = None
        self.game_state = "playing"  # "playing", "answered", "quit"
        
        # UI settings
        self.button_areas = []
        self.feedback_message = ""
        self.feedback_color = (255, 255, 255)
        
        # Suppress OpenCV warnings
        self.suppress_opencv_warnings()
        
    def suppress_opencv_warnings(self):
        """Suppress OpenCV and PNG warnings."""
        # Suppress libpng warnings
        os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'
        
        # Redirect stderr temporarily during image operations
        self.old_stderr = sys.stderr
        
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
        title = "Clean Face Mashup Game - No Warnings!"
        cv2.putText(canvas, title, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add subtitle
        subtitle = "(PNG Support - Warning Free)"
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
        """Start a new game round."""
        try:
            print("🎭 Generating new mashup...")
            
            # Suppress stderr during image processing
            sys.stderr = StringIO()
            
            self.current_mashup, used_players = self.mashup_generator.create_simple_mashup()
            self.quiz_options, self.correct_answer = self.mashup_generator.generate_quiz_options(used_players)
            
            # Restore stderr
            sys.stderr = self.old_stderr
            
            self.game_state = "playing"
            self.feedback_message = ""
            print(f"✅ Created mashup with: {', '.join(used_players)}")
            
        except Exception as e:
            # Restore stderr in case of error
            sys.stderr = self.old_stderr
            print(f"Error creating mashup: {e}")
            self.feedback_message = f"Error: {str(e)}"
            self.feedback_color = (0, 0, 255)
    
    def run(self):
        """Run the main game loop."""
        print("🎮 Starting Clean Face Mashup Game!")
        print("✨ PNG images supported - No warnings!")
        print("📁 Make sure you have player images in the 'players/' folder")
        
        # Check if players folder exists and has images
        try:
            # Suppress stderr during initial load
            sys.stderr = StringIO()
            players = self.mashup_generator.load_player_images()
            sys.stderr = self.old_stderr
            
            if len(players) < 3:
                print("❌ Error: Need at least 3 player images in the 'players/' folder!")
                print("📝 Add images named like: player1.png, player2.png, etc.")
                return
            
            print(f"✅ Found {len(players)} players!")
            
        except Exception as e:
            sys.stderr = self.old_stderr
            print(f"❌ Error loading player images: {e}")
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
                self.start_new_round()
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
    """Main function to run the Clean Face Mashup Game."""
    print("🎭 Clean Face Mashup Game")
    print("=" * 30)
    print("✨ PNG Support - No sRGB Warnings!")
    print("🚀 Enjoy the game without noise!")
    print()
    
    try:
        game = CleanFaceMashupGame()
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
