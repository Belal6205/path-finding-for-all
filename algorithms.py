
"""
algorithms.py - Pathfinding algorithms
Adham Sobhy (23-101003) - A* implementation
Team members will add their algorithms here
"""

import heapq
import time

from heuristics import manhattan


def manhattan_distance(pos1, pos2):
    """Manhattan distance heuristic"""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def run_astar(grid, start=None, goal=None, trace=False):
    """
    A* pathfinding algorithm
    
    Returns: (path, cost, expanded_nodes, time_taken)
    - path: list of (row, col) tuples from start to goal, or None
    - cost: total path length (number of steps)
    - expanded_nodes: number of nodes explored
    - time_taken: execution time in seconds
    """
    start_time = time.time()
    
    if start is None:
        start = grid.start
    if goal is None:
        goal = grid.goal
    
    # Priority queue: (f_score, counter, current_pos, path, g_score)
    counter = 0
    open_set = [(0, counter, start, [start], 0)]
    closed_set = set()
    expanded_nodes = 0
    expanded_order = []
    
    while open_set:
        f_score, _, current, path, g_score = heapq.heappop(open_set)
        
        if current in closed_set:
            continue
        
        closed_set.add(current)
        expanded_nodes += 1
        if trace:
            expanded_order.append(current)
        
        # Check if goal reached
        if current == goal:
            time_taken = time.time() - start_time
            if trace:
                return path, len(path) - 1, expanded_nodes, time_taken, expanded_order
            return path, len(path) - 1, expanded_nodes, time_taken
        
        # Explore neighbors
        for neighbor in grid.get_neighbors(current[0], current[1]):
            if neighbor in closed_set:
                continue
            
            new_g = g_score + 1
            h = manhattan_distance(neighbor, goal)
            f = new_g + h
            
            counter += 1
            heapq.heappush(open_set, (f, counter, neighbor, path + [neighbor], new_g))
    
    # No path found
    time_taken = time.time() - start_time
    if trace:
        return None, 0, expanded_nodes, time_taken, expanded_order
    return None, 0, expanded_nodes, time_taken


# =========================
# TEAM ALGORITHMS (to be added by team members)
# =========================

def run_dijkstra(grid, start=None, goal=None, trace=False):
    """Yassin Farrag - Dijkstra implementation"""
    start_time = time.time()

    if start is None:
        start = grid.start
    if goal is None:
        goal = grid.goal

    pq = [(0, start)]  # (distance, node)
    dist = {start: 0}
    parent = {start: None}
    visited = set()
    expanded_nodes = 0
    expanded_order = []

    while pq:
        current_dist, current = heapq.heappop(pq)

        if current in visited:
            continue

        visited.add(current)
        expanded_nodes += 1
        if trace:
            expanded_order.append(current)

        if current == goal:
            path = []
            node = goal
            while node is not None:
                path.append(node)
                node = parent.get(node)
            path.reverse()
            time_taken = time.time() - start_time
            if trace:
                return path, len(path) - 1, expanded_nodes, time_taken, expanded_order
            return path, len(path) - 1, expanded_nodes, time_taken

        for neighbor in grid.get_neighbors(current[0], current[1]):
            if neighbor in visited:
                continue

            new_dist = current_dist + 1
            if new_dist < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_dist
                parent[neighbor] = current
                heapq.heappush(pq, (new_dist, neighbor))

    time_taken = time.time() - start_time
    if trace:
        return None, 0, expanded_nodes, time_taken, expanded_order
    return None, 0, expanded_nodes, time_taken


def run_greedy(grid, start=None, goal=None, heuristic=None, trace=False):
    """Andrew Emad - Greedy Best-First implementation

    Uses only h(n) to choose which node to expand (no g(n)).
    The heuristic parameter allows selecting Manhattan (default) or Euclidean.
    """
    start_time = time.time()

    if start is None:
        start = grid.start
    if goal is None:
        goal = grid.goal

    # Default heuristic is Manhattan
    if heuristic is None:
        heuristic = manhattan

    if start == goal:
        time_taken = time.time() - start_time
        if trace:
            return [start], 0, 0, time_taken, []
        return [start], 0, 0, time_taken

    # Greedy Best-First Search: choose next node using h(n) only
    frontier = []  # (h, tie, node)
    tie = 0
    heapq.heappush(frontier, (heuristic(start, goal), tie, start))

    came_from = {start: None}
    visited = set()
    expanded_nodes = 0
    expanded_order = []

    while frontier:
        _, _, current = heapq.heappop(frontier)

        if current in visited:
            continue
        visited.add(current)
        expanded_nodes += 1
        if trace:
            expanded_order.append(current)

        if current == goal:
            path = []
            node = goal
            while node is not None:
                path.append(node)
                node = came_from.get(node)
            path.reverse()
            time_taken = time.time() - start_time
            if trace:
                return path, len(path) - 1, expanded_nodes, time_taken, expanded_order
            return path, len(path) - 1, expanded_nodes, time_taken

        for nxt in grid.get_neighbors(current[0], current[1]):
            if nxt in visited:
                continue
            if nxt not in came_from:
                came_from[nxt] = current
            tie += 1
            heapq.heappush(frontier, (heuristic(nxt, goal), tie, nxt))

    time_taken = time.time() - start_time
    if trace:
        return None, 0, expanded_nodes, time_taken, expanded_order
    return None, 0, expanded_nodes, time_taken


def run_bfs(grid, start=None, goal=None, trace=False):
    """Belal Mohamed - BFS implementation"""
    from collections import deque
    
    start_time = time.time()
    if start is None:
        start = grid.start
    if goal is None:
        goal = grid.goal
    
    visited = set()
    queue = deque([[start]])
    expanded_nodes = 0
    expanded_order = []

    while queue:
        path = queue.popleft()
        node = path[-1]
        
        if node in visited:
            continue
        
        visited.add(node)
        expanded_nodes += 1
        if trace:
            expanded_order.append(node)
        
        if node == goal:
            time_taken = time.time() - start_time
            if trace:
                return path, len(path) - 1, expanded_nodes, time_taken, expanded_order
            return path, len(path) - 1, expanded_nodes, time_taken
        
        for neighbor in grid.get_neighbors(node[0], node[1]):
            if neighbor not in visited:
                queue.append(path + [neighbor])
    
    time_taken = time.time() - start_time
    if trace:
        return None, 0, expanded_nodes, time_taken, expanded_order
    return None, 0, expanded_nodes, time_taken


def run_dfs(grid, start=None, goal=None, trace=False):
    """Belal Mohamed - DFS implementation"""
    start_time = time.time()
    if start is None:
        start = grid.start
    if goal is None:
        goal = grid.goal
    
    visited = set()
    stack = [[start]]
    expanded_nodes = 0
    expanded_order = []
    
    while stack:
        path = stack.pop()
        node = path[-1]
        
        if node in visited:
            continue
        
        visited.add(node)
        expanded_nodes += 1
        if trace:
            expanded_order.append(node)
        
        if node == goal:
            time_taken = time.time() - start_time
            if trace:
                return path, len(path) - 1, expanded_nodes, time_taken, expanded_order
            return path, len(path) - 1, expanded_nodes, time_taken
        
        neighbors = grid.get_neighbors(node[0], node[1])
        for neighbor in reversed(neighbors):
            if neighbor not in visited:
                stack.append(path + [neighbor])
    
    time_taken = time.time() - start_time
    if trace:
        return None, 0, expanded_nodes, time_taken, expanded_order
    return None, 0, expanded_nodes, time_taken


def run_bidirectional(grid, start=None, goal=None):
    """Yassin Farrag - Bidirectional Search implementation"""
    # TODO: Yassin will implement this
    return None, 0, 0, 0.0