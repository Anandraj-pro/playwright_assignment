# Placement Check: What Can You Skip?

Already working in QA or automation? Don't spend weeks on tasks you've mastered. This check tells you which 🟢 tasks you can skip, phase by phase.

**Rules:** about 60 minutes, **closed book and no AI**, answered out loud or in writing *before* you open any answer. Setup (P00) and the capstone (P13) aren't covered: everyone does P00-00 and P00-01, and the capstone is the final proof.

**Scoring per phase (5 questions each):**

| Score | Do this |
|---|---|
| **5/5** | Skip that phase's 🟢 tasks. Still do its 🔵 and 🟣 tasks and its phase checkpoint. |
| **4/5** | Skim the 🟢 guides and answer their interview questions out loud. Do any 🟢 task behind your missed question. |
| **0–3/5** | Do the phase in full. |

Record your scores and skip list in `interview-notes/placement.md`, and share it with your buddy. Retake the check after P07 if you skipped a lot: gaps show up in the 🔵 tasks.

---

## P01 · QE fundamentals

1. Name the phases of the STLC in order.
2. A discount field accepts whole numbers from 5 to 50 (%). Which boundary values do you test?
3. Give an example of a bug with low severity but high priority.
4. What's the difference between retesting and regression testing?
5. Name the four test levels.

<details><summary><b>Answers</b></summary>

1. Requirement analysis → test planning → test design → environment and data setup → execution → closure.
2. 4, 5, 6 and 49, 50, 51 (3-value BVA), or at least 4, 5, 50, 51. Also check non-integers and empty input.
3. A misspelled company name on the home page (or a legal-text typo).
4. Retesting confirms a specific fixed bug is fixed; regression testing checks that other, previously working things still work after a change.
5. Unit, integration, system (end-to-end) and acceptance.
</details>

## P02 · Python

1. What does `[p["name"] for p in products if p["price"] < 10]` return?
2. Why use `Decimal` rather than `float` for money?
3. What's wrong with `def add(item, cart=[]):`?
4. What does a `with` statement guarantee?
5. What's the difference between `d["key"]` and `d.get("key")`?

<details><summary><b>Answers</b></summary>

1. A list of the names of products that cost less than 10.
2. Floats are binary approximations (`0.1 + 0.2 != 0.3`); `Decimal` represents decimal amounts exactly and rounds predictably.
3. The default list is created once and shared between calls, so items accumulate across calls.
4. The context manager's cleanup (`__exit__`) runs even if the block raises: files are closed, locks are released.
5. `d["key"]` raises `KeyError` if the key is missing; `d.get("key")` returns `None` (or a default you pass).
</details>

## P03 · pytest

1. How does pytest find tests by default?
2. Write a parametrised test that checks `is_even()` for 2, 3 and 0.
3. What is a fixture's scope? Name two scopes.
4. What does `yield` do inside a fixture?
5. Which option re-runs only the tests that failed last time?

<details><summary><b>Answers</b></summary>

1. Files named `test_*.py` or `*_test.py`, functions named `test_*`, and methods named `test_*` in classes named `Test*` without an `__init__`.
2. `@pytest.mark.parametrize(("n", "expected"), [(2, True), (3, False), (0, True)])` on `def test_is_even(n, expected): assert is_even(n) is expected`.
3. How long one fixture instance lives and is shared: `function` (the default), `class`, `module`, `package`, `session`.
4. Everything before `yield` is setup; the yielded value goes to the test; everything after `yield` is teardown and runs even if the test fails.
5. `--lf` (`--last-failed`).
</details>

## P04 · API testing

1. What's the difference between PUT and PATCH?
2. What does 401 mean, compared with 403?
3. Write a `requests` call that GETs `/booking` with a 10-second timeout.
4. Is POST idempotent? Which common methods are?
5. Why validate the response schema as well as the status code?

<details><summary><b>Answers</b></summary>

1. PUT replaces the whole resource with the body you send; PATCH changes only the fields you send.
2. 401: not authenticated (no or invalid credentials). 403: authenticated but not allowed.
3. `requests.get(f"{BASE}/booking", timeout=10)`.
4. No. GET, PUT, DELETE (and HEAD, OPTIONS) are idempotent: repeating them has the same effect as doing them once.
5. A 200 can still carry a wrong or missing field, a wrong type or a changed contract; schema validation catches those automatically.
</details>

## P05 · UI testing with Playwright

1. What are browser, context and page?
2. Which locator would you choose for a "Login" button, and why?
3. Why use `expect(locator).to_have_text(...)` instead of `assert locator.inner_text() == ...`?
4. How do you handle a JavaScript `alert` in Playwright?
5. What is the Page Object Model?

<details><summary><b>Answers</b></summary>

1. Browser: the browser process. Context: an isolated, incognito-like profile (cookies, storage). Page: one tab inside a context.
2. `page.get_by_role("button", name="Login")`: it's how users and assistive technology find it, and it survives CSS changes.
3. `expect` retries until the condition holds or times out; a plain `inner_text()` read races the page rendering.
4. Register a handler before the action: `page.on("dialog", lambda d: d.accept())` (or `dismiss`).
5. Each page or component is a class holding its locators and user-level actions, so tests read like flows and locator changes happen in one place.
</details>

## P06 · Database testing

1. What's the difference between INNER JOIN and LEFT JOIN?
2. Write SQL for the 5 customers with the most rentals (`rental` has `customer_id`).
3. What's the difference between WHERE and HAVING?
4. How do you check that an API call created the right database row?
5. What does a foreign key prevent?

<details><summary><b>Answers</b></summary>

1. INNER returns only matching rows from both tables; LEFT returns all rows from the left table, with NULLs where there's no match.
2. `SELECT customer_id, COUNT(*) AS rentals FROM rental GROUP BY customer_id ORDER BY rentals DESC LIMIT 5;`
3. WHERE filters rows before grouping; HAVING filters groups after aggregation.
4. Create the data through the API with unique values, then query the database for exactly that row by its ID or unique value and compare fields. Never assume "the last row" is yours.
5. Orphaned rows: a child row that points at a parent that doesn't exist (referential integrity).
</details>

## P07 · Parallel execution

1. What does `pytest -n auto` do?
2. Give two reasons a test passes alone but fails in parallel.
3. How do you make test data unique per test?
4. What is `--dist loadgroup` for?
5. What's the difference between workers and shards?

<details><summary><b>Answers</b></summary>

1. With pytest-xdist, it starts one worker process per CPU core and spreads the tests across them.
2. Shared data (the same user or cart), shared global state, order dependence, and fixed ports or files.
3. Generate unique values per test (UUIDs, a worker ID prefix, factories) and create the data in the test's own setup.
4. Tests marked with the same `xdist_group` run on the same worker, which keeps tests that must share a resource together.
5. Workers are processes on one machine; shards split the suite across machines or CI jobs.
</details>

## P08 · Docker

1. What's the difference between an image and a container?
2. What does `-p 8080:80` mean?
3. What's the difference between `docker compose down` and `down -v`?
4. Why pin image versions instead of using `latest`?
5. Why run a test suite inside a container?

<details><summary><b>Answers</b></summary>

1. An image is a read-only template; a container is a running (or stopped) instance of it.
2. Host port 8080 forwards to port 80 inside the container.
3. `down` removes containers and networks but keeps volumes; `down -v` also deletes volumes (and your data).
4. `latest` changes underneath you, so builds aren't reproducible; pinned versions change only when you decide.
5. The same OS, Python, browsers and fonts everywhere, locally and in CI, which removes "works on my machine".
</details>

## P09 · CI with GitHub Actions

1. Define workflow, job and step.
2. How do two jobs share files?
3. How do you use a secret in a workflow?
4. What is a required check?
5. Why use `concurrency` with `cancel-in-progress` on PR workflows?

<details><summary><b>Answers</b></summary>

1. Workflow: a YAML file triggered by events. Job: a set of steps on one runner. Step: a shell command or an action.
2. Upload an artifact in one job and download it in another (jobs don't share a filesystem).
3. Store it in the repository or environment secrets and reference it as `${{ secrets.NAME }}`, ideally passed to steps through `env`.
4. A status check that must succeed before a PR can be merged into a protected branch.
5. When you push again, the run for the older commit is cancelled, which saves runner time and gives faster feedback.
</details>

## P10 · Reporting, bugs and flaky tests

1. Name five parts of a good bug report.
2. What is a flaky test?
3. Should failed tests be retried automatically?
4. What is test quarantine?
5. Which metric tells you testing missed something?

<details><summary><b>Answers</b></summary>

1. Title, steps to reproduce, expected result, actual result, environment and version, severity, and evidence (screenshots, logs, traces).
2. A test that passes and fails on the same code without any change.
3. Not silently. Retries can hide real bugs and flakiness; if used, report retried tests and track them as flaky.
4. Moving known-flaky tests out of the blocking gate into a separate, tracked lane, with an owner and a deadline to fix or delete them.
5. Escaped defects: bugs found after release, ideally by severity.
</details>

## P11 · Non-functional testing

1. What's the difference between a load test and a stress test?
2. Why report p95 rather than the average response time?
3. What does "WCAG 2.2 AA" mean?
4. What is BOLA (IDOR)?
5. Can automated tools find every accessibility problem?

<details><summary><b>Answers</b></summary>

1. Load: expected traffic, checked against targets. Stress: beyond expected traffic, to find the breaking point and see how it fails.
2. Averages hide the slow tail; p95 shows what the slowest 5% of users experience.
3. Meeting all level A and AA success criteria of version 2.2 of the Web Content Accessibility Guidelines, the usual legal target.
4. Broken Object Level Authorization: a logged-in user can access another user's object by changing its ID.
5. No. Tools find a minority of issues; keyboard and screen-reader testing are still needed.
</details>

## P12 · AI in QA

1. What is hallucination, and how do you reduce it?
2. What is MCP?
3. What is a skill for an AI coding assistant?
4. Why keep AI checks in CI advisory rather than blocking?
5. How do you know whether an AI agent is good?

<details><summary><b>Answers</b></summary>

1. Confident but false output. Reduce it by grounding with real context, constraining the task, validating outputs and reviewing them.
2. The Model Context Protocol: an open standard for connecting AI applications to tools and data through servers.
3. A packaged, reusable set of instructions (and optionally scripts) that the assistant loads for a matching task.
4. LLM output is non-deterministic and can be wrong, so blocking gates should stay deterministic; AI adds advice that a human verifies.
5. Evaluate it: a fixed set of cases with known answers, a measured accuracy threshold, and a re-run whenever the prompt or model changes.
</details>
