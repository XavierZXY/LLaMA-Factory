import json
import os
import glob
from typing import List, Dict

def merge_json_files(input_dir: str, output_file: str) -> None:
    """
    Merge multiple JSON files into a single JSON file.
    
    Args:
        input_dir (str): Directory containing the JSON files to merge
        output_file (str): Path to the output merged JSON file
    """
    # List to store all data
    merged_data = []
    
    # Get all JSON files in the input directory
    json_files = glob.glob(os.path.join(input_dir, "*.json"))
    
    # Read and merge each JSON file
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # If the data is a list, extend the merged_data
                if isinstance(data, list):
                    merged_data.extend(data)
                # If the data is a single object, append it
                else:
                    merged_data.append(data)
        except Exception as e:
            print(f"Error reading {json_file}: {str(e)}")
    
    # Write the merged data to the output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        print(f"Successfully merged {len(json_files)} files into {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {str(e)}")

if __name__ == "__main__":
    # Example usage
    input_directory = "data_self/convert/fire-data"  # Replace with your input directory
    output_file = "merged_output.json"  # Replace with your desired output file name
    
    merge_json_files(input_directory, output_file)
