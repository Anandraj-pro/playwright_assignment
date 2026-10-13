"""Regenerate learning-path/TASKS.md and learning-path/task-tracker.csv from the phase files.

Usage: python scripts/build_tracker.py
"""

import csv
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
LP = ROOT / "learning-path"
PHASES = sorted((LP / "phases").glob("P*.md"))
HOURS_PER_WEEK = 10
# The Essentials track: what every new engineer does first (see learning-path/README.md §1).
ESSENTIALS = {
    "P00-00",
    "P00-01",
    "P00-02",
    "P00-03",
    "P00-04",
    "P00-05",
    "P00-06",
    "P01-01",
    "P01-02",
    "P01-03",
    "P01-04",
    "P02-01",
    "P02-02",
    "P02-04",
    "P03-01",
    "P03-02",
    "P03-03",
    "P03-04",
    "P04-01",
    "P04-02",
    "P04-03",
    "P04-04",
    "P04-05",
    "P04-06",
    "P05-01",
    "P05-02",
    "P05-03",
    "P06-01",
    "P09-01",
    "P10-01",
}

TASK_RE = re.compile(r"^### (P\d{2}-\d{2}) · (.+)$")
META_RE = re.compile(
    r"^\*\*Level:\*\* (\S+) (Zero|Hero|Super Hero) · \*\*Time:\*\* (\d+)h · "
    r"\*\*App:\*\* (.+?) · \*\*Deliverable:\*\* (.+)$"
)
PHASE_RE = re.compile(r"^# (P\d{2}): (.+)$")


def anchor(heading: str) -> str:
    """GitHub-style heading anchor."""
    return re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")


def parse() -> list[dict[str, Any]]:
    tasks = []
    for path in PHASES:
        lines = path.read_text(encoding="utf-8").splitlines()
        phase_title = next(PHASE_RE.match(line).group(2) for line in lines if PHASE_RE.match(line))
        for i, line in enumerate(lines):
            task = TASK_RE.match(line)
            if not task:
                continue
            meta = next((META_RE.match(m) for m in lines[i + 1 : i + 4] if META_RE.match(m)), None)
            if meta is None:
                raise ValueError(f"{path.name}: task {task.group(1)} has no valid meta line")
            tasks.append(
                {
                    "id": task.group(1),
                    "phase": task.group(1)[:3],
                    "phase_title": phase_title,
                    "title": task.group(2),
                    "badge": meta.group(1),
                    "level": meta.group(2),
                    "hours": int(meta.group(3)),
                    "app": meta.group(4),
                    "deliverable": meta.group(5).replace("`", ""),
                    "deliverable_md": meta.group(5),
                    "phase_file": path,
                    "link": f"phases/{path.name}#{anchor(line.removeprefix('### '))}",
                }
            )
    return tasks


def write_csv(tasks: list[dict[str, Any]]) -> None:
    with (LP / "task-tracker.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "phase", "title", "level", "hours", "app", "deliverable", "status"])
        for t in tasks:
            writer.writerow(
                [t["id"], t["phase"], t["title"], t["level"], t["hours"], t["app"], t["deliverable"], "todo"]
            )


def write_markdown(tasks: list[dict[str, Any]]) -> None:
    total_hours = sum(t["hours"] for t in tasks)
    by_level = {lvl: [t for t in tasks if t["level"] == lvl] for lvl in ("Zero", "Hero", "Super Hero")}
    essentials = [t for t in tasks if t["id"] in ESSENTIALS]
    out = [
        "# Task Tracker: QE Learning Path (Zero → Super Hero)",
        "",
        "> Generated from `phases/*.md` by `scripts/build_tracker.py`.",
        "> Don't edit the table structure by hand; learners only change ⬜ to ✅ in their own copy.",
        "",
        "**How to use:** work top to bottom. For each task, open its guide (the link),",
        "create an issue and branch, build it, run `make check TASK=<id>`, open a PR,",
        "write your interview answers in `interview-notes/Pxx.md`, then tick ⬜ → ✅.",
        "⭐ marks the **Essentials** track: new engineers do these first.",
        f"*Target week* assumes ~{HOURS_PER_WEEK} h/week. Adjust to your pace.",
        "",
        "## Summary",
        "",
        "| Level | Tasks | Hours |",
        "|---|---|---|",
    ]
    for lvl, items in by_level.items():
        badge = items[0]["badge"] if items else ""
        out.append(f"| {badge} {lvl} | {len(items)} | {sum(t['hours'] for t in items)} |")
    out += [
        f"| **Total** | **{len(tasks)}** | **{total_hours}** (~{-(-total_hours // HOURS_PER_WEEK)} weeks) |",
        f"| ⭐ Essentials track | {len(essentials)} | {sum(t['hours'] for t in essentials)} |",
        "",
    ]

    cumulative = 0
    current_phase = None
    for t in tasks:
        if t["phase"] != current_phase:
            current_phase = t["phase"]
            phase_tasks = [x for x in tasks if x["phase"] == current_phase]
            phase_hours = sum(x["hours"] for x in phase_tasks)
            out += [
                "",
                f"## {current_phase}: {t['phase_title']} ({len(phase_tasks)} tasks, {phase_hours} h)",
                "",
                "| ✓ | ID | Task | Level | Time | Target week | App | Deliverable |",
                "|---|---|---|---|---|---|---|---|",
            ]
        cumulative += t["hours"]
        week = -(-cumulative // HOURS_PER_WEEK)
        out.append(
            f"| ⬜ | {t['id']}{' ⭐' if t['id'] in ESSENTIALS else ''} | [{t['title']}]({t['link']}) "
            f"| {t['badge']} | {t['hours']}h | W{week} "
            f"| {t['app']} | {t['deliverable']} |"
        )
    (LP / "TASKS.md").write_text("\n".join(out) + "\n", encoding="utf-8")


if __name__ == "__main__":
    all_tasks = parse()
    unknown = ESSENTIALS - {t["id"] for t in all_tasks}
    if unknown:
        raise SystemExit(f"ESSENTIALS lists unknown task ids: {sorted(unknown)}")
    write_csv(all_tasks)
    write_markdown(all_tasks)
    print(f"{len(all_tasks)} tasks, {sum(t['hours'] for t in all_tasks)} hours → TASKS.md + task-tracker.csv")
