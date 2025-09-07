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
def add_fax_artifacts(input_image_path: str, output_image_path: str):
    """
    Loads an image, sends it to the Gemini API with a prompt to add fax artifacts,
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
        prompt = """
        Add realistic fax artifacts, grain, and slight distortions to this image, making it look like a fax machine output.

        When a document is sent over a fax machine, a series of steps involving scanning, data compression, and transmission over a phone line can introduce a number of distinctive visual imperfections, known as artifacts. These are rarely seen in modern digital documents (like PDFs or JPEGs) unless they are intentionally designed to mimic a fax.

Here are the typical artifacts you see on a faxed document:

1. Compression Artifacts
Fax machines use a form of lossy compression to reduce the amount of data that needs to be transmitted over a telephone line. This often leads to:

Blockiness or Pixelation: Especially noticeable on images or areas with a lot of detail, the image may appear to be made up of small, blurry blocks or squares.

Contouring or Posterization: Gradients or subtle shading can be replaced with distinct bands of a single color (or, in the case of black-and-white faxes, different shades of gray), making the image look like a poster.

2. Signal and Transmission Noise
The analog nature of a fax transmission over a telephone line is susceptible to interference and signal degradation. This creates:

Horizontal Streaks or Lines: These are one of the most classic fax artifacts. A poor connection or line noise can cause the receiving machine to misinterpret the signal for a brief moment, resulting in a thin, solid line or streak across the page.

"Speckles" or "Static": Tiny, random black dots or specks may appear on the white background of the document, and tiny white specks may appear on black text. This is caused by noise on the phone line being misinterpreted as a black pixel.

3. Scanner and Printer-Related Artifacts
The physical components of the sending and receiving fax machines also contribute to the final look of the document:

Smudges and Dirt: If the scanner glass on the sending fax machine is dirty, it can cause black smudges or streaks to appear on the final document, as the dirt is scanned along with the paper. Similarly, a dirty roller can lead to repeated smudges or marks down the page.

Uneven Ink/Toner: The receiving machine's printer may have low toner or an old ink cartridge, leading to faded, streaky, or uneven text and images.

Skewing or Misalignment: The document feeder on the sending machine might not pull the paper straight, resulting in a final document that is noticeably skewed or crooked.

4. Text and Font-Specific Artifacts
Because a fax is essentially a low-resolution bitmap image, text loses its vector-based crispness.

Jagged or "Staircase" Edges: The diagonal or curved lines of letters (like "o," "s," or "r") will appear pixelated, with visible "steps" instead of a smooth curve.

Thickened or "Blobby" Characters: When the text is small, the low resolution can cause the letters to blur together, making them look thicker and less distinct.

Loss of Fine Detail: Thin fonts, serifs, and small punctuation marks can become difficult or impossible to read.

These artifacts are what give a faxed document its distinctive, low-fidelity appearance and are the reason why it's often difficult to read fine print or see details in a faxed image.
        """

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
    with fax effects applied.
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
        
        # Generate output filename with fax effect suffix
        file_name = input_file.stem  # filename without extension
        file_extension = input_file.suffix
        output_filename = f"{file_name}_fax_effect{file_extension}"
        output_file = output_path / output_filename
        
        # Process the image
        add_fax_artifacts(str(input_file), str(output_file))

# --- Example Usage ---
if __name__ == "__main__":
    # Check for the correct number of command line arguments
    if len(sys.argv) < 3:
        print("Usage: python script_name.py <input_folder> <output_folder>")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]

    process_folder(input_folder, output_folder)