# QE Learning Path: Zero → Hero → Super Hero

A task-based path that takes a Quality Engineer from **zero** to **super hero** across:

**QE fundamentals (test design, risk) · Python · pytest · API testing (requests) · UI testing (Playwright) · DB testing · parallel execution · Docker · GitHub Actions CI gates · performance, accessibility and security · AI in QA (MCP servers, skills, agents)**

and prepares you for **interviews at every step**. Each task has:

| Part | What you get |
|---|---|
| 📋 **Task** | What to build, where it goes in *your* repo, and a "done when" checklist |
| 📘 **User guide** | Key concepts, a deep-dive explanation, and **3 worked examples**: 🟢 Low · 🔵 Medium · 🟣 High/Complex |
| 🎤 **Interview Q&A** | Real interview questions with model answers (hidden until you click, so answer out loud first) |
| 🤖 **AI assist** | How to use AI on *this* task without skipping the learning |

All tasks target free demo apps (UI, API, DB). See **[DEMO_APPS.md](DEMO_APPS.md)**.

---

## 1. Levels and tracks

| Badge | Level | You can… | Interview target |
|---|---|---|---|
| 🟢 | **Zero** | Follow a guide, write working tests, explain the basics | Associate / Junior QE (0–2 yrs) |
| 🔵 | **Hero** | Design and build independently, debug, make trade-offs | QE / SDET (2–5 yrs) |
| 🟣 | **Super Hero** | Architect, scale, automate the automation, teach others, lead AI adoption | Senior / Lead SDET, QE Architect (5+ yrs) |

Interview questions are tagged **[Z]**, **[H]** or **[SH]** by the level they're typically asked at.

**Pick a track:**

| Track | For | Tasks | Time | You come out able to… |
|---|---|---|---|---|
| ⭐ **Essentials** | Every new engineer, first | 30 (marked ⭐ in [TASKS.md](TASKS.md)) | ~89 h: about 2½ weeks full-time or 9 weeks at 10 h/week | Run and extend a team's API and UI suites, decide what to test, debug failures, work through PRs with CI, use AI safely |
| **Hero** | QE / SDET growth | All 🟢 and 🔵 | ~212 h | Pass QE/SDET interviews and build a framework on your own |
| **Super Hero** | Senior / lead growth | All 78 | ~301 h | Lead quality for a product, including CI gates, non-functional testing and AI adoption |

**Already experienced?** Take the **[placement check](PLACEMENT.md)** (60 minutes, no AI): it tells you which 🟢 tasks to skip, phase by phase.

---

## 2. Start here (day 1)

1. **Do [P00-00](phases/P00-git-setup.md#p00-00--hello-automation-your-first-ui-and-api-tests) today.** You'll create your repo from this template (**Use this template**, name it e.g. `qe-hero-<yourname>`), open it in **GitHub Codespaces** with nothing to install, and have a green UI test and API test within about 2 hours.
2. Open **[TASKS.md](TASKS.md)**: that's your tracker. Tasks marked ⭐ are the Essentials track.
3. Meet your **buddy** and read **[SUPPORT.md](SUPPORT.md)**: who helps, when, the 2-hour rule, and the PR review rubric.
4. For **every task**, follow the loop below.

**Your environment:** Codespaces works in any browser, including on locked-down company laptops. P00-01 helps you choose between Codespaces, a dev container and a local install. **On Windows,** use WSL2 for a local install. Every `make` target has a plain `uv run …` equivalent (see P00-04), so you never *need* `make`.

### The task loop

```text
Read the task + user guide
   → create a GitHub issue for it (or run the P00-07 automation)
   → branch: task/P04-02-first-api-tests
   → build it, commit often (conventional commits)
   → write your interview answers IN YOUR OWN WORDS under "## P04-02" in interview-notes/P04.md
   → make check TASK=P04-02        (files, tests, notes; lists the "done when" items)
   → open a PR, fill in the template; CI runs your gates (from P00-05) and task-check
   → peer or buddy review with the rubric (SUPPORT.md §4), then merge and tick the task in TASKS.md
```

---

## 3. Phase map

| Phase | Topic | Tasks | Hours | Main apps |
|---|---|---|---|---|
| [P00](phases/P00-git-setup.md) | Setup, Git, first automation and safe AI | 8 | 20 | SauceDemo, Restful-Booker |
| [P01](phases/P01-qe-fundamentals.md) | **QE fundamentals:** what to test and why | 5 | 17 | Toolshop, SauceDemo |
| [P02](phases/P02-python.md) | Python for QE | 7 | 23 | SauceDemo, Toolshop data |
| [P03](phases/P03-pytest.md) | pytest, including debugging | 6 | 17 | SauceDemo, Restful-Booker |
| [P04](phases/P04-api-requests.md) | API testing with requests, and Docker as a user | 8 | 28 | Restful-Booker, Toolshop, Petstore |
| [P05](phases/P05-ui-playwright.md) | UI testing with Playwright, legacy rescue and migration | 8 | 32 | SauceDemo, The Internet, Toolshop |
| [P06](phases/P06-db-testing.md) | Database testing | 5 | 23 | Chinook, Pagila, Toolshop MySQL |
| [P07](phases/P07-parallel.md) | Parallel execution | 4 | 13 | All |
| [P08](phases/P08-docker.md) | Docker: build, compose and maintain | 3 | 12 | The Internet, Restful-Booker, Pagila, Toolshop |
| [P09](phases/P09-ci-github-actions.md) | GitHub Actions and CI gates | 5 | 19 | All |
| [P10](phases/P10-reporting-flaky.md) | Reporting, bugs and flaky tests | 4 | 14 | SauceDemo, Toolshop with-bugs |
| [P11](phases/P11-non-functional.md) | **Non-functional:** performance, accessibility, security | 4 | 18 | Toolshop, Restful-Booker (self-hosted) |
| [P12](phases/P12-ai-in-qa.md) | AI in QA: MCP, skills, agents | 6 | 29 | Toolshop, Pagila |
| [P13](phases/P13-capstone-interviews.md) | Capstone and interview readiness | 5 | 36 | Toolshop |

**Total:** 78 tasks (26 🟢 · 35 🔵 · 17 🟣), about 301 hours: roughly 7 months at 10 h/week, or 15 weeks at 20 h/week.

**Early wins by design:** your first UI and API tests run on day 1 (P00-00), every PR is checked by CI from week 2 (P00-05), AI guardrails start in week 2 (P00-06), and Docker is taught (P04-05) before the first task that needs it.

---

## 4. Your repo layout (grows as you progress)

```text
qe-hero-<yourname>/
├── learning-path/            # these instructions (read-only for you)
├── README.md                 # P00-01: your goal and target role
├── pyproject.toml, uv.lock   # shipped pre-configured; explained in P00-04
├── Makefile                  # make install | lint | test | smoke | check TASK=…
├── .pre-commit-config.yaml   # gate G0: ruff + gitleaks on every commit
├── .devcontainer/            # Codespaces / dev container: zero-install setup
├── .env.example              # config keys, no secrets (extended in P02-05)
├── legacy-suite/             # deliberately bad inherited tests (P05-04, P05-08)
├── scripts/
│   ├── check_task.py         # checks a task's deliverables (make check TASK=…)
│   └── build_tracker.py      # maintainers: regenerates TASKS.md and the CSV
├── python_basics/            # P02: exercises and interview drills
├── framework/                # P02–P06: your reusable test framework
│   ├── config.py             #   settings from env
│   ├── api/                  #   requests clients (booker, toolshop, petstore)
│   ├── pages/                #   Playwright page objects (saucedemo, internet, toolshop)
│   ├── db/                   #   DB engine + queries
│   └── data/                 #   factories, test data files
├── tests/
│   ├── conftest.py
│   ├── hello/                # P00-00
│   ├── unit/                 # tests for framework/ itself, plus the P03-02 debug lab
│   ├── api/  ui/  db/  e2e/
│   ├── a11y/  security/      # P11
├── perf/                     # P11: Locust scenarios
├── sql/                      # P06: query practice with expected answers
├── docker/                   # P08: test-runner Dockerfile
├── docker-compose.yml        # P08
├── .github/workflows/        # task-check.yml (shipped) + yours from P00-05 and P09
├── ai/                       # P01-05 prompts; P12 MCP server, agents, evals
├── .claude/skills/           # P12: your AI skills
├── docs/                     # notes, test design, bug reports, strategy docs
└── interview-notes/          # P00.md … P13.md: your answers, in your words
```

---

## 5. Ground rules

1. **Run everything you write.** A task is done when the "done when" boxes are ticked, `make check` passes *and* the code runs.
2. **No hard waits** (`time.sleep`, `wait_for_timeout`) in tests. Ever. (P05 explains why; P05-04 shows the damage.)
3. **No secrets in Git.** Use `.env` locally and GitHub Secrets in CI. gitleaks guards this from day 1.
4. **Tests own their data.** Create it, use it, clean it up. Shared demo apps change under you, and shared demo accounts can even get locked by other people.
5. **Stuck for 2 hours? Ask** (SUPPORT.md §3). Staying stuck isn't dedication; it's lost time.
6. **AI rules** (from day 1; P00-06 sets them up):
   - Try first on your own (30 minutes for 🟢 tasks), *then* ask AI.
   - **Never commit code you can't explain line by line.** Interviewers will ask.
   - Tick "AI-assisted" in your PR description when you used it.
   - Never paste credentials, tokens or personal data into an AI tool.
7. **Interview answers in your own words.** Reading the model answer isn't learning. Say it out loud, write yours, *then* compare.

---

## 6. How to use the interview Q&A

Answers are hidden in collapsible blocks:

<details>
<summary><b>[Z] Example: what is the difference between a fixture and a test?</b></summary>

A test *checks behaviour*; a fixture *prepares what the test needs* (data, browser, client) and cleans up afterwards. Fixtures are injected into tests by name.

</details>

1. Read the question and **answer out loud in under 2 minutes**.
2. Expand and compare. Note what you missed under the task's heading in `interview-notes/Pxx.md` (format: [interview-notes/README.md](../interview-notes/README.md)).
3. At each phase's end, do the **🏁 Phase checkpoint**: a mini mock interview, including an AI mock-interviewer prompt.

---

## 7. Tracking progress and getting help

- **[TASKS.md](TASKS.md)**: the master checklist with every task, level, time estimate, deliverable and the ⭐ Essentials marker.
- **[task-tracker.csv](task-tracker.csv)**: the same list for Excel/Google Sheets, or for creating GitHub issues automatically (P00-07).
- **[SUPPORT.md](SUPPORT.md)**: buddy, mentor and office hours; the 2-hour rule; the PR review rubric.
- **[PLACEMENT.md](PLACEMENT.md)**: skip what you already know.
- **Maintainers:** after editing any phase file, regenerate the tracker with `make tracker` (or `python scripts/build_tracker.py`).
