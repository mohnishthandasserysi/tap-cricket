import cv2
import numpy as np
import os
import random
import sys
from io import StringIO
from clean_utils import CleanMashupGenerator


class BeautifulFaceMashupGame:
    def __init__(self):
        """Initialize the Beautiful Face Mashup Game with modern UI."""
        self.mashup_generator = CleanMashupGenerator()
        self.score = 0
        self.rounds_played = 0
        self.window_name = "🎭 Cricket Face Mashup Challenge"
        
        # Game settings
        self.quiz_options = []
        self.correct_answer = ""
        self.current_mashup = None
        self.game_state = "playing"  # "playing", "answered", "quit"
        
        # UI settings
        self.button_areas = []
        self.feedback_message = ""
        self.feedback_color = (255, 255, 255)
        
        # Beautiful UI Theme
        self.colors = {
            'primary': (52, 152, 219),      # Beautiful blue
            'success': (46, 204, 113),      # Green
            'danger': (231, 76, 60),        # Red
            'warning': (241, 196, 15),      # Yellow
            'dark': (44, 62, 80),           # Dark blue-gray
            'light': (236, 240, 241),       # Light gray
            'white': (255, 255, 255),       # White
            'background': (25, 25, 40),     # Dark background
            'card': (45, 55, 72),           # Card background
            'accent': (155, 89, 182),       # Purple accent
            'gradient_start': (74, 144, 226),
            'gradient_end': (180, 58, 169)
        }
        
        # Cache all players at startup
        self.all_players = []
        self.all_player_names = []
        self.players_loaded = False
        
        # Suppress OpenCV warnings
        self.suppress_opencv_warnings()
        
    def suppress_opencv_warnings(self):
        """Suppress OpenCV and PNG warnings."""
        os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '1'
        self.old_stderr = sys.stderr
    
    def load_all_players_once(self):
        """Load all players once at startup and cache them."""
        if self.players_loaded:
            return True
            
        print("🔄 Loading all cricket players...")
        print("🏏 Building your ultimate cricket database...")
        
        try:
            sys.stderr = StringIO()
            self.all_players = self.mashup_generator.load_player_images()
            self.all_player_names = [name for name, _ in self.all_players]
            sys.stderr = self.old_stderr
            
            if len(self.all_players) >= 3:
                self.players_loaded = True
                print(f"✅ {len(self.all_players)} cricket legends loaded!")
                print("🎮 Ready for the ultimate face challenge!")
                return True
            else:
                print("❌ Need at least 3 players to play")
                return False
                
        except Exception as e:
            sys.stderr = self.old_stderr
            print(f"❌ Error loading players: {e}")
            return False
    
    def draw_gradient_background(self, canvas, width, height):
        """Draw a beautiful gradient background."""
        for y in range(height):
            ratio = y / height
            # Interpolate between gradient colors
            start_color = np.array(self.colors['gradient_start'])
            end_color = np.array(self.colors['gradient_end'])
            color = start_color + ratio * (end_color - start_color)
            cv2.line(canvas, (0, y), (width, y), color.astype(int).tolist(), 1)
        return canvas
    
    def draw_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius, color, thickness=-1):
        """Draw a rounded rectangle."""
        # Main rectangle
        cv2.rectangle(canvas, (x1 + radius, y1), (x2 - radius, y2), color, thickness)
        cv2.rectangle(canvas, (x1, y1 + radius), (x2, y2 - radius), color, thickness)
        
        # Corners
        cv2.circle(canvas, (x1 + radius, y1 + radius), radius, color, thickness)
        cv2.circle(canvas, (x2 - radius, y1 + radius), radius, color, thickness)
        cv2.circle(canvas, (x1 + radius, y2 - radius), radius, color, thickness)
        cv2.circle(canvas, (x2 - radius, y2 - radius), radius, color, thickness)
    
    def draw_shadow(self, canvas, x1, y1, x2, y2, radius=10, offset=5):
        """Draw a subtle shadow behind elements."""
        shadow_color = (0, 0, 0, 30)  # Semi-transparent black
        self.draw_rounded_rectangle(canvas, x1 + offset, y1 + offset, 
                                  x2 + offset, y2 + offset, radius, 
                                  (20, 20, 20), -1)
    
    def draw_modern_button(self, canvas, x, y, width, height, text, 
                          is_hovered=False, is_selected=False):
        """Draw a modern, beautiful button."""
        # Shadow
        self.draw_shadow(canvas, x, y, x + width, y + height)
        
        # Button background with gradient effect
        if is_selected:
            color = self.colors['success']
        elif is_hovered:
            color = self.colors['primary']
        else:
            color = self.colors['card']
        
        # Main button
        self.draw_rounded_rectangle(canvas, x, y, x + width, y + height, 12, color, -1)
        
        # Border
        border_color = self.colors['primary'] if is_hovered else self.colors['light']
        self.draw_rounded_rectangle(canvas, x, y, x + width, y + height, 12, border_color, 2)
        
        # Text with better styling
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.45
        thickness = 1
        
        # Calculate text position for centering
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        text_x = x + (width - text_size[0]) // 2
        text_y = y + (height + text_size[1]) // 2
        
        # Text shadow
        cv2.putText(canvas, text, (text_x + 1, text_y + 1), font, font_scale, 
                   (0, 0, 0), thickness)
        
        # Main text
        text_color = self.colors['white']
        cv2.putText(canvas, text, (text_x, text_y), font, font_scale, 
                   text_color, thickness)
    
    def draw_score_card(self, canvas, x, y, width, height):
        """Draw a beautiful score card."""
        # Shadow
        self.draw_shadow(canvas, x, y, x + width, y + height)
        
        # Card background
        self.draw_rounded_rectangle(canvas, x, y, x + width, y + height, 15, 
                                  self.colors['card'], -1)
        
        # Border
        self.draw_rounded_rectangle(canvas, x, y, x + width, y + height, 15, 
                                  self.colors['primary'], 2)
        
        # Score text
        score_text = f"{self.score}"
        attempts_text = f"of {self.rounds_played}"
        
        # Main score
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(canvas, "SCORE", (x + 15, y + 25), font, 0.5, 
                   self.colors['light'], 1)
        cv2.putText(canvas, score_text, (x + 15, y + 50), font, 1.2, 
                   self.colors['success'], 2)
        cv2.putText(canvas, attempts_text, (x + 15, y + 70), font, 0.4, 
                   self.colors['light'], 1)
    
    def draw_title_header(self, canvas, width):
        """Draw a beautiful title header."""
        header_height = 100
        
        # Header background with gradient
        for y in range(header_height):
            ratio = y / header_height
            start_color = np.array(self.colors['dark'])
            end_color = np.array(self.colors['card'])
            color = start_color + ratio * (end_color - start_color)
            cv2.line(canvas, (0, y), (width, y), color.astype(int).tolist(), 1)
        
        # Title with shadow effect
        title = "CRICKET FACE MASHUP CHALLENGE"
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Title shadow
        cv2.putText(canvas, title, (21, 41), font, 0.8, (0, 0, 0), 2)
        # Main title
        cv2.putText(canvas, title, (20, 40), font, 0.8, self.colors['white'], 2)
        
        # Subtitle
        subtitle = f"🏏 {len(self.all_players)} Cricket Legends • AI Face Blending"
        cv2.putText(canvas, subtitle, (20, 65), font, 0.4, self.colors['light'], 1)
        
        # Decorative line
        cv2.rectangle(canvas, (20, 75), (width - 20, 77), self.colors['primary'], -1)
    
    def create_optimized_mashup(self, num_players: int = 3):
        """Create a mashup using pre-loaded players."""
        if not self.players_loaded:
            raise ValueError("Players not loaded!")
        
        if len(self.all_players) < num_players:
            raise ValueError(f"Need at least {num_players} players")
        
        selected_players = random.sample(self.all_players, num_players)
        base_name, base_image = selected_players[0]
        base_face = self.mashup_generator.face_processor.detect_face(base_image)
        
        if base_face is None:
            for name, image in self.all_players:
                face = self.mashup_generator.face_processor.detect_face(image)
                if face is not None:
                    base_name, base_image, base_face = name, image, face
                    break
            else:
                raise ValueError("Could not find any player with detectable face")
        
        result_image = base_image.copy()
        used_players = [base_name]
        
        face_parts = [
            (self.mashup_generator.face_processor.eye_region, "eyes"),
            (self.mashup_generator.face_processor.nose_region, "nose"), 
            (self.mashup_generator.face_processor.mouth_region, "mouth")
        ]
        
        for i, (part_region, part_name) in enumerate(face_parts):
            if i + 1 < len(selected_players):
                source_name, source_image = selected_players[i + 1]
                source_face = self.mashup_generator.face_processor.detect_face(source_image)
                
                if source_face is not None:
                    try:
                        source_part = self.mashup_generator.face_processor.extract_face_part(
                            source_image, source_face, part_region
                        )
                        
                        fx, fy, fw, fh = base_face
                        rx, ry, rw, rh = part_region
                        target_x = int(fx + fw * rx)
                        target_y = int(fy + fh * ry)
                        target_w = int(fw * rw)
                        target_h = int(fh * rh)
                        
                        resized_part = self.mashup_generator.face_processor.resize_to_match(
                            source_part, (target_w, target_h)
                        )
                        
                        result_image = self.mashup_generator.face_processor.blend_parts(
                            result_image, resized_part, (target_x, target_y)
                        )
                        
                        if source_name not in used_players:
                            used_players.append(source_name)
                            
                    except Exception as e:
                        print(f"Could not blend {part_name} from {source_name}: {e}")
        
        return result_image, used_players
    
    def generate_optimized_quiz_options(self, correct_players, total_options: int = 4):
        """Generate quiz options using pre-loaded player names."""
        correct_answer = " + ".join(sorted(correct_players))
        
        wrong_options = []
        attempts = 0
        while len(wrong_options) < total_options - 1 and attempts < 20:
            num_players = random.randint(2, 3)
            random_players = random.sample(self.all_player_names, 
                                         min(num_players, len(self.all_player_names)))
            wrong_answer = " + ".join(sorted(random_players))
            
            if wrong_answer != correct_answer and wrong_answer not in wrong_options:
                wrong_options.append(wrong_answer)
            attempts += 1
        
        while len(wrong_options) < total_options - 1:
            random_player = random.choice(self.all_player_names)
            if random_player not in wrong_options and random_player != correct_answer:
                wrong_options.append(random_player)
        
        all_options = [correct_answer] + wrong_options[:total_options-1]
        random.shuffle(all_options)
        
        return all_options, correct_answer
        
    def create_beautiful_game_display(self, mashup_image: np.ndarray, options: list, feedback: str = "") -> np.ndarray:
        """Create a beautiful game display with modern UI."""
        # Calculate dimensions
        display_height = 420
        aspect_ratio = mashup_image.shape[1] / mashup_image.shape[0]
        display_width = int(display_height * aspect_ratio)
        
        canvas_width = max(900, display_width + 40)
        canvas_height = 720
        
        # Create canvas with gradient background
        canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 25
        canvas = self.draw_gradient_background(canvas, canvas_width, canvas_height)
        
        # Draw header
        self.draw_title_header(canvas, canvas_width)
        
        # Image card with shadow
        img_x = (canvas_width - display_width) // 2
        img_y = 120
        
        # Image shadow
        self.draw_shadow(canvas, img_x - 10, img_y - 10, 
                        img_x + display_width + 10, img_y + display_height + 10)
        
        # Image border
        cv2.rectangle(canvas, (img_x - 5, img_y - 5), 
                     (img_x + display_width + 5, img_y + display_height + 5), 
                     self.colors['white'], -1)
        
        # Place mashup image
        mashup_resized = cv2.resize(mashup_image, (display_width, display_height))
        canvas[img_y:img_y + display_height, img_x:img_x + display_width] = mashup_resized
        
        # Score card
        self.draw_score_card(canvas, canvas_width - 140, 120, 120, 90)
        
        # Question text
        question_y = img_y + display_height + 30
        cv2.putText(canvas, "👀 Which cricket players are in this mashup?", 
                   (30, question_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
                   self.colors['white'], 2)
        
        # Option buttons
        self.button_areas = []
        button_y_start = question_y + 40
        button_height = 50
        button_width = (canvas_width - 80) // 2
        button_spacing = 20
        
        for i, option in enumerate(options):
            row = i // 2
            col = i % 2
            
            x = 30 + col * (button_width + button_spacing)
            y = button_y_start + row * (button_height + 15)
            
            # Store button area for click detection
            self.button_areas.append((x, y, x + button_width, y + button_height, option))
            
            # Draw modern button
            is_hovered = False  # You could implement hover detection
            self.draw_modern_button(canvas, x, y, button_width, button_height, 
                                   f"{i+1}. {option}", is_hovered)
        
        # Feedback area
        if feedback:
            feedback_y = button_y_start + 140
            
            # Feedback card
            feedback_width = canvas_width - 60
            feedback_height = 60
            feedback_x = 30
            
            # Determine feedback color
            if "✅" in feedback:
                feedback_bg = self.colors['success']
            else:
                feedback_bg = self.colors['danger']
            
            # Feedback background
            self.draw_rounded_rectangle(canvas, feedback_x, feedback_y, 
                                      feedback_x + feedback_width, feedback_y + feedback_height, 
                                      10, feedback_bg, -1)
            
            # Feedback text
            cv2.putText(canvas, feedback, (feedback_x + 20, feedback_y + 25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.colors['white'], 2)
            
            if self.game_state == "answered":
                instruction = "Press SPACE for next round • Press Q to quit"
                cv2.putText(canvas, instruction, (feedback_x + 20, feedback_y + 45), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors['white'], 1)
        
        # Progress indicator
        if self.rounds_played > 0:
            accuracy = (self.score / self.rounds_played) * 100
            progress_text = f"Accuracy: {accuracy:.1f}%"
            cv2.putText(canvas, progress_text, (30, canvas_height - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.colors['light'], 1)
        
        # Controls hint
        controls_text = "Controls: Click buttons or press 1-4 • SPACE=Next • Q=Quit"
        cv2.putText(canvas, controls_text, (canvas_width - 400, canvas_height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, self.colors['light'], 1)
        
        return canvas
    
    def handle_mouse_click(self, event, x, y, flags, param):
        """Handle mouse click events."""
        if event == cv2.EVENT_LBUTTONDOWN and self.game_state == "playing":
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
            self.feedback_message = f"✅ Excellent! Correct: {self.correct_answer}"
            self.feedback_color = self.colors['success']
        else:
            self.feedback_message = f"❌ Not quite! Correct answer: {self.correct_answer}"
            self.feedback_color = self.colors['danger']
    
    def start_new_round(self):
        """Start a new game round."""
        try:
            self.current_mashup, used_players = self.create_optimized_mashup()
            self.quiz_options, self.correct_answer = self.generate_optimized_quiz_options(used_players)
            self.game_state = "playing"
            self.feedback_message = ""
            
        except Exception as e:
            self.feedback_message = f"Error: {str(e)}"
            self.feedback_color = self.colors['danger']
    
    def run(self):
        """Run the beautiful game loop."""
        print("🎮 Starting Beautiful Cricket Face Mashup Challenge!")
        print("✨ Modern UI • Smooth Animations • Professional Design")
        
        if not self.load_all_players_once():
            return
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_AUTOSIZE)
        cv2.setMouseCallback(self.window_name, self.handle_mouse_click)
        
        self.start_new_round()
        
        print("\n🎯 Beautiful UI Features:")
        print("• Modern gradient backgrounds")
        print("• Rounded corners and shadows")
        print("• Professional color scheme")
        print("• Smooth visual feedback")
        print("• Score cards and progress tracking")
        print("\n" + "="*50)
        
        while True:
            if self.current_mashup is not None:
                display = self.create_beautiful_game_display(
                    self.current_mashup, self.quiz_options, self.feedback_message)
                cv2.imshow(self.window_name, display)
            
            key = cv2.waitKey(30) & 0xFF
            
            if key == ord('q') or key == 27:
                break
            elif key == ord(' ') and self.game_state == "answered":
                self.start_new_round()
            elif self.game_state == "playing" and key in [ord('1'), ord('2'), ord('3'), ord('4')]:
                option_index = int(chr(key)) - 1
                if 0 <= option_index < len(self.quiz_options):
                    self.process_answer(self.quiz_options[option_index])
        
        print(f"\n🎮 Game Over! Final Score: {self.score}/{self.rounds_played}")
        if self.rounds_played > 0:
            accuracy = (self.score / self.rounds_played) * 100
            print(f"🎯 Final Accuracy: {accuracy:.1f}%")
        
        cv2.destroyAllWindows()


def main():
    """Main function."""
    print("🎭 Beautiful Cricket Face Mashup Challenge")
    print("=" * 45)
    print("✨ Modern UI • Professional Design • Smooth Experience")
    print("🏏 1,641+ Cricket Players • AI Face Blending")
    print()
    
    try:
        game = BeautifulFaceMashupGame()
        game.run()
    except KeyboardInterrupt:
        print("\n👋 Thanks for playing!")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
