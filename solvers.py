"""
Role B (scheduling).

Solve the assembled BQM three ways, so every result can be sanity-checked
and benchmarked against a known-optimal baseline:

1. Simulated annealing (dwave-neal / dimod's SimulatedAnnealingSampler)
   -- our default "quantum-ready" solver, runs entirely classically.
2. Greedy Maximum Weight Independent Set on the conflict graph directly
   -- a cheap classical baseline, no QUBO needed.
3. Exact solve via CP-SAT (ortools) -- ground truth for small/medium
   instances, used to validate (1) and (2) and to measure the optimality
   gap in scaling_plot.py.

TODO:
- solve_simulated_annealing(bqm, num_reads=...) -> best sample + energy
- solve_greedy_mwis(graph) -> selected node set (weight-greedy: repeatedly
  pick the highest-weight remaining node, remove its neighbors, repeat)
- solve_exact_cpsat(graph) -> optimal selected node set + objective value
  (model as: maximize sum(w_i * x_i) subject to x_i + x_j <= 1 for every
  conflict edge (i,j))
- All three should return a comparable structure, e.g.
    {"selected": set(node_ids), "objective": float, "runtime_sec": float}
"""

import time
import dimod
import networkx as nx


def solve_simulated_annealing(bqm: dimod.BinaryQuadraticModel, num_reads: int = 100) -> dict:
    raise NotImplementedError


def solve_greedy_mwis(graph: nx.Graph) -> dict:
    raise NotImplementedError


def solve_exact_cpsat(graph: nx.Graph) -> dict:
    raise NotImplementedError
