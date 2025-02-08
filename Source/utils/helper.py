import os
import json
import javalang
import subprocess
import argparse
from utils.constants import IGNORE_DIRS, IGNORE_FILES
from utils.nodes import AuthorNode


def dict_to_json_file(output_folder, dictionary):
    os.makedirs("./outputs/", exist_ok=True) if not output_folder else ''
    with open(output_folder, 'w') as file:
        json.dump(dictionary, file, indent=2, ensure_ascii=False)


def find_java_files(directory):
    """Find all Java files in the given directory."""
    java_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".java"):
                java_files.append(os.path.join(root, file))
    return java_files


def find_filtered_files(directory):
    """Find Files while ignoring specific directories and files."""
    files_list = []
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file in IGNORE_FILES or any(file.endswith(f) for f in IGNORE_FILES if f.startswith('.')):
                continue
            files_list.append(f"{root}/{file}")

    return files_list


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


def get_method_info(class_name, method_name,
                    full_method_name, author_username, author_email,
                    all_authors, top_contributor):
    return locals()


def get_author_node(file_path, line_number):
    """Get last commit author from the line number provided in the parameter."""
    cmd = ['git', 'blame', '-L', f'{line_number},{line_number}', '--date=iso', '-p',
           file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    author_info = {}
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        if line.startswith('author '):
            author_info['name'] = line.split(' ', 1)[1]
        if line.startswith('author-mail '):
            author_info['email'] = line.split(' ', 1)[1] \
                .removeprefix('<').removesuffix('>')
    return AuthorNode(author_info['email'], author_info['name'])


def probe_data_to_dict(probeName, nodes, edges):
    return {
        "probeName": probeName,
        "nodes": [node.to_dict() for node in nodes],
        "edges": [edge.to_dict() for edge in edges]
    }


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
            parameter_string += type if is_primitive_type(
                type) else f'java.lang.{type}'
        isImportFound = False

    full_method = ''
    if package_name:
        full_method += package_name + '.'
    if class_name:
        full_method += class_name + '.'

    full_method += f'{method_name}({parameter_string})'
    return full_method


def get_passed_arguments(*args):
    parser = argparse.ArgumentParser()
    for arg in args:
        parser.add_argument(arg)

    return parser.parse_args()
