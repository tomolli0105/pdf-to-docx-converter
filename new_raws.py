import cv2
import pytesseract
import os
import sys

class TextLineDetector:
    def __init__(self, input_image_path, output_image_path, pixel_expansion=0):
        self.input_image_path = input_image_path
        self.output_image_path = output_image_path
        self.pixel_expansion = pixel_expansion

    def blur_image(self, image_path, n_percentage):
        if not (0 <= n_percentage <= 100):
            raise ValueError("Percentage must be between 0 and 100.")

        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Image at path {image_path} not found.")
        
        height, width = image.shape[:2]
        kernel_size = max(1, int((n_percentage / 100) * min(height, width)))
        if kernel_size % 2 == 0:
            kernel_size += 1
        blurred_image = cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)
        
        return blurred_image

    def detect_and_draw_lines(self):
        image = cv2.imread(self.input_image_path)
        if image is None:
            raise FileNotFoundError(f"Input image not found at {self.input_image_path}")
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

        n_boxes = len(data['text'])
        for i in range(n_boxes):
            if int(data['level'][i]) == 4:
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

                x_expanded = max(0, x - self.pixel_expansion)
                y_expanded = max(0, y - self.pixel_expansion)
                w_expanded = w + 2 * self.pixel_expansion
                h_expanded = h + 2 * self.pixel_expansion

                cv2.rectangle(
                    image,
                    (x_expanded, y_expanded),
                    (x_expanded + w_expanded, y_expanded + h_expanded),
                    (0, 255, 0),
                    1
                )

        cv2.imwrite(self.output_image_path, image)

def get_next_experiment_number(output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        return 1
    
    files = os.listdir(output_folder)
    experiment_numbers = [
        int(f.split('_')[1].split('.')[0]) 
        for f in files 
        if f.startswith("expanded_") and f.split('_')[1].split('.')[0].isdigit()
    ]
    return max(experiment_numbers, default=0) + 1

def process_directory(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_image_path = os.path.join(input_directory, filename)
            output_image_path = os.path.join(output_directory, f"processed_{filename}")

            detector = TextLineDetector(input_image_path, output_image_path)
            try:
                detector.detect_and_draw_lines()
                print(f"Processed {filename} -> {output_image_path}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python detect_raws.py <input_directory> <output_directory>")
    else:
        input_directory = sys.argv[1]
        output_directory = sys.argv[2]

        process_directory(input_directory, output_directory)