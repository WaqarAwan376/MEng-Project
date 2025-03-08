import xml.etree.ElementTree as ET
import os
import re
from utils.helper import dict_to_json_file, get_passed_arguments, probe_data_to_dict
from utils.nodes import DependencyNode, FileNode
from utils.edges import Edge
from utils.enums import RelationType


def find_pom_files(directory):
    """ Find all pom files in the given directory. """
    pom_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file == "pom.xml":
                pom_file_path = os.path.join(root, file)
                # Get the parent folder name
                parent_folder = os.path.basename(root)
                pom_files.append({
                    'file_path': pom_file_path,
                    'parent_folder': parent_folder
                })
    return pom_files


def get_version(root, version_text):
    namespace = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
    properties = root.find("mvn:properties", namespaces=namespace)
    # Search for the match
    pattern = r"\$\{([^}]+)\}"
    match = re.search(pattern, version_text)
    if match:
        inside_text = match.group(1)  # Extract the text inside ${}
        return (properties.find(f'mvn:{inside_text}', namespaces=namespace)).text
    else:
        return 'N/A'


def extract_dependencies(pom_files_list):
    # Parse the XML file
    nodes = set()
    edges = []
    for pom_file_info in pom_files_list:
        tree = ET.parse(pom_file_info['file_path'])
        root = tree.getroot()
        fileNode = FileNode(pom_file_info['file_path'].split(
            args.DIR_NAME)[1])
        nodes.add(fileNode)
        # Define the namespace (Maven uses this in the pom.xml)
        namespace = {'mvn': 'http://maven.apache.org/POM/4.0.0'}

        # Find all dependencies in the pom.xml
        dependencies = root.findall(".//mvn:dependency", namespaces=namespace)

        # List to store extracted dependencies
        for dependency in dependencies:
            group_id = dependency.find('mvn:groupId', namespaces=namespace)
            artifact_id = dependency.find(
                'mvn:artifactId', namespaces=namespace)
            version = dependency.find('mvn:version', namespaces=namespace)
            scope = dependency.find('mvn:scope', namespaces=namespace)
            type = dependency.find('mvn:type', namespaces=namespace)
            optional = dependency.find('mvn:optional', namespaces=namespace)
            # version = dependency.find('mvn:version', namespaces=namespace)

            # Get the text, if any element is missing, replace it with an empty string
            dependency_node = DependencyNode(group_id.text, artifact_id.text)
            nodes.add(dependency_node)
            edge_properties = {}
            if version is not None:
                edge_properties['version'] = get_version(root, version.text)
            if scope is not None:
                edge_properties['scope'] = scope.text
            if type is not None:
                edge_properties['type'] = type.text
            if optional is not None:
                edge_properties['optional'] = optional.text

            edges.append(Edge(
                RelationType.DEPENDS_ON.value, fileNode.type, fileNode.identifier,
                fileNode.path, dependency_node.type, dependency_node.identifier,
                dependency_node.combined_name, edge_properties
            ))

    return {"nodes": nodes, "edges": edges}


args = get_passed_arguments("--INPUT_DIR", "--OUTPUT", "--DIR_NAME")
if __name__ == '__main__':
    print("Processing... ", end="", flush=True)

    pom_files = find_pom_files(args.INPUT_DIR)
    dependencies_list = extract_dependencies(pom_files)
    dict_to_json_file(args.OUTPUT, probe_data_to_dict(
        "Dependencies", dependencies_list['nodes'], dependencies_list['edges']))

    print("Done")
