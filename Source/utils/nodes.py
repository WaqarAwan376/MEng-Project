from .enums import NodeType

class Node:
    def __init__(self, node_type):
        self.type = node_type

        
class FileNode(Node):
    def __init__(self, path):
        super().__init__(NodeType.FILE.value)
        self.path=path
        self.identifier="Path"
    
    def to_dict(self):
        return {"type":self.type,"path":self.path}
        

class ClassNode(Node):
    def __init__(self, className, fullName):
        super().__init__(NodeType.CLASS.value)
        self.name = className
        self.full_name = fullName
        self.identifier="FullName"

    def to_dict(self):
        return {"type":self.type,"name":self.name,"full_name":self.full_name}
        

class EndpointNode(Node):
    def __init__(self, http_method, route):
        super().__init__(NodeType.ENDPOINT.value)
        self.http_method = http_method
        self.route = route
        self.full_method_id=f"{http_method} - {route}"
        self.identifier="FullMethodId"

    def to_dict(self):
        return {"type":self.type, 
                "full_method_id":self.full_method_id,
                "http_method":self.http_method,
                "route":self.route
            }

