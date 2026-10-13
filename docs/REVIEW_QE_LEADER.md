# Learning Path Review: QE Leader Perspective

| | |
|---|---|
| **Reviewed** | `learning-path/` v0.2 (66 tasks, 12 phases, ~258 h) and `docs/PROJECT_EXPECTATIONS.md` |
| **Lens** | Head of Quality Engineering who hires, onboards and promotes QEs |
| **Questions asked** | 1. What topics are missing? 2. Where are the gaps? 3. How easily and how quickly can a *new* engineer pick it up? |
| **Date** | 2026-09-23 |
| **Status** | ✅ All P1 fixes implemented in learning path v0.3 (see §8). Task IDs in §1–§7 refer to **v0.2** numbering; §8 maps them to v0.3. |
| **Method** | Read the task statements and a sample of guides end to end; keyword coverage scan of all 12 phase files (~75k words); counted interview questions by level; computed time-to-milestone from `task-tracker.csv` at 10 h/week |

---

## 1. Verdict

**As a technical curriculum, this is strong. As an onboarding path for new engineers, it's too slow to first value and tilted towards *automation* engineering over *quality* engineering.**

It would turn a motivated junior SDET into a strong mid-level automation engineer with an impressive portfolio. It would lose a good share of manual testers before week 8. It also doesn't yet teach the thing juniors are interviewed on first: deciding *what* to test.

### Scorecard (1 = weak, 5 = excellent)

| Dimension | Score | Evidence |
|---|---|---|
| Automation depth (API, UI, DB, parallel, Docker, CI) | ⭐⭐⭐⭐⭐ | Contract testing, sharding cost model, gated CI, image scanning, testcontainers: beyond most internal programs |
| AI in QA | ⭐⭐⭐⭐⭐ | MCP usage and building, skills, an evaluated agent, testing LLM features, adoption playbook. Ahead of the market. |
| Consistency and format | ⭐⭐⭐⭐⭐ | Every task has the same six parts; tracker is generated, not hand-maintained |
| Senior interview prep ([H]/[SH]) | ⭐⭐⭐⭐ | 279 questions with model answers, drills, rubrics, mock loops |
| **Junior interview prep ([Z])** | ⭐⭐ | Only **64 of 343** questions (19%) are [Z]. Classic junior topics are missing (§3.2). |
| **QE fundamentals (test design, strategy)** | ⭐⭐ | Scattered; the test pyramid and test strategy first appear in **P11, week 23** |
| **Non-functional (performance, security, accessibility)** | ⭐ | Performance and security are v1 non-goals; accessibility is a stretch note |
| **Time to first value** | ⭐⭐ | First real API test at hour 54, first UI test at hour 74, first CI-gated PR at hour 152 (§2.1) |
| **Can learners check their own work?** | ⭐⭐ | "Done when" is self-assessed; reference solutions (D9) and reviewers are still TBD |
| **Setup friction (Windows, corporate laptops)** | ⭐⭐ | Bash and Makefile only; no Windows/WSL guidance; the devcontainer arrives in P07-05 (week 16) |
| Maintainability | ⭐⭐⭐ | Template repos never receive fixes; demo-app drift has no automated detection (§2.2) |

### What's already working (keep it)

- **One repo per learner** that grows into a portfolio. That's the right model for both learning and hiring signal.
- **Three worked examples per task** (🟢/🔵/🟣) let one path serve three personas.
- **Toolshop as the spine**, with a with-bugs build and sprint versions, gives realistic bug hunts, contract drift and triage data.
- **"Answer out loud first"** collapsible answers, plus AI mock-interviewer prompts at each checkpoint.
- **Strong guardrails:** no hard waits, no secrets, own your data, disclose AI use, never commit code you can't explain.

---

## 2. How easily and how quickly can new engineers pick it up?

### 2.1 Time to milestones (today, at 10 h/week)

| Milestone | Today | Target for onboarding (learning hours) | Gap |
|---|---|---|---|
| First passing test against a **real app** | hour 54 · week 6 (P03-02) | ≤ 2 h (day 1) | 🔴 |
| First **UI** test | hour 74 · week 8 (P04-01) | ≤ 2 h (day 1) | 🔴 |
| First **CI-gated PR** | hour 152 · week 16 (P08-01) | ≤ 40 h (week 4 part-time, week 1 full-time) | 🔴 |
| Uses **AI** with guardrails | hour 187 · week 19 (P10-01) | Day 1 (they use it from day 1 anyway) | 🔴 |
| **Docker** first needed vs taught | needed P03-05 (week 7), P05-02 (week 11); taught P07-01 (week 14) | Taught before first use | 🟠 |
| Can contribute to a **team** suite | hour 84 · week 9 (after P04-03) | ≤ 80 h (end of the Essentials track, §4) | 🟠 |
| Full path | 258 h · about 26 weeks | Separate onboarding and mastery tracks | 🟠 |

**Realistic duration by persona** (reviewer estimate; calibrate in the R3 pilot):

| Persona | Stated | Likely | Why |
|---|---|---|---|
| Manual QA moving to automation | 258 h | **350–400 h** | 🔵/🟣 estimates assume someone who already codes; first-time coders typically take 1.5–2× on debugging-heavy tasks (P00-04, P05-04, P07-04, P10-06, P11-02) |
| Junior SDET | 258 h | ~220 h | Skims P01 🟢 |
| Experienced SDET | — | ~120 h | Proves 🟢 via Q&A, focuses on 🟣 |

### 2.2 Friction points, ranked by drop-off risk

| # | Friction | Where | Fix |
|---|---|---|---|
| 1 | **Six weeks of Python, pytest and Git before touching the app under test.** Manual testers join to test apps; they lose motivation. | P00–P02 | Add **P00-00 "Hello automation" (2 h)**: one Playwright codegen test and one API test on day 1, then "you'll understand every line by week 8". |
| 2 | **Week-2 tooling wall.** P00-04 asks someone who hasn't written Python yet to configure uv, ruff, mypy, pre-commit, gitleaks and a Makefile. | P00-04 | **Ship the skeleton pre-configured in the template.** P00-04 becomes "read, run and explain the tooling" (🟢). Building it from scratch moves to a 🟣 optional task. |
| 3 | **Windows and locked-down corporate laptops.** Zero Windows/WSL guidance; `make` and the bash scripts don't run natively; Docker needs admin rights and proxy setup. | P00-01 | Make the **devcontainer / Codespaces the default route** for 🟢 learners on day 1 (move it from P07-05). Add a WSL2 note and a `tasks.py` or `uv run` alternative to `make`. |
| 4 | **Reading load before doing.** About 1,000–1,340 words per task (P10 is the heaviest). | All phases | Add a **"⚡ Quick path"** box at the top of each task: 5 steps, the commands, done-when. The deep dive stays below for when they're stuck. |
| 5 | **No way to check your own work.** "Done when" is self-assessed; D9 (reference solutions) is open; reviewers are TBD. Learners stall on "is this right?". | All | Add `scripts/check_task.py P03-02` and a **`task-check` workflow**: deliverable paths exist, tests are collected and pass, `interview-notes/Pxx.md` isn't empty. The deliverables are already machine-readable in `task-tracker.csv`. |
| 6 | **Things are used before they're taught.** Docker (§2.1), CI (week 16, although P08-01 only needs P00-04) and AI (week 19, although AI rules apply from day 1). | P03–P10 | Resequence (§4): CI lint + unit moves to the end of the pytest phase; a "Docker as a user" task goes before P03-05; AI safe use goes into P00. |
| 7 | **Template repos never get fixes.** After "Use this template", corrections to `learning-path/` never reach a learner's repo, so they keep working from stale instructions. | Repo model | Learners read the path from the **central repo or a published site**, and their repo holds only their work. Or add `make sync-path` from an `upstream` remote. |
| 8 | **Demo-app drift.** Some Toolshop selectors and endpoints are marked "confirm with codegen/Swagger"; public apps reset or change. | P03–P05 | A **nightly canary workflow** in the template repo that runs the reference solutions against the demo apps and opens an issue on drift. |
| 9 | **No human support model.** No buddy, no PR review rubric, no peer review; office hours exist only in the pilot plan. | Roles | A buddy per learner, a 30-minute weekly demo, a **PR review rubric per level**, and **each learner reviews one peer PR per phase** (reviewing test code is itself an interview topic). |
| 10 | **No placement check.** Personas say "prove 🟢 via the Q&A" but there's no structured way to do it. | README | A 45-minute **placement quiz** (10 questions per phase) that outputs a skip list. |

---

## 3. Missed topics and gaps

**Priority key:** **P1** = add before the pilot · **P2** = v1.1 · **P3** = optional or v2

### 3.1 🔴 Quality-engineering fundamentals: the biggest gap (P1)

**Today:**
- Equivalence partitioning and pairwise appear only inside a P02-02 example.
- Exploratory testing appears in P09-01.
- The test pyramid, risk-based testing, test plans and entry/exit criteria appear only in **P11 (week 23)**.
- Decision tables, boundary-value analysis as a technique, state-transition testing, requirement/story review and traceability are **missing or one-liners**.

**Why it matters:** we'd be producing engineers who can automate anything but can't decide *what* is worth testing. This is the first thing juniors are interviewed on, and the first thing a lead notices on a real team.

**Add a phase "QE fundamentals" (~14 h, right after P00):**

| New task | Level | Hours | Content | App |
|---|---|---|---|---|
| Test-design techniques | 🟢 | 4 | EP, BVA, decision table (discount rules), state transition (order status), pairwise | Toolshop checkout and registration |
| Story review and shift-left | 🔵 | 3 | Review 3 stories: ambiguities, acceptance criteria, risk matrix, "three amigos" questions | Toolshop stories (write them from the UI) |
| Test cases, scenarios and traceability | 🟢 | 3 | Scenario vs case, a lightweight case format, mapping to stories, `@pytest.mark.req("TS-12")` linking automation to requirements | Toolshop |
| QA in the SDLC | 🟢 | 4 | SDLC/STLC, bug life cycle, severity vs priority, verification vs validation, smoke vs sanity vs regression vs retesting, the test pyramid, risk-based testing | — |

Then move the P11 questions on the test pyramid and risk-based testing into this phase, and keep the strategy *application* in P11.

### 3.2 🔴 Junior interview coverage (P1)

| Level | Questions | Share | Target |
|---|---|---|---|
| [Z] | 64 | 19% | ~30% |
| [H] | 167 | 49% | ~45% |
| [SH] | 112 | 33% | ~25% |

**Missing classic junior questions (zero hits in the path):**
- STLC
- bug life cycle
- verification vs validation
- black-box vs white-box
- smoke vs sanity
- test scenario vs test case
- traceability matrix

Also, P06 and P11 have only 2–3 [Z] questions each.

**Fix:** add about 40 [Z] questions, most of them in the new fundamentals phase.

### 3.3 🔴 Debugging (P1)

The path never mentions `pdb`, `breakpoint()`, `pytest --pdb`, `--lf`, `-l` or the IDE debugger, and mentions browser DevTools only twice in passing. Debugging is a new engineer's number-one daily skill and a live-coding differentiator.

- **Add a 🟢 task to the pytest phase, "Debug a failing test" (2 h):** read tracebacks, IDE breakpoints, `pytest --pdb -x --lf -l`, logging vs printing.
- **Add to P04:** the DevTools Network tab and the Playwright trace viewer side by side on the same failure.

### 3.4 🔴 Non-functional testing (P1 for performance and accessibility, P2 for security)

| Topic | Today | Why it can't wait for v2 | Add |
|---|---|---|---|
| **Performance** | Non-goal; one line in a P11 answer | "How would you performance-test X?" comes up in nearly every SDET loop | 🔵 **Locust against self-hosted Restful-Booker/Toolshop** (p50/p95/p99, ramp, think time, reading results) plus response-time budgets in API tests (4 h). 🟣 a performance smoke in nightly CI with thresholds and trend (5 h). |
| **Accessibility** | Stretch note plus one [SH] question | The **European Accessibility Act** has been enforced since June 2025, so accessibility is now a compliance requirement for many products, not a nice-to-have | 🔵 **axe scan of Toolshop's key pages**, keyboard-only checkout, gate on serious/critical findings, and the limits of automation (4 h) |
| **Security** | One AI-assist prompt about the OWASP API Top 10 | IDOR/BOLA and role escalation are functional bugs that QEs *should* catch | 🔵 **Authorisation matrix** (customer vs admin vs anonymous on every Toolshop endpoint, IDOR), injection payloads as negative tests, security headers, a **ZAP baseline scan in Docker** in nightly CI (5 h) |

The Docker and CI phases make all three cheap to add: the stack and pipelines already exist.

### 3.5 🔴 Brownfield skills (P1)

The path is 100% greenfield: every learner builds their own framework. **New hires don't build frameworks; they join an existing one.** Missing:

- reading and extending someone else's framework;
- refactoring a smelly suite;
- migrating Selenium to Playwright. Selenium is mentioned six times, but there's no task, and it's a common real-world job and interview topic.

**Add** a `legacy-suite/` folder to the template with planted smells:
- `time.sleep`
- absolute XPath
- shared state between tests
- copy-pasted setup
- no page objects
- Selenium-style waits

Then add two tasks:

| Task | Level | Hours | Placement |
|---|---|---|---|
| "Rescue a legacy suite": fix the smells and measure flake rate before and after | 🔵 | 5 | After P04-03 |
| "Selenium → Playwright migration plan": plan and migrate 5 tests | 🟣 | 3 | End of P04 |

### 3.6 🟠 API-side mocking and service virtualisation (P2)

`page.route` is well covered, but on the API side there's only one mention of `requests-mock`.

**Add to P03-04 (+1 h):**
- unit-test the API clients with `responses` or `pytest-httpserver`;
- when to stub and when to hit the real service;
- how stubs drift from reality, and how contract tests catch that.

### 3.7 🟠 QE inside the team process (P2)

The path never mentions test-management tools, test estimation or release sign-off, and mentions the Definition of Done only twice. New hires need to know how testing fits into sprints, not just how to write it.

**Add a 🔵 task to P09 (3 h):**
- estimate test effort for a Toolshop feature;
- write a **release-readiness report** (scope tested, open risks, go/no-go recommendation);
- map concepts to tools such as Jira, Xray or TestRail (concept-level, vendor-neutral).

### 3.8 🟠 BDD (P2, market-dependent)

BDD is a v1 non-goal today, but Gherkin/Cucumber is still common in enterprise job descriptions.

**Add an optional 🔵 task (3 h):**
- a `pytest-bdd` feature for SauceDemo checkout, reusing the existing page objects;
- plus the interview answer: when BDD helps collaboration, and when it's only a translation layer.

### 3.9 🟢 Async and event-driven systems (P3)

WebSockets, message queues and Kafka get zero hits. There's no suitable free demo app, so **add [SH] interview questions only**, not a task:
- polling vs waiting on events;
- eventual consistency;
- idempotent consumers;
- testing retries and dead-letter queues.

### 3.10 🟢 Playwright with TypeScript (P3)

This is a market note, not a design flaw: most Playwright job ads use TypeScript. **Add an optional 🟣 appendix (4 h):** port 5 tests to `@playwright/test`, and compare fixtures, config and the test runner. It improves hireability without changing the Python spine.

---

## 4. Recommended restructure

**Renumber now, before the pilot.** Once learners start, task IDs appear in their branches, issues and notes, so they must freeze. Today renumbering costs one scripted rename and a `build_tracker.py` run.

| New | Phase | Change from today |
|---|---|---|
| P00 | Setup, Git, **Hello automation**, **AI safe-use basics** | + P00-00 quick win (2 h); pre-configured skeleton; devcontainer by default; the core of P10-01/P10-02 moves here; P00-05 (gh issue automation) becomes optional |
| **P01** | **QE fundamentals** (new) | §3.1, ~14 h, plus most of the new [Z] questions |
| P02 | Python for QE | Unchanged |
| P03 | pytest | + debugging task (§3.3); + **CI lint and unit tests** (today's P08-01) so every later PR is gated |
| P04 | API testing | + "Docker as a user" (run, logs, compose up/down) before self-hosted Toolshop; + API mocking (§3.6) |
| P05 | UI testing | + legacy-suite rescue and Selenium migration (§3.5) |
| P06 | Database testing | Unchanged |
| P07 | Parallel execution | Unchanged |
| P08 | Docker: create and maintain | Fundamentals trimmed (now taught earlier) |
| P09 | CI gates | Starts from the existing CI instead of creating it |
| P10 | Reporting, bugs, flaky tests, **release readiness** | + §3.7 |
| **P11** | **Non-functional: performance, accessibility, security** (new) | §3.4, ~18 h |
| P12 | AI in QA | The basics now live in P00; this becomes MCP, skills, agents, evals and adoption |
| P13 | Capstone and interviews | The capstone must include one non-functional risk |

### Three tracks instead of one path

| Track | For | Tasks | Hours | Outcome |
|---|---|---|---|---|
| **Essentials** (onboarding) | Every new hire, weeks 1–8 | ~27 | **~80** (2 weeks full-time or 8 weeks part-time) | First CI-gated PR by hour ~40; ready to contribute to a team suite when the track ends |
| **Hero** | QE/SDET growth | All 🟢 + 🔵 | ~220 | Passes QE/SDET interviews |
| **Super Hero** | Senior/lead growth | All | ~300 | Senior/lead SDET, drives AI adoption |

**The Essentials track uses 23 existing tasks (69 h) plus 11 h of new work:**
- **Existing tasks:**
  - P00-01, P00-02, P00-03
  - P01-01, P01-02, P01-04
  - P02-01, P02-02, P02-03
  - P03-01 to P03-04
  - P04-01 to P04-03
  - P05-01
  - P07-01, P07-02
  - P08-01, P08-02
  - P09-01
  - P10-02
- **New tasks:** Hello automation (2 h), test-design techniques (4 h), story review (3 h) and debugging (2 h).

**New total:** about 300 h. The P1 additions come to ~44 h; P2 adds ~7 h.

---

## 5. Top 10 actions

| # | Action | Priority | Effort | Fixes |
|---|---|---|---|---|
| 1 | P00-00 "Hello automation" quick win on day 1 | P1 | S | Motivation, time to first value |
| 2 | Pre-configured skeleton, devcontainer by default, Windows/WSL notes | P1 | M | Setup friction and the week-2 tooling wall |
| 3 | New **QE fundamentals** phase and about 40 [Z] questions | P1 | L | The biggest content gap; junior interviews |
| 4 | Resequence: CI in week 4–5, AI basics in week 1, Docker-as-a-user before first use | P1 | M | Things used before they're taught |
| 5 | `check_task.py` and a `task-check` workflow (self-verification) | P1 | M | "Is this right?" stalls; mentor load |
| 6 | Debugging task and DevTools/trace exercise | P1 | S | Daily skill; live-coding rounds |
| 7 | Non-functional phase: performance, accessibility, security | P1 | L | Interview coverage; compliance (EAA) |
| 8 | `legacy-suite/` rescue and Selenium migration | P1 | M | Real-job readiness (brownfield) |
| 9 | Human support: buddy, PR review rubric, peer reviews, weekly demo, placement quiz | P1 | S (process) | Completion rate |
| 10 | Template sync (`make sync-path` or a published site) and a demo-app drift canary | P2 | M | Maintainability; stale instructions |

Effort: **S** < 1 day · **M** 1–3 days · **L** 1–2 weeks of authoring.

---

## 6. How to measure onboarding success (add to the pilot, R3)

| Metric | Target |
|---|---|
| Time to first green test against a real app | ≤ 1 day |
| Time to first CI-gated PR merged | ≤ 40 learning hours |
| Essentials track completion | ≤ 8 weeks part-time; ≥ 85% of starters finish |
| Drop-off per phase | < 15% |
| Actual vs estimated hours per task | Within ±30% after recalibration |
| Blocked time ("stuck > 2 h without help") | < 1 occurrence per phase |
| Mock-interview score, start → Essentials end → Hero end | +1 rubric point per stage |
| Hiring-manager rating of the portfolio repo | ≥ 4/5 from 3 independent reviewers |

---

## 7. Decisions needed from the owner

| # | Decision | Recommendation |
|---|---|---|
| R-1 | Add the QE fundamentals and non-functional phases to v1 (moving them out of v2)? | **Yes.** They're the largest interview and on-the-job gaps. |
| R-2 | Renumber phases now? | **Yes, before the pilot.** IDs freeze once learners start. |
| R-3 | Where do learners read the path: central repo/site, or a copy in their template? | **Central** (or a sync command). Copies go stale. |
| R-4 | Reference solutions (open decision D9) | A **private repo** that also powers `check_task.py` and the drift canary |
| R-5 | Essentials as the mandatory onboarding for new hires, Hero/Super Hero as growth tracks? | **Yes** |

---

## 8. Implementation status (v0.3, 2026-09-23)

All P1 items from §5 are implemented. The path is now **78 tasks in 14 phases, about 301 hours**, with a ⭐ **Essentials track of 30 tasks (~89 h)**.

### 8.1 What was done

| # | Action (§5) | Done | Where |
|---|---|---|---|
| 1 | Day-1 quick win | ✅ | **P00-00** *Hello automation*: create the repo, open Codespaces, 2 UI + 2 API tests, a trace; about 2 h |
| 2 | Pre-configured skeleton, devcontainer default, Windows notes | ✅ | Shipped at the repo root: `pyproject.toml`, `uv.lock`, `Makefile`, `.pre-commit-config.yaml`, `.devcontainer/`, `framework/`, `tests/unit/test_sanity.py`. P00-04 is now a 🟢 tour (building it from scratch is an optional stretch); P00-01 covers Codespaces / dev container / local routes and WSL2; every `make` target has a plain `uv run` equivalent |
| 3 | QE fundamentals phase + junior questions | ✅ | New **P01** (SDLC/STLC and the bug life cycle; test-design techniques on Toolshop's real validation rules; test cases and traceability; story review and risk) plus the moved prompting task. **[Z] questions: 64 → 117** (19% → 27% of 430) |
| 4 | Resequence | ✅ | CI lint + unit is now **P00-05** (hour 12); safe AI pair-testing is **P00-06** (hour 14); Docker-as-a-user is **P04-05/06**, before the first self-hosted task (P04-07). Renumbered before the pilot (map in §8.3) |
| 5 | Self-check tooling | ✅ | `scripts/check_task.py` (`make check TASK=…`): deliverables, test collection and run, interview-notes section, "done when" list. `.github/workflows/task-check.yml` runs it on `task/…` PRs |
| 6 | Debugging | ✅ | **P03-02** debugging lab (three planted bugs; tracebacks, `--pdb`, `-l`, `--lf`, IDE breakpoints, `git bisect`) + a DevTools-vs-trace exercise in **P05-07** |
| 7 | Non-functional phase | ✅ | New **P11**: Locust with budgets, axe + keyboard + screen reader, authorisation matrix / hostile input / headers, and a nightly CI gate for all three (perf budgets, ZAP baseline, axe) |
| 8 | Brownfield skills | ✅ | `legacy-suite/` (a Playwright suite with 20+ planted smells; a 5-test Selenium suite), **P05-04** *Rescue a legacy suite*, **P05-08** *Selenium → Playwright migration* with a parity script |
| 9 | Human support | ✅ | `learning-path/SUPPORT.md` (roles, cadence, the 2-hour rule, the PR review rubric per level, peer reviews), a peer-review step in P00-03, `learning-path/PLACEMENT.md` (60-question placement check with skip rules) |
| — | Capstone | ✅ | P13-02 now requires at least one non-functional risk with an automated check |

### 8.2 Milestones, before and after

| Milestone | v0.2 | v0.3 |
|---|---|---|
| First test against a real app | hour 54 (week 6) | **hour 0–2 (day 1)** |
| First UI test | hour 74 (week 8) | **hour 0–2 (day 1)** |
| First CI-gated PR | hour 152 (week 16) | **hour 12 (week 2)** |
| AI with guardrails | hour 187 (week 19) | **hour 14 (week 2)**; the rules apply from day 1 |
| Docker taught before first use | no (needed week 7, taught week 14) | **yes** (P04-05 at hour 90, first self-hosted task P04-07 at hour 96) |
| Ready to contribute to a team suite | about hour 84 | **end of Essentials, ~89 h** |

### 8.3 Task ID map (v0.2 → v0.3)

| v0.2 | v0.3 | Note |
|---|---|---|
| P00-01…04 | P00-01…04 | P00-04 rewritten as a 🟢 tour |
| P00-05 | P00-07 | Now optional |
| P01 (Python) | P02 | Same tasks |
| P02-01, 02-02…02-05 | P03-01, 03-03…03-06 | P03-02 is the new debugging lab |
| P03-01…04, 03-05, 03-06 | P04-01…04, 04-07, 04-08 | P04-05/06 are the moved Docker-as-a-user tasks |
| P04-01…03, 04-04…06 | P05-01…03, 05-05…07 | P05-04 and P05-08 are new |
| P05, P06, P09, P11 | P06, P07, P10, P13 | Same tasks |
| P07-01, 07-02 | P04-05, 04-06 | Docker as a user, moved earlier |
| P07-03…05 | P08-01…03 | Docker: build, compose, maintain |
| P08-01 | **P00-05** | CI from week 2 |
| P08-02…06 | P09-01…05 | |
| P10-01 | **P01-05** | Prompting for test design |
| P10-02 | **P00-06** | Safe AI pair-testing from week 2 |
| P10-03…08 | P12-01…06 | |
| — | P01 (new phase), P11 (new phase) | |

### 8.4 Where this differs from the review's plan

- **CI moved even earlier than proposed:** to P00-05 rather than the end of the pytest phase, because it only needs the shipped skeleton. First CI-gated PR at hour 12 instead of the ≤ 40 h target.
- **Prompting went to P01, not P00:** it's practised on the P01 test-design work (boundary tables, test cases). P00 keeps the guardrails (P00-06).
- **Essentials is ~89 h, not ~80 h:** it also includes SDLC basics (P01-01), test cases (P01-03) and the skeleton tour (P00-04), which new hires need.
- **Placement check has 5 questions per phase (60 in total), not 10:** 10 per phase wouldn't fit the proposed time box.
- **[Z] share is 27%, not 30%:** about 50 junior questions were added, but the new tasks also brought senior ones.
- **Security is in v1:** §3.4 rated it P2, but §5 had it in the P1 phase, so it was implemented.

### 8.5 Verification

- **Run against the live apps** while writing (2026-09-23):
  - the P00-00 hello tests;
  - both legacy suites (Playwright: green in order, ~25 s, fails when run alone; Selenium: 5 passed);
  - a migrated Playwright suite and its parity report (5/5, ~4 s vs ~8 s);
  - the debugging lab (fails as designed);
  - the pairwise generator (60 → 20);
  - the requirement-coverage hook;
  - Locust scripts (tiny runs) and the budget gate;
  - the axe fixture, gate and keyboard tests;
  - the authorisation matrix and ownership checks (read-only on hosted Toolshop).
- **Real findings built into the tasks:**
  - Toolshop rejects customers on their 18th birthday.
  - Toolshop's "younger than 75" limit actually sits around a 1933/34 birth year.
  - `not-an-email` is accepted by the registration API.
  - The shared `customer@…` account on hosted Toolshop was locked by other people's traffic.
  - SauceDemo allows checkout with an empty cart.
  - Toolshop's login page has an unnamed button; its home page has a `list` violation.
  - The API is missing security headers and shows a 404-vs-"not authorized" mismatch.
- **Static checks:**
  - All 25 Markdown files: links and anchors resolve.
  - All code blocks parse: 164 Python, 31 YAML (one valid Compose `!override` tag flagged), 3 JSON.
  - New Python examples pass the skeleton's ruff rules.
  - The skeleton passes `ruff`, `ruff format --check`, `mypy` and `pytest`.
- **`check_task.py`:** a simulated learner passes P00-00 (5/5 automatic checks), and an incomplete task fails as expected.

**Not yet verified:**
- **Dev container / Codespaces build:** not built. Docker wasn't running in the authoring environment.
- **`task-check.yml` workflow:** not run on GitHub. `actionlint` couldn't be installed, so it's YAML-parse-checked only.
- **Nightly non-functional workflow and the ZAP scan:** not run.
- **Security tests against a self-hosted Toolshop:** only the read-only hosted runs were done.
- **v0.2 examples:** still syntax-checked only (roadmap R1).

### 8.6 Still open

| Priority | Item |
|---|---|
| P2 | API-side mocking (§3.6), QE in the team process and release readiness (§3.7), BDD (§3.8), template sync + demo-app drift canary (§2.2 #7–8), a "⚡ Quick path" box per task (§2.2 #4) |
| P3 | Async/event-driven questions (§3.9), Playwright TypeScript appendix (§3.10) |
| Decisions | D9 reference solutions; D14 (R-3) where learners read the path |
| Pilot | R1 verification of the remaining v0.2 examples; R3 pilot to recalibrate hours (the §2.1 estimate of 350–400 h for manual testers still needs data) |
