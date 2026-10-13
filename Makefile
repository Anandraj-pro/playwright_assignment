# Every target is a thin wrapper around a `uv run` command, so you can copy the
# command into any shell (Windows PowerShell included) if you don't have make.
.PHONY: help install lint format test smoke check tracker

help:     ## list targets
	@grep -E '^[a-z-]+:.*##' $(MAKEFILE_LIST) | sed 's/:.*##/ →/'

install:  ## install dependencies, the Chromium browser and the git hooks
	uv sync
	uv run playwright install chromium
	uv run pre-commit install

lint:     ## ruff lint + format check, then mypy
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy

format:   ## auto-fix lint issues and format
	uv run ruff check --fix .
	uv run ruff format .

test:     ## run every test under tests/
	uv run pytest -q

smoke:    ## run only tests marked smoke
	uv run pytest -m smoke -q

check:    ## check a task's deliverables, e.g. make check TASK=P04-02
	uv run python scripts/check_task.py $(TASK) --run

tracker:  ## maintainers: regenerate TASKS.md and task-tracker.csv
	uv run python scripts/build_tracker.py
