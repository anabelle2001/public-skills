---
name: Writing Python
description: Write or revise Python scripts, CLIs, packages, and analysis code using Anabelle's Python tooling preferences.
---

# Writing Python

- Use `uv` for Python versions, environments, dependencies, and running commands. Keep dependencies in `pyproject.toml` and run project code through `uv run`.
- Build command-line scripts with Typer. Declare `typer` as a project dependency, expose a `main()` entry point, and give options and arguments useful names and help text. For a script with no user-facing inputs, keep a plain `main()` instead of inventing a CLI.
- Check types with Pyright (`uv run pyright`). Prefer precise types over `Any`. When a dependency lacks usable type information, install its stub package or add and maintain local `.pyi` stubs with Pyright's `stubPath`; type the API you actually use rather than suppressing errors with `Any`.
- Format with Ruff (`uv run ruff format .`) and set `preview = true` under `[tool.ruff]` in `pyproject.toml`. Follow existing project configuration where it already specifies stronger conventions.
- For any code that imports or depends on FLIR PySpin, use Python 3.10. Set the project's `requires-python` to `>=3.10,<3.11`, select it with `uv python pin 3.10`, and sync the environment with `uv sync --python 3.10` before running or type checking.

Use these preferences when creating a project; when editing an existing one, keep its dependency and entry-point layout consistent unless the task calls for changing it.
