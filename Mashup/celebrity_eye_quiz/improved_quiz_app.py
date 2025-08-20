import streamlit as st
import os
import random
from PIL import Image


class ImprovedCelebrityQuiz:
    def __init__(self, images_folder="images"):
        """Initialize the Improved Celebrity Quiz game."""
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
        if 'crop_style' not in st.session_state:
            st.session_state.crop_style = 'Eyes'
    
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
    
    def crop_image(self, image, style='Eyes'):
        """Crop image based on selected style."""
        width, height = image.size
        
        if style == 'Eyes':
            # Target eye region
            crop_width = int(width * 0.6)
            crop_height = int(height * 0.15)
            left = (width - crop_width) // 2
            top = int(height * 0.35)
            
        elif style == 'Upper Face':
            # Forehead to nose area
            crop_width = int(width * 0.7)
            crop_height = int(height * 0.25)
            left = (width - crop_width) // 2
            top = int(height * 0.25)
            
        elif style == 'Center Face':
            # Eyes and nose area
            crop_width = int(width * 0.6)
            crop_height = int(height * 0.25)
            left = (width - crop_width) // 2
            top = int(height * 0.35)
            
        elif style == 'Lower Face':
            # Nose to chin area
            crop_width = int(width * 0.6)
            crop_height = int(height * 0.25)
            left = (width - crop_width) // 2
            top = int(height * 0.55)
            
        else:  # Custom or Center
            crop_width = int(width * 0.5)
            crop_height = int(height * 0.5)
            left = (width - crop_width) // 2
            top = (height - crop_height) // 2
        
        right = left + crop_width
        bottom = top + crop_height
        
        # Ensure we don't go outside image bounds
        left = max(0, left)
        top = max(0, top)
        right = min(width, right)
        bottom = min(height, bottom)
        
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
        
        # Load and crop image
        try:
            image_path = os.path.join(self.images_folder, correct_image)
            image = Image.open(image_path)
            cropped_image = self.crop_image(image, st.session_state.crop_style)
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
        st.title("🎭 Celebrity Quiz (Improved Demo)")
        
        # Sidebar for settings
        with st.sidebar:
            st.header("⚙️ Settings")
            crop_options = ['Eyes', 'Upper Face', 'Center Face', 'Lower Face', 'Center']
            new_crop_style = st.selectbox(
                "Crop Style:", 
                crop_options, 
                index=crop_options.index(st.session_state.crop_style)
            )
            
            if new_crop_style != st.session_state.crop_style:
                st.session_state.crop_style = new_crop_style
                # Reset current question to regenerate with new crop
                if st.session_state.current_question:
                    st.session_state.current_question = None
            
            st.info("🎯 **Eyes**: Best for eye recognition quiz")
            st.info("👤 **Upper Face**: Forehead to nose")
            st.info("😊 **Center Face**: Eyes and nose")
            st.info("😮 **Lower Face**: Nose to chin")
        
        st.markdown("---")
        
        # Display score
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Score", st.session_state.score)
        with col2:
            st.metric("Crop Style", st.session_state.crop_style)
        
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
            if st.session_state.crop_style == 'Eyes':
                st.subheader("👀 Whose eyes are these?")
            else:
                st.subheader(f"🖼️ Whose {st.session_state.crop_style.lower()} is this?")
            
            st.image(question['cropped_image'], width=400, caption=f"Cropped {st.session_state.crop_style} Region")
            
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
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"Total Images: {len(celebrity_images)}")
        with col2:
            st.info(f"Current Score: {st.session_state.score}")
        with col3:
            if st.session_state.score > 0:
                accuracy = (st.session_state.score / (st.session_state.score + 1)) * 100
                st.info(f"Accuracy: {accuracy:.1f}%")
        
        # Reset game button
        if st.button("🔄 Reset Game"):
            st.session_state.score = 0
            self.reset_for_next_question()
            st.rerun()


def main():
    """Main function to run the app."""
    st.set_page_config(
        page_title="Celebrity Quiz (Improved)",
        page_icon="🎭",
        layout="wide"
    )
    
    # Initialize and run the quiz
    quiz = ImprovedCelebrityQuiz()
    quiz.run()


if __name__ == "__main__":
    main()
