"""
Role A (orbit/visibility).

Pull Two-Line Element (TLE) sets for the satellites in config.NORAD_IDS from
Celestrak, and cache them locally under config.TLE_CACHE_DIR so we don't
re-hit the network on every run.

TODO:
- Build the Celestrak query URL for a given NORAD ID
  (https://celestrak.org/NORAD/elements/gp.php?CATNR=<id>&FORMAT=TLE)
- Download and write the raw TLE text to
  f"{config.TLE_CACHE_DIR}/{norad_id}.tle"
- If a cached file already exists and is "fresh enough" (define a max age,
  e.g. 24h), skip the network call and just read the cache
- Return a dict: {norad_id: (line1, line2)}
"""

import config


def fetch_tle(norad_id: int) -> tuple[str, str]:
    """Fetch (and cache) the TLE lines for a single NORAD ID.

    Returns:
        (line1, line2) TLE strings.
    """
    raise NotImplementedError


def fetch_all_tles(norad_ids=None) -> dict:
    """Fetch TLEs for every satellite in config.NORAD_IDS (or the given list).

    Returns:
        Mapping of norad_id -> (line1, line2).
    """
    ids = norad_ids or config.NORAD_IDS
    raise NotImplementedError


if __name__ == "__main__":
    tles = fetch_all_tles()
    print(tles)
