from .model import Node, Edge

NODES: dict[str, Node] = {
    "A": Node("A", "Alpha",   150, 150),
    "B": Node("B", "Beta",    350,  80),
    "C": Node("C", "Gamma",   600, 120),
    "D": Node("D", "Delta",   280, 300),
    "E": Node("E", "Epsilon", 520, 320),
    "F": Node("F", "Zeta",    680, 450),
}

EDGES: list[Edge] = [
    Edge("A", "B", 1.0),
    Edge("A", "D", 2.0),
    Edge("B", "C", 1.5),
    Edge("B", "D", 1.0),
    Edge("C", "E", 1.0),
    Edge("D", "E", 1.5),
    Edge("E", "F", 1.0),
    Edge("D", "F", 3.0),
]
