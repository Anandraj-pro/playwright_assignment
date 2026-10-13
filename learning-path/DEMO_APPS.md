# Demo Applications: UI, API and Sample Databases

Every task in this learning path runs against **real, free, open-source demo applications**. These are the same apps interviewers use for take-home assignments and live-coding rounds, so practising on them is interview practice.

> ✅ Verified on 2026-09-23. Demo apps change over time. If a URL, credential or port differs, trust the app's own README, update this file in a PR, and treat it as practice in "the environment changed" debugging.

---

## 1. At a glance

| # | App | Layer(s) | Hosted (zero setup) | Self-host (Docker) | Primary phases |
|---|---|---|---|---|---|
| 1 | **Practice Software Testing, "Toolshop"** | UI + REST API + MySQL | ✅ | ✅ `docker compose` | P01, P04, P05, P06, P08, P09, P11, P13 |
| 2 | **SauceDemo** | UI | ✅ | ❌ (hosted only) | P00, P01, P02, P03, P05, P10 |
| 3 | **The Internet** | UI (edge cases) | ✅ | ✅ Docker image | P04, P05, P08 |
| 4 | **Restful-Booker** | REST API (+ MongoDB inside) | ✅ | ✅ `docker-compose` | P00, P04, P07, P08, P11 |
| 5 | **Swagger Petstore v3** | REST API + OpenAPI spec | ✅ | ✅ Docker image | P04 (contract testing) |
| 6 | **Pagila** | PostgreSQL sample DB | — | ✅ `docker compose` | P06, P07, P09, P12 |
| 7 | **Chinook** | Sample DB (SQLite/Postgres/MySQL…) | — | ✅ file download | P06 (SQL basics) |

**Rule of thumb:** use **hosted** apps while learning (P00–P04), and **self-hosted** apps from P04-06 onward, once you need DB access, parallel load, CI, load tests or security tests. Public demo apps are shared by thousands of people, so be polite: don't hammer them with `-n 16`, and **never** point load tests or attack payloads at them (P11).

---

## 2. Toolshop (Practice Software Testing): the main full-stack app

A realistic e-commerce tool store built for testers: Angular UI, Laravel REST API with Swagger, a MySQL database, an email catcher, and several **sprint versions** plus a **with-bugs** version. It is the only app here where you get **UI + API + DB** together, so most "senior" tasks use it.

| Item | Value |
|---|---|
| Source | https://github.com/testsmith-io/practice-software-testing |
| Hosted UI | https://practicesoftwaretesting.com |
| Hosted API | https://api.practicesoftwaretesting.com |
| Sprint versions | `https://v1.practicesoftwaretesting.com` … `v5` (each has a matching API host; see the repo README) |
| Bug-hunt version | https://with-bugs.practicesoftwaretesting.com |
| API docs (self-hosted) | http://localhost:8091/api/documentation (Swagger) |

**Test users**

| Email | Password | Role |
|---|---|---|
| `admin@practicesoftwaretesting.com` | `welcome01` | admin |
| `customer@practicesoftwaretesting.com` | `welcome01` | customer |
| `customer2@practicesoftwaretesting.com` | `welcome01` | customer |
| `customer3@practicesoftwaretesting.com` | `pass123` | customer |

**Self-host**

```bash
git clone https://github.com/testsmith-io/practice-software-testing.git
cd practice-software-testing
# optional: set SPRINT in .env to choose a version (check the folder names in the repo, e.g. sprint5)
docker compose up -d                       # first start can take ~5 minutes
docker exec -it pst-laravel-api-1 php artisan migrate:fresh --seed   # seed / reset DB
```

| Service | URL | Credentials |
|---|---|---|
| Angular UI | http://localhost:4200 | test users above |
| REST API | http://localhost:8091 | test users above |
| Swagger | http://localhost:8091/api/documentation | — |
| phpMyAdmin | http://localhost:8000 | `root` / `root` |
| MailCatcher | http://localhost:1080 | — |

> 🔒 **Shared accounts get locked.** On 2026-09-23 the hosted `customer@practicesoftwaretesting.com` account was locked ("too many failed attempts"), caused by other people's traffic. Use `customer2@…` or `customer3@…`, register your own user in a test, or self-host (where every account is yours).

> 🔎 **DB port:** run `docker compose ps` to see whether the MySQL container publishes a port to your host. If it doesn't, you'll publish one yourself with a `docker-compose.override.yml` (task P06-04 / P08-02). Container names such as `pst-laravel-api-1` can differ, so check `docker ps`.

**Why interviewers like it:** real auth (bearer tokens), pagination, filters, carts, invoices, admin CRUD, email flows, and a deliberately buggy variant.

---

## 3. SauceDemo: the classic UI interview app

| Item | Value |
|---|---|
| URL | https://www.saucedemo.com |
| Password (all users) | `secret_sauce` |
| Test attribute | `data-test` (e.g. `data-test="login-button"`) |

| Username | Behaviour (use it to practise) |
|---|---|
| `standard_user` | Happy path |
| `locked_out_user` | Login is blocked with an error message |
| `problem_user` | Broken images, broken sorting/forms: **bug-hunt practice** |
| `performance_glitch_user` | Slow login: **waiting-strategy practice** |
| `error_user` | Errors on some actions: **negative-path practice** |
| `visual_user` | Visual differences: **visual-check practice** |

Checkout applies **8% tax**, which is handy for cross-checking a Python function (P02) against the UI (P05).

---

## 4. The Internet: every awkward UI pattern in one place

| Item | Value |
|---|---|
| URL | https://the-internet.herokuapp.com |
| Source | https://github.com/saucelabs/the-internet |
| Docker image | `gprestes/the-internet` (Docker Hub). Finding its port yourself with `docker inspect` is part of task P04-05 |

Pages you'll use: Dynamic Loading, Nested Frames, JavaScript Alerts, Multiple Windows, File Upload, File Download, Basic Auth (`admin`/`admin`), Checkboxes, Dropdown, Drag and Drop, Hovers, Sortable Data Tables, Status Codes, Shadow DOM, Key Presses.

---

## 5. Restful-Booker: the classic API interview app

| Item | Value |
|---|---|
| Hosted API | https://restful-booker.herokuapp.com |
| API docs | https://restful-booker.herokuapp.com/apidoc/index.html |
| Source | https://github.com/mwinteringham/restful-booker |
| Auth | `POST /auth` with `{"username": "admin", "password": "password123"}` returns `{"token": "..."}` |

| Endpoint | Purpose |
|---|---|
| `GET /ping` | Health check (read the docs for the status code; it's a classic "gotcha") |
| `GET /booking` | List IDs, filter with `?firstname=&lastname=` or `?checkin=&checkout=` |
| `GET /booking/{id}` | Get one booking |
| `POST /booking` | Create (no auth) |
| `PUT /booking/{id}` / `PATCH` | Update. Needs `Cookie: token=<token>` or Basic auth |
| `DELETE /booking/{id}` | Delete. Needs auth |

**Self-host** (MongoDB runs behind it):

```bash
git clone https://github.com/mwinteringham/restful-booker.git
cd restful-booker
docker compose build && docker compose up -d     # API on http://localhost:3001
```

> ⚠️ The hosted instance is **shared and can be reset or changed by anyone**. Never assume a booking you didn't create exists. This is exactly why tests must create their own data.

---

## 6. Swagger Petstore v3: OpenAPI and contract testing

| Item | Value |
|---|---|
| Hosted | https://petstore3.swagger.io |
| OpenAPI spec (hosted) | https://petstore3.swagger.io/api/v3/openapi.json |
| Source | https://github.com/swagger-api/swagger-petstore |

```bash
docker run --name petstore3 -d -p 8080:8080 swaggerapi/petstore3:unstable
# UI: http://localhost:8080   Spec: http://localhost:8080/api/v3/openapi.json
```

---

## 7. Pagila: PostgreSQL sample DB (DVD rental)

| Item | Value |
|---|---|
| Source | https://github.com/devrimgunduz/pagila |
| Engine | PostgreSQL (recent releases require **PostgreSQL 18+**; check the README) |
| Main tables | `actor`, `address`, `category`, `city`, `country`, `customer`, `film`, `film_actor`, `film_category`, `inventory`, `language`, `payment` (partitioned), `rental`, `staff`, `store` |

```bash
git clone https://github.com/devrimgunduz/pagila.git
cd pagila
docker compose up -d
docker exec -it pagila psql -U postgres -c '\c pagila' -c '\dt'
```

Manual load into any Postgres: create a `pagila` database, then run `pagila-schema.sql` followed by `pagila-data.sql`.

**Why:** rich relationships (customer → rental → inventory → film → category → payment) make it ideal for JOIN, CTE and window-function questions, which dominate SQL interview rounds.

---

## 8. Chinook: zero-setup SQL practice

| Item | Value |
|---|---|
| Source | https://github.com/lerocha/chinook-database |
| Engines | SQLite, PostgreSQL, MySQL, SQL Server, Oracle, DB2 |
| Get it | Download the SQLite asset (e.g. `Chinook_Sqlite.sqlite`) from the **latest release** |
| Tables (SQLite naming) | `Artist`, `Album`, `Track`, `Genre`, `MediaType`, `Playlist`, `PlaylistTrack`, `Customer`, `Employee`, `Invoice`, `InvoiceLine` |

**Why:** Python ships with `sqlite3`, so you can write SQL and Python DB tests on day one with no Docker. Column naming differs between vendor scripts (PascalCase in SQLite), so check the schema first.

---

## 9. Helper tools (free)

| Tool | Use |
|---|---|
| **Bruno** or **Postman** | Manual API exploration before automating (P04-01) |
| **DBeaver** | Universal DB GUI for MySQL, Postgres and SQLite (P06) |
| **Playwright codegen / Inspector** | `playwright codegen <url>` to discover locators (P05) |
| **Playwright Trace Viewer** | `playwright show-trace trace.zip` or https://trace.playwright.dev (P00-00, P05, P09) |
| **Locust** | Load and performance tests in Python: `uv add --dev locust` (P11-01) |
| **axe-core** | Accessibility rules engine, injected into pages by your tests (P11-02) |
| **VoiceOver / NVDA** | Screen readers for manual accessibility checks: VoiceOver is built into macOS (Cmd+F5); NVDA is free for Windows (P11-02) |
| **OWASP ZAP** | Passive security baseline scans: `ghcr.io/zaproxy/zaproxy:stable` (P11-04) |
| **Selenium** | Only to *read and run* the legacy suite you migrate: `uv run --with selenium python -m pytest legacy-suite/selenium` (P05-08) |

---

## 10. Which app for which skill

| Skill | 🟢 Zero | 🔵 Hero | 🟣 Super Hero |
|---|---|---|---|
| First automation | SauceDemo login + Restful-Booker ping (P00-00) | — | — |
| Test design | Toolshop registration rules, SauceDemo checkout states | Toolshop story review and risk | Pairwise and traceability generated from tests |
| Python | SauceDemo product data | Toolshop models | Framework packaging |
| pytest | SauceDemo users CSV | Fixtures over Restful-Booker | Plugins/hooks across all apps |
| API (requests) | Restful-Booker | Toolshop API | Petstore/Toolshop OpenAPI contracts |
| UI (Playwright) | SauceDemo | The Internet + Toolshop; rescuing `legacy-suite/` | Toolshop hybrid, cross-browser, visual; Selenium migration |
| DB | Chinook (SQLite) | Pagila (Postgres) | Toolshop MySQL API↔DB consistency |
| Parallel | Restful-Booker | SauceDemo + Toolshop | Sharded suite on self-hosted stack |
| Docker | The Internet image | Restful-Booker + Pagila compose | Full stack + test runner compose |
| CI | Lint + unit (from week 2) | Smoke on hosted apps | Full stack in CI with gates |
| Non-functional | — | Locust on Restful-Booker; axe on Toolshop; authz matrix on Toolshop API | Performance, ZAP and accessibility gates in nightly CI |
| AI | Prompts on SauceDemo bugs | Playwright MCP on Toolshop | Triage agent on Toolshop with-bugs |
