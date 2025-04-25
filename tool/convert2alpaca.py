import json
import os


def convert_to_alpaca_format(input_file, output_file):
    """
    Convert JSON data from original format to Alpaca format.

    Original format:
    [
      {
        "question": "...",
        "answer": "...",
        "filename": "..."
      }
    ]

    Target Alpaca format:
    [
      {
        "instruction": "...",
        "input": "",
        "output": "..."
      }
    ]
    """
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} not found")
        return

    # Read the input JSON file
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            original_data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {input_file}")
        return
    except Exception as e:
        print(f"Error reading input file: {str(e)}")
        return

    # Convert each entry to the Alpaca format
    alpaca_data = []
    for item in original_data:
        if "question" not in item or "answer" not in item:
            print(f"Warning: Missing 'question' or 'answer' in item {item}")
            continue
        alpaca_item = {
            "instruction": item["question"],
            "input": "",
            "output": item["answer"],
        }
        alpaca_data.append(alpaca_item)

    # Write the converted data to the output file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(alpaca_data, f, ensure_ascii=False, indent=2)
        print(f"Conversion complete. Output saved to {output_file}")
    except Exception as e:
        print(f"Error writing output file: {str(e)}")


if __name__ == "__main__":
    # You can change these paths as needed
    input_list = [
        # "副本问题管理-热工.json",
        # "新能源问题1.json",
        "temp.json",
        # "励磁问题导出.json",
        # "现场评价管理---汽轮机.json",
        # "问题管理-供热专业.json",
        # "化学专业问题导出.json",
        # "'现场评价问题导出 (燃气轮机).json'",
        # "'问题管理 (绝缘专业).json'",
    ]
    output_list = [
        # "CopyIssueManagement_ThermalEngineering.json",
        # "NewEnergyIssue1.json",
        "OnsiteEvaluationIssues_EnergySaving.json",
        # "ExcitationIssues.json",
        # "OnsiteEvaluationManagement_Turbine.json",
        # "IssueManagement_HeatingSpecialty.json",
        # "ChemistrySpecialtyIssues.json",
        # "OnsiteEvaluationIssues_GasTurbine.json",
        # "IssueManagement_InsulationSpecialty.json",
    ]
    for input_file, output_file in zip(input_list, output_list):
        # Ensure the input file name is correctly formatted
        input_file = input_file.strip("'\"")
        output_file = output_file.strip("'\"")

        # Convert the files
        convert_to_alpaca_format(
            os.path.join("./origin", input_file), output_file
        )

    # convert_to_alpaca_format(input_file, output_file)
