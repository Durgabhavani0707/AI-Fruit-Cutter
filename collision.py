"""
collision.py

Contains math helpers to detect line segment to circle collisions.
Used to detect if the finger trail intersects a fruit.
"""
import math

def point_distance(p1, p2):
    """Calculates Euclidean distance between two points."""
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def line_intersects_circle(p1, p2, circle_center, circle_radius, line_thickness=30):
    """
    Checks if a line segment between p1 and p2 intersects a circle.
    Expands the circle radius by line_thickness to act as a generous slicing hitbox,
    preventing missed slices during very fast hand movements.
    
    p1, p2: (x, y) tuples
    circle_center: (x, y) tuple
    circle_radius: float
    line_thickness: float (buffer added to radius for better UX)
    """
    effective_radius = circle_radius + line_thickness
    
    # Vector from p1 to p2
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    
    # Vector from p1 to circle center
    cx, cy = circle_center[0] - p1[0], circle_center[1] - p1[1]
    
    line_length_sq = dx * dx + dy * dy
    if line_length_sq == 0:
        # p1 and p2 are the same point, just check point to circle distance
        return point_distance(p1, circle_center) <= effective_radius

    # Project c onto the line segment to find the closest point
    t = (cx * dx + cy * dy) / line_length_sq
    
    # Clamp t to [0, 1] to limit it to the line segment
    t = max(0, min(1, t))
    
    closest_x = p1[0] + t * dx
    closest_y = p1[1] + t * dy
    
    # Check if the closest point is within the effective circle radius
    return point_distance((closest_x, closest_y), circle_center) <= effective_radius
