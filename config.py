"""
Central configuration for the AEOS-SP QUBO pipeline.
All tunable knobs live here so no module hardcodes constants.
"""

# --- Satellite identity ---
# NORAD catalog ID(s) for the satellite(s) being scheduled.
# Example: 25544 = ISS (useful for testing orbit propagation early).
NORAD_IDS = [25544]

# --- Planning horizon ---
# UTC ISO 8601 start/end of the scheduling window (single orbit pass to start).
from datetime import datetime, timedelta, timezone
_now = datetime.now(timezone.utc)
HORIZON_START = _now.strftime("%Y-%m-%dT%H:%M:%SZ")
HORIZON_END = (_now + timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%SZ")

# --- Visibility / geometry ---
MIN_ELEVATION_DEG = 10.0          # minimum elevation angle to count as "visible"
MAX_OFF_NADIR_DEG = 45.0          # max roll/off-nadir angle the camera can achieve

# --- Slew constraint ---
SLEW_RATE_DEG_PER_SEC = 1.0       # camera slew speed; used in conflict_graph.py

# --- QUBO penalty ---
# Must exceed max(w_i + w_j) over conflicting pairs; brief suggests 1.5-2x max(w).
LAMBDA_MULTIPLIER = 1.75

# --- Rescheduling (closed-loop stretch feature) ---
RESCHEDULE_DEVIATION_PENALTY = 0.5  # weight on penalizing deviation from prior schedule

# --- Paths ---
DATA_DIR = "data"
TARGETS_CSV = "data/targets.csv"
TLE_CACHE_DIR = "data/tles"
OUTPUTS_DIR = "outputs"
