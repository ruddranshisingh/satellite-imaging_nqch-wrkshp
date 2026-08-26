"""
Solvers for the AEOS-SP QUBO built by qubo.build_qubo:

  - solve_greedy            priority-first heuristic baseline
  - solve_simulated_annealing   dwave-neal SA over the QUBO (classical
                             stand-in for / comparison point against QA)
  - solve_exact_cp_sat      OR-Tools CP-SAT exact solve of the equivalent
                             Maximum Weight Independent Set problem --
                             ground truth on small/medium instances
  - solve_qaoa              optional QAOA solver built directly from the
                             Ising Cost Hamiltonian (requires qiskit +
                             qiskit-aer + scipy; import is deferred so the
                             rest of the repo works without them)

Every solver returns a ScheduleResult so run_pipeline.py and Role C's viz
code can treat them interchangeably.
"""
import time
from dataclasses import dataclass, field

import dimod
import networkx as nx

from .qubo import is_feasible, to_ising, total_priority


@dataclass
class ScheduleResult:
    solver: str
    selected: list  # request ids scheduled (x_i = 1)
    total_priority: float
    feasible: bool
    runtime_sec: float
    extra: dict = field(default_factory=dict)  # solver-specific info (energy, reads, ...)


def _make_result(solver_name, graph, selected, runtime, extra=None):
    sel = list(selected)
    return ScheduleResult(
        solver=solver_name,
        selected=sel,
        total_priority=total_priority(graph, sel),
        feasible=is_feasible(graph, sel),
        runtime_sec=runtime,
        extra=extra or {},
    )


# ---------------------------------------------------------------------------
# Greedy priority-first baseline
# ---------------------------------------------------------------------------

def solve_greedy(graph: nx.Graph) -> ScheduleResult:
    """Sort requests by weight descending; take a request if it doesn't
    conflict with anything already taken. Fast and always feasible, but
    has no optimality guarantee."""
    t0 = time.perf_counter()
    order = sorted(graph.nodes, key=lambda i: graph.nodes[i]["weight"], reverse=True)
    selected = []
    blocked = set()
    for i in order:
        if i in blocked:
            continue
        selected.append(i)
        blocked.update(graph.neighbors(i))
    runtime = time.perf_counter() - t0
    return _make_result("greedy", graph, selected, runtime)


# ---------------------------------------------------------------------------
# Simulated annealing (dwave-neal) -- classical stand-in for QA
# ---------------------------------------------------------------------------

def solve_simulated_annealing(
    bqm: dimod.BinaryQuadraticModel,
    graph: nx.Graph,
    num_reads: int = 200,
    num_sweeps: int = 1000,
    seed: int = None,
) -> ScheduleResult:
    """Sample the QUBO with dwave-neal's SimulatedAnnealingSampler and
    return the lowest-energy sample found."""
    import neal

    t0 = time.perf_counter()
    sampler = neal.SimulatedAnnealingSampler()
    sampleset = sampler.sample(bqm, num_reads=num_reads, num_sweeps=num_sweeps, seed=seed)
    runtime = time.perf_counter() - t0

    best = sampleset.first
    selected = [i for i, x in best.sample.items() if x == 1]
    return _make_result(
        "simulated_annealing",
        graph,
        selected,
        runtime,
        extra={"energy": best.energy, "num_reads": num_reads, "num_sweeps": num_sweeps},
    )


# ---------------------------------------------------------------------------
# Exact baseline via OR-Tools CP-SAT (ground truth on small instances)
# ---------------------------------------------------------------------------

def solve_exact_cp_sat(graph: nx.Graph, time_limit_sec: float = 30.0) -> ScheduleResult:
    """Solve the equivalent 0/1 integer program exactly:

        maximize   sum_i w_i x_i
        subject to x_i + x_j <= 1   for every (i,j) in E
                   x_i in {0,1}

    This is Maximum Weight Independent Set on the conflict graph -- exact
    and NP-hard in general, but fine on the small/medium instances used to
    validate the QUBO solvers and to anchor the scaling plots.
    """
    from ortools.sat.python import cp_model

    t0 = time.perf_counter()
    model = cp_model.CpModel()
    x = {i: model.NewBoolVar(f"x_{i}") for i in graph.nodes}

    for i, j in graph.edges:
        model.Add(x[i] + x[j] <= 1)

    # CP-SAT needs integer coefficients; scale weights and round. Bump
    # WEIGHT_SCALE if your priority weights need more than 3 decimal
    # places of precision.
    WEIGHT_SCALE = 1000
    model.Maximize(sum(round(graph.nodes[i]["weight"] * WEIGHT_SCALE) * x[i] for i in graph.nodes))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_sec
    status = solver.Solve(model)
    runtime = time.perf_counter() - t0

    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return _make_result(
            "cp_sat", graph, [], runtime, extra={"status": solver.StatusName(status)}
        )

    selected = [i for i in graph.nodes if solver.Value(x[i]) == 1]
    return _make_result(
        "cp_sat",
        graph,
        selected,
        runtime,
        extra={"status": solver.StatusName(status), "time_limit_sec": time_limit_sec},
    )


# ---------------------------------------------------------------------------
# QAOA (optional -- requires qiskit + qiskit-aer + scipy)
# ---------------------------------------------------------------------------

def solve_qaoa(
    bqm: dimod.BinaryQuadraticModel,
    graph: nx.Graph,
    reps: int = 1,
    shots: int = 1024,
    optimizer_name: str = "COBYLA",
    seed: int = None,
) -> ScheduleResult:
    """Solve via QAOA built directly from the Ising Cost Hamiltonian:

        x_i -> (I - Z_i) / 2
        H_C = - sum_i w_i (I - Z_i)/2 + lambda * sum_{(i,j) in E} (I-Z_i)/2 (I-Z_j)/2
        H_M = sum_i X_i                       (transverse-field mixer)
        |gamma, beta> = prod_k e^{-i beta_k H_M} e^{-i gamma_k H_C} |+>^N

    `reps` is QAOA's circuit depth p (number of (gamma, beta) layers). The
    variational parameters are optimized classically (default: COBYLA) to
    minimize <H_C>, then the optimized circuit is sampled once more to
    read off the most frequent (lowest-energy) bitstring as the schedule.

    Optional dependency -- this project's requirements.txt does not
    install qiskit by default (it isn't needed for the SA/greedy/CP-SAT
    comparison the rest of the pipeline runs). Install with:

        pip install qiskit qiskit-aer scipy

    before calling this function.
    """
    try:
        from qiskit.circuit.library import QAOAAnsatz
        from qiskit.primitives import BackendSamplerV2
        from qiskit.quantum_info import SparsePauliOp
        from qiskit_aer import AerSimulator
        from scipy.optimize import minimize
    except ImportError as exc:
        raise ImportError(
            "solve_qaoa requires qiskit + qiskit-aer + scipy. "
            "Install with: pip install qiskit qiskit-aer scipy"
        ) from exc

    t0 = time.perf_counter()

    nodes = list(graph.nodes)
    n = len(nodes)
    index = {node: k for k, node in enumerate(nodes)}
    h, J, offset = to_ising(bqm)

    # Build H_C as a SparsePauliOp from the Ising linear (h) and
    # quadratic (J) terms.
    pauli_list = []
    for node, bias in h.items():
        if bias == 0:
            continue
        label = ["I"] * n
        label[index[node]] = "Z"
        pauli_list.append(("".join(label), bias))
    for (u, v), coupling in J.items():
        if coupling == 0:
            continue
        label = ["I"] * n
        label[index[u]] = "Z"
        label[index[v]] = "Z"
        pauli_list.append(("".join(label), coupling))

    if not pauli_list:
        runtime = time.perf_counter() - t0
        return _make_result("qaoa", graph, [], runtime, extra={"note": "empty Hamiltonian"})

    cost_hamiltonian = SparsePauliOp.from_list(pauli_list)
    qaoa_ansatz = QAOAAnsatz(cost_operator=cost_hamiltonian, reps=reps)
    backend = AerSimulator()
    sampler = BackendSamplerV2(backend=backend)

    def _bitstring_energy(bitstring: str) -> float:
        z = [1 - 2 * int(b) for b in bitstring[::-1]]  # '0' -> Z=+1, '1' -> Z=-1
        e = offset
        for node, bias in h.items():
            e += bias * z[index[node]]
        for (u, v), coupling in J.items():
            e += coupling * z[index[u]] * z[index[v]]
        return e

    def _expected_energy(params) -> float:
        bound = qaoa_ansatz.assign_parameters(params)
        bound.measure_all()
        result = sampler.run([bound], shots=shots).result()
        counts = result[0].data.meas.get_counts()
        total = sum(counts.values())
        return sum(_bitstring_energy(bs) * (count / total) for bs, count in counts.items())

    x0 = [0.1] * (2 * reps)
    opt_result = minimize(_expected_energy, x0, method=optimizer_name)

    bound = qaoa_ansatz.assign_parameters(opt_result.x)
    bound.measure_all()
    result = sampler.run([bound], shots=shots).result()
    counts = result[0].data.meas.get_counts()
    best_bitstring = max(counts, key=counts.get)
    selected = [nodes[k] for k, b in enumerate(best_bitstring[::-1]) if b == "1"]

    runtime = time.perf_counter() - t0
    return _make_result(
        "qaoa",
        graph,
        selected,
        runtime,
        extra={
            "reps": reps,
            "shots": shots,
            "optimizer": optimizer_name,
            "optimized_energy": opt_result.fun,
        },
    )


# ---------------------------------------------------------------------------
# Convenience: run every available solver and collect results together
# ---------------------------------------------------------------------------

def run_all(graph: nx.Graph, bqm: dimod.BinaryQuadraticModel, include_qaoa: bool = False) -> dict:
    """Run greedy, simulated annealing, and exact CP-SAT (and optionally
    QAOA) on the same instance and return {solver_name: ScheduleResult}.
    Used by scripts/run_pipeline.py and the scaling plots in Role C's
    viz code."""
    results = {
        "greedy": solve_greedy(graph),
        "simulated_annealing": solve_simulated_annealing(bqm, graph),
        "cp_sat": solve_exact_cp_sat(graph),
    }
    if include_qaoa:
        results["qaoa"] = solve_qaoa(bqm, graph)
    return results
