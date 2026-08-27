"""
Role A (orbit/visibility).

Pull TLEs from Celestrak, cache them locally under config.TLE_CACHE_DIR.
"""

import sys
import os

# Let Python find config.py, which lives at the repo root, not in this folder
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import time
import requests
import config

CELESTRAK_URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR={norad_id}&FORMAT=TLE"
MAX_CACHE_AGE_SECONDS = 24 * 60 * 60  # 24 hours


def fetch_tle(norad_id: int) -> tuple[str, str]:
    """Fetch (and cache) the TLE lines for a single NORAD ID."""
    os.makedirs(config.TLE_CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(config.TLE_CACHE_DIR, f"{norad_id}.tle")

    if os.path.exists(cache_path):
        age = time.time() - os.path.getmtime(cache_path)
        if age < MAX_CACHE_AGE_SECONDS:
            with open(cache_path) as f:
                lines = f.read().strip().splitlines()
            return lines[-2], lines[-1]

    url = CELESTRAK_URL.format(norad_id=norad_id)
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    lines = response.text.strip().splitlines()
    if len(lines) < 2:
        raise ValueError(f"Unexpected TLE response for NORAD ID {norad_id}: {response.text!r}")
    line1, line2 = lines[-2], lines[-1]

    with open(cache_path, "w") as f:
        f.write(f"{line1}\n{line2}\n")

    return line1, line2


def fetch_all_tles(norad_ids=None) -> dict:
    """Fetch TLEs for every satellite in config.NORAD_IDS (or the given list)."""
    ids = norad_ids or config.NORAD_IDS
    return {norad_id: fetch_tle(norad_id) for norad_id in ids}


if __name__ == "__main__":
    tles = fetch_all_tles()
    for norad_id, (l1, l2) in tles.items():
        print(f"NORAD {norad_id}:\n{l1}\n{l2}\n")