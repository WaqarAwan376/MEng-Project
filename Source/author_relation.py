import subprocess
import os
from collections import defaultdict
from itertools import combinations
from utils.helper import (dict_to_json_file, find_filtered_files, get_method_info)
from utils.nodes import AuthorNode, AuthorRelationStrengthNode
from utils.edges import Edge
from utils.enums import RelationType, NodeType

def get_pair_key(pair):
    return (pair[0]['author_email'],pair[1]['author_email'])

def remove_duplicates(authors_list):
    """ Remove repeating or duplicate authors from the list"""
    seen_emails=set()
    unique_authors=[]
    for author in authors_list:
        if author['author_email'] not in seen_emails:
            seen_emails.add(author['author_email'])
            unique_authors.append(author)
    return unique_authors

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
            line_info['author_name'] = line.split(' ', 1)[1]
        if line.startswith('author-mail '):
            line_info['author_email'] = line.split(' ', 1)[1] \
                .removeprefix('<').removesuffix('>')
    return line_info

def get_author_relation_strength(files_info_list):
    relation_strength = defaultdict()
    nodes=[]
    edges=[]
    for fileData in files_info_list['files']:
        # Extract unique authors for the current file
        authors_list = [item for item in fileData['contributors'] if \
            item['author_name'] != "Not Committed Yet"]
        authors_list = remove_duplicates(authors_list)
        # Calculate relation strength for the current file's authors
        for pair in combinations(authors_list, 2):
            pair_name = get_pair_key(pair)
            # Check if the pair_name already exists in relation_strength
            if pair_name in relation_strength:
                # Increment the strength if the pair already exists
                relation_strength[pair_name]['contribution_strength'].increment_strength()
            else:
                relation_strength[pair_name] = {
                    'author_1': AuthorNode(pair[0]['author_email'],pair[0]['author_name']),
                    'author_2': AuthorNode(pair[1]['author_email'],pair[1]['author_name']),
                    'contribution_strength': AuthorRelationStrengthNode(pair[0]['author_email'],pair[1]['author_email'])
                }

    for data_val in relation_strength.values():
        author1=data_val["author_1"]
        author2=data_val["author_2"]
        relation=data_val["contribution_strength"]
        
        if not any(node.type==NodeType.AUTHOR.value and node.email == author1.email for node in nodes):
            nodes.append(author1) 
        if not any(node.type==NodeType.AUTHOR.value and node.email == author2.email for node in nodes):
            nodes.append(author2) 
        nodes.append(relation)
 
        edges.append(Edge(
            RelationType.CONTRIBUTED.value, author1.type, author1.identifier, 
            author1.email, relation.type, relation.identifier, 
            relation.combined_emails
        ))         
        edges.append(Edge(
            RelationType.CONTRIBUTED.value, author2.type, author2.identifier, 
            author2.email, relation.type, relation.identifier, 
            relation.combined_emails
        ))         
        
    return {
        "probeName": "Authors_Relation",
        "nodes":[node.to_dict() for node in nodes],
        "edges":[edge.to_dict() for edge in edges]
    }


if __name__ == '__main__':
    input_directory = input("Please enter the absolute path to the folder containing the 'main' directory: ")
    original_directory = os.getcwd()
    os.chdir(input_directory)
    output_folder = input(
        "Please enter output folder path for author-tracking.json (default: ./outputs): ")

    # Extract all the required files from the given directory
    files_list= find_filtered_files(input_directory)

    # Extract Each line information from the files
    filesData = []
    extractedFileData=[]
    extracted_line_info = {"files": []}
    for fileName in files_list:
        with open(fileName, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                extractedFileData=extractedFileData+[get_line_info(fileName,line_number)]
            extracted_line_info['files'] = extracted_line_info['files'] + [{
                "file":fileName,
                "contributors":remove_duplicates(extractedFileData)
            }]
            extractedFileData=[]
            
    # Dump data into json files
    os.chdir(original_directory)
    dict_to_json_file("authors_relation",None, get_author_relation_strength(extracted_line_info))
