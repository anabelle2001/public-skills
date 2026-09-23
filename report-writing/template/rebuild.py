"""Poll report inputs and run make after changes. Stop with Ctrl+C."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCES = {"Makefile", "pyproject.toml", "uv.lock"}
EXTENSIONS = {
    ".md",
    ".py",
    ".csv",
    ".tsv",
    ".parquet",
    ".json",
    ".yaml",
    ".yml",
    ".tex",
    ".bib",
    ".png",
    ".jpg",
    ".svg",
}
SKIP = {".venv", ".git", "__pycache__", ".ruff_cache", "out"}


def snapshot() -> dict[str, tuple[int, int]]:
    result = {}
    for path in ROOT.rglob("*"):
        if any(
            part in SKIP or part.startswith(".")
            for part in path.relative_to(ROOT).parts[:-1]
        ):
            continue
        if path.is_file() and (path.name in SOURCES or path.suffix in EXTENSIONS):
            stat = path.stat()
            result[str(path)] = (stat.st_mtime_ns, stat.st_size)
    return result


def main() -> None:
    previous = snapshot()
    subprocess.run(["make"], cwd=ROOT, check=False)
    print("Watching report inputs. Ctrl+C to stop.", flush=True)
    try:
        while True:
            time.sleep(0.5)
            current = snapshot()
            if current != previous:
                previous = current
                subprocess.run(["make"], cwd=ROOT, check=False)
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()
