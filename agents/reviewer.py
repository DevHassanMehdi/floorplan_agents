# agents/reviewer.py
import asyncio
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour
import json
import time

class ReviewerAgent(Agent):
    class ReviewBehaviour(OneShotBehaviour):
        async def run(self):
            print("[ReviewerAgent] Waiting for floorplan to be generated...")
            # Wait until floorplan JSON is available
            while True:
                try:
                    with open("floorplan_layout.json", "r") as f:
                        layout = json.load(f)
                    with open("room_specs.json", "r") as f:
                        specs = {r["room_id"]: r for r in json.load(f)}
                    break
                except FileNotFoundError:
                    await asyncio.sleep(1)

            print("[ReviewerAgent] Loaded floorplan and specs.")

            total_score = 0
            for room in layout["rooms"]:
                rid = room["id"]
                actual_area = room["width"] * room["height"]
                desired_area = specs[rid]["desired_area"]
                accuracy = 1 - abs(actual_area - desired_area) / desired_area
                print(f"  - {room['name']}: actual={actual_area:.2f}, desired={desired_area:.2f}, score={accuracy:.2f}")
                total_score += accuracy

            avg_score = total_score / len(layout["rooms"])
            print(f"\n[ReviewerAgent] Final Score: {avg_score:.2f}")
            if avg_score >= 0.8:
                print("[ReviewerAgent] ✅ Design Approved")
            else:
                print("[ReviewerAgent] ❌ Design Rejected")

            await self.agent.stop()

    async def setup(self):
        print("[ReviewerAgent] Starting...")
        self.add_behaviour(self.ReviewBehaviour())
