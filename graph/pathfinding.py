import heapq
from .model import Node, Edge


def build_adjacency(edges: list[Edge]) -> dict[str, list[tuple[str, float]]]:
    adj: dict[str, list[tuple[str, float]]] = {}
    for e in edges:
        adj.setdefault(e.a, []).append((e.b, e.weight))
        adj.setdefault(e.b, []).append((e.a, e.weight))
    return adj


def dijkstra(
    nodes: dict[str, Node],
    edges: list[Edge],
    start: str,
    end: str,
) -> list[str]:
    adj = build_adjacency(edges)
    dist = {n: float("inf") for n in nodes}
    dist[start] = 0.0
    prev: dict[str, str | None] = {n: None for n in nodes}
    heap = [(0.0, start)]

    while heap:
        cost, u = heapq.heappop(heap)
        if cost > dist[u]:
            continue
        if u == end:
            break
        for v, w in adj.get(u, []):
            nc = dist[u] + w
            if nc < dist[v]:
                dist[v] = nc
                prev[v] = u
                heapq.heappush(heap, (nc, v))

    if dist[end] == float("inf"):
        return []

    path = []
    cur: str | None = end
    while cur is not None:
        path.append(cur)
        cur = prev[cur]
    path.reverse()
    return path


def get_adjacent(edges: list[Edge], node_id: str) -> list[str]:
    result = []
    for e in edges:
        if e.a == node_id:
            result.append(e.b)
        elif e.b == node_id:
            result.append(e.a)
    return result
