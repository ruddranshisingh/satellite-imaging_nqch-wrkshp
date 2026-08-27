"""Role B: assemble the QUBO."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import dimod
import config


def compute_lambda(graph):
    if graph.number_of_edges() == 0:
        return 1.0
    max_pair = max(
        graph.nodes[i]["weight"] + graph.nodes[j]["weight"]
        for i, j in graph.edges
    )
    return config.LAMBDA_MULTIPLIER * max_pair


def build_bqm(graph):
    lam = compute_lambda(graph)
    bqm = dimod.BinaryQuadraticModel(vartype=dimod.BINARY)
    for node, attrs in graph.nodes(data=True):
        bqm.add_variable(node, -attrs["weight"])
    for i, j in graph.edges:
        bqm.add_interaction(i, j, lam)
    return bqm