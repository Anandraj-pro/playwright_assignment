# P07: Parallel Execution

> **Goal:** make the suite fast *and* trustworthy in parallel: measure, isolate, choose distribution modes, share expensive setup safely, and shard across CI machines.
> **Apps:** all (prefer **self-hosted** Toolshop and Restful-Booker for heavy runs). **Prerequisites:** P03–P06. **Time:** ~13 h.

| ID | Task | Level | Time |
|---|---|---|---|
| P07-01 | Baseline and first parallel run | 🟢 | 2h |
| P07-02 | Make tests parallel-safe | 🔵 | 4h |
| P07-03 | Distribution modes and shared session resources | 🔵 | 3h |
| P07-04 | Sharding across machines and a parallel strategy | 🟣 | 4h |

> Be kind to public demo apps: use `-n 2` at most against hosted URLs. Use `--env local` (self-hosted, P08) for anything bigger.

---

### P07-01 · Baseline and first parallel run

**Level:** 🟢 Zero · **Time:** 2h · **App:** all · **Deliverable:** `docs/parallel-baseline.md`

#### 📋 Task
1. Run the whole suite serially with `--durations=15` and record the wall-clock time and the 15 slowest tests.
2. `uv add --dev pytest-xdist`, then run with `-n 2`, `-n 4` and `-n auto`. Record the times and **every failure that didn't happen serially**.
3. Compute **speedup** (serial time ÷ parallel time) and **efficiency** (speedup ÷ workers) for each run.
4. List the failures you'll fix in P07-02 and guess the cause of each.

**Done when**
- [ ] `docs/parallel-baseline.md` has a timing table and a list of parallel-only failures

#### 📘 User guide

**Concepts**
- **Concurrency vs parallelism:** interleaving work vs literally doing work at the same time.
- **pytest-xdist:** runs tests in multiple **worker processes** (`gw0`, `gw1`, …) coordinated by a controller.
- **`-n auto`:** one worker per CPU core (`-n logical` uses logical cores). `--maxprocesses` caps it.
- **Speedup and efficiency:** 60 s → 20 s with 4 workers = 3× speedup, 75% efficiency.
- **Amdahl's law:** the serial part (setup, the slowest single test) limits the maximum speedup.

**Deep dive**

**How xdist works:** the controller starts N workers. **Each worker collects the full test list**, and the lists must be identical. The controller then hands out test IDs. Consequences:
1. **Session fixtures run once per worker**, not once per run (4 workers means 4 logins).
2. **Collection must be deterministic.** Random data generated at *collection* time (e.g. `parametrize` with `uuid4()`) makes workers collect different tests, and xdist aborts with "Different tests were collected between gw0 and gw1". Generate random data inside fixtures or tests instead.
3. Processes don't share memory, so globals aren't shared. But **files, databases, user accounts and servers are.**

**I/O-bound suites** (API and UI tests mostly wait on the network and browser) can benefit from *more* workers than cores, until the machine or **the system under test** saturates. That's why you measure `-n 2/4/8` instead of assuming `auto` is optimal.

**Amdahl's law in practice:** if one test takes 90 s, no worker count gets the suite below 90 s. Split or speed up the long tail (hybrid tests, API setup) before adding workers.

**Examples**

🟢 **Low: measure**
```bash
uv run pytest -q --durations=15 -p no:randomly             # serial baseline
uv run pytest -q -n 2
uv run pytest -q -n 4
uv run pytest -q -n auto
```

🔵 **Medium: a timing matrix script**
```python
# scripts/parallel_matrix.py
import subprocess, time

def run(workers: str) -> tuple[float, int]:
    start = time.perf_counter()
    rc = subprocess.run(["uv", "run", "pytest", "-q", "-n", workers, "-m", "not db"],
                        capture_output=True).returncode
    return time.perf_counter() - start, rc

serial, _ = run("0")
print(f"{'workers':>8} {'seconds':>8} {'speedup':>8} {'eff':>6} rc")
for w in ["0", "2", "4", "8"]:
    t, rc = (serial, 0) if w == "0" else run(w)
    n = max(int(w), 1)
    print(f"{w:>8} {t:8.1f} {serial / t:8.2f} {serial / t / n:6.0%} {rc}")
```

🟣 **High/Complex: the non-deterministic collection trap, and fixing it**
```python
import uuid
import pytest

# ❌ Breaks xdist: every worker generates different IDs at collection time
@pytest.mark.parametrize("email", [f"user-{uuid.uuid4().hex[:6]}@example.com" for _ in range(3)])
def test_register_bad(email): ...

# ✅ Deterministic IDs at collection, uniqueness created at run time
@pytest.mark.parametrize("variant", ["plain", "plus-address", "subdomain"])
def test_register_good(variant, unique_email):
    email = {"plain": unique_email, "plus-address": unique_email.replace("@", "+tag@"),
             "subdomain": unique_email.replace("@example.com", "@mail.example.com")}[variant]
    assert "@" in email
```
```python
# tests/conftest.py
import uuid
import pytest

@pytest.fixture
def unique_email(worker_id: str) -> str:           # worker_id: provided by xdist ("master" when serial)
    return f"qe-{worker_id}-{uuid.uuid4().hex[:8]}@example.com"
```

#### 🎤 Interview Q&A

<details><summary><b>[Z] What does <code>pytest -n auto</code> do?</b></summary>

With pytest-xdist installed, it starts one worker process per available CPU core and distributes tests among them. It needs tests to be independent. Session fixtures then run once per worker.
</details>

<details><summary><b>[Z] Tests pass serially but fail in parallel. What are typical causes?</b></summary>

Shared state: the same test data (fixed usernames or IDs), the same user account used concurrently (server-side session or cart state), shared files or output paths, order dependencies (test B relies on test A's data), global app settings changed by one test, and rate limits or capacity on the system under test.
</details>

<details><summary><b>[H] How does pytest-xdist work internally?</b></summary>

A controller process spawns workers. Each worker collects the full test suite, and the controller verifies the collections match, then schedules test IDs to workers according to the distribution mode (load, loadscope, loadfile, loadgroup, worksteal). Results stream back to the controller for reporting. Each worker is a separate Python process with its own fixtures and imports.
</details>

<details><summary><b>[SH] Why can't you just keep adding workers to get faster?</b></summary>

Amdahl's law: the serial portion (per-worker session setup, the longest test, collection) caps the speedup. Beyond that, workers compete for CPU and memory (browsers are heavy), and the system under test, database or rate limits become the bottleneck. Measure speedup and efficiency at several worker counts and pick the knee of the curve.
</details>

<details><summary><b>[SH] What does "Different tests were collected between gw0 and gw1" mean?</b></summary>

Workers collected different test lists, usually because collection is non-deterministic: random values in parametrize IDs, parameters depending on time or unordered sets, or environment-dependent collection. Fix it by making collection deterministic and generating randomness at run time in fixtures.
</details>

<details><summary><b>[Z] Why do fast test suites matter to a development team?</b></summary>

Feedback time shapes behaviour. A suite that answers in minutes runs on every PR and catches problems while the change is fresh; a suite that takes an hour gets run less often, batched, or skipped, so bugs are found later and cost more to fix. Speed also reduces waiting and context switching for the whole team. Parallel execution is one of the cheapest ways to get it, provided the tests are independent.
</details>

#### 🤖 AI assist
- Paste your baseline table and ask AI where the bottleneck probably is. Then check it against your `--durations` output.

---

### P07-02 · Make tests parallel-safe

**Level:** 🔵 Hero · **Time:** 4h · **App:** Restful-Booker, SauceDemo, Toolshop · **Deliverable:** refactored `tests/`, `framework/data/accounts.py`

#### 📋 Task
Fix every parallel-only failure from P07-01. Then **plant and fix** these classic problems on purpose, so you can recognise them in interviews:
1. **Global state:** test A stores a booking ID in a module global and test B reads it.
2. **Fixed data:** two tests register the same email.
3. **Shared file:** two tests write `report.json` to the same path.
4. **Shared account:** two Toolshop UI tests add items to the cart of the *same* customer at the same time.
5. Add `pytest-randomly` and run 3 random seeds with `-n 4`, green each time.

**Done when**
- [ ] `uv run pytest -n 4 -p randomly` is green 3 times in a row with different seeds
- [ ] `docs/parallel-safety.md` lists each problem type and its fix

#### 📘 User guide

**Concepts**
- **`worker_id` fixture:** `"gw0"`, `"gw1"`, … (or `"master"` when not parallel). Also available as the `PYTEST_XDIST_WORKER` env var.
- **`testrun_uid` fixture:** a unique ID for the whole run, shared by all workers.
- **pytest-randomly:** shuffles test order (and reseeds `random`/Faker) every run and prints the seed. `-p randomly --randomly-seed=1234` reproduces an order. `-p no:randomly` disables it.
- **Account pool:** a distinct user per worker for stateful flows.

**Deep dive**

**Where shared state hides:**
| Layer | Example | Fix |
|---|---|---|
| In-process | Module globals, class attributes, cached singletons | Fixtures; no cross-test globals |
| Filesystem | Fixed output paths | `tmp_path`, worker-specific names |
| Test data | Same username, email or SKU | Unique suffix: worker ID + uuid |
| Accounts | One user's cart, session limits, "last login" | One account per worker, or register per test |
| App config | A test toggles a global feature flag | Serial lane or `xdist_group` (P07-03) |
| External limits | Rate limits on shared APIs | Fewer workers, self-hosted SUT |

**Order dependency is the silent sibling of parallel bugs.** A test that only passes *after* another is broken even serially: it fails with `-k`, `--lf` or random order. `pytest-randomly` flushes these out. When a random order fails, rerun with the printed seed to reproduce it deterministically, then bisect by removing tests.

**Server-side state is the sneakiest.** Different browser contexts isolate *cookies*, but not the *server's* view of "customer@…'s cart". Two workers using the same account corrupt each other's carts. Give each worker its own account.

**Examples**

🟢 **Low: worker-aware unique data**
```python
import uuid
import pytest

@pytest.fixture
def unique_name(worker_id, request) -> str:
    return f"qe-{worker_id}-{request.node.name[:20]}-{uuid.uuid4().hex[:6]}"

# tests/api/toolshop/test_brands_parallel.py  (admin_token comes from P04-07's conftest)
def test_create_brand(unique_name, http, settings, admin_token):
    r = http.post(f"{settings.toolshop_api_url}/brands", json={"name": unique_name, "slug": unique_name},
                  headers={"Authorization": f"Bearer {admin_token}"}, timeout=10)
    assert r.status_code in (200, 201), r.text
    assert r.json()["name"] == unique_name
```

🔵 **Medium: an order-dependent pair, broken and fixed**
```python
# ❌ BROKEN: test_b depends on test_a having run first (and in the same process)
CREATED = {}

def test_a_create(booker):
    CREATED["id"] = booker.create_booking(build_booking()).bookingid

def test_b_update(booker):
    booker.patch_booking(CREATED["id"], {"firstname": "X"})      # KeyError under -k, random order or xdist

# ✅ FIXED: each test owns its setup through a fixture
@pytest.fixture
def booking_id(booker):
    booking = booker.create_booking(build_booking())
    yield booking.bookingid
    booker.delete_booking(booking.bookingid)

def test_update(booker, booking_id):
    assert booker.patch_booking(booking_id, {"firstname": "X"}).firstname == "X"
```

🟣 **High/Complex: an account pool per worker, with fallback registration**
```python
# framework/data/accounts.py
from dataclasses import dataclass

@dataclass(frozen=True)
class Account:
    email: str
    password: str

SEEDED = [                                   # Toolshop's seeded customers (DEMO_APPS.md)
    Account("customer@practicesoftwaretesting.com", "welcome01"),
    Account("customer2@practicesoftwaretesting.com", "welcome01"),
    Account("customer3@practicesoftwaretesting.com", "pass123"),
]

def worker_index(worker_id: str) -> int:
    return 0 if worker_id == "master" else int(worker_id.removeprefix("gw"))
```
```python
# tests/ui/toolshop/conftest.py
import pytest
from framework.data.accounts import SEEDED, Account, worker_index
from framework.data.factories import user_payload

@pytest.fixture(scope="session")
def customer_account(worker_id, http, settings) -> Account:
    idx = worker_index(worker_id)
    if idx < len(SEEDED):
        return SEEDED[idx]                               # gw0..gw2 use seeded users
    payload = user_payload()                             # gw3+ get a freshly registered user
    r = http.post(f"{settings.toolshop_api_url}/users/register", json=payload, timeout=10)
    r.raise_for_status()
    return Account(payload["email"], payload["password"])
```
Update `customer_state` (P05-06) to log in with `customer_account`, so each worker has its own storage state **and** its own server-side cart.
```bash
uv run pytest tests/ui/toolshop -n 4 -p randomly          # note the printed seed
uv run pytest tests/ui/toolshop -n 4 -p randomly --randomly-seed=<seed>   # reproduce a failure
```

#### 🎤 Interview Q&A

<details><summary><b>[H] What makes a test not parallel-safe? How do you fix it?</b></summary>

Any shared, mutable resource: globals, fixed data values, shared files, shared user accounts or server-side state, global app configuration, or external limits. Fix with fixtures that create per-test data (unique IDs including the worker ID), `tmp_path` for files, one account per worker, isolating global-config tests in a serial lane, and self-hosted dependencies to avoid rate limits.
</details>

<details><summary><b>[H] How do you find hidden order dependencies?</b></summary>

Run in random order (`pytest-randomly`) across several seeds, and run tests individually (`-k`) and in reverse. When a seed fails, reproduce it with `--randomly-seed`, then narrow down by bisecting the preceding tests (`pytest-randomly` plus `--lf`, or a tool that bisects order dependencies). Fix by moving setup into fixtures.
</details>

<details><summary><b>[SH] Two UI tests use different browser contexts but still interfere. How?</b></summary>

Contexts isolate client-side state (cookies, storage), but both tests log in as the same user, so the server-side state is shared: cart contents, session limits (the second login invalidates the first), preferences, rate limits. Fix with one account per worker or per test, or reset server-side state for that account in setup.
</details>

<details><summary><b>[H] A random-order run failed. How do you reproduce it?</b></summary>

pytest-randomly prints the seed in the header. Rerun with `-p randomly --randomly-seed=<seed>` (and the same `-n`, or `-n 0` to simplify) to get the same order, then shrink the set of tests until the minimal failing pair is found.
</details>

<details><summary><b>[H] What does "idempotent test" mean?</b></summary>

A test that can run any number of times, in any order, alongside anything else, and always produce the same result. It creates what it needs, doesn't depend on leftovers, cleans up, and tolerates leftovers from earlier crashed runs (unique names instead of fixed ones).
</details>

<details><summary><b>[Z] What does it mean for a test to be "independent", and why does parallel execution need it?</b></summary>

An independent test sets up everything it needs, doesn't rely on another test having run first, and doesn't leave behind anything that affects others. Tests that share state (a user, a cart, a database row, a global variable) pass in one order and fail in another, and parallel runs change the order and timing constantly. Independence is what makes results trustworthy when tests run at the same time.
</details>

#### 🤖 AI assist
- Paste a failing parallel test and its fixtures, and ask AI to *list every shared resource it touches*. Verify each one.

---

### P07-03 · Distribution modes and shared session resources

**Level:** 🔵 Hero · **Time:** 3h · **App:** all · **Deliverable:** `tests/conftest.py` (lock-based session setup), `Makefile` lanes, `docs/parallel-safety.md` (update)

#### 📋 Task
1. Time the suite with each distribution mode: `--dist load` (default), `loadscope`, `loadfile`, `loadgroup`, `worksteal`. Explain the differences you see.
2. Group tests that must share a worker (e.g. admin tests that change global settings) with `@pytest.mark.xdist_group("admin-settings")` and `--dist loadgroup`.
3. Implement **once-per-run** expensive setup shared across workers using the **FileLock pattern** (e.g. seeding reference data or fetching a large dataset).
4. Create **two lanes**: `make test-serial` (`-m serial -n 0`) for tests that can't run concurrently, and `make test-parallel` (`-m "not serial" -n auto`).
5. Add a controller-only `pytest_sessionfinish` hook that prints a run summary (it runs once, not per worker).

**Done when**
- [ ] The once-per-run setup provably executes once with `-n 4` (a log line or counter file)
- [ ] The Makefile lanes both work and are documented

#### 📘 User guide

**Concepts**
| Mode | How tests are handed out | Good for |
|---|---|---|
| `load` | Individual tests to whichever worker is free | Default; uniform tests |
| `loadscope` | Whole module or class to one worker | Expensive module/class fixtures |
| `loadfile` | Whole file to one worker | File-level setup, locality |
| `loadgroup` | `xdist_group` tests to the same worker, others load-balanced | "Must not run concurrently with each other" |
| `worksteal` | Idle workers steal queued tests from busy ones | Very uneven test durations |

- **FileLock pattern:** workers race for a lock file. The first creates a shared resource and writes it to a file, and the others read it.
- **Controller vs worker:** worker processes have `config.workerinput`, and the controller doesn't.

**Deep dive**

**Session scope ≠ run scope under xdist.** Your "session" fixture runs once *per worker*. For truly once-per-run work, coordinate via the filesystem: `tmp_path_factory.getbasetemp().parent` is shared by all workers in a run, and a `FileLock` serialises creation. This pattern comes straight from the xdist docs and is worth memorising.

**Cleanup for once-per-run resources** is the tricky part. No single worker knows it's last. Do cleanup in `pytest_sessionfinish` on the **controller** (`not hasattr(session.config, "workerinput")`), or make the resource disposable (unique per run, swept later).

**Serial lanes beat clever locking** for tests that mutate global state (site settings, feature flags, time travel). Run them separately and first (or last), and keep that lane small.

**Examples**

🟢 **Low: group tests onto one worker**
```python
import pytest

@pytest.mark.xdist_group("admin-settings")
def test_enable_feature_x(admin_api): ...

@pytest.mark.xdist_group("admin-settings")
def test_feature_x_visible(admin_api): ...
```
```bash
uv run pytest -n 4 --dist loadgroup
uv run pytest -n 4 --dist worksteal --durations=10
```

🔵 **Medium: once-per-run setup across workers (FileLock)**
```python
# tests/conftest.py      (uv add --dev filelock)
import json
import pytest
from filelock import FileLock

def build_reference_data(http, settings) -> dict:
    """Expensive: e.g. walk the whole product catalogue once."""
    from framework.api.pagination import iter_products
    return {"product_ids": [p["id"] for p in iter_products(http, settings.toolshop_api_url)]}

@pytest.fixture(scope="session")
def reference_data(tmp_path_factory, worker_id, http, settings) -> dict:
    if worker_id == "master":                       # not running under xdist
        return build_reference_data(http, settings)
    shared_dir = tmp_path_factory.getbasetemp().parent
    data_file = shared_dir / "reference_data.json"
    with FileLock(str(data_file) + ".lock"):
        if data_file.is_file():
            return json.loads(data_file.read_text())
        data = build_reference_data(http, settings)
        data_file.write_text(json.dumps(data))
        return data
```

🟣 **High/Complex: serial and parallel lanes plus a controller-only summary**
```makefile
# the `serial` marker is registered in pyproject.toml (P03-05)
test-serial:   ; uv run pytest -m "serial" -n 0 --junitxml=test-results/serial.xml
test-parallel: ; uv run pytest -m "not serial" -n auto --dist loadgroup --junitxml=test-results/parallel.xml
test-all: test-serial test-parallel
```
```python
# framework/pytest_plugin.py (add)
import time

def pytest_sessionstart(session):
    session.config._qe_start = time.time()

def pytest_sessionfinish(session, exitstatus):
    if hasattr(session.config, "workerinput"):
        return                                                    # workers: do nothing
    elapsed = time.time() - session.config._qe_start
    workers = session.config.getoption("numprocesses", default=None) or 0
    session.config.pluginmanager.get_plugin("terminalreporter").write_line(
        f"[qe] run finished in {elapsed:.1f}s with {workers or 'no'} xdist workers, exit={exitstatus}")
    # place for once-per-run cleanup: delete resources tagged with this run's testrun_uid
```

#### 🎤 Interview Q&A

<details><summary><b>[H] Explain xdist distribution modes. When would you use loadgroup?</b></summary>

`load` sends individual tests to free workers. `loadscope` and `loadfile` keep a module/class or file on one worker, which is good for expensive module fixtures. `worksteal` rebalances uneven durations. `loadgroup` pins tests sharing an `xdist_group` name to the same worker, so they never run concurrently with each other while everything else stays parallel. Use it for tests that mutate the same global setting or resource.
</details>

<details><summary><b>[H] Where do session-scoped fixtures run under xdist?</b></summary>

Once per worker process, because each worker is a separate pytest session. With 8 workers, a session login happens 8 times. That's usually fine (and even desirable for per-worker accounts), but truly once-per-run work needs a FileLock or controller coordination.
</details>

<details><summary><b>[SH] How do you run expensive setup exactly once across all workers?</b></summary>

The FileLock pattern: use the shared base temp directory (`tmp_path_factory.getbasetemp().parent`), acquire a lock, have the first worker build the resource and write it (or its ID) to a file, and have the others read it. Handle the non-xdist case (`worker_id == "master"`). Do cleanup in the controller's `pytest_sessionfinish`, or make the resource run-unique and disposable.
</details>

<details><summary><b>[H] How do you handle tests that can't run in parallel?</b></summary>

First try to remove the reason (per-test data or accounts). If it's inherent (global settings, clock manipulation, destructive admin actions), mark them `serial` and run them in a separate `-n 0` lane, or group them with `xdist_group`. Keep that set small and visible, since it's a performance debt list.
</details>

<details><summary><b>[SH] How do you perform cleanup once after all workers finish?</b></summary>

Implement `pytest_sessionfinish` and run the logic only on the controller (`not hasattr(config, "workerinput")`). Identify what to clean by tagging resources with the run's `testrun_uid`. As a safety net, schedule a periodic sweeper for tagged leftovers from crashed runs.
</details>

#### 🤖 AI assist
- Ask AI to explain the xdist FileLock recipe line by line, then check the explanation against the pytest-xdist documentation.

---

### P07-04 · Sharding across machines and a parallel strategy

**Level:** 🟣 Super Hero · **Time:** 4h · **App:** self-hosted stack · **Deliverable:** `.test_durations`, `scripts/shard_model.py`, `docs/parallel-strategy.md`

#### 📋 Task
1. `uv add --dev pytest-split`, record durations with `--store-durations`, and commit `.test_durations`.
2. Run 3 shards locally (`--splits 3 --group 1..3`), each with `-n 2`, writing separate JUnit files, then **merge** them.
3. Build a simple **cost model** (`scripts/shard_model.py`): given the total test time, per-shard fixed overhead (checkout, install, browsers, containers), workers per shard and efficiency, predict wall-clock time and CI minutes for 1–8 shards.
4. Write `docs/parallel-strategy.md`: which suites run where (PR vs nightly), worker and shard counts with evidence, SUT capacity limits, when to rebalance durations, and a note on **test impact analysis** (running only tests affected by a change).

**Done when**
- [ ] The merged JUnit report contains every test exactly once
- [ ] The strategy doc recommends shard and worker counts backed by measurements and the model

#### 📘 User guide

**Concepts**
- **Vertical scaling** (more workers on one machine) vs **horizontal** (**shards** on many machines).
- **Duration-based splitting:** `pytest-split` uses recorded durations to balance shards (a bin-packing heuristic).
- **Fixed overhead per shard:** each CI machine pays setup costs before running any test.
- **Test impact analysis (TIA):** select tests based on changed code (e.g. `pytest-testmon`, or path-to-suite mapping).

**Deep dive**

**Wall-clock is the slowest shard plus its overhead.** Balanced shards matter more than the number of shards. With stale durations, one shard gets all the slow tests and your 3× plan becomes 1.5×. Refresh durations regularly (nightly job artifact).

**The cost model:**
```text
wall(shards) ≈ overhead + total_test_time / (shards × workers × efficiency)
ci_minutes(shards) ≈ shards × wall(shards)
```
Doubling shards halves the test portion but *adds* overhead minutes, so there's a point where more shards cost money without saving time. Show this trade-off in interviews.

**Where parallelism isn't the answer:** a slow suite is often a **pyramid problem** (too many UI tests). Moving checks to the API layer, using hybrid setup and deleting redundant tests beats adding hardware. Parallelism multiplies whatever efficiency you have.

**Test impact analysis** runs only tests related to the change on PRs (with the full suite nightly as a safety net). It's the biggest lever for PR feedback time in large repos.

**Examples**

🟢 **Low: record durations and run a shard**
```bash
uv run pytest --store-durations -m "not serial"            # writes .test_durations
uv run pytest --splits 3 --group 1 -n 2 --junitxml=test-results/shard-1.xml
uv run pytest --splits 3 --group 2 -n 2 --junitxml=test-results/shard-2.xml
uv run pytest --splits 3 --group 3 -n 2 --junitxml=test-results/shard-3.xml
```

🔵 **Medium: merge shard reports and verify completeness**
```bash
uv add --dev junitparser
uv run junitparser merge test-results/shard-*.xml test-results/merged.xml
```
```python
# scripts/check_merged.py: every collected test appears exactly once
import subprocess, collections
from junitparser import JUnitXml

collected = subprocess.run(["uv", "run", "pytest", "--co", "-q", "-m", "not serial"],
                           capture_output=True, text=True).stdout.splitlines()
collected = {line for line in collected if "::" in line}
seen = collections.Counter(f"{case.classname}::{case.name}" for suite in JUnitXml.fromfile("test-results/merged.xml")
                           for case in suite)
dupes = [k for k, n in seen.items() if n > 1]
print(f"collected={len(collected)} reported={sum(seen.values())} duplicates={len(dupes)}")
```
> JUnit `classname` formatting differs from pytest node IDs. Normalising them is part of the exercise.

🟣 **High/Complex: a shard cost model**
```python
# scripts/shard_model.py
import json
from pathlib import Path

durations = json.loads(Path(".test_durations").read_text())
total = sum(durations.values())
longest = max(durations.values())
OVERHEAD_S = 150          # checkout + uv sync + browsers + containers (measure yours in CI!)
WORKERS, EFFICIENCY = 2, 0.7

print(f"total test time {total/60:.1f} min, longest test {longest:.0f}s")
print(f"{'shards':>6} {'wall min':>9} {'CI min':>7}")
for shards in range(1, 9):
    test_part = max(total / (shards * WORKERS * EFFICIENCY), longest)   # Amdahl floor
    wall = (OVERHEAD_S + test_part) / 60
    print(f"{shards:>6} {wall:9.1f} {shards * wall:7.1f}")
```
Pick the shard count at the "knee": the point where wall time stops dropping meaningfully while CI minutes keep rising.

#### 🎤 Interview Q&A

<details><summary><b>[SH] Your regression suite takes 60 minutes. How do you get PR feedback under 10?</b></summary>

1) Measure: durations, slowest tests, failure and flake rates. 2) Fix the shape: move UI checks to the API, use hybrid setup and auth-state reuse, delete redundant tests. 3) Parallelise: xdist within a machine, sharded across CI jobs by recorded durations. 4) Select: a PR gate of smoke plus test impact analysis, with the full regression on merge and nightly. 5) Remove waste: caching (dependencies, browsers, images), fast container start-up. 6) Keep it healthy: quarantine flaky tests and track duration budgets per suite.
</details>

<details><summary><b>[H] Sharding vs xdist workers: what's the difference and when do you use each?</b></summary>

Workers parallelise within one machine and are limited by its CPU and memory. Shards split the suite across multiple CI machines (horizontal) and add per-machine setup overhead. Use workers first (cheap), then shards when one machine saturates. Combine them (e.g. 4 shards × 2 workers) and balance shards by duration.
</details>

<details><summary><b>[H] How does pytest-split balance shards?</b></summary>

It reads recorded per-test durations (`.test_durations`) and assigns tests so each group's total duration is roughly equal (a greedy bin-packing algorithm), falling back to average durations for new tests. Stale durations cause imbalance, so refresh them regularly.
</details>

<details><summary><b>[H] How do you combine results from multiple shards?</b></summary>

Each shard writes its own JUnit XML (and traces or other artifacts) with a unique name. A final CI job downloads all the artifacts, merges the XML (e.g. junitparser), publishes one report, and verifies completeness (every collected test reported exactly once, and no shard silently ran zero tests).
</details>

<details><summary><b>[SH] What is test impact analysis, and what are its risks?</b></summary>

Selecting tests to run based on which code changed, using coverage mapping (e.g. testmon) or ownership and path rules. It cuts PR time dramatically. Risks: missed dependencies (config, data, cross-service changes) and stale mappings. Mitigate with a full suite on merge or nightly, always-run smoke tests, and conservative rules for shared or core files.
</details>

<details><summary><b>[SH] How do you decide the number of shards?</b></summary>

With data: total test time, the longest test (the floor), per-shard overhead, workers per shard and parallel efficiency. Model wall-clock and CI minutes per shard count, pick the knee, respect SUT capacity (N shards × M workers hitting one environment), and revisit it as the suite grows.
</details>

<details><summary><b>[Z] In one sentence each: what are parallel workers and what are shards?</b></summary>

Workers are several processes on *one* machine running tests at the same time (pytest-xdist's `-n 4`). Shards split the suite across *several* machines or CI jobs, each running its own slice (and each shard can still use several workers).
</details>

#### 🤖 AI assist
- Ask AI to critique your cost model's assumptions (overhead, efficiency, Amdahl floor), then measure real overhead in P09 and update the model.

---

## 🏁 Phase checkpoint: P07

**Explain in 3 minutes (record yourself):** "How I made a 25-minute suite run in 6 minutes without increasing flakiness", using your own numbers.

**AI mock interviewer prompt**
```text
Interview me on parallel test execution (pytest-xdist, sharding, test isolation).
Ask 6 questions one at a time, then give me a scenario: "after enabling -n 8,
3% of tests fail randomly". Evaluate my diagnosis and plan. Score each 1-5 with
what a staff-level answer would add.
```
Record your results in `interview-notes/P07.md`.
