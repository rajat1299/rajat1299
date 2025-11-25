"""
Generates a minimal Game of Life SVG animation.
Starts with initials "RT" that evolve and transform.
Runs via GitHub Actions, outputs to dist/game-of-life.svg
"""

import os

# Configuration
CELL_SIZE = 6
GENERATIONS = 80
FRAME_DURATION = 0.12  # seconds per frame

# Colors - minimal, Apple-esque
CELL_COLOR = "#8b949e"
CELL_COLOR_BRIGHT = "#c9d1d9"

# Pixel art letters - each letter is 7 rows tall
# 1 = alive, 0 = dead

LETTER_R = [
    [1,1,1,1,0],
    [1,0,0,0,1],
    [1,0,0,0,1],
    [1,1,1,1,0],
    [1,0,0,1,0],
    [1,0,0,0,1],
    [1,0,0,0,1],
]

LETTER_T = [
    [1,1,1,1,1],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,0,1,0,0],
]

LETTER_A = [
    [0,0,1,0,0],
    [0,1,0,1,0],
    [1,0,0,0,1],
    [1,1,1,1,1],
    [1,0,0,0,1],
    [1,0,0,0,1],
    [1,0,0,0,1],
]

LETTER_I = [
    [1,1,1,1,1],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [0,0,1,0,0],
    [1,1,1,1,1],
]

def place_letter(grid, letter, start_x, start_y):
    """Place a letter pattern onto the grid."""
    for row_idx, row in enumerate(letter):
        for col_idx, cell in enumerate(row):
            y = start_y + row_idx
            x = start_x + col_idx
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                grid[y][x] = bool(cell)

def create_initial_grid():
    """Create grid with 'RT' initials centered."""
    # Calculate grid size to fit letters nicely
    letter_height = 7
    letter_width = 5
    spacing = 3
    
    # "RT" = 2 letters
    total_letter_width = (letter_width * 2) + spacing
    
    # Add padding around letters
    padding_x = 25
    padding_y = 8
    
    grid_width = total_letter_width + (padding_x * 2)
    grid_height = letter_height + (padding_y * 2)
    
    # Create empty grid
    grid = [[False for _ in range(grid_width)] for _ in range(grid_height)]
    
    # Center the letters
    start_y = padding_y
    start_x = padding_x
    
    # Place R
    place_letter(grid, LETTER_R, start_x, start_y)
    
    # Place T (after R + spacing)
    place_letter(grid, LETTER_T, start_x + letter_width + spacing, start_y)
    
    return grid

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
                new_grid[y][x] = neighbors in [2, 3]
            else:
                new_grid[y][x] = neighbors == 3
    
    return new_grid

def generate_svg(generations_data, grid_width, grid_height):
    """Generate animated SVG from generation data."""
    width = grid_width * CELL_SIZE
    height = grid_height * CELL_SIZE
    total_duration = len(generations_data) * FRAME_DURATION
    
    svg_parts = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">',
    ]
    
    # Track all cells that are ever alive
    cell_frames = {}
    
    for frame_idx, grid in enumerate(generations_data):
        for y in range(grid_height):
            for x in range(grid_width):
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
        values = []
        for i in range(len(generations_data)):
            values.append("1" if i in frames else "0")
        values_str = ";".join(values)
        
        # Cells that appear in early frames (part of letters) are brighter
        is_initial = 0 in frames or 1 in frames or 2 in frames
        color = CELL_COLOR_BRIGHT if is_initial else CELL_COLOR
        
        svg_parts.append(
            f'  <rect x="{px + 1}" y="{py + 1}" width="{CELL_SIZE - 2}" height="{CELL_SIZE - 2}" '
            f'rx="1" fill="{color}" opacity="0">'
        )
        svg_parts.append(
            f'    <animate attributeName="opacity" values="{values_str}" '
            f'dur="{total_duration}s" repeatCount="indefinite" calcMode="discrete"/>'
        )
        svg_parts.append('  </rect>')
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)

def main():
    print("Generating Game of Life with 'RT' initials...")
    
    # Initialize with letters
    grid = create_initial_grid()
    grid_height = len(grid)
    grid_width = len(grid[0])
    
    print(f"Grid size: {grid_width}x{grid_height}")
    
    # Show initial pattern
    print("Initial pattern:")
    for row in grid:
        print("".join(["█" if cell else "·" for cell in row]))
    
    # Run simulation
    generations = [grid]
    for i in range(GENERATIONS - 1):
        grid = next_generation(grid)
        generations.append(grid)
    
    # Generate SVG
    svg_content = generate_svg(generations, grid_width, grid_height)
    
    # Write output
    os.makedirs('dist', exist_ok=True)
    
    with open('dist/game-of-life.svg', 'w') as f:
        f.write(svg_content)
    
    print(f"\nGenerated game-of-life.svg")
    print(f"Frames: {GENERATIONS}, Duration: {GENERATIONS * FRAME_DURATION}s")

if __name__ == "__main__":
    main()
