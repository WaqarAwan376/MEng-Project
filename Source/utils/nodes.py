from .enums import NodeType

class Node:
    def __init__(self, node_type):
        self.type = node_type

        
class FileNode(Node):
    def __init__(self, path):
        super().__init__(NodeType.FILE.value)
        self.path=path
        self.identifier="path"
    
    def to_dict(self):
        return {"type":self.type,"path":self.path}
        

class ClassNode(Node):
    def __init__(self, className, fullName):
        super().__init__(NodeType.CLASS.value)
        self.name = className
        self.full_name = fullName
        self.identifier="full_name"

    def to_dict(self):
        return {"type":self.type,"name":self.name,"full_name":self.full_name}
        

class EndpointNode(Node):
    def __init__(self, http_method, route):
        super().__init__(NodeType.ENDPOINT.value)
        self.http_method = http_method
        self.route = route
        self.full_method_id=f"{http_method} - {route}"
        self.identifier="full_method_id"

    def to_dict(self):
        return {"type":self.type, 
                "full_method_id":self.full_method_id,
                "http_method":self.http_method,
                "route":self.route
            }
        

class AuthorNode(Node):
    def __init__(self, email, name):
        super().__init__(NodeType.AUTHOR.value)
        self.name = name
        self.email = email
        self.identifier="email"

    def to_dict(self):
        return {"type":self.type,"name":self.name,"email":self.email}
        

class AuthorRelationStrengthNode(Node):
    def __init__(self, authEmail1, authEmail2):
        super().__init__(NodeType.AUTHOR_RELATION.value)
        self.author1Email = authEmail1
        self.author2Email = authEmail2
        self.combined_emails = f"{self.author1Email}:{self.author2Email}"
        self.strength=1
        self.identifier="combined_emails"

    def increment_strength(self):
        self.strength+=1
        
    def to_dict(self):
        return {"type":self.type,
                "author1":self.author1Email,
                "author2":self.author2Email,
                "combined_emails":self.combined_emails,
                "strength":str(self.strength)
            }