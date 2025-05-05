# agents/data_collector.py

from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
import json
from config import DESIGNER_JID

ROOM_DATA = [
    {
        "room_name": "Living Room",
        "room_id": "R1",
        "desired_area": 20.0,
        "min_width": 4000,
        "connect_to": ["R2", "R3", "R7"],
        "public_access": True,
        "hallway_width": 1200
    },
    {
        "room_name": "Kitchen",
        "room_id": "R2",
        "desired_area": 12.0,
        "min_width": 2500,
        "connect_to": ["R1"],
        "public_access": False,
        "hallway_width": 1200
    },
    {
        "room_name": "Bedroom 1",
        "room_id": "R3",
        "desired_area": 15.0,
        "min_width": 3000,
        "connect_to": ["R1", "R4"],
        "public_access": False,
        "hallway_width": 1200
    },
    {
        "room_name": "Bathroom",
        "room_id": "R4",
        "desired_area": 6.0,
        "min_width": 1800,
        "connect_to": ["R3", "R7"],
        "public_access": True,
        "hallway_width": 1200
    },
    {
        "room_name": "Bedroom 2",
        "room_id": "R5",
        "desired_area": 14.0,
        "min_width": 2800,
        "connect_to": ["R7"],
        "public_access": False,
        "hallway_width": 1200
    },
    {
        "room_name": "Toilet",
        "room_id": "R6",
        "desired_area": 3.0,
        "min_width": 1500,
        "connect_to": ["R7"],
        "public_access": True,
        "hallway_width": 1200
    },
    {
        "room_name": "Hallway",
        "room_id": "R7",
        "desired_area": 10.0,
        "min_width": 1200,
        "connect_to": ["R1", "R4", "R5", "R6"],
        "public_access": False,
        "hallway_width": 1200
    }
]

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
