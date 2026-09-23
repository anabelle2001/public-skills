"""Replace this sample measurement with the real experiment procedure."""

import csv
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer()


@app.command()
def main(
    output: Annotated[Path, typer.Option(help="Headered CSV destination")] = Path(
        "data/results.csv"
    ),
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="") as data_file:
        writer = csv.DictWriter(data_file, fieldnames=["elapsed_s", "response_v"])
        writer.writeheader()
        writer.writerows([
            {"elapsed_s": 0, "response_v": 0},
            {"elapsed_s": 0.001, "response_v": 0.002},
            {"elapsed_s": 0.002, "response_v": 0.004},
        ])


if __name__ == "__main__":
    app()
