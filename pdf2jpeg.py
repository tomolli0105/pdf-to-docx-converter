import sys
import os
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

class PDFToJPEG:
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

    def ensure_directory_exists(self, directory):
        """Ensure the specified directory exists, creating it if necessary."""
        if not os.path.exists(directory):
            os.makedirs(directory)

    def detect_orientation(self, image):
        """Detect the orientation of an image using Tesseract."""
        osd = pytesseract.image_to_osd(image)
        angle = int(osd.split('\n')[2].split(':')[1].strip())
        return angle

    def rotate_image(self, image, angle):
        """Rotate an image by the specified angle."""
        return image.rotate(angle, expand=True)

    def process_page(self, image):
        """Process a single page: detect orientation and rotate if necessary."""
        angle = self.detect_orientation(image)
        if angle != 0:
            image = self.rotate_image(image, -angle)
        return image

    def convert_pdf_to_jpeg(self, input_pdf, output_path):
        """Convert all pages of a PDF to JPEG images, correcting orientation."""
        self.ensure_directory_exists(output_path)

        try:
            images = convert_from_path(input_pdf, dpi=200, fmt='JPEG', grayscale=True, use_pdftocairo=True)
            for i, image in enumerate(images):
                processed_image = self.process_page(image)
                output_file = os.path.join(output_path, f"page_{i + 1}.jpeg")
                processed_image.save(output_file, "JPEG")

            print(f"Successfully saved {len(images)} pages as JPEG images in '{output_path}'")
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python pdf2jpeg.py <input.pdf> <output_path>")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_path = sys.argv[2]

    converter = PDFToJPEG()
    converter.convert_pdf_to_jpeg(input_pdf, output_path)