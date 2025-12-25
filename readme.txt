

# ♿ Pathfinding for All: AI Accessibility Simulator

### *Bridging Algorithm Theory and Real-World Mobility*



## 📖 1. Project Vision & Mission

As computer science students, we often study algorithms in a vacuum. This project, created for our **Introduction to AI** course, aims to change that.

**The Mission:** To assist people with disabilities in navigating complex environments.
Navigating a building or a city isn't just about the "shortest" path; it's about the "best" path. Our simulator allows users to model architectural barriers (walls, narrow corridors, or stairs) as "walls" in a grid, then applies AI search logic to find the most efficient route for someone with mobility challenges.



## 🕹️ 2. Core Features

### 🖥️ Interactive Simulation (GUI)

Our custom-built Tkinter interface provides a laboratory for pathfinding:

* **Real-time Animation**: Watch the "Search Cloud" (expanded nodes) grow as the AI thinks.
* **Step-by-Step Execution**: Pause and step through the algorithm to understand its logic.
* **Comparison Mode**: Run two algorithms side-by-side to see which is more "cautious" or "direct."
* **Map Editor**: Click and drag to draw your own floor plans and save them as JSON.

### 🧪 Algorithm Suite

We implemented and compared five fundamental search strategies:

1. **A* (A-Star)**: The gold standard. Uses  to balance distance and direction.
2. **Dijkstra**: The reliable explorer. Guarantees the shortest path by searching uniformly in all directions.
3. **Greedy Best-First**: The fast-mover. Focuses purely on the goal, though it can sometimes get stuck in "traps."
4. **Breadth-First Search (BFS)**: Ideal for finding the fewest "steps" on unweighted maps.
5. **Depth-First Search (DFS)**: A memory-efficient explorer that often takes long, winding routes.



## 🛠️ 3. Technical Architecture

The project follows a modular design pattern to separate logic from visualization:

* **`algorithms/`**: Contains the mathematical core. Each algorithm follows a strict "Contract": it receives a grid and returns a tuple: `(path, cost, expanded_nodes, time_taken)`.
* **`grid/`**: The environment engine. Handles neighbor validation and obstacle detection.
* **`heuristics.py`**: Mathematical distance functions:
* **Manhattan**:  (best for 4-directional grid movement).
* **Euclidean**:  (straight-line "as the crow flies").


* **`gui.py`**: The presentation layer, built with Python's Tkinter library.



## 📊 4. Experimental Analysis

We conducted benchmarks across 10 unique map scenarios to prove the efficiency of our AI models.

| Algorithm | Optimality | Speed | Best Use Case |
| --- | --- | --- | --- |
| **A*** | ✅ Guaranteed | ⚡ Fast | Most efficient for real-world navigation. |
| **Dijkstra** | ✅ Guaranteed | 🐢 Slower | When the map has no clear "direction." |
| **Greedy** | ❌ No | 🚀 Very Fast | Finding a "good enough" path instantly. |
| **BFS** | ✅ Guaranteed | 🐢 Slower | Simple, unweighted grids. |



## 🚦 5. Installation & Usage

### Prerequisites

* Python 3.10 or higher.
* No external libraries required (uses standard `tkinter`).

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-pathfinding-accessibility.git
cd ai-pathfinding-accessibility




2. **Run the Visualizer**:
* Double-click `run_gui.bat` (Windows) or run `python gui.py`.


3. **Run the Performance Report**:
* Run `python main.py` and type `report` to see the full data table in your terminal.





## 👥 6. The Masters Team

This project was a collaborative effort by our team, with each member owning a critical component of the system:

* **Adham Sobhy (Leader)**: Masterminded the GUI architecture and the core A* integration.
* **Yassin**: Led the implementation of Dijkstra and acted as the QA lead for path validation.
* **Andrew Emad**: Engineered the Greedy search logic and implemented the Manhattan/Euclidean heuristic toggles.
* **Belal Mohamed**: Designed the benchmark maps and implemented BFS/DFS behaviors.
* **Ahmed**: Managed the project packaging, directory structure, and troubleshooting guides.
* **Mohamed**: Conducted the performance analysis, generated data tables, and designed the project presentation.



## 🔮 7. Future Work

* **Weighted Terrain**: Adding "slow" areas (carpet or ramps) vs "fast" areas (smooth floors).
* **Multi-Floor Navigation**: Implementing elevator/stair logic for 3D buildings.
* **Mobile Integration**: Exporting paths to a mobile interface for real-time guidance.



*“Technology is at its best when it brings people together and levels the playing field.”*
HOW TO RUN:
1. python main.py
2. Select a map (1-10) or type "report" to print results tables for all maps
3. Select an algorithm (1-5) or type "all"
4. View results

GUI (Phase 3):
1. run_gui.bat (recommended) OR python gui.py
2. Select a map and algorithm from the dropdowns
3. Click Run to show the path and metrics

PHASE 3 - CORE API RULES (DO NOT BREAK)
-------------------------------------
Single source of truth folder:
- AI Deliverable Three

Core modules (LOCKED unless Adham approves):
- algorithms/algorithms.py
- grid/grid.py
- heuristics.py

Algorithm contract (used by BOTH console and GUI):
- Call signature: algo_func(grid)
- Return: (path, cost, expanded_nodes, time_taken)
  * path: None (no path) OR list[(row,col)] from start to goal (inclusive)
  * cost: integer number of steps
  * expanded_nodes: integer
  * time_taken: seconds (float)

Map contract:
- Map functions must return a Grid object from grid/grid.py
- Grid must define: rows, cols, walls(set), start, goal, get_neighbors(row,col)

Allowed edits per member:
- Belal (maps): add new map factory functions in grid/grid.py, then register them in main.py and gui.py
- Andrew (GUI/UX): gui.py only (layout/colors/controls)
- Ahmed (packaging/docs): readme.txt + submission folder structure
- Mohamed (results/PPT): no code changes needed (use console report mode)
- Yassin (QA): no code changes unless a bug is confirmed

Adham merge & sanity checklist (run after every merge):
1) python main.py  -> type: report  (must print tables for all maps)
2) python gui.py   (must open, select Map 6 + A*, click Run)
3) python gui.py   (select Map 3 + BFS, click Run -> NO PATH)
4) Ensure no one changed the algorithm/map interfaces above.

HOW TO RUN (DETAILED) + TROUBLESHOOTING
--------------------------------------
Step 1: Prepare the Environment
- Install Python 3.x
- Confirm Python works:
  - python --version

Step 2: Verify Folder Structure
Project root should contain:
- main.py (console entry point)
- gui.py (GUI entry point)
- heuristics.py
- algorithms/ (contains algorithms.py)
- grid/ (contains grid.py)

Step 3: Run Console Mode (CLI)
- Run:
  - python main.py
- When prompted, you can:
  - Choose a map number (1-10)
  - OR type: report  (prints results tables for all maps/algorithms)
- Then choose an algorithm (1-5) or type: all

Step 4: Run GUI Mode
- Option A (recommended): double click:
  - run_gui.bat
- Option B: run directly:
  - python gui.py

GUI Notes
- If you select Greedy Best-First, a Heuristic dropdown appears:
  - Manhattan (default)
  - Euclidean

Troubleshooting
- If 'python' is not recognized:
  - Reinstall Python and enable "Add Python to PATH"
- If the GUI does not open:
  - Ensure you are running from the project root folder

  - Tkinter must be available (it is included with most standard Python installs)
