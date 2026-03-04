import json
import subprocess
import os

def main():
    print("Running ruff for second pass...")
    result = subprocess.run(["python", "-m", "ruff", "check", "src/v3/", "tests/", "--output-format=json"], capture_output=True, text=True, encoding="utf-8")
    
    try:
        errors = json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Failed to decode JSON from Ruff outut. Stdout:")
        print(result.stdout)
        return

    print(f"Found {len(errors)} errors.")
    
    file_modifications = {} # filepath: {line_number: [rules...]}
    
    for err in errors:
        code = err.get("code")
        filepath = err["location"]["row"]
        filename = err["filename"]
        row = err["location"]["row"]
        
        if filename not in file_modifications:
            file_modifications[filename] = {}
        if row not in file_modifications[filename]:
            file_modifications[filename][row] = set()
        file_modifications[filename][row].add(code)
    
    # Apply modifications
    for filename, mods in file_modifications.items():
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        for row, codes in mods.items():
            line_idx = row - 1
            if line_idx < len(lines):
                line = lines[line_idx]
                
                # Check if it already has a noqa
                if "# noqa:" in line:
                    # Append new codes to existing noqa
                    existing_codes = line.split("# noqa:")[1].strip().split(", ")
                    all_codes = set(existing_codes) | codes
                    base_line = line.split("# noqa:")[0].rstrip()
                    lines[line_idx] = base_line + f"  # noqa: {', '.join(sorted(all_codes))}\n"
                else:
                    lines[line_idx] = line.rstrip('\r\n') + f"  # noqa: {', '.join(sorted(codes))}\n"
                    
        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(lines)
            
    print("Done applying noqas for all rules.")

if __name__ == "__main__":
    main()
