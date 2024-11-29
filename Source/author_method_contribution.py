import subprocess
import javalang
import os
import json
from collections import Counter, defaultdict
from datetime import datetime
import re


def read_java_source_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


def get_file_package(code_tree):
    for _, node in code_tree.filter(javalang.tree.PackageDeclaration):
        return node.name


def is_primitive_type(type_name):
    primitive_types = {"boolean", "byte", "char",
                       "short", "int", "long",
                       "float", "double"}
    return type_name in primitive_types


def is_wrapper_class(type_name):
    wrapper_classes = {"Boolean", "Byte", "Character",
                       "Short", "Integer", "Long",
                       "Float", "Double", "ClassLoader",
                       "Object", "Class", "String"}
    return type_name in wrapper_classes


def get_full_method(class_name, package_name, method_name, parameters, import_statements):
    parameter_string = ''
    isImportFound = False

    for type, name in parameters:
        parameter_string += '' if parameter_string == '' else ','
        for importName in import_statements:
            if importName.endswith(type):
                parameter_string += f'{importName}'
                isImportFound = True
                break

        if not isImportFound and (not is_primitive_type(type) and not is_wrapper_class(type)):
            parameter_string += f"{package_name if package_name else ''}.{type}"
        elif not isImportFound and (is_primitive_type(type) or is_wrapper_class(type)):
            parameter_string += type if is_primitive_type(type) else f'java.lang.{type}'
        isImportFound = False

    full_method = ''
    if package_name:
        full_method += package_name + '.'
    if class_name:
        full_method += class_name + '.'

    full_method += f'{method_name}({parameter_string})'
    return full_method


def get_top_contributor(method_info):
    """Get the author that has contributed the most in the method."""

    author_counts = Counter(obj.get('last_author', 'unknown') for obj in method_info)
    sorted_authors = sorted(author_counts.items(), key=lambda item: (-item[1], item[0]))
    most_common_author = sorted_authors[0][0]

    author_details = defaultdict(lambda: {'emails': set(), 'line_numbers': []})
    for obj in method_info:
        author = obj.get('last_author', 'unknown')
        author_details[author]['emails'].add(obj.get('author_email', 'unknown'))
        author_details[author]['line_numbers'].append(obj.get('line_number', None))

    most_common_author_details = author_details[most_common_author]
    emails = next(iter(most_common_author_details['emails']))
    line_numbers = most_common_author_details['line_numbers']

    return {
        "username": most_common_author,
        "email": emails,
        "lines_updated": line_numbers
    }


def get_all_authors(method_info):
    """Get all the authors of a method and their lines of contribution"""
    author_lines = {}
    for entry in method_info:
        if 'last_author' in entry and 'line_number' in entry:
            author = entry['last_author']
            line_number = entry['line_number']
            if author in author_lines:
                author_lines[author]['line_numbers'].append(line_number)
                author_lines[author]['total_lines'] += 1
            else:
                author_lines[author] = {'line_numbers': [line_number], 'total_lines': 1}
            author_lines[author]['author_email'] = entry['author_email']
    unique_authors_with_lines = [
        {
            'author': author,
            'author_email': info['author_email'],
            'line_numbers': info['line_numbers'],
            'total_lines': info['total_lines']
        }
        for author, info in author_lines.items()
    ]

    return unique_authors_with_lines


def dict_to_json_file(output_folder, dictionary):
    with open(f"{output_folder}author-tracking.json" if output_folder else './author-tracking.json',
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

def is_record_declaration(source_code):
    # Pattern to detect `record` or `public record`
    record_pattern = re.compile(
        r'^\s*(?:public\s+)?record\s+\w+\s*\(.*?\)\s*\{',  # Match `record` declarations
        re.MULTILINE | re.DOTALL
    )
    return bool(record_pattern.search(source_code))



def parse_java_file(file_content):
    """Parsing the java file and finding the methods and their line ranges."""
    
    tree = javalang.parse.parse(file_content)
    package_name = get_file_package(tree)
    import_statements = [node.path for _, node in tree.filter(javalang.tree.Import)]

    methods = {}

    # Parsing each method declaration from each class in a file and keeping record of
    # start and end line of the method
    for _, classNode in tree.filter(javalang.tree.ClassDeclaration):
        for member in classNode.body:
            if isinstance(member, javalang.tree.MethodDeclaration) and member.position \
                    and member.body and member.name:

                start_line = member.position.line
                end_line = member.body[-1].position.line
                method_parameters = []

                for param in member.parameters:
                    param_name = param.name
                    param_type = param.type.name
                    method_parameters.append((param_type, param_name))
                full_method_name = get_full_method(classNode.name, package_name, member.name,
                                                   method_parameters, import_statements)
                methods[member.name] = (start_line, end_line, classNode.name, package_name,
                                        method_parameters, full_method_name)
    return methods


def find_last_author_per_method(file_path,file_content):
    methods = parse_java_file(file_content)
    methods_data = []
    method_line_info = []

    for method_name, (start_line, end_line, class_name, package_name, method_parameters,
                      full_method_name) in methods.items():
        if (method_name):
            last_author = None
            last_commit_time = None
            for line in range(start_line, end_line + 1):
                line_info = get_line_info(file_path, line)
                method_line_info.append({
                    **(line_info if line_info is not None else {}),
                    "line_number": line
                })
                if line_info:
                    commit_time = line_info["dateTime"]
                    if commit_time and (not last_commit_time or commit_time > \
                                        last_commit_time):
                        last_commit_time = commit_time
                        last_author = line_info["last_author"]
                        author_email = line_info["author_email"]
            top_contributor = get_top_contributor(method_line_info)
            all_authors = get_all_authors(method_line_info)
            method_line_info = []
            if last_author:
                methods_data.append(get_method_info(
                    package_name,
                    class_name,
                    method_name,
                    full_method_name,
                    last_author,
                    author_email,
                    datetime.fromtimestamp(last_commit_time).strftime('%Y-%m-%d %H:%M:%S'),
                    all_authors,
                    top_contributor
                ))
    return methods_data


if __name__ == '__main__':
    input_directory = input("Please enter the absolute path to the folder containing the 'main' directory: ")
    original_directory = os.getcwd()
    os.chdir(input_directory)
    output_folder = input(
        "Please enter output folder path for author-tracking.json (default: ./: ")
    # dir_path = r"./main"

    res= []
    for (dir_path, dir_names, file_names) in os.walk(input_directory):
        for fileName in file_names:
            res.append(f"{dir_path}/{fileName}")

    filesData = []
    methods_data = {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "edges": []}
    for fileName in res:
        if ('main' in fileName and fileName.split('.')[-1] == 'java'):
            file_content=read_java_source_file(fileName)
            if(not is_record_declaration(file_content)):
                methods_data['edges'] = methods_data['edges'] + find_last_author_per_method(fileName,file_content)

    os.chdir(original_directory)
    dict_to_json_file(output_folder, methods_data)
