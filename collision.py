"""
collision.py

Math helpers for detecting whether the AI-controlled
finger movement intersects a fruit.

Used by the Fruit Cutter game to detect slicing.
"""

import math


# ============================================================
# POINT DISTANCE
# ============================================================

def point_distance(p1, p2):
    """
    Calculate Euclidean distance between two points.

    Parameters
    ----------
    p1 : tuple
        First point (x, y)

    p2 : tuple
        Second point (x, y)

    Returns
    -------
    float
        Distance between the two points.
    """

    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    return math.hypot(dx, dy)


# ============================================================
# POINT TO CIRCLE
# ============================================================

def point_inside_circle(
    point,
    circle_center,
    circle_radius
):
    """
    Check whether a point is inside a circle.
    """

    dx = (
        point[0]
        - circle_center[0]
    )

    dy = (
        point[1]
        - circle_center[1]
    )

    return (
        dx * dx + dy * dy
        <= circle_radius * circle_radius
    )


# ============================================================
# LINE SEGMENT -> CIRCLE
# ============================================================

def line_intersects_circle(
    p1,
    p2,
    circle_center,
    circle_radius,
    line_thickness=30
):
    """
    Detect whether a line segment intersects a circle.

    The finger movement from p1 -> p2 is treated as
    a slicing line.

    A small extra radius is added to make slicing
    responsive even during fast hand movement.

    Parameters
    ----------
    p1 : tuple
        Previous finger position.

    p2 : tuple
        Current finger position.

    circle_center : tuple
        Fruit center.

    circle_radius : float
        Fruit radius.

    line_thickness : float
        Extra slicing buffer.

    Returns
    -------
    bool
        True if the finger movement intersects
        the fruit.
    """

    # --------------------------------------------------------
    # Validate input
    # --------------------------------------------------------

    if (
        p1 is None
        or p2 is None
        or circle_center is None
    ):
        return False

    try:

        radius = float(
            circle_radius
        )

        thickness = float(
            line_thickness
        )

    except (
        TypeError,
        ValueError
    ):

        return False

    # Invalid radius
    if radius < 0:
        return False

    # Prevent negative slicing buffer
    thickness = max(
        0.0,
        thickness
    )

    # --------------------------------------------------------
    # Effective fruit hitbox
    # --------------------------------------------------------

    effective_radius = (
        radius + thickness
    )

    # --------------------------------------------------------
    # Coordinates
    # --------------------------------------------------------

    x1 = float(p1[0])
    y1 = float(p1[1])

    x2 = float(p2[0])
    y2 = float(p2[1])

    cx = float(
        circle_center[0]
    )

    cy = float(
        circle_center[1]
    )

    # --------------------------------------------------------
    # Line vector
    # --------------------------------------------------------

    dx = x2 - x1
    dy = y2 - y1

    # --------------------------------------------------------
    # Special case:
    # No finger movement
    # --------------------------------------------------------

    line_length_sq = (
        dx * dx
        + dy * dy
    )

    if line_length_sq <= 1e-8:

        distance_x = (
            cx - x1
        )

        distance_y = (
            cy - y1
        )

        return (
            distance_x * distance_x
            + distance_y * distance_y
            <= effective_radius
            * effective_radius
        )

    # --------------------------------------------------------
    # Vector from p1 -> circle center
    # --------------------------------------------------------

    center_x = cx - x1
    center_y = cy - y1

    # --------------------------------------------------------
    # Project circle center onto line
    # --------------------------------------------------------

    t = (
        center_x * dx
        + center_y * dy
    ) / line_length_sq

    # Keep projection on the actual segment
    t = max(
        0.0,
        min(1.0, t)
    )

    # --------------------------------------------------------
    # Closest point on line segment
    # --------------------------------------------------------

    closest_x = (
        x1 + t * dx
    )

    closest_y = (
        y1 + t * dy
    )

    # --------------------------------------------------------
    # Distance from closest point
    # to fruit center
    # --------------------------------------------------------

    distance_x = (
        cx - closest_x
    )

    distance_y = (
        cy - closest_y
    )

    distance_sq = (
        distance_x * distance_x
        + distance_y * distance_y
    )

    # --------------------------------------------------------
    # Collision
    # --------------------------------------------------------

    return (
        distance_sq
        <= effective_radius
        * effective_radius
    )


# ============================================================
# FAST SLICE DETECTION
# ============================================================

def fast_line_intersects_circle(
    p1,
    p2,
    circle_center,
    circle_radius,
    min_buffer=25,
    max_buffer=55
):
    """
    Dynamic collision detection for fast finger movements.

    Faster finger movement gets a slightly larger
    hitbox, helping prevent missed slices.

    This function is optional. Your current game.py
    can continue using line_intersects_circle().
    """

    if p1 is None or p2 is None:
        return False

    # Calculate finger movement
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    movement_speed = math.hypot(
        dx,
        dy
    )

    # --------------------------------------------------------
    # Dynamic buffer
    # --------------------------------------------------------

    # 0 movement -> min_buffer
    # 50+ pixels -> max_buffer

    speed_factor = min(
        1.0,
        movement_speed / 50.0
    )

    dynamic_buffer = (
        min_buffer
        + (
            max_buffer
            - min_buffer
        )
        * speed_factor
    )

    return line_intersects_circle(
        p1,
        p2,
        circle_center,
        circle_radius,
        dynamic_buffer
    )


# ============================================================
# CIRCLE OVERLAP
# ============================================================

def circles_intersect(
    center1,
    radius1,
    center2,
    radius2
):
    """
    Check whether two circles overlap.
    """

    dx = (
        center2[0]
        - center1[0]
    )

    dy = (
        center2[1]
        - center1[1]
    )

    combined_radius = (
        radius1 + radius2
    )

    return (
        dx * dx
        + dy * dy
        <= combined_radius
        * combined_radius
    )