# agents/designer.py

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

        def generate_layout(self):
            layout = {"rooms": []}
            placed = {}
            spacing_x = 2.0  # meters between rooms horizontally
            spacing_y = 2.0  # meters between rooms vertically
            max_columns = 2  # layout rooms in N columns

            x_offset = 0
            y_offset = 0
            col_counter = 0

            for cluster_id, room_ids in self.clusters.items():
                for room_id in room_ids:
                    room = self.rooms[room_id]
                    width = round(room["min_width"] / 1000, 2)
                    height = round(room["desired_area"] / width, 2)

                    # Assign room position
                    x = x_offset
                    y = y_offset

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

                    placed[room_id] = {"points": points, "name": room["room_name"]}

                    # Update offsets
                    col_counter += 1
                    if col_counter >= max_columns:
                        col_counter = 0
                        x_offset = 0
                        y_offset += height + spacing_y
                    else:
                        x_offset += width + spacing_x

            with open("floorplan_layout.json", "w") as f:
                json.dump(layout, f, indent=4)
            print("[DesignerAgent] Layout exported to floorplan_layout.json")

    async def setup(self):
        print("[DesignerAgent] Starting...")
        self.add_behaviour(self.RoomClusteringBehaviour())
