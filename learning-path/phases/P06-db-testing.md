# P06: Database Testing

> **Goal:** write SQL that passes interview rounds, build a Python DB layer, verify data integrity, prove API/UI actions persist correctly, and manage test data like a senior.
> **Apps:** Chinook (SQLite), Pagila (PostgreSQL), Toolshop (MySQL, self-hosted). **Prerequisites:** P03, P04-04; P04-05 and P04-06 (Docker as a user). **Time:** ~23 h.

| ID | Task | Level | Time |
|---|---|---|---|
| P06-01 | SQL fundamentals on Chinook (SQLite) | 🟢 | 4h |
| P06-02 | Interview SQL on Pagila (PostgreSQL in Docker) | 🔵 | 5h |
| P06-03 | Python DB layer and data-integrity tests | 🔵 | 4h |
| P06-04 | API/UI → DB consistency on self-hosted Toolshop | 🔵 | 5h |
| P06-05 | Test data strategies, ephemeral DBs, schema and ETL checks | 🟣 | 5h |

---

### P06-01 · SQL fundamentals on Chinook (SQLite)

**Level:** 🟢 Zero · **Time:** 4h · **App:** Chinook · **Deliverable:** `sql/01_chinook_basics.sql`, `tests/db/test_chinook_queries.py`

#### 📋 Task
1. Download the Chinook SQLite file from the latest release (see DEMO_APPS.md) into `framework/data/chinook.sqlite`, or git-ignore it and download it in a fixture.
2. Explore it with DBeaver or `sqlite3 chinook.sqlite` (`.tables`, `.schema Track`).
3. Write **20 queries** in `sql/01_chinook_basics.sql`, each with a comment stating the question: filtering, sorting, `LIKE`/`IN`/`BETWEEN`, `NULL` handling, aggregates, `GROUP BY`/`HAVING`, `INNER` and `LEFT JOIN`, a subquery, `DISTINCT`.
4. Write pytest tests that run key queries through Python's built-in `sqlite3` and assert the results. This is your first **DB test**.

**Done when**
- [ ] 20 queries with correct results, verified by you
- [ ] ≥5 of them covered by pytest tests using **bound parameters** (`?`)

#### 📘 User guide

**Concepts**
- **Table/row/column**, **primary key** (unique row ID), **foreign key** (a reference to another table's key).
- **SELECT anatomy:** `SELECT cols FROM t JOIN … WHERE … GROUP BY … HAVING … ORDER BY … LIMIT …`.
- **Joins:** `INNER` (matches only), `LEFT` (all left rows plus matches or NULL), `RIGHT`, `FULL`, `CROSS`, self-join.
- **Aggregates:** `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, usually with `GROUP BY`.
- **NULL:** "unknown". Compare with `IS NULL`, never `= NULL`.

**Deep dive**

**Logical execution order** explains most SQL confusion:
```text
FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT
```
That's why a `SELECT` alias can't be used in `WHERE` (it doesn't exist yet), and why `HAVING` (which filters groups) is needed for aggregate conditions.

**NULL and three-valued logic:** `NULL = NULL` is *unknown*, not true. `COUNT(*)` counts rows, but `COUNT(col)` skips NULLs. `AVG` ignores NULLs. These cause real reporting bugs and are favourite interview traps.

**The LEFT JOIN trap:** `LEFT JOIN b ... WHERE b.x = 1` filters out the NULL rows, silently turning it into an INNER JOIN. Put right-table conditions in the `ON` clause if you want to keep unmatched left rows.

**SQL for testers:** you'll use SQL to (1) verify that what the app stored is correct, (2) find test data ("a customer with no orders"), (3) set up or clean data, and (4) investigate bugs. Readable, correct SQL is a core QE skill.

**Examples**

🟢 **Low: filter, sort and limit**
```sql
-- Q1: 5 longest tracks in the 'Rock' genre, in minutes
SELECT t.Name, ROUND(t.Milliseconds / 60000.0, 2) AS minutes
FROM Track t
JOIN Genre g ON g.GenreId = t.GenreId
WHERE g.Name = 'Rock'
ORDER BY t.Milliseconds DESC
LIMIT 5;
```

🔵 **Medium: GROUP BY/HAVING and LEFT JOIN**
```sql
-- Q2: countries with more than $100 total sales, highest first
SELECT BillingCountry, ROUND(SUM(Total), 2) AS revenue, COUNT(*) AS invoices
FROM Invoice
GROUP BY BillingCountry
HAVING SUM(Total) > 100
ORDER BY revenue DESC;

-- Q3: artists that have NO albums (anti-join with LEFT JOIN)
SELECT ar.ArtistId, ar.Name
FROM Artist ar
LEFT JOIN Album al ON al.ArtistId = ar.ArtistId
WHERE al.AlbumId IS NULL;
```

🟣 **High/Complex: SQL tested from pytest with bound parameters**
```python
# tests/db/test_chinook_queries.py
import sqlite3
from pathlib import Path
import pytest

DB = Path(__file__).resolve().parents[2] / "framework" / "data" / "chinook.sqlite"

@pytest.fixture(scope="module")
def chinook():
    if not DB.exists():
        pytest.skip(f"download Chinook SQLite to {DB}")
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)     # read-only: tests can't damage it
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

def test_every_invoice_total_equals_sum_of_lines(chinook):
    mismatches = chinook.execute("""
        SELECT i.InvoiceId, i.Total, ROUND(SUM(il.UnitPrice * il.Quantity), 2) AS line_sum
        FROM Invoice i JOIN InvoiceLine il ON il.InvoiceId = i.InvoiceId
        GROUP BY i.InvoiceId, i.Total
        HAVING ROUND(i.Total, 2) <> ROUND(SUM(il.UnitPrice * il.Quantity), 2)
    """).fetchall()
    assert not mismatches, [dict(r) for r in mismatches[:5]]

@pytest.mark.parametrize("country", ["USA", "Canada", "Brazil"])
def test_customers_above_country_average_spend(chinook, country):
    rows = chinook.execute("""
        SELECT c.CustomerId, SUM(i.Total) AS spend
        FROM Customer c JOIN Invoice i ON i.CustomerId = c.CustomerId
        WHERE c.Country = ?                                     -- bound parameter, never f-string
        GROUP BY c.CustomerId
        HAVING SUM(i.Total) > (SELECT AVG(t.s) FROM (SELECT SUM(Total) AS s FROM Invoice i2
                               JOIN Customer c2 ON c2.CustomerId = i2.CustomerId
                               WHERE c2.Country = ? GROUP BY c2.CustomerId) t)
    """, (country, country)).fetchall()
    assert all(r["spend"] > 0 for r in rows)
```
The first test is a **real data-integrity check** (header total = sum of lines). You'll use the same idea on Toolshop invoices in P06-04.

#### 🎤 Interview Q&A

<details><summary><b>[Z] WHERE vs HAVING?</b></summary>

`WHERE` filters rows *before* grouping and can't use aggregates. `HAVING` filters *groups* after `GROUP BY` and can use aggregates (`HAVING SUM(total) > 100`).
</details>

<details><summary><b>[Z] Explain INNER vs LEFT JOIN with an example.</b></summary>

INNER returns only rows with matches in both tables (customers who have invoices). LEFT returns all left rows, plus matching right rows or NULLs (all customers, with invoice data where it exists). A LEFT JOIN plus `WHERE right.id IS NULL` finds rows *without* a match (customers with no invoices).
</details>

<details><summary><b>[Z] <code>COUNT(*)</code> vs <code>COUNT(column)</code>?</b></summary>

`COUNT(*)` counts rows. `COUNT(column)` counts non-NULL values in that column. `COUNT(DISTINCT column)` counts unique non-NULL values.
</details>

<details><summary><b>[Z] DELETE vs TRUNCATE vs DROP?</b></summary>

`DELETE` removes rows (optionally filtered with WHERE), is logged per row, fires triggers and can be rolled back. `TRUNCATE` removes all rows quickly and resets storage (and often identity counters). `DROP` removes the table itself, structure and all. Transactional behaviour of TRUNCATE varies by database.
</details>

<details><summary><b>[H] Why doesn't <code>WHERE col = NULL</code> work?</b></summary>

NULL means unknown, so any comparison with NULL yields unknown (not true) and the row is filtered out. Use `IS NULL` / `IS NOT NULL`. `NOT IN` with a subquery containing a NULL returns no rows at all, a classic bug.
</details>

<details><summary><b>[H] Why can't I use a SELECT alias in WHERE?</b></summary>

Because of logical execution order: `WHERE` is evaluated before `SELECT`, so the alias doesn't exist yet. Repeat the expression, or wrap the query in a subquery or CTE. (`ORDER BY` can use aliases because it runs after `SELECT`.)
</details>

#### 🤖 AI assist
- Ask AI for *interview-style questions* on the Chinook schema (not answers). Solve them, then ask AI to review your SQL for NULL and join pitfalls.

---

### P06-02 · Interview SQL on Pagila (PostgreSQL in Docker)

**Level:** 🔵 Hero · **Time:** 5h · **App:** Pagila · **Deliverable:** `sql/02_pagila_interview.sql`, `docs/pagila-erd.png`

#### 📋 Task
1. Run Pagila with Docker (see DEMO_APPS.md), connect with `psql` and DBeaver, and export an ERD image.
2. Solve these **20 interview classics** (comment the question above each query):

| # | Question | # | Question |
|---|---|---|---|
| 1 | Top 5 customers by total payments | 11 | Customers who rented in every category (relational division) |
| 2 | Second-highest payment amount (2 ways) | 12 | Month-over-month revenue with % change (`LAG`) |
| 3 | Duplicate customer emails (if any) | 13 | Running total of payments per customer |
| 4 | Films never rented (anti-join) | 14 | Days with **zero** rentals (`generate_series`) |
| 5 | Top 3 films per category by rentals | 15 | Average rental duration per category |
| 6 | Rank customers by spend (`RANK` vs `DENSE_RANK` vs `ROW_NUMBER`) | 16 | Overdue rentals (returned later than `rental_duration`) |
| 7 | Actors who appeared in > 30 films | 17 | Revenue per store per month (pivot with `FILTER`) |
| 8 | Customers in the same city (self-join) | 18 | First and last rental per customer |
| 9 | Films longer than their category's average | 19 | Top film per rating (`DISTINCT ON`) |
| 10 | Categories with revenue share (%) | 20 | `EXPLAIN ANALYZE` a slow query, add an index, compare |

**Done when**
- [ ] All 20 answered, each in ≤10 minutes on a second attempt
- [ ] You can explain `RANK` vs `DENSE_RANK` vs `ROW_NUMBER` and `NOT IN` vs `NOT EXISTS` without notes

#### 📘 User guide

**Concepts**
- **CTE:** `WITH name AS (...)` gives a named subquery for readability, and can be recursive.
- **Window functions:** `fn() OVER (PARTITION BY … ORDER BY … [frame])` compute across related rows **without collapsing them** (unlike GROUP BY).
- **Ranking:** `ROW_NUMBER` (1,2,3,4), `RANK` (1,2,2,4), `DENSE_RANK` (1,2,2,3).
- **Offsets:** `LAG`/`LEAD` read the previous or next row's value.
- **Set operations:** `UNION` (dedup) vs `UNION ALL` (keep all, faster), `INTERSECT`, `EXCEPT`.
- **Indexes and plans:** `EXPLAIN ANALYZE` shows how the database executes a query.

**Deep dive**

**Window vs GROUP BY:** "total per customer" → GROUP BY (one row per customer). "each payment *and* the customer's running total" → a window function (every payment row kept).

**Top-N per group** is the most common advanced SQL question. The pattern: rank inside a partition in a subquery or CTE, then filter `WHERE rnk <= N` in the outer query (you can't filter on a window function in the same `WHERE`).

**`NOT IN` vs `NOT EXISTS`:** if the subquery returns any NULL, `NOT IN` returns **no rows** (three-valued logic). `NOT EXISTS` is NULL-safe and usually optimises equally well. Prefer it for anti-joins.

**Indexes:** B-tree indexes speed up equality and range lookups, joins and sorts on the indexed columns, but slow down writes and use space. Read `EXPLAIN ANALYZE` output: `Seq Scan` (reads the whole table), `Index Scan` / `Index Only Scan`, `Bitmap Heap Scan`, estimated vs actual rows, and time. On *small* tables the planner may rightly choose a Seq Scan even with an index.

**ACID and isolation** (for testers of concurrent systems): Atomicity, Consistency, Isolation, Durability. Isolation levels (Read Committed, Repeatable Read, Serializable) prevent anomalies such as dirty reads, non-repeatable reads and phantoms, which matter when testing double-booking or overselling.

**Examples**

🟢 **Low: top 5 customers by spend**
```sql
SELECT c.customer_id, c.first_name || ' ' || c.last_name AS customer, SUM(p.amount) AS total_paid
FROM customer c
JOIN payment p ON p.customer_id = c.customer_id
GROUP BY c.customer_id, customer
ORDER BY total_paid DESC
LIMIT 5;
```

🔵 **Medium: top 3 films per category, and the second-highest payment**
```sql
-- Top 3 films per category by rental count
WITH film_rentals AS (
  SELECT fc.category_id, f.title, COUNT(r.rental_id) AS rentals
  FROM film f
  JOIN film_category fc ON fc.film_id = f.film_id
  JOIN inventory i      ON i.film_id = f.film_id
  JOIN rental r         ON r.inventory_id = i.inventory_id
  GROUP BY fc.category_id, f.title
), ranked AS (
  SELECT fr.*, DENSE_RANK() OVER (PARTITION BY category_id ORDER BY rentals DESC) AS rnk
  FROM film_rentals fr
)
SELECT c.name AS category, title, rentals, rnk
FROM ranked JOIN category c ON c.category_id = ranked.category_id
WHERE rnk <= 3
ORDER BY category, rnk, title;

-- Second-highest payment: two ways
SELECT MAX(amount) FROM payment WHERE amount < (SELECT MAX(amount) FROM payment);
SELECT DISTINCT amount FROM payment ORDER BY amount DESC OFFSET 1 LIMIT 1;
```

🟣 **High/Complex: month-over-month growth, zero-activity days and plan analysis**
```sql
-- Month-over-month revenue with % change
WITH monthly AS (
  SELECT date_trunc('month', payment_date)::date AS month, SUM(amount) AS revenue
  FROM payment GROUP BY 1
)
SELECT month, revenue,
       LAG(revenue) OVER (ORDER BY month) AS prev,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month))
             / NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 1) AS pct_change
FROM monthly ORDER BY month;

-- Days with zero rentals inside the data range (gaps analysis)
WITH bounds AS (SELECT MIN(rental_date)::date AS d0, MAX(rental_date)::date AS d1 FROM rental),
days AS (SELECT generate_series(d0, d1, interval '1 day')::date AS day FROM bounds)
SELECT d.day
FROM days d
LEFT JOIN rental r ON r.rental_date::date = d.day
GROUP BY d.day
HAVING COUNT(r.rental_id) = 0
ORDER BY d.day;

-- Index experiment
EXPLAIN ANALYZE SELECT * FROM rental WHERE return_date > now() - interval '30 days';
CREATE INDEX IF NOT EXISTS idx_rental_return_date ON rental (return_date);
EXPLAIN ANALYZE SELECT * FROM rental WHERE return_date > now() - interval '30 days';
DROP INDEX idx_rental_return_date;   -- leave the sample DB as you found it
```
`NULLIF(x, 0)` prevents division-by-zero errors, a small habit that interviewers notice.

#### 🎤 Interview Q&A

<details><summary><b>[Z] How do you find duplicate records?</b></summary>

`SELECT email, COUNT(*) FROM customer GROUP BY email HAVING COUNT(*) > 1;`. To see the full duplicate rows, join back or use `COUNT(*) OVER (PARTITION BY email) > 1` in a subquery.
</details>

<details><summary><b>[H] RANK vs DENSE_RANK vs ROW_NUMBER?</b></summary>

For values 100, 90, 90, 80: `ROW_NUMBER` gives 1,2,3,4 (unique, arbitrary among ties), `RANK` gives 1,2,2,4 (gaps after ties), and `DENSE_RANK` gives 1,2,2,3 (no gaps). For "top N distinct values", use DENSE_RANK. For "exactly N rows", use ROW_NUMBER.
</details>

<details><summary><b>[H] How do you get the top N rows per group?</b></summary>

Compute a window rank partitioned by the group and ordered by the metric in a CTE or subquery, then filter `WHERE rnk <= N` outside. In Postgres, `DISTINCT ON (group)` handles the top-1 case, and `LATERAL` joins are an alternative.
</details>

<details><summary><b>[SH] NOT IN vs NOT EXISTS?</b></summary>

If the subquery can return NULL, `x NOT IN (subquery)` evaluates to unknown for every row and returns nothing. `NOT EXISTS` checks row existence and is NULL-safe. Use NOT EXISTS (or LEFT JOIN … IS NULL) for anti-joins.
</details>

<details><summary><b>[H] What is an index? What are the downsides?</b></summary>

A data structure (usually a B-tree) that lets the database find rows by column values without scanning the table. Downsides: slower inserts, updates and deletes (the index must be maintained), extra storage, and the planner may ignore it for small tables or low-selectivity predicates. Verify with EXPLAIN ANALYZE.
</details>

<details><summary><b>[SH] Explain ACID and why isolation levels matter to a tester.</b></summary>

Atomicity (all or nothing), Consistency (constraints hold), Isolation (concurrent transactions don't see each other's partial work), Durability (committed data survives crashes). Isolation levels trade anomalies for performance. Testers of bookings, inventory or payments must design concurrent tests (two users buying the last item) to catch race conditions like lost updates or double booking that single-threaded tests never reveal.
</details>

#### 🤖 AI assist
- Solve first. Then ask AI for an *alternative* solution to each of your 5 hardest queries and compare plans with `EXPLAIN ANALYZE`. Which is faster, and why?

---

### P06-03 · Python DB layer and data-integrity tests

**Level:** 🔵 Hero · **Time:** 4h · **App:** Pagila · **Deliverable:** `framework/db/engine.py`, `tests/db/pagila/test_integrity.py`

#### 📋 Task
1. `framework/db/engine.py`: build SQLAlchemy engines from settings (`QE_PAGILA_URL`, later `QE_TOOLSHOP_DB_URL`), plus a `fetch_all(engine, sql, **params) -> list[dict]` helper using `text()` and **bound parameters**.
2. A session fixture `pagila` (engine) and tests marked `@pytest.mark.db`.
3. **Integrity rules as data:** a list of SQL queries that must return **zero violating rows**: orphan rentals, negative payments, returns before rentals, films without a language, customers without an address, duplicate active emails.
4. **Constraint tests:** in a transaction that's always rolled back, try to insert a rental for a non-existent customer and assert `IntegrityError`.
5. **SQL-injection demo:** show why an f-string query is dangerous and the bound-parameter version is safe (in a test).

**Done when**
- [ ] `pytest -m db --env local` runs all integrity rules against Pagila
- [ ] No test modifies Pagila permanently

#### 📘 User guide

**Concepts**
- **Driver:** a library that talks the DB protocol (`psycopg` for Postgres, `PyMySQL` for MySQL, `sqlite3` built in).
- **SQLAlchemy Core:** `create_engine(url)`, `engine.connect()`, `text("… :param")`, `conn.execute(stmt, {"param": v})`.
- **Connection URL:** `postgresql+psycopg://user:pass@host:5432/db`, `mysql+pymysql://user:pass@host:3306/db`.
- **Transactions:** `with engine.begin() as conn:` commits on success and rolls back on error. `conn.rollback()` undoes explicitly.
- **Integrity types:** *entity* (PK unique), *referential* (FK valid), *domain* (valid values), *business rules* (checkout ≥ checkin).

**Deep dive**

**Integrity rules as data** is a scalable pattern: each rule is a query that returns *violations*. The test asserts that the result is empty and prints samples. Adding a rule is one line, and non-coders can contribute SQL. It's how data-quality tools work under the hood.

**Constraints vs data:** a constraint (FK, CHECK, UNIQUE) *prevents* bad data; a data check *detects* it. Test both: that critical constraints **exist and fire** (try to violate them in a rolled-back transaction), and that existing data **satisfies** rules the schema doesn't enforce (business rules).

**Why bound parameters:** `f"... WHERE email = '{email}'"` breaks on `O'Brien` and allows injection (`' OR '1'='1`). Bound parameters send values separately from SQL, so the database never interprets them as code. The same principle protects the app, which is why testers probe inputs with quotes.

**Connections in tests:** use one engine per session (it pools connections) and a connection per test. With xdist (P07), each worker process gets its own engine. Keep pool sizes small so 8 workers don't exhaust the database's connection limit.

**Least privilege:** verification queries should use a **read-only** DB role. Only setup and cleanup code gets write access.

**Examples**

🟢 **Low: engine and a first DB test**
```python
# framework/db/engine.py      (uv add sqlalchemy "psycopg[binary]" pymysql)
from functools import lru_cache
from typing import Any
from sqlalchemy import Engine, create_engine, text

@lru_cache
def get_engine(url: str) -> Engine:
    return create_engine(url, pool_size=2, max_overflow=2, pool_pre_ping=True)

def fetch_all(engine: Engine, sql: str, **params: Any) -> list[dict[str, Any]]:
    with engine.connect() as conn:
        return [dict(row._mapping) for row in conn.execute(text(sql), params)]
```
```python
# tests/db/pagila/conftest.py
import pytest
from framework.db.engine import get_engine

@pytest.fixture(scope="session")
def pagila(settings):
    return get_engine(settings.pagila_url)     # add pagila_url to Settings: QE_PAGILA_URL

# tests/db/pagila/test_basics.py
import pytest
from framework.db.engine import fetch_all

@pytest.mark.db
def test_catalogue_is_loaded(pagila):
    assert fetch_all(pagila, "SELECT COUNT(*) AS n FROM film")[0]["n"] > 0
```

🔵 **Medium: integrity rules as data**
```python
# tests/db/pagila/test_integrity.py
import pytest
from framework.db.engine import fetch_all

RULES = {
    "rental references existing customer": """
        SELECT r.rental_id FROM rental r LEFT JOIN customer c ON c.customer_id = r.customer_id
        WHERE c.customer_id IS NULL""",
    "payments are non-negative": "SELECT payment_id, amount FROM payment WHERE amount < 0",
    "return is not before rental": """
        SELECT rental_id, rental_date, return_date FROM rental
        WHERE return_date IS NOT NULL AND return_date < rental_date""",
    "every film has a language": "SELECT film_id FROM film WHERE language_id IS NULL",
    "active customers have unique emails": """
        SELECT lower(email) AS email, COUNT(*) FROM customer WHERE activebool
        GROUP BY lower(email) HAVING COUNT(*) > 1""",
}

@pytest.mark.db
@pytest.mark.parametrize("rule", RULES, ids=list(RULES))
def test_data_integrity(pagila, rule):
    violations = fetch_all(pagila, RULES[rule] + " LIMIT 10")
    assert not violations, f"{rule}: {len(violations)}+ violations, e.g. {violations[:3]}"
```

🟣 **High/Complex: constraints firing inside a rolled-back transaction, plus an injection demo**
```python
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

@pytest.fixture
def rollback_conn(pagila):
    conn = pagila.connect()
    tx = conn.begin()
    yield conn
    tx.rollback()                   # nothing this test does is ever committed
    conn.close()

@pytest.mark.db
def test_rental_requires_existing_customer(rollback_conn):
    with pytest.raises(IntegrityError, match="foreign key"):
        with rollback_conn.begin_nested():            # SAVEPOINT so the outer tx survives the error
            rollback_conn.execute(text("""
                INSERT INTO rental (rental_date, inventory_id, customer_id, staff_id)
                VALUES (now(), 1, -999, 1)"""))

@pytest.mark.db
def test_bound_parameters_neutralise_injection(rollback_conn):
    evil = "x' OR '1'='1"
    unsafe_sql = f"SELECT COUNT(*) FROM customer WHERE email = '{evil}'"     # ❌ never do this
    unsafe = rollback_conn.execute(text(unsafe_sql)).scalar()
    safe = rollback_conn.execute(text("SELECT COUNT(*) FROM customer WHERE email = :e"), {"e": evil}).scalar()
    assert unsafe > 0, "string-built SQL matched every row: injection"
    assert safe == 0, "bound parameter treated input as data"
```
Bonus: create a read-only role for verification queries:
```sql
CREATE ROLE qe_reader LOGIN PASSWORD 'change-me';
GRANT CONNECT ON DATABASE pagila TO qe_reader;
GRANT USAGE ON SCHEMA public TO qe_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO qe_reader;
```

#### 🎤 Interview Q&A

<details><summary><b>[Z] How do you connect to a database from Python tests?</b></summary>

With a driver (psycopg, PyMySQL) usually via SQLAlchemy: `create_engine(url)` once per session (connection pooling), then `with engine.connect() as conn: conn.execute(text(sql), params)`. The URL comes from config or env, never hard-coded, and verification uses a read-only user.
</details>

<details><summary><b>[H] What are parameterized queries and why do they matter?</b></summary>

SQL with placeholders (`:email`, `?`, `%s`) whose values are sent separately from the statement. The DB never parses values as SQL, which prevents injection and handles quoting (`O'Brien`) and types correctly. It's mandatory in test code too, and testers should verify the app does the same by probing inputs with quotes and SQL fragments.
</details>

<details><summary><b>[H] What data-integrity checks would you automate?</b></summary>

Referential (no orphans), entity (unique keys, no duplicates), domain (valid ranges and enums, non-negative amounts), business rules (dates in order, totals equal the sum of lines), completeness (required fields not null), and consistency across tables or systems. Implement them as "queries that return violations" run after data-changing tests or nightly.
</details>

<details><summary><b>[H] How do you keep DB tests from leaving data behind?</b></summary>

For direct DB tests, run in a transaction rolled back at teardown (using savepoints for expected errors). For app-driven data, use unique identifiers plus cleanup via API or DB, or disposable databases (containers, template DBs). Use a read-only user for verification so tests can't mutate accidentally.
</details>

<details><summary><b>[SH] Parallel DB tests start failing with "too many connections". Why, and how do you fix it?</b></summary>

Each xdist worker creates its own engine and pool, so workers × pool_size (+ overflow) exceeds `max_connections`. Fix with small pools per worker (e.g. 2+2), `pool_pre_ping`, closing connections promptly, session-scoped engines (not per test), or a `NullPool` for short-lived use. Raise DB limits only in test environments, and consider PgBouncer in shared ones.
</details>

<details><summary><b>[SH] Which data-quality dimensions would you monitor for a data-heavy product?</b></summary>

Completeness (missing values), uniqueness (duplicates), validity (format and range), consistency (across tables and systems), accuracy (matches the source of truth), and timeliness (freshness). Encode each as automated rules with thresholds, trend them, and alert on regressions. The pattern scales to tools like Great Expectations or dbt tests.
</details>

#### 🤖 AI assist
- Describe your schema to AI and ask for *more integrity rules*. Keep only the ones that encode real business meaning.

---

### P06-04 · API/UI → DB consistency on self-hosted Toolshop

**Level:** 🔵 Hero · **Time:** 5h · **App:** Toolshop (local Docker) · **Deliverable:** `docker-compose.override.yml` (in your Toolshop clone), `framework/db/toolshop.py`, `tests/db/toolshop/`

#### 📋 Task
1. Run Toolshop locally (DEMO_APPS.md). Find the DB service, database name and credentials in its compose/env files. If MySQL's port isn't published, publish it via a `docker-compose.override.yml`.
2. Explore the schema in phpMyAdmin (`http://localhost:8000`), identify the tables for users, brands and invoices, and note them in `docs/toolshop-schema.md`.
3. Tests (with `--env local`):
   - **Register via API → DB:** a `users` row exists with the right fields, the **password is hashed** (not plain text), and timestamps are set.
   - **Update via API → DB:** the change persists and `updated_at` moves forward.
   - **Admin creates a brand via API → DB row. Delete → row gone** (or soft-deleted: find out which).
   - **Invoice consistency:** after placing an order (API flow from Swagger: cart → add item → invoice), the invoice total in the **API response = DB header total = sum of DB line items**, and the order appears in the customer's invoices in the **UI**.
4. Use `wait_until` (P02-05) wherever persistence may be asynchronous.

**Done when**
- [ ] 4 consistency tests pass locally
- [ ] Each assertion message shows the API value and the DB value side by side

#### 📘 User guide

**Concepts**
- **Cross-layer consistency:** UI shows = API returns = DB stores.
- **Persistence verification:** what the API *claims* vs what's *actually* saved.
- **Password storage:** passwords must be stored as salted, slow hashes (bcrypt, argon2), never plain text or reversible. Laravel bcrypt hashes start with `$2y$`.
- **Soft delete:** a row is marked deleted (`deleted_at`) instead of removed.
- **Eventual consistency:** a write becomes visible after a delay (queues, caches, replicas).

**Deep dive**

**Why check the DB if the API said 200?** The API can return what you sent (an echo) while persisting something different: truncated strings, rounded money, a missing foreign key, the wrong timezone, a default overwriting your value, a password stored in plain text. DB checks catch **silent data corruption**, the most expensive class of bug.

**But don't overdo it.** DB assertions couple tests to the schema, and schema refactors then break tests. Use them **selectively** for critical data (money, identity, security, compliance), wrap queries in a small repository module (`framework/db/toolshop.py`) so schema changes are fixed in one place, and prefer API reads for everything else.

**Triangulation:** for critical flows, assert the **same fact at three layers**. When they disagree, the failing layer localises the bug immediately (the UI rounds wrong, the API serialises wrong, or the DB stored wrong).

**Asynchronous persistence:** if writes go through queues, poll (with `wait_until`) with a timeout. Never sleep.

**Examples**

🟢 **Low: publish the DB port and connect**
```yaml
# docker-compose.override.yml, placed next to Toolshop's compose file
# Find the real DB service name with: docker compose config --services
services:
  mariadb:                 # ← replace with the actual DB service name
    ports:
      - "3306:3306"
```
```bash
docker compose up -d
# credentials: check Toolshop's compose/.env files
QE_TOOLSHOP_DB_URL='mysql+pymysql://<user>:<password>@localhost:3306/<database>' \
  uv run python -c "from framework.db.engine import get_engine, fetch_all; import os; \
  print(fetch_all(get_engine(os.environ['QE_TOOLSHOP_DB_URL']), 'SELECT COUNT(*) AS n FROM users'))"
```

🔵 **Medium: register via the API, then verify storage, including password hashing**
```python
# framework/db/toolshop.py: one place for Toolshop SQL
from framework.db.engine import fetch_all

def user_by_email(engine, email: str) -> dict | None:
    rows = fetch_all(engine, "SELECT * FROM users WHERE email = :email", email=email)
    return rows[0] if rows else None
```
```python
# tests/db/toolshop/test_user_persistence.py
import pytest
from framework.data.factories import user_payload
from framework.db.toolshop import user_by_email

@pytest.mark.db
def test_registered_user_is_persisted_with_hashed_password(http, settings, toolshop_db):
    payload = user_payload()
    r = http.post(f"{settings.toolshop_api_url}/users/register", json=payload, timeout=10)
    assert r.status_code in (200, 201), r.text

    row = user_by_email(toolshop_db, payload["email"])
    assert row is not None, "API said created, but no DB row"
    assert (row["first_name"], row["last_name"]) == (payload["first_name"], payload["last_name"])
    assert row["password"] != payload["password"], "PASSWORD STORED IN PLAIN TEXT"
    assert row["password"].startswith("$2"), f"expected a bcrypt hash, got {row['password'][:7]}…"
    assert row["created_at"] is not None
```

🟣 **High/Complex: three-layer invoice consistency (API ↔ DB ↔ UI)**
```python
# tests/e2e/test_invoice_consistency.py
from decimal import Decimal
import pytest
from playwright.sync_api import expect
from framework.db.engine import fetch_all
from framework.utils.wait import wait_until

@pytest.mark.db
@pytest.mark.e2e
def test_invoice_is_consistent_across_layers(toolshop_api, toolshop_db, customer_page):
    # 1) API: place an order. Implement place_order() from Swagger: create cart → add item(s) → create invoice
    invoice = toolshop_api.place_order(product_count=2)
    api_total = Decimal(str(invoice["total"]))

    # 2) DB: header row exists (poll in case persistence is async), and lines sum to header
    header = wait_until(lambda: fetch_all(toolshop_db, "SELECT * FROM invoices WHERE id = :id", id=invoice["id"]),
                        timeout=10, message=f"invoice {invoice['id']} not in DB")[0]
    lines = fetch_all(toolshop_db, """SELECT SUM(unit_price * quantity) AS s
                                      FROM invoice_items WHERE invoice_id = :id""", id=invoice["id"])
    db_total, line_sum = Decimal(str(header["total"])), Decimal(str(lines[0]["s"]))
    assert api_total == db_total == line_sum, f"API={api_total} DB header={db_total} DB lines={line_sum}"

    # 3) UI: the customer sees the same invoice and total
    customer_page.goto("/account/invoices")
    row = customer_page.locator("tr", has_text=invoice["invoice_number"])
    expect(row).to_contain_text(f"{api_total:.2f}")
```
> Table and column names (`invoices`, `invoice_items`, `unit_price`), the invoice-list URL and `place_order` are **for you to confirm and implement** from phpMyAdmin and Swagger. That investigation is the senior part of the task.

#### 🎤 Interview Q&A

<details><summary><b>[Z] The API returned 201 Created. Why would you still check the database?</b></summary>

Because a success response doesn't prove correct persistence. Values can be truncated, rounded, defaulted, stored in the wrong timezone or linked to the wrong record, and sensitive data might be stored insecurely. For critical data (money, identity, permissions), verifying storage catches silent corruption that API-level tests miss.
</details>

<details><summary><b>[H] How would you verify that passwords are stored securely?</b></summary>

Register a user with a known password, then read the stored value: it must not equal the password or any reversible encoding (base64), should have a recognised slow-hash format (bcrypt `$2…`, argon2 `$argon2…`), and should differ for two users with the same password (salting). Also check that the password never appears in logs or API responses.
</details>

<details><summary><b>[H] Should UI tests query the database?</b></summary>

Selectively. For critical end-to-end flows, a DB assertion localises failures and catches persistence bugs. But it couples tests to the schema, needs DB access in the test environment, and slows tests. Default to API verification, keep DB checks in a repository module, and use them for money, security and compliance data.
</details>

<details><summary><b>[H] How do you test soft delete?</b></summary>

Delete via the API, then: the API returns 404 or excludes the item from lists, the DB row still exists with `deleted_at` set, related data behaves per the spec (hidden or retained), restore works if supported, unique constraints behave correctly (can a new record reuse the email?), and privacy rules (hard delete after N days, GDPR) are honoured.
</details>

<details><summary><b>[SH] How do you test eventually consistent systems?</b></summary>

Poll with a timeout for the expected state (never a fixed sleep), assert on the eventual outcome plus bounded latency (an SLO-style check), verify idempotency of consumers (the same message twice doesn't double-apply), test ordering and duplicate delivery, and observe intermediate states (pending → confirmed). Correlation IDs let you trace the event through the pipeline.
</details>

<details><summary><b>[SH] What timezone or precision issues do you look for between layers?</b></summary>

UTC vs local conversions (dates shifting a day near midnight), DST transitions, DB column types without a timezone, float vs DECIMAL money, rounding differences between UI JavaScript and backend, and truncation of long strings or high-precision timestamps. Test with boundary times and values deliberately.
</details>

#### 🤖 AI assist
- Paste the table list (not the data) and ask AI to suggest which tables relate to invoices and how they join. Then **verify** in phpMyAdmin.

---

### P06-05 · Test data strategies, ephemeral DBs, schema and ETL checks

**Level:** 🟣 Super Hero · **Time:** 5h · **App:** Pagila via testcontainers · **Deliverable:** `tests/db/conftest.py`, `tests/db/test_schema_contract.py`, `tests/db/test_reconciliation.py`, `docs/test-data-strategy.md`

#### 📋 Task
1. **Ephemeral DB:** a session fixture using `testcontainers` that starts PostgreSQL, loads Pagila automatically, waits until data is present, and yields a URL. The tests run against a DB nobody else touches.
2. **Schema contract:** snapshot `information_schema.columns` for key tables into `tests/db/__snapshots__/schema.json`. The test fails on unexpected changes (with `UPDATE_SNAPSHOTS=1` to accept).
3. **ETL-style reconciliation:** create a derived table `monthly_store_revenue` (store, month, revenue) from `payment`. Reconcile source vs target by row count, sum, and per-key differences both ways (`EXCEPT`). Then inject a transformation bug (e.g. wrong join) and watch the test catch it.
4. **Strategy doc:** compare rollback, truncate + seed, unique data per test, template databases, and container per run (speed, isolation, realism, cost). Recommend one for each of your suites.

**Done when**
- [ ] `pytest tests/db -m db` passes on a machine with only Docker (no manual DB setup)
- [ ] The reconciliation test fails on your injected bug with a clear diff

#### 📘 User guide

**Concepts**
- **Test data management (TDM):** how test data is created, isolated, reset, masked and versioned.
- **Ephemeral environment:** created per run, destroyed after, with no leftovers or interference.
- **Testcontainers:** a library that starts Docker containers from tests and tears them down automatically.
- **Schema drift:** unplanned differences between the expected and actual schema.
- **ETL testing:** verifying Extract-Transform-Load: completeness, accuracy, transformation logic, reconciliation.

**Deep dive**

**Choosing a data strategy:**
| Strategy | Isolation | Speed | Works when the app uses its own connections? | Best for |
|---|---|---|---|---|
| Transaction rollback | Excellent | Fastest | ❌ (the app can't see uncommitted data) | Direct DB/repository tests |
| Unique data per test | Good | Fast | ✅ | API/UI tests on shared envs, parallel runs |
| Truncate + seed | Good | Medium | ✅ | Small schemas, serial suites |
| Template DB (`CREATE DATABASE t TEMPLATE pagila`) | Excellent | Fast copy | ✅ | Postgres suites needing a pristine DB |
| Container per run | Excellent | Slow start | ✅ | CI, destructive tests, migrations |

**Rollback's blind spot:** it only works when the *test* owns the connection. When the *app under test* writes via its own connections (API tests), your transaction can't roll back the app's commits. Then you use unique data plus cleanup, or disposable databases.

**Schema contract tests** catch migrations that silently change types or nullability, or drop columns that reports depend on. Snapshot only what consumers depend on, and review snapshot updates like code.

**ETL/reconciliation techniques:** row counts (completeness), sums and checksums of measures (accuracy), `EXCEPT` both directions (exact per-key differences), null and duplicate checks on targets, sampled deep-compares of records, and boundary checks (month edges, timezones). With these, "the numbers look off" becomes a precise failing assertion.

**Masking:** never copy production PII into test environments. Mask or synthesise (Faker), keep referential integrity when masking, and treat test databases as sensitive anyway.

**Examples**

🟢 **Low: a transaction-per-test fixture (direct DB tests only)**
```python
# tests/db/conftest.py
import pytest

@pytest.fixture
def db_tx(pagila):
    conn = pagila.connect()
    tx = conn.begin()
    try:
        yield conn
    finally:
        tx.rollback()
        conn.close()
```
```python
# tests/db/test_tx_isolation.py
import pytest
from sqlalchemy import text

@pytest.mark.db
def test_insert_is_visible_inside_tx_only(db_tx):
    db_tx.execute(text("INSERT INTO category (name) VALUES ('QE-Temp')"))
    assert db_tx.execute(text("SELECT COUNT(*) FROM category WHERE name='QE-Temp'")).scalar() == 1
    # after teardown the row is gone; prove it with a second test that counts 0
```

🔵 **Medium: a schema snapshot contract**
```python
# tests/db/test_schema_contract.py
import json, os
from pathlib import Path
import pytest
from framework.db.engine import fetch_all

SNAPSHOT = Path(__file__).parent / "__snapshots__" / "schema.json"
TABLES = ("customer", "rental", "payment", "film")

@pytest.mark.db
def test_schema_matches_contract(pagila):
    rows = fetch_all(pagila, """
        SELECT table_name, column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = ANY(:tables)
        ORDER BY table_name, column_name""", tables=list(TABLES))
    current = {f"{r['table_name']}.{r['column_name']}": f"{r['data_type']} null={r['is_nullable']}" for r in rows}
    if os.getenv("UPDATE_SNAPSHOTS") == "1" or not SNAPSHOT.exists():
        SNAPSHOT.parent.mkdir(exist_ok=True)
        SNAPSHOT.write_text(json.dumps(current, indent=2, sort_keys=True))
        pytest.skip("schema snapshot written; commit it")
    expected = json.loads(SNAPSHOT.read_text())
    removed = sorted(expected.keys() - current.keys())
    changed = sorted(k for k in expected.keys() & current.keys() if expected[k] != current[k])
    added = sorted(current.keys() - expected.keys())
    assert not (removed or changed), f"removed={removed} changed={[(k, expected[k], current[k]) for k in changed]}"
    if added:
        print(f"note: new columns {added}")        # additive = non-breaking; update snapshot when intended
```

🟣 **High/Complex: a disposable Pagila per run plus ETL reconciliation**
```python
# tests/db/conftest.py      (uv add --dev "testcontainers[postgres]")
import os
from pathlib import Path
import pytest
from sqlalchemy import create_engine, text
from testcontainers.postgres import PostgresContainer
from framework.utils.wait import wait_until

PAGILA_DIR = Path(os.getenv("PAGILA_DIR", "../pagila"))          # your clone of devrimgunduz/pagila

@pytest.fixture(scope="session")
def pagila_url():
    if os.getenv("QE_PAGILA_URL"):                                # reuse an existing DB if configured
        yield os.environ["QE_PAGILA_URL"]
        return
    # user "postgres": Pagila's schema assigns ownership to that role; PG version per Pagila's README
    pg = (PostgresContainer("postgres:18", username="postgres", password="postgres", dbname="pagila", driver="psycopg")
          .with_volume_mapping(str((PAGILA_DIR / "pagila-schema.sql").resolve()), "/docker-entrypoint-initdb.d/01-schema.sql")
          .with_volume_mapping(str((PAGILA_DIR / "pagila-data.sql").resolve()), "/docker-entrypoint-initdb.d/02-data.sql"))
    with pg:
        url = pg.get_connection_url()
        engine = create_engine(url)
        def loaded() -> bool:
            try:
                with engine.connect() as c:
                    return c.execute(text("SELECT COUNT(*) FROM rental")).scalar() > 0
            except Exception:
                return False
        wait_until(loaded, timeout=120, interval=2, message="Pagila did not finish loading")
        engine.dispose()
        yield url

@pytest.fixture(scope="session")
def pagila(pagila_url):
    engine = create_engine(pagila_url, pool_size=2)
    yield engine
    engine.dispose()
# Delete the P06-03 `pagila` fixture in tests/db/pagila/conftest.py so every DB test shares this one.
```
```python
# tests/db/test_reconciliation.py
import pytest
from sqlalchemy import text
from framework.db.engine import fetch_all

TRANSFORM = """
CREATE TABLE monthly_store_revenue AS
SELECT s.store_id, date_trunc('month', p.payment_date)::date AS month, SUM(p.amount) AS revenue
FROM payment p
JOIN staff s ON s.staff_id = p.staff_id          -- inject a bug: join on customer's store instead
GROUP BY 1, 2
"""
SOURCE = """SELECT s.store_id, date_trunc('month', p.payment_date)::date AS month, SUM(p.amount) AS revenue
            FROM payment p JOIN staff s ON s.staff_id = p.staff_id GROUP BY 1, 2"""

@pytest.fixture(scope="module")
def target(pagila):
    with pagila.begin() as c:
        c.execute(text("DROP TABLE IF EXISTS monthly_store_revenue"))
        c.execute(text(TRANSFORM))
    yield
    with pagila.begin() as c:
        c.execute(text("DROP TABLE monthly_store_revenue"))

@pytest.mark.db
def test_totals_reconcile(pagila, target):
    src = fetch_all(pagila, "SELECT SUM(amount) AS s FROM payment")[0]["s"]
    tgt = fetch_all(pagila, "SELECT SUM(revenue) AS s FROM monthly_store_revenue")[0]["s"]
    assert src == tgt, f"source total {src} != target total {tgt}"

@pytest.mark.db
def test_no_per_key_differences(pagila, target):
    missing = fetch_all(pagila, f"({SOURCE}) EXCEPT (SELECT * FROM monthly_store_revenue) LIMIT 5")
    extra = fetch_all(pagila, f"(SELECT * FROM monthly_store_revenue) EXCEPT ({SOURCE}) LIMIT 5")
    assert not missing and not extra, f"missing in target: {missing}\nunexpected in target: {extra}"
```
> Check the testcontainers docs for your installed version if the constructor arguments differ. Adapting to library changes is part of Super Hero work.

#### 🎤 Interview Q&A

<details><summary><b>[H] What test data management strategies do you know? How do you choose?</b></summary>

Transaction rollback, unique data per test with cleanup, truncate plus seed, template or snapshot restore, and ephemeral containers per run, plus synthetic data generation and production-data masking. Choose by isolation needs (parallel?), who owns the connections (can I roll back?), speed, realism, and destructive vs read-only tests. Usually it's a mix: unique data for API/UI suites, rollback for repository tests, containers in CI.
</details>

<details><summary><b>[SH] Why doesn't transaction rollback work for API tests?</b></summary>

The API server commits through its own DB connections and transactions. The test's transaction is separate, so rolling it back doesn't undo the app's committed writes (and the app can't see the test's uncommitted setup data). You need app-visible strategies: unique data plus cleanup, or a disposable database per run.
</details>

<details><summary><b>[H] What are the benefits of testcontainers?</b></summary>

Real dependencies (actual Postgres, not a mock or SQLite stand-in) that start from code, isolated per run or suite, identical locally and in CI, torn down automatically, and version-pinned. The cost is start-up time and a Docker requirement, which you mitigate with session scope, reuse and template DBs.
</details>

<details><summary><b>[SH] How do you test database migrations?</b></summary>

Apply migrations from an empty DB and from the previous production schema snapshot, then run the schema contract and integrity checks. Test rollback (down migrations) where supported. Test data migrations on a masked copy with row-count and value reconciliation. Measure duration and locking on realistic volumes, and verify the app works on both old and new schema during rolling deploys (expand/contract pattern).
</details>

<details><summary><b>[SH] How do you approach ETL or data-pipeline testing?</b></summary>

Test each stage: source extraction completeness (counts), transformation logic (unit tests on the rules plus golden datasets), load accuracy (sums, checksums, `EXCEPT` both ways, sampled record compares), data quality on the target (nulls, duplicates, referential integrity, ranges), incremental loads (late or updated records, idempotent reruns), performance on volume, and monitoring in production (freshness, volume anomalies).
</details>

<details><summary><b>[SH] How do you handle PII in test environments?</b></summary>

Don't copy it. Prefer synthetic data. If production-like data is required, mask or tokenise irreversibly while preserving formats and referential integrity, restrict access, set retention, and audit. Never paste real PII into AI tools, logs or bug reports.
</details>

#### 🤖 AI assist
- Ask AI to generate **tricky reconciliation scenarios** (late-arriving records, timezone month edges, duplicate source rows) and add one as a test case.

---

## 🏁 Phase checkpoint: P06

**SQL self-test (30 min, no AI, on Pagila):** top 3 customers per store by spend, films never rented, second-highest payment, month-over-month revenue change, duplicate emails.

**AI mock interviewer prompt**
```text
Interview me for the SQL/database round of a QA automation role. Give me the
Pagila schema summary (customer, rental, inventory, film, category, payment),
then ask 5 SQL problems of increasing difficulty (joins → window functions),
one at a time, without solutions. Then ask 4 conceptual questions (ACID, indexes,
test data strategy, verifying API writes in DB). Score each 1-5.
```
Record your results in `interview-notes/P06.md`.
