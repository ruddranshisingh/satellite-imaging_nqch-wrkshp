"""
Role C (viz).

Gantt-style timeline of the schedule: one row per accepted request, bar
spanning its visibility window, annotated with target name and weight.

TODO:
- Take requests + the selected set from a solver result
- For each selected request, draw a horizontal bar from start to end on its
  own row (matplotlib.pyplot.barh or broken_barh)
- Label each bar with the target name
- Save to f"{config.OUTPUTS_DIR}/timeline.png"

(Stretch/closed-loop feature: accept two schedules -- before/after a
reschedule event -- and plot them stacked so the diff is visually obvious.)
"""

import config


def plot_timeline(requests: list[dict], selected: set, out_path: str = None):
    raise NotImplementedError


def plot_timeline_diff(requests: list[dict], selected_before: set, selected_after: set, out_path: str = None):
    """Stretch: visualize a closed-loop reschedule as two stacked timelines."""
    raise NotImplementedError
