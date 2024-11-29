import subprocess
import os
import json
from collections import defaultdict
from itertools import combinations
from datetime import datetime

# Define directories and files to ignore
IGNORE_DIRS = {
    'target',
    'build',
    '.m2',
    '.gradle',
    '.idea',
    '.settings',
    '.git',
    'node_modules',
    '__pycache__',
    'static',
    '.mvn'
}
IGNORE_FILES = {
    '.classpath',
    '.project',
    '.iml',
    '.DS_Store',
    'Thumbs.db',
    '.png',
    '.jpg',
    '.jar'
}

def dict_to_json_file(file_name,output_folder, dictionary):
    with open(f"{output_folder}{file_name}.json" if output_folder else f'./{file_name}.json',
              'w') as file:
        json.dump(dictionary, file, indent=2, ensure_ascii=False)


def get_method_info(package_name, class_name, method_name, full_method_name, author_username,
                    author_email, time, all_authors, top_contributor):
    return locals()


def get_line_info(file_path, line_number):
    """Get last commit author from the line number provided in the parameter."""

    cmd = ['git', 'blame', '-L', f'{line_number},{line_number}', '--date=iso', '-p', \
           file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    line_info = {}
    line_info['line_number'] = line_number
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        if line.startswith('author '):
            line_info['last_author'] = line.split(' ', 1)[1]
        if line.startswith('author-time '):
            line_info['dateTime'] = int(line.split(' ', 1)[1])
        if line.startswith('author-mail '):
            line_info['author_email'] = line.split(' ', 1)[1] \
                .removeprefix('<').removesuffix('>')
    return line_info

def get_author_relation_strength(files_info_list):
    relation_strength = defaultdict(int)
    author_relation_data = []

    for fileData in files_info_list:
        # Extract unique authors for the current file
        authors_list = [item['last_author'] for item in fileData['data'] if item['last_author'] != "Not Committed Yet"]
        authors_list = list(set(authors_list))

        # Calculate relation strength for the current file's authors
        for pair in combinations(authors_list, 2):
            relation_strength[pair] += 1

    for pair, strength in relation_strength.items():
        author_relation_data.append({
            'author_1': pair[0],
            'author_2': pair[1],
            'strength': strength
        })
        
    sorted_author_relation_data = sorted(author_relation_data, key=lambda x: x['strength'], reverse=True)
    return sorted_author_relation_data


if __name__ == '__main__':
    input_directory = input("Please enter the absolute path to the folder containing the 'main' directory: ")
    original_directory = os.getcwd()
    os.chdir(input_directory)
    output_folder = input(
        "Please enter output folder path for author-tracking.json (default: ./): ")

    # Extract all the required files from the given directory
    files_list= []
    for root, dirs, files in os.walk(input_directory):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file in IGNORE_FILES or any(file.endswith(f) for f in IGNORE_FILES if f.startswith('.')):
                continue
            files_list.append(f"{root}/{file}")

    # Extract Each line information from the files
    filesData = []
    extractedFileData=[]
    extracted_line_info = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "files": []}
    for fileName in files_list:
        with open(fileName, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                extractedFileData=extractedFileData+[get_line_info(fileName,line_number)]
            extracted_line_info['files'] = extracted_line_info['files'] + [{
                "file":fileName,
                "data":extractedFileData
            }]
            extractedFileData=[]
    # TODO: Dump each file data separately so that it does not go heavy on the memory usage
    
    # Dump data into json files
    os.chdir(original_directory)
    dict_to_json_file("code_contribution",output_folder, extracted_line_info)
    dict_to_json_file("authors_relation",output_folder, get_author_relation_strength(extracted_line_info['files']))
