import os
import sys
import google.genai as genai
from PIL import Image
from io import BytesIO

# --- Configuration ---
# Load your API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set. Please set it before running.")

# Initialize the client
client = genai.Client()

# The model suitable for image generation/editing
MODEL_NAME = "gemini-2.5-flash-image-preview"

# --- Main Logic ---
def add_photocopy_artifacts(input_image_path: str, output_image_path: str):
    """
    Loads an image, sends it to the Gemini API with a prompt to add photocopy artifacts,
    and saves the resulting image.
    """
    try:
        # 1. Load the input image using Pillow (PIL)
        print(f"Loading image from: {input_image_path}")
        try:
            input_image = Image.open(input_image_path)
            # Convert to RGB to ensure compatibility
            if input_image.mode != 'RGB':
                input_image = input_image.convert('RGB')
            print("Input image loaded successfully.")
        except FileNotFoundError:
            print(f"Error: Input image '{input_image_path}' not found.")
            return
        except Exception as e:
            print(f"Error loading input image: {e}")
            return

        # 2. Define the text prompt for the image edit
        prompt = "Add realistic photocopy artifacts, grain, and slight distortions to this image, making it look like a very old, faded photocopy."

        print(f"Sending image and prompt to {MODEL_NAME}...")

        # 3. Send the image and prompt to the Gemini model
        # The correct method is to call generate_content on the models object
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                input_image,  # The PIL Image object
                prompt        # The text prompt
            ]
        )

        # 4. Process the response and save the generated image
        if response.candidates and response.candidates[0].content.parts:
            found_image = False
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    # The image data is returned as bytes, decode it and save
                    generated_image = Image.open(BytesIO(part.inline_data.data))
                    generated_image.save(output_image_path)
                    print(f"Updated image saved as: {output_image_path}")
                    found_image = True
                    break
            if not found_image:
                print("No image found in the response parts.")
                print("Response text:", response.text)
        else:
            print("No candidates or content parts in the response.")
            print("Full response:", response)

    except Exception as e:
        # Catch a general exception to handle various API errors
        print(f"An unexpected error occurred: {e}")

# --- Example Usage ---
if __name__ == "__main__":
    # Check for the correct number of command line arguments
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <input_image_file_path>")
        sys.exit(1)

    # The first argument (sys.argv[0]) is the script name itself
    input_img = sys.argv[1]
    
    # Generate an output file name based on the input
    file_name, file_extension = os.path.splitext(input_img)
    output_img = f"{file_name}_photocopy_effect{file_extension}"

    add_photocopy_artifacts(input_img, output_img)