"""Role B: build conflict graph from requests."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import networkx as nx
import config


def conflicts(a, b):
    if a["start"] < b["end"] and b["start"] < a["end"]:
        return True
    gap = max(a["start"], b["start"]) - min(a["end"], b["end"])
    slew_time = abs(a["angle"] - b["angle"]) / config.SLEW_RATE_DEG_PER_SEC
    return gap < slew_time


def build_conflict_graph(requests):
    graph = nx.Graph()
    for r in requests:
        graph.add_node(r["id"], weight=r["weight"], target=r["target"])
    for i in range(len(requests)):
        for j in range(i + 1, len(requests)):
            if conflicts(requests[i], requests[j]):
                graph.add_edge(requests[i]["id"], requests[j]["id"])
    return graph