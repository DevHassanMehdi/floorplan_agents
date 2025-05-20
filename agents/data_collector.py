from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
from spade.message import Message
import json
from config import DESIGNER_JID

class DataCollectorAgent(Agent):
    def __init__(self, jid, password, external_data=None):
        super().__init__(jid, password)
        self.external_data = external_data or []

    class SendRoomDataBehaviour(OneShotBehaviour):
        async def run(self):
            for room in self.agent.external_data:
                msg = Message(to=DESIGNER_JID)
                msg.set_metadata("performative", "inform")
                msg.set_metadata("type", "room_data")
                msg.body = json.dumps(room)
                await self.send(msg)
            done_msg = Message(to=DESIGNER_JID)
            done_msg.set_metadata("type", "done")
            await self.send(done_msg)
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.SendRoomDataBehaviour())
