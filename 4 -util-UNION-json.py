# import pandas as pd
import glob
import json


insert_default = "Basic_Lux_2"

input_json_files = glob.glob(f'./pdf/{insert_default}/*.json')


combined_data = []

for file in input_json_files:
    print(f"Processing file: {file}")
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified_data = {
            "questions": data.get("questions", []),
            "answers": data.get("answers", []),
            "context": [f"PB. {insert_default} {c}" for c in data.get("context", [])]
        }
        combined_data.append(modified_data)
    except Exception as e:
        print(f"Error processing file {file}: {e}")

output_file = f'./pdf/{insert_default}/combined_file_{insert_default}.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(combined_data, f, ensure_ascii=False, indent=4)

print(f"Combined data saved to {output_file}")