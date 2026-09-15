import sys
import json
from pathlib import Path

def validate_jsonl(filepath: str):
    file_path = Path(filepath)
    
    if not file_path.exists():
        print(f"Error: File '{filepath}' does not exist.")
        sys.exit(1)
        
    required_keys = {"prompt", "chosen", "rejected"}
    line_number = 0
    errors = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line_number += 1
            line = line.strip()
            
            if not line:
                continue
                
            try:
                data = json.loads(line)
                
                missing_keys = required_keys - set(data.keys())
                if missing_keys:
                    print(f"Line {line_number} missing keys: {missing_keys}")
                    errors += 1
                    
                for key in required_keys:
                    if key in data and not isinstance(data[key], str):
                        print(f"Line {line_number} key '{key}' must be a string.")
                        errors += 1
                        
            except json.JSONDecodeError:
                print(f"Line {line_number} is not valid JSON.")
                errors += 1
                
    if errors == 0:
        print(f"Success! {line_number} lines validated perfectly.")
        sys.exit(0)
    else:
        print(f"Validation failed with {errors} errors.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python validate_data.py <path_to_jsonl_file>")
        sys.exit(1)
        
    validate_jsonl(sys.argv[1])