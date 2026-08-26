"""
Role A (orbit/visibility).

Given a TLE and a list of ground targets (data/targets.csv), propagate the
satellite's position over config.HORIZON_START..HORIZON_END using Skyfield
and compute visibility windows per target: the (start_time, end_time)
intervals during which elevation >= config.MIN_ELEVATION_DEG.

TODO:
- Load TLE lines (via orbit.fetch_tles) and build a Skyfield EarthSatellite
- Load targets from config.TARGETS_CSV (name, lat, lon, weight)
- Step through the horizon at some fixed resolution (e.g. 1s or 10s) and
  compute topocentric elevation of each target as seen from the satellite's
  ground track (or equivalently, use Skyfield's built-in `find_events` for
  rise/culminate/set)
- Group timestamps into contiguous windows above MIN_ELEVATION_DEG
- Return a list of dicts, one per visibility window:
    {"target": name, "start": t_start, "end": t_end, "weight": weight}
  This is the "requests" list that feeds scheduling/conflict_graph.py

NOTE: Role B should not block on this — use
scripts/run_pipeline.py::load_requests_stub() for fake data in the meantime.
"""

import config


def load_targets(csv_path: str = None) -> list[dict]:
    """Load targets.csv into a list of {name, lat, lon, weight} dicts."""
    path = csv_path or config.TARGETS_CSV
    raise NotImplementedError


def compute_visibility_windows(norad_id: int, targets: list[dict]) -> list[dict]:
    """Compute visibility windows for each target against one satellite.

    Returns:
        List of {"target": str, "start": datetime, "end": datetime, "weight": float}
    """
    raise NotImplementedError


if __name__ == "__main__":
    targets = load_targets()
    windows = compute_visibility_windows(config.NORAD_IDS[0], targets)
    print(windows)
