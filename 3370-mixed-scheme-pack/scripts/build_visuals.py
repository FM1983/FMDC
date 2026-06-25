#!/usr/bin/env python3
"""
3370 Great North Road - Mixed Residential Scheme
Schematic diagram generator (six figures).

EVERY figure here is a SCHEMATIC DIAGRAM, never architecture. Flat blocks,
clean lines, labelled zones - no textures, no photoreal lighting. The mandatory
rule-0 caption is placed under each figure in the PDF layer.

Outputs PNGs to ../figures/.
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow, Polygon, Circle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

# ---- Brand palette --------------------------------------------------------
GREEN   = "#727C60"
DARKGRN = "#3A4030"
LIGHT   = "#E8EBE4"
MID     = "#9BA38D"
INK     = "#2D2D2D"
MIDTXT  = "#555555"
LIGHTXT = "#808080"
BRICK   = "#8B3A2F"
CONCRETE= "#BFC1BA"   # flat schematic concrete grey
CONCDK  = "#9A9C94"
WHITE   = "#FFFFFF"

FIGDIR = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(FIGDIR, exist_ok=True)

plt.rcParams["font.family"] = "DejaVu Sans"  # clean sans, reads diagrammatic


def save(fig, name):
    path = os.path.join(FIGDIR, name)
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", os.path.relpath(path))


def title(ax, text, y=1.0):
    ax.set_title(text, fontsize=11, color=INK, fontweight="bold", pad=10)


# ===========================================================================
# 1. SITE PLAN (schematic)
# ===========================================================================
def site_plan():
    # Indicative site ~ 22 m (frontage) x 37 m (depth) = 814 m2 ~ 809 m2.
    SW, SD = 22.0, 37.0
    fig, ax = plt.subplots(figsize=(6.4, 7.2))
    ax.set_aspect("equal")
    ax.axis("off")

    # Landscaped margin (lighter band) = whole site
    ax.add_patch(Rectangle((0, 0), SW, SD, fc=LIGHT, ec=GREEN, lw=2.0, zorder=1))

    # Building footprint ~16 m x 25.3 m (= 405 m2 ~ 404 m2, 50% coverage),
    # set back from the Great North Road frontage (south, y=0).
    fw, fd = 16.0, 25.3
    fx = (SW - fw) / 2.0
    fy = 7.0
    ax.add_patch(Rectangle((fx, fy), fw, fd, fc=CONCRETE, ec=INK, lw=1.6, zorder=3))

    # Colliding-facilities zone at ground (corner of footprint)
    cf_w, cf_d = fw, 6.0
    ax.add_patch(Rectangle((fx, fy), cf_w, cf_d, fc=MID, ec=INK, lw=1.0,
                           hatch="///", alpha=0.55, zorder=4))
    ax.text(fx + cf_w / 2, fy + cf_d / 2,
            "Colliding facilities\n(ground floor)", ha="center", va="center",
            fontsize=7.5, color=INK, zorder=7,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=GREEN, lw=0.6))

    ax.text(fx + fw / 2, fy + cf_d + (fd - cf_d) / 2,
            "Residential\nfootprint\n~404 m² (50% cover)", ha="center",
            va="center", fontsize=8.5, color=INK, fontweight="bold")

    # Frontage label (Great North Road along south edge)
    ax.annotate("", xy=(SW, -2.2), xytext=(0, -2.2),
                arrowprops=dict(arrowstyle="-", color=GREEN, lw=2))
    ax.text(SW / 2, -3.8, "Great North Road frontage", ha="center", va="top",
            fontsize=8.5, color=DARKGRN, fontweight="bold")

    # Pedestrian entry marker (south face of footprint, toward frontage)
    ex = fx + fw / 2
    ax.add_patch(FancyArrow(ex, 1.5, 0, 4.0, width=0.5, head_width=1.6,
                            head_length=1.6, length_includes_head=True,
                            color=BRICK, zorder=6))
    ax.text(ex + 1.4, 3.3, "Pedestrian\nentry", ha="left", va="center",
            fontsize=7, color=BRICK)

    # Landscaped setback labels
    ax.text(SW / 2, SD - 2.0, "Landscaped setback", ha="center", va="center",
            fontsize=7, color=MIDTXT, style="italic")

    # North arrow (top-right)
    nx, ny = SW + 2.0, SD - 4.0
    ax.add_patch(FancyArrow(nx, ny, 0, 4.0, width=0.25, head_width=1.2,
                            head_length=1.3, length_includes_head=True,
                            color=INK))
    ax.text(nx, ny + 5.2, "N", ha="center", va="bottom", fontsize=9,
            fontweight="bold", color=INK)

    # Indicative scale bar (bottom, clear of the frontage label)
    sbx, sby = SW - 11, -9.5
    for i in range(2):
        ax.add_patch(Rectangle((sbx + i * 5, sby), 5, 0.7,
                     fc=(INK if i % 2 == 0 else WHITE), ec=INK, lw=0.8))
    ax.text(sbx, sby - 1.2, "0", ha="center", va="top", fontsize=6.5, color=MIDTXT)
    ax.text(sbx + 10, sby - 1.2, "10 m", ha="center", va="top", fontsize=6.5, color=MIDTXT)
    ax.text(sbx + 5, sby + 1.3, "indicative scale — not to scale", ha="center",
            va="bottom", fontsize=6.5, color=LIGHTXT, style="italic")

    ax.text(0, SD + 1.5, "809 m² site · THAB zone", ha="left", va="bottom",
            fontsize=8.5, color=INK, fontweight="bold")

    ax.set_xlim(-4, SW + 6)
    ax.set_ylim(-12, SD + 4)
    title(ax, "Indicative site plan — schematic")
    save(fig, "site_plan.png")


# ===========================================================================
# 2. 3D AXONOMETRIC MASSING (schematic)
# ===========================================================================
def massing_axo():
    GR = (0.447, 0.486, 0.376)   # green
    GY = (0.607, 0.639, 0.553)   # mid green (ground floor distinct)
    EDGE = (0.12, 0.12, 0.12)
    W, D = 25.5, 16.0
    floor_h, floors = 3.2, 4

    def box(x0, y0, z0, dx, dy, dz):
        x1, y1, z1 = x0 + dx, y0 + dy, z0 + dz
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        return [[v[0], v[1], v[2], v[3]], [v[4], v[5], v[6], v[7]],
                [v[0], v[1], v[5], v[4]], [v[2], v[3], v[7], v[6]],
                [v[1], v[2], v[6], v[5]], [v[0], v[3], v[7], v[4]]]

    fig = plt.figure(figsize=(6.8, 5.8))
    ax = fig.add_subplot(111, projection="3d")
    for i in range(floors):
        col = GY if i == 0 else GR
        pc = Poly3DCollection(box(0, 0, i * floor_h, W, D, floor_h), alpha=0.95)
        pc.set_facecolor(col)
        pc.set_edgecolor(EDGE)
        pc.set_linewidth(0.7)
        ax.add_collection3d(pc)

    ax.set_xlim(0, max(W, D))
    ax.set_ylim(0, max(W, D))
    ax.set_zlim(0, floors * floor_h + 4)
    ax.set_box_aspect((W, D, floors * floor_h))
    ax.view_init(elev=22, azim=-52)
    ax.set_axis_off()
    ax.set_title("Indicative massing — 4-level walk-up (~13 m), schematic",
                 fontsize=11, color=INK, fontweight="bold", y=0.96)

    # Annotations as figure-level text (avoids 3D-axes clipping)
    fig.text(0.50, 0.13,
             "Ground floor (lighter): colliding facilities + residences   ·   "
             "Levels 1–3: residential   ·   ~13 m, no lift",
             ha="center", va="bottom", fontsize=8, color=MIDTXT)
    save(fig, "massing_axo.png")


# ===========================================================================
# 3. STACKING DIAGRAM (schematic)
# ===========================================================================
def stacking():
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    ax.set_aspect("auto")
    ax.axis("off")

    # Ground 5 units + amenity; L1-L3 7 each => 26 titles
    floors = [
        ("Ground", "Colliding facilities (laundry, lounge, office) + 5 residences", 5),
        ("Level 1", "7 residences (mix of 1-bed + dual-key)", 7),
        ("Level 2", "7 residences (mix of 1-bed + dual-key)", 7),
        ("Level 3", "7 residences (mix of 1-bed + dual-key)", 7),
    ]
    bh = 1.0
    gap = 0.18
    cum = 26
    ytop = (bh + gap) * len(floors)
    running = 26
    for i, (lvl, desc, n) in enumerate(floors):
        # draw from top (L3) down to ground; list order is ground..L3
        idx = len(floors) - 1 - i
        y = idx * (bh + gap)
        fill = MID if (lvl == "Ground") else (LIGHT if idx % 2 == 0 else "#DDE1D6")
        ax.add_patch(Rectangle((0, y), 10, bh, fc=fill, ec=GREEN, lw=1.3))
        ax.text(0.25, y + bh / 2, lvl, ha="left", va="center", fontsize=9,
                fontweight="bold", color=INK)
        ax.text(2.4, y + bh / 2, desc, ha="left", va="center", fontsize=7.8,
                color=INK)
        ax.text(9.75, y + bh / 2, f"+{n}", ha="right", va="center", fontsize=9,
                fontweight="bold", color=DARKGRN)

    ax.text(5, ytop + 0.25, "Vertical stack — 26 titles across 4 levels",
            ha="center", va="bottom", fontsize=8.5, color=MIDTXT, style="italic")
    # total
    ax.add_patch(Rectangle((0, -1.25), 10, 0.9, fc=GREEN, ec=GREEN))
    ax.text(0.25, -0.8, "Total", ha="left", va="center", fontsize=9,
            fontweight="bold", color=WHITE)
    ax.text(9.75, -0.8, "26 residences  ·  36 lettable tenancies",
            ha="right", va="center", fontsize=8.5, fontweight="bold", color=WHITE)

    ax.set_xlim(-0.3, 10.3)
    ax.set_ylim(-1.6, ytop + 1.0)
    title(ax, "Indicative stacking — schematic")
    save(fig, "stacking.png")


# ===========================================================================
# 4. 1-BED PLATE (schematic, 45 m2)
# ===========================================================================
def plate_1bed():
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    ax.set_aspect("equal")
    ax.axis("off")
    W, H = 9.0, 5.0   # 45 m2
    ax.add_patch(Rectangle((0, 0), W, H, fill=False, ec=GREEN, lw=2.4))

    # zones
    def zone(x, y, w, h, label, fc=LIGHT):
        ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=GREEN, lw=1.0))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                fontsize=8, color=INK)

    zone(0.15, 0.15, 5.2, 4.7, "Living / Kitchen")
    zone(5.45, 2.55, 3.4, 2.3, "Bedroom")
    zone(5.45, 0.15, 2.0, 2.25, "Bathroom", fc=WHITE)
    zone(7.55, 0.15, 1.3, 2.25, "Entry", fc=WHITE)

    # simple furniture hints (schematic blocks only)
    ax.add_patch(Rectangle((6.0, 3.0), 2.3, 1.3, fc=MID, ec=GREEN, lw=0.6, alpha=0.6))  # bed
    ax.add_patch(Rectangle((0.5, 0.5), 2.4, 1.0, fc=MID, ec=GREEN, lw=0.6, alpha=0.5))  # sofa

    ax.text(W / 2, H + 0.45, "45 m² — one-bedroom residence", ha="center",
            va="bottom", fontsize=9.5, fontweight="bold", color=INK)
    ax.set_xlim(-0.4, W + 0.4)
    ax.set_ylim(-0.5, H + 1.1)
    save(fig, "plate_1bed.png")


# ===========================================================================
# 5. DUAL-KEY PLATE (schematic, 45 m2)
# ===========================================================================
def plate_dualkey():
    fig, ax = plt.subplots(figsize=(6.6, 3.9))
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), 9, 5, fill=False, ec=GREEN, lw=2.4))
    # studio A | shared entry | studio B
    ax.add_patch(Rectangle((0.1, 0.1), 3.8, 4.8, fc=LIGHT, ec=GREEN, lw=1.2))
    ax.add_patch(Rectangle((4.0, 0.1), 1.0, 4.8, fc=WHITE, ec=GREEN, lw=1.2))
    ax.add_patch(Rectangle((5.1, 0.1), 3.8, 4.8, fc=LIGHT, ec=GREEN, lw=1.2))

    for x0, lbl in [(0.1, "Studio A  ~20 m²"), (5.1, "Studio B  ~20 m²")]:
        ax.add_patch(Rectangle((x0 + 0.2, 3.4), 1.4, 1.2, fc=WHITE, ec=GREEN, lw=0.8))
        ax.text(x0 + 0.9, 4.0, "Ensuite", ha="center", va="center", fontsize=6.5, color=INK)
        ax.add_patch(Rectangle((x0 + 1.8, 3.4), 1.6, 1.2, fc=WHITE, ec=GREEN, lw=0.8))
        ax.text(x0 + 2.6, 4.0, "Kitchenette", ha="center", va="center", fontsize=6.5, color=INK)
        ax.text(x0 + 1.9, 1.7, lbl, ha="center", fontsize=8.5, color=INK, fontweight="bold")
        ax.text(x0 + 1.9, 1.0, "living / sleep", ha="center", fontsize=6.5, color=MIDTXT)
        # lock/key glyph on each studio door (independently lockable)
        ky = 0.45
        kx = x0 + 1.9
        ax.add_patch(Circle((kx, ky + 0.18), 0.16, fc=BRICK, ec=BRICK))
        ax.add_patch(Rectangle((kx - 0.05, ky - 0.25), 0.10, 0.32, fc=BRICK, ec=BRICK))
        ax.text(kx + 0.35, ky, "lockable", ha="left", va="center", fontsize=6, color=BRICK)

    ax.text(4.5, 2.5, "Shared\nentry", ha="center", va="center", fontsize=6.5,
            color=INK, rotation=90)
    ax.text(4.5, 5.45, "45 m² — dual-key (2 lockable studios, one title)",
            ha="center", fontsize=9.5, fontweight="bold", color=INK)
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(-0.5, 6.1)
    save(fig, "plate_dualkey.png")


# ===========================================================================
# 6. ELEVATION (schematic)
# ===========================================================================
def elevation():
    fig, ax = plt.subplots(figsize=(7.0, 4.2))
    ax.set_aspect("equal")
    ax.axis("off")
    W, Htot = 25.5, 13.0
    floor_h = Htot / 4.0

    # overall concrete mass
    ax.add_patch(Rectangle((0, 0), W, Htot, fc=CONCRETE, ec=INK, lw=1.6))

    # ground floor distinct (amenity frontage / entry)
    ax.add_patch(Rectangle((0, 0), W, floor_h, fc=CONCDK, ec=INK, lw=1.0))

    # expressed horizontal floor slabs (thin darker lines)
    for i in range(1, 4):
        y = i * floor_h
        ax.add_patch(Rectangle((0, y - 0.12), W, 0.24, fc=INK, ec=INK, lw=0))

    # regular window module rhythm (upper 3 residential floors)
    cols = 8
    margin = 1.2
    mod_w = (W - 2 * margin) / cols
    win_w = mod_w * 0.55
    for f in range(1, 4):
        y0 = f * floor_h
        wy = y0 + floor_h * 0.30
        wh = floor_h * 0.45
        for cidx in range(cols):
            wx = margin + cidx * mod_w + (mod_w - win_w) / 2
            ax.add_patch(Rectangle((wx, wy), win_w, wh, fc="#5B6470", ec=INK, lw=0.6))

    # ground floor: entry + amenity glazing
    ax.add_patch(Rectangle((W / 2 - 1.4, 0.3), 2.8, floor_h * 0.78, fc="#3E454E",
                 ec=INK, lw=0.8))  # entry
    ax.text(W / 2, 0.15, "entry", ha="center", va="top", fontsize=6.5, color=MIDTXT)
    for cidx in [1, 5]:
        gx = margin + cidx * mod_w
        ax.add_patch(Rectangle((gx, 0.3), mod_w * 1.4, floor_h * 0.62,
                     fc="#5B6470", ec=INK, lw=0.6))

    # height dimension
    ax.annotate("", xy=(-1.2, 0), xytext=(-1.2, Htot),
                arrowprops=dict(arrowstyle="<->", color=MIDTXT, lw=1))
    ax.text(-1.8, Htot / 2, "~13 m", rotation=90, ha="right", va="center",
            fontsize=7.5, color=MIDTXT)

    ax.text(W / 2, Htot + 0.7,
            "Indicative street elevation — schematic, not to scale",
            ha="center", va="bottom", fontsize=11, fontweight="bold", color=INK)
    ax.set_xlim(-3.5, W + 1)
    ax.set_ylim(-1.5, Htot + 2.0)
    save(fig, "elevation.png")


if __name__ == "__main__":
    site_plan()
    massing_axo()
    stacking()
    plate_1bed()
    plate_dualkey()
    elevation()
    print("All figures written to", os.path.relpath(FIGDIR))
