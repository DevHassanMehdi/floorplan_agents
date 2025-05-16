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
                self.generate_grid_based_layout()
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

        def generate_grid_based_layout(self):
            GRID_SIZE = 50
            CELL_SIZE = 1.0
            grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
            layout = {"rooms": [], "doors": []}
            placed = {}
            edges = {}

            def is_free(gx, gy, w, h):
                if gx < 0 or gy < 0 or gx + w > GRID_SIZE or gy + h > GRID_SIZE:
                    return False
                for i in range(h):
                    for j in range(w):
                        if grid[gy + i][gx + j] is not None:
                            return False
                return True

            def place_room(room_id, gx, gy, w, h):
                for i in range(h):
                    for j in range(w):
                        grid[gy + i][gx + j] = room_id
                placed[room_id] = (gx, gy, w, h)
                edges[room_id] = [
                    ((gx, gy), (gx + w, gy)),  # top
                    ((gx + w, gy), (gx + w, gy + h)),  # right
                    ((gx + w, gy + h), (gx, gy + h)),  # bottom
                    ((gx, gy + h), (gx, gy))  # left
                ]

            def find_adjacent_spot(conn_room_id, w, h):
                gx, gy, gw, gh = placed[conn_room_id]
                candidates = [
                    (gx + gw, gy),
                    (gx - w, gy),
                    (gx, gy + gh),
                    (gx, gy - h)
                ]
                for nx, ny in candidates:
                    if is_free(nx, ny, w, h):
                        return nx, ny
                return None

            center_x = GRID_SIZE // 2
            center_y = GRID_SIZE // 2
            for room_id, room in self.rooms.items():
                if room["room_name"].lower() == "hallway":
                    width = max(2, round(room["min_width"] / 1000))
                    height = max(2, round(room["desired_area"] / width))
                    place_room(room_id, center_x, center_y, width, height)
                    break

            for room_id, room in self.rooms.items():
                if room_id in placed:
                    continue
                for conn in room.get("connect_to", []):
                    if conn in placed:
                        width = max(2, round(room["min_width"] / 1000))
                        height = max(2, round(room["desired_area"] / width))
                        spot = find_adjacent_spot(conn, width, height)
                        if spot:
                            nx, ny = spot
                            place_room(room_id, nx, ny, width, height)
                            layout["doors"].append({"from": room_id, "to": conn})
                            break

            for room_id, (gx, gy, w, h) in placed.items():
                x = gx * CELL_SIZE
                y = gy * CELL_SIZE
                points = [
                    [x, y],
                    [x + w * CELL_SIZE, y],
                    [x + w * CELL_SIZE, y + h * CELL_SIZE],
                    [x, y + h * CELL_SIZE]
                ]
                room = self.rooms[room_id]
                layout["rooms"].append({
                    "id": room_id,
                    "name": room["room_name"],
                    "points": points,
                    "area": room["desired_area"],
                    "public_access": room["public_access"],
                    "connected_to": room.get("connect_to", []),
                    "orientation": room.get("orientation", "any"),
                    "open_sides": room.get("open_sides", "preferred-1")
                })

            with open("floorplan_layout.json", "w") as f:
                json.dump(layout, f, indent=4)
            print("[DesignerAgent] Final layout with door edge awareness generated.")

    async def setup(self):
        print("[DesignerAgent] Starting...")
        self.add_behaviour(self.RoomClusteringBehaviour())
