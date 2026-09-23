"""Example figure: replace the example observations with report data."""

import csv
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter

output = Path(sys.argv[1])
output.parent.mkdir(parents=True, exist_ok=True)
fig, ax = plt.subplots(figsize=(6.5, 4))
with Path("data.csv").open(newline="") as data_file:
    observations = list(csv.DictReader(data_file))
ax.plot(
    [float(row["elapsed_s"]) for row in observations],
    [float(row["response_v"]) for row in observations],
    marker="o",
)
ax.set(title="Response versus elapsed time", xlabel="Elapsed time", ylabel="Response")
ax.xaxis.set_major_formatter(EngFormatter(unit="s"))
ax.yaxis.set_major_formatter(EngFormatter(unit="V"))
ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig(output)
