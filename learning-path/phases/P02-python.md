# P02: Python for QE

> **Goal:** write clean, typed Python that test frameworks are built from, and pass the Python coding round.
> **Apps:** SauceDemo and Toolshop *data* (no browser yet). **Prerequisites:** P00 (P01 recommended). **Time:** ~23 h.

| ID | Task | Level | Time |
|---|---|---|---|
| P02-01 | Data types, collections and comprehensions | 🟢 | 3h |
| P02-02 | Functions, type hints and exceptions | 🟢 | 3h |
| P02-03 | Files and test-data formats | 🟢 | 2h |
| P02-04 | OOP and dataclasses | 🔵 | 3h |
| P02-05 | Decorators, context managers, logging and config | 🔵 | 4h |
| P02-06 | Coding interview drills | 🔵 | 4h |
| P02-07 | Advanced Python for framework authors | 🟣 | 4h |

> In P02, check your code with plain `assert` statements under `if __name__ == "__main__":`. In **P03-01** you'll convert them into pytest tests.

---

### P02-01 · Data types, collections and comprehensions

**Level:** 🟢 Zero · **Time:** 3h · **App:** SauceDemo · **Deliverable:** `python_basics/products.py`

#### 📋 Task
1. Log in to SauceDemo as `standard_user` and copy the 6 products (name and price) into a list of dicts in `products.py`.
2. Write functions that mirror the UI's sort dropdown: `sort_products(products, mode)` for `az`, `za`, `lohi` and `hilo`.
3. Write: `under(products, max_price)`, `cheapest(products)`, `total(products)`, `names_by_price(products) -> dict[price, list[name]]`, `duplicate_prices(products)`.
4. Write `is_sorted(values, reverse=False) -> bool`. You'll reuse it in P05 to verify the UI sort.

**Done when**
- [ ] All functions have asserts that pass (`python python_basics/products.py`)
- [ ] Prices use `Decimal`, not `float` (you can explain why)

#### 📘 User guide

**Concepts**
| Type | Ordered | Mutable | Duplicates | Typical QA use |
|---|---|---|---|---|
| `list` | ✅ | ✅ | ✅ | Rows from a table, test steps |
| `tuple` | ✅ | ❌ | ✅ | Fixed records, dict keys, parametrize rows |
| `dict` | ✅ (insertion) | ✅ | Keys unique | JSON payloads, lookups by ID |
| `set` | ❌ | ✅ | ❌ | Dedup, membership, "what's missing?" |

- **Comprehension:** `[expr for x in items if cond]`, a readable way to map and filter in one line.
- **`sorted(items, key=..., reverse=...)`** returns a new list. `list.sort()` sorts in place and returns `None` (a classic bug).

**Deep dive**

**References and mutability.** `a = [1, 2]; b = a; b.append(3)` changes `a` too, because both names point at the same list. Tests that share a mutable "default payload" dict and modify it will leak state into each other. Copy first (`dict(payload)`, `copy.deepcopy`) or build fresh data per test.

**Complexity you'll be asked about.** `x in list` checks every element (O(n)). `x in set` / `x in dict` is a hash lookup (O(1) on average). Comparing "expected vs actual IDs" with sets (`expected - actual`) is both faster and clearer than nested loops.

**Money is not a float.** `0.1 + 0.2 == 0.30000000000000004`. Use `Decimal("29.99")` (from a *string*) for prices and totals, otherwise your assertion that tax equals 8% will fail by a cent. This comes up again in P02-02 with rounding.

**Check properties, not hard-coded lists.** To verify "price low→high" in a UI, don't hard-code the expected order. Ties (SauceDemo has two $15.99 items) may appear in either order. Check the *property*: `prices == sorted(prices)`. This makes tests robust to data changes.

**Examples**

🟢 **Low: filter with a comprehension**
```python
from decimal import Decimal

PRODUCTS = [
    {"name": "Sauce Labs Backpack", "price": Decimal("29.99")},
    {"name": "Sauce Labs Bike Light", "price": Decimal("9.99")},
    {"name": "Sauce Labs Bolt T-Shirt", "price": Decimal("15.99")},
    {"name": "Sauce Labs Fleece Jacket", "price": Decimal("49.99")},
    {"name": "Sauce Labs Onesie", "price": Decimal("7.99")},
    {"name": "Test.allTheThings() T-Shirt (Red)", "price": Decimal("15.99")},
]

cheap = [p["name"] for p in PRODUCTS if p["price"] < Decimal("20")]
assert "Sauce Labs Onesie" in cheap and len(cheap) == 4
```

🔵 **Medium: sort, group and find duplicates**
```python
from collections import Counter, defaultdict

def sort_products(products, mode: str):
    keys = {
        "az":   (lambda p: p["name"], False),
        "za":   (lambda p: p["name"], True),
        "lohi": (lambda p: p["price"], False),
        "hilo": (lambda p: p["price"], True),
    }
    key, reverse = keys[mode]            # KeyError for unknown mode = fail fast
    return sorted(products, key=key, reverse=reverse)

def names_by_price(products):
    grouped = defaultdict(list)
    for p in products:
        grouped[p["price"]].append(p["name"])
    return dict(grouped)

def duplicate_prices(products):
    counts = Counter(p["price"] for p in products)
    return {price for price, n in counts.items() if n > 1}

assert sort_products(PRODUCTS, "lohi")[0]["name"] == "Sauce Labs Onesie"
assert duplicate_prices(PRODUCTS) == {Decimal("15.99")}
```

🟣 **High/Complex: property-based sort check with diagnostics (reused in P05)**
```python
def is_sorted(values, reverse: bool = False) -> bool:
    return all((a >= b) if reverse else (a <= b) for a, b in zip(values, values[1:]))

def first_unsorted_pair(values, reverse: bool = False):
    """Return (index, left, right) of the first violation, or None. Great for assertion messages."""
    for i, (a, b) in enumerate(zip(values, values[1:])):
        if (a < b) if reverse else (a > b):
            return i, a, b
    return None

ui_prices = [Decimal("7.99"), Decimal("15.99"), Decimal("9.99")]   # e.g. what problem_user shows
assert not is_sorted(ui_prices)
assert first_unsorted_pair(ui_prices) == (1, Decimal("15.99"), Decimal("9.99"))
```
`zip(values, values[1:])` pairs each element with its neighbour, an idiom worth memorising.

#### 🎤 Interview Q&A

<details><summary><b>[Z] List vs tuple?</b></summary>

Both are ordered sequences. Lists are mutable and tuples are immutable. Use tuples for fixed records (e.g. `("standard_user", "secret_sauce")` in parametrize) and as dict keys, since they're hashable if their contents are. Use lists for collections that grow or change.
</details>

<details><summary><b>[Z] Are dicts ordered in Python?</b></summary>

Yes. Since Python 3.7, dicts preserve insertion order as a language guarantee. Don't rely on JSON *API responses* keeping key order for equality checks, though. Compare dicts, not strings.
</details>

<details><summary><b>[H] Why is <code>x in my_set</code> faster than <code>x in my_list</code>?</b></summary>

Sets and dicts are hash tables: membership hashes `x` and jumps to its bucket, O(1) on average. Lists scan every element, O(n). With 10k IDs to reconcile, that's the difference between milliseconds and seconds. Set operations (`-`, `&`, `|`) also express "missing/extra records" clearly.
</details>

<details><summary><b>[H] Shallow vs deep copy? Give a testing example.</b></summary>

A shallow copy (`dict(d)`, `list(l)`, `copy.copy`) copies the outer container but shares nested objects. A deep copy (`copy.deepcopy`) copies everything recursively. Example: a base booking payload with nested `bookingdates`. Shallow-copying it and changing `bookingdates["checkin"]` mutates the base for every other test. Use deepcopy or a factory function that builds fresh data.
</details>

<details><summary><b>[H] Why shouldn't you use float for prices?</b></summary>

Binary floats can't represent most decimals exactly (`0.1 + 0.2 != 0.3`), so totals drift by fractions of a cent and equality assertions fail. Use `Decimal` constructed from strings, and apply explicit rounding rules (`quantize` with `ROUND_HALF_UP`) that match the business requirement.
</details>

#### 🤖 AI assist
- After writing your functions, ask AI: *"Review for edge cases: empty list, ties, unknown sort mode."* Then add asserts for each edge case it finds.

---

### P02-02 · Functions, type hints and exceptions

**Level:** 🟢 Zero · **Time:** 3h · **App:** SauceDemo checkout · **Deliverable:** `python_basics/checkout.py`

#### 📋 Task
1. `calculate_totals(prices: list[Decimal], tax_rate: Decimal = Decimal("0.08")) -> dict` returning `item_total`, `tax` and `total`, rounded to cents the way SauceDemo does. Verify against the UI by buying the Backpack ($29.99): the overview shows the tax and total.
2. `validate_checkout(first: str, last: str, postal: str) -> None` raising a custom `CheckoutValidationError` with SauceDemo's exact messages (e.g. `Error: First Name is required`). Check the UI for the others.
3. `build_booking(**overrides) -> dict` returning a valid Restful-Booker payload with sensible defaults that any field can override.

**Done when**
- [ ] Your totals match the SauceDemo UI for 1, 2 and 3 items
- [ ] Every function has type hints and a docstring
- [ ] Invalid input raises your custom exception with the right message

#### 📘 User guide

**Concepts**
- **Parameters:** positional, keyword, default values, `*args` (extra positional → tuple), `**kwargs` (extra keyword → dict).
- **Type hints:** `def f(x: int) -> str:`. They're documentation that tools (mypy, IDEs) check, and they aren't enforced at runtime.
- **Exceptions:** `raise`, `try/except/else/finally`, custom exception classes, `raise NewError(...) from original`.

**Deep dive**

**The mutable default trap** (a top interview question):
```python
def add_item(item, cart=[]):   # ❌ the SAME list is reused across calls
    cart.append(item); return cart
```
Defaults are evaluated **once**, when the function is defined. Use `cart: list | None = None` and create the list inside.

**Rounding is a business rule.** Python's `round(2.5) == 2` uses *banker's rounding* (round half to even), and `round(2.675, 2) == 2.67` because 2.675 is really 2.67499999… as a float. For money use `Decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` and confirm which rule the product uses. A one-cent mismatch is a real bug class.

**Exceptions as a design tool.** Raise specific exceptions (`CheckoutValidationError`) rather than returning `False` or error strings. Callers can't accidentally ignore them, and pytest can assert them with `pytest.raises(..., match=...)`. Catch narrowly: `except KeyError`, never bare `except:`, which also swallows `KeyboardInterrupt` and hides bugs. Use `raise ... from e` to keep the original cause in the traceback.

**`try/except/else/finally` order:** `try` runs; `except` handles failures; `else` runs only if there was no exception; `finally` **always** runs, which makes it the place for cleanup like closing a browser or deleting test data.

**Examples**

🟢 **Low: defaults and keyword arguments**
```python
def greet(user: str, greeting: str = "Hello") -> str:
    """Return a greeting for a user."""
    return f"{greeting}, {user}!"

assert greet("standard_user") == "Hello, standard_user!"
assert greet(greeting="Hi", user="problem_user") == "Hi, problem_user!"
```

🔵 **Medium: money maths plus a custom exception**
```python
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")

class CheckoutValidationError(ValueError):
    """Raised when checkout info is invalid; message mirrors the UI."""

def calculate_totals(prices: list[Decimal], tax_rate: Decimal = Decimal("0.08")) -> dict[str, Decimal]:
    item_total = sum(prices, Decimal("0"))
    tax = (item_total * tax_rate).quantize(CENT, rounding=ROUND_HALF_UP)
    return {"item_total": item_total, "tax": tax, "total": item_total + tax}

def validate_checkout(first: str, last: str, postal: str) -> None:
    for value, label in ((first, "First Name"), (last, "Last Name"), (postal, "Postal Code")):
        if not value.strip():
            raise CheckoutValidationError(f"Error: {label} is required")

assert calculate_totals([Decimal("29.99")])["tax"] == Decimal("2.40")
try:
    validate_checkout("Ada", "", "12345")
except CheckoutValidationError as e:
    assert str(e) == "Error: Last Name is required"
```

🟣 **High/Complex: a payload builder with overrides, deep-merge and exception chaining**
```python
import copy
from typing import Any

DEFAULT_BOOKING: dict[str, Any] = {
    "firstname": "Test", "lastname": "User", "totalprice": 150, "depositpaid": True,
    "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-05"},
    "additionalneeds": "Breakfast",
}

class PayloadError(Exception):
    pass

def _deep_merge(base: dict, overrides: dict) -> dict:
    for key, value in overrides.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base

def build_booking(**overrides: Any) -> dict[str, Any]:
    payload = copy.deepcopy(DEFAULT_BOOKING)          # never mutate the default!
    unknown = set(overrides) - set(payload)
    if unknown:
        raise PayloadError(f"Unknown booking fields: {sorted(unknown)}")
    try:
        return _deep_merge(payload, overrides)
    except TypeError as e:
        raise PayloadError("Invalid override value") from e

b = build_booking(lastname="Smith", bookingdates={"checkout": "2026-01-10"})
assert b["bookingdates"] == {"checkin": "2026-01-01", "checkout": "2026-01-10"}
assert DEFAULT_BOOKING["lastname"] == "User"      # default untouched
```
This "defaults + overrides" builder is the core of good test-data design. Tests state *only what matters to them*.

#### 🎤 Interview Q&A

<details><summary><b>[Z] What are <code>*args</code> and <code>**kwargs</code>?</b></summary>

`*args` collects extra positional arguments into a tuple, and `**kwargs` collects extra keyword arguments into a dict. They're used for flexible APIs, such as a payload builder accepting any field overrides or a wrapper that passes arguments through to another function.
</details>

<details><summary><b>[H] Explain the mutable default argument problem.</b></summary>

Default values are evaluated once at function definition, so a default `[]` or `{}` is shared by every call and accumulates state. Fix: default to `None` and create a new object inside. In test code this causes "passes alone, fails in suite" bugs.
</details>

<details><summary><b>[H] What does <code>round(2.5)</code> return, and why does it matter for testing?</b></summary>

`2`. Python uses round-half-to-even (banker's rounding). Combined with float representation (`round(2.675, 2) == 2.67`), this means tests that compute expected money values with `round()` can disagree with a system that rounds half-up. Use `Decimal` with an explicit rounding mode that matches the requirement.
</details>

<details><summary><b>[Z] Order of <code>try/except/else/finally</code>?</b></summary>

`try` runs first. If it raises, the matching `except` runs. If it doesn't raise, `else` runs. `finally` always runs last, even after `return` or an unhandled exception, so it's used for cleanup.
</details>

<details><summary><b>[SH] EAFP vs LBYL: which do you prefer in framework code?</b></summary>

LBYL ("look before you leap", e.g. `if key in d`) checks first. EAFP ("easier to ask forgiveness than permission", i.e. `try: d[key] except KeyError`) attempts and handles failure. Python favours EAFP: it avoids race conditions (a file checked with `exists()` can vanish before you open it) and keeps the happy path clean. I use LBYL for cheap validation with a clear error message, and EAFP around I/O and external systems.
</details>

#### 🤖 AI assist
- Ask AI *"why does round(2.675, 2) give 2.67?"*, then verify with `Decimal(2.675)` in a REPL.

---

### P02-03 · Files and test-data formats

**Level:** 🟢 Zero · **Time:** 2h · **App:** SauceDemo, Toolshop · **Deliverable:** `framework/data/saucedemo_users.csv`, `python_basics/data_io.py`

#### 📋 Task
1. Create `framework/data/saucedemo_users.csv` with columns `username,password,can_login,expected_error`, one row per SauceDemo user.
2. Create `framework/data/toolshop_users.json` with the Toolshop test users (see DEMO_APPS.md).
3. In `data_io.py`, write `load_csv(name)`, `load_json(name)` and `save_json(name, data)` that resolve paths **relative to the module**, not the current directory.
4. Read `BASE_URL` from an environment variable with a default.

**Done when**
- [ ] Loading works from *any* working directory (`cd /tmp && python /path/to/data_io.py`)
- [ ] `can_login` is converted to a real `bool` (not the string `"False"`, which is truthy!)

#### 📘 User guide

**Concepts**
- **`pathlib.Path`:** object-oriented paths. `Path(__file__).parent / "data" / "users.csv"`.
- **`with open(...) as f`:** a context manager that always closes the file.
- **CSV:** `csv.DictReader` gives one dict per row. **Everything is a string.**
- **JSON:** maps to dict/list/str/int/float/bool/None. **YAML:** a human-friendly superset of JSON (`yaml.safe_load`).
- **Environment variables:** `os.environ.get("BASE_URL", "https://www.saucedemo.com")`.

**Deep dive**

**The number-one CI failure for file-based data** is relative paths. `open("data/users.csv")` resolves against the *current working directory*, which differs between your IDE, the terminal, pytest's rootdir and a Docker container. Always anchor to the code file: `Path(__file__).resolve().parent`.

**CSV gotcha: `bool("False") is True`.** Any non-empty string is truthy. Convert explicitly: `row["can_login"].strip().lower() == "true"`.

**Choosing a format for test data:**
| Format | Best for | Watch out for |
|---|---|---|
| CSV | Tabular, data-driven cases edited by non-coders | No types, no nesting |
| JSON | API payloads, nested data | No comments |
| YAML | Environment configs, readable nested data | Indentation errors; use `safe_load` (plain `load` can construct arbitrary objects) |
| Python factories | Dynamic and unique data | Needs code to change |

Static files suit *reference* data (users, expected messages). Dynamic factories (P04-07) suit *created* data (unique emails), which parallel runs need.

**Examples**

🟢 **Low: read CSV rows**
```python
import csv
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "framework" / "data"

with (DATA / "saucedemo_users.csv").open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
assert rows[0]["username"] == "standard_user"
```

🔵 **Medium: typed loading with correct booleans**
```python
import csv, json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "framework" / "data"

def load_csv(name: str) -> list[dict]:
    with (DATA / name).open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        if "can_login" in row:
            row["can_login"] = row["can_login"].strip().lower() == "true"
    return rows

def save_json(name: str, data: object) -> Path:
    path = DATA.parent.parent / "test-results" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return path
```

🟣 **High/Complex: one loader for all formats, validated into dataclasses with precise errors**
```python
import csv, json
from dataclasses import dataclass, fields
from pathlib import Path
import yaml   # uv add pyyaml

DATA = Path(__file__).resolve().parent.parent / "framework" / "data"

@dataclass(frozen=True)
class SauceUser:
    username: str
    password: str
    can_login: bool
    expected_error: str = ""

def _read(path: Path) -> list[dict]:
    match path.suffix:
        case ".csv":
            with path.open(newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        case ".json":
            return json.loads(path.read_text(encoding="utf-8"))
        case ".yaml" | ".yml":
            return yaml.safe_load(path.read_text(encoding="utf-8"))
        case _:
            raise ValueError(f"Unsupported test-data format: {path.suffix}")

def load_as[T](name: str, model: type[T]) -> list[T]:          # Python 3.12 generic syntax
    path = DATA / name
    allowed = {f.name for f in fields(model)}
    out: list[T] = []
    for i, raw in enumerate(_read(path), start=1):
        extra = set(raw) - allowed
        if extra:
            raise ValueError(f"{path.name} row {i}: unknown columns {sorted(extra)}")
        if "can_login" in raw and isinstance(raw["can_login"], str):
            raw["can_login"] = raw["can_login"].lower() == "true"
        out.append(model(**raw))
    return out

users = load_as("saucedemo_users.csv", SauceUser)
```
Errors that name the **file and row** save hours when a teammate edits test data.

#### 🎤 Interview Q&A

<details><summary><b>[Z] Why use <code>with open(...)</code>?</b></summary>

It guarantees the file is closed even if an exception happens mid-read, so there are no leaked handles or unflushed writes. It's the context-manager protocol (`__enter__`/`__exit__`).
</details>

<details><summary><b>[H] Tests pass in the IDE but fail in CI with FileNotFoundError. Why?</b></summary>

Almost always a path relative to the *current working directory*, which differs between runners. Fix: build paths from `Path(__file__).resolve().parent`, or a fixture that exposes the data dir, and never assume the CWD.
</details>

<details><summary><b>[H] How do you choose between CSV, JSON, YAML and code for test data?</b></summary>

CSV for flat data-driven tables that non-coders maintain. JSON for API-shaped nested payloads. YAML for per-environment config. Code factories for dynamic, unique data needed in parallel runs. Reference data is static; created data is generated. Validate whatever you load.
</details>

<details><summary><b>[SH] How do you manage test data across dev, staging and pre-prod?</b></summary>

Separate *config* (URLs, credentials via env and secrets) from *data*. Prefer tests that **create their own data via API** so they're environment-independent. Keep a minimal seeded reference set per environment (known users and products) versioned in the repo or seed scripts. Never depend on prod-like data you don't control, mask PII, and have a reset or cleanup strategy (see P06-05).
</details>

<details><summary><b>[SH] Why <code>yaml.safe_load</code> instead of <code>yaml.load</code>?</b></summary>

Full `load` can construct arbitrary Python objects from tags, which is a code-execution risk if the file is untrusted. `safe_load` only builds basic types. It's the same principle as never `eval`-ing test data.
</details>

#### 🤖 AI assist
- Ask AI to generate 20 *edge-case* rows for your CSV (unicode names, whitespace, very long strings), then decide which are meaningful.

---

### P02-04 · OOP and dataclasses

**Level:** 🔵 Hero · **Time:** 3h · **App:** SauceDemo / Toolshop domain · **Deliverable:** `framework/models.py`, `python_basics/cart.py`

#### 📋 Task
1. `@dataclass(frozen=True) class Product(name: str, price: Decimal)` and `@dataclass class User`.
2. `class Cart` with `add`, `remove`, `count`, `total` (reuse P02-02), `__len__` and `__contains__`.
3. `Product.from_dict()` as a `classmethod`.
4. Preview POM: an abstract `BasePage` (abstract `url` property, `open()`) and two subclasses, `SauceLoginPage` and `ToolshopLoginPage`, each with `login(user)`. They just `print` for now; Playwright arrives in P05.

**Done when**
- [ ] `Product` instances are hashable and usable in a set
- [ ] Instantiating `BasePage` directly raises `TypeError`
- [ ] You can explain composition vs inheritance with *your* classes

#### 📘 User guide

**Concepts**
- **Class/instance/`self`:** a blueprint, an object built from it, and the object's reference to itself.
- **Four pillars:** *encapsulation* (hide internals), *inheritance* (is-a), *polymorphism* (same interface, different behaviour), *abstraction* (expose what, hide how).
- **`@dataclass`:** auto-generates `__init__`, `__repr__` and `__eq__`. `frozen=True` makes it immutable and hashable.
- **`@property`:** a computed attribute. **`@classmethod`:** alternative constructors. **`@staticmethod`:** a namespaced helper.
- **ABC:** `abc.ABC` plus `@abstractmethod` enforce that subclasses implement an interface.

**Deep dive**

**Where OOP shows up in test frameworks:**
- **Page Object Model:** each page is a class exposing *intent* (`login(user)`) while hiding locators (encapsulation).
- **Components:** a `Header` object *inside* several pages (composition).
- **API clients:** one class per resource (`BookingClient`) sharing a `BaseClient` (inheritance for shared plumbing).
- **Models:** dataclasses or pydantic models for payloads and responses (abstraction over raw dicts).

**Composition over inheritance.** Deep hierarchies (`BasePage → AuthPage → AdminPage → AdminProductPage`) get brittle. Pages *have* components (header, cart badge, table) instead. Rule of thumb: inherit for **shared plumbing** (open, wait for load), compose for **shared UI pieces**.

**Dataclass vs pydantic:** dataclasses are lightweight and don't validate types at runtime. Pydantic validates and coerces (`"29.99"` → `Decimal`), which is ideal for **API responses** where you want the test to fail if the schema is wrong (P04-04).

**Examples**

🟢 **Low: dataclass plus a simple cart**
```python
from dataclasses import dataclass, field
from decimal import Decimal

@dataclass(frozen=True)
class Product:
    name: str
    price: Decimal

@dataclass
class Cart:
    items: list[Product] = field(default_factory=list)   # never items: list = []

    def add(self, p: Product) -> None:
        self.items.append(p)

    @property
    def total(self) -> Decimal:
        return sum((p.price for p in self.items), Decimal("0"))

cart = Cart(); cart.add(Product("Onesie", Decimal("7.99")))
assert cart.total == Decimal("7.99")
```

🔵 **Medium: alternative constructor and dunder methods**
```python
@dataclass(frozen=True)
class Product:
    name: str
    price: Decimal

    @classmethod
    def from_dict(cls, d: dict) -> "Product":
        return cls(name=d["name"], price=Decimal(str(d["price"])))

class Cart:
    def __init__(self) -> None:
        self._items: dict[Product, int] = {}          # encapsulated

    def add(self, p: Product, qty: int = 1) -> None:
        self._items[p] = self._items.get(p, 0) + qty   # works because Product is hashable

    def __len__(self) -> int:
        return sum(self._items.values())

    def __contains__(self, p: Product) -> bool:
        return p in self._items
```

🟣 **High/Complex: abstraction plus polymorphism, "same test, two apps"**
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass(frozen=True)
class Credentials:
    username: str
    password: str

class Header:                                       # a component (composition)
    def __init__(self, page_name: str) -> None:
        self.page_name = page_name
    def cart_count(self) -> int:
        return 0                                    # real locator in P05

class BasePage(ABC):
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url
        self.header = Header(type(self).__name__)   # every page HAS a header

    @property
    @abstractmethod
    def path(self) -> str: ...

    def open(self) -> str:
        return f"{self.base_url}{self.path}"         # later: self.page.goto(...)

class LoginPage(BasePage, ABC):
    @abstractmethod
    def login(self, creds: Credentials) -> None: ...

class SauceLoginPage(LoginPage):
    path = "/"
    def login(self, creds: Credentials) -> None:
        print(f"fill #user-name={creds.username}")

class ToolshopLoginPage(LoginPage):
    path = "/auth/login"
    def login(self, creds: Credentials) -> None:
        print(f"fill [data-test=email]={creds.username}")

def smoke_login(page: LoginPage, creds: Credentials) -> None:   # polymorphism
    page.open(); page.login(creds)

smoke_login(SauceLoginPage("https://www.saucedemo.com"), Credentials("standard_user", "secret_sauce"))
```

#### 🎤 Interview Q&A

<details><summary><b>[Z] Explain the four OOP pillars with test-automation examples.</b></summary>

**Encapsulation:** page objects hide locators behind methods like `login()`. **Inheritance:** `BookingClient(BaseClient)` reuses session, auth and logging. **Polymorphism:** `smoke_login(page)` works with any `LoginPage` subclass. **Abstraction:** tests call `cart.checkout()` without knowing the clicks involved.
</details>

<details><summary><b>[H] Composition vs inheritance: which do you prefer in a UI framework?</b></summary>

Composition for UI pieces (header, table, modal components reused across pages). Inheritance only for thin shared plumbing (a `BasePage` with `open()` and wait-for-load). Deep hierarchies couple unrelated pages and make changes risky. "Has-a" is more flexible than "is-a".
</details>

<details><summary><b>[H] <code>@classmethod</code> vs <code>@staticmethod</code>?</b></summary>

A classmethod receives the class (`cls`) and is used for alternative constructors like `Product.from_dict()`, which also works for subclasses. A staticmethod receives nothing; it's a plain function namespaced in the class for organisation.
</details>

<details><summary><b>[H] Dataclass vs pydantic model vs plain dict for API responses?</b></summary>

A dict is flexible, but typos surface late and there's no schema. A dataclass gives structure and a readable `repr` but no runtime validation. Pydantic gives structure plus runtime validation and coercion, so the test fails with a precise error if the API returns a wrong type or misses a field. For API tests I prefer pydantic, and dataclasses for internal test data.
</details>

<details><summary><b>[SH] What is the MRO and when does it matter?</b></summary>

Method Resolution Order is the order Python searches classes for an attribute with multiple inheritance (C3 linearisation, visible via `Cls.__mro__`). It matters for mixins (e.g. `LoggingMixin, BasePage`), where `super()` follows the MRO, not just the direct parent. Keep mixins small and stateless, or prefer composition to avoid surprises.
</details>

#### 🤖 AI assist
- Ask AI to *critique* your class design: *"Where would this hierarchy become painful with 30 pages?"*

---

### P02-05 · Decorators, context managers, logging and config

**Level:** 🔵 Hero · **Time:** 4h · **App:** all (framework plumbing) · **Deliverable:** `framework/utils/retry.py`, `framework/utils/wait.py`, `framework/config.py`, `.env.example`

#### 📋 Task
1. `@retry(times=3, delay=0.5, backoff=2.0, exceptions=(ConnectionError,))`, a decorator factory using `functools.wraps`.
2. `wait_until(condition, timeout=10, interval=0.25, message="")`, a poller that returns the condition's truthy value or raises `TimeoutError` with the message.
3. `timer(name)`, a context manager that logs the duration.
4. `framework/config.py`: a `Settings` class using **pydantic-settings** with fields for SauceDemo, Toolshop UI/API and Restful-Booker URLs, the default timeout and the environment name, loaded from `.env` with the prefix `QE_`.
5. Configure `logging` once (format: time, level, logger name, message).

**Done when**
- [ ] `QE_TOOLSHOP_API_URL=http://localhost:8091 python -c "from framework.config import settings; print(settings.toolshop_api_url)"` prints the override
- [ ] `.env` is git-ignored and `.env.example` documents every key
- [ ] `retry` only retries the listed exceptions, and `wait_until` returns early when the condition is met

#### 📘 User guide

**Concepts**
- **Decorator:** a function that takes a function and returns a wrapped one. `@d` above `def f` means `f = d(f)`. A **decorator factory** takes arguments and returns a decorator.
- **Closure:** an inner function that remembers variables from its enclosing scope. It's how decorators keep `times`, `delay` and so on.
- **Context manager:** setup/teardown around a block (`with`). Built with `__enter__`/`__exit__` or `@contextlib.contextmanager`.
- **Logging:** levels `DEBUG < INFO < WARNING < ERROR < CRITICAL`; loggers per module (`logging.getLogger(__name__)`).
- **12-factor config:** config lives in the environment, not code.

**Deep dive**

**Why `functools.wraps`?** Without it, every decorated function is named `wrapper` in tracebacks and reports, and pytest-style introspection breaks. `wraps` copies the name, docstring and signature metadata.

**Retry is a scalpel, not a bandage.** Retrying *transient infrastructure* failures (connection reset, 503) on *idempotent* operations (GET, PUT) is reasonable. Retrying assertions or POSTs hides real bugs and creates duplicate data. Always cap attempts, back off exponentially, and log every retry so flakiness stays visible.

**Polling vs sleeping.** `sleep(5)` always costs 5 s, and fails if the system needs 6. `wait_until(cond, timeout=10)` returns as soon as `cond()` is true and fails with a clear message at 10 s. You'll use this for async states like order status in APIs and DBs. Playwright has its own auto-waiting for UI.

**Config precedence** (highest wins): real env vars → `.env` file → code defaults. CI sets env vars from secrets, developers use `.env`, and code defaults target the public demo apps. The same test code runs anywhere.

**Logging vs print.** Logs have levels, timestamps and sources. pytest captures them per test and shows them only on failure (or live with `log_cli = true`), and they can go to files. `print` has none of that.

**Examples**

🟢 **Low: a timing decorator**
```python
import functools, logging, time

log = logging.getLogger(__name__)

def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            log.info("%s took %.3fs", func.__name__, time.perf_counter() - start)
    return wrapper
```

🔵 **Medium: a retry decorator factory with backoff**
```python
import functools, logging, time
from collections.abc import Callable

log = logging.getLogger(__name__)

def retry(times: int = 3, delay: float = 0.5, backoff: float = 2.0,
          exceptions: tuple[type[BaseException], ...] = (ConnectionError,)) -> Callable:
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times:
                        raise
                    log.warning("%s failed (%s), retry %d/%d in %.1fs", func.__name__, e, attempt, times, wait)
                    time.sleep(wait)          # sleep is fine HERE: it's backoff, not a test wait
                    wait *= backoff
        return wrapper
    return decorator
```

🟣 **High/Complex: a poller, a timer context manager and typed settings**
```python
# framework/utils/wait.py
import logging, time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import TypeVar

T = TypeVar("T")
log = logging.getLogger(__name__)

def wait_until(condition: Callable[[], T], timeout: float = 10, interval: float = 0.25, message: str = "") -> T:
    deadline = time.monotonic() + timeout            # monotonic: immune to clock changes
    last: T | None = None
    while time.monotonic() < deadline:
        last = condition()
        if last:
            return last
        time.sleep(interval)
    raise TimeoutError(f"Timed out after {timeout}s: {message or condition!r} (last value: {last!r})")

@contextmanager
def timer(name: str) -> Iterator[None]:
    start = time.perf_counter()
    try:
        yield
    finally:
        log.info("%s: %.2fs", name, time.perf_counter() - start)
```
```python
# framework/config.py      (uv add pydantic-settings)
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="QE_", extra="ignore")

    env: str = "public"
    saucedemo_url: str = "https://www.saucedemo.com"
    toolshop_url: str = "https://practicesoftwaretesting.com"
    toolshop_api_url: str = "https://api.practicesoftwaretesting.com"
    booker_url: str = "https://restful-booker.herokuapp.com"
    http_timeout: float = 10.0

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```
```bash
# .env.example: copy to .env (git-ignored) and adjust
QE_ENV=local
QE_TOOLSHOP_URL=http://localhost:4200
QE_TOOLSHOP_API_URL=http://localhost:8091
QE_BOOKER_URL=http://localhost:3001
```

#### 🎤 Interview Q&A

<details><summary><b>[H] What is a decorator? Write one.</b></summary>

A callable that takes a function and returns a new function that adds behaviour before or after it, e.g. timing, retry, logging, or skipping in certain envs. `@timed def f` is `f = timed(f)`. Write it with an inner `wrapper(*args, **kwargs)` and `functools.wraps(func)` to preserve metadata. (Then write the timing example from memory.)
</details>

<details><summary><b>[H] Give examples of context managers in test automation.</b></summary>

`with open(...)` for files; Playwright's `with page.expect_download()` and `with context.expect_page()`; `with pytest.raises(Error)`; DB transactions (`with engine.begin()`) that commit or roll back; a temporary env override; a timer. They guarantee teardown even when the block fails.
</details>

<details><summary><b>[SH] When should you NOT retry?</b></summary>

When the operation isn't idempotent (POST create or payment, where you'd risk duplicates), when the failure is deterministic (4xx validation, assertion failures), or when retries would mask a product bug or flaky test. Retry transient infra errors with caps, backoff and jitter, log every retry, and track retry rates as a health metric.
</details>

<details><summary><b>[H] How do you manage configuration for multiple environments?</b></summary>

A typed settings object that reads env vars, with a `.env` file for local development and defaults for the public environment. Precedence is env var > .env > defaults. Secrets come only from the environment or a secret store, never from committed files. The test code is environment-agnostic, and environment selection happens via one variable or a CLI option (`--env`, P03-05).
</details>

<details><summary><b>[H] What is a closure?</b></summary>

An inner function that captures variables from its enclosing scope and keeps them after the outer function returns. Decorator factories rely on it: `retry(times=3)` returns a decorator whose wrapper still "remembers" `times`.
</details>

#### 🤖 AI assist
- Ask AI to write unit tests for `retry` using a fake function that fails N times. Check the tests don't actually sleep (hint: pass `delay=0` or monkeypatch `time.sleep`).

---

### P02-06 · Coding interview drills

**Level:** 🔵 Hero · **Time:** 4h · **App:** — · **Deliverable:** `python_basics/drills.py`

#### 📋 Task
Solve each drill in **≤15 minutes**, talking out loud (record yourself once). Add asserts, including edge cases.

| # | Drill | # | Drill |
|---|---|---|---|
| 1 | Reverse a string (no slicing, then with) | 11 | Merge two sorted lists |
| 2 | Palindrome (ignore case and non-alphanumerics) | 12 | Valid brackets `()[]{}` |
| 3 | Character frequency | 13 | Group anagrams |
| 4 | First non-repeating character | 14 | Two-sum (return indices) |
| 5 | Anagram check | 15 | Longest substring without repeating chars |
| 6 | Remove duplicates, keep order | 16 | **QA:** count ERROR lines per module in a log file |
| 7 | Second largest number | 17 | **QA:** extract all emails from text (regex) |
| 8 | Missing number in 1..n | 18 | **QA:** diff two JSON objects and report changed paths |
| 9 | Flatten a nested list | 19 | **QA:** validate that dates are in `YYYY-MM-DD` and checkout > checkin |
| 10 | FizzBuzz | 20 | **QA:** find duplicate records by key in a list of dicts |

**Done when**
- [ ] 20 drills with asserts covering empty input, single element, duplicates and unicode where relevant
- [ ] You can state the time complexity of each solution

#### 📘 User guide

**Concepts**
- **Big-O:** how cost grows with input size. O(1) hash lookup, O(n) single scan, O(n log n) sort, O(n²) nested loops.
- **Patterns:** *hashing* (dict/set for counts and seen-before), *two pointers* (palindrome, merge), *stack* (brackets), *sliding window* (longest substring), *recursion* (flatten, JSON diff).

**Deep dive**

QE coding rounds test **clear thinking and testing instinct** more than algorithms. A winning routine:
1. **Clarify:** input types, empty input, case sensitivity, duplicates, expected output format.
2. **Examples:** write 2–3 input→output pairs *including an edge case* before coding.
3. **Brute force first**, say its complexity, then improve if asked.
4. **Code cleanly**, naming things well and talking as you go.
5. **Test it yourself:** walk through your examples. As a QE, *listing edge cases unprompted* is where you shine.

The QA-flavoured drills (16–20) are increasingly common because they mirror real work: parsing logs, diffing API responses, validating data.

**Examples**

🟢 **Low: first non-repeating character, O(n)**
```python
from collections import Counter

def first_unique(s: str) -> str | None:
    counts = Counter(s)
    return next((ch for ch in s if counts[ch] == 1), None)

assert first_unique("swiss") == "w"
assert first_unique("aabb") is None
assert first_unique("") is None
```

🔵 **Medium: valid brackets with a stack, O(n)**
```python
def valid_brackets(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack

assert valid_brackets("{[()]}") and not valid_brackets("(]") and not valid_brackets("((") and valid_brackets("")
```

🟣 **High/Complex: recursive JSON diff with paths (QA gold)**
```python
from typing import Any

def json_diff(expected: Any, actual: Any, path: str = "$") -> list[str]:
    """Return human-readable differences, e.g. '$.bookingdates.checkin: expected 2026-01-01, got 2026-01-02'."""
    if isinstance(expected, dict) and isinstance(actual, dict):
        diffs = []
        for key in expected.keys() | actual.keys():
            if key not in actual:
                diffs.append(f"{path}.{key}: missing in actual")
            elif key not in expected:
                diffs.append(f"{path}.{key}: unexpected field")
            else:
                diffs += json_diff(expected[key], actual[key], f"{path}.{key}")
        return sorted(diffs)
    if isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            return [f"{path}: length {len(expected)} != {len(actual)}"]
        return [d for i, (e, a) in enumerate(zip(expected, actual)) for d in json_diff(e, a, f"{path}[{i}]")]
    return [] if expected == actual else [f"{path}: expected {expected!r}, got {actual!r}"]

exp = {"firstname": "Ada", "bookingdates": {"checkin": "2026-01-01"}, "tags": [1, 2]}
act = {"firstname": "Ada", "bookingdates": {"checkin": "2026-01-02"}, "tags": [1, 3], "extra": True}
assert json_diff(exp, act) == [
    "$.bookingdates.checkin: expected '2026-01-01', got '2026-01-02'",
    "$.extra: unexpected field",
    "$.tags[1]: expected 2, got 3",
]
```
And the sliding window (drill 15):
```python
def longest_unique(s: str) -> int:
    last_seen: dict[str, int] = {}
    start = best = 0
    for i, ch in enumerate(s):
        if last_seen.get(ch, -1) >= start:
            start = last_seen[ch] + 1          # shrink window past the repeat
        last_seen[ch] = i
        best = max(best, i - start + 1)
    return best

assert longest_unique("abcabcbb") == 3 and longest_unique("") == 0 and longest_unique("bbbb") == 1
```

#### 🎤 Interview Q&A

<details><summary><b>[Z] How do you approach a coding question in an interview?</b></summary>

Clarify requirements and edge cases, write examples, state a brute-force approach and its complexity, improve it if needed, code while explaining, then test with my examples and edge cases (empty, one element, duplicates, large input, invalid types).
</details>

<details><summary><b>[H] What's the time complexity of two-sum with a dict, and why?</b></summary>

O(n) time and O(n) space. One pass: for each number, check whether `target - n` is already in the dict (O(1) average lookup), then store `n → index`. Brute force is O(n²) with nested loops.
</details>

<details><summary><b>[H] You wrote a function. Which test cases do you add?</b></summary>

Happy path, boundaries (0, 1, max), empty or `None`, duplicates, negative numbers, unicode and whitespace for strings, very large input (performance), invalid types (expected exception), and idempotency or order-independence if relevant. Then equivalence partitions so I'm not writing redundant cases.
</details>

<details><summary><b>[SH] Recursion vs iteration: what are the risks of recursion in Python?</b></summary>

Python has no tail-call optimisation and a default recursion limit of about 1000, so deep inputs (a huge nested JSON) raise `RecursionError`. Recursion is clearest for tree-shaped data (JSON diff). For unbounded depth, use an explicit stack (iterative DFS).
</details>

#### 🤖 AI assist
- Use AI as the **interviewer**, not the solver: *"Give me a QA-flavoured Python coding problem, don't show the solution, and review my code for edge cases after I paste it."*

---

### P02-07 · Advanced Python for framework authors

**Level:** 🟣 Super Hero · **Time:** 4h · **App:** Toolshop API · **Deliverable:** `framework/api/pagination.py`, `framework/types.py`, framework passes `mypy --strict`

#### 📋 Task
1. Write the generator `iter_products(session, base_url)`, which lazily yields every Toolshop product across all pages (`GET /products?page=N`, stopping at `last_page`).
2. Define `Protocol` interfaces for your clients, `TypedDict`s for request payloads, and an `Enum` for statuses.
3. Make `framework` an installable package (build system in `pyproject.toml`) and import it from tests without `sys.path` hacks.
4. Get `mypy --strict framework` to zero errors.

**Done when**
- [ ] `sum(1 for _ in iter_products(...))` equals the API's reported `total`
- [ ] `mypy --strict framework` passes
- [ ] `docs/python-advanced.md` explains Protocol vs ABC and generators vs lists in your own words

#### 📘 User guide

**Concepts**
- **Iterator/generator:** `yield` produces values lazily, one at a time. Memory stays constant however many items there are.
- **`typing.Protocol`:** structural typing ("anything with a `.get()` method fits") as opposed to ABC's nominal typing ("must inherit").
- **`TypedDict`:** type hints for dict *shapes* (JSON payloads). **`Literal`**, **`Enum`**, **`TypeVar`/generics**.
- **Packaging:** `[build-system]` in `pyproject.toml` plus an editable install makes `import framework` work everywhere.

**Deep dive**

**Generators are everywhere in pytest.** A `yield` fixture *is* a generator: code before `yield` is setup, and code after is teardown. Understanding generators demystifies fixtures (P03-04).

**Pagination as a generator** hides page mechanics from tests. `for product in iter_products(...)` reads naturally, stops early if the consumer breaks, and never loads 10,000 products into memory.

**Protocol vs ABC.** An ABC forces inheritance, which is good when you *own* all implementations and want shared code. A Protocol only requires the right methods, which is good for accepting third-party objects or fakes in unit tests without inheritance. For a `HttpSession` protocol, both `requests.Session` and a test fake satisfy it.

**The GIL and parallel tests.** CPython's Global Interpreter Lock lets only one thread execute Python bytecode at a time. Threads still help for I/O-bound work (HTTP calls release the GIL while waiting), but CPU-bound work needs processes. That's why `pytest-xdist` uses **worker processes** (P07). Newer Python versions offer an experimental free-threaded build, but test tooling still assumes processes.

**Circular imports** usually mean two modules need each other: `pages` importing `api` importing `pages`. Fix it by moving shared types to a leaf module (`framework/types.py`) or importing inside a function.

**Examples**

🟢 **Low: an infinite generator of unique test emails**
```python
import itertools, uuid
from collections.abc import Iterator

def unique_emails(prefix: str = "qe") -> Iterator[str]:
    run = uuid.uuid4().hex[:6]
    for n in itertools.count(1):
        yield f"{prefix}+{run}-{n}@example.com"

emails = unique_emails()
assert next(emails) != next(emails)
```

🔵 **Medium: a pagination generator over the Toolshop API**
```python
# framework/api/pagination.py
from collections.abc import Iterator
from typing import Any
import requests

def iter_products(session: requests.Session, base_url: str, timeout: float = 10) -> Iterator[dict[str, Any]]:
    page = 1
    while True:
        resp = session.get(f"{base_url}/products", params={"page": page}, timeout=timeout)
        resp.raise_for_status()
        body = resp.json()                      # Laravel-style: data, current_page, last_page, total
        yield from body["data"]
        if body["current_page"] >= body["last_page"]:
            return
        page += 1

# usage: stop early without fetching every page
with requests.Session() as s:
    first_hammer = next(p for p in iter_products(s, "https://api.practicesoftwaretesting.com")
                        if "hammer" in p["name"].lower())
```
> Confirm the pagination field names in Swagger. If they differ, updating one function fixes every test, which is the point of the abstraction.

🟣 **High/Complex: Protocol, TypedDict and Enum for strict typing**
```python
# framework/types.py
from enum import StrEnum
from typing import Any, Protocol, TypedDict, NotRequired

class HttpResponse(Protocol):
    status_code: int
    def json(self) -> Any: ...
    def raise_for_status(self) -> None: ...

class HttpSession(Protocol):                     # requests.Session fits; so does a test fake
    def get(self, url: str, **kwargs: Any) -> HttpResponse: ...
    def post(self, url: str, **kwargs: Any) -> HttpResponse: ...

class BookingDates(TypedDict):
    checkin: str
    checkout: str

class BookingPayload(TypedDict):
    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: NotRequired[str]

class Role(StrEnum):
    ADMIN = "admin"
    CUSTOMER = "user"

class FakeSession:                               # structural match: no inheritance needed
    def __init__(self, payload: Any) -> None:
        self.payload = payload
    def get(self, url: str, **kwargs: Any) -> "FakeResponse":
        return FakeResponse(self.payload)
    def post(self, url: str, **kwargs: Any) -> "FakeResponse":
        return FakeResponse(self.payload)

class FakeResponse:
    status_code = 200
    def __init__(self, payload: Any) -> None:
        self.payload = payload
    def json(self) -> Any:
        return self.payload
    def raise_for_status(self) -> None:
        return None
```
```toml
# pyproject.toml: make `framework` installable
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["framework"]
```

#### 🎤 Interview Q&A

<details><summary><b>[H] Generator vs list: when do you use each?</b></summary>

A list holds all items in memory and can be iterated many times, indexed and measured with `len`. A generator produces items lazily, uses constant memory, can be infinite, and can be consumed only once. Use generators for large or unbounded streams (paginated APIs, log lines, unique data), and lists when you need random access or multiple passes.
</details>

<details><summary><b>[H] How does a pytest <code>yield</code> fixture relate to generators?</b></summary>

It *is* a generator function. pytest calls `next()` to run setup up to `yield` (the yielded value is injected into the test), and after the test it resumes the generator to run teardown. That's why teardown runs even if the test fails.
</details>

<details><summary><b>[SH] Protocol vs ABC?</b></summary>

ABCs use nominal typing (you must inherit), give you shared implementation, and fail at instantiation if methods are missing. Protocols use structural typing (any object with the right methods fits), checked statically by mypy. Protocols suit dependency injection and fakes; ABCs suit families of classes you own.
</details>

<details><summary><b>[SH] What is the GIL and how does it affect parallel test execution?</b></summary>

The GIL lets one thread run Python bytecode at a time per process. I/O-bound work (HTTP, browser I/O) still overlaps because waiting releases the GIL, but CPU-bound work doesn't parallelise with threads. pytest-xdist sidesteps this by running tests in separate **processes**, each with its own interpreter. That also isolates global state, so session fixtures run once *per worker*.
</details>

<details><summary><b>[SH] How would you share a test framework across 10 repos?</b></summary>

Package it (pyproject + build backend), version it with semver, publish to an internal index (or install from a Git tag), keep a changelog, and give it its own CI with unit tests. Keep the core small and stable (config, clients, base page, reporting hooks) and put app-specific pages and clients in each product repo. Deprecate before removing.
</details>

#### 🤖 AI assist
- Paste mypy errors into AI and ask for an **explanation**, not a fix. Fix them yourself, since that's how typing clicks.

---

## 🏁 Phase checkpoint: P02

**Live-coding self-test (45 min, no AI):** from an empty file, write `calculate_totals` with Decimal rounding, a `@retry` decorator, and `json_diff`, each with asserts.

**AI mock interviewer prompt**
```text
You are interviewing me for a QA Automation role (Python round). Ask 6 conceptual
questions (data types, mutability, decorators, generators, exceptions, OOP) and
then give me 2 coding problems of increasing difficulty, one QA-flavoured (logs/JSON).
Don't show solutions. After each answer: score 1-5 and one improvement tip.
```
Record your results in `interview-notes/P02.md`.
