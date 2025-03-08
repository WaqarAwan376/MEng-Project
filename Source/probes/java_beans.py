import os
import re
import javalang
from utils.helper import dict_to_json_file, get_passed_arguments
from utils.nodes import FileNode, ClassNode, MethodNode
from utils.helper import get_file_package, get_full_method, probe_data_to_dict
from utils.edges import Edge
from utils.enums import RelationType
from utils.constants import BEAN_ANNOTATIONS, CLASS_PATTERN, METHOD_PATTERN


def get_methods_list(file_content):
    """Parsing the java file and finding the methods and their line ranges."""

    tree = javalang.parse.parse(file_content)
    package_name = get_file_package(tree)
    import_statements = [node.path for _,
                         node in tree.filter(javalang.tree.Import)]
    methods = {}

    # Handle methods inside classes
    for _, classNode in tree.filter(javalang.tree.ClassDeclaration):
        for member in classNode.body:
            if isinstance(member, javalang.tree.MethodDeclaration) and member.position \
                    and member.body and member.name:
                method_parameters = [(param.type.name, param.name)
                                     for param in member.parameters]
                full_method_name = get_full_method(classNode.name, package_name, member.name,
                                                   method_parameters, import_statements)
                methods[member.name] = full_method_name

    return methods


def extract_spring_beans(directory):
    nodes = set()
    edges = []

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if ('main' in file_path and file.split('.')[-1] == 'java'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    file_node = FileNode(file_path.split(
                        args.DIR_NAME)[1])
                    nodes.add(file_node)
                    # Track whether we are in a multiline annotation
                    inside_annotation = False
                    annotation_buffer = ""
                    potential_bean = None

                    lines = content.splitlines()

                    for i, line in enumerate(lines):
                        line = line.strip()

                        # Check if the line contains part of an annotation
                        for annotation in BEAN_ANNOTATIONS:
                            if annotation in line or inside_annotation:
                                if not inside_annotation:
                                    annotation_buffer = annotation
                                    inside_annotation = True

                                # If the annotation is still continuing across lines
                                if "(" in line and ")" not in line:
                                    annotation_buffer += line
                                    continue

                                inside_annotation = False
                                potential_bean = annotation_buffer
                                annotation_buffer = ""

                        # If a class is found after an annotation
                        if potential_bean:
                            class_match = re.search(CLASS_PATTERN, line)
                            if class_match:
                                class_name = class_match.group(2)
                                class_node = ClassNode(
                                    class_name, file_node.path)
                                nodes.add(class_node)
                                edges.append(Edge(
                                    RelationType.HAS_BEAN_CLASS.value, file_node.type, file_node.identifier,
                                    file_node.path, class_node.type, class_node.identifier,
                                    class_node.full_name
                                ))
                                potential_bean = None

                        # If a method is found after an annotation
                        if potential_bean and potential_bean == "@Bean":
                            method_match = re.search(METHOD_PATTERN, line)
                            if method_match:
                                method_name = method_match.group(1)
                                try:
                                    method_list = get_methods_list(content)
                                except:
                                    continue
                                method_node = MethodNode(
                                    method_name, method_list[method_name])
                                nodes.add(method_node)
                                edges.append(Edge(
                                    RelationType.HAS_BEAN_METHOD.value, class_node.type, class_node.identifier,
                                    class_node.full_name, method_node.type, method_node.identifier,
                                    method_node.signature
                                ))
                                potential_bean = None

    return {"nodes": nodes, "edges": edges}


args = get_passed_arguments("--INPUT_DIR", "--OUTPUT", "--DIR_NAME")
if __name__ == '__main__':
    print("Processing... ", end="", flush=True)

    spring_beans = extract_spring_beans(args.INPUT_DIR)
    dict_to_json_file(args.OUTPUT, probe_data_to_dict(
        "Beans", spring_beans["nodes"], spring_beans["edges"]))

    print("Done")
