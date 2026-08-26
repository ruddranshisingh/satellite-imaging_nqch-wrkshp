"""
Brute-force sanity check on a small (5-6 node) toy conflict graph, per the
brief's section 9. Confirms that:
  1. build_bqm() produces a BQM whose ground state matches the brute-force
     optimal independent set on the toy graph, and
  2. compute_lambda() picks a large-enough penalty that no conflicting pair
     ever appears together in the ground state.

Run with: python -m pytest tests/test_qubo_sanity.py -v
(or just: python tests/test_qubo_sanity.py)

TODO:
- Hand-build a toy networkx.Graph with 5-6 nodes, known weights, and a few
  conflict edges (pick weights/edges so the optimal independent set is easy
  to verify by hand -- write it in a comment above the graph construction)
- Brute-force: try all 2^n subsets, keep the max-weight one that's an
  independent set (no edge fully inside it)
- Build the BQM via scheduling.qubo.build_bqm(graph) and solve it exactly
  (dimod.ExactSolver, fine at this size) or via
  scheduling.solvers.solve_exact_cpsat(graph)
- Assert the BQM's optimal solution's selected set matches the brute-force
  optimal set (same objective value at minimum; same set if unique optimum)
"""

import sys
import os
from itertools import combinations

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import networkx as nx


def build_toy_graph() -> nx.Graph:
    """5-6 node toy graph with known-by-hand optimal independent set.
    TODO: fill in nodes (with "weight" attr) and conflict edges.
    """
    raise NotImplementedError


def brute_force_optimal(graph: nx.Graph) -> tuple[set, float]:
    """Try every subset, return the max-weight independent set."""
    nodes = list(graph.nodes)
    best_set, best_weight = set(), 0.0
    for r in range(len(nodes) + 1):
        for combo in combinations(nodes, r):
            combo_set = set(combo)
            if all(not graph.has_edge(i, j) for i, j in combinations(combo_set, 2)):
                weight = sum(graph.nodes[n]["weight"] for n in combo_set)
                if weight > best_weight:
                    best_set, best_weight = combo_set, weight
    return best_set, best_weight


def test_bqm_matches_brute_force():
    graph = build_toy_graph()
    expected_set, expected_weight = brute_force_optimal(graph)
    # TODO: from scheduling.qubo import build_bqm
    # TODO: bqm = build_bqm(graph)
    # TODO: solve exactly, compare selected set / objective to expected
    raise NotImplementedError


if __name__ == "__main__":
    test_bqm_matches_brute_force()
    print("Sanity check passed.")
