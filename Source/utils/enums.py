from enum import Enum


class NodeType(Enum):
    FILE = "File"
    CLASS = "Class"
    ENDPOINT = "Endpoint"
    AUTHOR = "Author"
    AUTHOR_RELATION = "Author_Relation"
    METHOD = "Method"


class RelationType(Enum):
    CONTAINS = "Contains"
    MAPS = "Maps"
    CONTRIBUTED = "Contributed"
    AUTHORED_BY = "Authored_by"
