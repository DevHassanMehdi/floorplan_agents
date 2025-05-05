# main.py

import asyncio
from agents.data_collector import DataCollectorAgent
from agents.designer import DesignerAgent
from config import DATA_COLLECTOR_JID, DATA_COLLECTOR_PASS, DESIGNER_JID, DESIGNER_PASS

async def main():
    designer = DesignerAgent(DESIGNER_JID, DESIGNER_PASS)
    await designer.start()
    print("[Main] Designer Agent started")

    collector = DataCollectorAgent(DATA_COLLECTOR_JID, DATA_COLLECTOR_PASS)
    await collector.start()
    print("[Main] Data Collector Agent started")

    await asyncio.sleep(15)
    await collector.stop()
    await designer.stop()
    print("[Main] All agents stopped")

if __name__ == "__main__":
    asyncio.run(main())
