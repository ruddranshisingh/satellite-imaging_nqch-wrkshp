"""
Role C (viz).

Plot solution quality and runtime vs. instance size (number of requests),
comparing simulated annealing, greedy MWIS, and exact CP-SAT.

TODO:
- Take a list of benchmark results, e.g.
    [{"n_requests": int, "method": str, "objective": float,
      "runtime_sec": float, "optimal_objective": float}, ...]
  (produced by scripts/run_pipeline.py or a dedicated benchmark script,
  ideally including SPOT5-style instances alongside your own synthetic ones)
- Two subplots: (a) optimality gap (objective / optimal_objective) vs n,
  one line per method; (b) runtime vs n (log scale), one line per method
- Save to f"{config.OUTPUTS_DIR}/scaling_plot.png"

(Stretch: if graph decomposition is implemented, add a fourth series here
so the scaling benefit of decomposition is directly visible.)
"""

import config


def plot_scaling(results: list[dict], out_path: str = None):
    raise NotImplementedError
