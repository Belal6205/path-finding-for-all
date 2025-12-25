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