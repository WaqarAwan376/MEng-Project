class EdgeRelation:
    def __init__(self, nodeType, propertyName, propertyValue):
        self.nodeType = nodeType
        self.propertyName = propertyName
        self.propertyValue = propertyValue

    def to_dict(self):
        return {
            "nodeType": self.nodeType,
            "propertyName": self.propertyName,
            "propertyValue": self.propertyValue
        }


class Edge:
    def __init__(self, relation_name, fromNodeType,
                 fromPropertyName, fromPropertyVal, toNodeType,
                 toPropertyName, toPropertyVal, properties=None):
        self.relationName = relation_name
        self.from_ = EdgeRelation(
            fromNodeType, fromPropertyName, fromPropertyVal)
        self.to_ = EdgeRelation(toNodeType, toPropertyName, toPropertyVal)
        if properties:
            self.properties = properties

    def to_dict(self):
        data = {
            "relationName": self.relationName,
            "from": self.from_.to_dict(),
            "to": self.to_.to_dict(),
        }
        if hasattr(self, "properties") and self.properties:
            data["properties"] = self.properties

        return data
