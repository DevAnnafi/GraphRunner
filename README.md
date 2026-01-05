# Graph Runner

Graph Runner is a fast-paced, precision-based arcade game inspired by *The World’s Hardest Game*.  
It combines continuous player movement with **Dijkstra’s algorithm–driven enemy pathfinding**.

Built with **Python and Pygame**, the project demonstrates how classical graph algorithms can be integrated into real-time game systems.

---

## Features

- Continuous, physics-like movement (no grid snapping)
- Adaptive enemies that chase the player using **Dijkstra’s shortest path algorithm**
- Deterministic fixed-path “rail” enemies (classic timing challenges)
- Safe zones and checkpoints
- Circular collision detection
- Grid-based navigation with smooth pixel interpolation

---

## Tech Stack

- **Python 3**
- **Pygame**
- **Dijkstra’s Algorithm (graph-based pathfinding)**

---

## Gameplay Mechanics

### Adaptive Enemies
Enemies dynamically compute the shortest path to the player using Dijkstra’s algorithm over a grid-based navigation graph.

### Fixed-Path Enemies
Classic rail enemies move along predefined paths to create timing-based difficulty.

### Safe Zones
Green zones act as checkpoints and temporarily disable enemy collision.

---

---
### Gameplay


---

## Installation & Running Locally

```bash
git clone https://github.com/DevAnnafi/graph-runner.git
cd graph-runner
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py

