"""Corta las imagenes rompe_{1,2,3} en piezas jigsaw 3x3 con pestañas.

Genera images/minigame_rompecabezas/piezas/rompe{V}_{r}_{c}.png (con alpha)
y manifest.json. Las pestañas (knob/+1) y huecos (blank/-1) son complementarios
entre piezas vecinas, asi encajan.
"""
import json
import os
import random

from PIL import Image, ImageDraw

BASE  = os.path.join(os.path.dirname(__file__), "..", "images", "minigame_rompecabezas")
BASE  = os.path.abspath(BASE)
OUT   = os.path.join(BASE, "piezas")
GRID  = 3
VARIANTS = (1, 2, 3)


def build_edge_signs(seed: int):
    """Asigna +-1 a cada arista interna. Devuelve por pieza (top,right,bottom,left).

    0 = borde plano (externo). Vecinos comparten arista con signos opuestos.
    """
    rng = random.Random(seed)
    # vert[r][c] = signo del borde derecho de la pieza (r,c)  (c en 0..GRID-2)
    vert = [[rng.choice((-1, 1)) for _ in range(GRID - 1)] for _ in range(GRID)]
    # horz[r][c] = signo del borde inferior de la pieza (r,c) (r en 0..GRID-2)
    horz = [[rng.choice((-1, 1)) for _ in range(GRID)] for _ in range(GRID - 1)]

    edges = {}
    for r in range(GRID):
        for c in range(GRID):
            top    = 0 if r == 0          else -horz[r - 1][c]
            bottom = 0 if r == GRID - 1   else  horz[r][c]
            left   = 0 if c == 0          else -vert[r][c - 1]
            right  = 0 if c == GRID - 1   else  vert[r][c]
            edges[(r, c)] = (top, right, bottom, left)
    return edges


def piece_mask(cell: int, R: int, M: int, signs) -> Image.Image:
    """Mascara 'L' del canvas (cell+2M). signs=(top,right,bottom,left)."""
    top, right, bottom, left = signs
    size = cell + 2 * M
    mask = Image.new("L", (size, size), 0)
    d = ImageDraw.Draw(mask)
    # rectangulo base de la celda
    x0, y0 = M, M
    x1, y1 = M + cell, M + cell
    d.rectangle([x0, y0, x1, y1], fill=255)

    def knob(cx, cy, sign):
        bbox = [cx - R, cy - R, cx + R, cy + R]
        if sign > 0:
            d.ellipse(bbox, fill=255)      # sobresale (union)
        elif sign < 0:
            d.ellipse(bbox, fill=0)        # muerde hueco (resta)

    midx = M + cell // 2
    midy = M + cell // 2
    knob(midx, y0, top)       # arista superior
    knob(x1,   midy, right)   # arista derecha
    knob(midx, y1, bottom)    # arista inferior
    knob(x0,   midy, left)    # arista izquierda
    return mask


def cut_variant(v: int, manifest_acc: dict) -> None:
    src = Image.open(os.path.join(BASE, f"rompe_{v}.png")).convert("RGBA")
    W, H = src.size
    cell = W // GRID            # imagenes ~cuadradas; usamos ancho
    R    = int(cell * 0.20)
    M    = R + 4
    size = cell + 2 * M

    edges = build_edge_signs(seed=v * 1000 + 7)

    for r in range(GRID):
        for c in range(GRID):
            cell_x = c * cell
            cell_y = r * cell
            # recorte de la imagen fuente centrado en la celda con margen M
            crop = Image.new("RGBA", (size, size), (0, 0, 0, 0))
            sx = cell_x - M
            sy = cell_y - M
            region = src.crop((sx, sy, sx + size, sy + size))
            crop.paste(region, (0, 0))

            mask = piece_mask(cell, R, M, edges[(r, c)])
            crop.putalpha(mask)

            crop.save(os.path.join(OUT, f"rompe{v}_{r}_{c}.png"))

    manifest_acc[str(v)] = {"grid": GRID, "margin": M, "cell": cell, "img_w": W, "img_h": H}


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    manifest = {}
    for v in VARIANTS:
        cut_variant(v, manifest)
        print(f"rompe_{v}: piezas generadas")
    with open(os.path.join(OUT, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print("manifest.json escrito:", manifest)


if __name__ == "__main__":
    main()
