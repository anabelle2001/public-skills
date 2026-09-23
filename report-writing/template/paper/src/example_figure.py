"""Example figure: replace the example observations with report data."""

import csv
from pathlib import Path
from typing import Annotated

import matplotlib
import typer

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from util.plot import label_si_axes

app = typer.Typer()


@app.command()
def main(
    output: Annotated[Path, typer.Argument(help="Figure file (.pdf, .svg, or .png)")],
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with Path("data/results.csv").open(newline="") as data_file:
        observations = list(csv.DictReader(data_file))

    fig, ax = plt.subplots(figsize=(6.5, 4))
    ax.plot(
        [float(row["elapsed_s"]) for row in observations],
        [float(row["response_v"]) for row in observations],
        marker="o",
    )
    ax.set(title="Response versus elapsed time")
    label_si_axes(
        ax, x_label="Elapsed time", x_unit="s", y_label="Response", y_unit="V"
    )
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(output)


if __name__ == "__main__":
    app()
