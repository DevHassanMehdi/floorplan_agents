from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from collections import defaultdict
import json

class DesignerAgent(Agent):
    class RoomClusteringBehaviour(CyclicBehaviour):
        def __init__(self):
            super().__init__()
            self.rooms = {}
            self.received_done = False

        async def run(self):
            msg = await self.receive(timeout=10)
            if not msg:
                print("[DesignerAgent] No message received")
                return

            msg_type = msg.get_metadata("type")
            if msg_type == "room_data":
                room = json.loads(msg.body)
                self.rooms[room["room_id"]] = room
                print(f"[DesignerAgent] Received room: {room['room_name']}")
            elif msg_type == "done":
                print("[DesignerAgent] Received DONE signal")
                self.received_done = True

            if self.received_done and self.rooms:
                self.create_clusters()
                self.generate_layout()
                await self.agent.stop()

        def create_clusters(self):
            self.clusters = defaultdict(list)
            visited = set()

            def dfs(room_id, cluster_id):
                if room_id in visited:
                    return
                visited.add(room_id)
                self.clusters[cluster_id].append(room_id)
                for neighbor in self.rooms[room_id].get("connect_to", []):
                    if neighbor in self.rooms:
                        dfs(neighbor, cluster_id)

            cluster_id = 0
            for room_id in self.rooms:
                if room_id not in visited:
                    dfs(room_id, cluster_id)
                    cluster_id += 1

            print("\n[DesignerAgent] Room Clusters Formed:")
            for cid, room_ids in self.clusters.items():
                print(f"  Cluster {cid}: {room_ids}")

        def generate_l_shape_points(self, x, y, width, height):
            """Generate L-shaped polygon points based on width/height."""
            cut_x = width * 0.6
            cut_y = height * 0.5
            return [
                [x, y],
                [x + width, y],
                [x + width, y + cut_y],
                [x + cut_x, y + cut_y],
                [x + cut_x, y + height],
                [x, y + height]
            ]

        def generate_c_shape_points(self, x, y, width, height):
            """Generate C-shaped polygon points."""
            cut_w = width * 0.3
            cut_h = height * 0.4
            return [
                [x, y],
                [x + width, y],
                [x + width, y + height],
                [x + width - cut_w, y + height],
                [x + width - cut_w, y + cut_h],
                [x, y + cut_h]
            ]

        def generate_layout(self):
            layout = {"rooms": []}
            spacing_x = 2.0
            spacing_y = 2.0
            cluster_margin = 4.0

            global_x = 0
            global_y = 0

            for cluster_id, room_ids in self.clusters.items():
                max_height = 0
                x_offset = global_x
                y_offset = global_y
                col = 0

                for room_id in room_ids:
                    room = self.rooms[room_id]
                    width = round(room["min_width"] / 1000, 2)
                    height = round(room["desired_area"] / width, 2)

                    x = x_offset
                    y = y_offset

                    # Use C-L-shape for large or special rooms
                    room_name_lower = room["room_name"].lower()
                    if room["desired_area"] > 20.0 or "lounge" in room_name_lower or "living" in room_name_lower:
                        points = self.generate_c_shape_points(x, y, width, height)
                    elif room["desired_area"] > 15.0 or "kitchen" in room_name_lower:
                        points = self.generate_l_shape_points(x, y, width, height)
                    else:
                        points = [
                            [x, y],
                            [x + width, y],
                            [x + width, y + height],
                            [x, y + height]
                        ]

                    layout["rooms"].append({
                        "id": room_id,
                        "name": room["room_name"],
                        "points": points,
                        "area": room["desired_area"],
                        "public_access": room["public_access"],
                        "connected_to": room.get("connect_to", [])
                    })

                    max_height = max(max_height, y + height)

                    col += 1
                    if col == 2:
                        col = 0
                        x_offset = global_x
                        y_offset += height + spacing_y
                    else:
                        x_offset += width + spacing_x

                global_y = max_height + cluster_margin

            self.evaluate_layout(layout)

            with open("floorplan_layout.json", "w") as f:
                json.dump(layout, f, indent=4)
            print("[DesignerAgent] Layout with exported to floorplan_layout.json")

        def evaluate_layout(self, layout):
            print("\n[DesignerAgent] Evaluating layout...")

            all_points = [pt for room in layout["rooms"] for pt in room["points"]]
            min_x = min(pt[0] for pt in all_points)
            max_x = max(pt[0] for pt in all_points)
            min_y = min(pt[1] for pt in all_points)
            max_y = max(pt[1] for pt in all_points)

            total_area = (max_x - min_x) * (max_y - min_y)
            room_count = len(layout["rooms"])
            cluster_count = len(self.clusters)

            l_shaped = sum(
                1 for r in layout["rooms"] if len(r["points"]) == 6 and not r["name"].lower().startswith("hallway"))
            compact_rooms = room_count - l_shaped

            print(f"📏 Total layout bounding area: {total_area:.2f} m²")
            print(f"🏘️ Total rooms: {room_count}")
            print(f"🔗 Clusters (connected groups): {cluster_count}")
            print(f"🧩 L/C-Shaped Rooms: {l_shaped}")
            print(f"⬛ Rectangular Rooms: {compact_rooms}")

    async def setup(self):
        print("[DesignerAgent] Starting...")
        self.add_behaviour(self.RoomClusteringBehaviour())
