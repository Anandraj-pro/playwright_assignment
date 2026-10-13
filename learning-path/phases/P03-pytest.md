# P03: pytest

> **Goal:** master the test runner every Python QE job uses: structure, **debugging failures**, data-driven tests, fixtures, markers, CLI options and plugins.
> **Apps:** your P02 code, SauceDemo data, Restful-Booker. **Prerequisites:** P02. **Time:** ~17 h.

| ID | Task | Level | Time |
|---|---|---|---|
| P03-01 | First pytest suite: discovery, assertions, running | 🟢 | 2h |
| P03-02 | Debug a failing test: tracebacks, breakpoints and pytest's debugging flags | 🟢 | 2h |
| P03-03 | Parametrize and data-driven tests | 🟢 | 2h |
| P03-04 | Fixtures deep dive and conftest | 🔵 | 4h |
| P03-05 | Markers, config and custom CLI options | 🔵 | 3h |
| P03-06 | Hooks, plugins and coverage | 🟣 | 4h |

---

### P03-01 · First pytest suite: discovery, assertions, running

**Level:** 🟢 Zero · **Time:** 2h · **App:** — · **Deliverable:** `tests/unit/test_products.py`, `tests/unit/test_checkout.py`, `tests/unit/test_drills.py`

#### 📋 Task
1. Move every P02 `assert` into pytest test functions (one behaviour per test).
2. Use `pytest.raises(..., match=...)` for exceptions and `pytest.approx` where floats are unavoidable.
3. Practise and note in `docs/pytest-cli.md` what each does: `-v`, `-q`, `-x`, `-k`, `--lf`, `--ff`, `-s`, `--tb=short`, `--durations=5`, `--co`.
4. Break one function on purpose and confirm a test fails with a readable message, then fix it.

**Done when**
- [ ] `uv run pytest tests/unit -q` is green
- [ ] Every test name reads like a sentence: `test_tax_is_rounded_half_up_to_cents`
- [ ] You've seen each of pytest's exit codes 0, 1 and 5

#### 📘 User guide

**Concepts**
- **Discovery:** files `test_*.py` or `*_test.py` → functions `test_*` → classes `Test*` (no `__init__`) with `test_*` methods.
- **Plain `assert`:** pytest *rewrites* asserts to show both sides on failure, so there's no `assertEqual` zoo.
- **AAA:** *Arrange* (set up), *Act* (do one thing), *Assert* (check the outcome).
- **Exit codes:** `0` all passed, `1` some failed, `2` interrupted, `3` internal error, `4` usage error, `5` no tests collected.

**Deep dive**

**Assertion rewriting.** At import time pytest rewrites `assert` statements in test modules so a failure prints intermediate values (`assert 2.39 == 2.40` plus where each came from). That's why helper modules containing asserts should be registered with `pytest.register_assert_rewrite`, or just keep asserts in tests.

**Exit codes matter in CI.** CI fails a job on non-zero exit. Exit code **5** (no tests collected) catches a real trap: a typo in `-m smok` silently runs *nothing*, and without treating 5 as failure your gate would be "green".

**One behaviour per test.** When a test fails its name should tell you what broke. Multiple asserts are fine if they check *one behaviour* (e.g. all three totals fields). Unrelated checks belong in separate tests.

**Do your tests catch bugs?** A test that never fails is decoration. **Mutation testing** (tools like `mutmut`) flips operators and constants in your code and checks that some test fails. Surviving mutants reveal weak assertions. Do the manual version now: break the code and watch the test go red.

**Examples**

🟢 **Low: a first test and an exception test**
```python
# tests/unit/test_checkout.py
from decimal import Decimal
import pytest
from python_basics.checkout import calculate_totals, validate_checkout, CheckoutValidationError

def test_tax_is_eight_percent_rounded_to_cents():
    assert calculate_totals([Decimal("29.99")])["tax"] == Decimal("2.40")

def test_missing_last_name_is_rejected():
    with pytest.raises(CheckoutValidationError, match="Last Name is required"):
        validate_checkout("Ada", "", "12345")
```

🔵 **Medium: grouping, AAA and approx**
```python
import pytest
from python_basics.products import PRODUCTS, sort_products, is_sorted

class TestSorting:
    def test_low_to_high_orders_prices_ascending(self):
        # Arrange
        products = list(PRODUCTS)
        # Act
        result = sort_products(products, "lohi")
        # Assert
        assert is_sorted([p["price"] for p in result])

    def test_unknown_mode_fails_fast(self):
        with pytest.raises(KeyError):
            sort_products(PRODUCTS, "random")

def test_average_rating_float():
    assert (0.1 + 0.2) == pytest.approx(0.3)      # floats: approx, money: Decimal
```

🟣 **High/Complex: prove tests catch bugs (manual mutation testing)**
```bash
# 1. Mutate: in checkout.py change ROUND_HALF_UP → ROUND_DOWN
uv run pytest tests/unit/test_checkout.py -q     # must FAIL; if green, your tests are too weak
# 2. Mutate: change `if not value.strip()` → `if not value`
uv run pytest -k "whitespace" -q                  # do you have a test for "   " input? add one
# 3. Restore and run with details
uv run pytest -q --durations=5 --tb=short
# Automated version (explore): uv add --dev mutmut, then follow its docs to run on python_basics/
```
Write in `docs/pytest-cli.md` which mutants survived and the test you added to kill each.

#### 🎤 Interview Q&A

<details><summary><b>[Z] How does pytest find tests?</b></summary>

From the rootdir or `testpaths`, it collects files named `test_*.py` or `*_test.py`, then functions starting with `test`, and classes starting with `Test` (without an `__init__`) containing `test*` methods. You can customise this with `python_files`, `python_classes` and `python_functions` in config. `pytest --co` shows what would be collected.
</details>

<details><summary><b>[H] Why can pytest use plain <code>assert</code> when unittest needs <code>assertEqual</code>?</b></summary>

pytest rewrites the assert statements' AST at import time to capture sub-expression values, so failures show detailed diffs (including for dicts and lists). unittest predates this and uses methods to produce messages.
</details>

<details><summary><b>[H] Your CI job ran <code>pytest -m smok</code> and was green. What happened?</b></summary>

The typo matched no tests, so pytest exited with code 5 ("no tests collected"). If CI treats that as success (or the step ignores it), the gate is fake-green. Prevent it with registered markers plus `--strict-markers` (which catches unknown markers used *on tests*), by failing on exit code 5, and by checking collected-test counts in the job summary.
</details>

<details><summary><b>[Z] What is the AAA pattern?</b></summary>

Arrange, Act, Assert: set up preconditions, perform the single action under test, then verify the outcome. It keeps tests readable and focused on one behaviour. (BDD's Given/When/Then is the same idea.)
</details>

<details><summary><b>[SH] How do you know your test suite actually catches bugs?</b></summary>

Coverage only says code *ran*, not that it was *checked*. Mutation testing measures the suite's ability to detect injected faults. Also: review assertions for strength (exact values, not just "not None"), check historical defect escape rate (bugs found in prod that tests should have caught), and deliberately break features in a sandbox (the Toolshop with-bugs version is great for this).
</details>

#### 🤖 AI assist
- Ask AI to generate *mutants* of your function (small code changes) and check whether your tests kill each one.

---

### P03-02 · Debug a failing test: tracebacks, breakpoints and pytest's debugging flags

**Level:** 🟢 Zero · **Time:** 2h · **App:** — (a debugging lab) · **Deliverable:** `tests/unit/test_debug_lab.py`, `docs/debugging.md`

#### 📋 Task
1. Create `tests/unit/test_debug_lab.py` from the 🟢 example and run `uv run pytest tests/unit/test_debug_lab.py`. Three tests fail, each for a different reason.
2. For each failure, **read the output bottom-up and write a hypothesis *before* changing anything.**
3. Use every tool at least once: `-x`, `--lf`, `-l` (`--showlocals`), `--pdb` (then `p`, `pp`, `l`, `w`, `u`, `q`), a `breakpoint()` in the code, and your **IDE's debugger** with a breakpoint (VS Code *Debug Test*, or PyCharm's bug icon).
4. Run the failing cart test **on its own**. It passes. Explain why before you fix it.
5. Fix the *code under test*, not the assertions. (If you ever decide a test is wrong, say why in your notes.)
6. In `docs/debugging.md`, for each bug record the symptom, your hypothesis, the evidence and the tool that gave it, the root cause, the fix, and how you'd prevent it next time.

**Done when**
- [ ] All lab tests pass, both together and one at a time
- [ ] `docs/debugging.md` has symptom → hypothesis → evidence → root cause → fix → prevention for all three bugs
- [ ] You've used `--pdb` and an IDE breakpoint at least once each, and can say when you'd reach for each

#### 📘 User guide

**Concepts**
- **Traceback:** the chain of calls that led to an error. Read it **bottom-up**: the last line is the error, and the frames above show how you got there. Find the first frame in *your* code.
- **Assertion introspection:** pytest rewrites `assert` so a failure shows the values on both sides (`Decimal('1') == Decimal('1299.00')`). Read those values before anything else.
- **Useful flags:** `-x` (stop at the first failure), `--lf` (re-run only last failures), `-l` (show local variables in tracebacks), `-s` (show `print` output), `-k expr` (select by name), `-vv` (full diffs), `--pdb` (open the debugger at the failure), `--trace` (open it at the start of each test).
- **pdb:** Python's built-in debugger. `p expr` prints, `pp` pretty-prints, `l` lists code, `w` shows where you are, `u`/`d` move up and down the stack, `n` runs the next line, `s` steps into a call, `c` continues, `q` quits.
- **`breakpoint()`:** a line you put in code to pause there and open the debugger (pytest disables output capture automatically when it hits one).
- **IDE debugger:** the same thing with a UI: click in the margin to set a breakpoint, run the test in debug mode, and inspect variables with the mouse.

**Deep dive**

**Debugging is the scientific method, done quickly.** Observe the symptom, form a hypothesis ("the price parser drops everything after the comma"), predict what you'd see if it were true, and run the cheapest experiment that could prove it wrong: print a value, run one test alone, or pause in the debugger. Changing code at random until the test goes green isn't debugging; it's how new bugs get in.

**Each lab bug teaches a pattern you'll meet at work:**
- **Wrong value:** the assertion shows the values. Ask *which input* produces it, and whether that input is a boundary (a thousands separator is a boundary that the "happy" test didn't include).
- **Passes alone, fails with others:** shared state between tests. Here it's a Python classic, a **mutable default argument** (`cart=[]` is created once and shared by every call). In real suites the shared state is a database row, a logged-in browser or a global variable (P05-04, P07-02). Note the `# noqa: B006` in the lab: ruff *would* have caught this bug, and someone had switched that check off.
- **An exception deep in a data structure:** `KeyError: 'checkOut'` means the key isn't there. `--pdb` lets you type `p dates.keys()` and see instantly that the API uses `checkin` / `checkout`. Your code assumed a different contract (P04-08 is all about contracts).

**print vs logging vs the debugger:** `print` is fine for a 30-second experiment (run with `-s`). Use `logging` for anything you'd want to see in CI later, because pytest captures it and shows it only for failing tests (`--log-cli-level=INFO` shows it live). Reach for the debugger when you don't yet know *which* value to look at: pause, look around, move up the stack.

**When the bug is "it worked yesterday":** narrow it down. What changed (code, data, dependency versions, environment)? `git bisect` can find the exact commit that broke a test automatically (🟣 example). Dependency changes show up in the `uv.lock` diff.

**Examples**

🟢 **Low: the debugging lab** (copy it exactly, bugs included)
```python
# tests/unit/test_debug_lab.py: three bugs, three debugging tools. Fix the CODE, not the asserts.
from datetime import date
from decimal import Decimal


def parse_price(text: str) -> Decimal:
    """'$29.99' -> Decimal('29.99') and '$1,299.00' -> Decimal('1299.00')."""
    return Decimal(text.lstrip("$").split(",")[0])


def add_to_cart(item: str, cart: list[str] = []) -> list[str]:  # noqa: B006
    cart.append(item)
    return cart


def nights(booking: dict) -> int:
    dates = booking["bookingdates"]
    return (date.fromisoformat(dates["checkOut"]) - date.fromisoformat(dates["checkIn"])).days


BOOKING = {"firstname": "Jim", "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-04"}}


def test_parse_simple_price() -> None:
    assert parse_price("$29.99") == Decimal("29.99")


def test_parse_price_with_thousands_separator() -> None:
    assert parse_price("$1,299.00") == Decimal("1299.00")


def test_first_item_goes_into_an_empty_cart() -> None:
    assert add_to_cart("backpack") == ["backpack"]


def test_every_new_cart_starts_empty() -> None:
    assert add_to_cart("bike light") == ["bike light"]


def test_nights_for_a_three_night_booking() -> None:
    assert nights(BOOKING) == 3
```
```bash
uv run pytest tests/unit/test_debug_lab.py                     # 3 failures
uv run pytest tests/unit/test_debug_lab.py -x -l               # stop at the first, show locals
uv run pytest tests/unit/test_debug_lab.py -k new_cart         # the cart test alone: it passes!
uv run pytest tests/unit/test_debug_lab.py --lf --pdb          # re-run the failures, debug each
```

🔵 **Medium: a post-mortem pdb session on the `KeyError`**
```text
$ uv run pytest tests/unit/test_debug_lab.py -k nights --pdb
E       KeyError: 'checkOut'
>>> entering PDB >>>
> tests/unit/test_debug_lab.py(18)nights()
-> return (date.fromisoformat(dates["checkOut"]) - date.fromisoformat(dates["checkIn"])).days
(Pdb) p dates.keys()
dict_keys(['checkin', 'checkout'])
(Pdb) u
> tests/unit/test_debug_lab.py(41)test_nights_for_a_three_night_booking()
-> assert nights(BOOKING) == 3
(Pdb) pp BOOKING
{'bookingdates': {'checkin': '2026-01-01', 'checkout': '2026-01-04'},
 'firstname': 'Jim'}
(Pdb) q
```
Two commands answered the question: the data uses lowercase keys, so the code's assumption is wrong. The fix belongs in `nights()`, and the *prevention* is a typed model that fails loudly on the wrong shape (pydantic, P04-04).

🟣 **High/Complex: debug what you can't reproduce locally**

When an API test fails only in CI, make every HTTP exchange visible in the failure report:
```python
# tests/api/conftest.py (you'll build this folder in P04)
import logging

import pytest
import requests

log = logging.getLogger("http")


def _log_exchange(response: requests.Response, *args: object, **kwargs: object) -> None:
    request = response.request
    elapsed_ms = response.elapsed.total_seconds() * 1000
    log.info("%s %s -> %s in %.0f ms", request.method, request.url, response.status_code, elapsed_ms)
    log.debug("request body: %s", request.body)
    log.debug("response body: %s", response.text[:500])


@pytest.fixture
def http() -> requests.Session:
    session = requests.Session()
    session.hooks["response"].append(_log_exchange)
    return session
```
pytest attaches captured logs to each *failing* test's report, so a CI failure now shows the exact requests and responses. Run with `--log-cli-level=INFO` to watch them live.

When a test that used to pass starts failing, let Git find the guilty commit:
```bash
git bisect start
git bisect bad                    # the current commit fails
git bisect good v0.3.0            # this tag passed
git bisect run uv run pytest tests/unit/test_pricing.py -q
git bisect reset
```
`git bisect run` binary-searches the history, running the test at each step, and names the first bad commit, usually in a handful of steps even across hundreds of commits.

#### 🎤 Interview Q&A

<details><summary><b>[Z] How do you read a Python traceback?</b></summary>

Bottom-up. The last line is the exception type and message; the frames above show the call chain that led there, most recent last. Find the first frame in *your* code rather than the library's, read the line and the local values (`-l` helps), and form a hypothesis about why the data or state was wrong at that point.
</details>

<details><summary><b>[Z] A test passes on its own but fails when run with the others. What's likely going on?</b></summary>

Shared state: one test leaves something behind that another depends on or is broken by, such as a global or class variable, a mutable default argument, a database row, a logged-in browser session or a file. Prove it by running the pair in different orders, then fix it by giving each test its own fresh state through fixtures, unique data and teardown.
</details>

<details><summary><b>[Z] Which pytest options do you use most when debugging?</b></summary>

`-x` to stop at the first failure, `--lf` to re-run only the last failures, `-k` to select one test, `-l` to show local variables, `-vv` for full diffs, `-s` to see prints, `--log-cli-level` to see logs live, and `--pdb` to open the debugger where it failed.
</details>

<details><summary><b>[H] When do you use a debugger rather than print statements or logs?</b></summary>

Print is fine for a quick check of one value you already suspect. Logging is for information you'll want in CI and on future failures. A debugger is best when you don't yet know what to look at: you can pause at the failure, inspect any variable, walk up the call stack and try expressions interactively, without re-running the test for each guess.
</details>

<details><summary><b>[H] A test fails only in CI. How do you debug it?</b></summary>

Get the evidence CI already has: logs, the JUnit report, traces, screenshots, captured HTTP exchanges. Compare environments (versions, config, secrets, data, time zone, parallelism, resources). Reproduce CI's conditions locally: the same container image, the same flags (`-n`, random order), the same env vars. Add the missing observability for next time, and avoid "fixing" it with retries until you understand it.
</details>

<details><summary><b>[SH] How do you help a team get faster at diagnosing test failures?</b></summary>

Make failures self-explanatory: assertion messages with context, captured HTTP exchanges and traces attached to every failure, and a failure summary in the CI job page. Classify failures (product bug, test bug, environment, flaky) and track the time from red build to diagnosis. Keep a runbook of common failure signatures, and automate the first triage step (P12-04's triage agent does exactly that).
</details>

#### 🤖 AI assist
- Paste **only** the failure output (no fixes yet) and ask AI for three competing hypotheses and the cheapest experiment to tell them apart. Then run the experiments yourself.
- Don't ask for "the fix" until you've written your own hypothesis in `docs/debugging.md`. That hypothesis is the skill interviewers test in live-coding rounds.

---

### P03-03 · Parametrize and data-driven tests

**Level:** 🟢 Zero · **Time:** 2h · **App:** SauceDemo data · **Deliverable:** `tests/unit/test_checkout_params.py`, `tests/unit/test_users_data.py`

#### 📋 Task
1. Parametrize `calculate_totals` for 1, 2 and 3 items with readable `ids`.
2. Parametrize `validate_checkout` for each missing field, including whitespace-only values.
3. Load `saucedemo_users.csv` (P02-03) into a parametrize decorator with `ids=username`.
4. Use `pytest.param(..., marks=pytest.mark.xfail(reason="..."))` for one known-bug case.
5. Stack two parametrize decorators and observe the cartesian product in `pytest --co -q`.

**Done when**
- [ ] `pytest --co -q` shows readable IDs like `test_login_data[locked_out_user]`
- [ ] Every parametrized case is reported separately

#### 📘 User guide

**Concepts**
- **`@pytest.mark.parametrize("a,b", [(1, 2), (3, 4)])`:** run one test body per data row.
- **`ids`:** names for each case in reports (a list or a function).
- **`pytest.param(values, id=..., marks=...)`:** a per-case id or marks (xfail/skip).
- **Stacking:** two parametrize decorators give every combination (cartesian product).

**Deep dive**

**Parametrize vs a loop inside a test.** A loop stops at the first failure and reports one test. Parametrize runs *every* case independently, reports each separately, and supports `--lf` re-runs of just the failed case. Always parametrize.

**Parametrize the *data*, not the *behaviour*.** "Valid login" and "locked-out login" check different outcomes. You can parametrize them with an `expected` column, but if the test body needs `if expected_error:` branches everywhere, split it into two tests. Branches inside tests are a smell.

**Combinatorial explosion.** 3 browsers × 6 users × 4 sort modes = 72 runs. Stack only what truly interacts. For large input spaces use **pairwise testing** (every *pair* of values covered at least once), which cuts combinations dramatically with little loss in defect detection.

**Collection-time data.** Parametrize arguments are evaluated when the module is imported, so a broken CSV fails *collection* for the whole file with a clear error. That's good: bad data is caught before anything runs.

**Examples**

🟢 **Low: parametrize with ids**
```python
import pytest
from decimal import Decimal
from python_basics.checkout import calculate_totals

@pytest.mark.parametrize(
    "prices, expected_total",
    [
        ([Decimal("29.99")], Decimal("32.39")),
        ([Decimal("29.99"), Decimal("9.99")], Decimal("43.18")),
        ([Decimal("7.99"), Decimal("15.99"), Decimal("49.99")], Decimal("79.89")),
    ],
    ids=["one-item", "two-items", "three-items"],
)
def test_total_includes_tax(prices, expected_total):
    assert calculate_totals(prices)["total"] == expected_total
```
> Check the expected totals against the SauceDemo UI yourself. That *is* the exercise.

🔵 **Medium: data from CSV plus a known-bug xfail**
```python
import pytest
from python_basics.data_io import load_csv

USERS = load_csv("saucedemo_users.csv")

@pytest.mark.parametrize("user", USERS, ids=lambda u: u["username"])
def test_user_record_is_consistent(user):
    # a user that cannot log in must have an expected error message
    assert user["can_login"] or user["expected_error"]

@pytest.mark.parametrize("first, last, postal, message", [
    ("", "Doe", "123", "First Name is required"),
    ("Ada", "", "123", "Last Name is required"),
    ("Ada", "Doe", "", "Postal Code is required"),
    pytest.param("   ", "Doe", "123", "First Name is required", id="whitespace-first"),
    pytest.param("Ada", "Doe", "ABC", "Postal Code is invalid", id="letters-postal",
                 marks=pytest.mark.xfail(reason="BUG-12: validator doesn't check postal format yet", strict=True)),
])
def test_checkout_validation(first, last, postal, message):
    from python_basics.checkout import validate_checkout, CheckoutValidationError
    with pytest.raises(CheckoutValidationError, match=message):
        validate_checkout(first, last, postal)
```

🟣 **High/Complex: dynamic parametrization with the <code>pytest_generate_tests</code> hook**
```python
# tests/unit/conftest.py
from python_basics.data_io import load_csv

def pytest_generate_tests(metafunc):
    """Any test that asks for `sauce_user` is run once per CSV row; `--only-login-ok` filters rows."""
    if "sauce_user" in metafunc.fixturenames:
        rows = load_csv("saucedemo_users.csv")
        if metafunc.config.getoption("--only-login-ok", default=False):
            rows = [r for r in rows if r["can_login"]]
        metafunc.parametrize("sauce_user", rows, ids=[r["username"] for r in rows])

def pytest_addoption(parser):
    parser.addoption("--only-login-ok", action="store_true", help="only users that can log in")
```
```python
# tests/unit/test_dynamic.py
def test_username_has_no_spaces(sauce_user):
    assert " " not in sauce_user["username"]
```
The hook decouples *which data* from *which test*. The same pattern powers "run every test against every environment/browser" plugins.

#### 🎤 Interview Q&A

<details><summary><b>[Z] Why parametrize instead of looping inside one test?</b></summary>

Each case becomes its own test: independent pass/fail, separate report lines, re-runnable with `--lf`, and one failure doesn't hide the others. A loop stops at the first failing assert and reports a single result.
</details>

<details><summary><b>[H] How do you drive tests from CSV or Excel?</b></summary>

Load the file at collection time (csv module, openpyxl or pandas for Excel), convert types explicitly, and feed rows into `parametrize` with ids from a meaningful column. Validate the data (required columns) so a bad row fails collection clearly. For large or shared datasets, use the `pytest_generate_tests` hook so tests declare what data they need rather than where it comes from.
</details>

<details><summary><b>[H] What happens when you stack two parametrize decorators?</b></summary>

You get the cartesian product: every value of the first combined with every value of the second. Two lists of 3 give 9 tests. It's useful for real interactions (browser × viewport) but explodes quickly, so use it deliberately.
</details>

<details><summary><b>[SH] Your data-driven suite has 5 parameters with 4 values each (1,024 combos). What do you do?</b></summary>

Don't run all of them. Use equivalence partitioning to cut values per parameter, then pairwise (all-pairs) generation to cover every pair of values in roughly 16–25 cases. Add targeted cases for known risky combinations and boundary values. Run the exhaustive set nightly only if it's cheap (API level), never in PR gates.
</details>

<details><summary><b>[SH] When would you use <code>pytest_generate_tests</code> instead of the decorator?</b></summary>

When parameters depend on runtime config (CLI options, environment, a file chosen at run time), when many tests share the same dataset by fixture name, or when building a plugin (e.g. running every test per tenant). The decorator is static; the hook is dynamic.
</details>

#### 🤖 AI assist
- Give AI your input fields and ask for an **equivalence-partition + boundary table**, then turn the good rows into `pytest.param` cases.

---

### P03-04 · Fixtures deep dive and conftest

**Level:** 🔵 Hero · **Time:** 4h · **App:** Restful-Booker · **Deliverable:** `tests/conftest.py`, `tests/api/conftest.py`, `tests/api/booker/test_booking_fixtures.py`

#### 📋 Task
1. `tests/conftest.py`: a **session** fixture `settings` (from P02-05) and a session fixture `http` (a `requests.Session` closed at teardown).
2. `tests/api/conftest.py`: a session fixture `booker_token` (`POST /auth`) and a **function** fixture `booking` that creates a booking and deletes it after the test (yield).
3. A **factory fixture** `make_booking(**overrides)` that can be called many times in one test and deletes *everything* it created at teardown.
4. Use built-ins: `tmp_path` (write a file), `monkeypatch` (override an env var), `caplog` (assert a log line), `request` (read the test name).
5. Run `pytest --setup-show` and explain the output in `docs/fixtures.md`.

**Done when**
- [ ] No booking created by your tests remains after the run, even when a test fails
- [ ] `--setup-show` shows the token fetched once per session and bookings per test

#### 📘 User guide

**Concepts**
- **Fixture:** a function that provides a resource to tests that name it as a parameter (dependency injection).
- **Scope:** `function` (default), `class`, `module`, `package`, `session`. This is how long a fixture's value is cached.
- **`yield` fixture:** code before `yield` is setup, after it is teardown (it runs even if the test fails).
- **Factory fixture:** returns a *function* so tests can create N resources with different data.
- **`conftest.py`:** fixtures here are visible to all tests in that directory and below, with no import needed.
- **Built-ins:** `tmp_path`, `monkeypatch`, `caplog`, `capsys`, `request`, `pytestconfig`.

**Deep dive**

**How pytest resolves fixtures.** For each test, pytest reads parameter names, finds fixtures with those names (nearest `conftest.py` wins, which lets you **override** a fixture in a subfolder), builds the dependency graph, and executes it: higher scopes first, cached per scope. Teardown runs in **reverse (LIFO)** order.

**Scope rules.** A fixture can depend only on fixtures of the **same or wider** scope. A session `booker_token` can use a session `http`, but a session fixture requesting a function fixture raises `ScopeMismatch`. Choose scope by *cost vs isolation*:
| Resource | Scope | Why |
|---|---|---|
| Settings, HTTP session, auth token | session | Expensive, read-only |
| Browser (pytest-playwright) | session | Expensive to launch |
| Browser context/page | function | Isolation: fresh cookies/storage |
| Created test data | function | Each test owns its data |

**Factory fixtures** solve "I need 3 bookings with different names" without writing 3 fixtures, and centralise cleanup: the factory records every ID it creates and deletes them all in teardown.

**Avoid sharing state between tests.** Tests that pass data through globals or depend on order break under `--lf`, `-k`, random order and parallel runs (P07). Share **setup** via fixtures, never **results** via variables.

**autouse=True** runs a fixture for every test in scope without being requested. It's handy for global concerns (logging context, screenshot on failure) but invisible magic otherwise, so use it sparingly.

**Examples**

🟢 **Low: session fixtures with teardown**
```python
# tests/conftest.py
import pytest, requests
from framework.config import get_settings

@pytest.fixture(scope="session")
def settings():
    return get_settings()

@pytest.fixture(scope="session")
def http():
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})
    yield session                 # ← tests run here
    session.close()               # teardown, always
```

🔵 **Medium: auth token plus a create/delete data fixture**
```python
# tests/api/conftest.py
import pytest

@pytest.fixture(scope="session")
def booker_url(settings):
    return settings.booker_url

@pytest.fixture(scope="session")
def booker_token(http, booker_url, settings):
    r = http.post(f"{booker_url}/auth", json={"username": "admin", "password": "password123"},
                  timeout=settings.http_timeout)
    r.raise_for_status()
    return r.json()["token"]

@pytest.fixture
def booking(http, booker_url, booker_token, settings):
    from python_basics.checkout import build_booking   # P02-02 builder
    r = http.post(f"{booker_url}/booking", json=build_booking(), timeout=settings.http_timeout)
    r.raise_for_status()
    created = r.json()                                   # {"bookingid": 123, "booking": {...}}
    yield created
    http.delete(f"{booker_url}/booking/{created['bookingid']}",
                cookies={"token": booker_token}, timeout=settings.http_timeout)
```

🟣 **High/Complex: a factory fixture with tracked cleanup, built-ins and overrides**
```python
# tests/api/conftest.py (continued)
import logging
import pytest

log = logging.getLogger("fixtures")

@pytest.fixture
def make_booking(http, booker_url, booker_token, settings, request):
    created: list[int] = []

    def _make(**overrides):
        from python_basics.checkout import build_booking
        r = http.post(f"{booker_url}/booking", json=build_booking(**overrides), timeout=settings.http_timeout)
        r.raise_for_status()
        booking_id = r.json()["bookingid"]
        created.append(booking_id)
        log.info("[%s] created booking %s", request.node.name, booking_id)
        return r.json()

    yield _make

    for booking_id in reversed(created):                 # LIFO cleanup
        resp = http.delete(f"{booker_url}/booking/{booking_id}",
                           cookies={"token": booker_token}, timeout=settings.http_timeout)
        if resp.status_code >= 400:
            log.warning("cleanup failed for %s: %s", booking_id, resp.status_code)
```
```python
# tests/api/booker/test_booking_fixtures.py
import logging

def test_filter_by_lastname_returns_only_matches(make_booking, http, booker_url, caplog):
    caplog.set_level(logging.INFO)
    a = make_booking(lastname="Zyx-Unique-1")
    make_booking(lastname="Other")
    ids = [b["bookingid"] for b in http.get(f"{booker_url}/booking",
                                            params={"lastname": "Zyx-Unique-1"}, timeout=10).json()]
    assert a["bookingid"] in ids
    assert "created booking" in caplog.text

def test_env_override(monkeypatch):
    monkeypatch.setenv("QE_BOOKER_URL", "http://localhost:3001")   # auto-restored after test
    from framework.config import Settings
    assert Settings().booker_url == "http://localhost:3001"

def test_writes_report(tmp_path):
    report = tmp_path / "report.txt"                               # unique temp dir per test
    report.write_text("ok")
    assert report.read_text() == "ok"
```
Run `uv run pytest tests/api/booker -q --setup-show` and read the `SETUP S` / `SETUP F` lines.

#### 🎤 Interview Q&A

<details><summary><b>[Z] What are fixture scopes? Give an example of each.</b></summary>

`function` (default; created per test, e.g. test data or a browser page), `class` (shared by a test class), `module` (per file, e.g. a read-only dataset), `package` (per directory package), `session` (once per run, e.g. settings, HTTP session, browser, auth token). Wider scope is faster but risks shared state.
</details>

<details><summary><b>[Z] What is <code>conftest.py</code>?</b></summary>

A special file where fixtures and hooks are defined for its directory and all subdirectories. Tests use them by name without importing. Nested conftests can add or override fixtures for a subtree.
</details>

<details><summary><b>[H] <code>yield</code> fixture vs <code>request.addfinalizer</code>?</b></summary>

Both register teardown. `yield` is simpler and reads top to bottom. `addfinalizer` lets you register multiple finalizers dynamically, and registers teardown *before* risky setup completes (if setup fails after the `yield`-less part, `yield` teardown won't run). Modern code mostly uses `yield` and splits risky setup into separate fixtures.
</details>

<details><summary><b>[H] What is a ScopeMismatch error?</b></summary>

A fixture requested a fixture with a *narrower* scope, e.g. a session-scoped fixture depending on a function-scoped one. The wider fixture would outlive its dependency. Fix by widening the dependency's scope or narrowing the requester's.
</details>

<details><summary><b>[H] How do you share data between tests?</b></summary>

You shouldn't share *results* between tests: each test must be independent and order-agnostic (so it survives `-k`, `--lf`, random order and parallel runs). Share *setup* through fixtures at the appropriate scope, and create per-test data via factory fixtures.
</details>

<details><summary><b>[SH] How does fixture teardown behave when a test fails, or when setup fails halfway?</b></summary>

If the test fails, all yield fixtures still resume and run teardown in reverse order. If a fixture's setup raises *before* its `yield`, its own teardown doesn't run (it never yielded), but already-created fixtures still tear down. So make each fixture own exactly one resource, making partial failure clean. Factory fixtures should record IDs immediately after creation.
</details>

#### 🤖 AI assist
- Paste your `--setup-show` output into AI and ask it to explain the order, then check the explanation against the pytest docs on fixture scopes.

---

### P03-05 · Markers, config and custom CLI options

**Level:** 🔵 Hero · **Time:** 3h · **App:** all · **Deliverable:** `[tool.pytest.ini_options]` in `pyproject.toml`, `--env` option in `tests/conftest.py`

#### 📋 Task
1. Extend the `[tool.pytest.ini_options]` section the template gave you (P00-04): register the markers `smoke`, `regression`, `api`, `ui`, `db`, `slow` and `quarantine`. `--strict-markers` is already on; prove it by running a test with a misspelled marker.
2. Mark your existing tests. Practise `-m "smoke and not ui"`.
3. Add `--env {public,local,docker}` that switches all URLs (public demo apps / localhost / Docker service names).
4. `skipif` DB tests when `--env public` (no DB access). `xfail(strict=True)` a known bug with a link.
5. Configure `log_cli` and a log format in the pytest config.

**Done when**
- [ ] `pytest --env local -m smoke` targets localhost URLs (prove it with a log line)
- [ ] An unregistered marker causes an error
- [ ] `docs/markers.md` explains which markers each CI gate runs

#### 📘 User guide

**Concepts**
- **Marker:** a label on a test (`@pytest.mark.smoke`) used for selection (`-m`) or behaviour (`skip`, `xfail`).
- **`--strict-markers`:** unknown markers become errors, so typos can't hide tests.
- **`skip`/`skipif`:** don't run (not applicable here). **`xfail`:** run it, and a failure is *expected* (a known bug). `strict=True` fails when it unexpectedly passes.
- **`pytest_addoption` + `request.config.getoption()`:** your own CLI flags.
- **ini options:** `addopts`, `testpaths`, `markers`, `log_cli`, `log_cli_level`, `xfail_strict`.

**Deep dive**

**Markers are your gate API.** CI gates select tests by marker: G3 runs `-m "smoke and not quarantine"`, G4 runs `-m "not quarantine"`. That's why marker names must be a controlled vocabulary (`--strict-markers`) and documented.

**skip vs xfail semantics:**
| | Runs? | Reported as | Use for |
|---|---|---|---|
| `skip` / `skipif` | No | skipped | Not applicable (wrong env or OS, feature off) |
| `xfail` | Yes | xfailed / xpassed | Known bug, tracked |
| `xfail(strict=True)` | Yes | **fail** if it passes | Known bug: alerts you when it's fixed so you remove the mark |

**Environment selection.** Prefer *one* switch (`--env`) that maps to a config profile over many URL flags. Precedence: CLI flag > env var > `.env` > defaults. Note that `pytest-playwright` (via `pytest-base-url`) already defines `--base-url`, so don't clash with it.

**Examples**

🟢 **Low: register and use markers**
```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "-ra --strict-markers"
testpaths = ["tests"]
pythonpath = ["."]             # keep this from the template: tests import framework/ and python_basics/
markers = [
  "smoke: fast critical-path checks (PR gate)",
  "regression: full coverage (main/nightly)",
  "api: API layer", "ui: browser tests", "db: needs database access", "e2e: crosses API/UI/DB",
  "slow: > 10s", "quarantine(issue): known flaky, excluded from gates",
  "serial: must not run concurrently (P07)", "live: calls a real LLM API (P12)",
]
log_cli = false
log_cli_level = "INFO"
log_format = "%(asctime)s %(levelname)s %(name)s: %(message)s"
```
```python
import pytest

@pytest.mark.smoke
@pytest.mark.api
def test_ping(http, booker_url): ...
```

🔵 **Medium: skipif and a strict xfail**
```python
import sys, pytest

@pytest.mark.skipif(sys.platform == "win32", reason="uses unix socket")
def test_unix_only(): ...

@pytest.mark.xfail(strict=True, reason="BUG-42: sort by price ignores cents for problem_user")
def test_problem_user_price_sort(): ...
```

🟣 **High/Complex: an <code>--env</code> option driving settings, plus auto-skip for DB tests**
```python
# tests/conftest.py: this `settings` fixture replaces the simple one from P03-04
import pytest
from framework.config import Settings

PROFILES = {
    "public": {},                                            # Settings defaults = public demo apps
    "local":  {"toolshop_url": "http://localhost:4200", "toolshop_api_url": "http://localhost:8091",
               "booker_url": "http://localhost:3001"},
    "docker": {"toolshop_url": "http://toolshop-ui:4200", "toolshop_api_url": "http://toolshop-api:8091",
               "booker_url": "http://restful-booker:3001"},   # compose service names (P08)
}

def pytest_addoption(parser):
    parser.addoption("--env", choices=sorted(PROFILES), default="public", help="target environment")

@pytest.fixture(scope="session")
def settings(pytestconfig):
    env = pytestconfig.getoption("--env")
    return Settings(env=env, **PROFILES[env])                 # explicit kwargs beat env vars

def pytest_collection_modifyitems(config, items):
    if config.getoption("--env") == "public":
        skip_db = pytest.mark.skip(reason="no DB access against public demo apps; use --env local/docker")
        for item in items:
            if "db" in item.keywords:
                item.add_marker(skip_db)
```
> Adjust the Docker hostnames to your compose service names in P08.

#### 🎤 Interview Q&A

<details><summary><b>[Z] Skip vs xfail?</b></summary>

`skip` doesn't run the test because it isn't applicable in this context. `xfail` runs it but expects failure because of a known, tracked bug. It reports xfailed or xpassed, and with `strict=True` an unexpected pass fails the run so you remember to remove the mark.
</details>

<details><summary><b>[H] Why enable <code>--strict-markers</code>?</b></summary>

Unregistered markers are usually typos (`@pytest.mark.smok`), which silently drop tests out of `-m smoke` selections and CI gates. Strict mode turns them into errors and forces a documented, controlled marker vocabulary.
</details>

<details><summary><b>[H] How do you run different test subsets in different CI stages?</b></summary>

Markers plus expressions: PR gate `-m "smoke and not quarantine"`, merge/nightly `-m "not quarantine"`, DB jobs `-m db`. Combine with folder paths and `--env`. Document the mapping so developers know what runs where, and fail the job if zero tests are collected.
</details>

<details><summary><b>[H] How do you add a custom command-line option to pytest?</b></summary>

Implement `pytest_addoption(parser)` in the root `conftest.py` (or a plugin), calling `parser.addoption("--env", choices=[...], default=...)`, and read it via `request.config.getoption("--env")` or the `pytestconfig` fixture, typically inside a session fixture that builds settings.
</details>

<details><summary><b>[SH] Why <code>xfail(strict=True)</code> by default (<code>xfail_strict = true</code>)?</b></summary>

Non-strict xfails rot: the bug gets fixed, the test starts passing as XPASS, and nobody notices, so the test stays muted forever. Strict makes XPASS a failure, which forces cleanup and keeps the known-bugs list honest. Pair it with a bug-ID convention in the reason.
</details>

#### 🤖 AI assist
- Ask AI to propose a marker taxonomy for a 2,000-test suite, then trim it. Fewer, well-defined markers win.

---

### P03-06 · Hooks, plugins and coverage

**Level:** 🟣 Super Hero · **Time:** 4h · **App:** all · **Deliverable:** `framework/pytest_plugin.py`, `tests/unit/test_plugin.py`

#### 📋 Task
Build a local pytest plugin and load it from the root `conftest.py` with `pytest_plugins = ["framework.pytest_plugin"]`. The plugin should:
1. **Auto-mark** tests by folder (`tests/api/**` → `api`, `tests/ui/**` → `ui`, `tests/db/**` → `db`).
2. **Enforce policy:** `@pytest.mark.quarantine` must include `issue="..."`, otherwise it's a usage error.
3. **Record the outcome** of each phase on the test item (`item.rep_call`) so fixtures can act on failure (a screenshot-on-failure pattern for P05).
4. **Print a summary:** the 5 slowest tests and pass/fail counts per marker at the end of the run.
5. Test the plugin with **`pytester`**, and add `pytest-cov` on `framework/` with `--cov-fail-under=80`.

**Done when**
- [ ] The plugin tests pass (quarantine without issue → non-zero exit)
- [ ] Framework coverage is ≥80% and reported in the terminal

#### 📘 User guide

**Concepts**
- **Hook:** a named extension point pytest calls during its lifecycle (`pytest_collection_modifyitems`, `pytest_runtest_makereport`, …).
- **Plugin:** a module implementing hooks and/or fixtures. It's loaded from `conftest.py`, `-p name`, `pytest_plugins = [...]`, or installed packages via entry points.
- **Hook wrapper:** wraps other hook implementations. Code before `yield` runs first, and after `yield` you get the result.
- **Report phases:** each test has `setup`, `call` and `teardown` reports, each with `.passed`, `.failed`, `.skipped` and `.duration`.
- **`pytester`:** a built-in fixture that runs pytest *inside* a test on generated files, for testing plugins.

**Deep dive**

**The lifecycle you hook into:**
```text
pytest_addoption → pytest_configure → collection (pytest_generate_tests, pytest_collection_modifyitems)
→ for each test: setup → call → teardown   (pytest_runtest_makereport after each phase)
→ pytest_terminal_summary → pytest_unconfigure
```

**The "screenshot on failure" pattern** combines a hook wrapper with a fixture: the hook stores each phase's report on the item (`item.rep_call`), then a fixture's teardown reads `request.node.rep_call.failed` and captures evidence. You'll reuse this in P05 and P10.

**Policy as code.** Enforcing "quarantine needs an issue" at collection time turns a team agreement into a failing build. That's how Super Heroes scale standards across 50 contributors without nagging in reviews.

**Coverage for framework code, not tests.** Measure `framework/` (shared code) with `--cov=framework`. Coverage of *tests* is meaningless, and coverage of the *app* requires instrumenting the app (a different topic). 80% line coverage of framework code with meaningful asserts (see mutation testing in P03-01) is a healthy bar.

**Examples**

🟢 **Low: auto-mark by folder**
```python
# framework/pytest_plugin.py
import pytest

LAYERS = ("api", "ui", "db", "e2e")

def pytest_collection_modifyitems(config, items):
    for item in items:
        parts = item.path.parts
        for layer in LAYERS:
            if layer in parts:
                item.add_marker(getattr(pytest.mark, layer))
```

🔵 **Medium: store phase reports and use them in a fixture**
```python
# framework/pytest_plugin.py (continued)
@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item, call):
    report = yield                     # let pytest build the report
    setattr(item, f"rep_{report.when}", report)   # rep_setup / rep_call / rep_teardown
    return report

@pytest.fixture
def on_failure_evidence(request, tmp_path):
    yield
    rep = getattr(request.node, "rep_call", None)
    if rep is not None and rep.failed:
        (tmp_path / "failure.txt").write_text(f"{request.node.nodeid}\n{rep.longreprtext}")
```
> Older code uses `@pytest.hookimpl(hookwrapper=True)` with `outcome = yield; report = outcome.get_result()`. Recognise both styles.

🟣 **High/Complex: policy enforcement, a custom summary and a pytester test**
```python
# framework/pytest_plugin.py: final version of the collection hook (replaces the Low example's)
from collections import Counter
import pytest

LAYERS = ("api", "ui", "db", "e2e")

def pytest_collection_modifyitems(config, items):
    offenders = []
    for item in items:
        for layer in LAYERS:                                  # 1. auto-mark by folder
            if layer in item.path.parts:
                item.add_marker(getattr(pytest.mark, layer))
        marker = item.get_closest_marker("quarantine")        # 2. enforce policy
        if marker and not marker.kwargs.get("issue"):
            offenders.append(item.nodeid)
    if offenders:
        raise pytest.UsageError("quarantine marker requires issue='...': " + ", ".join(offenders))

@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    reports = [r for key in ("passed", "failed") for r in terminalreporter.stats.get(key, []) if r.when == "call"]
    slowest = sorted(reports, key=lambda r: r.duration, reverse=True)[:5]
    terminalreporter.section("QE summary")
    for r in slowest:
        terminalreporter.write_line(f"{r.duration:6.2f}s  {r.nodeid}")
    by_marker = Counter(k for r in reports for k in r.keywords if k in ("api", "ui", "db", "e2e"))
    terminalreporter.write_line(f"by layer: {dict(by_marker)}")
```
```python
# tests/unit/test_plugin.py
pytest_plugins = ["pytester"]

def test_quarantine_without_issue_is_rejected(pytester):
    pytester.makepyfile("""
        import pytest
        @pytest.mark.quarantine
        def test_flaky(): pass
    """)
    result = pytester.runpytest("-p", "framework.pytest_plugin")
    assert result.ret != 0
    assert "quarantine marker requires issue" in result.stdout.str() + result.stderr.str()

def test_quarantine_with_issue_runs(pytester):
    pytester.makepyfile("""
        import pytest
        @pytest.mark.quarantine(issue="QE-101")
        def test_flaky(): pass
    """)
    pytester.runpytest("-p", "framework.pytest_plugin").assert_outcomes(passed=1)
```
```bash
uv add --dev pytest-cov
uv run pytest tests/unit --cov=framework --cov-report=term-missing --cov-fail-under=80
```
> If `pytester` runs complain about unknown markers, register them in the generated test dir with `pytester.makeini(...)`. Debugging this is part of the exercise.

#### 🎤 Interview Q&A

<details><summary><b>[H] What is a pytest hook? Name three you've used.</b></summary>

A predefined lifecycle function pytest calls, which plugins and conftests implement to customise behaviour. Examples: `pytest_addoption` (CLI flags), `pytest_collection_modifyitems` (auto-mark, reorder, skip), `pytest_runtest_makereport` (capture results for screenshots or reporting), `pytest_generate_tests` (dynamic parametrisation), `pytest_terminal_summary` (custom summary).
</details>

<details><summary><b>[H] How do you take a screenshot only when a UI test fails?</b></summary>

A hook wrapper on `pytest_runtest_makereport` stores the call-phase report on the item. A fixture wrapping the page yields, then in teardown checks `request.node.rep_call.failed` and saves a screenshot/trace, attaching it to the report. (pytest-playwright also provides `--screenshot only-on-failure` and `--tracing retain-on-failure`.)
</details>

<details><summary><b>[SH] How would you build and distribute a pytest plugin for multiple teams?</b></summary>

Put hooks and fixtures in a package module, expose it through a `pytest11` entry point in `pyproject.toml` so it auto-loads when installed, add CLI options for opt-in behaviour, test it with `pytester` across pytest versions, version it semantically, and document the hooks and fixtures it adds. Keep it free of app-specific logic.
</details>

<details><summary><b>[SH] What are the three report phases and why do they matter?</b></summary>

`setup` (fixtures), `call` (the test body) and `teardown`. A failure in setup is an *error*, not a *failure*. It usually means environment or data problems, not a product bug, which is critical for triage. Reporting and screenshot logic must check the right phase (usually `call`), and teardown errors (cleanup failed) should be visible but separated.
</details>

<details><summary><b>[H] What does code coverage tell you about a test framework, and what doesn't it tell you?</b></summary>

It shows which lines ran during tests, so it finds untested framework code. It doesn't show whether behaviour was *verified* (weak asserts still give 100%), nor anything about product coverage. Combine it with mutation testing and requirement/risk coverage mapping.
</details>

#### 🤖 AI assist
- Ask AI to list pytest hooks relevant to reporting and explain when each fires, then verify with a tiny plugin that prints in each.

---

## 🏁 Phase checkpoint: P03

**Self-test (30 min, no AI):** write from memory a conftest with a session HTTP fixture, a factory fixture with cleanup, a `--env` option, and one parametrized test with ids.

**AI mock interviewer prompt**
```text
Interview me on pytest for an SDET role. Cover fixtures & scopes, conftest,
parametrize, markers, skip vs xfail, hooks and plugins. Ask 8 questions one at a
time, increasing difficulty, and include one "debug this conftest" scenario.
Score each answer 1-5 with what a senior answer would add.
```
Record your results in `interview-notes/P03.md`.
