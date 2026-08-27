"""End-to-end pipeline: real TLE -> real visibility -> conflict graph -> QUBO -> solve."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config
from orbit.fetch_tles import fetch_tle
from orbit.visibility import load_targets, compute_visibility_windows
from scheduling.conflict_graph import build_conflict_graph
from scheduling.qubo import build_bqm
from scheduling.solvers import solve_simulated_annealing


def main():
    norad_id = config.NORAD_IDS[0]
    print(f"Fetching TLE for NORAD {norad_id}...")
    tle = fetch_tle(norad_id)

    targets = load_targets()
    print(f"Loaded {len(targets)} targets.")

    requests = compute_visibility_windows(norad_id, tle, targets)
    print(f"Computed {len(requests)} visibility windows.")
    if not requests:
        print("No visibility windows found in this horizon — try widening HORIZON_START/END in config.py.")
        return

    graph = build_conflict_graph(requests)
    print(f"Conflict graph: {graph.number_of_nodes()} nodes, {graph.number_of_edges()} edges.")

    bqm = build_bqm(graph)
    result = solve_simulated_annealing(bqm)

    print("\n--- SCHEDULE ---")
    total_weight = 0
    for r in requests:
        status = "SCHEDULED" if r["id"] in result["selected"] else "skipped"
        if r["id"] in result["selected"]:
            total_weight += r["weight"]
        print(f"  [{status}] {r['target']} (weight={r['weight']}, window={r['start']}-{r['end']}s)")
    print(f"\nTotal priority captured: {total_weight}")


if __name__ == "__main__":
    main()