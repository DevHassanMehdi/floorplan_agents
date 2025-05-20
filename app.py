# app.py

from flask import Flask, render_template, request, redirect, url_for
import threading, asyncio, json
from agents.data_collector import DataCollectorAgent
from agents.designer import DesignerAgent
from agents.reviewer import ReviewerAgent
from agents.decision_maker import DecisionMakerAgent
from agents.visualizer import save_floorplan_svg
from config import *

app = Flask(__name__)
logs = []
pipeline_complete = False

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

def log(msg):
    print(msg)
    logs.append(msg)

def run_pipeline(room_data):
    global pipeline_complete
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def task():
        log("🚀 Starting DesignerAgent")
        designer = DesignerAgent(DESIGNER_JID, DESIGNER_PASS)
        await designer.start()
        await asyncio.sleep(2)  # let designer register and prepare

        log("📦 Starting DataCollectorAgent")
        collector = DataCollectorAgent(DATA_COLLECTOR_JID, DATA_COLLECTOR_PASS, external_data=room_data)
        await collector.start()
        await asyncio.sleep(10)  # give time for designer to receive messages


        log("🔍 Starting ReviewerAgent")
        reviewer = ReviewerAgent(REVIEWER_JID, REVIEWER_PASS)
        await reviewer.start()
        await asyncio.sleep(5)
        await reviewer.stop()

        log("🧠 Starting DecisionMakerAgent")
        decision = DecisionMakerAgent(DECISION_MAKER_JID, DECISION_MAKER_PASS)
        await decision.start()
        await asyncio.sleep(5)
        await decision.stop()

        log("🖼️ Generating SVG Layout")
        save_floorplan_svg()
        log("✅ Pipeline Complete")
        global pipeline_complete
        pipeline_complete = True

    loop.run_until_complete(task())