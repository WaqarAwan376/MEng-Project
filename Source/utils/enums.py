from enum import Enum

class NodeType(Enum):
    FILE = "File"
    CLASS = "Class"
    ENDPOINT = "Endpoint"


class RelationType(Enum):
    CONTAINS = "Contains"
    MAPS = "Maps"