"""
Stretch: sweep config.LAMBDA_MULTIPLIER across a range of values and plot
the feasibility rate (fraction of solver runs that produce a conflict-free
schedule) vs. lambda, to empirically validate the "1.5-2x max(w)" default
suggested in the brief.

TODO:
- For each lambda value in a sweep range (e.g. 0.5x to 3x max(w), step 0.25):
    - build the BQM with that lambda (bypass qubo.compute_lambda's default)
    - solve with simulated annealing, multiple reads
    - check what fraction of reads are conflict-free (no two selected
      requests share an edge in the conflict graph)
- Plot feasibility rate vs lambda multiplier
- Save to f"{config.OUTPUTS_DIR}/lambda_sweep.png"
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import config


def sweep_lambda(graph, multipliers: list[float] = None) -> list[dict]:
    multipliers = multipliers or [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]
    raise NotImplementedError


if __name__ == "__main__":
    raise NotImplementedError("Run after run_pipeline.py's conflict graph is available.")
