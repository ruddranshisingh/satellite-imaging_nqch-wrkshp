"""
Conflict graph construction for the Agile Earth-Observation Satellite
Scheduling Problem (AEOS-SP).

Two candidate imaging requests conflict -- and therefore cannot both be
scheduled -- if either:
  (a) their visibility windows overlap in time, or
  (b) the gap between their windows is shorter than the camera slew time
      needed to swing from one target's required angle to the other's.

This module turns a list of candidate requests into a networkx.Graph whose
nodes carry the request's priority weight and whose edges are exactly the
conflict set E used in the QUBO objective:

    H = - sum_i w_i x_i + lambda * sum_{(i,j) in E} x_i x_j
"""
from dataclasses import dataclass

import networkx as nx


@dataclass(frozen=True)
class Request:
    """One candidate imaging request.

    id: unique identifier (str or int) -- becomes the graph node label.
    weight: priority weight w_i > 0 (higher = more critical, e.g. disaster
        response vs. routine farmland monitoring).
    start / end: visibility window (seconds since epoch, or any consistent
        time unit) during which the target is capturable.
    angle: required off-nadir / roll angle (degrees) at closest approach,
        used to compute slew time between consecutive acquisitions.
    """

    id: str
    weight: float
    start: float
    end: float
    angle: float

    def __post_init__(self):
        if self.weight <= 0:
            raise ValueError(f"Request {self.id}: weight must be > 0, got {self.weight}")
        if self.end < self.start:
            raise ValueError(f"Request {self.id}: end ({self.end}) < start ({self.start})")


def windows_overlap(a: Request, b: Request) -> bool:
    """True if a and b's visibility windows overlap in time."""
    return a.start < b.end and b.start < a.end


def slew_time(a: Request, b: Request, slew_rate_deg_per_sec: float) -> float:
    """Time (same unit as start/end) needed to swing the camera from a's
    required angle to b's required angle."""
    if slew_rate_deg_per_sec <= 0:
        raise ValueError("slew_rate_deg_per_sec must be > 0")
    return abs(a.angle - b.angle) / slew_rate_deg_per_sec


def gap_between(a: Request, b: Request) -> float:
    """Time gap between two non-overlapping windows (0 if they touch or
    overlap)."""
    if windows_overlap(a, b):
        return 0.0
    return b.start - a.end if a.end <= b.start else a.start - b.end


def conflicts(a: Request, b: Request, slew_rate_deg_per_sec: float) -> bool:
    """True if a and b cannot both be scheduled: overlapping windows, OR
    the gap between them is shorter than the slew time required to point
    from one target's angle to the other's."""
    if windows_overlap(a, b):
        return True
    return gap_between(a, b) < slew_time(a, b, slew_rate_deg_per_sec)


def build_conflict_graph(requests, slew_rate_deg_per_sec: float) -> nx.Graph:
    """Build the conflict graph G = (V, E) for a list of Requests.

    Each node i carries attribute 'weight' = w_i and 'request' = the
    original Request. Each edge (i, j) means requests i and j conflict --
    E is exactly the edge set consumed by qubo.build_qubo.

    O(N^2) pairwise check -- fine for the request counts (tens to low
    hundreds per pass) this problem deals with. Revisit with an interval
    tree / sweep-line if N grows large.
    """
    graph = nx.Graph()
    for r in requests:
        graph.add_node(r.id, weight=r.weight, request=r)

    for i, a in enumerate(requests):
        for b in requests[i + 1:]:
            if conflicts(a, b, slew_rate_deg_per_sec):
                graph.add_edge(a.id, b.id)
    return graph
