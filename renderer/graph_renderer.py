import math
import pyray as pr
from graph.model import Node, Edge

_BASE_W    = 800
_BASE_H    = 600
NODE_R     = 32
GLOW_STEPS = 5


def _scale(x: float, y: float, sw: int, sh: int) -> tuple[int, int]:
    return int(x * sw / _BASE_W), int(y * sh / _BASE_H)


def _glow(nx: int, ny: int, r: int, color: pr.Color, steps: int = GLOW_STEPS) -> None:
    for i in range(steps, 0, -1):
        pr.draw_circle(nx, ny, r + i * 6, pr.fade(color, (i / steps) * 0.32))


def _shadow(nx: int, ny: int, r: int) -> None:
    pr.draw_circle(nx + 4, ny + 5, r + 2, pr.Color(0, 0, 0, 100))


def _draw_node(
    nx: int, ny: int, node_id: str,
    fill: pr.Color, border: pr.Color,
    glow: bool = False,
    pulse: bool = False,
    label_above: str = "",
    label_below: str = "",
) -> None:
    r = NODE_R
    if pulse:
        r = NODE_R + int(4 * math.sin(pr.get_time() * 5))

    if glow:
        _glow(nx, ny, r, fill)

    _shadow(nx, ny, r)
    pr.draw_circle(nx, ny, r, fill)
    pr.draw_circle_lines(nx, ny, r, border)
    # second ring for polish
    pr.draw_circle_lines(nx, ny, r - 3, pr.fade(border, 0.31))

    # node ID centered
    id_size = 20
    iw = pr.measure_text(node_id, id_size)
    pr.draw_text(node_id, nx - iw // 2, ny - id_size // 2, id_size, pr.WHITE)

    if label_above:
        fs = 16
        lw = pr.measure_text(label_above, fs)
        pr.draw_text(label_above, nx - lw // 2, ny - r - fs - 6, fs, border)

    if label_below:
        fs = 16
        lw = pr.measure_text(label_below, fs)
        pr.draw_text(label_below, nx - lw // 2, ny + r + 6, fs, border)


def _draw_edge(
    ax: int, ay: int, bx: int, by: int,
    on_path: bool,
    weight: float,
) -> None:
    if on_path:
        # outer glow
        pr.draw_line_ex(
            pr.Vector2(ax, ay), pr.Vector2(bx, by),
            12.0, pr.Color(255, 200, 0, 40),
        )
        pr.draw_line_ex(
            pr.Vector2(ax, ay), pr.Vector2(bx, by),
            6.0, pr.Color(255, 200, 0, 120),
        )
        pr.draw_line_ex(
            pr.Vector2(ax, ay), pr.Vector2(bx, by),
            3.0, pr.GOLD,
        )
    else:
        pr.draw_line_ex(
            pr.Vector2(ax, ay), pr.Vector2(bx, by),
            2.0, pr.Color(80, 80, 80, 180),
        )


def draw_graph(
    nodes: dict[str, Node],
    edges: list[Edge],
    optimal_path: list[str],
    current_node: str,
    visited: set[str],
    start_node: str,
    end_node: str,
    adjacent: list[str],
    sw: int,
    sh: int,
) -> str | None:
    path_set = set(zip(optimal_path, optimal_path[1:]))

    # edges (drawn before nodes so nodes sit on top)
    for e in edges:
        na, nb = nodes[e.a], nodes[e.b]
        ax, ay = _scale(na.x, na.y, sw, sh)
        bx, by = _scale(nb.x, nb.y, sw, sh)
        on_path = (e.a, e.b) in path_set or (e.b, e.a) in path_set
        _draw_edge(ax, ay, bx, by, on_path, e.weight)

    mx_pos = pr.get_mouse_x()
    my_pos = pr.get_mouse_y()
    clicked: str | None = None

    for node in nodes.values():
        nx, ny = _scale(node.x, node.y, sw, sh)
        nid    = node.id

        is_current  = nid == current_node
        is_start    = nid == start_node
        is_end      = nid == end_node
        is_visited  = nid in visited
        is_adjacent = nid in adjacent
        is_path     = nid in optimal_path

        # pick fill + border
        if is_current:
            fill   = pr.Color(0, 210, 180, 255)   # teal
            border = pr.WHITE
        elif is_end:
            fill   = pr.Color(220, 50, 50, 255)    # crimson
            border = pr.Color(255, 120, 120, 255)
        elif is_start:
            fill   = pr.Color(50, 180, 80, 255)    # emerald
            border = pr.Color(120, 255, 140, 255)
        elif is_visited:
            fill   = pr.Color(50, 50, 50, 255)
            border = pr.Color(90, 90, 90, 255)
        elif is_adjacent:
            fill   = pr.Color(60, 130, 200, 255)   # steel blue
            border = pr.Color(140, 200, 255, 255)
        elif is_path:
            fill   = pr.Color(180, 130, 0, 255)    # dark gold
            border = pr.GOLD
        else:
            fill   = pr.Color(70, 70, 80, 255)
            border = pr.Color(130, 130, 140, 255)

        label_above = ""
        label_below = ""
        if is_start and not is_current:
            label_above = "INICIO"
        if is_end:
            label_above = "META"

        _draw_node(
            nx, ny, nid,
            fill, border,
            glow=is_current or is_adjacent or is_end,
            pulse=is_current,
            label_above=label_above,
            label_below=label_below,
        )

        # hover ring for adjacent (clickable hint)
        if is_adjacent:
            dist = ((mx_pos - nx) ** 2 + (my_pos - ny) ** 2) ** 0.5
            if dist <= NODE_R + 10:
                pr.draw_circle_lines(nx, ny, NODE_R + 8, pr.Color(140, 200, 255, 180))

        dist = ((mx_pos - nx) ** 2 + (my_pos - ny) ** 2) ** 0.5
        if dist <= NODE_R and pr.is_mouse_button_pressed(pr.MOUSE_BUTTON_LEFT):
            clicked = nid

    return clicked
