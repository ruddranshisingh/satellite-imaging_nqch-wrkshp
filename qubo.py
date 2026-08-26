"""
Role B (scheduling).

Assemble the QUBO / Binary Quadratic Model (BQM) for the AEOS-SP:

    H = -sum_i(w_i * x_i) + lambda * sum_{(i,j) in conflicts}(x_i * x_j)

where x_i in {0,1} is "request i is scheduled", w_i is its priority weight,
and lambda (config.LAMBDA_MULTIPLIER * max(w_i+w_j) over conflicting pairs)
penalizes scheduling two conflicting requests together.

TODO:
- Take the conflict graph from conflict_graph.build_conflict_graph()
- Compute lambda_value = config.LAMBDA_MULTIPLIER * max(w_i + w_j) over all
  edges (i, j) in the graph
- Build a dimod.BinaryQuadraticModel:
    - linear term for node i: -w_i
    - quadratic term for edge (i, j): +lambda_value
- (Stretch/closed-loop feature) accept an optional `prior_schedule` dict of
  {request_id: 0/1} and add a linear penalty term
  config.RESCHEDULE_DEVIATION_PENALTY for flipping a previously-scheduled
  request off, to discourage unnecessary churn on reschedule
- Return the assembled BQM
"""

import dimod
import networkx as nx
import config


def build_bqm(graph: nx.Graph, prior_schedule: dict = None) -> dimod.BinaryQuadraticModel:
    """Assemble the BQM from a conflict graph.

    Args:
        graph: output of conflict_graph.build_conflict_graph(), nodes have
            a "weight" attribute.
        prior_schedule: optional {node_id: 0/1} for closed-loop rescheduling;
            adds a deviation penalty (see module docstring).

    Returns:
        dimod.BinaryQuadraticModel ready to hand to a sampler.
    """
    raise NotImplementedError


def compute_lambda(graph: nx.Graph) -> float:
    """lambda = config.LAMBDA_MULTIPLIER * max(w_i + w_j) over conflicting
    pairs (edges) in the graph."""
    raise NotImplementedError
