"""
Generates a minimal Game of Life SVG animation.
Runs via GitHub Actions, outputs to dist/game-of-life.svg
"""

import random
import hashlib
from datetime import datetime

# Configuration
GRID_WIDTH = 60
GRID_HEIGHT = 20
CELL_SIZE = 8
GENERATIONS = 60
FRAME_DURATION = 0.15  # seconds per frame

# Colors - minimal, Apple-esque
CELL_COLOR = "#8b949e"  # GitHub gray
CELL_COLOR_ACCENT = "#c9d1d9"  # Lighter for variation

def create_seed():
    """Create a deterministic seed based on today's date."""
    today = datetime.now().strftime("%Y-%m-%d")
    return int(hashlib.md5(today.encode()).hexdigest()[:8], 16)

def initialize_grid(width, height, density=0.3):
    """Initialize grid with random cells."""
    random.seed(create_seed())
    return [[random.random() < density for _ in range(width)] for _ in range(height)]

def count_neighbors(grid, x, y):
    """Count live neighbors for a cell."""
    height, width = len(grid), len(grid[0])
    count = 0
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = (x + dx) % width, (y + dy) % height
            if grid[ny][nx]:
                count += 1
    return count

def next_generation(grid):
    """Compute next generation."""
    height, width = len(grid), len(grid[0])
    new_grid = [[False for _ in range(width)] for _ in range(height)]
    
    for y in range(height):
        for x in range(width):
            neighbors = count_neighbors(grid, x, y)
            if grid[y][x]:
                # Live cell survives with 2-3 neighbors
                new_grid[y][x] = neighbors in [2, 3]
            else:
                # Dead cell becomes alive with exactly 3 neighbors
                new_grid[y][x] = neighbors == 3
    
    return new_grid

def generate_svg(generations_data):
    """Generate animated SVG from generation data."""
    width = GRID_WIDTH * CELL_SIZE
    height = GRID_HEIGHT * CELL_SIZE
    total_duration = len(generations_data) * FRAME_DURATION
    
    svg_parts = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
        '  <defs>',
        '    <style>',
        '      .cell { fill: #8b949e; }',
        '      .cell-bright { fill: #c9d1d9; }',
        '    </style>',
        '  </defs>',
        f'  <rect width="{width}" height="{height}" fill="transparent"/>',
    ]
    
    # Track all cells that are ever alive and their frame visibility
    cell_frames = {}  # (x, y) -> list of frames where alive
    
    for frame_idx, grid in enumerate(generations_data):
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x]:
                    key = (x, y)
                    if key not in cell_frames:
                        cell_frames[key] = []
                    cell_frames[key].append(frame_idx)
    
    # Generate cells with visibility animations
    for (x, y), frames in cell_frames.items():
        px = x * CELL_SIZE
        py = y * CELL_SIZE
        
        # Create visibility keyframes
        # Each frame is FRAME_DURATION seconds
        # We need to create a values string like "0;0;1;1;0;0;1;..."
        values = []
        for i in range(len(generations_data)):
            values.append("1" if i in frames else "0")
        values_str = ";".join(values)
        
        # Determine if this is a "bright" cell (alive in many frames)
        brightness_class = "cell-bright" if len(frames) > len(generations_data) * 0.3 else "cell"
        
        svg_parts.append(
            f'  <rect x="{px + 1}" y="{py + 1}" width="{CELL_SIZE - 2}" height="{CELL_SIZE - 2}" '
            f'rx="1" class="{brightness_class}" opacity="0">'
        )
        svg_parts.append(
            f'    <animate attributeName="opacity" values="{values_str}" '
            f'dur="{total_duration}s" repeatCount="indefinite" calcMode="discrete"/>'
        )
        svg_parts.append('  </rect>')
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)

def main():
    print("Generating Game of Life...")
    
    # Initialize
    grid = initialize_grid(GRID_WIDTH, GRID_HEIGHT, density=0.35)
    
    # Run simulation
    generations = [grid]
    for _ in range(GENERATIONS - 1):
        grid = next_generation(grid)
        generations.append(grid)
    
    # Generate SVG
    svg_content = generate_svg(generations)
    
    # Write output
    import os
    os.makedirs('dist', exist_ok=True)
    
    with open('dist/game-of-life.svg', 'w') as f:
        f.write(svg_content)
    
    print(f"Generated game-of-life.svg with {GENERATIONS} frames")
    print(f"Grid: {GRID_WIDTH}x{GRID_HEIGHT}, Cell size: {CELL_SIZE}px")
    print(f"Animation duration: {GENERATIONS * FRAME_DURATION}s")

if __name__ == "__main__":
    main()

