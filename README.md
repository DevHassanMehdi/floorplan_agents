# 🧠 Intelligent Floorplan Generator with SPADE Agents

This project implements an intelligent multi-agent system using [SPADE](https://spade-mas.readthedocs.io/) and a Flask web interface to generate and visualize intelligent floorplans based on structured room requirements. It showcases how autonomous agents can communicate and coordinate to produce optimized architectural layouts.

---

## 🗂️ Project Structure

```
floorplan_agents/
├── agents/
│   ├── data_collector.py      # Sends room specs to designer
│   ├── designer.py            # Lays out rooms in snapped positions
│   ├── reviewer.py            # Scores layout based on quality criteria
│   ├── decision_maker.py      # Selects best layout if multiple exist
│   ├── visualizer.py          # Generates annotated SVG of layout
├── templates/
│   ├── index.html             # Form UI for adding room requirements
│   ├── progress.html          # Shows logs, progress and final SVG
├── static/
│   └── floorplan.svg          # Final generated SVG layout
├── config.py                  # Agent XMPP credentials
├── main.py                    # Original CLI runner (replaced by Flask)
├── app.py                     # Flask web app
├── floorplan_layout.json      # Output JSON from designer
└── README.md                  # You are here
```

---

## 🌐 How to Use the Web App

1. Launch the Flask server:

```bash
export FLASK_APP=app.py
flask run
```

2. Visit `http://127.0.0.1:5000/` in your browser.

3. Use the form to add rooms, connect them, and set preferences.

4. Click **Generate Floorplan**.

5. View pipeline progress and final layout in SVG.

---

## 🧠 Technical Agent Architecture

This system uses **four core agents** communicating via **XMPP**:

### 🔹 DataCollectorAgent
- Collects user room specs (via web UI)
- Sends data to DesignerAgent using SPADE messages
- Triggers pipeline execution with a `done` signal

### 🔹 DesignerAgent
- Receives room specs
- Places hallway first, then arranges connected rooms
- Applies snapping and spacing rules
- Ensures rooms align with connection and hallway logic
- Outputs geometry in `floorplan_layout.json`

### 🔹 ReviewerAgent
- Reads the generated floorplan and compares it to specs
- Scores layout based on:
  - Floor area usage
  - Accuracy to desired room sizes
  - Rectangularity of building
- Marks design as ✅ Approved or ❌ Rejected

### 🔹 DecisionMakerAgent
- In future: Will choose best layout from multiple options
- Currently: Confirms review result and passes to visualizer

---

## 🎨 Visualization

SVG visualization is generated and saved in `static/floorplan.svg`. Features include:

- Color-coded rooms
- Room labels and dimensions
- Smart door rendering (based on shared walls)
- Legend and scaling
- Zoom and open in new tab from web UI

---

## ✅ Features

- ✅ Multi-agent SPADE system (XMPP-based)
- ✅ Modular Flask UI with live logs
- ✅ Add/edit/delete rooms via form
- ✅ Constraint-based spatial design logic
- ✅ Reviewer scoring logic for optimization
- ✅ Theme toggle, navigation bar, SVG rendering

---

## ⚙️ Requirements

- Python 3.10
- Flask
- SPADE
- matplotlib

Install with:

```bash
pip install flask spade matplotlib
```

---

## 🔐 XMPP Setup

Register free accounts at [xmpp.jp](https://xmpp.jp) or similar. Update `config.py`:

```python
DATA_COLLECTOR_JID = "data_collector@xmpp.jp"
DATA_COLLECTOR_PASS = "your_password"

DESIGNER_JID = "my_designer@xmpp.jp"
DESIGNER_PASS = "your_password"

REVIEWER_JID = "reviewer_agent@xmpp.jp"
REVIEWER_PASS = "your_password"

DECISION_MAKER_JID = "decision_agent@xmpp.jp"
DECISION_MAKER_PASS = "your_password"
```

---

## 🔮 Planned Enhancements

- Reviewer for room orientation and open sides
- Multiple layout variants for DecisionMakerAgent
- Tabbed SVG viewer and legend
- Export as PDF or DXF
- User authentication for room presets

---

## 👨‍💻 Authors

Built by **Hassan Mehdi** with **Juuso Nikkinen** (TIES454, 2025)  
Powered by **SPADE**, **matplotlib**, and **Flask**

---

## 📜 License

MIT License. Free to use, extend, and contribute.