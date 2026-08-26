"""
Role B (scheduling).

Build the conflict graph over candidate observation requests. Two requests
(i, j) conflict (get an edge) if either:
  1. Their visibility windows overlap in time, OR
  2. The gap between windows is smaller than the slew time required to move
     the camera between their off-nadir angles:
         slew_time = |angle_i - angle_j| / config.SLEW_RATE_DEG_PER_SEC

TODO:
- Take the list of requests (each with start, end, angle, weight) from
  orbit.visibility / orbit.geometry (or load_requests_stub() while Role A
  is still in progress)
- Build a networkx.Graph with one node per request
- For every pair, check the two conflict conditions above and add an edge
  if either holds
- Return the graph (nodes carry weight as a node attribute for qubo.py)
"""

import networkx as nx
import config


def build_conflict_graph(requests: list[dict]) -> nx.Graph:
    """Build the conflict graph.

    Args:
        requests: list of dicts, each with keys
            {"id": int, "target": str, "start": float, "end": float,
             "angle": float, "weight": float}
            (start/end as seconds-from-horizon-start floats keeps the slew
            math simple)

    Returns:
        networkx.Graph with node attribute "weight" and an edge between
        every conflicting pair of requests.
    """
    raise NotImplementedError


def conflicts(req_i: dict, req_j: dict) -> bool:
    """True if req_i and req_j cannot both be scheduled (overlap or slew
    time between them exceeds the available gap)."""
    raise NotImplementedError
