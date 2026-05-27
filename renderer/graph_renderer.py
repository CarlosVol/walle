import pyray as pr
from graph.model import Node, Edge

NODE_RADIUS = 26

_C_DEFAULT  = pr.LIGHTGRAY
_C_PATH     = pr.GOLD
_C_CURRENT  = pr.GREEN
_C_START    = pr.BLUE
_C_END      = pr.RED
_C_VISITED  = pr.DARKGRAY
_C_ADJACENT = pr.SKYBLUE


def _node_color(
    node_id: str,
    optimal_path: list[str],
    current_node: str,
    visited: set[str],
    start_node: str,
    end_node: str,
    adjacent: list[str],
) -> pr.Color:
    if node_id == current_node:
        return _C_CURRENT
    if node_id == end_node:
        return _C_END
    if node_id == start_node:
        return _C_START
    if node_id in visited:
        return _C_VISITED
    if node_id in adjacent:
        return _C_ADJACENT
    if node_id in optimal_path:
        return _C_PATH
    return _C_DEFAULT


def draw_graph(
    nodes: dict[str, Node],
    edges: list[Edge],
    optimal_path: list[str],
    current_node: str,
    visited: set[str],
    start_node: str,
    end_node: str,
    adjacent: list[str],
) -> str | None:
    path_set = set(zip(optimal_path, optimal_path[1:]))

    # edges
    for e in edges:
        na, nb = nodes[e.a], nodes[e.b]
        on_path = (e.a, e.b) in path_set or (e.b, e.a) in path_set
        color = pr.GOLD if on_path else pr.DARKGRAY
        thick = 4.0 if on_path else 2.0
        pr.draw_line_ex(
            pr.Vector2(na.x, na.y),
            pr.Vector2(nb.x, nb.y),
            thick,
            color,
        )
        # weight label
        mx = int((na.x + nb.x) / 2)
        my = int((na.y + nb.y) / 2)
        pr.draw_text(f"{e.weight:.0f}", mx, my, 14, pr.LIGHTGRAY)

    # nodes
    mx_pos = pr.get_mouse_x()
    my_pos = pr.get_mouse_y()
    clicked: str | None = None

    for node in nodes.values():
        color = _node_color(
            node.id, optimal_path, current_node,
            visited, start_node, end_node, adjacent,
        )
        pr.draw_circle(int(node.x), int(node.y), NODE_RADIUS, color)
        pr.draw_circle_lines(int(node.x), int(node.y), NODE_RADIUS, pr.WHITE)

        lw = pr.measure_text(node.label, 14)
        pr.draw_text(node.label, int(node.x) - lw // 2, int(node.y) - 7, 14, pr.BLACK)

        dist = ((mx_pos - node.x) ** 2 + (my_pos - node.y) ** 2) ** 0.5
        if dist <= NODE_RADIUS and pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT):
            clicked = node.id

    return clicked
