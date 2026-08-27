"""Role A: compute real visibility windows + off-nadir angle using Skyfield."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import csv
import math
from datetime import datetime, timedelta, timezone
from skyfield.api import load, wgs84, EarthSatellite
import config


def load_targets(csv_path=None):
    path = csv_path or config.TARGETS_CSV
    targets = []
    with open(path) as f:
        for row in csv.DictReader(f):
            targets.append({
                "name": row["name"],
                "lat": float(row["lat"]),
                "lon": float(row["lon"]),
                "weight": float(row["weight"]),
            })
    return targets


def compute_visibility_windows(norad_id, tle_lines, targets, step_seconds=30):
    ts = load.timescale()
    satellite = EarthSatellite(tle_lines[0], tle_lines[1], "SAT", ts)

    start = datetime.fromisoformat(config.HORIZON_START.replace("Z", "+00:00"))
    end = datetime.fromisoformat(config.HORIZON_END.replace("Z", "+00:00"))
    total_seconds = int((end - start).total_seconds())
    steps = range(0, total_seconds, step_seconds)

    windows = []
    req_id = 0

    for target in targets:
        observer = wgs84.latlon(target["lat"], target["lon"])
        difference = satellite - observer

        in_window = False
        window_start = None
        best_elev = -90
        best_angle = 0

        for s in steps:
            t = ts.from_datetime(start + timedelta(seconds=s))
            alt, az, distance = difference.at(t).altaz()
            elev = alt.degrees

            if elev >= config.MIN_ELEVATION_DEG:
                if not in_window:
                    in_window = True
                    window_start = s
                    best_elev = elev
                if elev > best_elev or window_start == s:
                    best_elev = elev
                    subpoint = satellite.at(t).subpoint()
                    h = subpoint.elevation.km
                    re = 6371.0
                    cos_el = math.cos(math.radians(elev))
                    ratio = (re / (re + h)) * cos_el
                    ratio = max(-1.0, min(1.0, ratio))
                    best_angle = math.degrees(math.asin(ratio))
            else:
                if in_window:
                    windows.append({
                        "id": req_id, "target": target["name"],
                        "start": window_start, "end": s,
                        "angle": best_angle, "weight": target["weight"],
                    })
                    req_id += 1
                    in_window = False

        if in_window:
            windows.append({
                "id": req_id, "target": target["name"],
                "start": window_start, "end": total_seconds,
                "angle": best_angle, "weight": target["weight"],
            })
            req_id += 1

    return windows


if __name__ == "__main__":
    from fetch_tles import fetch_tle
    tle = fetch_tle(config.NORAD_IDS[0])
    targets = load_targets()
    windows = compute_visibility_windows(config.NORAD_IDS[0], tle, targets)
    for w in windows:
        print(w)