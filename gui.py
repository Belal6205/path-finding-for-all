import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import random
import time
import json
import csv
import os
import ctypes
import copy

try:
    if os.name == "nt":
        ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

from algorithms.algorithms import run_astar, run_bfs, run_dfs, run_dijkstra, run_greedy
from grid.grid import Grid
from grid.grid import (
    create_andrew_map_5x5,
    create_comparison_map,
    create_greedy_trap_map,
    create_dfs_deep_trap_map,
    create_bridge_map_7x7,
    create_maze_map,
    create_no_path_map,
    create_simple_map,
    create_yassin_maze_5x5,
    create_yassin_simple_3x3,
)
from heuristics import euclidean, manhattan


class PathfindingGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI Pathfinding Simulator - Phase 3")
        self.minsize(1020, 680)
        self.configure(bg="#1e293b")

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#1e293b")
        style.configure("TLabel", background="#1e293b", foreground="#e2e8f0")
        style.configure("TButton", padding=(10, 6))
        style.configure("TCombobox", padding=(6, 4))

        self._random_map_key = "Random Map"
        self._random_run_counter = 0
        self._last_random_seed = None

        self.animate_var = tk.BooleanVar(value=True)
        self.animate_search_var = tk.BooleanVar(value=True)
        self.speed_ms_var = tk.IntVar(value=35)

        self._animation_after_id = None
        self._full_path = None
        self._anim_index = 0

        self._search_after_id = None
        self._search_order = None
        self._search_index = 0
        self._expanded_set = set()
        self._is_paused = False

        self.maps = {
            "Simple 5x5": create_simple_map,
            "Maze 10x10": create_maze_map,
            "No Path 5x5": create_no_path_map,
            "Comparison 8x8": create_comparison_map,
            "Small 3x3": create_yassin_simple_3x3,
            "Maze 5x5": create_yassin_maze_5x5,
            "Comparison 5x5": create_andrew_map_5x5,
            "Greedy Trap": create_greedy_trap_map,
            "DFS Deep Trap": create_dfs_deep_trap_map,
            "Bridge 7x7": create_bridge_map_7x7,
            self._random_map_key: self._create_random_map,
        }

        self.algorithms = {
            "A*": run_astar,
            "Dijkstra": run_dijkstra,
            "Greedy Best-First": run_greedy,
            "BFS": run_bfs,
            "DFS": run_dfs,
        }

        self.heuristics = {
            "Manhattan (default)": manhattan,
            "Euclidean": euclidean,
        }

        self.selected_map_name = tk.StringVar(value=list(self.maps.keys())[0])
        self.selected_algo_name = tk.StringVar(value=list(self.algorithms.keys())[0])
        self.selected_heuristic_name = tk.StringVar(value=list(self.heuristics.keys())[0])

        self.grid_obj = None
        self.last_path = None
        self._cells = []

        self.status_var = tk.StringVar(value="Ready")

        self._last_results = []  # list of dicts for leaderboard/export

        self._build_ui()
        self._load_map()
        self._on_algo_change()

    def _copy_grid(self, grid):
        g = Grid(grid.rows, grid.cols)
        g.walls = set(grid.walls)
        g.start = grid.start
        g.goal = grid.goal
        return g

    def _is_random_map_selected(self):
        return self.selected_map_name.get() == self._random_map_key

    def _regenerate_random_map(self):
        if not self._is_random_map_selected():
            return
        self._cancel_animation()
        self._expanded_set = set()
        self._random_run_counter += 1
        self._last_random_seed = time.time_ns()
        self.grid_obj = self._create_random_map(seed=self._last_random_seed)
        self.last_path = None
        self._set_metrics("Random map regenerated. Choose an algorithm and click Run.\n")
        self.status_var.set("Random map regenerated")
        self._draw()

    def _create_random_map(self, rows=20, cols=20, wall_prob=0.28, seed=None):
        """Create a randomized grid with obstacles but guarantees at least one valid path."""
        if seed is None:
            seed = time.time_ns()
        rng = random.Random(seed)

        grid = Grid(rows, cols)
        grid.set_start(0, 0)
        grid.set_goal(rows - 1, cols - 1)

        # Create a guaranteed path using a randomized sequence of right/down moves
        path = [grid.start]
        r, c = grid.start
        moves = ["D"] * (rows - 1) + ["R"] * (cols - 1)
        rng.shuffle(moves)
        for mv in moves:
            if mv == "D":
                r += 1
            else:
                c += 1
            path.append((r, c))
        path_set = set(path)

        for rr in range(rows):
            for cc in range(cols):
                if (rr, cc) in path_set:
                    continue
                if (rr, cc) == grid.start or (rr, cc) == grid.goal:
                    continue
                if rng.random() < wall_prob:
                    grid.set_wall(rr, cc)

        return grid

    def _build_ui(self):
        top = ttk.Frame(self, padding=12)
        top.pack(side=tk.TOP, fill=tk.X)

        title = ttk.Label(
            top,
            text="AI Pathfinding Simulator",
            font=("Segoe UI", 13, "bold"),
        )
        title.pack(side=tk.LEFT, padx=(0, 14))

        ttk.Label(top, text="Map:").pack(side=tk.LEFT)
        map_combo = ttk.Combobox(
            top,
            textvariable=self.selected_map_name,
            values=list(self.maps.keys()),
            state="readonly",
            width=30,
        )
        map_combo.pack(side=tk.LEFT, padx=(8, 16))
        map_combo.bind("<<ComboboxSelected>>", lambda _e: self._load_map())

        ttk.Label(top, text="Algorithm:").pack(side=tk.LEFT)
        algo_combo = ttk.Combobox(
            top,
            textvariable=self.selected_algo_name,
            values=list(self.algorithms.keys()),
            state="readonly",
            width=18,
        )
        algo_combo.pack(side=tk.LEFT, padx=(8, 16))
        algo_combo.bind("<<ComboboxSelected>>", lambda _e: self._on_algo_change())

        self.heuristic_label = ttk.Label(top, text="Heuristic:")

        self.heuristic_combo = ttk.Combobox(
            top,
            textvariable=self.selected_heuristic_name,
            values=list(self.heuristics.keys()),
            state="readonly",
            width=18,
        )

        self.run_button = ttk.Button(top, text="Run", command=self._run)
        self.run_button.pack(side=tk.LEFT)

        self.regen_button = ttk.Button(top, text="Regenerate", command=self._regenerate_random_map)

        ttk.Button(top, text="Clear Path", command=self._clear_path).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        ttk.Button(top, text="Run All", command=self._run_all).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(top, text="Compare", command=self._open_compare_window).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(top, text="Editor", command=self._open_editor_window).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(top, text="Export CSV", command=self._export_last_results_csv).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(top, text="Export Screenshot", command=self._export_screenshot).pack(side=tk.LEFT, padx=(8, 0))

        ttk.Separator(self, orient="horizontal").pack(fill=tk.X)

        mid = ttk.Frame(self, padding=12)
        mid.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Canvas area
        canvas_frame = ttk.Frame(mid)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_frame, background="#0f172a")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right panel
        right = ttk.Frame(mid, width=320)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(right, text="Metrics", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", pady=(0, 8)
        )

        controls = ttk.Frame(right)
        controls.pack(fill=tk.X, pady=(0, 10))

        ttk.Checkbutton(controls, text="Animate", variable=self.animate_var).pack(
            anchor="w"
        )
        ttk.Checkbutton(
            controls,
            text="Animate Search (expanded nodes)",
            variable=self.animate_search_var,
        ).pack(anchor="w", pady=(4, 0))

        btn_row = ttk.Frame(controls)
        btn_row.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(btn_row, text="Pause", command=self._pause).pack(side=tk.LEFT)
        ttk.Button(btn_row, text="Resume", command=self._resume).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(btn_row, text="Step", command=self._step_once).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Button(btn_row, text="Stop", command=self._stop).pack(side=tk.LEFT, padx=(6, 0))
        ttk.Label(controls, text="Speed (ms/step):").pack(anchor="w", pady=(6, 0))
        ttk.Scale(
            controls,
            from_=10,
            to=150,
            variable=self.speed_ms_var,
            orient="horizontal",
        ).pack(fill=tk.X)

        self.metrics_text = tk.Text(
            right,
            width=42,
            height=22,
            wrap="word",
        )
        self.metrics_text.pack(fill=tk.BOTH, expand=False)
        self.metrics_text.configure(state="disabled")

        ttk.Label(right, text="Legend", font=("Segoe UI", 12, "bold")).pack(
            anchor="w", pady=(16, 8)
        )

        legend = ttk.Frame(right)
        legend.pack(anchor="w")
        self._legend_row(legend, "Start", "#22c55e")
        self._legend_row(legend, "Goal", "#ef4444")
        self._legend_row(legend, "Wall", "#334155")
        self._legend_row(legend, "Empty", "#e2e8f0")
        self._legend_row(legend, "Path", "#38bdf8")
        self._legend_row(legend, "Expanded", "#f59e0b")

        self.canvas.bind("<Configure>", lambda _e: self._draw())

        status = ttk.Frame(self, padding=(12, 6))
        status.pack(side=tk.BOTTOM, fill=tk.X)
        ttk.Label(status, textvariable=self.status_var).pack(side=tk.LEFT)

    def _legend_row(self, parent, label, color):
        row = ttk.Frame(parent)
        row.pack(anchor="w", pady=2)
        swatch = tk.Canvas(row, width=14, height=14, highlightthickness=0)
        swatch.create_rectangle(0, 0, 14, 14, fill=color, outline=color)
        swatch.pack(side=tk.LEFT)
        ttk.Label(row, text=f"  {label}").pack(side=tk.LEFT)

    def _set_metrics(self, text):
        self.metrics_text.configure(state="normal")
        self.metrics_text.delete("1.0", tk.END)
        self.metrics_text.insert(tk.END, text)
        self.metrics_text.configure(state="disabled")

    def _cancel_animation(self):
        if self._animation_after_id is not None:
            try:
                self.after_cancel(self._animation_after_id)
            except Exception:
                pass
            self._animation_after_id = None
        self._full_path = None
        self._anim_index = 0

        if self._search_after_id is not None:
            try:
                self.after_cancel(self._search_after_id)
            except Exception:
                pass
            self._search_after_id = None
        self._search_order = None
        self._search_index = 0

    def _load_map(self):
        self._cancel_animation()
        self._expanded_set = set()
        creator = self.maps[self.selected_map_name.get()]
        if self._is_random_map_selected():
            # Generate once on selection; subsequent runs reuse the same grid.
            self._random_run_counter += 1
            self._last_random_seed = time.time_ns()
            self.grid_obj = self._create_random_map(seed=self._last_random_seed)
        else:
            self.grid_obj = creator()
        self.last_path = None
        if self._is_random_map_selected():
            self._set_metrics("Random map loaded. Click Run to solve, or Regenerate to create a new map.\n")
        else:
            self._set_metrics("Loaded map. Choose an algorithm and click Run.\n")

        # Show Regenerate only for Random Map
        if self._is_random_map_selected():
            self.regen_button.pack(side=tk.LEFT, padx=(8, 0), before=self.run_button)
        else:
            self.regen_button.pack_forget()

        self._draw()

    def _clear_path(self):
        self._cancel_animation()
        self.last_path = None
        self._set_metrics("Path cleared.\n")
        self.status_var.set("Path cleared")
        self._draw()

    def _pause(self):
        self._is_paused = True
        self.status_var.set("Paused")

    def _resume(self):
        if not self._is_paused:
            return
        self._is_paused = False
        self.status_var.set("Running")
        if self._search_order is not None:
            self._animate_search_step()
        elif self._full_path is not None:
            self._animate_step()

    def _stop(self):
        self._cancel_animation()
        self.last_path = None
        self._expanded_set = set()
        self._is_paused = False
        self.status_var.set("Stopped")
        self._draw()

    def _step_once(self):
        # Step through search first, then through path
        if self._search_order is not None:
            self._animate_search_step(step_only=True)
            return
        if self._full_path is not None:
            self._animate_step(step_only=True)

    def _animate_step(self, step_only=False):
        if not self._full_path:
            self._animation_after_id = None
            return

        if self._anim_index >= len(self._full_path):
            self._animation_after_id = None
            return

        self.last_path = self._full_path[: self._anim_index + 1]
        self._anim_index += 1
        self._draw()

        if step_only or self._is_paused:
            self._animation_after_id = None
            return

        delay = int(self.speed_ms_var.get())
        self._animation_after_id = self.after(delay, self._animate_step)

    def _animate_search_step(self, step_only=False):
        if not self._search_order:
            self._search_after_id = None
            return

        if self._search_index >= len(self._search_order):
            self._search_after_id = None
            # After search animation ends, animate final path if requested
            if self._full_path is not None and self.animate_var.get() and not self._is_paused:
                self._animate_step()
            return

        node = self._search_order[self._search_index]
        self._expanded_set.add(node)
        self._search_index += 1
        self._draw()

        if step_only or self._is_paused:
            self._search_after_id = None
            return

        delay = int(self.speed_ms_var.get())
        self._search_after_id = self.after(delay, self._animate_search_step)

    def _on_algo_change(self):
        algo_name = self.selected_algo_name.get()
        is_greedy = "Greedy" in algo_name
        if is_greedy:
            self.heuristic_label.pack(side=tk.LEFT, before=self.run_button)
            self.heuristic_combo.pack(side=tk.LEFT, padx=(8, 16), before=self.run_button)
        else:
            self.heuristic_label.pack_forget()
            self.heuristic_combo.pack_forget()

    def _run(self):
        self._cancel_animation()
        algo_name = self.selected_algo_name.get()
        algo = self.algorithms[algo_name]

        self.status_var.set("Running...")

        # Reset any previous expanded visualization for this new run
        self._expanded_set = set()

        trace = bool(self.animate_search_var.get())
        if "Greedy" in algo_name:
            heuristic = self.heuristics[self.selected_heuristic_name.get()]
            if trace:
                path, cost, expanded, time_taken, expanded_order = algo(
                    self.grid_obj, heuristic=heuristic, trace=True
                )
            else:
                path, cost, expanded, time_taken = algo(self.grid_obj, heuristic=heuristic)
                expanded_order = None
        else:
            if trace:
                path, cost, expanded, time_taken, expanded_order = algo(self.grid_obj, trace=True)
            else:
                path, cost, expanded, time_taken = algo(self.grid_obj)
                expanded_order = None

        self._full_path = path if path is not None else None
        self.last_path = [] if (path is not None and self.animate_var.get()) else path
        self._anim_index = 0

        if expanded_order is not None:
            self._search_order = expanded_order
            self._search_index = 0
            # If search animation is disabled, still show the explored nodes immediately.
            if not self.animate_search_var.get():
                self._expanded_set = set(expanded_order)

        if path is None:
            result = "NO PATH FOUND"
            path_str = "(none)"
        else:
            result = "PATH FOUND"
            path_str = " -> ".join([str(p) for p in path])

        algo_display = self.selected_algo_name.get()
        if "Greedy" in algo_name:
            heuristic_name = self.selected_heuristic_name.get()
            algo_display = f"{algo_display}\n  Heuristic: {heuristic_name}"

        map_display = self.selected_map_name.get()
        if self._is_random_map_selected():
            map_display = (
                f"{map_display}\n"
                f"  Generated: {self._random_run_counter}\n"
                f"  Walls: {len(self.grid_obj.walls)}\n"
                f"  Seed: {self._last_random_seed}"
            )

        self._set_metrics(
            "\n".join(
                [
                    f"Map: {map_display}",
                    f"Algorithm: {algo_display}",
                    "",
                    "━" * 30,
                    f"  Result: {result}",
                    f"  Path length: {cost} steps",
                    f"  Expanded nodes: {expanded}",
                    f"  Time: {time_taken:.6f} sec",
                    "━" * 30,
                    "",
                    "Path:",
                    path_str,
                ]
            )
            + "\n"
        )

        self._draw()
        if self._search_order is not None and self.animate_search_var.get():
            self._animate_search_step()
        elif self._full_path is not None and self.animate_var.get():
            self._animate_step()

        self.status_var.set("Done")

    def _run_all(self):
        # Runs all algorithms on the current map and stores results for export
        if self.grid_obj is None:
            return

        self._last_results = []
        for algo_name, algo_func in self.algorithms.items():
            g = self._copy_grid(self.grid_obj)
            if "Greedy" in algo_name:
                heuristic = self.heuristics[self.selected_heuristic_name.get()]
                path, cost, expanded, time_taken = algo_func(g, heuristic=heuristic)
            else:
                path, cost, expanded, time_taken = algo_func(g)
            self._last_results.append(
                {
                    "Algorithm": algo_name,
                    "Found": "Yes" if path is not None else "No",
                    "Cost": cost,
                    "Expanded": expanded,
                    "Time": time_taken,
                }
            )

        # Show in metrics as a small table
        lines = ["Run All Results:", "| Algorithm | Found | Cost | Expanded | Time (s) |", "|---|---|---:|---:|---:|"]
        for r in self._last_results:
            lines.append(
                f"| {r['Algorithm']} | {r['Found']} | {r['Cost']} | {r['Expanded']} | {r['Time']:.6f} |"
            )
        self._set_metrics("\n".join(lines) + "\n")
        self.status_var.set("Run All complete")

    def _export_last_results_csv(self):
        if not self._last_results:
            messagebox.showinfo("Export CSV", "Run 'Run All' first to generate results.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Export Results CSV",
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["Algorithm", "Found", "Cost", "Expanded", "Time"])
            writer.writeheader()
            for row in self._last_results:
                writer.writerow(row)
        messagebox.showinfo("Export CSV", f"Saved: {path}")

    def _export_screenshot(self):
        if self.grid_obj is None:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("JPEG", "*.jpeg"), ("PostScript (fallback)", "*.ps")],
            title="Export Canvas Screenshot",
        )
        if not path:
            return
        try:
            ext = os.path.splitext(path)[1].lower()
            if ext in (".png", ".jpg", ".jpeg"):
                try:
                    from PIL import ImageGrab

                    self.update_idletasks()
                    bbox = None

                    # Most reliable on Windows: ask Win32 for the *client area* rect in screen pixels.
                    try:
                        if os.name == "nt":
                            hwnd = int(self.canvas.winfo_id())

                            class _RECT(ctypes.Structure):
                                _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]

                            class _POINT(ctypes.Structure):
                                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

                            rect = _RECT()
                            if ctypes.windll.user32.GetClientRect(hwnd, ctypes.byref(rect)):
                                pt = _POINT(0, 0)
                                ctypes.windll.user32.ClientToScreen(hwnd, ctypes.byref(pt))
                                w = int(rect.right - rect.left)
                                h = int(rect.bottom - rect.top)
                                bbox = (int(pt.x), int(pt.y), int(pt.x + w), int(pt.y + h))
                    except Exception:
                        bbox = None

                    # Fallback: scale Tk root coords into physical pixels.
                    if bbox is None:
                        scales = [1.0]
                        try:
                            hwnd = int(self.canvas.winfo_id())
                            dpi = ctypes.windll.user32.GetDpiForWindow(hwnd)
                            if dpi:
                                scales.append(float(dpi) / 96.0)
                        except Exception:
                            pass

                        try:
                            scales.append(float(self.tk.call("tk", "scaling")))
                        except Exception:
                            pass

                        try:
                            ppi = float(self.winfo_fpixels("1i"))
                            if ppi:
                                scales.append(ppi / 96.0)
                        except Exception:
                            pass

                        scale = max(scales)
                        x = int(self.canvas.winfo_rootx() * scale)
                        y = int(self.canvas.winfo_rooty() * scale)
                        w = int(self.canvas.winfo_width() * scale)
                        h = int(self.canvas.winfo_height() * scale)
                        bbox = (x, y, x + w, y + h)

                    img = ImageGrab.grab(bbox=bbox)
                    img.save(path)
                    messagebox.showinfo("Export Screenshot", f"Saved: {path}")
                except ImportError:
                    messagebox.showerror(
                        "Export Screenshot",
                        "PNG/JPG export requires Pillow.\n\nInstall: pip install pillow\n\nOr export as .ps using the file type dropdown.",
                    )
                except Exception as e:
                    messagebox.showerror("Export Screenshot", str(e))
            else:
                self.canvas.postscript(file=path, colormode="color")
                messagebox.showinfo("Export Screenshot", f"Saved (PostScript): {path}")
        except Exception as e:
            messagebox.showerror("Export Screenshot", str(e))

    def _open_compare_window(self):
        if self.grid_obj is None:
            return

        win = tk.Toplevel(self)
        win.title("Compare Algorithms")
        win.geometry("1100x600")

        left_algo = tk.StringVar(value=list(self.algorithms.keys())[0])
        right_algo = tk.StringVar(value=list(self.algorithms.keys())[1])

        top = ttk.Frame(win, padding=10)
        top.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(top, text="Left:").pack(side=tk.LEFT)
        left_combo = ttk.Combobox(
            top,
            textvariable=left_algo,
            values=list(self.algorithms.keys()),
            state="readonly",
            width=18,
        )
        left_combo.pack(side=tk.LEFT, padx=6)
        ttk.Label(top, text="Right:").pack(side=tk.LEFT, padx=(16, 0))
        right_combo = ttk.Combobox(
            top,
            textvariable=right_algo,
            values=list(self.algorithms.keys()),
            state="readonly",
            width=18,
        )
        right_combo.pack(side=tk.LEFT, padx=6)

        mid = ttk.Frame(win, padding=10)
        mid.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        canvas_l = tk.Canvas(mid, background="#0f172a")
        canvas_r = tk.Canvas(mid, background="#0f172a")
        canvas_l.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        canvas_r.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0))

        metrics = tk.Text(win, height=8, wrap="word")
        metrics.pack(side=tk.BOTTOM, fill=tk.X)

        state = {
            "g1": None,
            "g2": None,
            "p1_full": None,
            "p2_full": None,
            "p1": None,
            "p2": None,
            "order1": None,
            "order2": None,
            "exp1": set(),
            "exp2": set(),
            "i1": 0,
            "i2": 0,
            "pi1": 0,
            "pi2": 0,
            "phase": "idle",  # idle | search | path
            "after_id": None,
            "c1": 0,
            "c2": 0,
            "e1": 0,
            "e2": 0,
            "t1": 0.0,
            "t2": 0.0,
        }

        def cancel_anim():
            if state["after_id"] is not None:
                try:
                    win.after_cancel(state["after_id"])
                except Exception:
                    pass
                state["after_id"] = None
            state["phase"] = "idle"

        def draw_on(canvas, grid, path, expanded_set):
            canvas.delete("all")
            rows, cols = grid.rows, grid.cols
            w = max(1, canvas.winfo_width())
            h = max(1, canvas.winfo_height())
            padding = 18
            cell = max(8, min((w - 2 * padding) // cols, (h - 2 * padding) // rows))
            x0 = (w - cell * cols) // 2
            y0 = (h - cell * rows) // 2
            path_set = set(path) if path else set()
            for rr in range(rows):
                for cc in range(cols):
                    x1 = x0 + cc * cell
                    y1 = y0 + rr * cell
                    x2 = x1 + cell
                    y2 = y1 + cell
                    fill = "#e2e8f0"
                    if (rr, cc) in grid.walls:
                        fill = "#334155"
                    if (rr, cc) in expanded_set and (rr, cc) not in grid.walls and (rr, cc) not in (grid.start, grid.goal):
                        fill = "#fbbf24"
                    if (rr, cc) in path_set and (rr, cc) not in (grid.start, grid.goal):
                        fill = "#38bdf8"
                    if (rr, cc) == grid.start:
                        fill = "#22c55e"
                    if (rr, cc) == grid.goal:
                        fill = "#ef4444"
                    canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#0f172a", width=2)

        def compute():
            try:
                cancel_anim()
                g1 = self._copy_grid(self.grid_obj)
                g2 = self._copy_grid(self.grid_obj)
                a1 = self.algorithms[left_algo.get()]
                a2 = self.algorithms[right_algo.get()]

                def run_algo(a, g, name):
                    if "Greedy" in name:
                        heuristic = self.heuristics[self.selected_heuristic_name.get()]
                        return a(g, heuristic=heuristic, trace=True)
                    return a(g, trace=True)

                p1, c1, e1, t1, order1 = run_algo(a1, g1, left_algo.get())
                p2, c2, e2, t2, order2 = run_algo(a2, g2, right_algo.get())

                state.update(
                    {
                        "g1": g1,
                        "g2": g2,
                        "p1_full": p1,
                        "p2_full": p2,
                        "p1": [],
                        "p2": [],
                        "order1": order1 or [],
                        "order2": order2 or [],
                        "exp1": set(),
                        "exp2": set(),
                        "i1": 0,
                        "i2": 0,
                        "pi1": 0,
                        "pi2": 0,
                        "c1": c1,
                        "c2": c2,
                        "e1": e1,
                        "e2": e2,
                        "t1": t1,
                        "t2": t2,
                        "phase": "search",
                    }
                )
                metrics.delete("1.0", tk.END)
                metrics.insert(
                    tk.END,
                    f"Left: {left_algo.get()} | Found={p1 is not None} Cost={c1} Expanded={e1} Time={t1:.6f}\n"
                    f"Right: {right_algo.get()} | Found={p2 is not None} Cost={c2} Expanded={e2} Time={t2:.6f}\n",
                )
            except Exception as e:
                metrics.delete("1.0", tk.END)
                metrics.insert(tk.END, f"Compare error: {e}\n")

        def redraw():
            if state["g1"] is None or state["g2"] is None:
                return
            draw_on(canvas_l, state["g1"], state["p1"], state["exp1"])
            draw_on(canvas_r, state["g2"], state["p2"], state["exp2"])

        def tick():
            if state["phase"] == "idle":
                state["after_id"] = None
                return

            if state["phase"] == "search":
                if state["i1"] < len(state["order1"]):
                    state["exp1"].add(state["order1"][state["i1"]])
                    state["i1"] += 1
                if state["i2"] < len(state["order2"]):
                    state["exp2"].add(state["order2"][state["i2"]])
                    state["i2"] += 1

                if state["i1"] >= len(state["order1"]) and state["i2"] >= len(state["order2"]):
                    state["phase"] = "path"

            elif state["phase"] == "path":
                if state["p1_full"]:
                    if state["pi1"] < len(state["p1_full"]):
                        state["p1"] = state["p1_full"][: state["pi1"] + 1]
                        state["pi1"] += 1
                if state["p2_full"]:
                    if state["pi2"] < len(state["p2_full"]):
                        state["p2"] = state["p2_full"][: state["pi2"] + 1]
                        state["pi2"] += 1

                done1 = (not state["p1_full"]) or state["pi1"] >= len(state["p1_full"])
                done2 = (not state["p2_full"]) or state["pi2"] >= len(state["p2_full"])
                if done1 and done2:
                    state["phase"] = "idle"
                    state["after_id"] = None

            redraw()
            if state["phase"] != "idle":
                delay = int(self.speed_ms_var.get())
                state["after_id"] = win.after(delay, tick)

        def play():
            # Start or restart animation
            if state["g1"] is None or state["g2"] is None:
                return
            cancel_anim()
            state["exp1"] = set()
            state["exp2"] = set()
            state["p1"] = []
            state["p2"] = []
            state["i1"] = 0
            state["i2"] = 0
            state["pi1"] = 0
            state["pi2"] = 0
            state["phase"] = "search"
            tick()

        def run_compare():
            compute()
            redraw()
            play()

        ttk.Button(top, text="Stop", command=cancel_anim).pack(side=tk.RIGHT)
        ttk.Button(top, text="Replay", command=play).pack(side=tk.RIGHT, padx=(0, 6))
        ttk.Button(top, text="Run Compare", command=run_compare).pack(side=tk.RIGHT, padx=(0, 6))
        canvas_l.bind("<Configure>", lambda _e: redraw())
        canvas_r.bind("<Configure>", lambda _e: redraw())
        left_combo.bind("<<ComboboxSelected>>", lambda _e: run_compare())
        right_combo.bind("<<ComboboxSelected>>", lambda _e: run_compare())

        run_compare()

        win.protocol("WM_DELETE_WINDOW", lambda: (cancel_anim(), win.destroy()))

    def _open_editor_window(self):
        win = tk.Toplevel(self)
        win.title("Map Editor")
        win.geometry("1000x650")

        mode = tk.StringVar(value="Wall")

        if self.grid_obj is None:
            self.grid_obj = self._create_random_map(seed=time.time_ns())

        editor_grid = self._copy_grid(self.grid_obj)

        top = ttk.Frame(win, padding=10)
        top.pack(side=tk.TOP, fill=tk.X)
        ttk.Label(top, text="Mode:").pack(side=tk.LEFT)
        for m in ("Wall", "Erase", "Start", "Goal"):
            ttk.Radiobutton(top, text=m, variable=mode, value=m).pack(side=tk.LEFT, padx=6)

        ttk.Button(top, text="Load JSON", command=lambda: load_json()).pack(side=tk.RIGHT)
        ttk.Button(top, text="Save JSON", command=lambda: save_json()).pack(side=tk.RIGHT, padx=(0, 6))
        ttk.Button(top, text="Use In Simulator", command=lambda: apply_to_sim()).pack(side=tk.RIGHT, padx=(0, 6))

        canvas = tk.Canvas(win, background="#0f172a")
        canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        def draw():
            canvas.delete("all")
            rows, cols = editor_grid.rows, editor_grid.cols
            w = max(1, canvas.winfo_width())
            h = max(1, canvas.winfo_height())
            padding = 18
            cell = max(10, min((w - 2 * padding) // cols, (h - 2 * padding) // rows))
            x0 = (w - cell * cols) // 2
            y0 = (h - cell * rows) // 2
            for rr in range(rows):
                for cc in range(cols):
                    x1 = x0 + cc * cell
                    y1 = y0 + rr * cell
                    x2 = x1 + cell
                    y2 = y1 + cell
                    fill = "#e2e8f0"
                    if (rr, cc) in editor_grid.walls:
                        fill = "#334155"
                    if (rr, cc) == editor_grid.start:
                        fill = "#22c55e"
                    if (rr, cc) == editor_grid.goal:
                        fill = "#ef4444"
                    canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline="#0f172a", width=2)

        def cell_from_event(event):
            rows, cols = editor_grid.rows, editor_grid.cols
            w = max(1, canvas.winfo_width())
            h = max(1, canvas.winfo_height())
            padding = 18
            cell = max(10, min((w - 2 * padding) // cols, (h - 2 * padding) // rows))
            x0 = (w - cell * cols) // 2
            y0 = (h - cell * rows) // 2
            c = (event.x - x0) // cell
            r = (event.y - y0) // cell
            if 0 <= r < rows and 0 <= c < cols:
                return int(r), int(c)
            return None

        def on_click(event):
            rc = cell_from_event(event)
            if rc is None:
                return
            r, c = rc
            m = mode.get()
            if m == "Wall":
                if (r, c) not in (editor_grid.start, editor_grid.goal):
                    editor_grid.walls.add((r, c))
            elif m == "Erase":
                editor_grid.walls.discard((r, c))
            elif m == "Start":
                if (r, c) not in editor_grid.walls and (r, c) != editor_grid.goal:
                    editor_grid.start = (r, c)
            elif m == "Goal":
                if (r, c) not in editor_grid.walls and (r, c) != editor_grid.start:
                    editor_grid.goal = (r, c)
            draw()

        def save_json():
            path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
            if not path:
                return
            data = {
                "rows": editor_grid.rows,
                "cols": editor_grid.cols,
                "start": list(editor_grid.start),
                "goal": list(editor_grid.goal),
                "walls": [list(x) for x in sorted(editor_grid.walls)],
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Save", f"Saved: {path}")

        def load_json():
            path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
            if not path:
                return
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            editor_grid.rows = int(data["rows"])
            editor_grid.cols = int(data["cols"])
            editor_grid.start = tuple(data["start"])
            editor_grid.goal = tuple(data["goal"])
            editor_grid.walls = set(tuple(w) for w in data.get("walls", []))
            draw()

        def apply_to_sim():
            self._cancel_animation()
            self._expanded_set = set()
            self.selected_map_name.set("(Custom)")
            self.maps["(Custom)"] = lambda: self._copy_grid(editor_grid)
            self.grid_obj = self._copy_grid(editor_grid)
            self.last_path = None
            self._set_metrics("Custom map loaded from editor.\n")
            self.status_var.set("Custom map loaded")
            self._draw()
            win.destroy()

        canvas.bind("<Button-1>", on_click)
        canvas.bind("<B1-Motion>", on_click)
        canvas.bind("<Configure>", lambda _e: draw())
        draw()

    def _draw(self):
        if self.grid_obj is None:
            return

        self.canvas.delete("all")

        rows = self.grid_obj.rows
        cols = self.grid_obj.cols

        w = max(1, self.canvas.winfo_width())
        h = max(1, self.canvas.winfo_height())

        padding = 18
        cell_size = max(10, min((w - 2 * padding) // cols, (h - 2 * padding) // rows))

        total_w = cell_size * cols
        total_h = cell_size * rows

        x0 = (w - total_w) // 2
        y0 = (h - total_h) // 2

        path_set = set(self.last_path) if self.last_path else set()

        for r in range(rows):
            for c in range(cols):
                x1 = x0 + c * cell_size
                y1 = y0 + r * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                if (r, c) in self.grid_obj.walls:
                    fill = "#334155"
                else:
                    fill = "#e2e8f0"

                if (
                    (r, c) in self._expanded_set
                    and (r, c) not in self.grid_obj.walls
                    and (r, c) not in (self.grid_obj.start, self.grid_obj.goal)
                ):
                    fill = "#fbbf24"

                if (r, c) in path_set and (r, c) != self.grid_obj.start and (r, c) != self.grid_obj.goal:
                    fill = "#38bdf8"

                if (r, c) == self.grid_obj.start:
                    fill = "#22c55e"
                elif (r, c) == self.grid_obj.goal:
                    fill = "#ef4444"

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=fill,
                    outline="#0f172a",
                    width=2,
                )

                # Optional labels for small grids
                if rows <= 10 and cols <= 10:
                    if (r, c) == self.grid_obj.start:
                        self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text="S", fill="#0f172a")
                    elif (r, c) == self.grid_obj.goal:
                        self.canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text="G", fill="#0f172a")


if __name__ == "__main__":
    app = PathfindingGUI()
    app.mainloop()
