# Support Model: Buddies, Reviews and Getting Unstuck

Nobody should learn this alone, and nobody should stay stuck for a day on something a colleague could explain in five minutes. This page describes who helps, when, and how work is reviewed.

---

## 1. Roles

| Role | Who | Time | Does |
|---|---|---|---|
| **Learner** | You | ~10 h/week (Essentials: see README §1) | Works through the tasks in their own repo, asks early, reviews one peer PR per phase |
| **Buddy** | A peer one or two phases ahead, or a mid-level QE | 30 min/week | Weekly check-in, first stop when stuck, reviews your PRs against the rubric |
| **Mentor / QE lead** | A senior QE | 1 h/fortnight + reviews | Office hours, reviews 🟣 tasks and the capstone, runs the mock interview loops (P13-05) |
| **Maintainer** | Owner of this repo | As needed | Keeps tasks and demo-app details current, triages "the guide is wrong" issues |

Working solo, with no team? Use an AI assistant as your reviewer against the rubric in §4 (and judge its review), and find a study partner for the mock interviews. The P00-06 rules still apply.

---

## 2. Cadence

| When | What | Length |
|---|---|---|
| Weekly | **Buddy check-in:** what I finished, where I'm stuck, what's next | 30 min |
| Weekly | **Demo:** show one merged PR to your cohort or buddy (what it tests, how you know it can fail) | 5 min each |
| Every 2 weeks | **Mentor office hours:** open questions, 🟣 design discussions | 60 min |
| End of each phase | **Checkpoint:** the phase's AI mock interview + one peer PR review | 1 h |
| Monthly | **Retro on the path itself:** file issues for anything unclear, wrong or out of date | 30 min |

---

## 3. Getting unstuck: the 2-hour rule

**If you've been stuck for 2 hours, ask.** (For 🟢 tasks, try on your own for 30 minutes before asking AI, as README §5 says.) Being stuck isn't a failure, but staying stuck is wasted time.

Before asking, work down this ladder:
1. **Re-read** the task's user guide and the "Done when" list.
2. **Debug properly** (P03-02): read the failure bottom-up, write a hypothesis, run the cheapest experiment.
3. **Ask AI**, following the rules (no secrets; you must understand every line you keep).
4. **Ask your buddy**, then **office hours**, using this template:

```markdown
**Task:** P04-03 · Auth, CRUD and negative testing
**Goal:** what I'm trying to make work
**What I tried:** 1) … 2) … 3) …
**Exact error / output:** (paste it; redact tokens)
**My current hypothesis:** …
**Branch / commit:** link
```

A question in this format usually gets answered in minutes, and about half the time writing it down solves the problem.

**The guide itself is wrong or out of date?** Open an issue in the template repo with the task ID and what you observed. Demo apps change, and your report keeps the path working for the next person.

---

## 4. PR review rubric

Use this for your own PRs (self-review before asking), for peer reviews, and for buddy or mentor reviews. Score each row 1–4.

| Criterion | 1: Not yet | 2: Developing | 3: Solid | 4: Excellent |
|---|---|---|---|---|
| **Correctness:** does it check the right thing, and can it fail? | Assertions missing or always true | Checks something, but weak (visibility only, status only) | Specific assertions on the behaviour that matters; the author showed it failing | Also checks side effects and negative paths; failure messages explain themselves |
| **Test design:** right layer, right techniques | UI used for everything; happy path only | Some negative cases; layer not justified | Lowest sensible layer; partitions and boundaries covered (P01-02) | Coverage driven by risk; explicitly says what's *not* tested |
| **Reliability** | Sleeps, shared state or order dependence | Works alone, fragile together | Independent, owns its data, no hard waits, parallel-safe | Proven stable (repeat and random-order runs), explicit timeouts where justified |
| **Readability** | Unclear names, copy-paste | Understandable with effort | Behaviour-named tests, arrange/act/assert visible, no duplication | Reads like a specification; a newcomer could extend it |
| **Framework use** | Ignores existing fixtures, clients and page objects | Uses some, duplicates others | Reuses the framework consistently | Improves the framework for everyone, with tests for the framework change |
| **Evidence** | "Works on my machine" | CI green | CI green plus how it was tested, including a deliberate failure | Traces, reports or screenshots attached where they help the reviewer |
| **Hygiene and security** | Secrets, no timeouts, noisy logs | Minor issues | No secrets, timeouts everywhere, lint clean | Adds or tightens a guard (lint rule, gate, check) |
| **AI disclosure** | AI used, not disclosed | Disclosed | Disclosed, with what was checked or changed | Disclosed, with a mistake caught and a `CLAUDE.md` rule added |

**What "good enough to merge" means by level:**

| Level | Bar |
|---|---|
| 🟢 Zero | At least 2 in every row, and **3 in Correctness** (a test that can't fail never merges) |
| 🔵 Hero | At least 3 in every row |
| 🟣 Super Hero | At least 3 in every row, and 4 in Test design *or* Reliability |

**How to write review comments:** start with what's good; prefix each comment with **must-fix**, **suggestion** or **nit**; leave at least one comment about *test quality*, not just style; and ask questions rather than issuing orders ("What happens if two tests use this user at the same time?").

---

## 5. Peer reviews

- **One peer PR per phase**, from P00-03 onwards. Find one by labelling your PR `review-wanted` in your cohort's channel or project board.
- Review against §4, then compare your scores with the author's self-review. Big gaps are the interesting conversations.
- Reviewing is an interview skill in itself: *"How do you review test code?"* comes up in SDET interviews, and you'll have real examples.

---

## 6. Checking your own work

- **`make check TASK=P04-02`** (or `uv run python scripts/check_task.py P04-02 --run`) checks that the task's deliverables exist, that its tests are collected and pass, and that `interview-notes/P04.md` has a `## P04-02` section with real content. It then lists the "Done when" items for you or your buddy to confirm by hand.
- The **`task-check`** workflow (shipped with the template) runs the same check on every PR from a `task/Pxx-yy-…` branch and writes the result to the job summary.
- Passing `check_task` means the *mechanics* are done. The rubric in §4 decides whether it's *good*.

---

## 7. For mentors

- Review 🟣 tasks and the capstone yourself; delegate 🟢 and 🔵 reviews to buddies and peers.
- Look first at **Correctness** and **Reliability**. Style can wait; false confidence can't.
- Track each learner's hours against the estimates in `TASKS.md` and report big differences to the maintainer: estimates are recalibrated after each pilot.
- Reference solutions (decision D9 in `docs/PROJECT_EXPECTATIONS.md`) are for mentors. Share approaches, not answers.
