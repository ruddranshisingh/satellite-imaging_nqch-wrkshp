"""
Brute-force sanity check for the AEOS-SP QUBO (repo brief, section 9):
build a small (6-node) conflict graph by hand and verify

  1. the lambda produced by qubo.min_valid_lambda / build_qubo forbids
     every conflicting pair from co-appearing in the QUBO's ground state,
     and
  2. the QUBO's ground state (found here by brute force over all 2^N
     bitstrings) exactly matches the true Maximum Weight Independent Set
     of the conflict graph (also found by brute force).

Run with: pytest tests/test_qubo_sanity.py -v
"""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.scheduling.conflict_graph import Request, build_conflict_graph
from src.scheduling.qubo import build_qubo, is_feasible, min_valid_lambda, total_priority


def _toy_requests():
    # 6 requests, deliberately overlapping so the conflict graph has
    # several edges to exercise the penalty term.
    return [
        Request(id="r1", weight=5, start=0, end=10, angle=0),
        Request(id="r2", weight=8, start=5, end=15, angle=5),  # overlaps r1
        Request(id="r3", weight=3, start=20, end=30, angle=40),  # far from r1/r2
        Request(id="r4", weight=9, start=12, end=22, angle=10),  # overlaps r2, r3
        Request(id="r5", weight=2, start=31, end=35, angle=41),  # tight slew vs r3
        Request(id="r6", weight=6, start=50, end=60, angle=0),  # isolated
    ]


def _brute_force_mwis(graph):
    """Exact Maximum Weight Independent Set by trying every subset --
    only viable for small N, which is exactly what this sanity test is."""
    nodes = list(graph.nodes)
    best_selected, best_weight = [], -1
    for r in range(len(nodes) + 1):
        for subset in itertools.combinations(nodes, r):
            if is_feasible(graph, subset):
                w = total_priority(graph, subset)
                if w > best_weight:
                    best_weight, best_selected = w, list(subset)
    return best_selected, best_weight


def _brute_force_qubo_ground_state(bqm):
    """Exact QUBO ground state by evaluating every bitstring."""
    variables = list(bqm.variables)
    best_sample, best_energy = None, float("inf")
    for bits in itertools.product([0, 1], repeat=len(variables)):
        sample = dict(zip(variables, bits))
        energy = bqm.energy(sample)
        if energy < best_energy:
            best_energy, best_sample = energy, sample
    return best_sample, best_energy


def test_conflict_graph_has_expected_edges():
    graph = build_conflict_graph(_toy_requests(), slew_rate_deg_per_sec=2.0)
    assert graph.has_edge("r1", "r2")  # overlapping windows
    assert graph.has_edge("r2", "r4")  # overlapping windows
    assert graph.has_edge("r3", "r4")  # overlapping windows
    assert not graph.has_edge("r1", "r6")  # far apart, isolated


def test_lambda_forbids_all_conflicts():
    # min_valid_lambda(graph) is exactly max(w_i + w_j) over conflicting
    # pairs -- used unscaled it would only guarantee a *tie*, not a strict
    # preference for dropping the conflict. build_qubo applies
    # lambda_multiplier (> 1) on top of it precisely to make the
    # inequality strict, so that's the value to check here.
    graph = build_conflict_graph(_toy_requests(), slew_rate_deg_per_sec=2.0)
    bqm = build_qubo(graph, lambda_multiplier=1.75)
    lam = bqm.info["lambda"]
    for i, j in graph.edges:
        assert lam > graph.nodes[i]["weight"] + graph.nodes[j]["weight"]


def test_min_valid_lambda_is_the_tight_threshold():
    graph = build_conflict_graph(_toy_requests(), slew_rate_deg_per_sec=2.0)
    lam = min_valid_lambda(graph)
    for i, j in graph.edges:
        assert lam >= graph.nodes[i]["weight"] + graph.nodes[j]["weight"]


def test_qubo_ground_state_matches_brute_force_mwis():
    graph = build_conflict_graph(_toy_requests(), slew_rate_deg_per_sec=2.0)
    bqm = build_qubo(graph, lambda_multiplier=1.75)

    qubo_sample, _ = _brute_force_qubo_ground_state(bqm)
    qubo_selected = [i for i, x in qubo_sample.items() if x == 1]

    mwis_selected, mwis_weight = _brute_force_mwis(graph)

    assert is_feasible(graph, qubo_selected)
    assert sorted(qubo_selected) == sorted(mwis_selected)
    assert total_priority(graph, qubo_selected) == mwis_weight
