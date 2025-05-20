import json
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_svg import FigureCanvasSVG
import matplotlib.lines as mlines

def get_color(name):
    name = name.lower()
    color_map = {
        "foyer": "#E8E8E8",
        "hallway": "#D3D3D3",
        "bedroom": "#CAB8FF",
        "guest": "#D8BFD8",
        "kitchen": "#FFC1B6",
        "dining": "#FFFACD",
        "closet": "#F5F5DC",
        "bath": "#ADD8E6",
        "living": "#A9A9A9",
        "default": "#C0C0C0"
    }
    for key in color_map:
        if key in name:
            return color_map[key]
    return color_map["default"]

def save_floorplan_svg():
    try:
        with open("floorplan_layout.json", "r") as f:
            layout = json.load(f)
    except FileNotFoundError:
        print("[Visualizer] ❌ floorplan_layout.json not found.")
        return

    fig, ax = plt.subplots(figsize=(10, 10))
    rooms = layout.get("rooms", [])
    rendered_doors = set()
    legend_labels = {}

    for room in rooms:
        x, y, w, h = room["x"], room["y"], room["width"], room["height"]
        color = get_color(room["name"])
        ax.add_patch(Rectangle((x, y), w, h, facecolor=color, edgecolor='black', linewidth=2))
        ax.text(x + w/2, y + h/2, room["name"], ha="center", va="center", fontsize=9)
        legend_labels[room["name"]] = color

        for door in room.get("doors", []):
            other_id = door["to"]
            pair = tuple(sorted([room["id"], other_id]))
            if pair in rendered_doors:
                continue
            rendered_doors.add(pair)

            side = door["side"]
            if side == "top":
                dx, dy = x + w/2 - 0.25, y + h
                ax.plot([dx, dx + 0.5], [dy, dy], color='green', linewidth=4)
            elif side == "bottom":
                dx, dy = x + w/2 - 0.25, y
                ax.plot([dx, dx + 0.5], [dy, dy], color='green', linewidth=4)
            elif side == "left":
                dx, dy = x, y + h/2 - 0.25
                ax.plot([dx, dx], [dy, dy + 0.5], color='green', linewidth=4)
            elif side == "right":
                dx, dy = x + w, y + h/2 - 0.25
                ax.plot([dx, dx], [dy, dy + 0.5], color='green', linewidth=4)

    if rooms:
        all_x = [r["x"] for r in rooms] + [r["x"] + r["width"] for r in rooms]
        all_y = [r["y"] for r in rooms] + [r["y"] + r["height"] for r in rooms]
        ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
        ax.set_ylim(min(all_y) - 1, max(all_y) + 1)

    ax.set_aspect("equal")
    ax.axis("off")
    plt.tight_layout()

    with open("static/floorplan.svg", "w") as svg_file:
        FigureCanvasSVG(fig).print_svg(svg_file)

    plt.close(fig)
