# agents/data_collector.py

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
import json
from config import DESIGNER_JID

# Here are a couple of example floor plan requirements data. Uncomment the one that you want to use
# Example 1: Compact Family Home

ROOM_DATA = [
    {
        "room_name": "Foyer",
        "room_id": "R1",
        "desired_area": 4.0,
        "min_width": 1500,
        "connect_to": ["R2"],
        "connected_to_hallway": True,
        "public_access": True,
        "orientation": "must-north",
        "open_sides": "preferred-1",
        "hallway_width": 1200
    },
    {
        "room_name": "Hallway",
        "room_id": "R2",
        "desired_area": 8.0,  # will be optimized to minimize area
        "min_width": 1200,
        "connect_to": ["R1", "R3", "R4", "R5", "R6"],
        "connected_to_hallway": False,
        "public_access": False,
        "orientation": "any",
        "open_sides": "minimum-0",
        "hallway_width": 1200
    },
    {
        "room_name": "Living Room",
        "room_id": "R3",
        "desired_area": 20.0,
        "min_width": 4000,
        "connect_to": ["R2", "R4"],
        "connected_to_hallway": True,
        "public_access": True,
        "orientation": "preferred-south",
        "open_sides": "preferred-2",
        "hallway_width": 1200
    },
    {
        "room_name": "Kitchen",
        "room_id": "R4",
        "desired_area": 12.0,
        "min_width": 2500,
        "connect_to": ["R2", "R3"],
        "connected_to_hallway": True,
        "public_access": False,
        "orientation": "preferred-east",
        "open_sides": "preferred-1",
        "hallway_width": 1200
    },
    {
        "room_name": "Bedroom",
        "room_id": "R5",
        "desired_area": 14.0,
        "min_width": 2800,
        "connect_to": ["R2", "R6"],
        "connected_to_hallway": True,
        "public_access": False,
        "orientation": "preferred-west",
        "open_sides": "exact-1",
        "hallway_width": 1200
    },
    {
        "room_name": "Bathroom",
        "room_id": "R6",
        "desired_area": 5.0,
        "min_width": 1800,
        "connect_to": ["R2", "R5"],
        "connected_to_hallway": True,
        "public_access": True,
        "orientation": "any",
        "open_sides": "minimum-0",
        "hallway_width": 1200
    }
]

# Example 2: Guest Suite with Walk-In Closet Cluster
# ROOM_DATA = [
#     {
#         "room_name": "Foyer",
#         "room_id": "R1",
#         "desired_area": 5.0,
#         "min_width": 1500,
#         "connect_to": ["R2"],
#         "connected_to_hallway": True,
#         "public_access": True,
#         "orientation": "must-north",
#         "open_sides": "exact-1",
#         "hallway_width": 1200
#     },
#     {
#         "room_name": "Hallway",
#         "room_id": "R2",
#         "desired_area": 9.0,
#         "min_width": 1200,
#         "connect_to": ["R1", "R3", "R4", "R5", "R6"],
#         "connected_to_hallway": False,
#         "public_access": False,
#         "orientation": "any",
#         "open_sides": "minimum-0",
#         "hallway_width": 1200
#     },
#     {
#         "room_name": "Guest Bedroom",
#         "room_id": "R3",
#         "desired_area": 16.0,
#         "min_width": 3000,
#         "connect_to": ["R2", "R4"],
#         "connected_to_hallway": True,
#         "public_access": False,
#         "orientation": "preferred-south",
#         "open_sides": "preferred-2",
#         "hallway_width": 1200
#     },
#     {
#         "room_name": "Walk-in Closet",
#         "room_id": "R4",
#         "desired_area": 5.0,
#         "min_width": 1800,
#         "connect_to": ["R3"],
#         "connected_to_hallway": False,
#         "public_access": False,
#         "orientation": "any",
#         "open_sides": "preferred-0",
#         "hallway_width": 1200
#     },
#     {
#         "room_name": "Dining Room",
#         "room_id": "R5",
#         "desired_area": 18.0,
#         "min_width": 3500,
#         "connect_to": ["R2", "R6"],
#         "connected_to_hallway": True,
#         "public_access": True,
#         "orientation": "preferred-west",
#         "open_sides": "preferred-1",
#         "hallway_width": 1200
#     },
#     {
#         "room_name": "Kitchen",
#         "room_id": "R6",
#         "desired_area": 10.0,
#         "min_width": 2500,
#         "connect_to": ["R2", "R5"],
#         "connected_to_hallway": True,
#         "public_access": False,
#         "orientation": "preferred-east",
#         "open_sides": "preferred-1",
#         "hallway_width": 1200
#     }
# ]
#

class DataCollectorAgent(Agent):
    class SendRoomDataBehaviour(OneShotBehaviour):
        async def run(self):
            for room in ROOM_DATA:
                msg = Message(to=DESIGNER_JID)
                msg.set_metadata("performative", "inform")
                msg.set_metadata("type", "room_data")
                msg.body = json.dumps(room)
                await self.send(msg)
                print(f"[DataCollectorAgent] Sent room data: {room['room_name']}")

            # Signal done
            done_msg = Message(to=DESIGNER_JID)
            done_msg.set_metadata("performative", "inform")
            done_msg.set_metadata("type", "done")
            await self.send(done_msg)
            print("[DataCollectorAgent] Sent DONE signal")

            await self.agent.stop()

    async def setup(self):
        print("[DataCollectorAgent] Starting...")
        b = self.SendRoomDataBehaviour()
        self.add_behaviour(b)
