# main.py

import asyncio
import json
from agents.data_collector import DataCollectorAgent, ROOM_DATA
from agents.designer import DesignerAgent
from agents.reviewer import ReviewerAgent
from agents.decision_maker import DecisionMakerAgent
from agents.visualizer import render_layout
from config import (
    DATA_COLLECTOR_JID, DATA_COLLECTOR_PASS,
    DESIGNER_JID, DESIGNER_PASS,
    REVIEWER_JID, REVIEWER_PASS,
    DECISION_MAKER_JID, DECISION_MAKER_PASS
)

async def main():
    with open("room_specs.json", "w") as f:
        json.dump(ROOM_DATA, f, indent=2)
    print("[Main] Saved room_specs.json")

    # ✅ 1. Start Designer FIRST
    designer = DesignerAgent(DESIGNER_JID, DESIGNER_PASS)
    await designer.start()
    print("[Main] Designer Agent started")

    await asyncio.sleep(2)  # give designer a moment to boot up

    # ✅ 2. Start Data Collector
    collector = DataCollectorAgent(DATA_COLLECTOR_JID, DATA_COLLECTOR_PASS)
    await collector.start()
    print("[Main] Data Collector Agent started")

    await asyncio.sleep(10)
    await collector.stop()
    await designer.stop()
    print("[Main] Data Collector and Designer stopped")

    # ✅ 3. Start Reviewer
    reviewer = ReviewerAgent(REVIEWER_JID, REVIEWER_PASS)
    await reviewer.start()
    print("[Main] Reviewer Agent started")
    await asyncio.sleep(5)
    await reviewer.stop()
    print("[Main] Reviewer Agent stopped")

    # ✅ 4. Start Decision Maker
    decision_maker = DecisionMakerAgent(DECISION_MAKER_JID, DECISION_MAKER_PASS)
    await decision_maker.start()
    print("[Main] Decision Maker Agent started")
    await asyncio.sleep(5)
    await decision_maker.stop()
    print("[Main] Decision Maker Agent stopped")

    # ✅ 5. Visualize
    print("[Main] Rendering final layout...")
    render_layout()
    print("[Main] Visualization complete ✅")

if __name__ == "__main__":
    asyncio.run(main())
