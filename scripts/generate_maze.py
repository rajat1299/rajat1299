"""
Generates a circular/spiral maze with A* pathfinding animation.
Neon aesthetic with subtle glow trails.
"""

import random
import hashlib
import heapq
import os
import math
from datetime import datetime

# Configuration
RINGS = 8  # Number of concentric rings
SECTORS_BASE = 8  # Sectors in innermost ring (doubles as you go out)
CENTER_X = 200
CENTER_Y = 200
RING_WIDTH = 22
INNER_RADIUS = 25
FRAME_DURATION = 0.06

# Neon Colors (slightly muted glow)
BG_COLOR = "#0d1117"
WALL_COLOR = "#30363d"
EXPLORING_COLOR = "#00d4d4"  # Slightly muted cyan
SOLUTION_COLOR = "#f0f0f0"  # Soft white
START_COLOR = "#00cc77"  # Muted neon green
END_COLOR = "#ff6b6b"  # Neon coral

def create_seed():
    today = datetime.now().strftime("%Y-%m-%d")
    return int(hashlib.md5(today.encode()).hexdigest()[:8], 16)

class CircularMaze:
    def __init__(self, rings, base_sectors):
        random.seed(create_seed())
        self.rings = rings
        self.base_sectors = base_sectors
        
        # Each ring has a number of sectors (cells)
        # Inner rings have fewer sectors, outer rings have more
        self.sectors_per_ring = []
        for r in range(rings):
            # Double sectors every 2 rings for balanced look
            multiplier = 2 ** (r // 2)
            self.sectors_per_ring.append(base_sectors * multiplier)
        
        # Track which walls exist
        # radial_walls[ring][sector] = True means wall between sector and sector+1
        # ring_walls[ring][sector] = True means wall between ring and ring+1 at that sector
        self.radial_walls = []
        self.ring_walls = []
        
        for r in range(rings):
            num_sectors = self.sectors_per_ring[r]
            self.radial_walls.append([True] * num_sectors)
            self.ring_walls.append([True] * num_sectors)
        
        self._generate()
    
    def _get_neighbors(self, ring, sector):
        """Get neighboring cells."""
        neighbors = []
        num_sectors = self.sectors_per_ring[ring]
        
        # Same ring, adjacent sectors
        prev_sector = (sector - 1) % num_sectors
        next_sector = (sector + 1) % num_sectors
        neighbors.append((ring, prev_sector, 'radial', prev_sector))
        neighbors.append((ring, next_sector, 'radial', sector))
        
        # Inner ring
        if ring > 0:
            inner_sectors = self.sectors_per_ring[ring - 1]
            inner_sector = (sector * inner_sectors) // num_sectors
            neighbors.append((ring - 1, inner_sector, 'ring', ring - 1))
        
        # Outer ring
        if ring < self.rings - 1:
            outer_sectors = self.sectors_per_ring[ring + 1]
            # Multiple outer sectors might connect
            start_outer = (sector * outer_sectors) // num_sectors
            end_outer = ((sector + 1) * outer_sectors) // num_sectors
            for os in range(start_outer, end_outer):
                neighbors.append((ring + 1, os % outer_sectors, 'ring', ring))
        
        return neighbors
    
    def _generate(self):
        """Generate maze using randomized Prim's algorithm."""
        visited = set()
        walls = []
        
        # Start from center
        start_cell = (0, 0)
        visited.add(start_cell)
        
        # Add walls of starting cell
        for neighbor in self._get_neighbors(0, 0):
            walls.append((start_cell, neighbor[:2], neighbor[2], neighbor[3]))
        
        random.shuffle(walls)
        
        while walls:
            wall = walls.pop(random.randint(0, len(walls) - 1) if walls else 0)
            cell1, cell2, wall_type, wall_idx = wall
            
            if cell2 in visited:
                continue
            
            # Remove this wall
            r, s = cell2
            if wall_type == 'radial':
                self.radial_walls[r][wall_idx] = False
            else:
                inner_r = wall_idx
                # Find which sector in inner ring
                inner_sectors = self.sectors_per_ring[inner_r]
                outer_sectors = self.sectors_per_ring[inner_r + 1]
                if r == inner_r:
                    inner_sector = s
                else:
                    inner_sector = (s * inner_sectors) // outer_sectors
                self.ring_walls[inner_r][inner_sector] = False
            
            visited.add(cell2)
            
            # Add walls of new cell
            for neighbor in self._get_neighbors(r, s):
                if neighbor[:2] not in visited:
                    walls.append((cell2, neighbor[:2], neighbor[2], neighbor[3]))
    
    def get_cell_center(self, ring, sector):
        """Get the center point of a cell."""
        num_sectors = self.sectors_per_ring[ring]
        angle = (2 * math.pi * sector / num_sectors) + (math.pi / num_sectors)
        radius = INNER_RADIUS + (ring + 0.5) * RING_WIDTH
        x = CENTER_X + radius * math.cos(angle)
        y = CENTER_Y + radius * math.sin(angle)
        return (x, y)
    
    def get_graph(self):
        """Return adjacency list for pathfinding."""
        graph = {}
        
        for r in range(self.rings):
            num_sectors = self.sectors_per_ring[r]
            for s in range(num_sectors):
                cell = (r, s)
                graph[cell] = []
                
                # Check radial walls (same ring)
                prev_s = (s - 1) % num_sectors
                if not self.radial_walls[r][prev_s]:
                    graph[cell].append((r, prev_s))
                if not self.radial_walls[r][s]:
                    graph[cell].append((r, (s + 1) % num_sectors))
                
                # Check ring walls (between rings)
                if r > 0:
                    inner_sectors = self.sectors_per_ring[r - 1]
                    inner_s = (s * inner_sectors) // num_sectors
                    if not self.ring_walls[r - 1][inner_s]:
                        graph[cell].append((r - 1, inner_s))
                
                if r < self.rings - 1:
                    outer_sectors = self.sectors_per_ring[r + 1]
                    start_outer = (s * outer_sectors) // num_sectors
                    end_outer = ((s + 1) * outer_sectors) // num_sectors
                    for os in range(start_outer, end_outer):
                        outer_s = os % outer_sectors
                        if not self.ring_walls[r][s] or (start_outer != end_outer - 1):
                            # Check if this specific connection is open
                            inner_s_check = (outer_s * num_sectors) // outer_sectors
                            if inner_s_check == s and not self.ring_walls[r][s]:
                                graph[cell].append((r + 1, outer_s))
        
        return graph

def astar_circular(maze, start, end):
    """A* for circular maze."""
    graph = maze.get_graph()
    
    def heuristic(cell):
        c1 = maze.get_cell_center(*cell)
        c2 = maze.get_cell_center(*end)
        return math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
    
    open_set = []
    heapq.heappush(open_set, (0, start))
    
    came_from = {}
    g_score = {start: 0}
    
    exploration_order = []
    visited = set()
    
    while open_set:
        current = heapq.heappop(open_set)[1]
        
        if current in visited:
            continue
        visited.add(current)
        
        if current != start and current != end:
            exploration_order.append(current)
        
        if current == end:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return exploration_order, path
        
        for neighbor in graph.get(current, []):
            tentative_g = g_score[current] + 1
            
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + heuristic(neighbor)
                heapq.heappush(open_set, (f, neighbor))
    
    return exploration_order, []

def generate_svg(maze, exploration_order, path, start, end):
    svg_width = CENTER_X * 2
    svg_height = CENTER_Y * 2
    
    explore_frames = len(exploration_order)
    path_frames = len(path)
    pause_frames = 15
    total_frames = explore_frames + path_frames + pause_frames
    total_duration = total_frames * FRAME_DURATION
    
    svg_parts = [
        f'<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" xmlns="http://www.w3.org/2000/svg">',
        '  <defs>',
        '    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">',
        '      <feGaussianBlur stdDeviation="2" result="blur"/>',
        '      <feMerge>',
        '        <feMergeNode in="blur"/>',
        '        <feMergeNode in="SourceGraphic"/>',
        '      </feMerge>',
        '    </filter>',
        '    <filter id="glow-strong" x="-50%" y="-50%" width="200%" height="200%">',
        '      <feGaussianBlur stdDeviation="3" result="blur"/>',
        '      <feMerge>',
        '        <feMergeNode in="blur"/>',
        '        <feMergeNode in="blur"/>',
        '        <feMergeNode in="SourceGraphic"/>',
        '      </feMerge>',
        '    </filter>',
        '  </defs>',
        f'  <rect width="{svg_width}" height="{svg_height}" fill="{BG_COLOR}"/>',
    ]
    
    # Draw maze walls
    # Concentric ring walls
    for r in range(maze.rings):
        outer_radius = INNER_RADIUS + (r + 1) * RING_WIDTH
        svg_parts.append(
            f'  <circle cx="{CENTER_X}" cy="{CENTER_Y}" r="{outer_radius}" '
            f'fill="none" stroke="{WALL_COLOR}" stroke-width="2"/>'
        )
    
    # Inner circle
    svg_parts.append(
        f'  <circle cx="{CENTER_X}" cy="{CENTER_Y}" r="{INNER_RADIUS}" '
        f'fill="{BG_COLOR}" stroke="{WALL_COLOR}" stroke-width="2"/>'
    )
    
    # Radial walls
    for r in range(maze.rings):
        num_sectors = maze.sectors_per_ring[r]
        for s in range(num_sectors):
            if maze.radial_walls[r][s]:
                angle = 2 * math.pi * (s + 1) / num_sectors
                inner_r = INNER_RADIUS + r * RING_WIDTH
                outer_r = INNER_RADIUS + (r + 1) * RING_WIDTH
                x1 = CENTER_X + inner_r * math.cos(angle)
                y1 = CENTER_Y + inner_r * math.sin(angle)
                x2 = CENTER_X + outer_r * math.cos(angle)
                y2 = CENTER_Y + outer_r * math.sin(angle)
                svg_parts.append(
                    f'  <line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                    f'stroke="{WALL_COLOR}" stroke-width="2"/>'
                )
    
    # Draw exploration
    for i, (r, s) in enumerate(exploration_order):
        cx, cy = maze.get_cell_center(r, s)
        
        appear_time = i / total_frames
        fade_time = (explore_frames + path_frames) / total_frames
        
        svg_parts.append(
            f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{RING_WIDTH * 0.3}" '
            f'fill="{EXPLORING_COLOR}" filter="url(#glow)" opacity="0">'
        )
        svg_parts.append(
            f'    <animate attributeName="opacity" '
            f'values="0;0;0.6;0.6;0.15;0" '
            f'keyTimes="0;{appear_time:.4f};{appear_time + 0.01:.4f};{fade_time:.4f};{fade_time + 0.05:.4f};1" '
            f'dur="{total_duration}s" repeatCount="indefinite"/>'
        )
        svg_parts.append('  </circle>')
    
    # Draw solution path
    for i, (r, s) in enumerate(path):
        if (r, s) == start or (r, s) == end:
            continue
        
        cx, cy = maze.get_cell_center(r, s)
        
        appear_time = (explore_frames + i) / total_frames
        stay_time = (explore_frames + path_frames + pause_frames - 3) / total_frames
        
        svg_parts.append(
            f'  <circle cx="{cx:.1f}" cy="{cy:.1f}" r="{RING_WIDTH * 0.35}" '
            f'fill="{SOLUTION_COLOR}" filter="url(#glow-strong)" opacity="0">'
        )
        svg_parts.append(
            f'    <animate attributeName="opacity" '
            f'values="0;0;0.9;0.9;0" '
            f'keyTimes="0;{appear_time:.4f};{appear_time + 0.01:.4f};{stay_time:.4f};1" '
            f'dur="{total_duration}s" repeatCount="indefinite"/>'
        )
        svg_parts.append('  </circle>')
    
    # Start point (center)
    sx, sy = maze.get_cell_center(*start)
    svg_parts.append(
        f'  <circle cx="{sx:.1f}" cy="{sy:.1f}" r="{RING_WIDTH * 0.4}" '
        f'fill="{START_COLOR}" filter="url(#glow-strong)"/>'
    )
    
    # End point (outer edge)
    ex, ey = maze.get_cell_center(*end)
    svg_parts.append(
        f'  <circle cx="{ex:.1f}" cy="{ey:.1f}" r="{RING_WIDTH * 0.4}" '
        f'fill="{END_COLOR}" filter="url(#glow-strong)"/>'
    )
    
    svg_parts.append('</svg>')
    
    return '\n'.join(svg_parts)

def main():
    print("Generating circular neon maze...")
    
    maze = CircularMaze(RINGS, SECTORS_BASE)
    
    # Start at center, end at outer edge
    start = (0, 0)
    end = (RINGS - 1, maze.sectors_per_ring[RINGS - 1] // 2)
    
    exploration_order, path = astar_circular(maze, start, end)
    
    print(f"Rings: {RINGS}, Base sectors: {SECTORS_BASE}")
    print(f"Explored {len(exploration_order)} cells")
    print(f"Path length: {len(path)}")
    
    svg_content = generate_svg(maze, exploration_order, path, start, end)
    
    os.makedirs('dist', exist_ok=True)
    
    with open('dist/circular-maze.svg', 'w') as f:
        f.write(svg_content)
    
    print("Generated circular maze with neon glow")

if __name__ == "__main__":
    main()
