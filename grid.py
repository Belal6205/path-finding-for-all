"""
grid.py - Grid representation for pathfinding algorithms
Adham Sobhy (23-101003) - Team Leader
"""

class Grid:
    """2D grid for pathfinding with walls, empty cells, start, and goal"""
    
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.walls = set()
        self.start = None
        self.goal = None
    
    def set_wall(self, row, col):
        """Mark a cell as a wall (obstacle)"""
        self.walls.add((row, col))
    
    def set_start(self, row, col):
        """Set the start position"""
        self.start = (row, col)
    
    def set_goal(self, row, col):
        """Set the goal position"""
        self.goal = (row, col)
    
    def is_valid(self, row, col):
        """Check if a cell is within bounds and not a wall"""
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            return False
        if (row, col) in self.walls:
            return False
        return True
    
    def get_neighbors(self, row, col):
        """Get valid neighbors (up, down, left, right)"""
        neighbors = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if self.is_valid(new_row, new_col):
                neighbors.append((new_row, new_col))
        
        return neighbors
    
    def display(self):
        """Print the grid (for debugging)"""
        for r in range(self.rows):
            row_str = ""
            for c in range(self.cols):
                if (r, c) == self.start:
                    row_str += "S "
                elif (r, c) == self.goal:
                    row_str += "G "
                elif (r, c) in self.walls:
                    row_str += "# "
                else:
                    row_str += ". "
            print(row_str)
        print()


# =========================
# TEST MAPS (for Phase 2)
# =========================

def create_simple_map():
    """Simple 5x5 grid with no obstacles"""
    grid = Grid(5, 5)
    grid.set_start(0, 0)
    grid.set_goal(4, 4)
    return grid


def create_maze_map():
    """10x10 grid with walls forming a maze"""
    grid = Grid(10, 10)
    grid.set_start(0, 0)
    grid.set_goal(9, 9)
    
    # Add walls to create a maze
    walls = [
        (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7),
        (3, 1), (3, 3), (3, 5), (3, 7), (3, 9),
        (5, 1), (5, 2), (5, 3), (5, 5), (5, 6), (5, 7), (5, 8),
        (7, 3), (7, 5), (7, 7), (7, 9),
    ]
    for r, c in walls:
        grid.set_wall(r, c)
    
    return grid


def create_greedy_trap_map():
    """Greedy Trap Map (7x7)"""
    grid = Grid(7, 7)
    grid.set_start(0, 0)
    grid.set_goal(6, 6)

    walls = [
        (1, 1), (2, 1), (3, 1), (4, 1),
        (1, 3), (2, 3), (3, 3), (4, 3),
        (4, 4), (4, 5),
        (5, 5),
    ]
    for r, c in walls:
        grid.set_wall(r, c)

    return grid


def create_dfs_deep_trap_map():
    """DFS Deep Trap Map (8x8)"""
    grid = Grid(8, 8)
    grid.set_start(0, 0)
    grid.set_goal(7, 7)

    walls = [
        (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1),
        (5, 2), (5, 3), (5, 4), (5, 5),
        (4, 5), (3, 5), (2, 5), (1, 5),
        (1, 3), (2, 3), (3, 3),
    ]
    for r, c in walls:
        grid.set_wall(r, c)

    return grid


def create_bridge_map_7x7():
    """Bridge Map (7x7)"""
    grid = Grid(7, 7)
    grid.set_start(3, 0)
    grid.set_goal(3, 6)

    for r in range(7):
        if r != 0:
            grid.set_wall(r, 3)

    return grid


def create_yassin_simple_3x3():
    """Yassin Test Map 1 – Simple Map (3×3)"""
    grid = Grid(3, 3)
    grid.set_start(0, 0)
    grid.set_goal(2, 2)

    grid.set_wall(1, 0)
    grid.set_wall(1, 1)

    return grid


def create_yassin_maze_5x5():
    """Yassin Test Map 2 – Maze Map (5×5)"""
    grid = Grid(5, 5)
    grid.set_start(0, 0)
    grid.set_goal(4, 4)

    walls = [
        (0, 1),
        (1, 1), (1, 3),
        (2, 3),
        (3, 0), (3, 1),
        (4, 3),
    ]
    for r, c in walls:
        grid.set_wall(r, c)

    return grid


def create_andrew_map_5x5():
    """Andrew Test Map – 5x5 comparison map for A* vs Greedy"""
    grid = Grid(5, 5)
    grid.set_start(0, 0)
    grid.set_goal(4, 4)

    # From Andrew's comparison grid (1 = wall)
    walls = [
        (1, 0), (1, 1), (1, 2), (1, 3),
        (2, 3),
        (3, 1), (3, 3),
        (4, 1), (4, 3),
    ]
    for r, c in walls:
        grid.set_wall(r, c)

    return grid


def create_no_path_map():
    """5x5 grid where goal is completely blocked"""
    grid = Grid(5, 5)
    grid.set_start(0, 0)
    grid.set_goal(4, 4)
    
    # Block the goal completely
    walls = [(3, 3), (3, 4), (4, 3)]
    for r, c in walls:
        grid.set_wall(r, c)
    
    return grid


def create_comparison_map():
    """Map where BFS is clearly better than DFS"""
    grid = Grid(8, 8)
    grid.set_start(0, 0)
    grid.set_goal(7, 7)
    
    # Create a pattern that makes DFS go deep
    walls = [
        (1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5),
        (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7),
        (5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5),
    ]
    for r, c in walls:
        grid.set_wall(r, c)
    
    return grid


# Test the grid
if __name__ == "__main__":
    print("Simple Map:")
    create_simple_map().display()
    
    print("Maze Map:")
    create_maze_map().display()
    
    print("No Path Map:")
    create_no_path_map().display()
    
    print("Comparison Map:")
    create_comparison_map().display()

    print("Yassin Simple 3x3:")
    create_yassin_simple_3x3().display()

    print("Yassin Maze 5x5:")
    create_yassin_maze_5x5().display()
