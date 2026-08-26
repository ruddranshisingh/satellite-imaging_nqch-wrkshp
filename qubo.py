"""
QUBO / Ising assembly for the AEOS-SP conflict graph.

    H_QUBO(x) = - sum_i w_i x_i + lambda * sum_{(i,j) in E} x_i x_j

x_i = 1 means request i is scheduled. Feasibility (no two conflicting
requests both scheduled, i.e. x_i + x_j <= 1 for every (i,j) in E) is
enforced softly via the quadratic penalty term rather than as a hard
constraint, so choosing lambda correctly matters:

    lambda > max_{(i,j) in E} (w_i + w_j)

guarantees that any bitstring containing a conflicting pair scores worse
than the same bitstring with the lower-weight member of the pair dropped,
so the ground state of H_QUBO is always a *feasible* (conflict-free)
schedule that maximizes total priority among feasible schedules.

If lambda is too small, solvers (SA, QAOA) can return infeasible
schedules with conflicts. If lambda is excessively large, the energy
landscape flattens around priority differences between valid schedules,
making it harder for heuristic/quantum solvers to distinguish them --
hence the repo default of a modest multiplier (1.5-2x) above the strict
minimum rather than an arbitrarily huge value.
"""
import dimod
import networkx as nx


def min_valid_lambda(graph: nx.Graph) -> float:
    """Smallest lambda that provably guarantees conflict-free ground
    states: max(w_i + w_j) over all conflicting pairs, or 0 if the graph
    has no edges (nothing to penalize)."""
    if graph.number_of_edges() == 0:
        return 0.0
    return max(
        graph.nodes[i]["weight"] + graph.nodes[j]["weight"] for i, j in graph.edges
    )


def build_qubo(graph: nx.Graph, lambda_multiplier: float = 1.75) -> dimod.BinaryQuadraticModel:
    """Assemble H_QUBO as a dimod BinaryQuadraticModel.

    lambda_multiplier scales min_valid_lambda(graph) -- the repo default
    of 1.75 gives headroom above the strict minimum so near-boundary
    cases still resolve cleanly under sampler noise, without being so
    large it drowns out priority differences (see module docstring).
    """
    lam = lambda_multiplier * min_valid_lambda(graph)
    if lam == 0.0:
        # No conflicts in this instance -- lambda is unused but must still
        # be well-defined for downstream code (e.g. QAOA's to_ising()).
        lam = lambda_multiplier

    bqm = dimod.BinaryQuadraticModel(vartype=dimod.BINARY)
    for i in graph.nodes:
        w = graph.nodes[i]["weight"]
        bqm.add_variable(i, -w)  # linear term: -w_i x_i
    for i, j in graph.edges:
        bqm.add_interaction(i, j, lam)  # quadratic term: lambda x_i x_j

    bqm.info = {"lambda": lam}  # stash for reporting/debugging
    return bqm


def to_ising(bqm: dimod.BinaryQuadraticModel):
    """Convert to the Ising Cost Hamiltonian H_C via x_i -> (I - Z_i)/2,
    returned as (h, J, offset): linear biases, quadratic couplings, and a
    constant offset. This is the form QAOA circuits consume (see
    solvers.solve_qaoa) and matches dimod's own to_ising() convention."""
    h, J, offset = bqm.to_ising()
    return h, J, offset


def is_feasible(graph: nx.Graph, selected) -> bool:
    """True if `selected` (an iterable of scheduled request ids) contains
    no conflicting pair, i.e. satisfies x_i + x_j <= 1 for every (i,j) in E."""
    selected = set(selected)
    return all(not (i in selected and j in selected) for i, j in graph.edges)


def total_priority(graph: nx.Graph, selected) -> float:
    """Sum of w_i over scheduled requests."""
    return sum(graph.nodes[i]["weight"] for i in selected)
