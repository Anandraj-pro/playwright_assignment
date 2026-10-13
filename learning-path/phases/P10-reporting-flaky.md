# P10: Reporting, Bugs and Flaky Tests

> **Goal:** communicate quality: bug reports that get fixed, reports that explain failures, a disciplined flaky-test process, and metrics leaders care about.
> **Apps:** SauceDemo (`problem_user`, `error_user`), Toolshop **with-bugs**, your CI history. **Prerequisites:** P05, P09. **Time:** ~14 h.

| ID | Task | Level | Time |
|---|---|---|---|
| P10-01 | Bug reports that get fixed | 🟢 | 3h |
| P10-02 | Rich reports: pytest-html and Allure with attachments | 🔵 | 3h |
| P10-03 | Flaky tests: detect, reproduce, quarantine | 🔵 | 4h |
| P10-04 | Test metrics and a quality dashboard | 🟣 | 4h |

---

### P10-01 · Bug reports that get fixed

**Level:** 🟢 Zero · **Time:** 3h · **App:** Toolshop with-bugs, SauceDemo · **Deliverable:** `docs/bugs/BUG-001.md` … `BUG-005.md`, `.github/ISSUE_TEMPLATE/bug_report.yml`

#### 📋 Task
1. Run a **60-minute exploratory session** on https://with-bugs.practicesoftwaretesting.com with a written charter (see the examples). Take notes as you go.
2. Also use SauceDemo's `problem_user` and `error_user`.
3. Write **≥5 bug reports** using the template below, each with evidence (screenshot, trace, or the API request/response).
4. Classify **severity** and **priority** for each, with a one-line justification.
5. Create a GitHub **issue form** (`bug_report.yml`) that enforces the template.
6. Link each bug to a strict-xfail test where automatable (P05-07).

**Done when**
- [ ] 5 reports, each reproducible by a stranger in under 2 minutes
- [ ] The session notes include the charter, time spent, coverage and open questions

#### 📘 User guide

**Concepts**
- **Bug report anatomy:** title, environment, preconditions, steps, expected, actual, evidence, severity, priority, frequency, notes.
- **Severity** is the *impact on the system or user* (a technical judgement). **Priority** is the *urgency to fix* (a business judgement).
- **Exploratory testing charter:** "Explore *target* with *resources* to discover *information*."
- **Session-based test management (SBTM):** time-boxed sessions with notes, bugs, issues and coverage.
- **Minimal reproduction:** the fewest steps and least data that still show the bug.

**Deep dive**

**Developers fix bugs they can reproduce quickly and whose impact is clear.** Every field serves that goal:
- **Title formula:** `[Area] Action → wrong result (condition)`, e.g. `[Checkout] Applying coupon twice doubles the discount (with-bugs v5)`.
- **Steps:** numbered, minimal, with exact data. **Expected:** cite the source (spec, previous behaviour, common sense). **Actual:** facts only, no blame.
- **Evidence:** a screenshot or **trace**, and for API bugs the **request and response**. A Playwright trace is a gold-standard bug attachment.
- **Frequency:** 5/5, 2/10, only on Firefox… Intermittent bugs need their conditions stated.

**Severity vs priority examples:**
| Case | Severity | Priority |
|---|---|---|
| Checkout crashes for all users | Critical | P1 |
| Company logo misspelled on home page | Low | P1 (brand, visible) |
| Rare crash in a legacy admin report | High | P3 (few users, workaround) |
| Tooltip typo in settings | Low | P4 |

**"Can't reproduce"** usually means missing context: the environment, data state, user role, browser, timing. Add a trace, HAR, exact data and a video. Offer to pair.

**Examples**

🟢 **Low: from a bad title to a good one**
| ❌ Bad | ✅ Good |
|---|---|
| "Images broken" | `[Inventory] All products show the same image for problem_user` |
| "Search doesn't work" | `[Search] Query 'hammer' returns 0 results although 7 hammers exist (with-bugs)` |
| "Error on checkout" | `[Checkout] 'Finish' does nothing for error_user; no confirmation shown` |

🔵 **Medium: a complete report**
```markdown
# BUG-001 [Inventory] All products show the same image for problem_user

**Environment:** https://www.saucedemo.com · Chromium 1xx · 2026-09-23
**User/role:** problem_user / secret_sauce
**Severity:** Medium (wrong product info, purchase still possible) · **Priority:** P2 (visible on main page)
**Frequency:** 5/5

## Steps
1. Log in as `problem_user`
2. Look at the product list

## Expected
Each product shows its own image (as for `standard_user`).

## Actual
All 6 products show the same dog image.

## Evidence
- Screenshot: bug-001.png · Trace: trace-bug-001.zip
- DOM: all `.inventory_item img` have the same `src`

## Automated check
`tests/ui/test_bug_hunt.py::test_product_images_are_distinct_for_problem_user` (strict xfail)
```

🟣 **High/Complex: an issue form, plus filing bugs straight from failing tests**
```yaml
# .github/ISSUE_TEMPLATE/bug_report.yml
name: Bug report
description: A reproducible defect in the system under test
labels: ["bug", "triage"]
body:
  - type: input
    id: title_hint
    attributes: { label: "Area", placeholder: "Checkout / Search / Auth …" }
    validations: { required: true }
  - type: textarea
    id: steps
    attributes: { label: "Steps to reproduce", value: "1.\n2.\n3." }
    validations: { required: true }
  - type: textarea
    id: expected
    attributes: { label: "Expected result (and source)" }
    validations: { required: true }
  - type: textarea
    id: actual
    attributes: { label: "Actual result" }
    validations: { required: true }
  - type: dropdown
    id: severity
    attributes: { label: "Severity", options: ["Critical", "High", "Medium", "Low"] }
    validations: { required: true }
  - type: input
    id: env
    attributes: { label: "Environment (URL, version, browser, user)" }
    validations: { required: true }
  - type: textarea
    id: evidence
    attributes: { label: "Evidence (trace, screenshot, request/response)", description: "Never paste secrets or personal data." }
```
```bash
# scripts/file_bug.sh "<title>" <body.md>: body built from a failing test's report section
gh issue create --title "$1" --body-file "$2" --label bug --label triage
```

#### 🎤 Interview Q&A

<details><summary><b>[Z] What makes a good bug report?</b></summary>

A specific title, environment details, minimal numbered steps with exact data, expected (with source) vs actual, evidence (screenshots, traces, logs, request/response), severity and priority, and frequency. One bug per report, factual tone, and it's reproducible by someone else without asking questions.
</details>

<details><summary><b>[Z] Severity vs priority, with an example of high priority but low severity.</b></summary>

Severity is technical impact. Priority is business urgency. High priority, low severity: a misspelled brand name on the landing page, which is harmless functionally but embarrassing and highly visible. Low priority, high severity: a crash in a rarely used legacy report that has a workaround.
</details>

<details><summary><b>[H] A developer says "can't reproduce". What do you do?</b></summary>

Re-verify on a clean environment, then add the missing context: exact build/version, environment, user role and data state, browser and OS, timing or frequency, a trace or video, a HAR or API request/response, and logs with a correlation ID. Offer a short pairing session. If it's intermittent, document the conditions and reproduction rate, and consider adding logging to catch it.
</details>

<details><summary><b>[H] How do you run an exploratory testing session?</b></summary>

Write a charter (target, resources, information sought) and time-box it (45–90 min). Use heuristics (CRUD, boundaries, interruptions, roles, state transitions, error handling) and take notes on what was covered, bugs, questions and ideas. Debrief afterwards: what I found, what I didn't cover, risks, and follow-up charters. Convert repeatable findings into automated checks.
</details>

<details><summary><b>[SH] How do you get stakeholders to fix the bugs that matter?</b></summary>

Bug advocacy: frame the impact in business terms (users affected, revenue or compliance risk, support cost), show evidence and the reproduction rate, relate it to similar incidents, propose the fix scope or a workaround, and triage together with product and engineering using an agreed severity/priority rubric. Track the escape cost of bugs that were deferred and later hit production, to calibrate future decisions.
</details>

<details><summary><b>[SH] How do you run a root cause analysis for an escaped defect?</b></summary>

Blameless and systemic. Build a timeline, find the technical root cause and the *process* causes (why tests, reviews or monitoring didn't catch it: missing scenario, wrong test layer, environment gap, flaky test ignored), use 5 Whys or a fishbone diagram, and define concrete actions (a new test at the right layer, monitoring or alerts, a checklist update) with owners and dates. Then track whether the actions worked.
</details>

#### 🤖 AI assist
- After *you* write a report, ask AI: *"What would a developer ask before starting on this?"* Add the missing information. Never let AI invent steps or results you didn't observe.

---

### P10-02 · Rich reports: pytest-html and Allure with attachments

**Level:** 🔵 Hero · **Time:** 3h · **App:** all · **Deliverable:** report hooks in `framework/pytest_plugin.py`, Allure steps in page objects and clients, `docs/reporting.md`

#### 📋 Task
1. **pytest-html:** a custom title and environment metadata. On failure, attach a **screenshot** (UI tests) and the **last API exchanges** (API tests, from P04-04).
2. **Allure:** `uv add --dev allure-pytest`. Add `@allure.step` to page-object and client methods, attach traces and screenshots on failure, and add `feature`/`story`/`severity` labels and issue links.
3. Add `categories.json` so Allure groups failures into *Product defect*, *Test defect*, *Environment* and *Flaky*.
4. Generate the Allure report locally and in the nightly workflow (next to the P09-04 report).
5. `docs/reporting.md`: which report serves which audience.

**Done when**
- [ ] A failing UI test shows its screenshot inside the HTML report
- [ ] The Allure report shows steps from page objects, with attachments on failure

#### 📘 User guide

**Concepts**
- **JUnit XML:** a machine-readable standard (CI, dashboards). **HTML reports:** human-readable. **Allure:** rich steps, attachments, history, categories.
- **pytest-html extras:** `pytest_html.extras.png(...)`, `.text(...)`, `.url(...)` attached to a report.
- **Allure API:** `@allure.step("…")`, `allure.attach(body, name, attachment_type)`, `allure.dynamic.title/feature/story/severity`, `@allure.issue`, `--alluredir`.
- **Categories:** rules that classify failures by message or trace patterns.

**Deep dive**

**Different audiences, different reports:**
| Audience | Needs | Format |
|---|---|---|
| CI system | Pass/fail, counts | JUnit XML, exit code |
| Developer fixing a failure | Exact failure, evidence, steps | HTML/Allure with trace, screenshot, API exchange |
| QA lead | Trends, flaky tests, coverage by feature | Allure history, dashboard (P10-04) |
| Manager / release | Go/no-go, risks | A 1-page summary: critical flows green? known issues? |

**Steps make failures readable.** "Failed at step 4/7: *Checkout with Ada Lovelace / 1234AB*" beats a stack trace. Putting `@allure.step` on page-object and client methods gives you steps for free in every test.

**Attachment strategy:** attach on **failure**, not always, because traces and videos are large and CI storage costs money. Always keep enough evidence to diagnose without re-running.

**Failure categories** speed up triage: a regex on messages classifies `TimeoutError` → Environment/Flaky candidate, `AssertionError` with business values → Product defect candidate, `strict mode violation`/locator errors → Test defect.

**Examples**

🟢 **Low: HTML report title and metadata**
```python
# tests/conftest.py
def pytest_html_report_title(report):
    report.title = "QE Hero: test report"
```
```bash
uv run pytest -m smoke --html=test-results/report.html --self-contained-html \
  --metadata Environment public --metadata Commit "$(git rev-parse --short HEAD)"
```
> `--metadata` comes from `pytest-metadata`, which pytest-html installs.

🔵 **Medium: attach a screenshot and API exchanges on failure (pytest-html 4)**
```python
# framework/pytest_plugin.py (add)
import base64
import pytest

@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield
    if report.when == "call" and report.failed:
        pytest_html = item.config.pluginmanager.getplugin("html")
        if pytest_html:
            extras = getattr(report, "extras", [])
            page = item.funcargs.get("page") or item.funcargs.get("customer_page")
            if page is not None and not page.is_closed():
                png = base64.b64encode(page.screenshot(full_page=True)).decode()
                extras.append(pytest_html.extras.png(png, name="screenshot"))
            client = item.funcargs.get("booker")
            if client is not None and getattr(client, "history", None):
                extras.append(pytest_html.extras.text("\n\n".join(client.history), name="API exchanges"))
            report.extras = extras
    return report
```

🟣 **High/Complex: Allure steps, attachments and failure categories**
```python
# framework/pages/saucedemo/login_page.py (decorate intent methods)
import allure

class LoginPage:
    @allure.step("Log in as {user}")
    def login(self, user: str, password: str = "secret_sauce") -> "InventoryPage":
        ...

# framework/api/booker_client.py
class BookerClient(BaseClient):
    @allure.step("API: create booking for {payload[firstname]}")
    def create_booking(self, payload: dict) -> BookingCreated: ...
```
```python
# tests/ui/saucedemo/test_checkout.py
import allure

@allure.feature("Checkout")
@allure.story("Totals")
@allure.severity(allure.severity_level.CRITICAL)
@allure.issue("BUG-001", "https://github.com/<you>/<repo>/issues/1")
def test_checkout_totals_match_business_rules(inventory): ...
```
```python
# framework/pytest_plugin.py (add): attach the Playwright trace/screenshot to Allure on failure
import allure

@pytest.fixture
def allure_evidence(request, page):
    yield
    rep = getattr(request.node, "rep_call", None)
    if rep is not None and rep.failed:
        allure.attach(page.screenshot(full_page=True), name="screenshot",
                      attachment_type=allure.attachment_type.PNG)
```
```json
// allure-results/categories.json  (copy into allure-results before generating the report)
[
  { "name": "Environment", "matchedStatuses": ["broken", "failed"],
    "messageRegex": ".*(ConnectionError|ECONNREFUSED|503 Service Unavailable|Name or service not known).*" },
  { "name": "Test defect (locator/wait)", "matchedStatuses": ["broken", "failed"],
    "messageRegex": ".*(strict mode violation|waiting for locator|Timeout \\d+ms exceeded).*" },
  { "name": "Product defect candidate", "matchedStatuses": ["failed"],
    "messageRegex": ".*AssertionError.*" }
]
```
```bash
uv run pytest -m smoke --alluredir=allure-results
cp docs/allure/categories.json allure-results/
allure generate allure-results --clean -o allure-report && allure open allure-report
# Allure 2's CLI needs Java; check the Allure docs for the current CLI (Allure 3 installs via npm)
```

#### 🎤 Interview Q&A

<details><summary><b>[H] What should a good automated test report show?</b></summary>

What ran and the result (counts, duration), what failed and *why* (message, step, evidence like a screenshot, trace or API exchange), since when (history or trend), which area or feature is affected, and who owns it. It should be accessible from the CI run and link to bugs. Different views serve CI, developers, QA leads and managers.
</details>

<details><summary><b>[Z] How do you attach screenshots to failed tests?</b></summary>

Capture on failure through the hook-plus-fixture pattern (store the call report, check `failed` in teardown) or plugin options (`--screenshot only-on-failure`), and attach via the report library: pytest-html extras or `allure.attach`. Also keep Playwright traces for deeper debugging.
</details>

<details><summary><b>[H] What does Allure add over a basic HTML report?</b></summary>

Hierarchical steps (from decorated framework methods), rich attachments, behaviour grouping (epic/feature/story), severity, issue and TMS links, history and trends across runs (when history is preserved), retries and flaky markers, and failure categories. It's more useful for triage and for stakeholders.
</details>

<details><summary><b>[SH] How do you speed up failure triage across hundreds of tests?</b></summary>

Classify automatically: categories by message pattern (environment vs locator vs assertion), cluster identical failures (same message or stack) so 40 failures become 3 root causes, flag known flaky or quarantined tests, link to recent commits in the affected area, and give AI-assisted summaries (P12-04) that a human verifies. Invest in evidence (traces, correlation IDs) so each cluster is diagnosable without re-running.
</details>

<details><summary><b>[SH] How much evidence should you attach, and what's the trade-off?</b></summary>

Enough to diagnose without re-running: failure-only screenshots and traces, API exchanges, and logs with correlation IDs. Always-on video and traces for every test inflate storage, upload time and cost. Use retention policies (e.g. 14 days), capture on failure (or on first retry), and never capture secrets or PII.
</details>

<details><summary><b>[Z] What's the difference between a test report and a bug report?</b></summary>

A test report summarises a test run for everyone: what ran, what passed and failed, how long it took, and the evidence for failures. A bug report describes one specific defect for the people who'll fix it: steps to reproduce, expected versus actual results, environment, severity and evidence. A failing test in a report may lead to a bug report after triage, but it could also be a test or environment problem.
</details>

#### 🤖 AI assist
- Ask AI to propose more Allure category regexes from a sample of your real failure messages, then test each regex against real messages before adopting it.

---

### P10-03 · Flaky tests: detect, reproduce, quarantine

**Level:** 🔵 Hero · **Time:** 4h · **App:** SauceDemo (`performance_glitch_user`), The Internet (dynamic loading), your suite · **Deliverable:** `scripts/flake_rate.py`, a quarantine lane in `Makefile` and CI, `docs/flaky-policy.md`

#### 📋 Task
1. **Create** 3 flaky tests on purpose (in a branch): a too-short timeout on `/dynamic_loading/2`, a `performance_glitch_user` login with a tight timeout, and an order dependency (P07-02).
2. **Detect** with `pytest-repeat` (`--count 20`) and parallel stress (`-n 4`), and compute each test's **flake rate** with `scripts/flake_rate.py`.
3. **Root-cause and fix** each one, and document the cause category.
4. **Quarantine policy:** `@pytest.mark.quarantine(issue="…", since="YYYY-MM-DD")` (the P03-06 plugin enforces `issue`). Quarantined tests are excluded from gates and run in a **non-blocking** CI job.
5. **Policy as code:** a weekly job lists quarantined tests older than 14 days and fails, so they get fixed or deleted.
6. Write `docs/flaky-policy.md`.

**Done when**
- [ ] Each planted flaky test has a measured flake rate before and 0% after the fix
- [ ] The quarantine lane runs non-blocking in CI, and the SLA check works

#### 📘 User guide

**Concepts**
- **Flaky test:** passes and fails on the **same code** without changes.
- **Root-cause categories:** timing/async, shared state/order, test data, environment/infrastructure, external dependencies, resource leaks, non-deterministic app behaviour (**real race conditions**), test-framework bugs.
- **Detection:** reruns, repetition (`pytest-repeat`), history analysis (same SHA with both pass and fail).
- **Quarantine:** remove from blocking gates, keep running, track, fix within an SLA.
- **Flake rate:** failures ÷ runs for a test on unchanged code.

**Deep dive**

**Why flaky tests are expensive:** they waste re-runs, but worse, they **destroy trust**. Once people expect random reds, they ignore real failures. A 1% flake rate per test across 300 tests means most runs have *some* failure.

**Retries: detect, don't hide.** `pytest-rerunfailures` (`--reruns 2`) turns red into green, and that's exactly the problem. If you use retries, (1) report "passed on retry" as **flaky** and track it, (2) never retry in a way that masks product bugs, and (3) prefer running retries in a **separate diagnostic job**, not the gate.

**Sometimes the test is right.** An intermittently failing test can be exposing a **real race condition** in the product (double-submit, eventual-consistency bug). Investigate before "fixing the test".

**Reproducing flakiness:** repeat under stress (`--count 50 -n 8`), vary one factor at a time (serial vs parallel, browser, data, CPU throttling), add tracing on every run (`--tracing on` temporarily), and compare passing and failing traces side by side.

**Examples**

🟢 **Low: reproduce by repetition**
```bash
uv add --dev pytest-repeat pytest-rerunfailures
uv run pytest tests/ui/internet/test_dynamic.py::test_late_rendered_element --count 20 -q -p no:randomly
uv run pytest tests/ui/internet/test_dynamic.py --count 10 -n 4 --tracing on    # stress plus evidence
```

🔵 **Medium: measure the flake rate, and a quarantine lane**
```python
# scripts/flake_rate.py: usage: flake_rate.py <nodeid> [runs]
import subprocess, sys, tempfile, xml.etree.ElementTree as ET
from pathlib import Path

node, runs = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 20
with tempfile.TemporaryDirectory() as tmp:
    xml = Path(tmp) / "r.xml"
    subprocess.run(["uv", "run", "pytest", node, "--count", str(runs), "-q", "-p", "no:randomly",
                    f"--junitxml={xml}"], capture_output=True)
    cases = list(ET.parse(xml).getroot().iter("testcase"))
    failed = sum(1 for c in cases if c.find("failure") is not None or c.find("error") is not None)
print(f"{node}: {failed}/{len(cases)} failed → flake rate {failed / max(len(cases), 1):.0%}")
```
```python
@pytest.mark.quarantine(issue="QE-123", since="2026-09-23")
def test_sometimes_slow_login(page): ...
```
```makefile
test-gate:       ; uv run pytest -m "not quarantine" -n auto
test-quarantine: ; uv run pytest -m quarantine --reruns 2 --junitxml=test-results/quarantine.xml || true
```
```yaml
  quarantine:
    name: quarantine (non-blocking)
    needs: static
    runs-on: ubuntu-latest
    continue-on-error: true            # never blocks, but results are visible
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-qe
      - run: uv run pytest -m quarantine --reruns 2 --junitxml=test-results/quarantine.xml
```

🟣 **High/Complex: enforce the quarantine SLA as code**
```python
# framework/pytest_plugin.py (add): `pytest --quarantine-report out.json --co -q` lists quarantined tests
import json

def pytest_addoption(parser):
    parser.addoption("--quarantine-report", default=None, help="write quarantined tests to JSON")

def pytest_collection_finish(session):
    path = session.config.getoption("--quarantine-report")
    if not path:
        return
    entries = []
    for item in session.items:
        m = item.get_closest_marker("quarantine")
        if m:
            entries.append({"test": item.nodeid, "issue": m.kwargs.get("issue"), "since": m.kwargs.get("since")})
    with open(path, "w") as f:
        json.dump(entries, f, indent=2)
```
```python
# scripts/quarantine_sla.py: fail if anything has been quarantined for longer than the SLA
import datetime, json, subprocess, sys

SLA_DAYS = 14
subprocess.run(["uv", "run", "pytest", "--co", "-q", "--quarantine-report", "q.json"], check=True, capture_output=True)
today = datetime.date.today()
overdue = [e for e in json.load(open("q.json"))
           if e["since"] and (today - datetime.date.fromisoformat(e["since"])).days > SLA_DAYS]
for e in overdue:
    print(f"::error title=Quarantine SLA breached::{e['test']} ({e['issue']}) since {e['since']}")
sys.exit(1 if overdue else 0)
```
> If you already defined `pytest_addoption` in the plugin, merge the options into one function.

#### 🎤 Interview Q&A

<details><summary><b>[Z] What is a flaky test and what commonly causes it?</b></summary>

A test that passes and fails without code changes. Common causes: timing (racing async UI or API, fixed sleeps), shared state and order dependency, test data collisions, environment instability, external services, resource leaks, and real non-determinism or race conditions in the product.
</details>

<details><summary><b>[H] Should you automatically retry failed tests?</b></summary>

Carefully. Retries reduce noise but hide flakiness and real intermittent bugs. If used, cap them (1–2), record "passed on retry" as flaky with tracking, keep them out of (or visible in) blocking gates, and fix root causes within an SLA. Never retry to make a red build green without reporting it.
</details>

<details><summary><b>[H] How do you detect flaky tests systematically?</b></summary>

History analysis (the same commit has both pass and fail results across runs or reruns), scheduled repetition runs of the suite, rerun-to-detect in a diagnostic job, and tracking per-test flake rate over time. New tests can be run N times before merge (a "burn-in") to catch flakiness early.
</details>

<details><summary><b>[H] Describe a quarantine process.</b></summary>

Mark the test (with issue ID and date) so it's excluded from blocking gates but still runs in a non-blocking lane to gather data. Create a ticket with an owner, set an SLA (e.g. 14 days) to fix or delete, and enforce the SLA automatically. Un-quarantine only after it proves stable (e.g. 50 consecutive passes).
</details>

<details><summary><b>[SH] A "flaky" test turned out to be a real bug. How could that happen, and what do you learn?</b></summary>

Intermittent product behaviour (race conditions, eventual-consistency windows, cache invalidation, concurrency bugs) produces intermittent test failures. If the team labels it "flaky" and retries it, the bug ships. Lesson: investigate flakiness with traces and logs before blaming the test, and treat unexplained intermittency as a potential product defect.
</details>

<details><summary><b>[SH] What flake-rate target is realistic, and how do you track it?</b></summary>

Per test, near zero. Suite-level, aim for under 1–2% of runs failing due to flakiness. Track per-test flake rate from CI history (same-SHA pass/fail), show the top offenders on a dashboard, alert on new flaky tests, and tie it to gate trust metrics (re-run rate, time lost).
</details>

#### 🤖 AI assist
- Give AI a passing trace summary and a failing one for the same test (action lists and timings) and ask what differs. Verify it in Trace Viewer.

---

### P10-04 · Test metrics and a quality dashboard

**Level:** 🟣 Super Hero · **Time:** 4h · **App:** your CI history · **Deliverable:** `scripts/metrics_ingest.py`, `scripts/metrics_report.py`, `docs/quality-dashboard.md`

#### 📋 Task
1. Download JUnit artifacts from your last ≥10 CI runs (`gh run list` / `gh run download`).
2. Ingest them into **SQLite** (`runs`, `results` tables) with the commit SHA, date, test ID, outcome and duration.
3. Compute, **in SQL**: pass rate per run, **flaky tests** (both pass and fail at the same SHA), the top 10 slowest tests and their trend, failure clusters by message, and time lost to failures.
4. Generate a markdown or HTML dashboard and publish it next to the nightly report (Pages).
5. In `docs/quality-dashboard.md`, explain which metrics you'd show to a team, a QA lead and an executive, and which **vanity metrics** you'd avoid.

**Done when**
- [ ] The dashboard is generated from real CI data
- [ ] It lists flaky tests detected purely from history

#### 📘 User guide

**Concepts**
- **Leading vs lagging indicators:** flake rate and gate duration (leading) vs escaped defects (lagging).
- **Useful test metrics:** pass rate (excluding known issues), flake rate, gate duration, MTTR for a red `main`, coverage of **critical flows/risks**, defect escape rate, and time to feedback.
- **Vanity metrics:** raw test count, "% automated" without risk context, line coverage alone.
- **DORA metrics:** deployment frequency, lead time for changes, change failure rate, time to restore. Test automation directly affects the last three.

**Deep dive**

**Measure what drives decisions.** "We have 2,000 tests" says nothing. "Checkout, login and payment are covered at API and UI level, the PR gate is 8 minutes with a 0.5% flake rate, and 2 bugs escaped last quarter (both in untested promo logic)" drives action.

**Flaky detection from history** is powerful and cheap: if the *same commit* produced both pass and fail for a test, the test (or the product) is non-deterministic. No reruns needed. Just data.

**Metrics can be gamed.** Targets on test count produce trivial tests, and targets on coverage produce assertion-free tests. Pair metrics (coverage *and* mutation score, pass rate *and* flake rate) and review them with context.

**Examples**

🟢 **Low: fetch CI results**
```bash
gh run list --workflow nightly.yml -L 10 --json databaseId,headSha,createdAt,conclusion > runs.json
for id in $(jq -r '.[].databaseId' runs.json); do
  gh run download "$id" -D "ci-history/$id" || echo "no artifacts for $id"
done
```

🔵 **Medium: ingest JUnit into SQLite**
```python
# scripts/metrics_ingest.py
import json, sqlite3, xml.etree.ElementTree as ET
from pathlib import Path

db = sqlite3.connect("metrics.sqlite")
db.executescript("""
CREATE TABLE IF NOT EXISTS runs (run_id INTEGER PRIMARY KEY, sha TEXT, created_at TEXT, conclusion TEXT);
CREATE TABLE IF NOT EXISTS results (run_id INTEGER, test_id TEXT, outcome TEXT, duration REAL, message TEXT);
""")
for run in json.load(open("runs.json")):
    db.execute("INSERT OR REPLACE INTO runs VALUES (?,?,?,?)",
               (run["databaseId"], run["headSha"], run["createdAt"], run["conclusion"]))
    db.execute("DELETE FROM results WHERE run_id = ?", (run["databaseId"],))
    for xml in Path(f"ci-history/{run['databaseId']}").rglob("*.xml"):
        for case in ET.parse(xml).getroot().iter("testcase"):
            problem = case.find("failure")
            if problem is None:
                problem = case.find("error")
            outcome = "skipped" if case.find("skipped") is not None else ("failed" if problem is not None else "passed")
            db.execute("INSERT INTO results VALUES (?,?,?,?,?)", (
                run["databaseId"], f"{case.get('classname')}::{case.get('name')}", outcome,
                float(case.get("time", 0)), (problem.get("message") or "")[:300] if problem is not None else None))
db.commit()
```

🟣 **High/Complex: metrics in SQL and a dashboard**
```python
# scripts/metrics_report.py
import sqlite3
from pathlib import Path

db = sqlite3.connect("metrics.sqlite")
q = lambda sql: db.execute(sql).fetchall()

pass_rate = q("""SELECT r.created_at, ROUND(100.0 * SUM(res.outcome='passed') / COUNT(*), 1)
                 FROM runs r JOIN results res USING (run_id) WHERE res.outcome != 'skipped'
                 GROUP BY r.run_id ORDER BY r.created_at DESC LIMIT 10""")
flaky = q("""SELECT test_id, COUNT(*) AS flaky_commits FROM (
               SELECT res.test_id, r.sha FROM results res JOIN runs r USING (run_id)
               GROUP BY res.test_id, r.sha
               HAVING SUM(res.outcome='passed') > 0 AND SUM(res.outcome='failed') > 0)
             GROUP BY test_id ORDER BY flaky_commits DESC""")
slowest = q("""SELECT test_id, ROUND(AVG(duration), 1) AS avg_s, ROUND(MAX(duration), 1) AS max_s
               FROM results GROUP BY test_id ORDER BY avg_s DESC LIMIT 10""")
clusters = q("""SELECT substr(message, 1, 80) AS msg, COUNT(*) AS n, COUNT(DISTINCT test_id) AS tests
                FROM results WHERE outcome='failed' GROUP BY msg ORDER BY n DESC LIMIT 5""")

out = ["# Quality dashboard", "", "## Pass rate (last runs)", "| Run | Pass % |", "|---|---|"]
out += [f"| {d[:10]} | {p} |" for d, p in pass_rate]
out += ["", "## Flaky tests (pass and fail on the same commit)", "| Test |", "|---|"]
out += [f"| `{t}` |" for t, _ in flaky] or ["| none 🎉 |"]
out += ["", "## Slowest tests", "| Test | avg s | max s |", "|---|---|---|"]
out += [f"| `{t}` | {a} | {m} |" for t, a, m in slowest]
out += ["", "## Top failure clusters", "| Message | Failures | Tests |", "|---|---|---|"]
out += [f"| {m} | {n} | {t} |" for m, n, t in clusters]
Path("site").mkdir(exist_ok=True)
Path("site/dashboard.md").write_text("\n".join(out))
```
> Stretch: render `dashboard.md` to HTML (or with Chart.js) and publish it with the nightly report.

#### 🎤 Interview Q&A

<details><summary><b>[H] Which QA metrics do you report, and to whom?</b></summary>

Team: gate duration, flake rate, failing and quarantined tests, time to fix a red main. QA lead: risk and critical-flow coverage by layer, defect trends by area, escape rate, automation health. Leadership: release readiness (critical flows green, open high-severity bugs), escaped defects and their impact, lead-time and change-failure trends. Always with context and actions, not raw numbers.
</details>

<details><summary><b>[H] What are vanity metrics in testing?</b></summary>

Numbers that look good but don't inform decisions: raw test counts, "% of test cases automated" without risk weighting, line coverage alone, number of bugs logged. They're easy to game and can reward the wrong behaviour.
</details>

<details><summary><b>[SH] How do you measure flakiness from CI data?</b></summary>

For each test, look for commits (SHAs) where it has both passed and failed across runs, reruns or matrix cells. That's non-determinism by definition. Compute per-test flake rate (inconsistent runs ÷ total runs) over a window, rank the offenders, and alert on new entries. No extra test runs are needed.
</details>

<details><summary><b>[H] What is defect escape rate and why does it matter?</b></summary>

The share of defects found after release (production) vs before (e.g. escaped ÷ total over a period, often weighted by severity). It's the ultimate lagging indicator of test effectiveness, and analysing escapes (which layer should have caught it?) drives where to invest in testing.
</details>

<details><summary><b>[SH] How does test automation influence DORA metrics?</b></summary>

Fast, reliable gates shorten lead time (fast feedback, no manual regression phase), reduce change failure rate (regressions caught before deploy), enable higher deployment frequency (confidence to ship small changes often), and speed up time to restore (fast verification of fixes, good diagnostics). Slow or flaky suites directly worsen all four.
</details>

<details><summary><b>[SH] How would you present quality status to executives?</b></summary>

One page: a release-readiness verdict with a traffic light per critical business flow, the top 3 risks with mitigations, the trend of escaped defects and customer-impacting incidents, and one or two process improvements with measured effect (e.g. "PR feedback 25 → 8 min"). Business language, no test-count trivia, with drill-down links for detail.
</details>

<details><summary><b>[Z] Name three test metrics and what each one tells you.</b></summary>

Flake rate (how often tests fail without a code change) tells you how much you can trust red builds. Escaped defects (bugs found after release, by severity) tell you what testing missed. Suite duration or time to feedback tells you whether the team will actually run the tests. Metrics are useful when they lead to a decision, not as targets in themselves.
</details>

#### 🤖 AI assist
- Give AI your dashboard numbers and ask it to draft a 5-sentence executive summary. Then fact-check every claim against the data.

---

## 🏁 Phase checkpoint: P10

**Scenario drill (20 min, no AI):** "Nightly shows 37 failures after a deploy." Walk through your triage: clustering, categories, evidence, owners, communication, and what goes to the bug tracker vs the quarantine list.

**AI mock interviewer prompt**
```text
Interview me as a QA lead candidate on bug reporting, severity vs priority,
exploratory testing, test reporting, flaky test management and quality metrics.
6 questions one at a time, then a scenario: "leadership asks whether we can ship
tomorrow: 3 flaky tests, 1 open high-severity bug, green smoke". Evaluate my answer
and communication. Score 1-5 each.
```
Record your results in `interview-notes/P10.md`.
