from .enums import NodeType


class Node:
    def __init__(self, node_type):
        self.type = node_type


class FileNode(Node):
    def __init__(self, path):
        super().__init__(NodeType.FILE.value)
        self.path = path
        self.identifier = "path"

    def to_dict(self):
        return {"type": self.type, "path": self.path}


class ClassNode(Node):
    def __init__(self, className, filePath):
        super().__init__(NodeType.CLASS.value)
        self.name = className
        self.full_name = f"{filePath}:{className}"
        self.identifier = "full_name"

    def to_dict(self):
        return {"type": self.type, "name": self.name, "full_name": self.full_name}

    def __eq__(self, other):
        if isinstance(other, ClassNode):
            return self.full_name == other.full_name
        return False

    def __hash__(self):
        return hash((self.name, self.full_name))


class EndpointNode(Node):
    def __init__(self, http_method, route):
        super().__init__(NodeType.ENDPOINT.value)
        self.http_method = http_method
        self.route = route
        self.full_method_id = f"{http_method} - {route}"
        self.identifier = "full_method_id"

    def to_dict(self):
        return {"type": self.type,
                "full_method_id": self.full_method_id,
                "http_method": self.http_method,
                "route": self.route
                }


class AuthorNode(Node):
    def __init__(self, email, name):
        super().__init__(NodeType.AUTHOR.value)
        self.name = name
        self.email = email
        self.identifier = "email"

    def to_dict(self):
        return {"type": self.type, "name": self.name, "email": self.email}

    @staticmethod
    def remove_duplicates(authors_list):
        """Remove repeating or duplicate authors from the list"""
        seen_emails = set()
        unique_authors = []
        for author in authors_list:
            if author.email not in seen_emails:
                seen_emails.add(author.email)
                unique_authors.append(author)
        return unique_authors

    def __eq__(self, other):
        if isinstance(other, AuthorNode):
            return self.name == other.name and self.email == other.email
        return False

    def __hash__(self):
        return hash((self.name, self.email))


class AuthorRelationStrengthNode(Node):
    def __init__(self, authEmail1, authEmail2):
        super().__init__(NodeType.AUTHOR_RELATION.value)
        self.author1Email = authEmail1
        self.author2Email = authEmail2
        self.combined_emails = f"{self.author1Email}:{self.author2Email}"
        self.strength = 1
        self.identifier = "combined_emails"

    def increment_strength(self):
        self.strength += 1

    def to_dict(self):
        return {"type": self.type,
                "author1": self.author1Email,
                "author2": self.author2Email,
                "combined_emails": self.combined_emails,
                "strength": self.strength
                }


class MethodNode(Node):
    def __init__(self, name, full_method_name):
        super().__init__(NodeType.METHOD.value)
        self.name = name
        self.signature = full_method_name
        self.identifier = "signature"

    def to_dict(self):
        return {"type": self.type,
                "name": self.name,
                "signature": self.signature
                }


class DependencyNode(Node):
    def __init__(self, group_id, artifact_id):
        super().__init__(NodeType.DEPENDENCY.value)
        self.group_id = group_id
        self.artifact_id = artifact_id
        self.combined_name = f"{group_id}:{artifact_id}"
        self.identifier = "combined_name"

    def to_dict(self):
        return {"type": self.type,
                "group_id": self.group_id,
                "artifact_id": self.artifact_id,
                "combined_name": self.combined_name,
                }

    def __eq__(self, other):
        if isinstance(other, DependencyNode):
            return self.combined_name == other.combined_name
        return False

    def __hash__(self):
        return hash((self.artifact_id, self.combined_name))
