import cv2
import pytesseract
import numpy as np
import json
import os
import sys
import re

class BlockExtractor:
    def __init__(self, image_path, output_dir, tesseract_lang="rus"):
        self.image_path = image_path
        self.tesseract_lang = tesseract_lang
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def text_correction(self, given_text: str):
        replacements = {
            "|": "1",
            "No": "№",
            "СТ.": "ст.",
            "Ne ": "№",
            "Nel,": "№ 1,",
            "5 »": "5»",
            "№ I": "№ 1",
            "5‘": "5.1",
            "BHOCATCA": "вносятся",
            "Российскои": "Российской",
            "OT ": "от ",
            "oT ": "от ",
            "а} ": "а) ",
            " обюджетных ": " бюджетных ",
            "aanHOH; с суб": 'субсидий;".'
            }
        
        for old, new in replacements.items():
            given_text = given_text.replace(old, new)
        given_text = re.sub(r"(\d+)'", r"\1.1", given_text)
        given_text = re.sub(r"(\d+)!", r"\1.1", given_text)
        given_text = re.sub(r"(\d+)°", r"\1.2", given_text)
        given_text = re.sub(r"(№ \d+)\?", r"\g<1>2", given_text)
        given_text = re.sub(r"(\d+)\?", r"\1.2", given_text)
        given_text = re.sub(r"^([А-Я])\)", lambda match: match.group(1).lower() + ")", given_text)
        return given_text

    def process_string(self, input_string: str) -> str:
        result = re.sub(r'\s{2,}', ' ', input_string)
        return result

    def checker_words(self, textt: str):
        listt = textt.split()
        lengthh = [len(x) for x in listt]
        if len(textt) < 8 and min(lengthh) == 1:
            return 0
        elif len(textt) < 20 and lengthh.count(1) > 2:
            return 0
        elif len(textt) < 8 and min(lengthh) > 1:
            return 1
        else:
            return 2

    def extract_text(self):
        image = cv2.imread(self.image_path)
        if image is None:
            raise FileNotFoundError(f"Image not found at {self.image_path}")

        scale_factor = 1
        image = cv2.resize(image, (0, 0),
                           fx=scale_factor,
                           fy=scale_factor,  
                           interpolation=cv2.INTER_AREA)

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_green = np.array([40, 40, 40])
        upper_green = np.array([80, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        rectangles = [
            (*cv2.boundingRect(contour), cv2.contourArea(contour)) for contour in contours
        ]
        rectangles.sort(key=lambda rect: rect[1])

        results = []
        image_width = image.shape[1]
        image_height = image.shape[0]

        for i, (x, y, w, h, area) in enumerate(rectangles):
            cropped_region = image[y:y + h, x:x + w]

            # Calculate average color in the cropped region
            avg_color_per_row = np.mean(cropped_region, axis=0)  # Average across rows
            avg_color = np.mean(avg_color_per_row, axis=0)  # Average across columns
            avg_color = [int(c) for c in avg_color]  # Convert to integer values

            gray = cv2.cvtColor(cropped_region, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)
            _, binary_image = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            custom_config = r'--psm 6'
            extracted_text = pytesseract.image_to_string(binary_image, lang=self.tesseract_lang, config=custom_config).strip()
            corrected_text = self.text_correction(extracted_text)
            last_corrections = self.process_string(corrected_text)

            horizontal_length_from_right = image_width - (x + w)
            vertical_length_from_previous = y - rectangles[i - 1][1] - rectangles[i - 1][3] if i > 0 else y
            vertical_length_to_next = rectangles[i + 1][1] - (y + h) if i < len(rectangles) - 1 else image_height - (y + h)

            results.append({
                "order": i + 1,
                "text": last_corrections,
                "horizontal_length_left": x,
                "horizontal_length_right": horizontal_length_from_right,
                "vertical_length_to_previous": vertical_length_from_previous,
                "vertical_length_to_next": vertical_length_to_next,
                "area": area,
                "color_code": avg_color  # Add the average color code here
            })

        # Filter out results where the length of "text" is less than 2
        filtered_results = [result for result in results if len(result["text"]) >= 2 and self.checker_words(result['text']) > 0]

        # Reassign order sequentially
        for new_order, result in enumerate(filtered_results, start=1):
            result["order"] = new_order

        json_filename = os.path.basename(self.image_path).rsplit('.', 1)[0] + '.json'
        output_file = os.path.join(self.output_dir, json_filename)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(filtered_results, f, ensure_ascii=False, indent=4)

        print(f"Results saved to {output_file}")
        return output_file


def process_directory(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(input_directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            input_image_path = os.path.join(input_directory, filename)
            try:
                extractor = BlockExtractor(input_image_path, output_directory)
                extractor.extract_text()
            except Exception as e:
                print(f"Error processing {filename}: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python blocked.py <rectangled_path> <output_path>")
        sys.exit(1)

    rectangled_path = sys.argv[1]
    output_path = sys.argv[2]

    process_directory(rectangled_path, output_path)
