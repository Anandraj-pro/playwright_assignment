# QE Hands-On Lab: Project Expectations

| Field | Value |
|---|---|
| Document | Project Expectations |
| Status | Draft v0.3 (QE-leader review P1 fixes applied; see [`REVIEW_QE_LEADER.md`](REVIEW_QE_LEADER.md)) |
| Last updated | 2026-09-23 |
| Owner | _TBD (repo maintainer)_ |
| Reviewers | _TBD (QE leads / mentors)_ |
| Working repo name | `qe-hands-on-lab` (template) → each learner creates `qe-hero-<name>` |

---

## 1. Purpose

Quality Engineers learn modern automation fastest by building it, not reading about it. This repository is a **hands-on, interview-oriented learning path** that takes a QE from **zero to super hero**:

> **QE fundamentals → Python → pytest → API testing (requests) → UI testing (Playwright) → DB testing → parallel execution → Docker → GitHub Actions CI gates → performance, accessibility and security → AI in QA (MCP servers, skills, agents, adoption)**

Every task runs against **free, open-source demo applications** (UI, API and sample databases; see [`learning-path/DEMO_APPS.md`](../learning-path/DEMO_APPS.md)). Each learner works **in their own copy of this repo**, reading each task there and building the solution in the same repo. By the end, their work runs in containers, in parallel, behind CI gates, with AI tooling that helps rather than replaces the engineer, and they have rehearsed interviews at every step.

### 1.1 Problem this solves

- Tutorials cover tools in isolation. Real QE work needs them **integrated**: a UI test that seeds data via API, verifies it in the DB, and runs in parallel in a container in CI.
- Hosted demo sites alone give **no DB access** and change without notice. So we pair them with **self-hostable** apps (Toolshop, Restful-Booker, Pagila) that run locally in Docker.
- Learning and interview prep are usually separate. Here **every task ends with interview Q&A**, and every phase ends with a mock-interview checkpoint.
- Teams want to "adopt AI in QA" but lack a **safe sandbox** and a playbook for where it adds value.

---

## 2. Goals and Non-Goals

### 2.1 Goals

1. A **Zero → Hero → Super Hero learning path**: 78 tasks in 14 phases (P00–P13), about 301 hours, with a ⭐ **Essentials track** (30 tasks, ~89 hours) that every new engineer does first.
2. **Every task is self-contained**, with: 📋 task and "done when" checklist · 📘 user guide (concepts, deep dive, **3 worked examples: low / medium / high-complex**) · 🎤 **interview Q&A with model answers** · 🤖 guidance on using AI for the task.
3. Use **identified open-source demo apps** for UI, API and DB, runnable hosted *and* self-hosted via Docker.
4. Learners build a **reference-quality framework** in their own repo (config, API clients, page objects, DB layer, data factories, pytest plugin).
5. Demonstrate **real CI quality gates** on GitHub Actions: static checks, build and scan, smoke, regression, nightly reporting.
6. Demonstrate **practical AI adoption in QA**: using MCP servers, building one, writing skills, building an evaluated triage agent, testing LLM features, and writing an adoption playbook.
7. Keep everything **runnable on a laptop or in Codespaces**, with no paid services required except an optional LLM API key (every AI lab has an offline path).
8. **Fast time to first value** for new engineers: green UI and API tests on day 1, CI on every PR from week 2, a pre-configured skeleton, and tasks learners can check themselves (`scripts/check_task.py`, the `task-check` workflow).
9. Teach **quality engineering, not only automation**: test design and risk come before code (P01), and non-functional testing is part of v1 (P11).

### 2.2 Non-Goals (v1)

| Out of scope | Reason / future |
|---|---|
| Production-scale capacity testing | P11 teaches the method on local stacks; real capacity numbers need a dedicated environment |
| Penetration testing / active DAST scans | P11 covers QE-level checks and *passive* ZAP baselines only |
| Mobile native (Appium) | Different toolchain (mobile *web* emulation is covered in P05-07) |
| BDD (pytest-bdd / Gherkin) | Optional stretch only (v1.1 candidate) |
| Selenium as a main tool | Playwright only; P05-08 reads and migrates a small Selenium suite |
| Kubernetes / cloud deployment | Docker Compose is the ceiling for v1 |
| Building our own app to test | We use maintained open-source demo apps instead (decision D1) |

---

## 3. Audience, Levels and Prerequisites

### 3.1 Levels

| Badge | Level | Learner can… | Interview target |
|---|---|---|---|
| 🟢 | **Zero** | Follow a guide, write working tests, explain the basics | Associate / Junior QE (0–2 yrs) |
| 🔵 | **Hero** | Design and build independently, debug, make trade-offs | QE / SDET (2–5 yrs) |
| 🟣 | **Super Hero** | Architect, scale, automate the automation, lead AI adoption | Senior / Lead SDET, QE Architect (5+ yrs) |

Interview questions are tagged **[Z] / [H] / [SH]** to match.

### 3.2 Learner personas

| Persona | Starting point | Recommended path |
|---|---|---|
| **New engineer (any background)** | Joining a team | ⭐ Essentials track first (30 tasks, ~89 h), with a buddy (`learning-path/SUPPORT.md`) |
| **Manual QA moving to automation** | Test design skills, little code | Essentials, then the remaining 🟢 and 🔵 tasks in phase order; 🟣 on a second pass |
| **Junior SDET** | Some Python/Selenium | Take the placement check (`learning-path/PLACEMENT.md`), skip what it allows, then 🔵 and 🟣 from P03 onward |
| **Experienced SDET / QE lead** | Strong automation | Placement check, then focus on P07–P13 🟣 |

### 3.3 Prerequisites

- No coding or test-design experience required: P00 and P01 start from zero. Basic terminal use helps.
- A GitHub account. Either GitHub Codespaces (nothing to install; the template ships a dev container) or a machine with 8 GB RAM minimum (16 GB recommended), ~15 GB free disk and a Docker-compatible runtime. Windows users work inside WSL2.
- Optional: an LLM API key for live P12 labs.

---

## 4. Learning Outcomes

After completing the path, a learner can:

1. Decide what to test: test levels and types, test-design techniques (partitions, boundaries, decision tables, state transitions, pairwise), test cases and traceability, story review and risk-based testing.
2. Write clean, typed Python for automation, and pass Python coding rounds with QA-flavoured problems.
3. Debug failing tests systematically, and design pytest suites with fixtures, parametrisation, markers, custom options, hooks and plugins.
4. Build a requests-based API layer with auth, schema validation, negative matrices and contract tests.
5. Build Playwright tests with resilient locators, page objects, auth-state reuse, hybrid API+UI setup, network mocking and trace-based debugging; rescue an inherited suite and plan a Selenium migration.
6. Write interview-level SQL, and verify data integrity and API/UI → DB consistency with isolated data.
7. Make suites parallel-safe, choose xdist distribution modes, and shard across CI machines with a cost model.
8. Create, run and maintain Docker images and Compose stacks (health checks, networking, pinning, scanning).
9. Build GitHub Actions pipelines with blocking gates, matrices, nightly reports and secure runner practices.
10. Report quality well: bug reports, rich reports, flaky-test policy, metrics dashboards.
11. Run performance tests with budgets, accessibility checks (axe, keyboard, screen reader) and QE-level security checks (authorisation matrix, hostile input, headers), and gate them in CI.
12. Use and build **MCP servers**, write **skills**, build and **evaluate** an agent, test LLM features, and write an **AI adoption playbook**.
13. Tell their framework story, deliver STAR stories, and handle a full interview loop.

---

## 5. Demo Applications (System Under Test)

Full details (URLs, credentials, ports, self-host commands): **[`learning-path/DEMO_APPS.md`](../learning-path/DEMO_APPS.md)**.

| App | Layer(s) | Role in the path |
|---|---|---|
| **Practice Software Testing, "Toolshop"** | UI (Angular) + REST API (Laravel, Swagger) + MySQL | Main full-stack SUT: hybrid, DB consistency, CI stack, capstone |
| **SauceDemo** | UI | Classic interview UI app, with special users for bugs, performance and visual checks |
| **The Internet** | UI edge cases | Frames, dialogs, tabs, uploads/downloads, waits |
| **Restful-Booker** | REST API | Classic interview API: auth, CRUD, negative testing |
| **Swagger Petstore v3** | REST API + OpenAPI | Contract and property-based testing |
| **Pagila** | PostgreSQL sample DB | Interview SQL, integrity rules, ephemeral DBs, CI service containers |
| **Chinook** | SQLite (plus other engines) | Zero-setup SQL basics |

### 5.1 Bug and fault sources (for bug hunts, flakiness and AI-triage labs)

| Source | Used for |
|---|---|
| Toolshop **with-bugs** version and **sprint versions** (v1–v5) | Bug hunts, capstone, schema drift / contract diffs, AI triage eval set |
| SauceDemo `problem_user`, `error_user`, `performance_glitch_user`, `visual_user` | UI bug hunts, waiting strategies, visual checks |
| Playwright `page.route` fault injection | Empty states, 500s, slow responses |
| Stopping containers / wrong URLs | Environment-failure triage |
| Planted flaky tests (P10-03) | Flake detection and quarantine |
| `legacy-suite/` (planted smells; a small Selenium suite) | Legacy rescue (P05-04), Selenium migration (P05-08) |
| Real findings observed while writing the path (Toolshop age boundaries, an unnamed button, header gaps) | Test design (P01-02), accessibility (P11-02), security (P11-03) |

---

## 6. Technology Stack

Exact versions are pinned in each learner's `pyproject.toml`/`uv.lock`, Dockerfiles and workflows, and Dependabot keeps them current.

| Area | Choice |
|---|---|
| Language / env | Python 3.12+ (3.13 recommended), `uv` |
| Test runner | `pytest` (+ `pytest-xdist`, `pytest-randomly`, `pytest-split`, `pytest-repeat`, `pytest-rerunfailures`, `pytest-cov`) |
| UI | `playwright` + `pytest-playwright` (sync API) |
| API | `requests`, `pydantic` v2, Schemathesis (contract), `oasdiff` (spec diff) |
| DB | `sqlite3`, SQLAlchemy 2 + `psycopg` 3 (Postgres) + `PyMySQL` (Toolshop MySQL), `testcontainers` |
| Test data | `Faker` + factory functions |
| Reporting | JUnit XML, `pytest-html`, Allure (P10) |
| Quality | `ruff`, `mypy`, `pre-commit`, `gitleaks`, `actionlint`, `hadolint`, `trivy` |
| Containers / CI | Docker + Compose v2, Buildx, GitHub Actions, GHCR |
| Non-functional | Locust (performance), axe-core (accessibility), OWASP ZAP baseline in Docker (security) |
| Onboarding | Dev container / GitHub Codespaces, pre-configured skeleton, `scripts/check_task.py` + `task-check` workflow |
| AI | MCP Python SDK (`mcp`), Playwright MCP, Anthropic SDK / Claude Agent SDK, Claude Code skills; model ID configurable via `QE_AI_MODEL` |

---

## 7. Repository Structure

**This template repo:**
```text
qe-hands-on-lab/
├── README.md                        # the learner's landing page (they personalise it in P00-01)
├── pyproject.toml, uv.lock          # pre-configured skeleton: deps, ruff, mypy, pytest
├── Makefile                         # install | lint | format | test | smoke | check TASK=… | tracker
├── .pre-commit-config.yaml          # gate G0: ruff (from the lockfile) + gitleaks
├── .devcontainer/devcontainer.json  # Codespaces / dev container, the day-1 default
├── .github/workflows/task-check.yml # checks the deliverables of task/Pxx-yy-… PRs
├── .env.example, .gitignore
├── framework/__init__.py            # empty package learners grow from P02
├── tests/unit/test_sanity.py        # so `make test` has something to run on day 1
├── interview-notes/README.md        # the per-task notes format check_task.py looks for
├── legacy-suite/                    # deliberately bad inherited tests (Playwright + Selenium)
├── docs/
│   ├── PROJECT_EXPECTATIONS.md      # this document
│   └── REVIEW_QE_LEADER.md          # QE-leader review of v0.2 and its implementation status
├── learning-path/
│   ├── README.md                    # how to use the path: levels, tracks, task loop, rules
│   ├── DEMO_APPS.md                 # identified UI / API / DB apps
│   ├── SUPPORT.md                   # buddies, cadence, the 2-hour rule, PR review rubric
│   ├── PLACEMENT.md                 # placement check: what experienced learners can skip
│   ├── TASKS.md                     # master tracker with the ⭐ Essentials marker (generated)
│   ├── task-tracker.csv             # the same list for spreadsheets / issue automation (generated)
│   └── phases/
│       ├── P00-git-setup.md … P13-capstone-interviews.md   # tasks + user guides + interview Q&A
└── scripts/
    ├── build_tracker.py             # regenerates TASKS.md + CSV from the phase files
    └── check_task.py                # checks one task's deliverables (make check TASK=…)
```

**Each learner's repo grows into** (the full layout is in `learning-path/README.md` §4): `framework/` (config, api, pages, db, data), `tests/` (hello, unit, api, ui, db, e2e, a11y, security), `perf/`, `python_basics/`, `sql/`, `docker/`, `docker-compose.yml`, `.github/workflows/`, `ai/` (prompts, MCP server, agents, evals), `.claude/skills/`, `docs/`, and `interview-notes/`.

---

## 8. Curriculum

| Phase | Topic | Tasks (🟢/🔵/🟣) | Hours | Key deliverables |
|---|---|---|---|---|
| P00 | Setup, Git, first automation and safe AI | 8 (6/1/1) | 20 | Day-1 UI + API tests, own repo, PR workflow, skeleton tour, CI from week 2, AI guardrails |
| P01 | **QE fundamentals** | 5 (4/1/0) | 17 | SDLC/STLC, test-design techniques on real rules, test cases + traceability, story review and risk, prompting for test design |
| P02 | Python for QE | 7 (3/3/1) | 23 | Data/money utilities, retry/wait/config, coding drills, typed framework |
| P03 | pytest | 6 (3/2/1) | 17 | Debugging lab, fixtures, parametrisation, `--env`, a custom plugin with tests |
| P04 | API testing (requests) + Docker as a user | 8 (4/3/1) | 28 | Client layer + models, negative matrix, local demo stack, Toolshop API, contract tests |
| P05 | UI testing (Playwright) | 8 (2/4/2) | 32 | POM, legacy-suite rescue, tricky UI patterns, auth reuse, hybrid, mocking, DevTools + traces, visual, Selenium migration |
| P06 | Database testing | 5 (1/3/1) | 23 | Interview SQL, integrity rules, API/UI→DB consistency, ETL checks |
| P07 | Parallel execution | 4 (1/2/1) | 13 | Parallel-safe suite, distribution modes, sharding cost model |
| P08 | Docker: build, compose, maintain | 3 (0/2/1) | 12 | Test-runner image, Compose with health checks, maintenance and devcontainer upkeep |
| P09 | GitHub Actions and CI gates | 5 (1/3/1) | 19 | Smoke gate, full stack in CI, nightly + Pages, reusable workflows |
| P10 | Reporting and flaky tests | 4 (1/2/1) | 14 | Bug reports, Allure, quarantine policy, metrics dashboard |
| P11 | **Non-functional testing** | 4 (0/3/1) | 18 | Locust + budgets, axe/keyboard/screen reader, authorisation matrix + hostile input, nightly non-functional gates |
| P12 | AI in QA (advanced) | 6 (0/3/3) | 29 | MCP usage and server, skills, triage agent + evals, LLM feature tests, playbook |
| P13 | Capstone and interviews | 5 (0/3/2) | 36 | Framework story, capstone on Toolshop (incl. one non-functional risk), live-coding drills, STAR, mock loops |
| | **Total** | **78 (26/35/17)** | **301** | ⭐ Essentials: 30 tasks, 89 h |

**Task format (mandatory for every task):** title and meta line (level, time, app, deliverable) → 📋 Task (steps + "done when") → 📘 User guide (Concepts, Deep dive, Examples 🟢 Low / 🔵 Medium / 🟣 High-complex) → 🎤 Interview Q&A (collapsible model answers, level-tagged) → 🤖 AI assist. **Every phase ends** with a 🏁 checkpoint (a no-AI self-test plus an AI mock-interviewer prompt).

---

## 9. Engineering and Test-Design Standards

These apply to all example code and learner submissions (each is taught in the phase noted):

1. **Independent tests**: own their data, pass under `-n auto` and random order (P03, P07).
2. **No hard waits**: `expect`, `wait_until`, network waits only (P02-05, P05).
3. **Arrange fast, assert where it matters**: API/DB setup, UI for the behaviour under test (P05-06).
4. **Config over constants**: typed settings from env, `.env.example` documented (P02-05, P03-05).
5. **No secrets in Git**: gitleaks in pre-commit and CI (P00-04, P09).
6. **Locator priority**: role → label/placeholder → test id → CSS. XPath justified (P05-02).
7. **Every HTTP call has a timeout**, and clients return typed models (P04).
8. **Readable tests**: behaviour-named, one behaviour per test, assertion messages with context (P03).
9. **Typed framework code** with its own unit tests and coverage (P02-07, P03-06).
10. **Flaky policy**: detect, don't hide. Quarantine with an issue and a 14-day SLA (P10-03).
11. **Evidence on failure**: traces, screenshots, API exchanges, container logs (P05-07, P09, P10).
12. **AI-generated code** meets the same bar and is disclosed in PRs (P00-06).
13. **Tests must be able to fail**: every new test is seen failing once (P00-00, P03-02), and reviews check it first (SUPPORT.md §4).
14. **Non-functional thresholds live in files**: performance budgets, ZAP rules and accessibility allowlists change only through reviewed PRs (P11).

---

## 10. CI/CD Quality Gates (started in P00-05, completed in P09 and P11)

| Gate | Trigger | Checks | Blocking | Time budget |
|---|---|---|---|---|
| **G0 Local** | `pre-commit` | ruff, gitleaks, YAML/TOML | Local | < 15 s |
| **G1 Static** | Every push / PR (from P00-05) | ruff, mypy, unit tests + coverage, gitleaks, actionlint | ✅ | < 2 min |
| **G2 Build and Scan** | Docker/dependency changes + `main` | Build test image, trivy (CRITICAL), push to GHCR | ✅ | < 6 min |
| **G3 Smoke** | Every PR | API + UI smoke (Chromium), `-n 2` against public apps | ✅ | < 10 min |
| **G4 Regression** | Merge + nightly | Browser × shard matrix, DB service container, Toolshop stack E2E | ✅ on `main`; nightly reports | < 15 min wall-clock |
| **G5 AI Advisory** | After failed CI | Triage summary comment | ❌ advisory | < 5 min |
| **G6 Non-functional** | Nightly + on demand (P11-04) | Locust performance smoke + per-endpoint budgets, ZAP baseline (FAIL-level rules), axe gate | ✅ nightly | < 30 min |
| **Task check** | PRs from `task/…` branches (shipped) | Task deliverables exist, tests collected, interview notes written | ✅ | < 3 min |

A single aggregator `gate` job is the required status check. It's merge-queue ready.

---

## 11. Docker Expectations (used from P04-05, built by learners in P08)

- `make stack-up` starts the self-hosted demo apps. `make docker-test` runs the suite in a container.
- Health checks gate tests (real readiness queries, not "container started").
- Images are pinned and scanned, run as non-root, and the Playwright image version matches the package version (enforced at build time).
- Docs cover Docker Desktop alternatives, Apple Silicon (multi-arch), and the SPA/localhost networking trap.
- A dev container (and so Codespaces) is shipped with the template for day 1 and maintained by learners in P08-03.

---

## 12. AI Adoption: Principles and Guardrails (from P00-06; advanced in P12)

| QA activity | AI use in the path | How it's measured |
|---|---|---|
| Test design | Story → test ideas prompts (P01-05) | Stability across runs, reviewer acceptance |
| Authoring | Skills + Playwright MCP (P12-01, P12-03) | Edits needed, mutation checks on generated tests |
| Tooling | Custom MCP server (P12-02) | Unit tests, security tests on guards |
| Failure triage | Agent + eval set (P12-04) | Accuracy, confusion matrix |
| AI features | Evals, LLM-as-judge, injection tests (P12-05) | Pass rate vs threshold, judge agreement |
| Team adoption | Advisory CI + playbook (P12-06) | Baseline vs day-90 metrics |

**Guardrails (non-negotiable):** human in the loop · same review bar and CI gates · blocking gates stay deterministic · least-privilege tools (read-only DB roles, allow-lists) · no secrets or PII in prompts · pinned model IDs and versioned prompts · evaluate before trusting · disclose AI assistance · cost awareness · treat tool and page content as untrusted (prompt injection).

---

## 13. Definition of Done

### 13.1 For a task (content authors)
- [ ] Follows the mandatory task format (§8) with a valid meta line (parsed by `scripts/build_tracker.py`)
- [ ] 3 examples (low/medium/high) that are syntax-checked and verified against the current demo apps
- [ ] ≥4 interview Q&As with level tags and model answers
- [ ] Dry-run by someone other than the author, with the time estimate within ±25%

### 13.2 For learning-path v1.0
- [x] All phases drafted *(v0.1: 12 phases, 66 tasks; v0.3: 14 phases, 78 tasks, 2026-09-23)*
- [x] Demo-app catalogue verified *(2026-09-23)*
- [x] Tracker and CSV generated from the phase files, with the Essentials marker
- [x] QE-leader review done and its P1 fixes applied *(2026-09-23; see `REVIEW_QE_LEADER.md` §8)*
- [x] Self-check tooling: `scripts/check_task.py` and the `task-check` workflow
- [ ] Every example executed end to end against live/self-hosted apps *(v0.3's new examples were run against the live apps; older examples are syntax-checked only)*
- [ ] A pilot cohort (≥5 QEs) completes P00–P09, and their feedback is addressed
- [ ] Mentor answer keys or reference solutions for 🟣 tasks on a protected branch

---

## 14. Contribution Workflow

- Branch from `main` (`content/P05-…`, `fix/…`), use conventional commits, and open a PR with the template.
- After editing any phase file, run `python scripts/build_tracker.py` and commit the regenerated `TASKS.md` and CSV.
- Demo-app drift (a changed URL, locator or endpoint) is fixed in `DEMO_APPS.md` plus the affected guides, with a new verification date.
- Structural or tooling decisions get an ADR in `docs/adr/`.

---

## 15. Roadmap

| Phase | Scope | Exit criteria |
|---|---|---|
| **R0 Draft** ✅ | Expectations, demo-app catalogue, 12 phase guides, tracker | Content complete (v0.1) |
| **R0.5 Leader review** ✅ | QE-leader review; P1 fixes: fundamentals and non-functional phases, day-1 start, skeleton + devcontainer, check tooling, support model, placement check, resequencing | v0.3: 14 phases, 78 tasks |
| **R1 Verify** | Execute every example against the live and self-hosted apps and fix drift | All examples run, verification date updated |
| **R2 Reference build** | Maintainers build a reference learner repo (on a protected branch) through P09 | CI green on the reference repo |
| **R3 Pilot** | 5+ learners with buddies (SUPPORT.md), weekly office hours, feedback per phase. **Task IDs freeze here.** | ≥85% finish Essentials; estimates recalibrated |
| **R4 v1.0** | Apply pilot feedback, add answer keys, tag release | §13.2 complete |
| **v1.1 candidates (review P2)** | API-side mocking, QE in the team process (estimation, release readiness), BDD, template sync + demo-app drift canary | Prioritised after the pilot |
| **v2 candidates** | Mobile (Appium), Playwright TypeScript appendix, event-driven systems | Prioritised by demand |

---

## 16. Success Metrics

| Category | Metric | Target |
|---|---|---|
| Onboarding | Time to first green test against a real app | ≤ 1 day (P00-00) |
| Onboarding | Time to first CI-gated PR | ≤ 40 learning hours (P00-05 sits at hour 12) |
| Onboarding | Essentials track completion | ≥85% of starters, within 9 weeks part-time |
| Onboarding | Drop-off per phase / blocked time | < 15% / fewer than 1 "stuck > 2 h without help" per phase |
| Content | Actual vs estimated hours per task | Within ±30% after recalibration |
| Learning | Pilot learners completing P00–P09 | ≥80% within 20 weeks |
| Learning | Capstone (P13-02) pass rate | ≥70% on first submission |
| Interview | Mock-loop average score (P13-05), loop 1 → loop 2 | +0.5 or more |
| Interview | Learners reporting interview success within 6 months | Tracked (opt-in) |
| Repo health (learner repos) | PR gate duration / flake rate | ≤10 min / <2% |
| Content | Examples verified against live apps | 100% at each release |
| AI | Triage agent accuracy on the learner's eval set | ≥80% |

---

## 17. Roles and Responsibilities

| Role | Responsibilities |
|---|---|
| **Maintainer / Owner** | Roadmap, demo-app verification, tracker generation, releases, standards |
| **Phase author** | Keeps a phase's guides accurate and verified, and answers learner questions |
| **Mentor / Reviewer** | Reviews 🟣 tasks and the capstone, runs office hours and mock interviews, collects feedback |
| **Buddy** | A peer one or two phases ahead: weekly check-in, first stop when stuck, rubric reviews (SUPPORT.md) |
| **Learner** | Works in their own repo, follows the task loop and rules, writes interview notes, gives feedback |

---

## 18. Risks and Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Demo apps change, move or go offline | Broken tasks | Prefer self-hosted pinned versions; verification date in DEMO_APPS.md; guides tell learners to confirm locators with codegen; drift fixes are welcome PRs |
| Public demo apps rate-limit or get hammered | Flaky learner runs | Guides cap workers against hosted apps (`-n 2`); heavy runs use the local stack |
| Tool churn (Playwright, AI SDKs, MCP, Actions) | Stale instructions | Pinned versions + Dependabot; quarterly review of P09 and P12 |
| Self-hosted runners on public repos | Remote code execution | P09-05 restricts them to private forks with ephemeral runners, plus a security doc |
| LLM API keys and cost | Blocks P12 | Offline record/replay paths; costs stated; live runs optional |
| Docker licensing / laptop limits / locked-down laptops | Can't run the stack | Codespaces + dev container are the day-1 default (P00-00); Colima/Rancher/Podman alternatives; WSL2 for Windows (P00-01) |
| Shared demo accounts locked by other people | Flaky logins on hosted apps | Seen on 2026-09-23 (`customer@…`); guides use `customer2/3`, own registered users, or the self-hosted stack |
| Learners stall without feedback | Drop-off, slow onboarding | Self-check (`check_task.py`, task-check), buddy + 2-hour rule, rubric reviews (SUPPORT.md) |
| Learners' template copies go stale | Following outdated instructions | Open (review R-3, v1.1): read the path centrally or add `make sync-path` |
| Learners copy model answers without understanding | Weak interviews | Collapsible answers, "answer out loud first" rule, no-AI checkpoints, live-coding drills |
| Scope creep | Delays v1 | Non-goals (§2.2); v2 candidate list |

---

## 19. Decisions

| # | Decision | Outcome |
|---|---|---|
| D1 | App under test: build our own vs adopt existing | ✅ **Adopt open-source demo apps** (Toolshop as the main full-stack app, plus SauceDemo, The Internet, Restful-Booker, Petstore, Pagila, Chinook) |
| D2 | Dependency tool | ✅ **uv** (pip export possible) |
| D3 | Reporting | ✅ JUnit + pytest-html in the core path, Allure in P10-02 |
| D4 | Levels | ✅ **Zero / Hero / Super Hero** for tasks and interview questions |
| D5 | AI tooling | ✅ MCP as the neutral protocol; Claude Code / Anthropic SDK / Claude Agent SDK for concrete labs; model ID configurable |
| D6 | Where learners work | ✅ **Their own repo** created from this template; tasks are read and done in the same repo |
| D7 | Playwright API style | ✅ Sync (matches pytest-playwright) |
| D8 | Repo visibility | ⏳ Open: affects self-hosted runner labs (private forks recommended for P09-05) |
| D9 | Reference solutions | ⏳ Open: protected branch vs private repo (the review recommends a private repo that also powers `check_task.py` and a drift canary) |
| D10 | Phase structure | ✅ **Renumbered to 14 phases before the pilot** (v0.3); task IDs freeze from R3 |
| D11 | Non-functional testing | ✅ **In v1** as P11 (performance, accessibility, security) |
| D12 | Onboarding | ✅ **Essentials track** (30 tasks, ~89 h) + placement check + support model |
| D13 | Day-1 environment | ✅ Pre-configured skeleton; Codespaces/dev container as the default route |
| D14 | Where learners read the path | ⏳ Open: central repo or site vs template copy (review R-3) |

---

## 20. Glossary

- **SUT**: System Under Test, here the demo apps listed in §5.
- **Gate**: a CI check that must pass before code can merge or release.
- **MCP (Model Context Protocol)**: an open protocol that lets AI assistants use external tools and data via "MCP servers".
- **Skill**: a packaged, reusable instruction set (`SKILL.md` plus optional files) that teaches an AI assistant a team-specific workflow.
- **Agent**: an LLM-driven program that calls tools in a loop to reach a goal (e.g. triaging failures).
- **Eval**: a labelled dataset plus metrics used to measure AI behaviour statistically.
- **Quarantine**: marking a known-flaky test so it's excluded from blocking gates while it's tracked for a fix.
- **Sharding**: splitting a test suite across multiple CI jobs to run concurrently.
- **STAR**: Situation, Task, Action, Result, a structure for behavioural interview answers.
- **Essentials track**: the 30 tasks (⭐ in TASKS.md) every new engineer does first.
- **BOLA / IDOR**: Broken Object Level Authorization, reading or changing another user's object by changing its ID.
- **WCAG**: the Web Content Accessibility Guidelines; level AA is the usual legal target.
- **Test smell**: a pattern in test code that signals a deeper problem (sleeps, order dependence, assertions that can't fail).
