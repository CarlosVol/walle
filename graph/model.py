from dataclasses import dataclass


@dataclass(frozen=True)
class Node:
    id:    str
    label: str
    x:     float
    y:     float


@dataclass(frozen=True)
class Edge:
    a:      str
    b:      str
    weight: float = 1.0
