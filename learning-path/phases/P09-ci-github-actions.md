# P09: GitHub Actions and CI Gates

> **Goal:** grow the lint-and-unit workflow you've had since P00-05 into a real pipeline with quality gates: smoke, DB and full-stack tests, matrix and sharding, nightly regression with published reports, container images, reusable workflows, and self-hosted runners.
> **Apps:** all. **Prerequisites:** P00-05 (your first workflow), P07, P08. **Time:** ~19 h.

| ID | Task | Level | Time |
|---|---|---|---|
| P09-01 | API + UI smoke in CI with artifacts and summaries | 🟢 | 3h |
| P09-02 | Quality gates and branch protection | 🔵 | 3h |
| P09-03 | Service containers, DB tests and the full stack in CI | 🔵 | 4h |
| P09-04 | Matrix, sharding, nightly regression and published reports | 🔵 | 4h |
| P09-05 | Images in CI, reusable workflows, environments, self-hosted runners | 🟣 | 5h |

> **Action versions:** examples use major-version tags that existed when written. Dependabot (P08-03) will propose bumps. Treat those PRs as part of your maintenance practice.

---

### P09-01 · API + UI smoke in CI with artifacts and summaries

**Level:** 🟢 Zero · **Time:** 3h · **App:** public demo apps · **Deliverable:** a `smoke` job in `ci.yml`, `scripts/junit_summary.py`

#### 📋 Task
1. Add a `smoke` job (`needs: static`) that installs Chromium (**cached** by Playwright version) and runs `-m "smoke and not db" -n 2`.
2. Produce JUnit XML, a self-contained HTML report (`pytest-html`) and Playwright traces on failure.
3. Upload them as artifacts with `if: always()` and a retention period.
4. Write `scripts/junit_summary.py` to render a markdown summary (totals plus a failures table) into `$GITHUB_STEP_SUMMARY`, and emit `::error` annotations for failures.
5. Break a UI test on purpose, then diagnose it from the downloaded trace only.

**Done when**
- [ ] The run page shows a summary table, and failing tests appear as annotations
- [ ] You diagnosed a CI failure using only its artifacts

#### 📘 User guide

**Concepts**
- **Artifacts** are files kept after the run (reports, traces). **Caches** are reusable dependency directories keyed by a hash.
- **Step conditions:** `if: always()`, `if: failure()`, `if: success()`, `if: steps.x.outputs.y == 'z'`.
- **Job summary:** markdown appended to `$GITHUB_STEP_SUMMARY` appears on the run page.
- **Workflow commands:** `echo "::error file=…,line=…::message"` creates an annotation.
- **Secrets:** `${{ secrets.NAME }}`, masked in logs and passed to steps via `env`.

**Deep dive**

**Upload evidence *especially* on failure.** A default step runs only if previous steps succeeded, so the upload step needs `if: always()`, or the trace you need is never uploaded.

**Cache vs artifact:** caches are *inputs* for speed (the uv cache, Playwright browsers) and may be evicted. Artifacts are *outputs* for humans and later jobs. Never rely on a cache for correctness.

**Browser caching key:** browsers are tied to the Playwright version, so key the cache on it. With a cache hit you still need OS dependencies (`playwright install-deps`), which aren't cached.

**Be a good citizen:** smoke against *public* demo apps uses few workers (`-n 2`). Heavier suites run against a self-hosted stack inside CI (P09-03).

**Examples**

🟢 **Low: a smoke job with artifacts**
```yaml
  smoke:
    name: G3 smoke
    needs: static
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with: { enable-cache: true }
      - run: uv sync --frozen
      - run: uv run playwright install --with-deps chromium
      - run: uv run pytest -m "smoke and not db" -n 2 --junitxml=test-results/junit.xml
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: smoke-results
          path: test-results/
          retention-days: 14
```

🔵 **Medium: browser cache, HTML report and traces**
```yaml
      - name: Resolve Playwright version
        id: pw
        run: echo "version=$(uv run python -c 'import importlib.metadata as m; print(m.version("playwright"))')" >> "$GITHUB_OUTPUT"
      - uses: actions/cache@v4
        id: pw-cache
        with:
          path: ~/.cache/ms-playwright
          key: pw-${{ runner.os }}-${{ steps.pw.outputs.version }}-chromium
      - if: steps.pw-cache.outputs.cache-hit != 'true'
        run: uv run playwright install --with-deps chromium
      - if: steps.pw-cache.outputs.cache-hit == 'true'
        run: uv run playwright install-deps chromium
      - name: Smoke
        run: >
          uv run pytest -m "smoke and not db" -n 2 --browser chromium
          --junitxml=test-results/junit.xml
          --html=test-results/report.html --self-contained-html
          --tracing retain-on-failure --screenshot only-on-failure --output test-results/playwright
```
(`uv add --dev pytest-html`.)

🟣 **High/Complex: summary and annotations from JUnit**
```python
# scripts/junit_summary.py: usage: junit_summary.py <junit.xml> [title]
import sys
import xml.etree.ElementTree as ET

def main(path: str, title: str = "Tests") -> None:
    root = ET.parse(path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    total = sum(int(s.get("tests", 0)) for s in suites)
    failed = sum(int(s.get("failures", 0)) + int(s.get("errors", 0)) for s in suites)
    skipped = sum(int(s.get("skipped", 0)) for s in suites)
    seconds = sum(float(s.get("time", 0)) for s in suites)

    print(f"### {'❌' if failed else '✅'} {title}\n")
    print("| Total | Passed | Failed | Skipped | Time |\n|---|---|---|---|---|")
    print(f"| {total} | {total - failed - skipped} | {failed} | {skipped} | {seconds:.0f}s |\n")

    failures = []
    for case in root.iter("testcase"):
        problem = case.find("failure")
        if problem is None:
            problem = case.find("error")
        if problem is not None:
            message = (problem.get("message") or "").replace("\n", " ")[:150]
            failures.append((case.get("classname", ""), case.get("name", ""), message))
            # annotation → shown on the PR "Files changed" / run page (stderr so it's not in the summary)
            print(f"::error title={case.get('name')}::{message}", file=sys.stderr)
    if failures:
        print("| Test | Message |\n|---|---|")
        for cls, name, msg in failures[:30]:
            print(f"| `{cls}::{name}` | {msg.replace('|', '/')} |")

if __name__ == "__main__":
    main(*sys.argv[1:3])
```
```yaml
      - name: Summary
        if: always()
        run: uv run python scripts/junit_summary.py test-results/junit.xml "Smoke" >> "$GITHUB_STEP_SUMMARY"
```

#### 🎤 Interview Q&A

<details><summary><b>[Z] A UI test failed in CI. How do you find out why?</b></summary>

Open the run: the job summary or annotations show which test failed and the message. Download the artifacts (HTML report, screenshot, video, Playwright trace) and open the trace to see the DOM, network and console at the failing step. Reproduce locally with the same browser, flags and container image if needed.
</details>

<details><summary><b>[H] Artifact vs cache?</b></summary>

Artifacts are outputs you keep and share (reports, traces, built packages), downloadable from the run and by later jobs. Caches are speed optimisations for inputs (dependencies, browsers), keyed by a hash and evictable. Correctness must never depend on a cache hit.
</details>

<details><summary><b>[H] Why <code>if: always()</code> on report upload steps?</b></summary>

Steps are skipped after a failure by default. Without `always()` (or `failure()`), the reports and traces are never uploaded exactly when you need them most. Use `always()` for reports and `failure()` for debug-only artifacts.
</details>

<details><summary><b>[Z] How do you use secrets in GitHub Actions?</b></summary>

Store them in repository, environment or organisation secrets, reference them as `${{ secrets.NAME }}` and pass them to steps via `env:`. They're masked in logs and unavailable to fork PRs. Never echo them, write them to artifacts, or put them in command-line arguments that get logged.
</details>

<details><summary><b>[H] Why set <code>timeout-minutes</code> on jobs?</b></summary>

The default job timeout is very long (hours). A hung browser or a request without a timeout would burn runner minutes and block the pipeline. Explicit budgets fail fast and make slowness visible.
</details>

#### 🤖 AI assist
- Ask AI to improve `junit_summary.py` (e.g. add flaky-rerun info), then write a unit test for it with a sample JUnit file.

---

### P09-02 · Quality gates and branch protection

**Level:** 🔵 Hero · **Time:** 3h · **App:** your repo · **Deliverable:** gate jobs in `ci.yml`, `.github/CODEOWNERS`, branch protection on `main`, `docs/ci-gates.md`

#### 📋 Task
1. Structure `ci.yml` into named gates: **G1 static**, **G3 smoke**, plus a final **`gate`** job that aggregates all results into *one* required check.
2. Protect `main` (a ruleset or branch protection): require PRs, 1 approval, the `gate` check passing, and up-to-date branches, and block force pushes.
3. Add `CODEOWNERS` (e.g. `framework/` owned by you, `.github/` requiring your review).
4. Add the `merge_group` trigger so the workflow is merge-queue ready.
5. Document in `docs/ci-gates.md`: each gate's purpose, trigger, blocking status, time budget and owner.
6. Prove it: open a PR that fails a gate and confirm GitHub **blocks the merge**.

**Done when**
- [ ] A screenshot or link shows a PR blocked by a failing gate
- [ ] `docs/ci-gates.md` matches your workflow

#### 📘 User guide

**Concepts**
- **Quality gate:** an automated check that must pass before code moves forward (merge, deploy).
- **Required status checks:** branch protection or rulesets make specific checks mandatory for merging.
- **CODEOWNERS:** maps paths to required reviewers.
- **Merge queue:** GitHub tests PRs *combined with* the latest `main` before merging (the `merge_group` event).
- **Aggregator job:** one stable job name that depends on all the others. It's what you mark as required.

**Deep dive**

**Gate design principles:**
1. **Fast first:** static checks in minutes, before expensive browser runs (`needs`).
2. **Deterministic:** a flaky gate trains people to click "re-run" and ignore red. Quarantine flaky tests (P10-03) instead of retrying blindly.
3. **Budgeted:** each gate has a time budget, so creeping duration is visible.
4. **Owned:** someone is accountable for each gate's health.
5. **Layered:** PR gates (smoke) are cheap and blocking; merge or nightly gates (regression) are thorough.

**Why an aggregator job?** Required checks match job *names*. Matrix jobs have generated names (`smoke (chromium, 1)`), and path-filtered workflows may not run at all, which leaves a required check "pending" forever. One `gate` job with `if: always()` that fails when any dependency failed or was cancelled gives you a single, stable required check.

**Merge queues** fix "green alone, red together": two PRs pass individually but break when both merge. The queue tests each PR on top of the others before merging.

**Examples**

🟢 **Low: protect `main` with the GitHub CLI**
```bash
# Needs admin rights on the repo (branch protection on private repos needs a paid plan).
gh api -X PUT "repos/{owner}/{repo}/branches/main/protection" --input - <<'EOF'
{
  "required_status_checks": { "strict": true, "contexts": ["gate"] },
  "enforce_admins": false,
  "required_pull_request_reviews": { "required_approving_review_count": 1 },
  "restrictions": null,
  "allow_force_pushes": false
}
EOF
```
You can also do this in the UI: **Settings → Rules → Rulesets** (the newer approach) or **Branches**.

🔵 **Medium: CODEOWNERS and the aggregator job**
```text
# .github/CODEOWNERS
*                 @your-github-user
/framework/       @your-github-user
/.github/         @your-github-user
```
```yaml
  gate:
    name: gate
    if: always()
    needs: [static, smoke]
    runs-on: ubuntu-latest
    steps:
      - name: All required jobs succeeded?
        env:
          RESULTS: ${{ toJSON(needs.*.result) }}
        run: |
          echo "results: $RESULTS"
          if echo "$RESULTS" | grep -qE '"(failure|cancelled)"'; then exit 1; fi
```

🟣 **High/Complex: a complete gated pipeline, merge-queue ready**
```yaml
# .github/workflows/ci.yml
name: ci
on:
  pull_request:
  push:
    branches: [main]
  merge_group:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  static:
    name: G1 static
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }                       # full history for secret scanning
      - uses: astral-sh/setup-uv@v5
        with: { enable-cache: true }
      - run: uv sync --frozen
      - run: uv run ruff check . && uv run ruff format --check . && uv run mypy
      - run: uv run pytest tests/unit -q --cov=framework --cov-fail-under=80
      - uses: gitleaks/gitleaks-action@v2                 # organisation accounts need a (free) licence key
        env: { GITHUB_TOKEN: "${{ secrets.GITHUB_TOKEN }}" }

  smoke:
    name: G3 smoke
    needs: static
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-qe                   # composite action from P09-05 (or inline the steps)
      - run: >
          uv run pytest -m "smoke and not db and not quarantine" -n 2 --junitxml=test-results/junit.xml
          --tracing retain-on-failure --output test-results/playwright
      - if: always()
        run: uv run python scripts/junit_summary.py test-results/junit.xml "G3 smoke" >> "$GITHUB_STEP_SUMMARY"
      - if: always()
        uses: actions/upload-artifact@v4
        with: { name: smoke-results, path: test-results/, retention-days: 14 }

  gate:
    name: gate
    if: always()
    needs: [static, smoke]
    runs-on: ubuntu-latest
    steps:
      - env: { RESULTS: "${{ toJSON(needs.*.result) }}" }
        run: echo "$RESULTS" | grep -qE '"(failure|cancelled)"' && exit 1 || echo "all gates green"
```

#### 🎤 Interview Q&A

<details><summary><b>[Z] What is a quality gate in CI?</b></summary>

An automated checkpoint with pass/fail criteria (lint, type checks, tests, coverage, security scans) that must succeed before code can merge or deploy. It enforces the team's standards consistently, without relying on reviewers remembering.
</details>

<details><summary><b>[H] Which tests run on a PR, and which on merge or nightly?</b></summary>

PR: fast, deterministic, high-value checks: static analysis, unit tests, API smoke, critical-path UI smoke, ideally under 10 minutes. Merge to main: broader regression. Nightly: the full matrix (all browsers, all shards, long-running and DB-heavy suites) plus trend reporting. Test impact analysis can add relevant extra tests to the PR.
</details>

<details><summary><b>[SH] Why use a single aggregator job as the required check?</b></summary>

Required checks are matched by name. Matrix and conditional jobs have dynamic names or may be skipped, which leaves required checks missing or pending. An aggregator job that always runs and fails if any dependency failed or was cancelled gives one stable check, and adding or removing jobs doesn't require changing branch protection.
</details>

<details><summary><b>[H] A flaky test keeps blocking PRs. What do you do?</b></summary>

Don't add blanket retries to the gate. Quarantine it: mark it `quarantine` with an issue link so it's excluded from blocking runs, keep it running in a non-blocking job to collect data, fix the root cause within an SLA, then restore it. Track the flake rate as a gate-health metric.
</details>

<details><summary><b>[SH] What problem does a merge queue solve?</b></summary>

Semantic conflicts between PRs: each passes CI against an older `main`, but together they break it. A merge queue creates temporary branches combining queued PRs with the latest `main`, runs required checks on them (the `merge_group` event), and merges only if green, which keeps `main` always green in busy repos.
</details>

<details><summary><b>[H] What is CODEOWNERS for?</b></summary>

It automatically requests reviews from the owners of the paths a PR touches, and with branch protection can *require* their approval. That protects critical areas (framework core, CI config, security-sensitive code) and routes reviews to people with context.
</details>

<details><summary><b>[Z] What is branch protection, and what does a "required check" do?</b></summary>

Branch protection rules stop direct pushes to an important branch such as `main` and set conditions for merging: reviews, an up-to-date branch, and required status checks. A required check is a CI job that must succeed before the PR can be merged, which is how quality gates become enforceable rather than advisory.
</details>

#### 🤖 AI assist
- Ask AI to critique your `docs/ci-gates.md` from a developer's perspective ("what would annoy me?"), and adjust the time budgets or blocking rules.

---

### P09-03 · Service containers, DB tests and the full stack in CI

**Level:** 🔵 Hero · **Time:** 4h · **App:** Pagila, Toolshop · **Deliverable:** `db` and `toolshop-e2e` jobs

#### 📋 Task
1. **`db` job:** a Postgres **service container** with a health check. Load Pagila into it (clone the Pagila repo, then `psql`), then run `-m db`.
2. **`toolshop-e2e` job:** check out Toolshop, `docker compose up -d`, seed with a retry loop, wait for readiness (your P04-06 script), and run Toolshop API + UI + DB tests with `--env local`.
3. On failure, upload **container logs** (`docker compose logs`) as an artifact. Always run `docker compose down -v`.
4. Decide which gate each job belongs to (probably G4: merge and nightly) and update `docs/ci-gates.md`.

**Done when**
- [ ] Both jobs are green in CI
- [ ] A deliberately broken environment (e.g. the wrong API URL) produces a failure you can diagnose from uploaded logs

#### 📘 User guide

**Concepts**
- **Service containers:** `services:` in a job starts containers (DBs, caches) alongside the job, with health-check options.
- **Networking:** when the job runs **on the runner VM**, services are reached at `localhost:<mapped port>`. When the job runs **in a container** (`container:`), they're reached by service name.
- **Docker Compose on hosted runners:** Docker is preinstalled on Ubuntu runners, so any compose stack can start in a step.
- **Cleanup:** `if: always()` teardown and log capture.

**Deep dive**

**Service containers vs Compose in a step:** service containers are declarative, start before your steps and suit a single DB or cache. Compose suits whole application stacks you don't control (Toolshop's many services). Both are ephemeral per job, which gives perfect isolation.

**Seeding and readiness in CI:** apps take longer to boot on shared runners. Use retry loops for seed commands (a backoff sleep is fine in *infrastructure scripts*, just never in tests) and explicit readiness checks before tests.

**When environments fail, logs are the evidence.** Upload `docker compose logs` and `docker ps -a` output on failure. Most "tests failed" in full-stack CI turn out to be "environment didn't start", and without logs you're guessing.

**Examples**

🟢 **Low: a Postgres service container**
```yaml
  db:
    name: G4 db
    runs-on: ubuntu-latest
    timeout-minutes: 15
    services:
      postgres:
        image: postgres:18
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: pagila
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 5s --health-timeout 5s --health-retries 20
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with: { enable-cache: true }
      - run: uv sync --frozen
      - run: uv run pytest -m db -q
        env:
          QE_PAGILA_URL: postgresql+psycopg://postgres:postgres@localhost:5432/pagila
```

🔵 **Medium: load Pagila into the service**
```yaml
      - uses: actions/checkout@v4
        with:
          repository: devrimgunduz/pagila
          path: pagila
      - name: Load Pagila
        env: { PGPASSWORD: postgres }
        run: |
          # psql is preinstalled on ubuntu runners; if not: sudo apt-get install -y postgresql-client
          psql -h localhost -U postgres -d pagila -v ON_ERROR_STOP=1 -q -f pagila/pagila-schema.sql
          psql -h localhost -U postgres -d pagila -v ON_ERROR_STOP=1 -q -f pagila/pagila-data.sql
          psql -h localhost -U postgres -d pagila -tAc "SELECT COUNT(*) FROM rental"
```
> If the runner's `psql` client is older than the server and complains, run psql from the server image instead: `docker run --rm --network host -e PGPASSWORD=postgres -v "$PWD/pagila:/p" postgres:18 psql -h localhost -U postgres -d pagila -f /p/pagila-schema.sql`.

🟣 **High/Complex: the Toolshop stack in CI, with evidence on failure**
```yaml
  toolshop-e2e:
    name: G4 toolshop e2e
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v4
      - uses: actions/checkout@v4
        with:
          repository: testsmith-io/practice-software-testing
          path: toolshop
      - uses: ./.github/actions/setup-qe
      - name: Start Toolshop
        working-directory: toolshop
        run: docker compose up -d
      - name: Seed (retry while the API container boots)
        run: |
          for i in $(seq 1 30); do
            docker exec pst-laravel-api-1 php artisan migrate:fresh --seed && exit 0
            echo "seed attempt $i failed, retrying in 10s"; sleep 10
          done
          exit 1
      - run: uv run python scripts/wait_for_stack.py
      - name: Toolshop tests
        run: >
          uv run pytest tests/api/toolshop tests/ui/toolshop tests/db/toolshop -n 4 --env local
          --junitxml=test-results/toolshop.xml --tracing retain-on-failure --output test-results/playwright
        env:
          QE_TOOLSHOP_DB_URL: ${{ secrets.TOOLSHOP_DB_URL }}      # or build it from the compose defaults
      - name: Capture environment evidence
        if: failure()
        run: |
          docker ps -a > test-results/docker-ps.txt
          (cd toolshop && docker compose logs --no-color > ../test-results/toolshop-compose.log)
      - if: always()
        uses: actions/upload-artifact@v4
        with: { name: toolshop-results, path: test-results/, retention-days: 14 }
      - name: Teardown
        if: always()
        working-directory: toolshop
        run: docker compose down -v
```
> On Linux runners your tests run *on the host*, so the Toolshop SPA's `localhost:8091` API calls just work (compare with the P08-02 container trap). If the development compose is slow to build in CI, check Toolshop's README for its pre-built "prod" compose file.

#### 🎤 Interview Q&A

<details><summary><b>[H] Service containers vs Docker Compose inside a job?</b></summary>

Service containers are declared on the job, start before the steps with health checks, and suit single dependencies (a DB, Redis). Compose in a step suits multi-service stacks you don't control and reuses the same compose files as local development. Both are ephemeral per job. Compose gives more control (seeding, logs, profiles).
</details>

<details><summary><b>[H] Full-stack tests fail in CI but pass locally. How do you investigate?</b></summary>

Check whether the environment actually came up: container status (`docker ps -a`), compose logs, seed step output, readiness-check output. Compare resources and timing (slower runners mean longer boot, so fix readiness checks), config differences (env vars, URLs, secrets missing in CI), and network differences (host vs container, localhost semantics). Always upload environment logs on failure.
</details>

<details><summary><b>[Z] How do you make sure CI environments are cleaned up?</b></summary>

Teardown steps with `if: always()` (`docker compose down -v`), which run even after failures or cancellations. Ephemeral runners discard everything anyway, but explicit cleanup matters on self-hosted runners, where leftovers leak into the next job.
</details>

<details><summary><b>[H] Where does test data come from in CI databases?</b></summary>

Deterministic seeds (migrations plus seed scripts, SQL dumps like Pagila), created fresh per job, with tests creating their own additional data. Never depend on shared long-lived CI databases. Use snapshots or templates if loading is slow.
</details>

<details><summary><b>[SH] How would you give every PR its own full environment?</b></summary>

Ephemeral environments: per-PR Compose on the runner for small stacks, or preview environments (a Kubernetes namespace per PR via Helm or Argo, seeded from snapshots) for larger ones, with URLs posted to the PR, tests run against them, and automatic teardown on merge or close. Keep costs down with TTLs, scale-to-zero and shared read-only dependencies.
</details>

<details><summary><b>[Z] What is a service container in GitHub Actions?</b></summary>

A Docker container that GitHub Actions starts alongside a job, such as a PostgreSQL database, declared under `services:` in the workflow. Your steps can reach it on a mapped port, and it's thrown away when the job ends, so every run starts with a clean dependency.
</details>

#### 🤖 AI assist
- Paste `toolshop-compose.log` from a failed run and ask AI which service failed first and why. Verify against the timestamps.

---

### P09-04 · Matrix, sharding, nightly regression and published reports

**Level:** 🔵 Hero · **Time:** 4h · **App:** all · **Deliverable:** `.github/workflows/nightly.yml`

#### 📋 Task
1. `nightly.yml` with `schedule` (cron) and `workflow_dispatch` **inputs** (marker expression, browsers).
2. A **matrix** of `browser × shard` (`fail-fast: false`) using `pytest-split` and your committed `.test_durations`.
3. A **report** job that downloads all shard artifacts, merges the JUnit files, renders an HTML report and publishes it to **GitHub Pages**.
4. A **notify** job that opens (or comments on) a GitHub issue when the scheduled run fails.
5. A job that refreshes `.test_durations` as an artifact, for you to commit when drift is large.

**Done when**
- [ ] A manual `workflow_dispatch` run with custom inputs succeeds
- [ ] The latest report is reachable at your Pages URL
- [ ] A forced failure creates or updates the "Nightly regression failed" issue

#### 📘 User guide

**Concepts**
- **`strategy.matrix`:** run a job for every combination. Also `include`/`exclude`, `fail-fast`, `max-parallel`.
- **`schedule`:** cron syntax, in **UTC**, and it runs on the **default branch**.
- **`workflow_dispatch` inputs:** manual runs with parameters from the UI or `gh workflow run`.
- **Pages deployment:** `actions/upload-pages-artifact` + `actions/deploy-pages` (Settings → Pages → Source: GitHub Actions).
- **`gh` in workflows:** use `GH_TOKEN: ${{ github.token }}` plus job `permissions`.

**Deep dive**

**`fail-fast: false` for test matrices.** The default cancels sibling jobs when one fails, so you'd lose Firefox results because WebKit failed. For test matrices you want the full picture.

**Unique artifact names per matrix cell.** Artifact names must be unique (`results-firefox-2`). The report job downloads them with a pattern and merges them.

**Scheduled-workflow gotchas:** cron runs in UTC, can be delayed under load, uses the workflow file on the default branch, and in public repos scheduled workflows are **disabled after 60 days without repository activity**, which is how "nightly" silently stops.

**Publishing reports** makes quality visible to the team (a link in Slack, dashboards). Pair it with trend data (P10-04) so people see direction, not just today.

**Examples**

🟢 **Low: a browser matrix**
```yaml
jobs:
  ui:
    strategy:
      fail-fast: false
      matrix:
        browser: [chromium, firefox, webkit]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-qe
        with: { browsers: "${{ matrix.browser }}" }
      - run: uv run pytest tests/ui -m "not quarantine" --browser ${{ matrix.browser }} -n 2
```

🔵 **Medium: browser × shard with unique artifacts**
```yaml
  regression:
    name: regression (${{ matrix.browser }}, ${{ matrix.shard }}/3)
    strategy:
      fail-fast: false
      matrix:
        browser: ${{ fromJSON(inputs.browsers || '["chromium","firefox","webkit"]') }}
        shard: [1, 2, 3]
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-qe
        with: { browsers: "${{ matrix.browser }}" }
      - name: Run shard
        env:
          MARKER: ${{ inputs.marker || 'not quarantine and not db' }}
        run: >
          uv run pytest -m "$MARKER" --splits 3 --group ${{ matrix.shard }} -n 2
          --browser ${{ matrix.browser }}
          --junitxml=test-results/junit-${{ matrix.browser }}-${{ matrix.shard }}.xml
          --tracing retain-on-failure --output test-results/pw-${{ matrix.browser }}-${{ matrix.shard }}
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: results-${{ matrix.browser }}-${{ matrix.shard }}
          path: test-results/
          retention-days: 14
```
> The `MARKER` input goes through `env` rather than being pasted into the script. Interpolating user input straight into `run:` is a script-injection risk (P09-05).

🟣 **High/Complex: a full nightly with Pages report and failure notification**
```yaml
# .github/workflows/nightly.yml
name: nightly
on:
  schedule:
    - cron: "0 2 * * *"            # 02:00 UTC
  workflow_dispatch:
    inputs:
      marker:   { description: "pytest -m expression", type: string, default: "not quarantine and not db" }
      browsers: { description: 'JSON list, e.g. ["chromium"]', type: string, default: '["chromium","firefox","webkit"]' }

permissions:
  contents: read

jobs:
  regression:
    # …Medium example above…

  report:
    needs: regression
    if: always()
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - uses: actions/download-artifact@v4
        with: { pattern: "results-*", path: all-results, merge-multiple: true }
      - name: Merge and render
        run: |
          uvx junitparser merge all-results/junit-*.xml merged.xml
          mkdir -p site
          uvx junit2html merged.xml site/index.html
          uv run python scripts/junit_summary.py merged.xml "Nightly regression" >> "$GITHUB_STEP_SUMMARY"
      - uses: actions/upload-pages-artifact@v3
        with: { path: site }

  publish:
    needs: report
    if: always() && needs.report.result == 'success'
    runs-on: ubuntu-latest
    permissions: { pages: write, id-token: write }
    environment:
      name: github-pages
      url: ${{ steps.deploy.outputs.page_url }}
    steps:
      - id: deploy
        uses: actions/deploy-pages@v4

  notify:
    needs: regression
    if: failure() && github.event_name == 'schedule'
    runs-on: ubuntu-latest
    permissions: { issues: write }
    steps:
      - env:
          GH_TOKEN: ${{ github.token }}
          GH_REPO: ${{ github.repository }}
          RUN_URL: ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
        run: |
          gh label create nightly --color B60205 --force
          title="Nightly regression failed"
          num=$(gh issue list --state open --label nightly --json number,title \
                -q ".[] | select(.title == \"$title\") | .number" | head -1)
          if [ -n "$num" ]; then gh issue comment "$num" --body "Failed again: $RUN_URL"
          else gh issue create --title "$title" --label nightly --body "First failure: $RUN_URL"; fi
```
> `junit2html` is one option for rendering; any JUnit-to-HTML tool (or Allure, P10-02) works.

#### 🎤 Interview Q&A

<details><summary><b>[Z] What is a build matrix used for in test pipelines?</b></summary>

Running the same job across combinations (browsers, OS, Python versions, shards) in parallel from one definition. Each cell is an independent job with its own results.
</details>

<details><summary><b>[H] Why set <code>fail-fast: false</code> for test matrices?</b></summary>

With fail-fast (the default), one failing cell cancels the rest, so you lose results for other browsers or shards and can't tell whether a failure is browser-specific or global. Test matrices should report completely.
</details>

<details><summary><b>[SH] What can go wrong with scheduled workflows?</b></summary>

Cron is UTC. Runs can be delayed or dropped under high load. They always use the default branch's workflow file. In public repos they're auto-disabled after 60 days without activity. They run with the repo's permissions but not on PR code. Add alerting for "nightly didn't run", not just "nightly failed".
</details>

<details><summary><b>[H] How do you publish and share test reports from CI?</b></summary>

Upload reports as artifacts per run, write a job summary for quick viewing, publish the latest (and ideally a history) to GitHub Pages or a report server (Allure, ReportPortal), post links and failure summaries to chat or issues, and keep trends (pass rate, duration, flakiness) visible on a dashboard.
</details>

<details><summary><b>[H] How do you notify the team about nightly failures without spam?</b></summary>

One tracking issue (or chat thread) per failure streak: create it on first failure, comment on repeats, and auto-close it on recovery. Include the run link, a failure summary and a suspect commit range. Route it to owners via labels or CODEOWNERS, and avoid one message per test.
</details>

#### 🤖 AI assist
- Ask AI to generate `gh workflow run nightly.yml -f marker=... -f browsers=...` commands for 3 scenarios, and run one.

---

### P09-05 · Images in CI, reusable workflows, environments, self-hosted runners

**Level:** 🟣 Super Hero · **Time:** 5h · **App:** your images and workflows · **Deliverable:** `.github/actions/setup-qe/action.yml`, `.github/workflows/image.yml`, `.github/workflows/run-suite.yml`, `docs/runners-security.md`

#### 📋 Task
1. **Composite action** `setup-qe` (uv + deps + cached browsers) used by all jobs.
2. **G2 build and scan:** build the test image with Buildx using the GitHub Actions cache, **scan it with trivy (fail on CRITICAL)**, and push to **GHCR** on `main`.
3. **Reusable workflow** `run-suite.yml` (`workflow_call`) with inputs (marker, browsers, workers) and secrets, called from `ci.yml` and `nightly.yml`.
4. **Environments:** create a `staging` environment with a required reviewer and an environment secret, and use it in a job that runs tests "against staging" (Toolshop hosted).
5. **Self-hosted runner (private fork only):** register a runner on your laptop (or in a container) with label `qe`, run a job on it, and then remove it.
6. Write `docs/runners-security.md`: hosted vs self-hosted, fork-PR risks, `pull_request_target`, script injection, and SHA pinning.

**Done when**
- [ ] The image is built, scanned and pushed by CI, and a job runs tests inside that image
- [ ] `ci.yml` and `nightly.yml` call the reusable workflow
- [ ] A job ran on your self-hosted runner (screenshot in the doc), and the runner has since been removed

#### 📘 User guide

**Concepts**
- **Composite action:** bundles *steps* into one reusable action (`runs.using: composite`).
- **Reusable workflow:** a whole *workflow* (jobs, runners, permissions) called with `uses: ./.github/workflows/x.yml` and `workflow_call`.
- **GHCR:** GitHub Container Registry. Push with `GITHUB_TOKEN` and `permissions: packages: write`.
- **Environments:** named deployment targets with protection rules (required reviewers, wait timers, branch restrictions) and their own secrets.
- **Self-hosted runner:** your machine running the Actions runner agent, targeted with `runs-on: [self-hosted, <label>]`.

**Deep dive**

**Composite action vs reusable workflow:**
| | Composite action | Reusable workflow |
|---|---|---|
| Unit | Steps inside *your* job | Whole jobs |
| Runner choice | The caller's | Defined by the workflow |
| Secrets | Passed as inputs or env | `secrets:` / `secrets: inherit` |
| Use for | "Setup" blocks | Standard pipelines ("run a suite") |

**Hosted vs self-hosted runners:** hosted runners are clean, ephemeral VMs maintained by GitHub and billed by the minute. Self-hosted runners use your hardware (GPUs, big RAM, internal network access, cached state) but **you** handle security, updates and cleanup.

**Self-hosted security (critical):** never attach self-hosted runners to **public** repos. Anyone can open a PR whose workflow runs arbitrary code *on your machine*. Prefer **ephemeral** runners (one job, then destroyed), run as a low-privilege user, isolate the network, and never leave credentials on the host.

**Workflow security traps:**
- **Script injection:** `run: echo "${{ github.event.pull_request.title }}"` executes attacker-controlled text. Pass it through `env:` and quote it.
- **`pull_request_target`** runs with base-repo secrets and write permissions. Checking out and running PR code there hands secrets to attackers.
- **Third-party actions** execute with your token. Pin them by SHA and review them.

**Environments as gates:** tests against a real staging environment can require approval, use environment-scoped secrets, and show deployment history, which bridges CI and CD.

**Examples**

🟢 **Low: the composite setup action**
```yaml
# .github/actions/setup-qe/action.yml
name: Setup QE
description: uv, project dependencies and cached Playwright browsers
inputs:
  browsers:
    description: space-separated browsers to install
    default: chromium
runs:
  using: composite
  steps:
    - uses: astral-sh/setup-uv@v5
      with: { enable-cache: true }
    - shell: bash
      run: uv sync --frozen
    - id: pw
      shell: bash
      run: echo "version=$(uv run python -c 'import importlib.metadata as m; print(m.version("playwright"))')" >> "$GITHUB_OUTPUT"
    - id: cache
      uses: actions/cache@v4
      with:
        path: ~/.cache/ms-playwright
        key: pw-${{ runner.os }}-${{ steps.pw.outputs.version }}-${{ inputs.browsers }}
    - if: steps.cache.outputs.cache-hit != 'true'
      shell: bash
      run: uv run playwright install --with-deps ${{ inputs.browsers }}
    - if: steps.cache.outputs.cache-hit == 'true'
      shell: bash
      run: uv run playwright install-deps ${{ inputs.browsers }}
```

🔵 **Medium: G2 build → scan → push, then run tests inside the image**
```yaml
# .github/workflows/image.yml
name: image
on:
  pull_request:
    paths: ["docker/**", "pyproject.toml", "uv.lock"]
  push:
    branches: [main]

permissions:
  contents: read
  packages: write

jobs:
  build-scan:
    name: G2 build & scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Image name (GHCR needs lowercase)
        run: echo "IMAGE=ghcr.io/${GITHUB_REPOSITORY,,}/qe-tests:${GITHUB_SHA}" >> "$GITHUB_ENV"
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with: { registry: ghcr.io, username: "${{ github.actor }}", password: "${{ secrets.GITHUB_TOKEN }}" }
      - uses: docker/build-push-action@v6
        with:
          context: .
          file: docker/tests.Dockerfile
          tags: ${{ env.IMAGE }}
          load: true
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - name: Scan (fail on fixable CRITICAL)
        run: >
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy
          image --severity CRITICAL --ignore-unfixed --exit-code 1 "$IMAGE"
      - name: Smoke inside the image
        run: docker run --rm --ipc=host --init "$IMAGE" -m "smoke and api" -q
      - name: Push
        if: github.ref == 'refs/heads/main'
        run: docker push "$IMAGE"
```

🟣 **High/Complex: a reusable suite workflow, environments and a self-hosted runner**
```yaml
# .github/workflows/run-suite.yml
name: run-suite
on:
  workflow_call:
    inputs:
      marker:   { type: string, required: true }
      browsers: { type: string, default: chromium }
      workers:  { type: string, default: "2" }
      env:      { type: string, default: public }
      environment: { type: string, default: "" }       # empty = no environment protection
      label:    { type: string, default: suite }      # unique per call: artifact names must not collide
    secrets:
      TOOLSHOP_ADMIN_PASSWORD: { required: false }

jobs:
  run:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-qe
        with: { browsers: "${{ inputs.browsers }}" }
      - name: Tests
        env:
          MARKER: ${{ inputs.marker }}
          QE_TOOLSHOP_ADMIN_PASSWORD: ${{ secrets.TOOLSHOP_ADMIN_PASSWORD }}
        run: uv run pytest -m "$MARKER" -n ${{ inputs.workers }} --env ${{ inputs.env }} --junitxml=test-results/junit.xml
      - if: always()
        uses: actions/upload-artifact@v4
        with: { name: "${{ inputs.label }}-results", path: test-results/ }
```
```yaml
# caller: ci.yml / nightly.yml
jobs:
  staging-smoke:
    uses: ./.github/workflows/run-suite.yml
    with:
      marker: "smoke and api"
      label: staging-smoke
      environment: staging        # approval + environment secrets (Settings → Environments)
    secrets: inherit

  on-my-machine:                  # PRIVATE fork only
    runs-on: [self-hosted, qe]
    if: github.event_name == 'workflow_dispatch'
    steps:
      - uses: actions/checkout@v4
      - run: uv sync --frozen && uv run pytest -m smoke -q
```
```bash
# Register (Settings → Actions → Runners → New self-hosted runner shows the exact download and token)
./config.sh --url https://github.com/<you>/<private-repo> --token <REG_TOKEN> --labels qe --ephemeral
./run.sh            # processes one job, then exits because of --ephemeral
# Remove when done: ./config.sh remove --token <REMOVE_TOKEN>
```

#### 🎤 Interview Q&A

<details><summary><b>[H] GitHub-hosted vs self-hosted runners?</b></summary>

Hosted: clean ephemeral VMs, zero maintenance, standard sizes, pay per minute, and public internet only. Self-hosted: your hardware (bigger machines, GPUs, internal network access, warm caches), cheaper at scale, but you own patching, isolation, cleanup and security. Use hosted by default and self-hosted for specific needs, preferably ephemeral and autoscaled.
</details>

<details><summary><b>[SH] Why is a self-hosted runner on a public repo dangerous?</b></summary>

Anyone can open a pull request that modifies workflow files or test code, and that code runs on your runner, inside your network, with access to whatever is on the machine (credentials, caches, other jobs' leftovers). It's remote code execution by design. Restrict self-hosted runners to private repos, use ephemeral isolated runners, and require approval for outside contributors.
</details>

<details><summary><b>[SH] What's the risk with <code>pull_request_target</code>?</b></summary>

It runs in the context of the base repository, with secrets and a write-capable token, even for fork PRs. If the workflow checks out and executes the PR's code (installs dependencies, runs tests), an attacker can exfiltrate secrets or push code. Use it only for metadata tasks (labelling) that never run PR code, or split into an untrusted build and a trusted follow-up via `workflow_run` with artifact validation.
</details>

<details><summary><b>[H] Composite action vs reusable workflow?</b></summary>

A composite action packages steps that run inside the caller's job, which suits setup logic. A reusable workflow packages entire jobs (its own runners, permissions, environment) and is called at job level, which suits standard pipelines like "run a test suite". Many teams use both: reusable workflows built from composite actions.
</details>

<details><summary><b>[SH] How do you prevent script injection in workflows?</b></summary>

Never interpolate untrusted context values (PR titles, branch names, issue bodies, inputs) directly into `run:` scripts. Pass them via `env:` and reference them as quoted shell variables. Restrict token permissions, pin third-party actions by SHA, and lint workflows (actionlint; zizmor for security).
</details>

<details><summary><b>[H] What do GitHub Environments add for test pipelines?</b></summary>

Named targets (staging, prod) with protection rules (required reviewers, wait timers, allowed branches), environment-scoped secrets, and deployment history. Tests against real environments can be gated by approval and use credentials not exposed to regular jobs.
</details>

#### 🤖 AI assist
- Give AI your workflows and ask for a **security review** (permissions, injection, action pinning, secrets exposure). Cross-check with `actionlint` and read each finding critically.

---

## 🏁 Phase checkpoint: P09

**Design exercise (30 min, no AI):** draw the CI/CD test pipeline for a 5-service e-commerce product: which suites run on PR, merge, nightly and pre-release, with time budgets, gates, environments, owners and reporting. Present it in 5 minutes.

**AI mock interviewer prompt**
```text
Interview me on CI/CD for test automation with GitHub Actions: workflow anatomy,
quality gates, artifacts vs caches, matrices and sharding, service containers,
flaky tests in pipelines, runners and security (fork PRs, pull_request_target,
script injection). 8 questions one at a time, then ask me to design a pipeline for
a microservices product. Score 1-5 each with staff-level additions.
```
Record your results in `interview-notes/P09.md`.
