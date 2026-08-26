"""
End-to-end entry point: stitches every module together.

    fetch_tles -> visibility -> geometry -> conflict_graph -> qubo -> solvers -> viz

Run with: python scripts/run_pipeline.py

TODO once each role's modules are implemented:
1. Get requests (real: orbit.visibility + orbit.geometry, OR fake:
   load_requests_stub() below while Role A is still in progress)
2. Build conflict graph: scheduling.conflict_graph.build_conflict_graph(requests)
3. Build BQM: scheduling.qubo.build_bqm(graph)
4. Solve with all three methods: scheduling.solvers.solve_*()
5. Plot results: viz.target_map / viz.timeline / viz.ground_track
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import config


def load_requests_stub() -> list[dict]:
    """Fake visibility data so Role B (QUBO/solvers) isn't blocked on
    Role A's real orbit propagation. Replace with a call into
    orbit.visibility.compute_visibility_windows(...) once that's ready.

    Returns a small hand-built instance: 5 requests, overlapping windows,
    varying angles -- enough to sanity check conflict_graph.py and qubo.py.
    """
    return [
        {"id": 0, "target": "farmland_a", "start": 0, "end": 60, "angle": -10, "weight": 3},
        {"id": 1, "target": "city_downtown", "start": 30, "end": 90, "angle": 5, "weight": 8},
        {"id": 2, "target": "disaster_zone_1", "start": 100, "end": 160, "angle": 20, "weight": 10},
        {"id": 3, "target": "port_harbor", "start": 150, "end": 200, "angle": -15, "weight": 6},
        {"id": 4, "target": "coastal_survey", "start": 210, "end": 260, "angle": 0, "weight": 4},
    ]


def main():
    requests = load_requests_stub()  # TODO: swap for real orbit pipeline
    print(f"Loaded {len(requests)} candidate requests.")

    # TODO: graph = conflict_graph.build_conflict_graph(requests)
    # TODO: bqm = qubo.build_bqm(graph)
    # TODO: result = solvers.solve_simulated_annealing(bqm)
    # TODO: viz.target_map.plot_target_map(requests, result["selected"])
    # TODO: viz.timeline.plot_timeline(requests, result["selected"])

    raise NotImplementedError("Wire up the pipeline once each role's modules are ready.")


if __name__ == "__main__":
    main()
