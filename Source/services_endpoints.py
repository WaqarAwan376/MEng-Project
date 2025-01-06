import os
import re
import json
from datetime import datetime

# Constants
OUTPUT_DIR='./outputs'
OUTPUT_FILE='endpoints'

# Class-level @RequestMapping pattern
class_pattern = r'@RequestMapping\s*\(\s*(?:value\s*=\s*)?"([^"]+)"\s*\)'

# Method-level mapping patterns for different HTTP methods
method_patterns = {
    "GET": [
        r'@GetMapping\s*\(\s*(?:value\s*=\s*)?"([^"]*)"\s*\)',
        r'@GetMapping\s*\(\s*path\s*=\s*\{"([^"]*)"\s*\}\)',
        r"@GetMapping\s*\(\s*\)",
        r"@GetMapping(?!\()",
    ],
    "POST": [
        r'@PostMapping\s*\(\s*(?:value\s*=\s*)?"([^"]*)"\s*\)',
        r'@PostMapping\s*\(\s*path\s*=\s*\{"([^"]*)"\s*\}\)',
        r"@PostMapping\s*\(\s*\)",
        r"@PostMapping(?!\()",
    ],
    "PUT": [
        r'@PutMapping\s*\(\s*(?:value\s*=\s*)?"([^"]*)"\s*\)',
        r'@PutMapping\s*\(\s*path\s*=\s*\{"([^"]*)"\s*\}\)',
        r"@PutMapping\s*\(\s*\)",
        r"@PutMapping(?!\()",
    ],
    "DELETE": [
        r'@DeleteMapping\s*\(\s*(?:value\s*=\s*)?"([^"]*)"\s*\)',
        r'@DeleteMapping\s*\(\s*path\s*=\s*\{"([^"]*)"\s*\}\)',
        r"@DeleteMapping\s*\(\s*\)",
        r"@DeleteMapping(?!\()",
    ],
}


def dict_to_json_file(file_name,output_folder, dictionary):
    os.makedirs("./outputs/", exist_ok=True) if not output_folder else ''
    with open(f"{output_folder}{file_name}.json" if output_folder else f'./outputs/{file_name}.json',
              'w') as file:
        json.dump(dictionary, file, indent=2, ensure_ascii=False)


def find_java_files(directory):
    """Find all Java files in the given directory."""
    java_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    return java_files


def extract_paths_from_file(file_path):
    """Extract REST paths from the java file."""
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Extract class-level base URL
    base_url = ""
    class_match = re.search(class_pattern, content)
    if class_match:
        base_url = class_match.group(1).strip()
    if not base_url.endswith("/"):
        base_url += "/"

    paths = []
    for request_type, patterns in method_patterns.items():
        for pattern in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                path = match.group(1) if match.groups() else ""
                if path:  # Specific path defined
                    for sub_path in path.split(","):
                        if sub_path.strip():
                            full_path = (base_url + sub_path.strip()).replace("//", "/")
                            paths.append({"type": request_type, "path": full_path})
                else:
                    # No specific path, assume class-level base path
                    full_path = base_url.rstrip("/")
                    paths.append(
                        {"type": request_type, "path": full_path if full_path else "/"}
                    )

    # Deduplicate paths
    unique_paths = {f"{p['type']} - {p['path']}": p for p in paths}
    return list(unique_paths.values())


def extract_all_paths(directory):
    """Extract REST paths from all Java files in the given directory."""
    java_files = find_java_files(directory)
    all_paths = []
    for java_file in java_files:
        paths = extract_paths_from_file(java_file)
        if paths:
            class_name = os.path.basename(java_file).replace(".java", "")
            all_paths.append({
                    "file_path":java_file,
                    "class_name": class_name,
                    "paths": paths
                })
    return {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"endpoints": all_paths}


if __name__ == "__main__":
    
    input_directory = input("Please enter the absolute path to the folder containing the 'main' directory: ")
    original_directory = os.getcwd()
    os.chdir(input_directory)
    output_folder = input(
        f"Please enter output folder path for {OUTPUT_FILE} (default: {OUTPUT_DIR}): ")

    paths = extract_all_paths(input_directory)

    # Write paths to a JSON file
    os.chdir(original_directory)
    dict_to_json_file(OUTPUT_FILE,output_folder, paths)
