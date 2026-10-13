# QE Hero: <your name>

> Replace this block in P00-01 with your goal, e.g. *"SDET interview-ready by March; strongest in API + CI."*

This repo is my hands-on Quality Engineering learning path: Python, pytest, API testing with requests,
UI testing with Playwright, database testing, parallel runs, Docker, GitHub Actions quality gates,
performance/accessibility/security basics, and AI in QA (MCP servers, skills, agents).

## Start here

1. **Read [`learning-path/README.md`](learning-path/README.md)**: how the path works, levels and tracks.
2. **Day 1:** do [P00-00](learning-path/phases/P00-git-setup.md#p00-00--hello-automation-your-first-ui-and-api-tests):
   your first UI and API tests, in about 2 hours.
3. Track progress in [`learning-path/TASKS.md`](learning-path/TASKS.md).

## Quick start

| | Command (with make) | Without make (Windows PowerShell, etc.) |
|---|---|---|
| Install | `make install` | `uv sync; uv run playwright install chromium; uv run pre-commit install` |
| Lint | `make lint` | `uv run ruff check .; uv run ruff format --check .; uv run mypy` |
| Test | `make test` | `uv run pytest -q` |
| Check a task | `make check TASK=P04-02` | `uv run python scripts/check_task.py P04-02 --run` |

No local setup yet? Open the repo in **GitHub Codespaces** (Code → Codespaces → Create) or in a
**VS Code dev container**. Everything is preinstalled from `.devcontainer/devcontainer.json`.
