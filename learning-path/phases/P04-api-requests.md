# P04: API Testing with requests

> **Goal:** test REST APIs like a professional: HTTP fluency, CRUD and negative tests, a clean client layer, **running the apps locally with Docker**, schema validation and contract testing.
> **Apps:** Restful-Booker, Toolshop API, Swagger Petstore, The Internet (Docker image). **Prerequisites:** P03. **Time:** ~28 h.

| ID | Task | Level | Time |
|---|---|---|---|
| P04-01 | HTTP fundamentals and manual API exploration | 🟢 | 2h |
| P04-02 | First API tests with requests | 🟢 | 3h |
| P04-03 | Auth, CRUD and negative testing | 🔵 | 4h |
| P04-04 | API client layer and schema validation | 🔵 | 4h |
| P04-05 | Docker as a user: images, containers, ports and volumes | 🟢 | 3h |
| P04-06 | Run the demo stack locally with Compose | 🟢 | 3h |
| P04-07 | Toolshop API: bearer auth, pagination, filters, data factories | 🔵 | 4h |
| P04-08 | Contract testing and API resilience | 🟣 | 5h |

---

### P04-01 · HTTP fundamentals and manual API exploration

**Level:** 🟢 Zero · **Time:** 2h · **App:** Restful-Booker · **Deliverable:** `docs/api-exploration.md`

#### 📋 Task
1. Using **curl** and **Bruno or Postman**, call every Restful-Booker endpoint: `/ping`, `/auth`, `GET /booking`, `GET /booking/{id}`, `POST /booking`, `PUT`, `PATCH`, `DELETE`, and the filters `?firstname=` / `?checkin=`.
2. For each call, record the method, URL, request headers and body, **status code**, response headers (`Content-Type`), a body sample and anything surprising.
3. Write **15 test ideas** in a table, at least 7 of them negative (missing auth, bad dates, wrong types, non-existent IDs…).
4. Save your Bruno/Postman collection in `api-collections/`.

**Done when**
- [ ] Every endpoint has been called successfully at least once
- [ ] You've noted which status codes differ from REST conventions (there are some; that's a discussion point)

#### 📘 User guide

**Concepts**
- **Request:** method + URL (scheme, host, **path params** like `/booking/5`, **query params** like `?lastname=Smith`) + headers + optional body.
- **Response:** status code + headers + body.
- **Headers you'll use constantly:** `Content-Type` (what I'm sending), `Accept` (what I want back), `Authorization`, `Cookie`.
- **REST:** resources are nouns (`/booking`), methods are verbs, and the server is **stateless** (each request carries all context, e.g. the token).

**Deep dive**

**Method semantics** (interviewers probe these):
| Method | Purpose | Safe? | Idempotent? | Typical success |
|---|---|---|---|---|
| GET | Read | ✅ | ✅ | 200 |
| POST | Create / action | ❌ | ❌ | 201 (or 200) |
| PUT | Replace entire resource | ❌ | ✅ | 200 / 204 |
| PATCH | Partial update | ❌ | Not guaranteed | 200 / 204 |
| DELETE | Remove | ❌ | ✅ | 204 / 200 |

*Safe* = no server state change. *Idempotent* = repeating it has the same effect as doing it once. Idempotency decides what's safe to **retry** (P04-04).

**Status code families:** `2xx` success, `3xx` redirect, `4xx` **client** error (your request is wrong), `5xx` **server** error (their bug or outage).
| Code | Meaning | Test angle |
|---|---|---|
| 400 | Malformed request | Broken JSON, wrong types |
| 401 | Not authenticated ("who are you?") | Missing or invalid token |
| 403 | Authenticated but not allowed ("I know you, but no") | Customer calling an admin endpoint |
| 404 | Not found | Deleted or non-existent ID |
| 409 | Conflict | Duplicate email, version conflict |
| 422 | Semantically invalid | Checkout before checkin |
| 429 | Rate limited | Too many requests |
| 500 | Server crashed | **Always a bug when caused by client input** |

**Explore before you automate.** Manual exploration builds the mental model your automation encodes. Use heuristics: **CRUD** round trips, **boundaries** (empty, long, unicode, negative), **auth** (none, wrong, expired, wrong role), **formats** (missing fields, extra fields, wrong types), **state** (delete then read, update a deleted resource).

**Examples**

🟢 **Low: read-only calls with curl**
```bash
curl -i https://restful-booker.herokuapp.com/ping              # -i shows status + headers
curl -s "https://restful-booker.herokuapp.com/booking?firstname=Sally" | head -c 300
curl -s -H "Accept: application/json" https://restful-booker.herokuapp.com/booking/1
```

🔵 **Medium: create, auth, update, with timing**
```bash
BASE=https://restful-booker.herokuapp.com
TOKEN=$(curl -s -X POST $BASE/auth -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"password123"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["token"])')

ID=$(curl -s -X POST $BASE/booking -H 'Content-Type: application/json' -H 'Accept: application/json' \
  -d '{"firstname":"Ada","lastname":"Lovelace","totalprice":111,"depositpaid":true,
       "bookingdates":{"checkin":"2026-01-01","checkout":"2026-01-03"},"additionalneeds":"Tea"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["bookingid"])')

curl -s -o /dev/null -w "PATCH status=%{http_code} time=%{time_total}s\n" -X PATCH $BASE/booking/$ID \
  -H 'Content-Type: application/json' -H "Cookie: token=$TOKEN" -d '{"firstname":"Grace"}'
```

🟣 **High/Complex: a test-idea matrix derived from heuristics**
| # | Endpoint | Idea | Type | Expected |
|---|---|---|---|---|
| 1 | POST /booking | Valid payload round-trips exactly | Positive | 200 + echo |
| 2 | POST /booking | `checkout` before `checkin` | Validation | 4xx (if 200 → bug?) |
| 3 | POST /booking | `totalprice` as string `"abc"` | Type | 4xx, never 500 |
| 4 | POST /booking | Missing `firstname` | Required field | 4xx |
| 5 | PUT /booking/{id} | No token | Auth | 403 |
| 6 | PUT /booking/{id} | Expired or garbage token | Auth | 403 |
| 7 | PATCH /booking/{id} | Only firstname → other fields unchanged | Partial update | 200 |
| 8 | DELETE /booking/{id} | Then GET the same ID | State | 404 |
| 9 | DELETE /booking/{id} | Twice | Idempotency | 2nd → 404/405, not 500 |
| 10 | GET /booking?checkin= | Invalid date format | Validation | 4xx or empty list, not 500 |
| 11 | POST /booking | 10,000-char `additionalneeds` | Boundary | Defined limit or accepted |
| 12 | POST /booking | Unicode names `Zoë 李` | i18n | Round-trips unchanged |
Mark each idea with what you actually observed. Where "expected" and "actual" differ, you have a **bug candidate** (P10-01).

#### 🎤 Interview Q&A

<details><summary><b>[Z] PUT vs PATCH?</b></summary>

PUT replaces the whole resource with the payload (omitted fields may be cleared) and is idempotent. PATCH applies a partial update to specific fields. Test PATCH by asserting that the untouched fields are unchanged.
</details>

<details><summary><b>[Z] 401 vs 403?</b></summary>

401 Unauthorized really means *unauthenticated*: no or invalid credentials. 403 Forbidden means authenticated but lacking permission. Some APIs (including Restful-Booker) use 403 for a missing token, so test what the contract says and flag deviations for discussion.
</details>

<details><summary><b>[H] What does "idempotent" mean for HTTP methods, and why do testers care?</b></summary>

Repeating the request has the same effect on server state as sending it once. GET, PUT and DELETE should be idempotent; POST generally isn't. Testers care because (1) it defines what's safe to retry automatically, and (2) it's testable: send PUT twice and the state is the same; send POST twice and you probably get a duplicate (sometimes a bug, e.g. double payments, if there's no idempotency key).
</details>

<details><summary><b>[H] 400 vs 422?</b></summary>

400 means the request is malformed (unparseable JSON, wrong content type). 422 means it's well-formed but semantically invalid (checkout before checkin, invalid email). Many APIs use 400 for both. What matters is consistency and never returning 500 for client mistakes.
</details>

<details><summary><b>[H] You get an API with no documentation. How do you test it?</b></summary>

Discover: capture real traffic (browser DevTools, proxy), look for OpenAPI/Swagger endpoints, read the client code. Explore with heuristics (CRUD, auth, boundaries, errors). Document the inferred contract, confirm it with developers, then automate the confirmed behaviour and push for a spec, which becomes the basis for contract tests.
</details>

<details><summary><b>[SH] REST vs GraphQL vs gRPC: how does your testing approach change?</b></summary>

REST: resource URLs, status codes carry meaning, test per endpoint. GraphQL: a single endpoint, errors often come back as HTTP 200 with an `errors` array, so assert the body, test query depth/complexity limits, field-level auth and N+1 performance. gRPC: a binary protobuf contract, status codes are gRPC codes, you test with generated stubs, and contract changes are caught via proto compatibility rules. The principles stay the same: contract, auth, validation, errors, performance.
</details>

#### 🤖 AI assist
- Paste the API docs page and ask AI for *more negative test ideas*. Add only the ones you can justify.

---

### P04-02 · First API tests with requests

**Level:** 🟢 Zero · **Time:** 3h · **App:** Restful-Booker · **Deliverable:** `tests/api/booker/test_booking_basic.py`

#### 📋 Task
Automate the core checks with `requests` (using the `http`, `settings` and `booker_url` fixtures from P03):
1. `/ping` health check (assert the *documented* code).
2. `GET /booking` returns a list of objects with `bookingid`.
3. `POST /booking` creates a booking and echoes the payload, then `GET /booking/{id}` returns the same data (round trip).
4. The filter `?firstname=` returns your created booking.
5. Assert the `Content-Type` header, and put a soft response-time budget (e.g. < 3 s) in the assertion message.
6. **Every call has a timeout.**

**Done when**
- [ ] ≥6 tests, all green, none depending on pre-existing data
- [ ] Assertion messages include the response body on failure

#### 📘 User guide

**Concepts**
- `requests.get/post/put/patch/delete(url, params=, json=, data=, headers=, cookies=, auth=, timeout=)`.
- **`json=`** serialises a dict *and* sets `Content-Type: application/json`. **`data=`** sends form-encoded (or raw) data.
- **Response:** `.status_code`, `.ok`, `.json()`, `.text`, `.headers` (case-insensitive dict), `.elapsed`, `.raise_for_status()`.
- **Timeout:** `timeout=10` or `(connect, read)` like `(3.05, 10)`.

**Deep dive**

**No timeout means a hung suite.** `requests` waits **forever** by default. One stalled server freezes CI until the job-level timeout (often 6 hours). Ruff rule `S113` from P00-04 catches this. Always pass `timeout`.

**What to assert (in order):**
1. **Status code.** Assert it first with a message that includes the body: `assert r.status_code == 200, r.text`.
2. **Headers** that matter (`Content-Type`, caching, `Location` for 201s).
3. **Body:** key fields and **types**, not the whole blob.
4. **Side effects:** read back what you wrote (round trip), and later check the DB (P06).

**Dynamic fields** (IDs, timestamps) make whole-body equality brittle. Compare the fields you control, or strip dynamic keys before comparing.

**`response.json()`** raises if the body isn't JSON, e.g. an HTML error page from a proxy. Assert the status and content type first so failures are readable.

**Response time checks** in functional tests should be **coarse smoke budgets** that catch "suddenly 30 s", not performance testing. Real performance testing needs controlled load and percentiles (a separate discipline).

**Examples**

🟢 **Low: health and list**
```python
import pytest

@pytest.mark.smoke
def test_ping(http, booker_url):
    r = http.get(f"{booker_url}/ping", timeout=10)
    assert r.status_code == 201, r.text          # yes, 201: it's documented, and a classic gotcha

def test_booking_ids_are_listed(http, booker_url):
    r = http.get(f"{booker_url}/booking", timeout=10)
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list) and body, "expected a non-empty list"
    assert all("bookingid" in item for item in body)
```

🔵 **Medium: a create → read round trip**
```python
from python_basics.checkout import build_booking

def test_created_booking_can_be_read_back(http, booker_url):
    payload = build_booking(firstname="Ada", lastname="Lovelace")
    created = http.post(f"{booker_url}/booking", json=payload,
                        headers={"Accept": "application/json"}, timeout=(3.05, 10))
    assert created.status_code == 200, created.text
    assert created.headers["Content-Type"].startswith("application/json")
    booking_id = created.json()["bookingid"]
    assert created.json()["booking"] == payload

    fetched = http.get(f"{booker_url}/booking/{booking_id}", headers={"Accept": "application/json"}, timeout=10)
    assert fetched.status_code == 200, fetched.text
    assert fetched.json() == payload
    assert fetched.elapsed.total_seconds() < 3, f"slow response: {fetched.elapsed}"
```

🟣 **High/Complex: edge-value round trips with helpful diffs**
```python
import pytest
from python_basics.checkout import build_booking
from python_basics.drills import json_diff        # P02-06

EDGE_CASES = [
    pytest.param({"firstname": "Zoë", "lastname": "李"}, id="unicode"),
    pytest.param({"totalprice": 0}, id="zero-price"),
    pytest.param({"depositpaid": False}, id="no-deposit"),
    pytest.param({"bookingdates": {"checkin": "2026-02-28", "checkout": "2026-03-01"}}, id="month-boundary"),
    pytest.param({"additionalneeds": "x" * 500}, id="long-text"),
]

@pytest.mark.parametrize("overrides", EDGE_CASES)
def test_booking_round_trips_edge_values(http, booker_url, overrides):
    payload = build_booking(**overrides)
    r = http.post(f"{booker_url}/booking", json=payload, headers={"Accept": "application/json"}, timeout=10)
    assert r.status_code == 200, f"create failed: {r.status_code} {r.text[:300]}"

    got = http.get(f"{booker_url}/booking/{r.json()['bookingid']}",
                   headers={"Accept": "application/json"}, timeout=10).json()
    diffs = json_diff(payload, got)
    assert not diffs, "round-trip mismatch:\n" + "\n".join(diffs)
```
If an edge case fails, you may have found a real bug. Write it up in P10-01 rather than "fixing" the test.

#### 🎤 Interview Q&A

<details><summary><b>[Z] <code>json=</code> vs <code>data=</code> in requests?</b></summary>

`json=` serialises a Python object to JSON and sets `Content-Type: application/json`. `data=` sends form-encoded data for dicts, or raw bytes/strings as-is, and you set the content type yourself. Using `data=dict` against a JSON API is a common bug (the server gets form data and returns 400/415).
</details>

<details><summary><b>[Z] Why must every request have a timeout?</b></summary>

requests has no default timeout, so a hung server blocks the test (and the CI job) indefinitely. A timeout turns a hang into a fast, clear failure. Use a connect/read tuple and a sensible default from config.
</details>

<details><summary><b>[H] What do you assert in an API test?</b></summary>

Status code (with the body in the message), important headers, body fields and types (ideally via schema/model validation), business rules (totals, states), side effects (read back, DB checks), and for errors the error contract (code, message format). I avoid asserting volatile fields (timestamps, IDs) except for format.
</details>

<details><summary><b>[H] How do you compare API responses that contain dynamic values?</b></summary>

Compare only controlled fields, strip or mask dynamic keys before comparing, assert formats for dynamic values (UUID regex, ISO timestamp within a time window), or validate with a schema/model and check the specific business fields separately. A path-reporting diff makes failures readable.
</details>

<details><summary><b>[H] Should functional API tests check response time?</b></summary>

Only as a coarse guardrail (e.g. < 2–3 s per call) to catch severe regressions, with generous limits to avoid flakiness. Real performance validation (percentiles under load, throughput) belongs in dedicated performance tests with controlled environments.
</details>

#### 🤖 AI assist
- Ask AI to review your test file for *missing assertions* ("what bug would still pass these tests?").

---

### P04-03 · Auth, CRUD and negative testing

**Level:** 🔵 Hero · **Time:** 4h · **App:** Restful-Booker · **Deliverable:** `tests/api/booker/test_booking_crud.py`, `tests/api/booker/test_booking_negative.py`

#### 📋 Task
1. Full lifecycle test: create → read → PUT (full replace) → PATCH (partial) → DELETE → GET returns 404.
2. After a PATCH, assert that the **untouched fields are unchanged**.
3. Authenticate two ways: the token **cookie** and **HTTP Basic** (`auth=("admin", "password123")`).
4. A parametrized negative matrix: no token, garbage token, non-existent ID, wrong types, missing required fields, malformed JSON.
5. For every negative case, assert **"never 5xx"** as well as the expected code. If the API returns 500 for bad input, mark it `xfail(strict=True)` with a bug ID and write the bug report (P10-01).

**Done when**
- [ ] Lifecycle and negative tests pass (or strict-xfail with a filed bug)
- [ ] You can explain each negative category and why it matters

#### 📘 User guide

**Concepts**
- **Authentication** (who you are) vs **authorization** (what you may do).
- **Auth mechanisms:** Basic (base64 `user:pass` in the `Authorization` header), **Bearer token** (`Authorization: Bearer <jwt>`), **API key** (a header or query param), **cookie/session**, **OAuth2** (tokens issued by an auth server).
- **Negative testing:** proving the system *rejects* bad input safely and clearly.

**Deep dive**

**Token lifecycle in a suite:** get a token once per session (a session fixture). If tokens expire mid-run (long suites), build a client that refreshes on 401 **once** and then fails. Never hard-code tokens.

**Negative test categories:**
| Category | Examples | Expected |
|---|---|---|
| Authentication | Missing, garbage, expired token | 401/403 |
| Authorization | Customer → admin endpoint, user A → user B's data (**IDOR**) | 403/404 |
| Validation | Missing required, wrong type, out-of-range, bad format | 400/422 with a clear message |
| Existence | Unknown ID, already deleted | 404 |
| Conflict | Duplicate unique field | 409 |
| Protocol | Wrong method, wrong content type, malformed JSON | 405/415/400 |

**5xx on bad input is always a bug.** It means input wasn't validated, and it often hides security issues. A robust negative test asserts both `status < 500` and the specific expected code, so the failure message is precise.

**IDOR** (Insecure Direct Object Reference): can user A read or modify user B's resource by changing an ID? It's one of the most common real-world API vulnerabilities, and testers find it with simple two-user tests.

**Examples**

🟢 **Low: token plus an authorised update**
```python
from python_basics.checkout import build_booking

def test_put_with_token_replaces_booking(http, booker_url, booker_token, booking):
    new = build_booking(firstname="Grace", lastname="Hopper", totalprice=999)
    r = http.put(f"{booker_url}/booking/{booking['bookingid']}", json=new,
                 cookies={"token": booker_token}, headers={"Accept": "application/json"}, timeout=10)
    assert r.status_code == 200, r.text
    assert r.json() == new
```

🔵 **Medium: PATCH semantics and the full lifecycle**
```python
def test_patch_changes_only_given_fields(http, booker_url, booker_token, booking):
    booking_id, before = booking["bookingid"], booking["booking"]
    r = http.patch(f"{booker_url}/booking/{booking_id}", json={"firstname": "Patched"},
                   cookies={"token": booker_token}, headers={"Accept": "application/json"}, timeout=10)
    assert r.status_code == 200, r.text
    after = r.json()
    assert after["firstname"] == "Patched"
    assert {k: v for k, v in after.items() if k != "firstname"} == \
           {k: v for k, v in before.items() if k != "firstname"}

def test_deleted_booking_is_gone(http, booker_url, make_booking):
    booking_id = make_booking()["bookingid"]
    d = http.delete(f"{booker_url}/booking/{booking_id}", auth=("admin", "password123"), timeout=10)
    assert d.status_code in (200, 201, 204), d.text      # check the docs: Restful-Booker's code is unusual
    assert http.get(f"{booker_url}/booking/{booking_id}", timeout=10).status_code == 404
```

🟣 **High/Complex: a data-driven negative matrix with a "never 5xx" guard**
```python
import pytest
from python_basics.checkout import build_booking

def without(field):
    p = build_booking(); p.pop(field); return p

NEGATIVE = [
    # id,                method,   path,               auth,       body,                                  expected
    ("no-token",         "PUT",    "/booking/{id}",    None,       build_booking(),                       403),
    ("garbage-token",    "PUT",    "/booking/{id}",    "garbage",  build_booking(),                       403),
    ("unknown-id",       "GET",    "/booking/999999999", None,     None,                                  404),
    ("missing-lastname", "POST",   "/booking",         None,       without("lastname"),                   400),
    ("price-as-text",    "POST",   "/booking",         None,       build_booking(totalprice="abc"),       400),
    ("malformed-json",   "POST",   "/booking",         None,       '{"firstname": "Ada",',                400),
]

@pytest.mark.parametrize("method,path,auth,body,expected", [pytest.param(*row[1:], id=row[0]) for row in NEGATIVE])
def test_bad_requests_are_rejected_cleanly(http, booker_url, booking, method, path, auth, body, expected):
    url = booker_url + path.format(id=booking["bookingid"])
    kwargs = {"timeout": 10, "headers": {"Accept": "application/json", "Content-Type": "application/json"}}
    if auth:
        kwargs["cookies"] = {"token": auth}
    if isinstance(body, str):
        kwargs["data"] = body                        # raw malformed JSON
    elif body is not None:
        kwargs["json"] = body
    r = http.request(method, url, **kwargs)
    assert r.status_code < 500, f"server error on bad input ({r.status_code}): {r.text[:200]}"
    assert r.status_code == expected, f"expected {expected}, got {r.status_code}: {r.text[:200]}"
```
> Run it and **observe**: some of these may return 500 on the demo app. Don't change `expected` to 500. Mark it `xfail(strict=True, reason="BUG-…")` and report it.

#### 🎤 Interview Q&A

<details><summary><b>[Z] Authentication vs authorization?</b></summary>

Authentication verifies identity (login, token validity). Authorization decides what an authenticated identity may access (roles, ownership). Tests must cover both: invalid identity is rejected, and a valid identity can't exceed its permissions.
</details>

<details><summary><b>[H] How do you handle token expiry in a long-running suite?</b></summary>

Fetch the token in a session fixture. Wrap the client so a 401 triggers one re-authentication and retry of that request, and log it. Decode the JWT `exp` claim to refresh proactively. Keep a separate test that verifies expired tokens *are* rejected, so the refresh logic never hides an auth bug.
</details>

<details><summary><b>[H] What categories of negative tests do you write for an API?</b></summary>

Authentication, authorization (roles and IDOR), input validation (required, types, formats, ranges, lengths), existence (unknown or deleted IDs), conflicts (duplicates, stale versions), protocol (method, content type, malformed body), and rate limiting. Each asserts the specific code, a helpful error body, and never 5xx.
</details>

<details><summary><b>[H] The API returns 500 when you send a string for a number. Is that a bug?</b></summary>

Yes. 5xx means the server failed to handle client input, which should be a 4xx with a validation message. It can indicate missing validation and potential security issues, and it pollutes error monitoring. I'd report it with the request, response and expected behaviour, and keep a strict-xfail test linked to the bug so we notice when it's fixed.
</details>

<details><summary><b>[SH] How do you test an RBAC permission matrix without writing hundreds of tests by hand?</b></summary>

Define the matrix as data: roles × endpoints × methods → expected allow/deny. Generate parametrized tests from it (`pytest_generate_tests`), with a token fixture per role and per-test data ownership (user A's resources vs user B's for IDOR). Review the matrix with product/security, since it becomes living documentation, and run it on every permission-related change.
</details>

<details><summary><b>[SH] How would you test an OAuth2-protected API in automation?</b></summary>

Use the client-credentials grant (or a test-only confidential client) to get tokens programmatically. Avoid automating the provider's login UI. Cache tokens per role for the session, and test token handling separately: expired, wrong audience or scope, revoked. Keep client secrets in the CI secret store, and use short-lived tokens in pipelines.
</details>

#### 🤖 AI assist
- Ask AI: *"List OWASP API Top 10 risks that a functional tester can check with simple requests."* Pick two (e.g. BOLA/IDOR) and add tests.

---

### P04-04 · API client layer and schema validation

**Level:** 🔵 Hero · **Time:** 4h · **App:** Restful-Booker · **Deliverable:** `framework/api/base_client.py`, `framework/api/booker_client.py`, `framework/api/models/booking.py`

#### 📋 Task
1. `BaseClient`: owns a `requests.Session`, joins base URL + path, applies the default timeout, logs every request and response, and **retries only idempotent methods** on 502/503/504.
2. `BookerClient(BaseClient)`: `auth()`, `create_booking()`, `get_booking()`, `update_booking()`, `patch_booking()`, `delete_booking()`, `list_bookings(**filters)`.
3. Pydantic models `Booking`, `BookingDates`, `BookingCreated`. Successful calls return **models**, and negative tests can still get the raw `Response`.
4. Refactor your P04-02/P04-03 tests to use the client. **No raw URLs in tests.**
5. On test failure, attach the last request/response to the report (use the P03-06 hook pattern).

**Done when**
- [ ] Tests read like: `booking = booker.create_booking(payload); assert booker.get_booking(booking.bookingid) == booking.booking`
- [ ] A schema change (e.g. `totalprice` returned as a string) makes tests fail with a clear pydantic error

#### 📘 User guide

**Concepts**
- **Layered framework:** tests (intent and assertions) → clients (endpoints) → transport (session, auth, retries, logging).
- **Service object / API client:** one class per service or resource, one method per operation.
- **Pydantic:** `BaseModel`, `model_validate(dict)`, `model_dump()`, `ConfigDict(extra="forbid")`, validators.
- **Retry adapter:** `HTTPAdapter(max_retries=Retry(...))` from `urllib3`.

**Deep dive**

**Why a client layer?** When the base URL, auth scheme or an endpoint path changes, you fix one method, not 200 tests. Tests become readable business statements. Logging and retries are applied consistently.

**Where do assertions live?** Tests assert **business outcomes**. Clients may **validate transport-level expectations** (e.g. `expect=200` → raise with the body if not) so positive tests stay terse, but they never decide pass/fail for business rules. For negative tests, expose the raw response (`create_booking_raw()` or `expect=None`).

**Schema strictness is a design decision:**
| Mode | Pydantic | Catches | Risk |
|---|---|---|---|
| Lenient | `extra="ignore"` | Missing or wrong-typed fields you use | Misses new or unknown fields |
| Strict | `extra="forbid"` | Any unexpected field (contract drift) | Breaks on harmless additive changes |
Common practice: **lenient in functional tests** (validate what you consume) and **strict in dedicated contract tests** (P04-08).

**Retries in a test framework:** retry *transport* failures (502/503/504, connection resets) on *idempotent* methods only, with backoff. Never retry POST blindly (duplicates), and never retry assertion failures. Log each retry so flakiness is visible.

**Examples**

🟢 **Low: a minimal base client**
```python
# framework/api/base_client.py
import requests

class BaseClient:
    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, f"{self.base_url}/{path.lstrip('/')}", **kwargs)
```

🔵 **Medium: a typed client with pydantic models**
```python
# framework/api/models/booking.py
from pydantic import BaseModel, ConfigDict

class BookingDates(BaseModel):
    checkin: str
    checkout: str

class Booking(BaseModel):
    model_config = ConfigDict(extra="ignore")      # lenient: functional tests
    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str | None = None

class BookingCreated(BaseModel):
    bookingid: int
    booking: Booking
```
```python
# framework/api/booker_client.py
import requests
from framework.api.base_client import BaseClient
from framework.api.models.booking import Booking, BookingCreated

class ApiError(AssertionError):
    pass

class BookerClient(BaseClient):
    def _expect(self, r: requests.Response, status: int) -> requests.Response:
        if r.status_code != status:
            raise ApiError(f"{r.request.method} {r.url} → {r.status_code} (expected {status}): {r.text[:500]}")
        return r

    def auth(self, username: str = "admin", password: str = "password123") -> None:
        r = self._expect(self.request("POST", "/auth", json={"username": username, "password": password}), 200)
        self.session.cookies.set("token", r.json()["token"])

    def create_booking_raw(self, payload: dict) -> requests.Response:
        return self.request("POST", "/booking", json=payload)

    def create_booking(self, payload: dict) -> BookingCreated:
        return BookingCreated.model_validate(self._expect(self.create_booking_raw(payload), 200).json())

    def get_booking(self, booking_id: int) -> Booking:
        return Booking.model_validate(self._expect(self.request("GET", f"/booking/{booking_id}"), 200).json())
```
```python
# test using the client
def test_round_trip(booker):              # fixture: BookerClient(settings.booker_url) with .auth()
    created = booker.create_booking(build_booking(firstname="Ada"))
    assert booker.get_booking(created.bookingid) == created.booking
```

🟣 **High/Complex: retries for idempotent methods, exchange capture and report attachment**
```python
# framework/api/base_client.py (full)
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

log = logging.getLogger("api")

class BaseClient:
    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url, self.timeout = base_url.rstrip("/"), timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        retry = Retry(total=3, backoff_factor=0.5, status_forcelist=(502, 503, 504),
                      allowed_methods=frozenset({"GET", "PUT", "DELETE", "HEAD", "OPTIONS"}),
                      raise_on_status=False)
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.session.mount("http://", HTTPAdapter(max_retries=retry))
        self.session.hooks["response"].append(self._record)
        self.history: list[str] = []                       # last N exchanges for failure reports

    def _record(self, r: requests.Response, *args, **kwargs) -> None:
        req = r.request
        entry = (f"{req.method} {req.url}\n> {(req.body or b'')[:500]!r}\n"
                 f"< {r.status_code} in {r.elapsed.total_seconds():.2f}s\n< {r.text[:500]}")
        self.history = (self.history + [entry])[-5:]
        log.info("%s %s → %s (%.2fs)", req.method, req.url, r.status_code, r.elapsed.total_seconds())

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        return self.session.request(method, f"{self.base_url}/{path.lstrip('/')}", **kwargs)
```
```python
# tests/api/conftest.py: attach the API history to the report when a test fails
import pytest
from framework.api.booker_client import BookerClient

@pytest.fixture
def booker(settings, request):
    client = BookerClient(settings.booker_url, timeout=settings.http_timeout)
    client.auth()
    yield client
    rep = getattr(request.node, "rep_call", None)          # set by the P03-06 plugin
    if rep is not None and rep.failed:
        rep.sections.append(("API exchanges", "\n\n".join(client.history)))
    client.session.close()
```

#### 🎤 Interview Q&A

<details><summary><b>[H] Why build an API client layer instead of calling requests in tests?</b></summary>

Single responsibility and change isolation: URLs, auth, headers, timeouts, retries and logging live in one place. Tests become readable business scenarios, and endpoint changes are one-line fixes. It also enables typed models, shared evidence capture and reuse by UI tests (API setup for UI flows).
</details>

<details><summary><b>[H] Where should assertions live: in clients or in tests?</b></summary>

Business assertions live in tests. Clients may enforce expected transport status for convenience (raise with context), but they must also expose raw responses for negative tests. Hiding business checks in clients makes tests unclear about what they verify.
</details>

<details><summary><b>[H] Pydantic vs JSON Schema for response validation?</b></summary>

Pydantic: Python-native models, typed objects for tests, readable errors, and it doubles as the data model. JSON Schema: language-agnostic, can be generated from or shared with OpenAPI specs, and good for pure contract checks. Many frameworks use pydantic models in functional tests and spec-based validation in contract tests.
</details>

<details><summary><b>[SH] Strict or lenient schema validation?</b></summary>

It depends on the goal. Functional tests should be lenient (validate what they use) so additive, backward-compatible changes don't break unrelated tests. Contract tests should be strict (forbid unknown fields, validate every documented field) to detect drift early, and they're owned with the API team. Mixing the two causes either brittleness or blind spots.
</details>

<details><summary><b>[SH] How do you make API test failures easy to debug?</b></summary>

Capture request/response exchanges (method, URL, headers minus secrets, body, status, timing) and attach them to the report on failure. Add a correlation ID header per test so backend logs can be searched. Use assertion messages with the body, and link to logs or traces. Mask tokens and PII in anything logged.
</details>

#### 🤖 AI assist
- Paste a JSON response and ask AI to *draft* pydantic models, then review the types (int vs float, optional fields) against real responses.

---

### P04-05 · Docker as a user: images, containers, ports and volumes

**Level:** 🟢 Zero · **Time:** 3h · **App:** The Internet (Docker image) · **Deliverable:** `docs/docker-cheatsheet.md`

> **Why here?** From P04-07 onwards you'll run Toolshop, Restful-Booker and Pagila on your own machine, so you need to *use* Docker confidently first. Building and maintaining your own images comes later, in P08.

#### 📋 Task
1. `docker pull gprestes/the-internet`, then **find the port it listens on yourself**: `docker image inspect` (look at `Config.ExposedPorts`).
2. Run it detached with a port mapping, open it in your browser, and point a small smoke check at it (🔵 example). In P05-05 you'll point your UI tests at the same container.
3. Practise the lifecycle: `ps`, `logs -f`, `exec -it … sh`, `stop`, `start`, `rm`, `images`, `rmi`, `system df`.
4. **Volumes:** run `postgres` with a named volume, create a table, remove the container, start a new one on the same volume, and show the table survived.
5. Write `docs/docker-cheatsheet.md` in your own words.

**Done when**
- [ ] Your smoke check passes against the local container (`QE_INTERNET_URL=http://localhost:7080`)
- [ ] You can explain image vs container, `EXPOSE` vs `-p`, and named volume vs bind mount

#### 📘 User guide

**Concepts**
- **Image:** a read-only, layered filesystem plus metadata (default command, env, exposed ports). **Container:** a running (or stopped) instance of an image with its own writable layer.
- **Registry and tags:** `name:tag` (e.g. `postgres:18`). `latest` is just a tag, not "newest guaranteed".
- **Port publishing:** `-p HOST:CONTAINER` maps a host port to the container's port. `EXPOSE` in an image is *documentation only*.
- **Volumes:** a **named volume** is managed by Docker and survives containers. A **bind mount** maps a host folder into the container.
- **Networks:** containers on the same user-defined network reach each other **by name**.

**Deep dive**

**Containers are processes, not VMs.** They share the host kernel and are isolated with namespaces and cgroups, so they start in milliseconds and are light. (On macOS and Windows, Docker runs them inside a small Linux VM, which is why file mounts can be slower there.)

**Ephemeral by design.** Anything written inside a container's writable layer disappears with `docker rm`. Persist data in volumes, and get test reports out through bind mounts (P08-01).

**`localhost` means "me".** Inside a container, `localhost` is the container itself, not your laptop or another container. This is the number-one Docker networking confusion. Other containers are reached by service or container name on a shared network, and the host by `host.docker.internal` (Docker Desktop).

**Why a container "exits immediately":** a container lives only as long as its main process. If the command finishes (or crashes), the container stops. `docker logs <name>` tells you why.

**Examples**

🟢 **Low: pull, inspect, run, observe**
```bash
docker pull gprestes/the-internet
docker image inspect gprestes/the-internet --format '{{json .Config.ExposedPorts}}'   # find the port
docker run -d --name internet -p 7080:<container-port> gprestes/the-internet
docker ps
docker logs -f internet            # Ctrl+C to stop following
curl -I http://localhost:7080/
```

🔵 **Medium: point a smoke check at the container**
```python
# tests/smoke/test_internet_up.py (in P05-05 the same fixture moves to tests/ui/internet/conftest.py)
import os

import pytest
import requests


@pytest.fixture(scope="session")
def internet_url() -> str:
    return os.getenv("QE_INTERNET_URL", "https://the-internet.herokuapp.com")


@pytest.mark.parametrize("path", ["/", "/login", "/dynamic_loading", "/nested_frames"])
def test_page_is_served(internet_url: str, path: str) -> None:
    response = requests.get(f"{internet_url}{path}", timeout=10)
    assert response.status_code == 200, f"{path} returned {response.status_code}"
```
```bash
QE_INTERNET_URL=http://localhost:7080 uv run pytest tests/smoke -q
docker exec -it internet sh -c 'ls /; ps aux | head'   # look inside (tools vary by image)
docker stop internet && docker rm internet
```

🟣 **High/Complex: persistence, resource limits and inspection with templates**
```bash
docker volume create pgdata
docker run -d --name pg1 -e POSTGRES_PASSWORD=secret -v pgdata:/var/lib/postgresql -p 5433:5432 postgres:18
docker exec -it pg1 psql -U postgres -c "CREATE TABLE survivor(id int); INSERT INTO survivor VALUES (42);"
docker rm -f pg1
docker run -d --name pg2 -e POSTGRES_PASSWORD=secret -v pgdata:/var/lib/postgresql -p 5433:5432 postgres:18
docker exec -it pg2 psql -U postgres -c "SELECT * FROM survivor;"     # 42 is still there
# PG 18 images store data under /var/lib/postgresql/<version>; older images used /var/lib/postgresql/data

docker run -d --name limited --memory 512m --cpus 1 gprestes/the-internet
docker stats --no-stream limited
docker inspect limited --format 'IP={{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}} Restart={{.HostConfig.RestartPolicy.Name}}'
docker rm -f pg2 limited && docker volume rm pgdata
```

#### 🎤 Interview Q&A

<details><summary><b>[Z] Image vs container?</b></summary>

An image is an immutable template (layered filesystem plus config). A container is a running instance of it with a thin writable layer. You can run many containers from one image, and deleting a container loses anything not stored in a volume.
</details>

<details><summary><b>[Z] Docker container vs virtual machine?</b></summary>

VMs virtualise hardware and run a full guest OS: heavy, with slow boot and strong isolation. Containers share the host kernel and isolate processes with namespaces and cgroups: light, fast to start, dense. For test environments, containers give reproducible dependencies in seconds.
</details>

<details><summary><b>[H] <code>EXPOSE</code> vs <code>-p</code>?</b></summary>

`EXPOSE` in a Dockerfile documents which port the app listens on and publishes nothing. `-p 8080:80` (or `ports:` in Compose) actually maps a host port to a container port. Containers on the same network can reach each other's ports without `-p`.
</details>

<details><summary><b>[H] Named volumes vs bind mounts?</b></summary>

Named volumes are managed by Docker, portable, and good for database data that must survive container recreation. Bind mounts map a specific host path, which is good for source code during development and for getting test reports out to the host. Bind mounts depend on host paths and permissions.
</details>

<details><summary><b>[H] Inside a container, tests fail to reach <code>http://localhost:3001</code>, which works on your laptop. Why?</b></summary>

Inside the container, localhost is the container itself. Use the other container's service name on a shared network (`http://restful-booker:3001`), or `host.docker.internal` to reach a service on the host (Docker Desktop, or with an extra host mapping on Linux).
</details>

#### 🤖 AI assist
- Paste a failing `docker run` error and ask AI to explain it, then confirm with `docker logs` and `docker inspect`.

---

### P04-06 · Run the demo stack locally with Compose

**Level:** 🟢 Zero · **Time:** 3h · **App:** Toolshop, Restful-Booker, Pagila · **Deliverable:** `docs/local-stack.md`, `Makefile` targets `stack-up`, `stack-down`, `stack-reset`

#### 📋 Task
1. Clone and start **Toolshop**, **Restful-Booker** and **Pagila** with their own Compose files (DEMO_APPS.md). Seed the Toolshop DB.
2. Use `docker compose ps`, `logs -f <service>`, `exec`, `stop`, `down` and `down -v` (understand what `-v` destroys).
3. Resolve at least one **port conflict** (e.g. something already on 5432 or 8080) by changing the *host* side of a mapping in an override file.
4. Run your suites with `--env local`.
5. Add `make stack-up` / `stack-down` / `stack-reset` plus a readiness check, and document everything in `docs/local-stack.md`.

**Done when**
- [ ] `make stack-up && uv run pytest --env local -m "smoke"` works from a cold start
- [ ] `docs/local-stack.md` has start, stop, reset and troubleshooting sections

#### 📘 User guide

**Concepts**
- **Compose file:** declares **services** (containers), networks and volumes for a multi-container app.
- **Project:** the set of containers from one compose file, named after the folder or `name:`. It gets its own default network.
- **Commands:** `up -d`, `ps`, `logs`, `exec`, `stop`, `down` (removes containers and networks), `down -v` (**also deletes volumes**).
- **Override file:** `docker-compose.override.yml` is merged automatically, so you can change ports locally without editing upstream files.

**Deep dive**

**Service discovery:** Compose puts a project's services on one network where each service is reachable by its **service name** (`http://laravel-api:80` inside the network, even while the host sees `localhost:8091`). Host ports are only for *you* (and host processes).

**State and resets:** DB data usually lives in a named volume, so `down` keeps your data and `down -v` wipes it. Know which one you need. A deterministic reset command (Toolshop's `migrate:fresh --seed`) is gold for testing: reset → run → known state.

**Readiness vs started:** "container started" ≠ "app ready". Databases need seconds to accept connections and web apps need time to boot. Always wait on a *readiness signal* (an HTTP 200 on a health URL, or a DB query) before running tests. P08-02 builds this into Compose with health checks.

**Examples**

🟢 **Low: everyday Compose commands**
```bash
cd ~/src/practice-software-testing && docker compose up -d
docker compose ps
docker compose logs -f --tail=50          # all services; add a service name to focus
docker exec -it pst-laravel-api-1 php artisan migrate:fresh --seed     # reset data (check container name)
docker compose down                        # keep volumes
```

🔵 **Medium: Makefile orchestration across stacks**
```makefile
STACKS := ~/src/practice-software-testing ~/src/restful-booker ~/src/pagila

stack-up:
	@for d in $(STACKS); do (cd $$d && docker compose up -d); done
	@uv run python scripts/wait_for_stack.py

stack-down:
	@for d in $(STACKS); do (cd $$d && docker compose down); done

stack-reset:
	docker exec pst-laravel-api-1 php artisan migrate:fresh --seed
```

🟣 **High/Complex: a readiness checker that tells you *which* service isn't ready**
```python
# scripts/wait_for_stack.py
import sys
import requests
from framework.utils.wait import wait_until       # P02-05

CHECKS = {
    "toolshop-api": "http://localhost:8091/products",
    "toolshop-ui": "http://localhost:4200/",
    "restful-booker": "http://localhost:3001/ping",
}

def ready(url: str) -> bool:
    try:
        return requests.get(url, timeout=3).status_code < 500
    except requests.RequestException:
        return False

def main() -> int:
    failed = []
    for name, url in CHECKS.items():
        try:
            wait_until(lambda: ready(url), timeout=180, interval=3, message=f"{name} at {url}")
            print(f"✅ {name}")
        except TimeoutError as e:
            print(f"❌ {e}")
            failed.append(name)
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
```
```yaml
# docker-compose.override.yml in the Pagila folder: fix a port conflict on the HOST side only
services:
  pagila:                  # check the service name with: docker compose config --services
    ports: !override
      - "5544:5432"
```
> `!override` replaces the list instead of merging it (a recent Compose feature). If your version lacks it, edit the port in a copy of the file.

#### 🎤 Interview Q&A

<details><summary><b>[Z] <code>docker compose</code> vs <code>docker run</code>?</b></summary>

`docker run` starts one container with flags on the command line. Compose declares a multi-container application (services, networks, volumes, env, dependencies) in a versioned YAML file, starts it with one command and gives shared networking with service-name DNS. It's reproducible and reviewable.
</details>

<details><summary><b>[H] How do services in a Compose project talk to each other?</b></summary>

Compose creates a network per project, and each service is resolvable by its service name. Service A calls `http://service-b:<container-port>`. Host port mappings are irrelevant between containers and only needed for access from the host.
</details>

<details><summary><b>[H] <code>docker compose down</code> vs <code>down -v</code>?</b></summary>

`down` removes containers and networks but keeps named volumes (your DB data survives). `down -v` also deletes the volumes, which is a full data reset. That's handy for clean test runs and disastrous if you meant to keep the data.
</details>

<details><summary><b>[Z] You get "port is already allocated". What do you do?</b></summary>

Another process or container already uses that host port. Find it (`docker ps`, `lsof -i :5432`), stop it, or map a different *host* port (`"5544:5432"`) via an override file, then update your test config (`.env`).
</details>

<details><summary><b>[H] How do you give every test run a known environment state?</b></summary>

A scripted reset: recreate volumes (`down -v && up`), run the app's seed/migrate command, or restore a DB snapshot or template, then wait for readiness. Tests still create their own data, and the reset guarantees the *reference* data (users, catalogue) is known.
</details>

#### 🤖 AI assist
- Ask AI to explain an unfamiliar service in Toolshop's compose file (what it is and why it's there), then verify by reading the file and the logs.

---

### P04-07 · Toolshop API: bearer auth, pagination, filters, data factories

**Level:** 🔵 Hero · **Time:** 4h · **App:** Toolshop API · **Deliverable:** `framework/api/toolshop_client.py`, `framework/data/factories.py`, `tests/api/toolshop/`

#### 📋 Task
Use Swagger (`/api/documentation`) to discover endpoints, then:
1. **Login** (`POST /users/login`) returns a bearer token. `GET /users/me` returns the right user. Decode the JWT and assert the claims you find (e.g. expiry in the future).
2. **Pagination invariants** on `GET /products`: the items across all pages equal `total`, there are **no duplicates** across pages, and a page beyond the last returns empty or a defined error.
3. **Filtering and search:** every result matches the filter (category, brand, or search term).
4. **Factories:** `make_user()` / `make_brand()` with Faker plus a unique suffix, and cleanup where the API allows it.
5. **RBAC:** for one admin-only operation, assert admin succeeds and customer and anonymous are rejected (discover the codes, and flag inconsistencies).

**Done when**
- [ ] Tests pass against **hosted** *and* **self-hosted** Toolshop (`--env public` / `--env local`)
- [ ] No test depends on product names or counts that could change; assert invariants instead

#### 📘 User guide

**Concepts**
- **Bearer token / JWT:** `header.payload.signature`, base64url-encoded JSON with claims like `sub`, `exp` and `role`. Anyone can *decode* it, but only the server can *verify* it.
- **Pagination styles:** page/offset (`?page=2`) and cursor (`?after=abc`). Metadata: `total`, `per_page`, `last_page`.
- **Invariants:** properties that must always hold regardless of data (all results match the filter, and so on).
- **Factories + Faker:** generate realistic, unique data on demand.

**Deep dive**

**Test invariants, not snapshots.** Shared demo data changes. Instead of "page 1 has these 9 products", assert *properties*: every item has required fields, pages don't overlap, the union's size equals `total`, and sorting holds. This is how you write tests that survive data changes.

**Pagination bugs to hunt:** duplicates or missing items at page boundaries (unstable sort!), `total` disagreeing with the actual count, page `0`/negative/non-numeric pages returning 500, oversized `per_page` not capped.

**Filter testing:** positive (all results match), negative (non-matching items excluded, checked by creating one), empty results (a valid filter with no matches → empty list, not an error), invalid filter values (→ 4xx, not 500), and combined filters (AND semantics).

**Data factories:** `Faker` makes realistic data. Add a **unique suffix** (uuid or worker ID, P07) so parallel tests never collide. Seed Faker (`Faker.seed(n)`) when you want reproducible runs. Cleanup options, from best to worst: delete via API → use a disposable environment → mark with a prefix and sweep periodically.

**Examples**

🟢 **Low: login and "who am I"**
```python
def test_customer_can_login_and_see_profile(http, settings):
    api = settings.toolshop_api_url
    r = http.post(f"{api}/users/login", json={"email": "customer@practicesoftwaretesting.com",
                                              "password": "welcome01"}, timeout=10)
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    me = http.get(f"{api}/users/me", headers={"Authorization": f"Bearer {token}"}, timeout=10)
    assert me.status_code == 200, me.text
    assert me.json()["email"] == "customer@practicesoftwaretesting.com"
```

🔵 **Medium: role tokens, pagination invariants and JWT claims**
```python
# tests/api/toolshop/conftest.py
import pytest

USERS = {"admin": ("admin@practicesoftwaretesting.com", "welcome01"),
         "customer": ("customer@practicesoftwaretesting.com", "welcome01")}

@pytest.fixture(scope="session")
def tokens(http, settings) -> dict[str, str | None]:
    out: dict[str, str | None] = {"anonymous": None}
    for role, (email, password) in USERS.items():
        r = http.post(f"{settings.toolshop_api_url}/users/login",
                      json={"email": email, "password": password}, timeout=10)
        r.raise_for_status()
        out[role] = r.json()["access_token"]
    return out

@pytest.fixture(scope="session")
def admin_token(tokens):
    return tokens["admin"]

@pytest.fixture(scope="session")
def customer_token(tokens):
    return tokens["customer"]
```
```python
# tests/api/toolshop/test_products.py
import base64, json, time
from framework.api.pagination import iter_products      # P02-07

def jwt_claims(token: str) -> dict:
    payload = token.split(".")[1]
    return json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))

def test_token_expires_in_future(customer_token):
    assert jwt_claims(customer_token)["exp"] > time.time()

def test_pagination_has_no_gaps_or_duplicates(http, settings):
    api = settings.toolshop_api_url
    total = http.get(f"{api}/products", timeout=10).json()["total"]
    ids = [p["id"] for p in iter_products(http, api)]
    assert len(ids) == len(set(ids)), "duplicate products across pages"
    assert len(ids) == total, f"walked {len(ids)} items but API reports total={total}"
```

🟣 **High/Complex: factories, admin CRUD with cleanup and an RBAC matrix**
```python
# framework/data/factories.py
import uuid
from faker import Faker

fake = Faker()

def unique(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def brand_payload(**overrides) -> dict:
    name = unique("qe-brand")
    return {"name": name, "slug": name} | overrides

def user_payload(**overrides) -> dict:
    return {
        "first_name": fake.first_name(), "last_name": fake.last_name(),
        "email": f"{unique('qe')}@example.com", "password": "Sup3r$ecret!2026",
        "dob": "1990-01-01", "phone": fake.msisdn()[:10],
        "address": {"street": fake.street_address(), "city": fake.city(), "state": fake.state(),
                    "country": "NL", "postal_code": "1234AB"},
    } | overrides
```
> The payload fields must match Toolshop's current register-user schema, so **check Swagger** and adapt (older versions use flat address fields). Fixing a factory from the spec is part of the task.

```python
# tests/api/toolshop/test_brands_rbac.py
import pytest
from framework.data.factories import brand_payload

@pytest.fixture
def created_brands(http, settings, admin_token):
    ids = []
    yield ids
    for brand_id in ids:
        http.delete(f"{settings.toolshop_api_url}/brands/{brand_id}",
                    headers={"Authorization": f"Bearer {admin_token}"}, timeout=10)

@pytest.mark.parametrize("role, allowed", [("admin", True), ("customer", False), ("anonymous", False)])
def test_create_brand_permissions(http, settings, tokens, created_brands, role, allowed):
    headers = {"Authorization": f"Bearer {tokens[role]}"} if tokens.get(role) else {}
    r = http.post(f"{settings.toolshop_api_url}/brands", json=brand_payload(), headers=headers, timeout=10)
    if r.status_code in (200, 201):
        created_brands.append(r.json()["id"])
    if allowed:
        assert r.status_code in (200, 201), r.text
    else:
        assert r.status_code in (401, 403), f"{role} should be denied but got {r.status_code}: {r.text[:200]}"
```
If a role that *should* be denied succeeds, you've found an authorization bug, or learned that the endpoint is public in this version. Either way, document it.

#### 🎤 Interview Q&A

<details><summary><b>[H] What is a JWT, and what would you test around it?</b></summary>

A signed token (`header.payload.signature`) carrying claims such as subject, role and expiry. Tests: a valid token grants access; an expired token is rejected; a tampered payload (edit the claim, keep the signature) is rejected; the `alg: none` trick is rejected; the token doesn't contain sensitive data (it's only encoded, not encrypted); role claims match server-side authorization; logout/revocation behaves as specified.
</details>

<details><summary><b>[H] How do you test pagination?</b></summary>

Invariants: the union of all pages equals `total`, with no duplicates or gaps (watch unstable sort order), page size is honoured and capped, and the first, last and beyond-last pages behave as specified. Invalid page parameters (0, negative, text) return 4xx and never 500. Sort order holds across page boundaries. Also test consistency when data changes between page fetches, if the API promises that.
</details>

<details><summary><b>[H] How do you test search and filter endpoints?</b></summary>

Create known data, then verify that every result matches the criteria, known matches are included, known non-matches are excluded, an empty match returns an empty list, invalid values return 4xx, combinations use the right logic (AND/OR), and case/partial matching follows the spec. Assert invariants rather than exact counts on shared data.
</details>

<details><summary><b>[SH] How do you keep API tests independent of existing environment data?</b></summary>

Each test creates what it needs via factories (unique suffixes for parallel safety) and cleans up. Assertions use invariants rather than hard-coded counts. Reference data (roles, product catalogue) comes from a known seed. For destructive or global tests, use isolated environments (containers, P08). Tag and sweep leftovers periodically.
</details>

<details><summary><b>[SH] How do you systematically test authorization (RBAC) across an API?</b></summary>

Build a roles × operations matrix with expected outcomes (with the product owner or security team), obtain tokens per role in fixtures, generate parametrized tests from the matrix, include ownership checks (IDOR: user B accessing user A's resources), run it on every auth-related change, and treat unexpected "allowed" results as high-severity bugs.
</details>

#### 🤖 AI assist
- Give AI the Swagger JSON of *one* endpoint and ask it to generate the pydantic model and 8 test ideas. Then check both against real responses.

---

### P04-08 · Contract testing and API resilience

**Level:** 🟣 Super Hero · **Time:** 5h · **App:** Petstore v3 (self-hosted), Toolshop specs · **Deliverable:** `tests/contract/`, `scripts/spec_diff.py`, `docs/contract-testing.md`

#### 📋 Task
1. **Spec coverage:** load the Petstore OpenAPI spec, list all operations, and report which ones your tests call.
2. **Property-based conformance:** run **Schemathesis** against *self-hosted* Petstore (`docker run -p 8080:8080 swaggerapi/petstore3:unstable`) for GET operations. Record failures and classify each as a spec bug or an implementation bug.
3. **Breaking-change detection:** fetch the OpenAPI JSON of two Toolshop sprint versions (find the spec URL via the Swagger UI's network tab), then write `scripts/spec_diff.py` to report removed paths/methods and removed or retyped response fields. Compare with `oasdiff`.
4. **Resilience:** add an `X-Request-ID` header (test node ID + uuid) to every client request, and write `docs/contract-testing.md` explaining schema-based vs consumer-driven contracts (Pact) and when you'd use each.

**Done when**
- [ ] A spec-coverage report exists (e.g. "12/19 operations covered")
- [ ] At least one real finding (or a documented "none found") from Schemathesis
- [ ] `spec_diff.py` lists differences between two versions

#### 📘 User guide

**Concepts**
- **API contract:** the agreed request/response shape and behaviour, often written as an **OpenAPI** spec.
- **Schema/provider contract testing:** verify that the implementation matches the spec.
- **Consumer-driven contracts (Pact):** each consumer records what it *actually uses*, and the provider verifies against all consumers' expectations.
- **Breaking change:** removing an endpoint or field, changing a type, adding a *required* request field, narrowing an enum. **Non-breaking:** adding optional fields or endpoints.
- **Property-based testing:** generate many inputs from a description (the spec) and check properties (no 5xx, response matches schema).

**Deep dive**

**Why contract tests?** In microservices, end-to-end environments are slow and flaky. Contract tests catch integration breaks **at PR time, per service**, without deploying everything. The spec becomes an executable agreement.

**Schema-based vs consumer-driven:**
| | Schema/provider (OpenAPI) | Consumer-driven (Pact) |
|---|---|---|
| Source of truth | Provider's spec | Consumers' recorded expectations |
| Catches | Implementation ≠ spec | Provider change breaks a *real* consumer |
| Blind spot | Spec may not reflect real usage | Needs consumer teams to participate |
| Good for | Public APIs, many unknown consumers | Internal microservices with known consumers |

**Schemathesis** reads the spec, generates valid *and* edge-case requests (via Hypothesis), and checks responses: no 5xx, status codes documented, bodies conform to schemas, content types match. It finds bugs humans don't think of, such as an unexpected `null`, huge integers, or odd unicode.

**Breaking-change gates:** run a spec diff (e.g. `oasdiff breaking old.json new.json`) in the provider's CI. Breaking changes require a version bump or explicit approval.

**Correlation IDs:** send a unique `X-Request-ID` per test so a failing test can be matched to server logs and traces. It's cheap, and it pays off in every triage session.

**Examples**

🟢 **Low: spec coverage report**
```python
# tests/contract/test_spec_coverage.py
import requests

SPEC_URL = "http://localhost:8080/api/v3/openapi.json"        # self-hosted Petstore
TESTED = {("GET", "/pet/{petId}"), ("POST", "/pet"), ("GET", "/pet/findByStatus")}   # keep in sync with tests

def test_report_spec_coverage():
    spec = requests.get(SPEC_URL, timeout=10).json()
    ops = {(m.upper(), path) for path, item in spec["paths"].items()
           for m in item if m in {"get", "post", "put", "patch", "delete"}}
    missing = sorted(ops - TESTED)
    print(f"\nSpec coverage: {len(ops & TESTED)}/{len(ops)} operations")
    print("Not covered:\n  " + "\n  ".join(f"{m} {p}" for m, p in missing))
    assert TESTED <= ops, f"tests call undocumented operations: {TESTED - ops}"
```

🔵 **Medium: property-based conformance with Schemathesis**
```python
# tests/contract/test_petstore_conformance.py      (uv add --dev schemathesis)
import pytest
import schemathesis

schema = schemathesis.openapi.from_url("http://localhost:8080/api/v3/openapi.json")   # v3.x: schemathesis.from_uri(...)

@schema.parametrize()
def test_petstore_conforms_to_spec(case):
    if case.method != "GET":
        pytest.skip("read-only run: don't mutate shared data")
    case.call_and_validate()          # checks: no 5xx, documented status, schema-conformant body
```
> Schemathesis's API evolves, so check its docs for your installed version. Run it only against *self-hosted* services: it sends many requests.

🟣 **High/Complex: a breaking-change detector between API versions**
```python
# scripts/spec_diff.py: usage: python scripts/spec_diff.py old.json new.json
import json, sys

METHODS = {"get", "post", "put", "patch", "delete"}

def operations(spec: dict) -> dict[tuple[str, str], dict]:
    return {(m.upper(), path): op for path, item in spec.get("paths", {}).items()
            for m, op in item.items() if m in METHODS}

def props(spec: dict, schema: dict) -> dict[str, str]:
    """Top-level response properties → type, following local $refs like #/components/schemas/Product."""
    if "$ref" in schema:
        name = schema["$ref"].split("/")[-1]
        schema = spec["components"]["schemas"][name]
    if schema.get("type") == "array":
        return props(spec, schema.get("items", {}))
    return {k: v.get("type", "ref") for k, v in schema.get("properties", {}).items()}

def success_schema(op: dict) -> dict:
    for code in ("200", "201"):
        content = op.get("responses", {}).get(code, {}).get("content", {})
        if "application/json" in content:
            return content["application/json"].get("schema", {})
    return {}

def main(old_path: str, new_path: str) -> int:
    old, new = (json.load(open(p)) for p in (old_path, new_path))
    old_ops, new_ops = operations(old), operations(new)
    breaking = [f"REMOVED operation {m} {p}" for (m, p) in sorted(old_ops.keys() - new_ops.keys())]
    for key in sorted(old_ops.keys() & new_ops.keys()):
        before = props(old, success_schema(old_ops[key]))
        after = props(new, success_schema(new_ops[key]))
        for field in sorted(before.keys() - after.keys()):
            breaking.append(f"REMOVED field '{field}' from {key[0]} {key[1]} response")
        for field in sorted(before.keys() & after.keys()):
            if before[field] != after[field]:
                breaking.append(f"RETYPED '{field}' {before[field]}→{after[field]} in {key[0]} {key[1]}")
    added = sorted(new_ops.keys() - old_ops.keys())
    print("\n".join(breaking) or "No breaking changes detected")
    print(f"(+{len(added)} new operations)")
    return 1 if breaking else 0

if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:3]))
```
```bash
# Cross-check with a dedicated tool
docker run --rm -v "$PWD:/specs" tufin/oasdiff breaking /specs/old.json /specs/new.json
```
Use the script's exit code as a CI gate on the provider side (P09).

#### 🎤 Interview Q&A

<details><summary><b>[H] What is contract testing and why use it?</b></summary>

Verifying that a provider and its consumers agree on the API's shape and behaviour, without running the full system. It catches integration breaks early (at PR time) and cheaply, reduces reliance on slow, flaky end-to-end environments, and documents the agreement as executable checks.
</details>

<details><summary><b>[SH] Schema-based vs consumer-driven contract testing?</b></summary>

Schema-based validates the provider against its OpenAPI spec. It's simple, suits public APIs, but only proves conformance to the spec. Consumer-driven (Pact) has each consumer publish the interactions it relies on, and the provider verifies all of them, so it proves real consumers won't break. It needs cross-team adoption and a broker. Many organisations use both: spec validation plus Pact for critical internal consumers.
</details>

<details><summary><b>[SH] Which API changes are breaking?</b></summary>

Removing or renaming endpoints or fields, changing types or formats, making optional request fields required, adding new required request fields, narrowing enums or validation ranges, changing auth requirements, and changing status-code semantics. Usually non-breaking: adding optional request fields, new response fields (if consumers are tolerant readers), new endpoints. Gate breaking changes with a spec diff in CI and version the API.
</details>

<details><summary><b>[SH] What is property-based API testing, and when does it beat example-based tests?</b></summary>

A tool (e.g. Schemathesis with Hypothesis) generates many requests from the schema, including edge cases, and checks universal properties: no 5xx, responses conform to the schema, documented status codes. It beats hand-written examples at finding unexpected input-handling bugs and spec drift. It complements, rather than replaces, business-rule tests, and should target isolated environments.
</details>

<details><summary><b>[H] What is a correlation ID and why add it in tests?</b></summary>

A unique ID sent with each request (e.g. `X-Request-ID`) that services propagate into logs and traces. Including the test name in it lets you jump from a failing test straight to the exact backend logs, which dramatically speeds up triage, especially across microservices.
</details>

<details><summary><b>[SH] How do you test a service whose dependency is unavailable or expensive?</b></summary>

Contract-test the boundary, and use service virtualisation or mocks (WireMock, Prism from the OpenAPI spec, or `responses`/`requests-mock` at the client level) to simulate normal, slow, error and malformed responses. Verify resilience behaviours (timeouts, retries, circuit breaker, fallbacks), and run a small number of real integration tests in a shared environment.
</details>

#### 🤖 AI assist
- Give AI two spec versions and ask for a breaking-change summary, then compare it with your script's and `oasdiff`'s output. Note where AI missed or invented changes.

---

## 🏁 Phase checkpoint: P04

**Live-coding self-test (40 min, no AI):** from an empty folder, write a Restful-Booker test suite with a session fixture for the token, a factory fixture with cleanup, one CRUD lifecycle test and a 4-case negative matrix.

**AI mock interviewer prompt**
```text
Act as an interviewer for an API test automation role (Python + requests + pytest).
Ask about HTTP semantics, status codes, auth, negative testing, framework design,
schema validation and contract testing. 8 questions, one at a time, then one
design question: "design an API test framework for 20 microservices".
Score each 1-5 and tell me what a senior answer would add.
```
Record your results in `interview-notes/P04.md`.
