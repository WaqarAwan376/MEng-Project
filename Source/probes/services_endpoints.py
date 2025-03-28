import os
import re
from utils.constants import method_patterns
from utils.constants import class_pattern
from utils.helper import dict_to_json_file, get_passed_arguments, probe_data_to_dict
from utils.helper import find_java_files
from utils.nodes import FileNode, ClassNode, EndpointNode
from utils.edges import Edge
from utils.enums import RelationType


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
                            full_path = (base_url + sub_path.strip()
                                         ).replace("//", "/")
                            paths.append(EndpointNode(request_type, full_path))
                else:
                    # No specific path, assume class-level base path
                    full_path = base_url.rstrip("/")
                    paths.append(
                        EndpointNode(
                            request_type, full_path if full_path else "/")
                    )

    # Deduplicate paths
    if len(paths) == 0:
        return []

    unique_paths = {f"{p.full_method_id}": p for p in paths}
    return list(unique_paths.values())


def extract_all_paths(directory):
    """Extract REST paths from all Java files in the given directory."""
    java_files = find_java_files(directory)
    nodes = []
    edges = []
    for java_file in java_files:
        paths = extract_paths_from_file(java_file)
        if paths:
            class_name = os.path.basename(java_file).replace(".java", "")
            file_path = java_file.split(args.DIR_NAME)[1]
            fileNode = FileNode(file_path)
            classNode = ClassNode(class_name, file_path)
            # Add Nodes
            nodes.append(fileNode)
            nodes.append(classNode)

            # Add File to Class Relation
            edges.append(Edge(
                RelationType.CONTAINS.value, fileNode.type, fileNode.identifier,
                fileNode.path, classNode.type, classNode.identifier,
                classNode.full_name
            ))

            for path in paths:
                # Add Nodes
                nodes.append(path)
                # Add File to Endpoint Relation
                edges.append(Edge(
                    RelationType.MAPS.value, classNode.type, classNode.identifier,
                    classNode.full_name, path.type, path.identifier,
                    path.full_method_id
                ))
    return probe_data_to_dict(args.PROBE_NAME, nodes, edges)


args = get_passed_arguments(
    "--INPUT_DIR", "--OUTPUT", "--DIR_NAME", "--PROBE_NAME")
if __name__ == "__main__":
    print("Processing... ", end="", flush=True)

    original_directory = os.getcwd()
    os.chdir(args.INPUT_DIR)
    paths = extract_all_paths(args.INPUT_DIR)
    # Write paths to a JSON file
    os.chdir(original_directory)
    dict_to_json_file(args.OUTPUT, paths)

    print("Done")
