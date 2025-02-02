import os
from collections import defaultdict
from itertools import combinations
from utils.helper import (dict_to_json_file, find_filtered_files, get_author_node,
                          probe_data_to_dict)
from utils.nodes import AuthorRelationStrengthNode, FileNode, AuthorNode
from utils.edges import Edge
from utils.enums import RelationType, NodeType

def get_pair_key(pair):
    return (pair[0].email,pair[1].email)

def get_author_relation_strength(files_and_authors):
    relation_strength = defaultdict()
    nodes=[]
    edges=[]
    for fileData in files_and_authors:
        # Extract unique authors for the current file
        authors_list = [item for item in fileData['contributors'] if \
            item.name != "Not Committed Yet"]
        authors_list = AuthorNode.remove_duplicates(authors_list)
        # Calculate relation strength for the current file's authors
        for pair in combinations(authors_list, 2):
            pair_name = get_pair_key(pair)
            # Check if the pair_name already exists in relation_strength
            if pair_name in relation_strength:
                # Increment the strength if the pair already exists
                relation_strength[pair_name]['contribution_strength'].increment_strength()
            else:
                relation_strength[pair_name] = {
                    'author_1': pair[0],
                    'author_2': pair[1],
                    'contribution_strength': AuthorRelationStrengthNode(pair[0].email,pair[1].email)
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
        
    return probe_data_to_dict("Authors_Relation",nodes,edges)

def get_file_contributions(files_list):
    file_authors=[]
    files_with_unique_contributors_nodes = []
    files_contributors_nodes=[]
    files_contributors_edges=[]
    
    for fileName in files_list:
        with open(fileName, 'r') as file:
            for line_number, line in enumerate(file, start=1):
                file_authors=file_authors+[get_author_node(fileName,line_number)]
            file_contributors_unique=AuthorNode.remove_duplicates(file_authors)
            files_with_unique_contributors_nodes.append({
                "file":fileName,
                "contributors":file_contributors_unique
            })
            fileNode=FileNode(fileName.split('spring-petclinic-microservices')[1])
            files_contributors_nodes.append(fileNode)
            for authorNode in file_contributors_unique:
                if not any(node.type==NodeType.AUTHOR.value and node.email == authorNode.email for node in files_contributors_nodes):
                    files_contributors_nodes.append(authorNode) 
                files_contributors_edges.append(Edge(
                    RelationType.AUTHORED_BY.value, fileNode.type, fileNode.identifier, 
                    fileNode.path, authorNode.type, authorNode.identifier, 
                    authorNode.email))
            file_authors=[]
    
    return files_with_unique_contributors_nodes, files_contributors_nodes, files_contributors_edges

if __name__ == '__main__':
    input_directory = "/Users/waqarawan/Documents/University Masters Data/Program Project/spring-petclinic-microservices"
    original_directory = os.getcwd()
    os.chdir(input_directory)
    output_folder = input(
        "Please enter output folder path for author-tracking.json (default: ./outputs): ")

    print("Processing... ", end="", flush=True)
    # Extract all the required files from the given directory
    files_list= find_filtered_files(input_directory)

    # Extract data
    files_contributions=get_file_contributions(files_list)
    author_relation_nodes_edges=get_author_relation_strength(files_contributions[0])
    files_contributors_nodes_edges=probe_data_to_dict("FileContributors",files_contributions[1],files_contributions[2]) 
    # Dump data into json files
    os.chdir(original_directory)

    dict_to_json_file("code_contribution",output_folder, files_contributors_nodes_edges)
    dict_to_json_file("authors_relation",output_folder,author_relation_nodes_edges )
    print("Done")
