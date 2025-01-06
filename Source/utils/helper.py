import os
import json
import javalang

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


def get_method_info(package_name, class_name, method_name, full_method_name, author_username,
                    author_email, time, all_authors, top_contributor):
    return locals()