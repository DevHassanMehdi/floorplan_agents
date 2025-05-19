# agents/visualizer.py

import json
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
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

def render_layout():
    # ✅ Now the layout is loaded only when this function is called
    try:
        with open("floorplan_layout.json", "r") as f:
            layout = json.load(f)
    except FileNotFoundError:
        print("[Visualizer] ❌ floorplan_layout.json not found. Has the DesignerAgent run yet?")
        return

    fig, ax = plt.subplots(figsize=(10, 10))
    legend_labels = {}
    rendered_doors = set()

    for room in layout["rooms"]:
        x, y, w, h = room["x"], room["y"], room["width"], room["height"]
        color = get_color(room["name"])
        rect = Rectangle((x, y), w, h, facecolor=color, edgecolor='black', linewidth=2.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, room["name"], ha="center", va="center", fontsize=9, weight="bold")
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

    all_x = [r["x"] for r in layout["rooms"]] + [r["x"] + r["width"] for r in layout["rooms"]]
    all_y = [r["y"] for r in layout["rooms"]] + [r["y"] + r["height"] for r in layout["rooms"]]
    ax.set_xlim(min(all_x) - 1, max(all_x) + 1)
    ax.set_ylim(min(all_y) - 1, max(all_y) + 1)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("2D Floor Plan with Clean Door Mapping")

    handles = [mlines.Line2D([], [], color=color, marker='s', linestyle='None',
                             markersize=10, label=name) for name, color in legend_labels.items()]
    ax.legend(handles=handles, loc="upper right")

    plt.tight_layout()
    plt.savefig("floorplan_simplified.png", dpi=150)
    plt.show()
