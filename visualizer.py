import json
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Arc
import matplotlib.lines as mlines

# Load layout
with open("floorplan_layout.json", "r") as f:
    layout = json.load(f)

rooms = {room["id"]: room for room in layout["rooms"]}
doors = layout.get("doors", [])

# Color map
color_map = {
    "foyer": "#E8E8E8",
    "hallway": "#D3D3D3",
    "bedroom": "#CAB8FF",
    "guest": "#D8BFD8",
    "kitchen": "#FFC1B6",
    "dining": "#FFFACD",
    "closet": "#F5F5DC",
    "bath": "#ADD8E6",
    "default": "#C0C0C0"
}

def get_color(name):
    name = name.lower()
    for key in color_map:
        if key in name:
            return color_map[key]
    return color_map["default"]

fig, ax = plt.subplots(figsize=(10, 10))
legend_labels = {}
centers = {}

# Draw rooms
for room in layout["rooms"]:
    color = get_color(room["name"])
    points = room["points"]
    poly = Polygon(points, closed=True, facecolor=color, edgecolor="black", linewidth=2.5)
    ax.add_patch(poly)
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    centers[room["id"]] = (cx, cy)
    ax.text(cx, cy, room["name"], ha="center", va="center", fontsize=9, weight="bold")
    legend_labels[room["name"]] = color

# Draw door arcs between rooms
for door in doors:
    r1, r2 = rooms[door["from"]], rooms[door["to"]]
    c1x, c1y = centers[r1["id"]]
    c2x, c2y = centers[r2["id"]]
    mx = (c1x + c2x) / 2
    my = (c1y + c2y) / 2
    dx = c2x - c1x
    dy = c2y - c1y
    angle = 0
    if abs(dx) > abs(dy):
        angle = 0 if dx > 0 else 180
    else:
        angle = 90 if dy > 0 else 270
    ax.add_patch(Arc((mx, my), 0.6, 0.6, angle=angle, theta1=0, theta2=180, color='red', linewidth=1.5))

# Fix axis limits to ensure visibility
all_x = [p[0] for room in layout["rooms"] for p in room["points"]]
all_y = [p[1] for room in layout["rooms"] for p in room["points"]]
ax.set_xlim(min(all_x) - 2, max(all_x) + 2)
ax.set_ylim(min(all_y) - 2, max(all_y) + 2)

# Final formatting
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("2D Floor Plan View with Walls and Doorways")

# Add legend
handles = [mlines.Line2D([], [], color=color, marker='s', linestyle='None',
                         markersize=10, label=name) for name, color in legend_labels.items()]
ax.legend(handles=handles, loc="upper right")

plt.tight_layout()
plt.savefig("floorplan_topview.png", dpi=150)
plt.show()
