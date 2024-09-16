import subprocess
import shutil
import pytesseract
import os
import sys
from PIL import Image

def get_tesseract_version():
    """
    This function finds the installed Tesseract OCR version.

    Returns:
        str: The version of Tesseract OCR installed.
        None: If there is an error retrieving the version.
    """
    try:
        version_output = subprocess.check_output(['tesseract', '--version'], stderr=subprocess.STDOUT)
        version_line = version_output.decode('utf-8').splitlines()[0]
        version = version_line.split()[1]
        print(f"Detected Tesseract version: {version}")
        return version
    except Exception as e:
        print(f"Error detecting Tesseract version: {e}")
        return None

def ocr_cropped_volume(volume, dir='cropped'):
    """
    This function performs OCR on cropped images in a specified directory and saves the text output to files.

    PARAMETERS:
        volume (int or str): The volume identifier for the image files.
        dir (str): The name of the directory containing cropped images (default is 'cropped').

    Raises:
        EnvironmentError: If the Tesseract binary is not found.
    """
    # Automatically find the Tesseract binary
    #I had to hard code it I am not sure how it is automatically finding the tesseract binary 
    tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    else:
        raise EnvironmentError("Tesseract binary not found. Make sure Tesseract is installed and accessible in your system's PATH.")

    # Get Tesseract version (optional, but useful for logging)
    tesseract_version = get_tesseract_version()
    cwd = os.getcwd()
    cropped = os.path.join(cwd, "images", volume, dir) #cropped = f"{cwd}/images/{volume}/{dir}/" 

    print(f"Processing cropped images in: {cropped}")
    
    if not os.path.exists(cropped):
        print(f"Directory not found: {cropped}")
        return
    content = [x for x in os.listdir(cropped) if '_crop.jpg' in x]
    content.sort()

    if len(content) > 0:
        output_dir = f"{cwd}/images/{volume}/text/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        print(f"Starting OCR Batch for Volume {volume} with Tesseract {tesseract_version}")
        for filename in content:
            file = os.path.join(cropped, filename)
            name = filename.replace('_crop.jpg', '.txt')
            target = os.path.join(output_dir, name)
            print(f"Processing {filename}...")

            img = Image.open(file)
            text = pytesseract.image_to_string(img)

            with open(target, mode='w') as ocrf:
                ocrf.write(text)

        print(f"Finished OCR for Volume {volume}")
    else:
        print(f"No cropped images found in {cropped}")

if __name__ == "__main__":
    get_tesseract_version()
    volume = input("Enter the volume number: ")
    ocr_cropped_volume(volume)
    
