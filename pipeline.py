import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime

class PDFToDocxPipeline:
    def __init__(self, base_path="./"):
        self.base_path = base_path
        self.exp_folder = None

    def get_next_experiment_folder(self):
        """Get the next experiment folder name like exp_1, exp_2, etc."""
        exp_num = 1
        while True:
            exp_folder = os.path.join(self.base_path, f"exp_{exp_num}")
            if not os.path.exists(exp_folder):
                os.makedirs(exp_folder)
                self.exp_folder = exp_folder
                return exp_folder
            exp_num += 1

    @staticmethod
    def run_step(command):
        """Run a subprocess command."""
        print(f"Running: {command}")
        result = subprocess.run(command, shell=True)
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {command}")

    @staticmethod
    def clean_folder(folder_path):
        """Remove all files in a folder."""
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            os.makedirs(folder_path)

    def clean_experiment_folder(self):
        """Remove the entire experiment folder."""
        if self.exp_folder and os.path.exists(self.exp_folder):
            shutil.rmtree(self.exp_folder)

    # def run_pipeline(self, pdf_file):
    #     start = datetime.now()
    #     # try:
    #     self.get_next_experiment_folder()
    #     images_output_path = os.path.join(self.exp_folder, "images")
    #     os.makedirs(images_output_path, exist_ok=True)
    #     self.run_step(f"python pdf2jpeg.py {pdf_file} {images_output_path}")

    #     rectangled_images_path = os.path.join(self.exp_folder, "rectangled_images")
    #     os.makedirs(rectangled_images_path, exist_ok=True)
    #     self.run_step(f"python new_raws.py {images_output_path} {rectangled_images_path}")

    #     # self.clean_folder(images_output_path)

    #     json_output_path = os.path.join(self.exp_folder, "jsons")
    #     os.makedirs(json_output_path, exist_ok=True)
    #     self.run_step(f"python blocked.py {rectangled_images_path} {json_output_path}")

    #     # self.clean_folder(rectangled_images_path)

    #     concatenated_json_path = os.path.join(json_output_path, "concatenated.json")
    #     self.run_step(f"python conc_jsons.py {json_output_path}")

    #     self.run_step(f"python write_docx.py {concatenated_json_path}")
    #     # self.clean_folder(json_output_path)
    #     end = datetime.now()    
    #     print(f"All steps completed. Outputs saved in: {self.exp_folder}")

    #     td = (end - start).total_seconds()  # No multiplication needed
    #     print(f"The time of execution of the above program is : {td:.03f}s")
    #     # finally:
    #     #     self.clean_experiment_folder()

    def run_pipeline(self, pdf_file, output_docx):
        start = datetime.now()
        
        self.get_next_experiment_folder()
        images_output_path = os.path.join(self.exp_folder, "images")
        os.makedirs(images_output_path, exist_ok=True)
        self.run_step(f"python pdf2jpeg.py {pdf_file} {images_output_path}")

        rectangled_images_path = os.path.join(self.exp_folder, "rectangled_images")
        os.makedirs(rectangled_images_path, exist_ok=True)
        self.run_step(f"python new_raws.py {images_output_path} {rectangled_images_path}")

        json_output_path = os.path.join(self.exp_folder, "jsons")
        os.makedirs(json_output_path, exist_ok=True)
        self.run_step(f"python blocked.py {rectangled_images_path} {json_output_path}")

        concatenated_json_path = os.path.join(json_output_path, "concatenated.json")
        self.run_step(f"python conc_jsons.py {json_output_path}")

        self.run_step(f"python write_docx.py {concatenated_json_path} {output_docx}")

        end = datetime.now()
        print(f"All steps completed. Outputs saved in: {self.exp_folder}")

        td = (end - start).total_seconds()
        print(f"The time of execution of the program is : {td:.03f}s")


# if __name__ == "__main__":
#     import argparse
#     parser = argparse.ArgumentParser(description="Automate PDF to DOCX text extraction pipeline.")
#     parser.add_argument("pdf_file", help="Path to the input PDF file.")
#     args = parser.parse_args()

#     pipeline = PDFToDocxPipeline()
#     pipeline.run_pipeline(args.pdf_file)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Automate PDF to DOCX text extraction pipeline.")
    parser.add_argument("pdf_file", help="Path to the input PDF file.")
    parser.add_argument("output_docx", help="Path to save the output DOCX file.")

    args = parser.parse_args()

    pipeline = PDFToDocxPipeline()
    pipeline.run_pipeline(args.pdf_file, args.output_docx)
