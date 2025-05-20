# agents/decision_maker.py

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json


class DecisionMakerAgent(Agent):
    class CollectScoresBehaviour(CyclicBehaviour):
        def __init__(self):
            super().__init__()
            self.scores = {}
            self.expected_reviewers = [
                "reviewer_agent@xmpp.jp"  # add more if needed
            ]

        async def run(self):
            msg = await self.receive(timeout=15)
            if msg and msg.get_metadata("type") == "review_score":
                data = json.loads(msg.body)
                reviewer = str(msg.sender).split("/")[0]
                score = data["score"]
                print(f"[DecisionMaker] Received score from {reviewer}: {score}")

                self.scores[reviewer] = score

            if len(self.scores) == len(self.expected_reviewers):
                final_score = sum(self.scores.values()) / len(self.scores)
                print(f"\n[DecisionMaker] ✅ Final aggregated score: {round(final_score, 4)}")

                # Save to file for optional UI or logging
                with open("final_score.json", "w") as f:
                    json.dump(self.scores, f, indent=2)

                await self.agent.stop()

    async def setup(self):
        print("[DecisionMaker] Starting...")
        self.add_behaviour(self.CollectScoresBehaviour())
