from enum import Enum


class NodeType(Enum):
    FILE = "File"
    CLASS = "Class"
    ENDPOINT = "Endpoint"
    AUTHOR = "Author"
    AUTHOR_RELATION = "Author_Relation"
    METHOD = "Method"
    DEPENDENCY = "Dependency"


class RelationType(Enum):
    CONTAINS = "Contains"
    MAPS = "Maps"
    CONTRIBUTED = "Contributed"
    AUTHORED_BY = "Authored_by"
    HAS = "Has"
    TOP_CONTRIBUTOR = "Top_contributor"
    MODIFIED_BY = "Modified_by"
    LAST_MODIFIER = "Last_modifier"
    DEPENDS_ON = "Depends_on"
    HAS_BEAN_CLASS = "Has_bean_class"
    HAS_BEAN_METHOD = "Has_bean_method"
