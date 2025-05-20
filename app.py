from flask import Flask, render_template, request, redirect, url_for
import threading, asyncio, json, builtins
from agents.data_collector import DataCollectorAgent
from agents.designer import DesignerAgent
from agents.reviewer import ReviewerAgent
from agents.decision_maker import DecisionMakerAgent
from agents.visualizer import save_floorplan_svg
from config import *

# Global log state
logs = []
pipeline_complete = False

# Override built-in print to capture logs in memory
original_print = builtins.print


def custom_print(*args, **kwargs):
    message = " ".join(str(a) for a in args)
    logs.append(message)
    original_print(*args, **kwargs)


builtins.print = custom_print

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    global logs, pipeline_complete
    logs.clear()
    pipeline_complete = False

    try:
        room_data = json.loads(request.form["room_data"])
        with open("room_specs.json", "w") as f:
            json.dump(room_data, f, indent=2)
    except json.JSONDecodeError:
        logs.append("[Error] Invalid room data JSON")
        return redirect(url_for("progress"))

    thread = threading.Thread(target=run_pipeline, args=(room_data,))
    thread.start()
    return redirect(url_for("progress"))


@app.route("/progress")
def progress():
    return render_template("progress.html", logs=logs, done=pipeline_complete)


def run_pipeline(room_data):
    global pipeline_complete
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def task():
        print("🚀 Starting DesignerAgent")
        designer = DesignerAgent(DESIGNER_JID, DESIGNER_PASS)
        await designer.start()
        await asyncio.sleep(2)  # Let DesignerAgent prepare

        print("📦 Starting DataCollectorAgent")
        collector = DataCollectorAgent(DATA_COLLECTOR_JID, DATA_COLLECTOR_PASS, external_data=room_data)
        await collector.start()
        await asyncio.sleep(10)

        print("🔍 Starting ReviewerAgent")
        reviewer = ReviewerAgent(REVIEWER_JID, REVIEWER_PASS)
        await reviewer.start()
        await asyncio.sleep(5)
        await reviewer.stop()

        print("🧠 Starting DecisionMakerAgent")
        decision = DecisionMakerAgent(DECISION_MAKER_JID, DECISION_MAKER_PASS)
        await decision.start()
        await asyncio.sleep(5)
        await decision.stop()

        print("🖼️ Generating SVG Layout")
        save_floorplan_svg()
        print("✅ Pipeline Complete")

        global pipeline_complete
        pipeline_complete = True

    loop.run_until_complete(task())
