import streamlit as st
import os
import random
from PIL import Image


class SimpleCelebrityQuiz:
    def __init__(self, images_folder="images"):
        """Initialize the Simple Celebrity Quiz game without MediaPipe."""
        self.images_folder = images_folder
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if 'score' not in st.session_state:
            st.session_state.score = 0
        if 'current_question' not in st.session_state:
            st.session_state.current_question = None
        if 'game_state' not in st.session_state:
            st.session_state.game_state = 'playing'
        if 'last_answer' not in st.session_state:
            st.session_state.last_answer = None
        if 'correct_answer' not in st.session_state:
            st.session_state.correct_answer = None
    
    def get_celebrity_images(self):
        """Get list of celebrity images from the images folder."""
        if not os.path.exists(self.images_folder):
            return []
        
        image_files = []
        for file in os.listdir(self.images_folder):
            if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                image_files.append(file)
        
        return image_files
    
    def get_celebrity_name_from_filename(self, filename):
        """Extract celebrity name from filename (remove extension)."""
        return os.path.splitext(filename)[0].replace('_', ' ').title()
    
    def simple_crop_center(self, image, crop_ratio=0.6):
        """Simple crop to target eye region."""
        width, height = image.size
        crop_width = int(width * crop_ratio)
        crop_height = int(height * 0.15)  # Narrow horizontal strip for eyes
        
        left = (width - crop_width) // 2
        top = int(height * 0.35)  # Eyes are typically 35% down from top
        right = left + crop_width
        bottom = top + crop_height
        
        return image.crop((left, top, right, bottom))
    
    def generate_question(self):
        """Generate a new question with random celebrity and options."""
        celebrity_images = self.get_celebrity_images()
        
        if len(celebrity_images) < 4:
            st.error("Need at least 4 celebrity images in the images/ folder to play!")
            return None
        
        # Pick random celebrity for this question
        correct_image = random.choice(celebrity_images)
        correct_name = self.get_celebrity_name_from_filename(correct_image)
        
        # Load and crop image (simple center crop for demo)
        try:
            image_path = os.path.join(self.images_folder, correct_image)
            image = Image.open(image_path)
            cropped_image = self.simple_crop_center(image)
        except Exception as e:
            st.error(f"Error loading image {correct_image}: {str(e)}")
            return self.generate_question()
        
        # Generate 3 wrong options
        other_images = [img for img in celebrity_images if img != correct_image]
        wrong_options = random.sample(other_images, min(3, len(other_images)))
        wrong_names = [self.get_celebrity_name_from_filename(img) for img in wrong_options]
        
        # Create all options and shuffle
        all_options = [correct_name] + wrong_names
        random.shuffle(all_options)
        
        return {
            'cropped_image': cropped_image,
            'correct_answer': correct_name,
            'options': all_options,
            'image_filename': correct_image
        }
    
    def handle_answer(self, selected_option, correct_answer):
        """Handle user's answer selection."""
        st.session_state.game_state = 'answered'
        st.session_state.last_answer = selected_option
        st.session_state.correct_answer = correct_answer
        
        if selected_option == correct_answer:
            st.session_state.score += 1
    
    def reset_for_next_question(self):
        """Reset state for next question."""
        st.session_state.game_state = 'playing'
        st.session_state.current_question = None
        st.session_state.last_answer = None
        st.session_state.correct_answer = None
    
    def run(self):
        """Run the Streamlit app."""
        st.title("🎭 Celebrity Quiz (Demo Version)")
        st.info("📝 This is a simplified version without MediaPipe face detection. It uses center cropping instead.")
        st.markdown("---")
        
        # Display score
        st.metric("Score", st.session_state.score)
        
        # Check if images folder exists
        if not os.path.exists(self.images_folder):
            st.error(f"Images folder '{self.images_folder}' not found!")
            st.info("Please create an 'images/' folder and add celebrity images.")
            st.info("Each image should be named after the celebrity (e.g., 'virat.jpg', 'shahrukh.jpg')")
            return
        
        celebrity_images = self.get_celebrity_images()
        if len(celebrity_images) == 0:
            st.error("No images found in the images/ folder!")
            st.info("Please add celebrity images with names like 'virat.jpg', 'shahrukh.jpg', etc.")
            return
        
        if len(celebrity_images) < 4:
            st.error("Need at least 4 celebrity images to play the quiz!")
            return
        
        # Generate question if needed
        if st.session_state.current_question is None and st.session_state.game_state == 'playing':
            st.session_state.current_question = self.generate_question()
        
        # Display current question
        if st.session_state.current_question:
            question = st.session_state.current_question
            
            # Display cropped image
            st.subheader("🖼️ Whose image is this?")
            st.image(question['cropped_image'], width=300, caption="Cropped Image Region (Demo)")
            
            # Show feedback if answered
            if st.session_state.game_state == 'answered':
                if st.session_state.last_answer == st.session_state.correct_answer:
                    st.success("✅ Correct!")
                else:
                    st.error(f"❌ Wrong. Correct answer: {st.session_state.correct_answer}")
                
                # Next button
                if st.button("Next Question", type="primary"):
                    self.reset_for_next_question()
                    st.rerun()
            
            else:
                # Show options as buttons
                st.subheader("Choose the correct celebrity:")
                
                cols = st.columns(2)
                for i, option in enumerate(question['options']):
                    col = cols[i % 2]
                    with col:
                        if st.button(option, key=f"option_{i}", use_container_width=True):
                            self.handle_answer(option, question['correct_answer'])
                            st.rerun()
        
        # Game statistics
        st.markdown("---")
        st.subheader("📊 Game Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"Total Images: {len(celebrity_images)}")
        with col2:
            st.info(f"Current Score: {st.session_state.score}")
        
        # Reset game button
        if st.button("🔄 Reset Game"):
            st.session_state.score = 0
            self.reset_for_next_question()
            st.rerun()


def main():
    """Main function to run the app."""
    st.set_page_config(
        page_title="Celebrity Quiz (Demo)",
        page_icon="🎭",
        layout="centered"
    )
    
    # Initialize and run the quiz
    quiz = SimpleCelebrityQuiz()
    quiz.run()


if __name__ == "__main__":
    main()
