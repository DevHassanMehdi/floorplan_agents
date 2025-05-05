# visualizer.py

import json
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

# Room color mapping
ROOM_COLOR_MAP = {
    "living room": "lightblue",
    "kitchen": "coral",
    "bedroom": "plum",
    "bathroom": "lightgreen",
    "toilet": "lightsalmon",
    "hallway": "gray",
    "lounge": "skyblue",
    "dining": "khaki",
    "study": "orchid",
    "storage": "beige",
    "garage": "lightsteelblue",
    "utility": "tan",
    "balcony": "lightcyan",
    "default": "lightgray"
}

def get_room_color(name):
    name = name.lower()
    if "hallway" in name:
        return "lightgray"
    for key in ROOM_COLOR_MAP:
        if key in name:
            return ROOM_COLOR_MAP[key]
    return ROOM_COLOR_MAP["default"]

def add_spacing_to_room(points, spacing):
    """Expand each room outward from top-left to prevent overlaps."""
    return [[x + spacing, y + spacing] for x, y in points]

def visualize_layout(json_file, padding=0.5, spacing_between_rooms=1.0, show_legend=True):
    with open(json_file, "r") as f:
        layout = json.load(f)

    fig, ax = plt.subplots(figsize=(10, 8))

    used_colors = {}
    for room in layout["rooms"]:
        original_points = room["points"]
        # Apply spacing and padding to prevent overlaps
        shifted_points = add_spacing_to_room(original_points, spacing_between_rooms)

        color = get_room_color(room["name"])
        used_colors[room["name"]] = color

        poly = Polygon(shifted_points, closed=True, edgecolor="black", facecolor=color, linewidth=1.5)
        ax.add_patch(poly)

        # Center label
        cx = sum(p[0] for p in shifted_points) / len(shifted_points)
        cy = sum(p[1] for p in shifted_points) / len(shifted_points)
        ax.text(cx, cy, room["name"], ha="center", va="center", fontsize=10, weight="bold")

    ax.set_aspect("equal")
    ax.set_title("Generated Floor Plan", fontsize=14)
    ax.autoscale_view()
    ax.grid(True, linestyle='--', linewidth=0.5)

    # Add legend if needed
    if show_legend:
        handles = [
            plt.Line2D([0], [0], color=color, lw=6, label=room_name)
            for room_name, color in used_colors.items()
        ]
        ax.legend(handles=handles, loc="upper right", fontsize=9, frameon=True)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    visualize_layout("floorplan_layout.json")
