# 🧠 Intelligent Floorplan Generator with SPADE Agents

This project implements an intelligent multi-agent system using [SPADE](https://spade-mas.readthedocs.io/) to generate and visualize floorplans from room requirements. The system includes autonomous agents that collect room specifications, process spatial layouts, and output a visualized design.

---

## 📁 Project Structure

```
floorplan_agents/
├── agents/
│   ├── data_collector.py      # Sends room requirements to DesignerAgent
│   ├── designer.py            # Processes room layout and outputs geometry
├── config.py                  # XMPP credentials for both agents
├── main.py                    # Launches both SPADE agents
├── visualizer.py              # Draws room layout using matplotlib
├── floorplan_layout.json      # Output JSON with room geometry
└── README.md                  # 📘 You are here
```

---

## 🤖 Agents

### `DataCollectorAgent`
- Sends structured room specs to `DesignerAgent`
- Sends a final `"done"` message to trigger processing

### `DesignerAgent`
- Receives rooms and organizes them into clusters
- Computes spatial layout and dimensions
- Exports `floorplan_layout.json`

---

## 🖼️ Visualization

The layout is visualized using `matplotlib`:
- Rooms are colored by type (e.g., kitchen, hallway)
- Labels are centered
- Grid spacing avoids overlaps
- An optional legend improves readability

---

## 📦 Requirements

- Python 3.10
- matplotlib
- [Conda environment (recommended)](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)

Install dependencies:

```bash
pip install spade matplotlib
```

---

## 🔐 XMPP Setup

This project uses public XMPP servers (like `xmpp.jp`) for agent communication.

Create two users:

- `data_collector@xmpp.jp`
- `my_designer@xmpp.jp`

Update `config.py`:

```python
DATA_COLLECTOR_JID = "data_collector@xmpp.jp"
DATA_COLLECTOR_PASS = "your_password"

DESIGNER_JID = "my_designer@xmpp.jp"
DESIGNER_PASS = "your_password"
```

---

## 🚀 How to Run

1. Run the SPADE agents:

```bash
python main.py
```

This will:
- Start both agents
- Send room definitions
- Generate and save the layout JSON

2. Visualize the layout:

```bash
python visualizer.py
```

---

## 🎨 Output Example

- Rooms are rendered with colors like:

| Room Type  | Color         |
|------------|---------------|
| Living Room | lightblue     |
| Kitchen     | coral         |
| Bedroom     | plum          |
| Bathroom    | lightgreen    |
| Toilet      | lightsalmon   |
| Hallway     | gray          |

---

## 📌 Features

✅ Multi-agent communication using XMPP  
✅ Arbitrary number of rooms  
✅ Automatic layout generation  
✅ JSON export of geometric plan  
✅ Matplotlib-based visualizer with color coding  
✅ Legend, labels, and spacing adjustments  

---

## 🛠️ Future Extensions

- Room shape generalization (e.g., L-shapes)
- Hallway access enforcement
- Export to SVG or DXF
- Layout optimization (fitness scoring)

---

## 🧑‍💻 Author

Hassan Mehdi  
Built using [SPADE](https://spade-mas.readthedocs.io/) and `matplotlib`.

---

## 📜 License

MIT License. Feel free to use, modify, and share.