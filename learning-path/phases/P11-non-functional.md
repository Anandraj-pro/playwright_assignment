# P11: Non-functional Testing: Performance, Accessibility and Security

> **Goal:** test *how well* the product works, not only *what* it does: load and response-time budgets, accessibility (now a legal requirement in many markets), the security checks every QE should run, and then all three as CI gates.
> **Apps:** self-hosted Toolshop and Restful-Booker (P04-06) for load and security tests; hosted Toolshop is fine for read-only accessibility scans. **Prerequisites:** P04, P05, P08, P09. **Time:** ~18 h.
> ⚠️ **Only load-test or security-test systems you run yourself, or have written permission to test.** Public demo apps are shared by thousands of people. Hammering them or firing attack payloads at them is abuse, and in many countries it's illegal.

| ID | Task | Level | Time |
|---|---|---|---|
| P11-01 | Performance testing with Locust | 🔵 | 4h |
| P11-02 | Accessibility testing: axe scans, keyboard and screen readers | 🔵 | 4h |
| P11-03 | Security testing basics for QEs | 🔵 | 5h |
| P11-04 | Non-functional gates in CI: performance smoke, ZAP baseline and accessibility | 🟣 | 5h |

---

### P11-01 · Performance testing with Locust

**Level:** 🔵 Hero · **Time:** 4h · **App:** Restful-Booker and Toolshop API (self-hosted) · **Deliverable:** `perf/locustfile.py`, `docs/performance/report.md`

#### 📋 Task
1. Start your local stack (`make stack-up`, P04-06) and add Locust: `uv add --dev locust`.
2. Write `perf/locustfile.py` with a realistic mix for Restful-Booker: mostly reads, some creates, a few authenticated updates, with think time between actions.
3. Run four kinds of test, each headless with `--csv` so the numbers are saved:
   - **smoke:** 1–2 users for 1 minute (does the script work?)
   - **load:** your expected peak, e.g. 20 users for 5 minutes
   - **stress:** ramp up until errors appear or p95 passes your budget (🟣 example)
   - **soak:** moderate load for 20+ minutes while watching `docker stats` for memory growth
4. Write `docs/performance/report.md`: throughput, p50/p95/p99 per endpoint, error rate, the **knee point** where latency starts climbing, CPU and memory from `docker stats`, and a recommendation.
5. Add **response-time budgets**: a Locust `quitting` hook that makes the run fail if the error rate is above 1% or p95 is over budget.

**Done when**
- [ ] Four runs saved as CSVs, and a report that names the knee point with evidence
- [ ] Setting an impossible budget makes `locust` exit non-zero (prove it, then put the budget back)
- [ ] You can explain why you report percentiles rather than averages

#### 📘 User guide

**Concepts**
- **Latency:** how long one request takes. **Throughput:** requests per second the system handles.
- **Percentiles:** p95 = 95% of requests were at least this fast. p50 is the typical user; p95 and p99 are your unhappy users.
- **Error rate:** failed requests ÷ all requests, including timeouts and wrong responses, not only 5xx codes.
- **Test types:** *smoke* (tiny load, does it work), *load* (expected traffic), *stress* (beyond expected, find the limit), *spike* (sudden jump), *soak* (hours at steady load, finds leaks), *scalability* (does adding capacity help?).
- **Think time:** real users pause between actions. Without it, 10 virtual users behave like 100 real ones.
- **Budget / SLO:** a target such as "p95 under 500 ms with under 1% errors at 20 users". An *SLA* is the contractual version.
- **Tools:** Locust (Python), k6 (JavaScript), JMeter (GUI and XML), Gatling (Scala/Java). The concepts transfer between them.

**Deep dive**

**Start with a question, not a tool.** "How many users can checkout handle before p95 passes 1 second?" is a performance test. "Run JMeter at 100 users" isn't. The question decides the workload, the duration, the data and what you measure.

**Why percentiles beat averages:** if 95 requests take 100 ms and 5 take 5 seconds, the average is 345 ms, which describes nobody. The p95 of 5 s tells you one user in twenty is suffering. Latency distributions have long tails, and the tail is where users leave.

**Users vs requests per second:** with Little's law, concurrency = throughput × time in the system. Twenty users, each taking an action every 2 seconds (think time plus response time), produce about 10 requests per second. Be explicit about which one your requirement means.

**Your laptop isn't production.** Numbers from a local Docker stack are *relative*: they compare builds and find the knee and the leaks, but they don't predict production capacity. Keep the environment the same between runs, warm the app up first, and check the *load generator* isn't the bottleneck (if Locust's own CPU is at 100%, your results are about Locust).

**A lesson from the shared demo:** even two users against the hosted Restful-Booker once measured a p95 around 2.5 seconds when this guide was written. That's network distance and a shared free server, not the app's real capacity, which is one more reason to test your own instance.

**Examples**

🟢 **Low: the smallest useful Locust test**
```python
# perf/locustfile.py
from locust import HttpUser, between, task


class BookingUser(HttpUser):
    wait_time = between(1, 3)  # think time

    @task(5)
    def list_bookings(self) -> None:
        self.client.get("/booking", name="GET /booking")

    @task(1)
    def ping(self) -> None:
        with self.client.get("/ping", name="GET /ping", catch_response=True) as response:
            if response.status_code != 201:  # Restful-Booker's /ping answers 201
                response.failure(f"expected 201, got {response.status_code}")
```
```bash
uv run locust -f perf/locustfile.py --headless -u 2 -r 1 -t 1m \
  --host http://localhost:3001 --csv test-results/perf --html test-results/perf.html
```
The `--csv` prefix produces `test-results/perf_stats.csv`, with one row per endpoint (`Name`, `Request Count`, `Failure Count`, `95%`, `99%` and more) plus an `Aggregated` row.

🔵 **Medium: a realistic user journey with auth, creates and updates**
```python
# perf/locustfile.py
import random

from locust import HttpUser, between, task

BOOKING = {
    "firstname": "Load",
    "lastname": "Test",
    "totalprice": 150,
    "depositpaid": True,
    "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-03"},
}
JSON = {"Accept": "application/json"}


class BookingUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self) -> None:  # runs once per simulated user
        credentials = {"username": "admin", "password": "password123"}
        self.token = self.client.post("/auth", json=credentials, name="POST /auth").json()["token"]
        self.my_ids: list[int] = []

    @task(6)
    def list_bookings(self) -> None:
        self.client.get("/booking", name="GET /booking")

    @task(3)
    def read_my_booking(self) -> None:
        if self.my_ids:
            self.client.get(f"/booking/{random.choice(self.my_ids)}", headers=JSON, name="GET /booking/{id}")

    @task(2)
    def create_booking(self) -> None:
        with self.client.post(
            "/booking", json=BOOKING, headers=JSON, name="POST /booking", catch_response=True
        ) as response:
            if response.status_code == 200:
                self.my_ids.append(response.json()["bookingid"])
            else:
                response.failure(f"create failed with {response.status_code}")

    @task(1)
    def update_booking(self) -> None:
        if self.my_ids:
            headers = {**JSON, "Cookie": f"token={self.token}"}
            body = {**BOOKING, "totalprice": 200}
            path = f"/booking/{self.my_ids[-1]}"
            self.client.put(path, json=body, headers=headers, name="PUT /booking/{id}")
```
`name=` groups requests like `/booking/17` and `/booking/42` into one row, otherwise every ID becomes its own line in the report. Each simulated user only reads bookings *it* created, so the test owns its data even under load.

🟣 **High/Complex: find the knee with a step ramp, and enforce budgets**
```python
# perf/locustfile_stress.py: run with  locust -f perf/locustfile_stress.py --headless --host ...
from locust import LoadTestShape, events
from locustfile import BookingUser  # noqa: F401  (Locust runs every user class it finds here)


class StepRamp(LoadTestShape):
    """Add 10 users every 60 s up to 100, then stop. Plot p95 per step to see the knee."""

    step_users, step_seconds, max_users = 10, 60, 100

    def tick(self) -> tuple[int, float] | None:
        users = (int(self.get_run_time() // self.step_seconds) + 1) * self.step_users
        return None if users > self.max_users else (users, self.step_users)


@events.quitting.add_listener
def enforce_budgets(environment, **kwargs) -> None:  # type: ignore[no-untyped-def]
    total = environment.stats.total
    p95 = total.get_response_time_percentile(0.95)
    if total.fail_ratio > 0.01 or p95 > 800:
        print(f"FAIL: p95 {p95:.0f} ms, error rate {total.fail_ratio:.1%} (budget: 800 ms, 1%)")
        environment.process_exit_code = 1
```
With `--csv`, Locust also writes `perf_stats_history.csv`, a row every few seconds. Plot p95 against user count from it: the knee is where the line stops being flat.

#### 🎤 Interview Q&A

<details><summary><b>[Z] What's the difference between load, stress and soak testing?</b></summary>

Load testing checks behaviour at the expected traffic level against the performance targets. Stress testing goes beyond it to find the breaking point and see how the system fails and recovers. Soak (endurance) testing holds a steady, realistic load for hours to find slow problems such as memory leaks, connection-pool exhaustion or growing queues.
</details>

<details><summary><b>[Z] Why report p95 and p99 instead of the average response time?</b></summary>

Response times have long tails, and averages hide them: a few very slow requests barely move the average but ruin those users' experience. p95 and p99 describe the slowest 5% and 1% of requests, which is where users give up. Report the percentiles alongside throughput and error rate.
</details>

<details><summary><b>[H] How do you design a realistic performance test?</b></summary>

Start from a question and a target (an SLO). Build the workload model from production analytics: the journeys, their mix, arrival rates, think times and data volumes. Use realistic, varied test data. Run on an environment close to production and keep it stable between runs. Warm up, measure percentiles, errors and resource usage on both the system and the load generator, and compare against a baseline over time rather than a single run.
</details>

<details><summary><b>[H] p95 doubled between two builds. How do you investigate?</b></summary>

Confirm it's real: re-run on the same environment, and check the load generator and the data weren't different. Find which endpoints moved (per-endpoint percentiles), then correlate with resource metrics (CPU, memory, DB connections, GC) and traces or slow-query logs to locate the layer. Diff the builds (code, dependencies, configuration, queries), bisect if necessary, and add a budget check so the next regression is caught automatically.
</details>

<details><summary><b>[SH] How would you fit performance testing into a CI/CD pipeline?</b></summary>

In layers: fast, small performance smoke tests with per-endpoint budgets on every merge or nightly (catching big regressions), fuller load and soak tests on a stable, production-like environment on a schedule or before releases, and production monitoring (SLOs, real-user metrics) as the final check. CI runners are noisy, so gate on generous thresholds and trends rather than exact numbers, and keep budgets in version control so changing one is a reviewed decision.
</details>

#### 🤖 AI assist
- Give AI your `perf_stats.csv` and ask for a plain-English summary for a product manager. Check every number it quotes against the file. Models misread tables surprisingly often.
- Ask it to review your workload model: *"What would real users do that this script doesn't?"*

---

### P11-02 · Accessibility testing: axe scans, keyboard and screen readers

**Level:** 🔵 Hero · **Time:** 4h · **App:** Toolshop (hosted is fine: scans only read pages), SauceDemo · **Deliverable:** `tests/a11y/test_axe_scans.py`, `tests/a11y/test_keyboard.py`, `docs/accessibility.md`

#### 📋 Task
1. Write an **axe fixture** that injects axe-core into a page and returns its violations (🟢 example). Scan at least 5 Toolshop page *states* (home, login, a product page, contact, the cart with an item) **after they've rendered**.
2. **Gate** on impact: fail on `critical` and `serious` violations, except known ones listed in an allowlist with a bug ID. When a known issue is fixed, its allowlist entry must fail loudly, so the list can't rot (🔵 example).
3. **Keyboard only:** log in, search, add a product to the cart and reach checkout without a mouse. Check that focus is always visible and the tab order is logical, and assert focus with `to_be_focused()`.
4. **Screen reader, 15 minutes:** VoiceOver (macOS: Cmd+F5) or NVDA (Windows, free) on the login page. Write down exactly what's announced for each control.
5. Write `docs/accessibility.md`: a findings table (issue, WCAG criterion, impact, who's affected, found by axe, keyboard or screen reader) and what automation missed.

**Done when**
- [ ] Axe scans cover at least 5 page states and fail on new serious or critical violations
- [ ] A keyboard-only journey test passes (or fails with a filed bug)
- [ ] Your doc lists at least one issue axe found and at least one that only a human found

#### 📘 User guide

**Concepts**
- **WCAG 2.2:** the Web Content Accessibility Guidelines. Levels A, AA and AAA; most laws and contracts require **AA**.
- **POUR:** content must be **P**erceivable, **O**perable, **U**nderstandable and **R**obust.
- **Accessible name and role:** what assistive technology announces, e.g. *"Login, button"*. An icon-only button without a name is announced as just *"button"*.
- **The first rule of ARIA:** use native HTML elements (`<button>`, `<label>`) before adding ARIA attributes. Wrong ARIA is worse than none.
- **axe-core:** the most widely used rules engine for automated accessibility checks. Each violation has a rule ID, an impact (`minor`, `moderate`, `serious`, `critical`), the elements affected and a help link.
- **Laws:** the **European Accessibility Act** has applied to many products and services sold in the EU since 28 June 2025; the ADA and Section 508 apply in the US. Accessibility is a compliance risk, not only good practice.

**Deep dive**

**Automation finds a minority of the problems.** Rules engines reliably catch missing names and labels, contrast failures, invalid ARIA and structural errors. They can't judge whether alt text is *meaningful*, whether the focus order makes *sense*, or whether a screen-reader user can actually complete checkout. Treat axe as a fast safety net and keyboard and screen-reader checks as the real test.

**What we found on Toolshop (2026-09-23):**
- The **home page** had a `serious` `list` violation: lists containing elements other than `<li>`.
- The **login page** had a `button-name` violation: the show-password toggle is an icon-only button with no accessible name, and Playwright's accessibility snapshot shows it as just `- button`. A screen-reader user hears "button" and has to guess.
- That login violation **only appeared when the scan ran after the form had rendered.** Scanning too early produced a clean report. Always wait for the content you care about before scanning, as you would before asserting.
- Several `color-contrast` results came back as *incomplete*, meaning axe couldn't decide and a human has to check.

**Where accessibility checks fit:** role-based locators (P05-02) are already a small accessibility check, because they fail when elements have no accessible name. Add axe scans of key page states to the regression suite, a keyboard journey for each critical flow, and a manual screen-reader pass before major releases.

**Examples**

🟢 **Low: an axe fixture and a scan**
```python
# tests/a11y/conftest.py
from collections.abc import Callable
from typing import Any

import pytest
from playwright.sync_api import Page

# Pin the version: a new axe release can add rules, and new rules mean new failures.
AXE_URL = "https://cdn.jsdelivr.net/npm/axe-core@4.13.0/axe.min.js"
WCAG_AA = {"runOnly": {"type": "tag", "values": ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"]}}


@pytest.fixture
def axe(page: Page) -> Callable[[], list[dict[str, Any]]]:
    def run() -> list[dict[str, Any]]:
        page.add_script_tag(url=AXE_URL)
        return page.evaluate("async (options) => (await axe.run(document, options)).violations", WCAG_AA)

    return run
```
```python
# tests/a11y/test_axe_scans.py
from playwright.sync_api import Page, expect

BASE = "https://practicesoftwaretesting.com"


def test_login_page_has_no_serious_violations(page: Page, axe) -> None:
    page.goto(f"{BASE}/auth/login")
    expect(page.get_by_role("button", name="Login")).to_be_visible()  # scan the real page, not a shell
    violations = axe()
    summary = [(v["id"], v["impact"], len(v["nodes"])) for v in violations]
    assert not [v for v in violations if v["impact"] in ("serious", "critical")], summary
```
**Run it: on today's Toolshop it fails** with the real `button-name` violation described in the deep dive. That's your first accessibility bug: file it (P10-01 format), then step 2 turns it into a known, tracked issue instead of a permanently red test. In a self-contained CI image you'd serve `axe.min.js` from the repo or a package instead of a CDN (P08).

🔵 **Medium: gate on impact, with an allowlist that can't rot**
```python
# tests/a11y/test_axe_scans.py
import pytest
from playwright.sync_api import Page, expect

BASE = "https://practicesoftwaretesting.com"
BLOCKING = {"serious", "critical"}
KNOWN = {  # (page, rule id): bug id. Remove an entry the day its bug is fixed.
    ("/", "list"): "A11Y-001",
    ("/auth/login", "button-name"): "A11Y-002",
}
PAGES = {
    "/": lambda page: expect(page.locator('[data-test="product-name"]').first).to_be_visible(),
    "/auth/login": lambda page: expect(page.get_by_role("button", name="Login")).to_be_visible(),
    "/contact": lambda page: expect(page.get_by_role("button", name="Send")).to_be_visible(),
}


@pytest.mark.parametrize("path", PAGES)
def test_no_new_blocking_violations(page: Page, axe, path: str) -> None:
    page.goto(f"{BASE}{path}")
    PAGES[path](page)  # wait for the real content
    found = {v["id"] for v in axe() if v["impact"] in BLOCKING}
    known_here = {rule for (p, rule) in KNOWN if p == path}
    new = found - known_here
    fixed = known_here - found
    assert not new, f"new blocking accessibility violations on {path}: {sorted(new)}"
    bugs = [KNOWN[(path, rule)] for rule in fixed]
    assert not fixed, f"{sorted(fixed)} no longer found on {path}: close {bugs} and remove them from KNOWN"
```
Check each wait condition with Playwright's codegen or inspector before relying on it; selectors on a demo app can change.

🟣 **High/Complex: a keyboard journey and an accessibility-tree assertion**
```python
# tests/a11y/test_keyboard.py
from playwright.sync_api import Page, expect

BASE = "https://practicesoftwaretesting.com"


def test_login_form_exposes_named_controls(page: Page) -> None:
    page.goto(f"{BASE}/auth/login")
    form = page.locator("form").first
    expect(form.get_by_role("button", name="Login")).to_be_visible()
    expect(form).to_match_aria_snapshot("""
      - textbox "Email address *"
      - textbox "Password *"
      - button "Login"
    """)  # partial match: lists what a screen reader must be able to name


def test_login_with_keyboard_only(page: Page) -> None:
    page.goto(f"{BASE}/auth/login")
    email = page.get_by_role("textbox", name="Email address *")
    password = page.get_by_role("textbox", name="Password *")
    email.focus()
    page.keyboard.type("customer2@practicesoftwaretesting.com")
    page.keyboard.press("Tab")
    expect(password).to_be_focused()
    page.keyboard.type("welcome01")
    page.keyboard.press("Enter")  # a form must submit from the keyboard
    expect(page).to_have_url(f"{BASE}/account")
```
Pressing Tab once after the password lands on the unnamed show-password button, *before* Login. Write down whether that order makes sense to a keyboard user; it's a judgement call that no tool will make for you. (The keyboard test logs in as `customer2@…`: the shared `customer@…` account on the hosted demo is sometimes locked by other people's failed logins.)

#### 🎤 Interview Q&A

<details><summary><b>[Z] What is WCAG, and what does "AA" mean?</b></summary>

The Web Content Accessibility Guidelines, from the W3C, define how to make web content usable by people with disabilities, organised around four principles: perceivable, operable, understandable and robust. Success criteria come in levels A (minimum), AA (the usual legal and contractual target) and AAA (enhanced). "WCAG 2.2 AA" means meeting every A and AA criterion of version 2.2.
</details>

<details><summary><b>[Z] Can automated tools test accessibility completely?</b></summary>

No. Rules engines like axe reliably catch a subset of issues (missing names and labels, contrast, invalid ARIA, structure), but can't judge meaning or usability: whether alt text describes the image, whether focus order is logical, whether a screen-reader user can complete a task. You need keyboard testing, screen-reader checks and ideally feedback from disabled users as well.
</details>

<details><summary><b>[H] How do you build accessibility into a test-automation suite?</b></summary>

Use role-based locators so missing accessible names fail tests naturally; run axe scans on key page *states* (after content renders) and gate on serious and critical violations with a reviewed allowlist; add keyboard-only journeys for critical flows and accessibility-tree snapshot assertions for key components; pin the axe version so new rules arrive as deliberate upgrades; and schedule manual screen-reader passes before major releases.
</details>

<details><summary><b>[SH] Your product must comply with the European Accessibility Act. How do you organise testing?</b></summary>

Agree the target (WCAG 2.2 AA via the harmonised standard) and scope with legal and product. Audit the current state (automated scans plus an expert manual audit) and prioritise by user impact and legal risk. Shift left: accessibility acceptance criteria in stories, a design-system component library tested once and reused, automated checks as CI gates, and manual checks per release. Track open issues like any quality risk, publish an accessibility statement, and include disabled users in usability testing.
</details>

#### 🤖 AI assist
- Paste one axe violation (rule, HTML snippet, help text) and ask AI to explain who is affected and how, then to propose the smallest correct fix. Verify the fix against the rule's help page: AI often "fixes" things with unnecessary ARIA.

---

### P11-03 · Security testing basics for QEs

**Level:** 🔵 Hero · **Time:** 5h · **App:** Toolshop API (self-hosted) · **Deliverable:** `tests/security/test_authz_matrix.py`, `tests/security/test_input_handling.py`, `tests/security/test_headers.py`, `docs/security-testing.md`

> **Self-hosted only.** Everything here runs against *your* Toolshop (`make stack-up`, API on http://localhost:8091). The one exception is the header check, which only reads response headers, so pointing it at the hosted site is fine.

#### 📋 Task
1. **Authorisation matrix:** using Swagger (http://localhost:8091/api/documentation), pick at least 8 endpoints and write the expected status for every role: anonymous, customer, *another* customer, and admin. Give a reason for every cell.
2. **Automate the matrix** as one parametrised test, with tokens from a session fixture (🟢 example).
3. **Ownership (IDOR/BOLA):** prove a customer can't read, change or delete another customer's invoice, favourite or profile by guessing or reusing its ID (🔵 example).
4. **Hostile input:** send classic payloads (SQL injection, script tags, path traversal, very long strings, emoji, wrong types) to search, registration and the contact form. The rule is *never a 500*, and nothing a user types is ever executed in the browser (🟣 example).
5. **Tokens:** a missing, malformed or expired token gets 401; a valid customer token on an admin endpoint gets 403; a token stops working after logout.
6. **Headers:** check the security headers on the API and on the web pages, and decide which ones matter for each.
7. Write `docs/security-testing.md`: findings with severity and an **OWASP API Security Top 10 (2023)** category for each, plus what you'd hand to a security specialist.

**Done when**
- [ ] The authorisation matrix is documented and automated, with a reason for every cell
- [ ] No input produced a 5xx, or each 5xx is filed as a bug with the exact payload
- [ ] Every finding in your doc maps to an OWASP API Top 10 category

#### 📘 User guide

**Concepts**
- **Authentication vs authorisation:** *who are you?* (login, tokens) vs *what are you allowed to do?* (roles, ownership). Most serious API bugs are authorisation bugs.
- **401 vs 403 vs 404:** 401 means "not authenticated"; 403 means "authenticated, but not allowed"; 404 is often used deliberately instead of 403 so an attacker can't learn that an object *exists*.
- **OWASP API Security Top 10 (2023):** API1 Broken Object Level Authorization (BOLA, also called IDOR), API2 Broken Authentication, API3 Broken Object Property Level Authorization, API4 Unrestricted Resource Consumption, API5 Broken Function Level Authorization, API6 Unrestricted Access to Sensitive Business Flows, API7 Server-Side Request Forgery, API8 Security Misconfiguration, API9 Improper Inventory Management, API10 Unsafe Consumption of APIs.
- **SAST / DAST / SCA:** static analysis of source code, dynamic scanning of the running app (ZAP, P11-04), and scanning dependencies for known vulnerabilities (trivy and Dependabot, P08).
- **QE security checks vs a penetration test:** QEs automate the predictable checks (authorisation, input handling, headers, tokens) on every build; specialists do the creative, adversarial testing. You need both.

**Deep dive**

**Authorisation is where functional testers find security bugs.** You already know the roles and the data model, so ask of every endpoint: *who should be able to call this, on whose data?* Then test the other people. The classic bug is BOLA: `GET /invoices/1042` returns someone else's invoice because the API checks you're *logged in* but not that invoice 1042 is *yours*. No scanner finds that reliably; a tester with two accounts finds it in minutes.

**What we saw on hosted Toolshop (2026-09-23, read-only calls):**
- `GET /users`: 401 anonymous, 403 customer, 200 admin. That's correct function-level authorisation.
- A customer reading another customer's invoice got **404 "Requested item not found"**. That's correct, and it doesn't confirm the invoice exists.
- A customer reading another *user's* record got **HTTP 404 but a body saying "You are not authorized to view this user."** The status says "doesn't exist" while the message says "exists, but not for you". That's a small inconsistency, but it leaks existence, which is exactly what the 404 was meant to hide. Write findings like that up with the evidence and a low severity.
- The API responses had no `Strict-Transport-Security` or `X-Content-Type-Options` headers, and the `Server` header gave the exact Apache version.
- The home page was also missing `Strict-Transport-Security`, `X-Content-Type-Options` and `Content-Security-Policy`.

**Hostile input: what "handled" looks like.** The server should reject bad input with a clear 4xx, store what it accepts safely, and never execute it. Watch for 500 errors (unhandled input often means injectable input), stack traces or SQL in error bodies (information disclosure), and anything you typed being run as script when displayed (cross-site scripting). With Playwright you can *prove* a script didn't run by listening for dialogs.

**Which headers matter where:** browsers act on headers for *HTML pages*: `Content-Security-Policy` (limits where scripts can come from), `frame-ancestors` or `X-Frame-Options` (clickjacking), `Strict-Transport-Security` (HTTPS only), `X-Content-Type-Options: nosniff`, `Referrer-Policy`. For a JSON API, HSTS, `nosniff`, a deliberate CORS policy and *not* advertising software versions matter most. Checking for headers that don't apply generates noise, and noise gets security checks switched off.

**Examples**

🟢 **Low: tokens per role, and the matrix as data**
```python
# tests/security/conftest.py
import os
from collections.abc import Callable

import pytest
import requests

API = os.getenv("QE_TOOLSHOP_API", "http://localhost:8091")  # your self-hosted Toolshop
USERS = {
    "admin": ("admin@practicesoftwaretesting.com", "welcome01"),
    "customer": ("customer@practicesoftwaretesting.com", "welcome01"),
    "customer2": ("customer2@practicesoftwaretesting.com", "welcome01"),
}


@pytest.fixture(scope="session")
def tokens() -> dict[str, str | None]:
    result: dict[str, str | None] = {"anonymous": None}
    for role, (email, password) in USERS.items():
        credentials = {"email": email, "password": password}
        response = requests.post(f"{API}/users/login", json=credentials, timeout=10)
        response.raise_for_status()
        result[role] = response.json()["access_token"]
    return result


@pytest.fixture(scope="session")
def api_call() -> Callable[..., requests.Response]:
    def call(method: str, path: str, token: str | None, **kwargs: object) -> requests.Response:
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return requests.request(method, f"{API}{path}", headers=headers, timeout=10, **kwargs)

    return call
```
```python
# tests/security/test_authz_matrix.py
from collections.abc import Callable

import pytest
import requests

Tokens = dict[str, str | None]
Call = Callable[..., requests.Response]

MATRIX = [  # method, path, role, expected status. Keep the reasons in docs/security-testing.md
    ("GET", "/users", "anonymous", 401),
    ("GET", "/users", "customer", 403),
    ("GET", "/users", "admin", 200),
    ("GET", "/users/me", "anonymous", 401),
    ("GET", "/users/me", "customer", 200),
    ("GET", "/invoices", "anonymous", 401),
    ("GET", "/invoices", "customer", 200),
    ("GET", "/invoices", "admin", 200),
]


@pytest.mark.parametrize(("method", "path", "role", "expected"), MATRIX)
def test_access_rules(
    tokens: Tokens, api_call: Call, method: str, path: str, role: str, expected: int
) -> None:
    response = api_call(method, path, tokens[role])
    got = response.status_code
    assert got == expected, f"{role} {method} {path}: expected {expected}, got {got}: {response.text[:200]}"
```
`api_call` is a fixture rather than a function imported from `conftest.py`: importing from a conftest is one of the smells you removed in P05-04.

🔵 **Medium: ownership checks (BOLA / IDOR)**
```python
# tests/security/test_authz_matrix.py (continued)
def test_customer_cannot_read_another_customers_invoice(tokens: Tokens, api_call: Call) -> None:
    me = api_call("GET", "/users/me", tokens["customer2"]).json()["id"]
    every_invoice = api_call("GET", "/invoices", tokens["admin"]).json()["data"]  # admin sees everyone's
    theirs = next((invoice for invoice in every_invoice if invoice["user_id"] != me), None)
    assert theirs, "need an invoice owned by someone else: place an order as 'customer' first"
    response = api_call("GET", f"/invoices/{theirs['id']}", tokens["customer2"])
    assert response.status_code in (403, 404), f"BOLA: read another user's invoice: {response.text[:200]}"


def test_customer_list_contains_only_their_own_invoices(tokens: Tokens, api_call: Call) -> None:
    me = api_call("GET", "/users/me", tokens["customer2"]).json()["id"]
    invoices = api_call("GET", "/invoices", tokens["customer2"]).json()["data"]
    owners = {invoice["user_id"] for invoice in invoices}
    assert owners <= {me}, f"list leaks other users' invoices: {owners - {me}}"
```
Test every verb, not only GET: a team that protects `GET /invoices/{id}` sometimes forgets `PUT` and `DELETE` on the same path.

🟣 **High/Complex: hostile input at the API, and proof that nothing executes in the browser**
```python
# tests/security/test_input_handling.py
import os

import pytest
import requests
from playwright.sync_api import Page, expect

API = os.getenv("QE_TOOLSHOP_API", "http://localhost:8091")
UI = os.getenv("QE_TOOLSHOP_URL", "http://localhost:4200")
PAYLOADS = {
    "sql": "' OR '1'='1' --",
    "script": "<script>alert('xss')</script>",
    "img-onerror": '<img src=x onerror="alert(1)">',
    "traversal": "../../../../etc/passwd",
    "template": "{{7*7}}${7*7}",
    "long": "A" * 5_000,
    "emoji": "🔨" * 100,
    "null-byte": "abc\x00def",
}


@pytest.mark.parametrize("name", PAYLOADS)
def test_search_rejects_or_ignores_hostile_input(name: str) -> None:
    response = requests.get(f"{API}/products/search", params={"q": PAYLOADS[name]}, timeout=10)
    assert response.status_code < 500, f"{name}: {response.status_code} {response.text[:200]}"
    for leak in ("SQLSTATE", "Traceback", "Stack trace"):
        assert leak not in response.text, f"{name}: error details leaked ({leak})"


@pytest.mark.parametrize("name", ["script", "img-onerror"])
def test_search_box_never_executes_what_users_type(page: Page, name: str) -> None:
    dialogs: list[str] = []
    page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.dismiss()))
    page.goto(UI)
    page.locator('[data-test="search-query"]').fill(PAYLOADS[name])
    page.locator('[data-test="search-submit"]').click()
    expect(page.locator('[data-test="search-caption"]')).to_be_visible()
    assert dialogs == [], f"script executed from search input: {dialogs}"
```
```python
# tests/security/test_headers.py: passive (one GET per URL), so the hosted site is fine here
import os

import pytest
import requests

TARGETS = {
    "api": os.getenv("QE_HEADERS_API", "https://api.practicesoftwaretesting.com/products"),
    "web": os.getenv("QE_HEADERS_WEB", "https://practicesoftwaretesting.com/"),
}
REQUIRED = {
    "api": ["strict-transport-security", "x-content-type-options"],
    "web": ["strict-transport-security", "x-content-type-options", "content-security-policy"],
}
KNOWN_MISSING = {  # (surface, header): bug id. Build yours from what you actually observe
    ("api", "strict-transport-security"): "SEC-001",
    ("api", "x-content-type-options"): "SEC-002",
}


@pytest.mark.parametrize(("surface", "header"), [(s, h) for s, hs in REQUIRED.items() for h in hs])
def test_security_header_present(surface: str, header: str) -> None:
    if (surface, header) in KNOWN_MISSING:
        pytest.xfail(f"{KNOWN_MISSING[(surface, header)]}: {header} missing on {surface} (filed)")
    response = requests.get(TARGETS[surface], timeout=10)
    assert header in {h.lower() for h in response.headers}, f"{header} missing on {TARGETS[surface]}"


def test_server_header_does_not_leak_versions() -> None:
    server = requests.get(TARGETS["api"], timeout=10).headers.get("Server", "")
    assert not any(ch.isdigit() for ch in server), f"Server header discloses a version: {server!r}"
```
Check the `data-test` selectors with codegen before relying on them. **Expect the header tests to fail on the hosted site:** when this guide was written, the web page lacked all three headers and the `Server` header disclosed a version. Each failure is a finding: file it, then add it to `KNOWN_MISSING` with its bug ID. Your known-missing list is *your* evidence file, so build it from what you observe, not from this example.

#### 🎤 Interview Q&A

<details><summary><b>[Z] What's the difference between authentication and authorisation?</b></summary>

Authentication establishes who you are (login, tokens, certificates). Authorisation decides what you're allowed to do once identified (roles, permissions, ownership of data). A system can authenticate perfectly and still let a logged-in customer read someone else's invoice. That's an authorisation bug, and the most common serious API vulnerability.
</details>

<details><summary><b>[Z] When should an API return 401, 403 or 404?</b></summary>

401 when the caller isn't authenticated (no token, or an invalid or expired one). 403 when they're authenticated but not allowed. 404 when the resource doesn't exist, and often deliberately *instead of* 403 for objects the caller mustn't know exist, so IDs can't be probed. Whatever the choice, it should be consistent, and the response body shouldn't contradict the status.
</details>

<details><summary><b>[H] What is BOLA (IDOR), and how do you test for it?</b></summary>

Broken Object Level Authorization: the API checks that you're logged in but not that the object you're asking for is yours, so changing an ID in the URL or body exposes someone else's data. Test it with at least two users of the same role: create or find an object as user A, then request, update and delete it as user B with every HTTP method, and expect 403 or 404. Automate it for every endpoint that takes an ID.
</details>

<details><summary><b>[H] Which security checks belong in a QE's automated suite, and which don't?</b></summary>

In the suite: authorisation matrices and ownership checks, token handling (missing, expired, revoked), input validation with hostile payloads (no 5xx, no leaked errors, nothing executed), security headers where they apply, dependency and image scanning, and a passive DAST baseline. Outside it: creative adversarial testing, business-logic abuse, cryptography review and active exploitation, which belong to security specialists and penetration tests. The QE suite makes the predictable checks continuous.
</details>

<details><summary><b>[SH] How do you make security testing part of the delivery process without slowing teams down?</b></summary>

Shift left and automate the predictable parts: threat-model questions in refinement, authorisation rules written as acceptance criteria, SAST and dependency scanning on every PR, authz and input tests in the regression suite, a passive DAST scan nightly, and severity-based gates with a reviewed exception process so noise doesn't lead people to disable checks. Keep specialists for periodic penetration tests and high-risk changes, and feed every finding back into an automated test.
</details>

#### 🤖 AI assist
- Paste your Swagger endpoint list (no tokens) and ask AI to propose the authorisation matrix. Compare it with yours: AI often assumes rules the product doesn't have, so every cell still needs your evidence.
- Never paste real tokens or production data into an AI tool, even from a demo app. That habit carries over to work.

---

### P11-04 · Non-functional gates in CI: performance smoke, ZAP baseline and accessibility

**Level:** 🟣 Super Hero · **Time:** 5h · **App:** your self-hosted stack in CI · **Deliverable:** `.github/workflows/non-functional.yml`, `scripts/perf_gate.py`, `.zap/rules.tsv`, `docs/non-functional-gates.md`

#### 📋 Task
1. Create a workflow that runs **nightly and on demand**, starts your demo stack (reuse the approach from P09-03) and waits until it's ready.
2. **Performance smoke:** run Locust headless for 2 minutes at modest load, then `scripts/perf_gate.py` checks every endpoint's p95 and error rate against budgets kept in version control. Upload the CSV and HTML reports and write a summary table to the job page.
3. **ZAP baseline (passive DAST):** scan your local Toolshop with the official ZAP Docker image. Keep accepted or irrelevant alerts in `.zap/rules.tsv`, and fail only on alerts you've marked `FAIL`.
4. **Accessibility gate:** run `tests/a11y` against the local Toolshop.
5. Write `docs/non-functional-gates.md`: which checks block and which are advisory, the thresholds, why they're set there, and how to change them (by PR, with a reason).

**Done when**
- [ ] The workflow runs nightly and on demand, uploads all three reports and writes a job summary
- [ ] You've seen each gate fail once (tighten a budget, add a failing ZAP rule, remove an allowlist entry) and pass again
- [ ] Budgets, ZAP rules and accessibility allowlists live in version-controlled files and change only through reviewed PRs

#### 📘 User guide

**Concepts**
- **Blocking vs advisory gates:** a blocking gate fails the pipeline; an advisory one reports without failing. Block on high-signal, low-noise checks.
- **Baseline vs threshold vs trend:** compare with the last good run, with a fixed budget, or over time. Performance on shared CI runners is noisy, so trends and generous thresholds work better than tight fixed numbers.
- **ZAP baseline scan:** OWASP ZAP spiders the site and *passively* inspects responses (headers, cookies, information leaks) without attacking it. It's safe to run in CI against your own environment.
- **ZAP active scan:** actually sends attacks. Only run one in an isolated environment, with permission.
- **Exit codes:** `zap-baseline.py` exits 0 when clean, 1 when there are FAIL-level alerts, 2 for warnings only, and 3 on errors. `-I` stops warnings from failing the step.

**Deep dive**

**Noise kills gates.** A gate that fails randomly gets rerun, then ignored, then deleted. Make each gate earn its place: per-endpoint budgets with headroom (e.g. 2× the typical p95 on the runner), ZAP alerts triaged once into a rules file (`IGNORE` for irrelevant, `WARN` for accepted with a reason, `FAIL` for what you'll never ship), and accessibility allowlists tied to bug IDs. Track how often each gate fails for reasons other than real problems; above a few percent, fix the gate before trusting it.

**Where to run what:** performance numbers from GitHub-hosted runners vary from run to run, so use them to catch *large* regressions and look at trends. For real capacity numbers, use a dedicated, stable environment (a self-hosted runner or a performance environment) on a schedule. A nightly schedule is a good default for all three checks here: they're slower than PR gates and don't need to block every commit.

**Everything as reviewed files:** budgets in `scripts/perf_gate.py` (or a YAML file it reads), ZAP rules in `.zap/rules.tsv`, and accessibility exceptions in the test module. Changing a threshold then needs a PR, a reason and a reviewer, which is how "we temporarily raised the budget" stops becoming permanent without anyone deciding it.

**Examples**

🟢 **Low: the per-endpoint budget gate**
```python
# scripts/perf_gate.py
"""Fail the build if an endpoint breaks its performance budget.

Usage: python scripts/perf_gate.py test-results/perf_stats.csv
Budgets live in this file on purpose: changing one is a reviewed PR, not a silent tweak.
"""

import csv
import sys

P95_BUDGET_MS = {
    "POST /auth": 500,
    "GET /booking": 500,
    "GET /booking/{id}": 300,
    "POST /booking": 800,
    "PUT /booking/{id}": 800,
}
MAX_ERROR_RATE = 0.01


def main(path: str) -> int:
    failures = []
    print("| Endpoint | Requests | Errors | p95 (ms) | Budget (ms) | Result |")
    print("|---|---|---|---|---|---|")
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            name = row["Name"]
            if name == "Aggregated":
                continue
            count, errors, p95 = int(row["Request Count"]), int(row["Failure Count"]), float(row["95%"])
            budget = P95_BUDGET_MS.get(name)
            problems = []
            if budget is None:
                problems.append("no budget defined")
            elif p95 > budget:
                problems.append(f"p95 {p95:.0f} > {budget}")
            if count and errors / count > MAX_ERROR_RATE:
                problems.append(f"errors {errors / count:.1%}")
            result = "❌ " + "; ".join(problems) if problems else "✅"
            print(f"| {name} | {count} | {errors} | {p95:.0f} | {budget or '—'} | {result} |")
            failures += [f"{name}: {problem}" for problem in problems]
    print(f"\n**{'FAIL' if failures else 'PASS'}** " + "; ".join(failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
```
An endpoint *without* a budget fails too: new endpoints can't slip in unmeasured.

🔵 **Medium: the nightly workflow**
```yaml
# .github/workflows/non-functional.yml
name: non-functional
on:
  schedule:
    - cron: "0 3 * * *"
  workflow_dispatch:

permissions:
  contents: read

jobs:
  non-functional:
    runs-on: ubuntu-latest
    timeout-minutes: 45
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --frozen
      - run: uv run playwright install --with-deps chromium
      - name: Start the demo stack
        run: make stack-up                     # from P04-06 / P09-03: starts Toolshop + Restful-Booker, waits for readiness
      - name: Performance smoke
        run: >
          uv run locust -f perf/locustfile.py --headless -u 10 -r 2 -t 2m
          --host http://localhost:3001 --csv test-results/perf --html test-results/perf.html
      - name: Performance budgets
        shell: bash
        run: uv run python scripts/perf_gate.py test-results/perf_stats.csv | tee -a "$GITHUB_STEP_SUMMARY"
      - name: ZAP baseline (passive)
        if: always()
        run: |
          cp .zap/rules.tsv test-results/
          docker run --rm --network host -v "$PWD/test-results:/zap/wrk:rw" ghcr.io/zaproxy/zaproxy:stable \
            zap-baseline.py -t http://localhost:4200 -c rules.tsv -r zap-report.html -J zap-report.json -I
      - name: Accessibility gate
        if: always()
        env:
          QE_TOOLSHOP_URL: http://localhost:4200
        run: uv run pytest tests/a11y -q
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: non-functional-reports
          path: test-results/
```
`if: always()` makes every check run and report even when an earlier one fails, so one bad night shows all three problems at once. `--network host` lets the ZAP container reach `localhost` on a Linux runner. On your Mac, drop it and target `http://host.docker.internal:4200` instead. Your a11y tests need to read `QE_TOOLSHOP_URL` instead of a hard-coded `BASE` for this step to scan the local app.

🟣 **High/Complex: triage ZAP once, then gate on what matters**
```bash
# 1. Generate a rules file listing every alert ZAP raised, all at WARN
docker run --rm -v "$PWD/test-results:/zap/wrk:rw" ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://host.docker.internal:4200 -g gen.conf -r first-scan.html
# 2. Triage: copy test-results/gen.conf to .zap/rules.tsv and set each rule to IGNORE, WARN or FAIL, with a comment
```
```text
# .zap/rules.tsv: rule id <TAB> action <TAB> (name and your reason)
10038	WARN	(Content Security Policy Header Not Set: accepted for the demo, see SEC-003)
10020	FAIL	(Missing Anti-clickjacking Header: never ship without it)
10096	IGNORE	(Timestamp Disclosure: false positive on build numbers)
```
Rule IDs and names come from *your* first scan's output. The ones above only show the format. From now on a new alert type shows up as `WARN` (visible but not blocking) until someone triages it, and anything marked `FAIL` blocks the nightly run. Put the rules file under CODEOWNERS (P09-02) so security review is automatic.

#### 🎤 Interview Q&A

<details><summary><b>[H] Which non-functional checks would you make blocking in CI, and which advisory?</b></summary>

Block on high-signal, low-noise checks with clear owners: critical dependency or image vulnerabilities, ZAP alerts explicitly marked FAIL, serious and critical accessibility violations not on a tracked allowlist, and large performance regressions against generous per-endpoint budgets. Keep advisory what's noisy or needs judgement: small performance deltas on shared runners, new unclassified ZAP warnings, and contrast checks axe marks as incomplete. Review the split regularly using data on false-alarm rates.
</details>

<details><summary><b>[H] What's the difference between a ZAP baseline scan and an active scan?</b></summary>

A baseline scan spiders the application and passively inspects responses (missing headers, insecure cookies, information leaks) without sending attacks, so it's quick and safe for CI against your own environment. An active scan sends real attack payloads (injection, XSS and more), which can modify data or take a system down, so it runs only in isolated environments, with permission, and usually on a schedule rather than per commit.
</details>

<details><summary><b>[SH] Performance tests in CI keep failing randomly. What do you do?</b></summary>

Measure the noise first: run the same build repeatedly and look at the spread per endpoint. Then reduce it (warm-up, fixed data, isolated or dedicated runners, fewer parallel jobs), widen budgets to sit above normal variance, and compare against a rolling baseline or trend instead of a single fixed number. Move precise capacity testing to a stable environment on a schedule. A performance gate that cries wolf will be ignored, so fix the gate's reliability before tightening it.
</details>

#### 🤖 AI assist
- Give AI your first ZAP report and ask it to explain each alert *for this app* and propose IGNORE, WARN or FAIL with a reason. Then decide yourself: you own the risk decision, not the model.

---

## 🏁 Phase checkpoint: P11

**Self-check:** without notes, can you explain load vs stress vs soak testing and why percentiles beat averages; WCAG AA and what axe can't find; 401 vs 403 vs 404 and how you'd test for BOLA; the difference between a ZAP baseline and an active scan; and which non-functional checks you'd block on in CI?

**AI mock interviewer prompt** (paste into your AI assistant):
```text
You are interviewing me for a mid-level QE / SDET role. Focus on non-functional
testing: performance (workload models, percentiles, test types, CI budgets),
accessibility (WCAG 2.2 AA, automated vs manual checks, keyboard and screen-reader
testing) and security for testers (authentication vs authorisation, BOLA/IDOR,
OWASP API Top 10, input handling, headers, DAST in CI). Ask 8 questions one at a
time, including 2 "design a test for ..." scenarios. After each answer, score 1-5
and say what a strong answer adds. End with my 3 weakest areas and one exercise
for each.
```
Record your score and gaps in `interview-notes/P11.md`.
