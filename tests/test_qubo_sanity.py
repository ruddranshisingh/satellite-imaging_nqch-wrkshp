"""
Brute-force sanity check on a small toy conflict graph. Confirms that:
  1. build_bqm() produces a BQM whose ground state matches the brute-force
     optimal independent set on the toy graph, and
  2. compute_lambda() picks a large-enough penalty that no conflicting pair
     ever appears together in the ground state.

Run with: python tests/test_qubo_sanity.py
"""
import sys
import os
from itertools import combinations

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import dimod
import networkx as nx
from scheduling.qubo import build_bqm


def build_toy_graph() -> nx.Graph:
    """6-node toy graph.
    Weights: A=5, B=3, C=4, D=6, E=2, F=7
    Conflicts (edges): A-B, B-C, C-D, D-E, E-F, A-F
    (a 6-cycle: A-B-C-D-E-F-A)

    By hand: picking alternating nodes avoids all conflicts.
    {A, C, E} = 5+4+2 = 11
    {B, D, F} = 3+6+7 = 16   <- best alternating set
    {D, F} = 6+7 = 13 (also valid, no edge between D and F)
    {B, D, F} is independent (no edges among B,D,F in this cycle) and beats
    every other combination checked by hand, so 16 is the expected optimum.
    """
    graph = nx.Graph()
    weights = {"A": 5, "B": 3, "C": 4, "D": 6, "E": 2, "F": 7}
    for node, w in weights.items():
        graph.add_node(node, weight=w)
    edges = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "F"), ("A", "F")]
    graph.add_edges_from(edges)
    return graph


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
    print(f"Brute-force optimal: {expected_set} (weight={expected_weight})")

    bqm = build_bqm(graph)
    sampler = dimod.ExactSolver()
    sampleset = sampler.sample(bqm)
    best = sampleset.first.sample
    selected = {node for node, val in best.items() if val == 1}
    selected_weight = sum(graph.nodes[n]["weight"] for n in selected)

    print(f"BQM ground state:     {selected} (weight={selected_weight})")

    # Check no conflicting pair is selected together
    for i, j in graph.edges:
        assert not (i in selected and j in selected), \
            f"Conflict violated: both {i} and {j} selected!"

    assert selected_weight == expected_weight, \
        f"Objective mismatch: BQM got {selected_weight}, expected {expected_weight}"

    print("PASSED: BQM ground state matches brute-force optimum, no conflicts violated.")


if __name__ == "__main__":
    test_bqm_matches_brute_force()
