from algorithms.algorithms import (
    run_astar,
    run_bfs,
    run_dfs,
    run_dijkstra,
    run_greedy,
)
from grid.grid import (
    create_simple_map,
    create_maze_map,
    create_no_path_map,
    create_comparison_map,
    create_greedy_trap_map,
    create_dfs_deep_trap_map,
    create_bridge_map_7x7,
    create_yassin_simple_3x3,
    create_yassin_maze_5x5,
    create_andrew_map_5x5,
)


def print_result(algorithm_name, path, cost, expanded, time_taken):
    print("\n" + "=" * 60)
    print(f"Algorithm: {algorithm_name}")
    print("=" * 60)

    if path is None:
        print("Result: NO PATH FOUND")
    else:
        print("Result: PATH FOUND")
        print(f"Path length (steps): {cost}")
        print(f"Path: {' -> '.join([str(p) for p in path])}")

    print(f"Expanded nodes: {expanded}")
    print(f"Execution time: {time_taken:.6f} seconds")
    print("=" * 60 + "\n")


def print_results_table_for_map(map_name, grid, algorithms):
    print("\n" + "-" * 60)
    print(f"Map: {map_name}")
    print("-" * 60)
    print("| Algorithm | Path Found | Path Length | Expanded Nodes | Time (s) |")
    print("|---|---:|---:|---:|---:|")

    for _, (algo_name, algo_func) in algorithms.items():
        path, cost, expanded, time_taken = algo_func(grid)
        path_found = "Yes" if path is not None else "No"
        print(f"| {algo_name} | {path_found} | {cost} | {expanded} | {time_taken:.6f} |")


def main():
    maps = {
        "1": ("Simple 5x5 (no obstacles)", create_simple_map),
        "2": ("Maze 10x10", create_maze_map),
        "3": ("No Path 5x5 (goal blocked)", create_no_path_map),
        "4": ("Comparison 8x8 (BFS vs DFS test)", create_comparison_map),
        "5": ("Yassin Simple 3x3", create_yassin_simple_3x3),
        "6": ("Yassin Maze 5x5", create_yassin_maze_5x5),
        "7": ("Andrew Comparison 5x5 (A* vs Greedy)", create_andrew_map_5x5),
        "8": ("Greedy Trap (A* vs Greedy)", create_greedy_trap_map),
        "9": ("DFS Deep Trap (BFS vs DFS)", create_dfs_deep_trap_map),
        "10": ("Bridge Map 7x7 (Optimal Path)", create_bridge_map_7x7),
    }

    algorithms = {
        "1": ("A* (Adham)", run_astar),
        "2": ("Dijkstra (Yassin)", run_dijkstra),
        "3": ("Greedy Best-First (Andrew)", run_greedy),
        "4": ("BFS (Belal)", run_bfs),
        "5": ("DFS (Belal)", run_dfs),
    }

    print("\n" + "=" * 60)
    print("AI PATHFINDING SIMULATOR - PHASE 2")
    print("=" * 60 + "\n")

    print("Available Maps:")
    for key, (name, _) in maps.items():
        print(f"  {key}. {name}")
    print("  report. Print results table for all maps (copy/paste)")

    map_choice = input("\nSelect map (1-10): ").strip()
    if map_choice.lower() == "report":
        for _, (map_name, map_creator) in maps.items():
            grid = map_creator()
            print_results_table_for_map(map_name, grid, algorithms)
        return
    if map_choice not in maps:
        print("Invalid choice. Using Simple map.")
        map_choice = "1"

    map_name, map_creator = maps[map_choice]
    grid = map_creator()

    print(f"\nSelected Map: {map_name}")
    print("\nGrid Layout:")
    grid.display()

    print("Available Algorithms:")
    for key, (name, _) in algorithms.items():
        print(f"  {key}. {name}")

    algo_choice = input("\nSelect algorithm (1-5, or 'all' to run all): ").strip().lower()

    if algo_choice == "all":
        for _, (algo_name, algo_func) in algorithms.items():
            path, cost, expanded, time_taken = algo_func(grid)
            print_result(algo_name, path, cost, expanded, time_taken)
        return

    if algo_choice not in algorithms:
        print("Invalid choice. Running A* by default.")
        algo_choice = "1"

    algo_name, algo_func = algorithms[algo_choice]
    path, cost, expanded, time_taken = algo_func(grid)
    print_result(algo_name, path, cost, expanded, time_taken)


if __name__ == "__main__":
    main()
