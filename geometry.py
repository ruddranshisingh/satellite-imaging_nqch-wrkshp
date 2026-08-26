"""
Role A (orbit/visibility).

For each visibility window, compute the required off-nadir/roll angle at
closest approach (the point of minimum slant range / maximum elevation
within the window). This angle is what conflict_graph.py uses to compute
slew time between consecutive targets.

TODO:
- Given satellite position and target lat/lon at time t, compute the
  off-nadir angle geometrically (angle between the nadir vector and the
  vector from satellite to target)
- Find t* = argmax(elevation) within a visibility window (closest approach)
- Return required_angle_deg at t* for that window
- Reject windows where required_angle_deg > config.MAX_OFF_NADIR_DEG
"""

import config


def required_angle_deg(sat_position, target_lat: float, target_lon: float, t) -> float:
    """Off-nadir angle (degrees) required to point at (target_lat, target_lon)
    at time t, given the satellite's position at that time.
    """
    raise NotImplementedError


def angle_at_closest_approach(window: dict) -> float:
    """Given a visibility window dict (from visibility.py), find the
    off-nadir angle at the moment of closest approach / peak elevation.
    """
    raise NotImplementedError
