import os
import sys
import google.genai as genai
from PIL import Image
from io import BytesIO
from pathlib import Path

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

def process_folder(input_folder: str, output_folder: str):
    """
    Processes all image files in the input folder and saves them to the output folder
    with photocopy effects applied.
    """
    input_path = Path(input_folder)
    output_path = Path(output_folder)
    
    # Validate input folder exists
    if not input_path.exists() or not input_path.is_dir():
        print(f"Error: Input folder '{input_folder}' does not exist or is not a directory.")
        return
    
    # Create output folder if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Common image file extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp'}
    
    # Find all image files in input folder
    image_files = []
    for file_path in input_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(file_path)
    
    if not image_files:
        print(f"No image files found in '{input_folder}'")
        return
    
    print(f"Found {len(image_files)} image files to process...")
    
    # Process each image file
    for i, input_file in enumerate(image_files, 1):
        print(f"\nProcessing {i}/{len(image_files)}: {input_file.name}")
        
        # Generate output filename with photocopy effect suffix
        file_name = input_file.stem  # filename without extension
        file_extension = input_file.suffix
        output_filename = f"{file_name}_photocopy{file_extension}"
        output_file = output_path / output_filename
        
        # Process the image
        add_photocopy_artifacts(str(input_file), str(output_file))

# --- Example Usage ---
if __name__ == "__main__":
    # Check for the correct number of command line arguments
    if len(sys.argv) < 3:
        print("Usage: python script_name.py <input_folder> <output_folder>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    process_folder(input_folder, output_folder)
