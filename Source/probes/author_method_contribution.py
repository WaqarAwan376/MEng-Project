import subprocess
import javalang
import os
from collections import Counter, defaultdict
import re
from utils.helper import (read_java_source_file, get_file_package, dict_to_json_file,
                          probe_data_to_dict, get_full_method, get_passed_arguments,
                          convert_timestamp)
from utils.nodes import (AuthorNode, ClassNode, FileNode,
                         MethodNode)
from utils.edges import Edge
from utils.enums import RelationType


def get_top_contributor(method_info):
    """Get the top contributor of the method."""
    # Get author count from the method lines.
    author_counts = Counter(obj.get('last_author', 'unknown')
                            for obj in method_info)
    sorted_authors = sorted(author_counts.items(),
                            key=lambda item: (-item[1], item[0]))
    most_common_author = sorted_authors[0][0]

    author_details = defaultdict(lambda: {'emails': set(), 'line_numbers': []})
    for obj in method_info:
        author = obj.get('last_author', 'unknown')
        author_details[author]['emails'].add(
            obj.get('author_email', 'unknown'))
        author_details[author]['line_numbers'].append(
            obj.get('line_number', None))

    most_common_author_details = author_details[most_common_author]
    # Get the first element from the sorted list.
    emails = next(iter(most_common_author_details['emails']))
    lines_updated = most_common_author_details['line_numbers']

    return (AuthorNode(emails, most_common_author), lines_updated)


def get_all_authors(method_info):
    """Get all the authors of a method and their lines of contribution"""
    author_lines = {}

    for entry in method_info:
        if 'last_author' in entry:
            author = entry['last_author']
            author_lines[author] = {}
            author_lines[author]['author_email'] = entry['author_email']
    unique_authors_with_lines = [
        AuthorNode(info['author_email'], author)
        for author, info in author_lines.items()
    ]

    return unique_authors_with_lines


def get_line_info(file_path, line_number):
    """Get last commit author from the line number provided in the parameter."""
    cmd = ['git', 'blame', '-L', f'{line_number},{line_number}', '--date=iso', '-p',
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
    # Pattern to detect 'record' or 'public record'
    record_pattern = re.compile(
        # Match 'record' declarations
        r'^\s*(?:public\s+)?record\s+\w+\s*\(.*?\)\s*\{',
        re.MULTILINE | re.DOTALL
    )
    return bool(record_pattern.search(source_code))


def parse_java_file(file_content):
    """Parsing the java file and finding the methods and their line ranges."""
    tree = javalang.parse.parse(file_content)
    package_name = get_file_package(tree)
    import_statements = [node.path for _,
                         node in tree.filter(javalang.tree.Import)]
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
                methods[member.name] = (
                    start_line, end_line, classNode.name, full_method_name)
    return methods


def find_last_top_all_method_contributors(res):
    # file_path, file_content
    nodes = set()
    edges = []
    # Iterate over each file
    for fileName in res:
        if ('main' in fileName and fileName.split('.')[-1] == 'java'):
            file_content = read_java_source_file(fileName)
            if (not is_record_declaration(file_content)):
                try:
                    methods = parse_java_file(file_content)
                except:
                    continue
                method_line_info = []
                fileNode = FileNode(fileName.split(args.DIR_NAME)[1])
                nodes.add(fileNode)
                isClassEdgeAdded = False
                # Loop through each line of the method and extract information
                for method_name, (start_line, end_line, class_name,
                                  full_method_name) in methods.items():
                    if (method_name):
                        method_node = MethodNode(method_name, full_method_name)
                        nodes.add(method_node)
                        last_author = None
                        last_commit_time = None
                        for line in range(start_line, end_line + 1):
                            line_info = get_line_info(fileName, line)
                            method_line_info.append({
                                **(line_info if line_info is not None else {}),
                                "line_number": line})
                            if line_info:
                                commit_time = line_info["dateTime"]
                                if commit_time and (not last_commit_time or commit_time > last_commit_time):
                                    last_commit_time = commit_time
                                    last_author = line_info["last_author"]
                                    author_email = line_info["author_email"]
                        top_cont_info = get_top_contributor(method_line_info)
                        top_contributor = top_cont_info[0]
                        nodes.add(top_contributor)
                        edge_properties = {
                            "total_contribution": len(top_cont_info[1]),
                            "lines_contributed": top_cont_info[1]
                        }
                        edges.append(Edge(
                            RelationType.TOP_CONTRIBUTOR.value, method_node.type, method_node.identifier,
                            method_node.signature, top_contributor.type, top_contributor.identifier,
                            top_contributor.email, edge_properties
                        ))
                        all_authors = get_all_authors(method_line_info)
                        for author in all_authors:
                            edges.append(Edge(
                                RelationType.MODIFIED_BY.value, method_node.type, method_node.identifier,
                                method_node.signature, author.type, author.identifier,
                                author.email
                            ))
                        nodes = nodes | set(all_authors)
                        method_line_info = []
                        if last_author:
                            lastModifier = AuthorNode(
                                author_email, last_author)
                            nodes.add(lastModifier)
                            edges.append(Edge(
                                RelationType.LAST_MODIFIER.value, method_node.type, method_node.identifier,
                                method_node.signature, lastModifier.type, lastModifier.identifier,
                                lastModifier.email, {
                                    "last_modified_at": convert_timestamp(last_commit_time)}
                            ))
                            if not isClassEdgeAdded:
                                isClassEdgeAdded = True
                                classNode = ClassNode(
                                    class_name, fileNode.path)
                                nodes.add(classNode)
                                edges.append(Edge(
                                    RelationType.CONTAINS.value, fileNode.type, fileNode.identifier,
                                    fileNode.path, classNode.type, classNode.identifier,
                                    classNode.full_name
                                ))
                            edges.append(Edge(
                                RelationType.HAS.value, classNode.type, classNode.identifier,
                                classNode.full_name, method_node.type, method_node.identifier,
                                method_node.signature
                            ))

    return nodes, edges


args = get_passed_arguments(
    "--INPUT_DIR", "--OUTPUT", "--DIR_NAME", "--PROBE_NAME")
if __name__ == '__main__':
    print("Processing... ", end="", flush=True)

    original_directory = os.getcwd()
    os.chdir(args.INPUT_DIR)
    res = []
    for (dir_path, dir_names, file_names) in os.walk(args.INPUT_DIR):
        for fileName in file_names:
            res.append(f"{dir_path}/{fileName}")
    method_nodes_and_edges = find_last_top_all_method_contributors(res)
    nodes = method_nodes_and_edges[0]
    edges = method_nodes_and_edges[1]
    os.chdir(original_directory)
    dict_to_json_file(args.OUTPUT, probe_data_to_dict(
        args.PROBE_NAME, nodes, edges))

    print("Done")
