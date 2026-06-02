from .model import Node, Edge

NODES: dict[str, Node] = {
    "A": Node("A", "A", 130, 140),
    "B": Node("B", "B", 350,  80),
    "C": Node("C", "C", 620, 110),
    "D": Node("D", "D", 280, 300),
    "E": Node("E", "E", 520, 320),
    "F": Node("F", "F", 700, 440),
    "G": Node("G", "G", 140, 470),
    "H": Node("H", "H", 430, 510),
    "I": Node("I", "I", 730, 240),
}

EDGES: list[Edge] = [
    Edge("A", "B", 1.0),
    Edge("A", "D", 2.0),
    Edge("B", "C", 1.5),
    Edge("B", "D", 1.0),
    Edge("C", "E", 1.0),
    Edge("C", "I", 1.0),
    Edge("D", "E", 1.5),
    Edge("D", "F", 3.0),
    Edge("E", "F", 1.0),
    Edge("A", "G", 1.5),
    Edge("D", "G", 1.0),
    Edge("G", "H", 1.5),
    Edge("H", "E", 1.0),
    Edge("H", "F", 1.5),
    Edge("I", "E", 1.5),
    Edge("I", "F", 1.0),
]
