"""
Generates a maze with A* pathfinding animation.
Shows the algorithm exploring, then finding the optimal path.
"""

import random
import hashlib
import heapq
import os
from datetime import datetime

# Configuration
CELL_SIZE = 12
MAZE_WIDTH = 41  # Must be odd
MAZE_HEIGHT = 21  # Must be odd
FRAME_DURATION = 0.05

# Colors
WALL_COLOR = "#30363d"
PATH_COLOR = "transparent"
EXPLORING_COLOR = "#8b949e"
SOLUTION_COLOR = "#58a6ff"
START_COLOR = "#3fb950"
END_COLOR = "#f85149"

def create_seed():
    """Deterministic seed based on date."""
    today = datetime.now().strftime("%Y-%m-%d")
    return int(hashlib.md5(today.encode()).hexdigest()[:8], 16)

def generate_maze(width, height):
    """Generate maze using recursive backtracking."""
    random.seed(create_seed())
    
    # Initialize with all walls
    maze = [[1 for _ in range(width)] for _ in range(height)]
    
    def carve(x, y):
        maze[y][x] = 0
        directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < width - 1 and 0 < ny < height - 1 and maze[ny][nx] == 1:
                maze[y + dy // 2][x + dx // 2] = 0
                carve(nx, ny)
    
    # Start from (1, 1)
    carve(1, 1)
    
    return maze

def heuristic(a, b):
    """Manhattan distance."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(maze, start, end):
    """A* pathfinding. Returns (exploration_order, final_path)."""
    height, width = len(maze), len(maze[0])
    
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}
    
    exploration_order = []
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        
        if current != start and current != end:
            exploration_order.append(current)
        
        if current == end:
            # Reconstruct path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return exploration_order, path
        
        x, y = current
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)
            
            if 0 <= nx < width and 0 <= ny < height and maze[ny][nx] == 0:
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, end)
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
    
    return exploration_order, []

def generate_svg(maze, exploration_order, path, start, end):
    """Generate animated SVG."""
    height, width = len(maze), len(maze[0])
    svg_width = width * CELL_SIZE
    svg_height = height * CELL_SIZE
    
    # Calculate timing
    explore_frames = len(exploration_order)
    path_frames = len(path)
    pause_frames = 20  # Pause at end before loop
    total_frames = explore_frames + path_frames + pause_frames
    total_duration = total_frames * FRAME_DURATION
    
    svg_parts = [
        f'<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">',
    ]
    
    # Draw maze walls (static)
    for y in range(height):
        for x in range(width):
            if maze[y][x] == 1:
                px, py = x * CELL_SIZE, y * CELL_SIZE
                svg_parts.append(
                    f'  <rect x="{px}" y="{py}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="{WALL_COLOR}"/>'
                )
    
    # Draw exploration animation
    for i, (x, y) in enumerate(exploration_order):
        px, py = x * CELL_SIZE, y * CELL_SIZE
        
        # Calculate when this cell appears (as fraction of total duration)
        appear_time = (i / total_frames)
        fade_time = ((explore_frames + path_frames) / total_frames)
        
        # Keyframes: invisible -> appear -> stay -> fade for loop
        svg_parts.append(
            f'  <rect x="{px + 2}" y="{py + 2}" width="{CELL_SIZE - 4}" height="{CELL_SIZE - 4}" '
            f'rx="2" fill="{EXPLORING_COLOR}" opacity="0">'
        )
        svg_parts.append(
            f'    <animate attributeName="opacity" '
            f'values="0;0;0.6;0.6;0.3;0" '
            f'keyTimes="0;{appear_time:.3f};{appear_time + 0.01:.3f};{fade_time:.3f};{fade_time + 0.05:.3f};1" '
            f'dur="{total_duration}s" repeatCount="indefinite"/>'
        )
        svg_parts.append('  </rect>')
    
    # Draw solution path animation
    for i, (x, y) in enumerate(path):
        if (x, y) == start or (x, y) == end:
            continue
            
        px, py = x * CELL_SIZE, y * CELL_SIZE
        
        # Path appears after exploration
        appear_time = ((explore_frames + i) / total_frames)
        stay_time = ((explore_frames + path_frames + pause_frames - 5) / total_frames)
        
        svg_parts.append(
            f'  <rect x="{px + 1}" y="{py + 1}" width="{CELL_SIZE - 2}" height="{CELL_SIZE - 2}" '
            f'rx="2" fill="{SOLUTION_COLOR}" opacity="0">'
        )
        svg_parts.append(
            f'    <animate attributeName="opacity" '
            f'values="0;0;1;1;0" '
            f'keyTimes="0;{appear_time:.3f};{appear_time + 0.01:.3f};{stay_time:.3f};1" '
            f'dur="{total_duration}s" repeatCount="indefinite"/>'
        )
        svg_parts.append('  </rect>')
    
    # Start point (always visible)
    sx, sy = start
    svg_parts.append(
        f'  <rect x="{sx * CELL_SIZE + 2}" y="{sy * CELL_SIZE + 2}" '
        f'width="{CELL_SIZE - 4}" height="{CELL_SIZE - 4}" rx="2" fill="{START_COLOR}"/>'
    )
    
    # End point (always visible)
    ex, ey = end
    svg_parts.append(
        f'  <rect x="{ex * CELL_SIZE + 2}" y="{ey * CELL_SIZE + 2}" '
        f'width="{CELL_SIZE - 4}" height="{CELL_SIZE - 4}" rx="2" fill="{END_COLOR}"/>'
    )
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)

def main():
    print("Generating maze with A* pathfinding...")
    
    # Generate maze
    maze = generate_maze(MAZE_WIDTH, MAZE_HEIGHT)
    
    # Define start and end
    start = (1, 1)
    end = (MAZE_WIDTH - 2, MAZE_HEIGHT - 2)
    
    # Run A*
    exploration_order, path = astar(maze, start, end)
    
    print(f"Maze: {MAZE_WIDTH}x{MAZE_HEIGHT}")
    print(f"Explored {len(exploration_order)} cells")
    print(f"Path length: {len(path)}")
    
    # Generate SVG
    svg_content = generate_svg(maze, exploration_order, path, start, end)
    
    # Write output
    os.makedirs('dist', exist_ok=True)
    
    with open('dist/maze-pathfinding.svg', 'w') as f:
        f.write(svg_content)
    
    print(f"Generated maze-pathfinding.svg")

if __name__ == "__main__":
    main()

