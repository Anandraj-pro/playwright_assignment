"""Check a task's deliverables: files exist, tests are collected (and pass), interview notes are written.

Usage:
    uv run python scripts/check_task.py P04-02            # files, test collection, interview notes
    uv run python scripts/check_task.py P04-02 --run      # ...and run the task's tests
    uv run python scripts/check_task.py --branch task/P04-02-first-api-tests   # used by CI

Deliverables come from each task's meta line in learning-path/phases/. Anything that can't be checked
automatically (a merged PR, a presentation, "Done when" items) is printed as a manual item for you
or your buddy to confirm. Exit code 1 means at least one automatic check failed.
"""

from __future__ import annotations

import argparse
import glob
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_tracker import parse  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TASK_ID = re.compile(r"P\d{2}-\d{2}", re.IGNORECASE)
BACKTICK = re.compile(r"`([^`]+)`")
PATH_CHARS = re.compile(r"^[\w.\-/*{},]+$")
MIN_TESTS = re.compile(r"≥\s*(\d+)\s*tests")
BRACES = re.compile(r"\{([^{}]+)\}")
NOTES_MIN_WORDS = 40


@dataclass
class Result:
    ok: bool | None  # None = manual check
    text: str


def looks_like_path(token: str) -> bool:
    if not PATH_CHARS.match(token) or token.startswith(("-", "[")):
        return False
    return "/" in token or "." in token or token in {"Makefile", "Dockerfile"}


def expand_braces(pattern: str) -> list[str]:
    match = BRACES.search(pattern)
    if not match:
        return [pattern]
    head, tail = pattern[: match.start()], pattern[match.end() :]
    return [p for option in match.group(1).split(",") for p in expand_braces(head + option + tail)]


def matches(pattern: str) -> list[Path]:
    """Existing, non-empty files or directories for a deliverable pattern."""
    if any(ch in pattern for ch in "*?["):
        found = [Path(p) for p in glob.glob(str(ROOT / pattern), recursive=True)]
    else:
        found = [ROOT / pattern] if (ROOT / pattern).exists() else []
    return [p for p in found if (p.is_dir() and any(p.iterdir())) or (p.is_file() and p.stat().st_size > 0)]


def split_items(deliverable_md: str) -> list[str]:
    return [item.strip() for item in deliverable_md.split(", ") if item.strip()]


def check_item(item: str, test_paths: list[Path], min_tests: list[int]) -> list[Result]:
    tokens = BACKTICK.findall(item)
    plain = BACKTICK.sub(lambda m: m.group(1), item)
    if not item.startswith("`") or not tokens or not looks_like_path(tokens[0]) or "clone)" in item:
        return [Result(None, plain)]

    if "…" in item and len(tokens) >= 2:  # `docs/bugs/BUG-001.md` … `BUG-005.md`
        first = tokens[0]
        last = str(Path(first).parent / tokens[-1])
        ok = bool(matches(first)) and bool(matches(last))
        return [Result(ok, f"{first} … {last} exist")]

    if "(or " in item:  # `CLAUDE.md` (or `AGENTS.md`)
        options = [t for t in tokens if looks_like_path(t)]
        ok = any(matches(t) for t in options)
        return [Result(ok, " or ".join(options) + " exists")]

    results = []
    for pattern in expand_braces(tokens[0]):
        found = matches(pattern)
        results.append(Result(bool(found), f"{pattern} exists" + ("" if found else " (missing or empty)")))
        if pattern.startswith("tests/"):
            test_paths.extend(found)
    if m := MIN_TESTS.search(item):
        min_tests.append(int(m.group(1)))
    extra = BACKTICK.sub("", item).strip(" ()")
    if extra and not MIN_TESTS.search(item) and not item.rstrip().endswith(")"):
        results.append(Result(None, f"also check: {plain}"))
    return results


def check_tests(test_paths: list[Path], min_tests: int, run: bool) -> list[Result]:
    if not test_paths:
        return []
    args = [str(p.relative_to(ROOT)) for p in test_paths]
    collect = subprocess.run(
        [sys.executable, "-m", "pytest", "--collect-only", "-q", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    found = re.search(r"(\d+) tests? collected", collect.stdout)
    count = int(found.group(1)) if found else 0
    need = max(min_tests, 1)
    results = [
        Result(
            collect.returncode == 0 and count >= need,
            f"{count} test(s) collected (need ≥ {need}) in {', '.join(args)}",
        )
    ]
    if collect.returncode != 0:
        results.append(Result(False, "collection errors:\n" + collect.stdout[-1500:]))
    if run and collect.returncode == 0:
        run_result = subprocess.run([sys.executable, "-m", "pytest", "-q", *args], cwd=ROOT, check=False)
        results.append(Result(run_result.returncode == 0, "tests pass"))
    return results


def check_notes(task_id: str) -> Result:
    notes = ROOT / "interview-notes" / f"{task_id[:3]}.md"
    if not notes.exists():
        return Result(False, f"{notes.relative_to(ROOT)} has a '## {task_id}' section (file missing)")
    section, inside = [], False
    for line in notes.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            if inside and line.startswith(("# ", "## ")):
                break
            inside = inside or bool(re.match(rf"^#+\s*{task_id}\b", line))
            continue
        if inside:
            section.append(line)
    words = len(" ".join(section).split())
    ok = words >= NOTES_MIN_WORDS
    return Result(
        ok,
        f"{notes.relative_to(ROOT)} has a '## {task_id}' section with ≥ {NOTES_MIN_WORDS} words "
        f"(found {words})",
    )


def done_when(task: dict[str, Any]) -> list[str]:
    text = task["phase_file"].read_text(encoding="utf-8")
    start = text.find(f"### {task['id']} · ")
    block = text[start : text.find("#### 📘", start)]
    return [line[6:].strip() for line in block.splitlines() if line.startswith("- [ ] ")]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("task", nargs="?", help="task id, e.g. P04-02")
    parser.add_argument("--branch", help="derive the task id from a branch name like task/P04-02-...")
    parser.add_argument("--run", action="store_true", help="also run the task's tests")
    args = parser.parse_args()

    source = args.task or args.branch or ""
    found = TASK_ID.search(source)
    if not found:
        if args.branch:
            print(f"Branch '{args.branch}' doesn't name a task (task/Pxx-yy-...): nothing to check.")
            return 0
        parser.error("give a task id such as P04-02")
    task_id = found.group(0).upper()
    tasks = {t["id"]: t for t in parse()}
    if task_id not in tasks:
        print(f"Unknown task {task_id}. See learning-path/TASKS.md.")
        return 1
    task = tasks[task_id]

    test_paths: list[Path] = []
    min_tests: list[int] = []
    results: list[Result] = []
    for item in split_items(task["deliverable_md"]):
        results += check_item(item, test_paths, min_tests)
    results += check_tests(test_paths, max(min_tests, default=1), args.run)
    results.append(check_notes(task_id))
    results += [Result(None, f"done when: {line}") for line in done_when(task)]

    print(f"### {task_id} · {task['title']} ({task['badge']} {task['level']}, {task['hours']}h)\n")
    for r in results:
        mark = "☐" if r.ok is None else ("✅" if r.ok else "❌")
        print(f"- {mark} {r.text}")
    failed = [r for r in results if r.ok is False]
    automatic = [r for r in results if r.ok is not None]
    manual = len(results) - len(automatic)
    verdict = "FAIL" if failed else "PASS"
    print(
        f"\n**{verdict}**: {len(automatic) - len(failed)}/{len(automatic)} automatic checks passed; "
        f"{manual} manual item(s) for you or your buddy to confirm."
    )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
