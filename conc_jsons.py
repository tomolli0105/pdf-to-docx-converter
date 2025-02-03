import os
import json
import sys
import re

class JSONConcatenator:
    def __init__(self, json_directory, output_file="concatenated.json"):
        self.json_directory = json_directory
        self.output_file = output_file
        self.concatenated_data = []
        self.current_order = 1

    def validate_directory(self):
        if not os.path.exists(self.json_directory):
            raise FileNotFoundError(f"Directory {self.json_directory} does not exist.")
        if not any(f.endswith(".json") for f in os.listdir(self.json_directory)):
            raise ValueError(f"No JSON files found in directory {self.json_directory}.")

    def get_sorted_files(self):
        json_files = [
            f for f in os.listdir(self.json_directory) if f.endswith(".json")
        ]
        json_files.sort(
            key=lambda fname: int(re.search(r"processed_page_(\d+)", fname).group(1))
            if re.search(r"processed_page_(\d+)", fname) else float('inf')
        )
        return json_files

    def process_file(self, json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

                for entry in data:
                    # Update vertical_length_to_previous for the first order
                    if entry["order"] == 1:
                        entry["vertical_length_to_previous"] = 10  # Set to desired value
                
                    entry["order"] = self.current_order
                    self.current_order += 1

                self.concatenated_data.extend(data)

        except json.JSONDecodeError:
            print(f"Error: {json_path} is not a valid JSON file.")
        except Exception as e:
            print(f"Error processing {json_path}: {e}")

    def concatenate(self):
        self.validate_directory()
        json_files = self.get_sorted_files()

        for json_file in json_files:
            json_path = os.path.join(self.json_directory, json_file)
            self.process_file(json_path)

        output_path = os.path.join(self.json_directory, self.output_file)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.concatenated_data, f, ensure_ascii=False, indent=4)

        print(f"Concatenated JSON saved to {output_path}")

    @staticmethod
    def run_from_command_line():
        if len(sys.argv) != 2:
            print("Usage: python conc_jsons.py <json_output_path>")
            sys.exit(1)

        json_output_path = sys.argv[1]

        try:
            concatenator = JSONConcatenator(json_output_path)
            concatenator.concatenate()
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    JSONConcatenator.run_from_command_line()
