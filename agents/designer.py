from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json

class DesignerAgent(Agent):
    class RoomLayoutBehaviour(CyclicBehaviour):
        def __init__(self):
            super().__init__()
            self.rooms = {}
            self.done = False

        async def run(self):
            msg = await self.receive(timeout=10)
            if not msg:
                print("[DesignerAgent] No message received")
                return

            msg_type = msg.get_metadata("type")
            if msg_type == "room_data":
                room = json.loads(msg.body)
                self.rooms[room["room_id"]] = room
                print(f"[DesignerAgent] Received: {room['room_name']}")
            elif msg_type == "done":
                self.done = True

            if self.done and self.rooms:
                self.generate_layout()
                await self.agent.stop()

        def generate_layout(self):
            placed = {}
            layout = {"rooms": []}
            spacing = 0

            def place_room(room_id, room, x, y, width, height):
                placed[room_id] = {
                    "id": room_id,
                    "name": room["room_name"],
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                    "doors": []
                }

            def get_room_dimensions(room):
                w = max(2, round(room["min_width"] / 1000))
                h = max(2, round(room["desired_area"] / w))
                return w, h

            # Place hallway first at center
            origin_x, origin_y = 20, 20
            for rid, room in self.rooms.items():
                if room["room_name"].lower() == "hallway":
                    w, h = get_room_dimensions(room)
                    place_room(rid, room, origin_x, origin_y, w, h)
                    break

            # Place all unplaced rooms based on placed ones
            unplaced = [r for r in self.rooms if r not in placed]

            while unplaced:
                placed_this_round = False

                for rid in list(unplaced):  # clone list to modify unplaced safely
                    room = self.rooms[rid]
                    for conn in room.get("connect_to", []):
                        if conn in placed:
                            # get dimensions of new room
                            rw = max(2, round(room["min_width"] / 1000))
                            rh = max(2, round(room["desired_area"] / rw))

                            # connected room info
                            ref = placed[conn]
                            cx, cy, cw, ch = ref["x"], ref["y"], ref["width"], ref["height"]

                            # Try placing on all 4 sides
                            candidates = {
                                "top":    (cx, cy + ch + spacing, "bottom", "top"),
                                "bottom": (cx, cy - rh - spacing, "top", "bottom"),
                                "right":  (cx + cw + spacing, cy, "left", "right"),
                                "left":   (cx - rw - spacing, cy, "right", "left"),
                            }

                            for side, (nx, ny, this_side, other_side) in candidates.items():
                                # check for overlap with placed rooms
                                overlap = any(
                                    abs(nx - p["x"]) < p["width"] and
                                    abs(ny - p["y"]) < p["height"]
                                    for pid, p in placed.items()
                                )
                                if not overlap:
                                    place_room(rid, room, nx, ny, rw, rh)
                                    placed[rid]["doors"].append({"side": this_side, "to": conn})
                                    placed[conn]["doors"].append({"side": other_side, "to": rid})
                                    unplaced.remove(rid)
                                    placed_this_round = True
                                    break
                            break  # stop after first valid placement attempt

                if not placed_this_round:
                    print(f"[DesignerAgent] Could not place these rooms: {unplaced}")
                    break


            layout["rooms"] = list(placed.values())

            with open("floorplan_layout.json", "w") as f:
                json.dump(layout, f, indent=4)
            print("[DesignerAgent] Wrote aligned layout with correct door placement.")

    async def setup(self):
        print("[DesignerAgent] Starting...")
        self.add_behaviour(self.RoomLayoutBehaviour())
