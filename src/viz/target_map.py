"""
Role C (viz).

Plot all candidate targets on a map, colored by whether they were accepted
(scheduled) or rejected by the solver: accepted=green, rejected=red.

TODO:
- Take the solver output ({"selected": set(node_ids), ...}) plus the
  original requests list (with target lat/lon)
- Scatter-plot every target, green if its request id is in `selected`,
  red otherwise
- Save to f"{config.OUTPUTS_DIR}/target_map.png"
"""

import config


def plot_target_map(requests: list[dict], selected: set, out_path: str = None):
    raise NotImplementedError
