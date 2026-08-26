"""
Role C (viz).

Plot the satellite's ground track (sub-satellite lat/lon path) over the
planning horizon, with target locations overlaid, using matplotlib.

TODO:
- Take the propagated positions from orbit.visibility (or recompute lat/lon
  from the TLE directly for the horizon)
- Plot lat/lon path as a line
- Overlay target markers from data/targets.csv, sized/colored by weight
- Save to f"{config.OUTPUTS_DIR}/ground_track.png"
"""

import config


def plot_ground_track(positions: list[tuple], targets: list[dict], out_path: str = None):
    """positions: list of (lat, lon) over time. targets: from
    orbit.visibility.load_targets()."""
    raise NotImplementedError
