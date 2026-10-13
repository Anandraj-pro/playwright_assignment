# P00: Setup, Git, First Automation and Safe AI

> **Goal:** green UI and API tests on day 1, a working toolchain (Codespaces, dev container or local), Git habits good enough for code review, a quality skeleton you understand, CI on every PR, and safe AI habits from the start.
> **Apps:** SauceDemo and Restful-Booker (P00-00). **Prerequisites:** none. **Time:** ~20 h.
> **Essentials track:** P00-00 to P00-06. P00-07 is optional.

| ID | Task | Level | Time |
|---|---|---|---|
| P00-00 | Hello automation: your first UI and API tests | 🟢 | 2h |
| P00-01 | Your toolchain: Codespaces, dev container or local | 🟢 | 2h |
| P00-02 | Git fundamentals | 🟢 | 3h |
| P00-03 | PR workflow, conflicts and rebase | 🔵 | 3h |
| P00-04 | Tour the project skeleton and quality tooling | 🟢 | 2h |
| P00-05 | First workflow: lint and unit tests on every PR | 🟢 | 2h |
| P00-06 | AI pair-testing in your repo, safely | 🟢 | 3h |
| P00-07 | Automate your task tracker with the GitHub CLI (optional) | 🟣 | 3h |

---

### P00-00 · Hello automation: your first UI and API tests

**Level:** 🟢 Zero · **Time:** 2h · **App:** SauceDemo, Restful-Booker · **Deliverable:** `tests/hello/test_hello_api.py`, `tests/hello/test_hello_ui.py`

> **Day 1, before anything else.** You'll spend the next weeks learning the pieces properly. This task shows you where they lead, so every later concept has a hook: "that's the `assert` from day 1".

#### 📋 Task
1. **Create your own repo:** on this repo's GitHub page click **Use this template → Create a new repository**, name it `qe-hero-<yourname>`, and make it **private** if you'll try self-hosted runners later (P09-05).
2. **Open it with nothing to install:** on *your* repo page click **Code → Codespaces → Create codespace on main**. The first start takes about 5 minutes: it installs Python packages and the Chromium browser for you (`.devcontainer/devcontainer.json`).
   *Already have Python, uv and Git?* Clone the repo and run `make install` instead. Windows users: see P00-01 before installing anything.
3. Create `tests/hello/test_hello_api.py` from the 🟢 example. **Type it rather than pasting it**, then run `uv run pytest tests/hello -v`.
4. Create `tests/hello/test_hello_ui.py` from the 🟢 example and run it. Run it again with `--tracing on`, download `test-results/<test-name>/trace.zip`, and open it at https://trace.playwright.dev.
5. **Break each test on purpose:** change one expected value, run it, read the failure, then put it back.
6. Commit and push: `git add tests/hello && git commit -m "test: hello automation" && git push`.

**Done when**
- [ ] `uv run pytest tests/hello -v` shows at least 3 passed tests
- [ ] You saw every test fail when you broke it, and can say what each failure message told you
- [ ] In the trace, you can point to the step where the browser clicked **Login** and the network call that followed

#### 📘 User guide

**Concepts**
- **Automated test:** code that performs steps *and checks an expected result*. Without a check, it's a script, not a test.
- **API test:** talks to the application's backend over HTTP, with no browser. It's fast and stable, and it's where most business rules can be checked.
- **UI test:** drives a real browser like a user would. It's slower, but it's the only way to prove the screen works.
- **pytest:** finds files named `test_*.py` and functions named `test_*`, runs them and reports pass or fail. `assert` is how a test checks something.
- **Playwright:** controls Chromium, Firefox and WebKit. Its `page` fixture hands every test a fresh browser tab.
- **Trace:** a recording of each step (DOM snapshots, network calls, console logs) that you can replay after the run.

**Deep dive**

**Read the API test like a sentence:** *send a request → check the status code → check the body.* Those are two different kinds of check. The *status* says whether the server accepted the request; the *body* says whether it did the right thing. Most real API bugs hide in the body: a 200 with the wrong price is still a bug.

**Read the UI test the same way:** go to the page, find the username field *by what a user sees* (its placeholder), fill it, click the button *by its role and name*, then `expect` the URL and the heading. Notice there's **no `sleep` anywhere**. Playwright waits for elements to be ready before acting, and `expect` keeps retrying until the condition is true or a timeout expires. P05 explains why that one design decision removes most flaky tests.

**Why break your own tests?** A test you've never seen fail might not be able to fail: a typo in an assertion, or checking the wrong thing, can make it pass forever. Breaking it on purpose proves it's actually checking something, and teaches you to read failure messages, which is most of a QE's debugging day.

**Why Codespaces for day 1?** It's the same preinstalled environment for everyone, it runs in the browser, and it works on locked-down company laptops. Personal GitHub accounts get a free monthly allowance: check your usage under *Settings → Billing*, and **stop the codespace** when you finish a session. In P00-01 you'll decide whether to also install everything locally.

**Examples**

🟢 **Low: the two hello files**
```python
# tests/hello/test_hello_api.py
import requests

BASE = "https://restful-booker.herokuapp.com"


def test_api_is_up() -> None:
    response = requests.get(f"{BASE}/ping", timeout=10)
    assert response.status_code == 201  # not 200! You'll find out why in P04-01


def test_can_list_bookings() -> None:
    response = requests.get(f"{BASE}/booking", timeout=10)
    assert response.status_code == 200
    assert len(response.json()) > 0, "expected at least one booking id"
```
```python
# tests/hello/test_hello_ui.py
from playwright.sync_api import Page, expect


def test_standard_user_can_log_in(page: Page) -> None:
    page.goto("https://www.saucedemo.com/")
    page.get_by_placeholder("Username").fill("standard_user")
    page.get_by_placeholder("Password").fill("secret_sauce")
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url("https://www.saucedemo.com/inventory.html")
    expect(page.get_by_text("Products", exact=True)).to_be_visible()
```
```bash
uv run pytest tests/hello -v                 # run them
uv run pytest tests/hello -v --tracing on    # record traces into test-results/
```

🔵 **Medium: let Playwright write the clicks, then add the check it forgot**

Run `uv run playwright codegen https://www.saucedemo.com` on your own machine (or in the Codespaces desktop: open the forwarded port **6080** and use the password `vscode`). Log in and add the backpack to the cart while codegen writes the code. Then turn the recording into a test:
```python
# tests/hello/test_hello_ui.py (add this test below the first one)
def test_add_backpack_to_cart(page: Page) -> None:
    page.goto("https://www.saucedemo.com/")
    page.locator('[data-test="username"]').fill("standard_user")
    page.locator('[data-test="password"]').fill("secret_sauce")
    page.locator('[data-test="login-button"]').click()
    page.locator('[data-test="add-to-cart-sauce-labs-backpack"]').click()
    # Codegen records actions, not checks. This line is the part you add:
    expect(page.locator('[data-test="shopping-cart-badge"]')).to_have_text("1")
```
Codegen records *what you did*, never *what should be true*. Adding the `expect` is the part that makes it a test, and it's your job.

🟣 **High/Complex: a test that creates its own data and proves it round-trips**
```python
# tests/hello/test_hello_layers.py
import uuid

import requests

BOOKER = "https://restful-booker.herokuapp.com"


def test_booking_i_create_can_be_read_back() -> None:
    lastname = f"Hello-{uuid.uuid4().hex[:8]}"  # unique, so other people's data can't confuse the test
    new = {
        "firstname": "Day1",
        "lastname": lastname,
        "totalprice": 100,
        "depositpaid": True,
        "bookingdates": {"checkin": "2026-01-01", "checkout": "2026-01-02"},
    }
    created = requests.post(f"{BOOKER}/booking", json=new, timeout=10)
    assert created.status_code == 200, created.text
    booking_id = created.json()["bookingid"]

    json_only = {"Accept": "application/json"}
    fetched = requests.get(f"{BOOKER}/booking/{booking_id}", headers=json_only, timeout=10)
    assert fetched.status_code == 200
    assert fetched.json()["lastname"] == lastname

    found = requests.get(f"{BOOKER}/booking", params={"lastname": lastname}, timeout=10).json()
    assert {"bookingid": booking_id} in found
```
Three habits you'll use for the next six months are already here: the test **owns its data** (a unique name), it checks the **write and the read** separately, and every HTTP call has a **timeout**.

#### 🎤 Interview Q&A

<details><summary><b>[Z] What's the difference between a UI test and an API test, and when would you pick each?</b></summary>

An API test sends HTTP requests straight to the backend and checks responses, so it's fast, stable and good for business rules, validation and data. A UI test drives a browser like a user, so it's slower and more fragile but proves the screens and user journeys work. Put most checks at the API level and keep UI tests for the critical journeys a user actually walks through.
</details>

<details><summary><b>[Z] What turns a script into a test?</b></summary>

An expected result that's checked automatically. A script performs steps; a test performs steps *and* asserts an outcome, so it can pass or fail on its own without a human watching. The check should target the behaviour that matters (the right data, the right page), not just "no error happened".
</details>

<details><summary><b>[Z] Why don't Playwright tests need <code>sleep</code>?</b></summary>

Playwright auto-waits before every action (the element must be attached, visible, stable, enabled and able to receive events), and `expect` assertions retry until they pass or time out. A fixed sleep is either too short (flaky) or too long (slow); waiting on a condition is both faster and more reliable.
</details>

<details><summary><b>[H] Why should you watch a new test fail before trusting it?</b></summary>

A test that has never failed might be unable to fail: a wrong locator that matches something else, an assertion on the wrong value, or a swallowed exception. Breaking the product (or the expected value) on purpose and seeing a clear failure proves the test checks what you think it checks, and shows you what the failure message will look like when it matters.
</details>

<details><summary><b>[H] What's in a Playwright trace, and why is it better than a screenshot?</b></summary>

For every action: DOM snapshots before and after, the locator used, the network requests and responses, console logs and timing. A screenshot shows one moment; a trace lets you step through the whole test and see *why* it failed (a slow request, the wrong element, an error in the console). It's the fastest way to debug CI failures you can't reproduce locally.
</details>

#### 🤖 AI assist
- Paste your UI test into an AI assistant and ask: *"Explain each line to a manual tester. What would make this test fail?"* Check one of its claims against the Playwright docs.
- Don't paste anything secret. P00-06 sets up your AI rules properly.

---

### P00-01 · Your toolchain: Codespaces, dev container or local

**Level:** 🟢 Zero · **Time:** 2h · **App:** — · **Deliverable:** `README.md`, `docs/setup.md`

#### 📋 Task
1. **Choose your route** (see the deep dive): **A. Codespaces** (what you used in P00-00), **B. a dev container** on your own machine (Docker + VS Code, same config), or **C. a local install**. Most people settle on C, with A as a backup when their laptop misbehaves.
2. **Route C only:** install **Python 3.12+**, **uv**, **Git**, **GitHub CLI (`gh`)**, a **Docker runtime** (Docker Desktop, Colima, Rancher Desktop or Podman), **Node.js LTS** (needed for Playwright MCP in P12) and an IDE (VS Code or PyCharm). **On Windows,** first install **WSL2 with Ubuntu** (`wsl --install` in an administrator PowerShell) and do *everything* inside WSL: clone there, install uv there, and turn on WSL integration in your Docker runtime.
3. Configure your Git identity (`user.name`, `user.email`) and authenticate: `gh auth login`.
4. Replace the top of `README.md` with *your* goal and target role.
5. Record your route, OS and every tool's version in `docs/setup.md`, then commit and push.

**Done when**
- [ ] In your chosen environment, `python --version`, `uv --version`, `git --version`, `gh auth status`, `docker run hello-world` and `node --version` all succeed
- [ ] `make install && make test` is green (or the plain commands from P00-04)
- [ ] `docs/setup.md` lists your route, OS and versions, and your new README is visible on GitHub

#### 📘 User guide

**Concepts**
- **Interpreter:** the `python` program that runs your code. Multiple versions can coexist.
- **Virtual environment (venv):** an isolated folder of packages per project, so project A's `pytest 8` doesn't fight project B's `pytest 7`.
- **Package manager:** installs libraries. `pip` is the classic one; **`uv`** is a fast modern replacement that also manages venvs, Python versions and lockfiles.
- **PATH:** the list of folders your shell searches for commands. "Command not found" usually means a PATH problem.
- **Git vs GitHub:** Git is the version-control tool on your machine; GitHub hosts repos and adds PRs, Actions and Issues.
- **Dev container:** a Docker image plus a config file (`.devcontainer/devcontainer.json`) that describes the whole development environment. VS Code and Codespaces build it for you, so everyone gets identical tools.
- **WSL2:** the Windows Subsystem for Linux, a real Linux environment inside Windows. Test tooling (bash, make, Docker, Playwright's Linux dependencies) behaves the same there as on CI runners.

**Deep dive**

Automation code is only as reliable as the environment it runs in. The classic "works on my machine" bug is usually a **different Python or library version**. Three habits prevent it:

1. **One venv per project.** `uv venv` creates `.venv/`, and `uv run <cmd>` runs inside it automatically, so you never "forget to activate".
2. **Pinned dependencies.** `uv add requests` writes the dependency to `pyproject.toml` *and* the exact resolved versions to `uv.lock`. Commit both. A teammate or CI running `uv sync` gets identical versions.
3. **Recorded tool versions.** Your `docs/setup.md` becomes the first thing you check when "it worked yesterday".

**Authentication:** `gh auth login` stores a token so `git push` and `gh` commands work. HTTPS with a token and SSH keys are both fine. SSH avoids token expiry, while HTTPS works through strict corporate proxies.

**Docker runtime choice:** Docker Desktop needs a paid licence at larger companies. Colima (macOS/Linux), Rancher Desktop and Podman are free alternatives that all run the same `docker`/`docker compose` commands used later.

**Which route?**

| Route | Best when | Watch out for |
|---|---|---|
| **A. Codespaces** | Locked-down laptop, no admin rights, or you want zero setup | Monthly free quota: stop the codespace when you're done. Headed browsers run in the forwarded desktop on port 6080. |
| **B. Dev container** | You have Docker and VS Code and want the exact CI-like environment offline | Needs Docker running and a few GB of disk |
| **C. Local install** | You'll use this machine daily and want the fastest feedback | You own the versions: `docs/setup.md` and the doctor script below keep you honest |

**Windows:** use WSL2 for route C. Native Windows mostly works with uv, but you'll hit differences in paths, shells and `make` that CI (Linux) doesn't have, and debugging those teaches you nothing about testing. **Corporate proxy?** Set `HTTPS_PROXY`, and ask IT for the proxy's root certificate if `uv sync` or `playwright install` fails with SSL errors. That's a very common first-week blocker.

**Examples**

🟢 **Low: verify the toolchain by hand**
```bash
python3 --version        # 3.12+ expected
uv --version
git --version
gh auth status
docker run --rm hello-world
node --version
git config --global user.name  "Your Name"
git config --global user.email "you@example.com"
```

🔵 **Medium: a doctor script anyone can run**
```bash
#!/usr/bin/env bash
# scripts/doctor.sh: prints tool versions, fails if any are missing
set -euo pipefail
for tool in python3 uv git gh docker node; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf "%-8s %s\n" "$tool" "$("$tool" --version 2>&1 | head -1)"
  else
    echo "MISSING: $tool" >&2; exit 1
  fi
done
docker info >/dev/null 2>&1 || { echo "Docker daemon not running" >&2; exit 1; }
```

🟣 **High/Complex: a version-aware doctor in Python (reusable in CI later)**
```python
# scripts/doctor.py
import re, shutil, subprocess, sys

REQUIRED = {"python3": (3, 12), "uv": (0, 4), "git": (2, 40), "docker": (24, 0), "node": (20, 0)}

def version_of(tool: str) -> tuple[int, ...] | None:
    if not shutil.which(tool):
        return None
    out = subprocess.run([tool, "--version"], capture_output=True, text=True).stdout
    match = re.search(r"(\d+)\.(\d+)", out)
    return tuple(map(int, match.groups())) if match else None

def main() -> int:
    failed = False
    for tool, minimum in REQUIRED.items():
        found = version_of(tool)
        ok = found is not None and found >= minimum
        failed |= not ok
        print(f"{'✅' if ok else '❌'} {tool:8} found={found} need>={minimum}")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())
```
Tuple comparison (`(3, 13) >= (3, 12)`) makes version checks trivial, and the non-zero exit code lets CI fail fast.

#### 🎤 Interview Q&A

<details><summary><b>[Z] What is a virtual environment and why do test projects need one?</b></summary>

An isolated set of Python packages per project. Test suites depend on exact versions of pytest, Playwright and so on. Without isolation, installing something for project B can silently break project A. With a venv plus a lockfile, every machine and CI run uses the same versions, which makes results reproducible.
</details>

<details><summary><b>[Z] What is a dev container, and why do teams use them?</b></summary>

A container image plus a config file that defines the full development environment: language version, tools, browsers, editor extensions. Anyone (or Codespaces) can build it and get an identical setup in minutes. Teams use them to cut onboarding from days to minutes, to remove "works on my machine" differences, and to keep local environments close to CI.
</details>

<details><summary><b>[H] What is a lockfile and should you commit it?</b></summary>

`pyproject.toml` says what you *want* (`requests>=2.31`). The lockfile (`uv.lock`) records exactly what was *resolved*, including transitive dependencies and hashes. For an application or test repo, **commit it**. It makes CI deterministic and turns "a new library version broke us" into an explicit, reviewable PR (e.g., from Dependabot) instead of a surprise.
</details>

<details><summary><b>[H] A test passes on your laptop but fails in CI. What do you check first?</b></summary>

Environment differences, in order: (1) tool and library versions (lockfile used? same Python?), (2) config and env vars (base URL, secrets present?), (3) data (does CI have the data the test assumes?), (4) timing (CI is slower; is there a missing wait?), (5) OS/browser differences (headless, fonts, timezone, locale). Reproduce locally with CI's settings, or in the same container image.
</details>

<details><summary><b>[SH] What belongs in the README of a test-automation repo?</b></summary>

What it tests and what it doesn't, a one-command quick start, prerequisites with versions, how to run subsets (smoke/regression/env), how config and secrets work, the folder architecture and conventions, how CI gates work, how to debug failures (reports, traces), and ownership/contribution rules. The test: a new joiner gets a green run in under 15 minutes without asking anyone.
</details>

#### 🤖 AI assist
- Paste an install error (not your tokens!) and ask *"explain the cause, then give the fix"*.
- Ask: *"Explain PATH and virtual environments to a manual tester using an analogy."*

---

### P00-02 · Git fundamentals

**Level:** 🟢 Zero · **Time:** 3h · **App:** — · **Deliverable:** `docs/git-cheatsheet.md`

#### 📋 Task
In a **scratch repo** (`mkdir git-lab && cd git-lab && git init`), practise each scenario and record the command and what it does *in your own words*:
1. Commit cycle: `status`, `add`, `commit`, `diff` vs `diff --staged`, `log --oneline --graph`.
2. Branches: create, switch, merge (fast-forward and 3-way).
3. Undo: `restore`, `restore --staged`, `commit --amend`, `reset --soft/--mixed/--hard`, `revert`.
4. Save work: `stash`, `stash pop`.
5. Recover: lose a commit with `reset --hard`, then get it back with `reflog`.
6. Find a bad commit with `git bisect`.

**Done when**
- [ ] `docs/git-cheatsheet.md` has ≥20 commands, each with a one-line explanation and "when I'd use it"
- [ ] You can explain the three trees (working tree, index, HEAD) on a whiteboard

#### 📘 User guide

**Concepts**
- **Working tree:** the files you edit. **Index/staging area:** what goes into the next commit. **HEAD:** the commit you're on.
- **Commit:** a *snapshot* of the whole project plus a pointer to its parent(s) and a message.
- **Branch:** a movable *pointer* to a commit. Creating one is instant.
- **Remote / origin:** a copy of the repo elsewhere (GitHub). `origin` is the default name.
- **Reflog:** a local diary of everywhere HEAD has pointed. It's your safety net.

**Deep dive**

Git is a graph of snapshots. Each commit points to its parent, and a branch is just a label on one commit. Once you see this, every command is "move a pointer" or "make a new snapshot":

| Command | What really happens | Rewrites history? |
|---|---|---|
| `commit` | New snapshot; the branch pointer moves forward | No |
| `merge` | New commit with **two** parents (or just moves the pointer if fast-forward) | No |
| `reset --soft X` | Branch pointer → X; changes stay **staged** | Yes |
| `reset --mixed X` | Branch pointer → X; changes stay in the **working tree** | Yes |
| `reset --hard X` | Branch pointer → X; changes **discarded** | Yes |
| `revert X` | New commit that *undoes* X | No (safe on shared branches) |
| `rebase main` | Replays your commits on top of main as *new* commits | Yes |

**The golden rule:** never rewrite history other people have pulled (reset, rebase, amend on a shared branch). Use `revert` there instead.

**Reflog:** even after `reset --hard`, the "lost" commit still exists for a while (default ~90 days) and the reflog still points to it. `git reset --hard HEAD@{1}` usually brings it back. Reflog is **local only**; it isn't pushed.

**Bisect** binary-searches history for the commit that broke something. With 1,000 commits it needs about 10 steps. `git bisect run <command>` automates it with any command that exits 0 for good and non-zero for bad, such as a pytest test.

**Examples**

🟢 **Low: the everyday cycle**
```bash
echo "# Lab" > README.md
git add README.md
git commit -m "docs: add readme"
git switch -c feature/login
echo "login notes" >> README.md
git diff                    # unstaged changes
git add -A && git diff --staged
git commit -m "docs: login notes"
git switch main && git merge feature/login   # fast-forward
git log --oneline --graph --all
```

🔵 **Medium: an undo cookbook**
| Situation | Command |
|---|---|
| Discard edits to a file | `git restore file.py` |
| Unstage a file | `git restore --staged file.py` |
| Fix the last commit message (not pushed) | `git commit --amend -m "better message"` |
| Undo the last commit but keep changes | `git reset --soft HEAD~1` |
| Undo a commit that's already pushed | `git revert <sha>` |
| Park work to switch branches | `git stash` … `git stash pop` |

🟣 **High/Complex: recover "lost" work, then bisect a regression**
```bash
# 1. Lose a commit
git commit --allow-empty -m "important work"
git reset --hard HEAD~1          # "oops"
git reflog                       # find: abc123 HEAD@{1}: commit: important work
git reset --hard abc123          # recovered

# 2. Find which commit broke a test
git bisect start
git bisect bad                   # current commit is broken
git bisect good v1.0             # this tag was fine
git bisect run uv run pytest tests/unit/test_cart.py -q   # Git tests each midpoint
git bisect reset
```

#### 🎤 Interview Q&A

<details><summary><b>[Z] What's the difference between <code>git fetch</code> and <code>git pull</code>?</b></summary>

`fetch` downloads new commits from the remote and updates `origin/main` but doesn't touch your branch. `pull` = `fetch` + integrate (merge, or rebase with `--rebase`) into your current branch. Fetch first when you want to *see* what changed before integrating.
</details>

<details><summary><b>[Z] <code>reset</code> vs <code>revert</code>?</b></summary>

`reset` moves the branch pointer backwards, *removing* commits from the branch's history. That's fine locally but dangerous on shared branches. `revert` adds a *new* commit that undoes an earlier one, so history stays intact and it's safe after pushing.
</details>

<details><summary><b>[H] Merge vs rebase: when do you use each?</b></summary>

**Merge** preserves true history and adds a merge commit. It's safe for shared branches. **Rebase** rewrites your commits on top of the target, giving linear history, but changes commit hashes. My default: rebase my *own* feature branch onto `main` to stay current and keep history clean, and merge (usually squash-merge) into `main` via PR. Never rebase a branch others are working on.
</details>

<details><summary><b>[H] What is "detached HEAD"?</b></summary>

HEAD points directly at a commit instead of a branch, e.g. after `git checkout <sha>` or a tag. You can look around and even commit, but those commits belong to no branch and can be lost. Fix: `git switch -c new-branch` to keep them.
</details>

<details><summary><b>[SH] A test started failing sometime in the last 200 commits. How do you find the culprit fast?</b></summary>

`git bisect` with automation: `git bisect start; git bisect bad HEAD; git bisect good <last-known-good>; git bisect run pytest path::test -q`. That's about 8 steps for 200 commits. Caveats: the test must be deterministic (a flaky test gives false answers, so run it several times per step), and each commit must be buildable (`git bisect skip` if not). Then read the culprit's diff and confirm by reverting it locally.
</details>

#### 🤖 AI assist
- Ask AI to **quiz you**: *"Give me 10 Git scenarios ('I committed to the wrong branch…'). I'll answer with commands; you grade me."*
- Don't ask AI to write the cheatsheet. Writing it *is* the learning.

---

### P00-03 · PR workflow, conflicts and rebase

**Level:** 🔵 Hero · **Time:** 3h · **App:** — · **Deliverable:** `.github/PULL_REQUEST_TEMPLATE.md`, a merged PR

#### 📋 Task
1. Create a GitHub issue "Add PR template". Branch as `task/P00-03-pr-template`.
2. Add `.github/PULL_REQUEST_TEMPLATE.md` (what/why, how tested, screenshots/traces, checklist, **AI-assisted?** box).
3. **Conflict lab:** create `branch-a` and `branch-b`, and change the *same line* of `README.md` in both. Merge `branch-a` into main, then:
   - resolve `branch-b` via **merge** (read the conflict markers), then
   - repeat the exercise using **rebase** + `git push --force-with-lease`.
4. Open a PR using conventional commit titles, self-review it (comment on your own diff), and **squash-merge**.
5. **Peer review:** ask your buddy or a cohort peer to review your PR using the [PR review rubric](../SUPPORT.md#4-pr-review-rubric), and review one of theirs. From now on you review **one peer PR per phase**. Working solo? Ask an AI to review against the rubric, then judge its review.

**Done when**
- [ ] PR template exists and is used in your PR
- [ ] You've resolved a conflict with merge *and* with rebase
- [ ] Your merged PR is linked to its issue (`Closes #N`)
- [ ] You've reviewed one peer's PR with the rubric, and left at least one comment about test quality (not just style)

#### 📘 User guide

**Concepts**
- **Pull request (PR):** a request to merge a branch, with review, discussion and CI checks.
- **Conventional commits:** `type(scope): summary`, where type is `feat`, `fix`, `test`, `docs`, `refactor`, `ci`, `chore`, etc. This enables readable history and automated changelogs.
- **Merge strategies on GitHub:** *merge commit* (keeps all commits), *squash* (one commit per PR, the common choice), *rebase* (linear, keeps commits).
- **Conflict:** Git can't auto-combine two changes to the same lines, so a human decides.
- **`--force-with-lease`:** a force push that refuses if the remote has commits you haven't seen. It's the safe force push.

**Deep dive**

**Why PRs matter more in test code:** test code decides whether a release ships. A bad assertion that always passes is worse than no test. Reviewers of test PRs look for: *does this test fail when the feature breaks?*, no hard waits, isolated data, clear names, no secrets, and correct layer (API vs UI).

**Anatomy of a conflict:**
```text
<<<<<<< HEAD            ← what's on the branch you're merging INTO
Base URL: staging
=======
Base URL: production
>>>>>>> branch-b        ← what's coming in
```
Edit the file to the correct final content, delete the markers, `git add`, then `git commit` (merge) or `git rebase --continue` (rebase).

**Rebase flow:** `git switch branch-b && git fetch && git rebase origin/main`. Git replays each of your commits, and you may resolve conflicts once per commit. Afterwards your branch has *new* hashes, so a normal push is rejected. Use `git push --force-with-lease`. Plain `--force` would silently overwrite a teammate's push. `--force-with-lease` won't.

**Branching models:** *GitFlow* (develop/release/hotfix branches) suits scheduled releases. *Trunk-based* (short-lived branches into `main` behind CI gates) suits continuous delivery and is what this repo uses.

**Examples**

🟢 **Low: branch → PR with the GitHub CLI**
```bash
git switch -c task/P00-03-pr-template
git add .github/PULL_REQUEST_TEMPLATE.md
git commit -m "docs(repo): add pull request template"
git push -u origin HEAD
gh pr create --fill --body "Closes #3"
```

🔵 **Medium: a PR template that makes reviews faster**
```markdown
## What & why
<!-- one paragraph; link the task: Closes #N -->

## How was it tested?
- [ ] Ran locally: `make test` (paste summary)
- [ ] New tests FAIL when the feature is broken (I checked)

## Evidence
<!-- screenshots / trace links / report link -->

## Checklist
- [ ] No hard waits, no hard-coded secrets/URLs
- [ ] Tests create and clean their own data
- [ ] AI-assisted? If yes, what for:
```

🟣 **High/Complex: rebase onto an updated main, with a conflict**
```bash
git switch branch-b
git fetch origin
git rebase origin/main
# CONFLICT in README.md → edit the file, remove markers
git add README.md
git rebase --continue
uv run pytest -q                      # re-test after rewriting history!
git push --force-with-lease
```
Also try `git rerere` (`git config rerere.enabled true`). It remembers how you resolved a conflict and reapplies it automatically, which helps with long-lived branches.

#### 🎤 Interview Q&A

<details><summary><b>[Z] What makes a good commit message?</b></summary>

A short imperative summary (≤72 chars) of *what* changed, and a body explaining *why* if it's not obvious. For example: `fix(api): add timeout to booking client` rather than `fixed stuff`. Conventional-commit prefixes make history scannable.
</details>

<details><summary><b>[H] What do you look for when reviewing someone's test-automation PR?</b></summary>

(1) **Does the test actually fail when the feature breaks?** That means meaningful assertions, not just "no exception". (2) Right layer: could a UI test be an API test? (3) Isolation: own data, no order dependency. (4) No hard waits or brittle locators (XPath with indexes). (5) Readable names and failure messages. (6) No secrets or hard-coded environments. (7) Reuse of framework helpers instead of copy-paste. (8) CI evidence that it passed, ideally in parallel.
</details>

<details><summary><b>[H] <code>--force</code> vs <code>--force-with-lease</code>?</b></summary>

`--force` overwrites the remote branch unconditionally and can delete a teammate's commits. `--force-with-lease` only overwrites if the remote is still where you last saw it, otherwise it refuses. Always use the lease version after a rebase.
</details>

<details><summary><b>[SH] Five teams contribute to one test repo. What branching and merge policy do you set?</b></summary>

Trunk-based: short-lived branches, PRs into a protected `main`, squash merges, required CI checks (lint, type check, smoke), CODEOWNERS per area (framework core owned by the platform team, suites owned by each product team), and at least one review from an owner. Framework changes need a changelog entry and are released with tags if other repos consume the framework as a package. Add a merge queue if main breaks from "green individually, red together" PRs.
</details>

#### 🤖 AI assist
- After a conflict, ask AI *"explain what each side of this conflict is trying to do"* (paste the hunk), then decide yourself.
- Use AI to review your PR description: *"Is anything unclear to a reviewer?"*

---

### P00-04 · Tour the project skeleton and quality tooling

**Level:** 🟢 Zero · **Time:** 2h · **App:** — · **Deliverable:** `docs/tooling.md`

> Your repo **already contains a working skeleton**, so you don't have to configure five tools before writing your first line of Python. Your job here is to run it, break it, and explain it. Building one from scratch is an optional 🟣 stretch below.

#### 📋 Task
1. Find these files in your repo: `pyproject.toml`, `uv.lock`, `Makefile`, `.pre-commit-config.yaml`, `.gitignore`, `.env.example`, `.devcontainer/devcontainer.json`, `framework/__init__.py`, `tests/unit/test_sanity.py` and `.github/workflows/task-check.yml`.
2. Run `make install`, `make lint` and `make test`. **No `make`** (e.g. Windows PowerShell)? Run the plain `uv run …` commands from the 🟢 example instead.
3. On a scratch branch, **make each tool catch something**, then throw the branch away:
   - **ruff:** add an unused `import os` to `framework/__init__.py`, then run `make lint`
   - **ruff S113:** add `requests.get("https://example.com")` without a `timeout` in a new `framework/tmp.py`
   - **mypy:** add `def add(a: int, b: int) -> int: return str(a + b)` to `framework/tmp.py`
   - **gitleaks:** create `secret.txt` containing a fake GitHub token (see the 🟢 example), `git add` it and try to commit
4. Write `docs/tooling.md`: one short paragraph per file from step 1 covering what it does, when it runs, and what would go wrong without it.

**Done when**
- [ ] `make install && make lint && make test` (or the plain commands) is green
- [ ] You've seen ruff, mypy and gitleaks each block a change, and none of those changes were committed
- [ ] `docs/tooling.md` explains every skeleton file in your own words
- [ ] *(Optional 🟣 stretch)* You rebuilt the skeleton in an empty scratch repo (🟣 example) and can explain every difference from the template

#### 📘 User guide

**Concepts**
- **`pyproject.toml`:** the single config file for dependencies *and* tool settings (pytest, ruff, mypy).
- **`uv.lock`:** the exact version of every package, direct and indirect, so every machine and CI run installs the same thing.
- **Linter** finds bugs and bad patterns (unused imports, missing timeouts). **Formatter** fixes layout. **Ruff** does both, fast.
- **Type checker (mypy):** catches `None` bugs and wrong types before the code runs.
- **pre-commit:** runs checks on the files you're committing, at `git commit` time. It's the cheapest quality gate you'll ever have (gate "G0").
- **Secret scanning (gitleaks):** detects API keys and passwords before they reach Git history.
- **Makefile:** short names (`make lint`) for the long commands a team runs every day. Each target here is a thin wrapper around `uv run …`.

**Deep dive**

**Shift-left economics:** a lint error caught at commit time costs seconds; in CI, minutes; in code review, a round trip with a colleague; in production, an incident. The earlier the gate, the cheaper the fix. That's why the first gate lives on your own machine.

**Why ruff?** It replaces flake8, isort, pyupgrade, black and many plugins with one fast tool and one config section. The rules in your `pyproject.toml` are chosen deliberately: `E`/`F` (errors), `I` (import order), `B` (likely bugs), `UP` (modern syntax), `PT` (**pytest style**) and `S113` (an HTTP call without a timeout, which is how test suites hang forever).

**Why do the hooks call `uv run ruff`?** The template's pre-commit config runs ruff *from your locked environment* instead of downloading a separate copy. Your editor, your commit hook and CI then all use exactly the same ruff version, so a file that passes locally can't fail in CI for a version reason.

**Typing strategy:** strict typing on `framework/` (shared code, where one bug affects every test), lighter on `tests/`. It's a pragmatic split, and interviewers like hearing the reason for it.

**What's excluded, and why:** ruff skips `legacy-suite/` (deliberately bad code you'll rescue in P05-04) and Markdown files (the learning path's code samples are teaching material). pytest only collects from `tests/`, so `make test` never runs the legacy suite by accident.

**If a secret is ever committed:** (1) **rotate it immediately**, because it's compromised the moment it's pushed; (2) remove it from history (`git filter-repo`) and force-push; (3) add a scanning gate so it can't happen again. Deleting it in a new commit is *not enough*, because history keeps it.

**Examples**

🟢 **Low: the daily commands, with and without make**

| Task | With make | Plain command (any shell) |
|---|---|---|
| Install | `make install` | `uv sync` → `uv run playwright install chromium` → `uv run pre-commit install` |
| Lint | `make lint` | `uv run ruff check .` → `uv run ruff format --check .` → `uv run mypy` |
| Fix formatting | `make format` | `uv run ruff check --fix .` → `uv run ruff format .` |
| Test | `make test` | `uv run pytest -q` |
| Check a task | `make check TASK=P00-04` | `uv run python scripts/check_task.py P00-04 --run` |

```bash
# A fake GitHub token for the gitleaks exercise (random, so it looks real to the scanner)
python -c "import secrets, string; print('ghp_' + ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(36)))" > secret.txt
git add secret.txt && git commit -m "try to leak"     # gitleaks should block this
git restore --staged secret.txt && rm secret.txt
```

🔵 **Medium: read the tool config you were given**
```toml
[tool.ruff]
line-length = 110
target-version = "py312"
extend-exclude = ["legacy-suite", "*.md"]

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "PT", "S113"]   # S113 = HTTP call without timeout

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]          # allow assert in tests

[tool.mypy]
python_version = "3.12"
files = ["framework"]          # strict where it matters most
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]             # so tests can import python_basics/, framework/, ai/ from the repo root
addopts = "-ra --strict-markers"
markers = ["smoke: fast checks of the most important paths"]
```
For each line, write in `docs/tooling.md` what would change if you deleted it. For example, without `--strict-markers` a typo like `@pytest.mark.smoek` silently selects nothing.

🟣 **High/Complex (optional stretch): rebuild the skeleton from scratch**
```bash
mkdir /tmp/skeleton && cd /tmp/skeleton && git init
uv init --name qe-hero
uv add requests pytest playwright pytest-playwright
uv add --dev ruff mypy pre-commit types-requests
uv run playwright install chromium
```
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks: [{id: end-of-file-fixer}, {id: trailing-whitespace}, {id: check-yaml}, {id: check-toml}]
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1          # run `pre-commit autoupdate` to move to the latest release
    hooks: [{id: gitleaks}]
  - repo: local           # ruff from the locked environment: one version everywhere
    hooks:
      - {id: ruff, name: ruff check, entry: uv run ruff check --fix, language: system, types: [python]}
      - {id: ruff-format, name: ruff format, entry: uv run ruff format, language: system, types: [python]}
```
Then diff your result against the template (`diff -r`), and explain each difference in `docs/tooling.md`. This is exactly what you'd do when setting up a new team's test repo.

#### 🎤 Interview Q&A

<details><summary><b>[Z] What's the difference between a linter and a formatter?</b></summary>

A formatter changes *layout only* (spacing, quotes, line breaks) so code looks the same everywhere. A linter *analyses* code for probable bugs and bad practice (unused variables, missing timeouts, mutable defaults). Ruff does both.
</details>

<details><summary><b>[Z] What is a pre-commit hook, and why run checks before CI?</b></summary>

A script Git runs automatically at `git commit`. The pre-commit framework uses it to run fast checks (formatting, lint, secret scanning) on the files you're committing. Catching a problem there takes seconds and never reaches anyone else; the same problem found in CI costs a pipeline run and a context switch, and a leaked secret found after pushing has to be rotated.
</details>

<details><summary><b>[H] Someone committed an API key to the test repo. What do you do?</b></summary>

1) Rotate or revoke the key **first**, since it's already compromised. 2) Purge it from history (`git filter-repo` / BFG), force-push, and ask everyone to re-clone. 3) Check the provider's logs for misuse. 4) Prevent recurrence with gitleaks in pre-commit *and* CI plus GitHub secret scanning. 5) Move the secret to a secret store or CI secrets and load it from env.
</details>

<details><summary><b>[H] Why type-check test framework code?</b></summary>

Framework code is shared by every test, so a bug there multiplies. Types catch `None` handling, wrong return shapes and refactor breakage before runtime. They're also documentation: `def create_booking(...) -> Booking` tells the reader exactly what they get. I'm strict on `framework/` and lenient on `tests/` to keep test authoring fast.
</details>

<details><summary><b>[SH] Design the quality gates for a test-automation repository.</b></summary>

G0 local pre-commit (format, lint, secrets, under 15 s). G1 CI static checks on every push (ruff, mypy, gitleaks, actionlint/hadolint). G2 build and scan when Docker files change. G3 PR smoke (API + critical UI, parallel, under 10 min). G4 full regression on merge and nightly (matrix, sharded). AI review stays advisory. Principles: fast gates first, every gate has a time budget, flaky tests are quarantined rather than retried silently, and gates are required checks in branch protection.
</details>

#### 🤖 AI assist
- Ask AI to explain each ruff rule in `select` with one example violation, then **verify** by writing that violation and running `make lint`.

---

### P00-05 · First workflow: lint and unit tests on every PR

**Level:** 🟢 Zero · **Time:** 2h · **App:** — · **Deliverable:** `.github/workflows/ci.yml`, a status badge in `README.md`

> **Why this early?** From this task on, every PR you open is checked by CI, so you learn to read red builds from week 1 instead of week 16. Your repo already runs one workflow you didn't write, `task-check.yml`. Read it before you start: it's a small, complete example.

#### 📋 Task
1. Create `ci.yml` triggered on `pull_request` and on `push` to `main`, with one job that installs dependencies with `uv` and runs ruff, mypy and `tests/unit`.
2. Open a PR with a deliberate lint error, watch it go **red**, read the log, fix it, and watch it go **green**.
3. Add least-privilege `permissions`, `timeout-minutes` and `concurrency` (cancel superseded PR runs).
4. Add the workflow status badge to your README.

**Done when**
- [ ] Your PR history shows one red and one green run of the same workflow
- [ ] You can explain workflow → job → step → action, and where each runs

#### 📘 User guide

**Concepts**
- **Workflow:** a YAML file in `.github/workflows/` triggered by **events** (`push`, `pull_request`, `schedule`, `workflow_dispatch`, …).
- **Job:** a set of steps on one **runner** (a fresh VM for GitHub-hosted runners). Jobs run **in parallel** unless linked with `needs`.
- **Step:** either `run:` (a shell command) or `uses:` (an **action**, a reusable unit like `actions/checkout`).
- **Contexts:** `${{ github.* }}`, `${{ secrets.* }}`, `${{ runner.* }}`, `${{ steps.<id>.outputs.* }}`.
- **Exit codes:** any step exiting non-zero fails the job (the default shell uses `bash -e`).

**Deep dive**

**Each job starts from scratch.** A GitHub-hosted runner is a clean VM, so nothing survives between jobs except what you explicitly pass on: **artifacts** (files), **outputs** (small strings), or **caches** (dependency speed-ups). Steps *within* a job share the filesystem.

**`push` vs `pull_request`:** `pull_request` runs on a merge preview of the PR and is the gate for incoming changes. `push` to `main` verifies what actually landed. PRs from **forks** get a read-only token and **no secrets**, a deliberate security boundary (P09-05).

**Least privilege:** the automatic `GITHUB_TOKEN`'s permissions should be restricted (`permissions: contents: read`) and widened per job only where needed (e.g. `pages: write`).

**Pinning actions:** `@v4` is a *movable* tag. Pinning to a full commit SHA is immutable and protects against a compromised action release (supply-chain attacks have happened). Many teams pin SHAs for third-party actions and let Dependabot update them.

**Examples**

🟢 **Low: a minimal CI workflow**
```yaml
# .github/workflows/ci.yml
name: ci
on:
  pull_request:
  push:
    branches: [main]

jobs:
  static:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
      - run: uv sync --frozen
      - run: uv run ruff check .
      - run: uv run pytest tests/unit -q
```

🔵 **Medium: permissions, caching, timeouts and concurrency**
```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]

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
      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: true
      - run: uv sync --frozen
      - run: uv run ruff check . && uv run ruff format --check .
      - run: uv run mypy
      - run: uv run pytest tests/unit -q --junitxml=test-results/unit.xml
```

🟣 **High/Complex: lint the workflows too, skip docs-only changes, and write a job summary**
```yaml
on:
  pull_request:
    paths-ignore: ["**/*.md", "learning-path/**"]     # docs-only PRs skip CI (careful with required checks, P09-02)
  push:
    branches: [main]

jobs:
  static:
    name: G1 static
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v5
        with: { enable-cache: true }
      - run: uv sync --frozen
      - name: Lint workflows
        run: docker run --rm -v "$PWD:/repo" --workdir /repo rhysd/actionlint:latest -color
      - run: uv run ruff check . && uv run ruff format --check . && uv run mypy
      - run: uv run pytest tests/unit -q --junitxml=test-results/unit.xml
      - name: Summary
        if: always()
        run: uv run python scripts/junit_summary.py test-results/unit.xml "Unit tests" >> "$GITHUB_STEP_SUMMARY"
```
(`scripts/junit_summary.py` is built in P09-01.)

#### 🎤 Interview Q&A

<details><summary><b>[Z] Explain workflow, job, step, action and runner.</b></summary>

A workflow is an automated process defined in YAML and triggered by events. It contains jobs, each running on a runner (a VM or container). A job is a sequence of steps. A step runs a shell command or uses an action, a reusable packaged step like `actions/checkout`. Jobs run in parallel unless ordered with `needs`.
</details>

<details><summary><b>[H] How do jobs share data?</b></summary>

They don't share a filesystem. Use artifacts (upload in one job, download in another) for files like reports, job outputs for small values, and caches to speed up repeated dependency installs (not for passing results). Within a job, steps share the workspace.
</details>

<details><summary><b>[H] <code>pull_request</code> vs <code>push</code> triggers?</b></summary>

`pull_request` runs against the PR's merge result, which is the pre-merge gate. For fork PRs it gets a read-only token and no secrets. `push` runs on commits pushed to a branch, e.g. post-merge verification on `main`. Most pipelines use both.
</details>

<details><summary><b>[SH] Why restrict <code>GITHUB_TOKEN</code> permissions and pin actions by SHA?</b></summary>

Least privilege limits the damage if a step or dependency is compromised: a token that can only read contents can't push code or publish packages. Tags like `@v4` can be moved to malicious code if an action's repository is compromised. SHA pinning makes the reference immutable, and Dependabot keeps SHAs current.
</details>

#### 🤖 AI assist
- Paste a failing CI log (redact secrets) and ask AI for the root cause *and the line that proves it*.

---

### P00-06 · AI pair-testing in your repo, safely

**Level:** 🟢 Zero · **Time:** 3h · **App:** your repo · **Deliverable:** `CLAUDE.md` (or `AGENTS.md`), `docs/ai/usage-log.md`, `interview-notes/ai-mock.md`

#### 📋 Task
> **Why in week 1?** You'll use AI from day one whether or not anyone teaches you, so learn the safe habits before the bad ones set in. P12 builds on this with MCP servers, skills and agents.

1. **Check your company's AI policy first:** which tools are approved, and what data may go into them. Then install an AI coding assistant that works in your repo (e.g. **Claude Code**) and learn its permission settings.
2. Write a project instruction file (`CLAUDE.md`) with the conventions you already have: the `make` commands, "no hard waits", "every HTTP call has a timeout", "never commit secrets" and "explain before large changes". Add a **Conventions** section that you'll grow as the framework grows (P02–P05).
3. Do **3 pair-testing tasks** on what you have now, reviewing every diff line by line:
   - ask it to explain your P00-00 tests and two skeleton files, then check two of its claims against the official docs;
   - break a hello test, paste **only the failure output** and ask for the root cause *and the line that proves it*;
   - ask it to add one more hello test (e.g. update a booking you created), review it with the 🔵 checklist, and break it on purpose to prove it can fail.
4. Log each in `docs/ai/usage-log.md`: task, time with vs without (an estimate), issues you found in the AI's output, and your verdict.
5. Run one **AI mock interview** on P00 topics (Git, tooling, CI) and record your gaps in `interview-notes/ai-mock.md`.

**Done when**
- [ ] 3 logged tasks, each with at least one issue you caught in the AI's output (there's always one)
- [ ] `CLAUDE.md` is committed. From now on, whenever you catch the AI repeating a mistake, add a rule for it
- [ ] You can state the four AI rules from `learning-path/README.md` §5 without looking, and you tick "AI-assisted" in every PR where you used it

#### 📘 User guide

**Concepts**
- **Chat assistant vs agentic assistant:** a chat assistant answers. An agentic assistant **reads files, edits code and runs commands** in your repo.
- **Project instruction file:** `CLAUDE.md` (Claude Code) or `AGENTS.md` (a cross-tool convention) is loaded as persistent context: your team's rules.
- **Permission modes:** control what the assistant may do without asking (edit files, run commands).
- **Review discipline:** treat AI changes like a PR from a fast but inexperienced colleague.

**Deep dive**

**What AI gets wrong in test code, most often:** weak assertions (checks that something is "visible" instead of verifying values), invented locators or API fields, `sleep`s, ignoring your fixtures and duplicating setup, over-mocking so the test can't fail, tests that pass for the wrong reason, and outdated library APIs. Your review checklist should target exactly these.

**Instruction files are leverage.** Every convention you write once (locator priority, "use factories", "no hard waits") is applied to every future AI change. Keep the file short and concrete, with commands and examples, and update it when you catch a repeated mistake.

**Measure honestly.** "AI made me faster" is an opinion. Track time and rework. Some tasks (boilerplate, test data, explaining errors) get much faster, while others (subtle flaky failures, framework design) often don't.

**Examples**

🟢 **Low: `CLAUDE.md` for your repo**
```markdown
# QE Hero repo: rules for AI assistants

## Commands
- Install: `make install` · Lint: `make lint` · Tests: `make test` · Check a task: `make check TASK=P00-06`

## Conventions (grow this list as the framework grows)
- NEVER use time.sleep or page.wait_for_timeout in tests. Use expect(...) (and later wait_until, P02-05).
- Every HTTP call has a timeout. No secrets or tokens in code, prompts or logs.
- Every test creates and cleans up its own data. No reliance on test order.
- Locators (from P05): get_by_role > get_by_label/placeholder > get_by_test_id > CSS. No XPath without a comment.
- Framework layers (from P04/P05): framework/api/* clients, framework/pages/* page objects, framework/data/factories.py.

## Working style
- Explain your plan before changing more than 2 files.
- After changes, run lint and the affected tests, and show the output.
```

🔵 **Medium: a pair-testing prompt plus a review checklist**
```text
Add one test to tests/hello/test_hello_layers.py: create a booking, update its
totalprice with PUT (auth: POST /auth with the demo credentials from DEMO_APPS.md),
then read it back and check the new price. Follow CLAUDE.md. Don't change existing
tests. Run the file afterwards and show me the output.
```
| Review check | Pass? |
|---|---|
| Still fails if the feature breaks? (break it and see) | |
| No sleeps or hard-coded waits | |
| Locators follow priority, none invented | |
| Uses existing fixtures and factories | |
| Assertions are specific (values, not just visibility) | |
| No secrets or environment URLs hard-coded | |

🟣 **High/Complex: judge AI-written tests objectively with mutation checks**
```markdown
<!-- docs/ai/usage-log.md -->
| Date | Task | AI time | Est. manual | Issues found in AI output | Tests killed mutants? | Verdict |
|---|---|---|---|---|---|---|
| 2026-10-01 | Unit tests for wait_until | 6 min | 25 min | Slept for real 10s; missed timeout message check | 3/5 → added 2 tests → 5/5 | Keep, after fixes |
```
Procedure (come back to this after P03-01): for each AI-written test, apply 3–5 small **mutations** to the code under test (P03-01). A test that stays green under mutation is decoration, whoever wrote it. This is how you *measure* AI-generated test quality instead of guessing.

#### 🎤 Interview Q&A

<details><summary><b>[Z] How do you use AI in your day-to-day QA work?</b></summary>

As a pair: drafting test ideas from stories, generating test data, scaffolding page objects or clients from real HTML or specs, explaining errors and traces, and quizzing me. Everything is grounded in real context and reviewed. I keep team conventions in an instruction file and never paste secrets or customer data. For example: "I cut page-object scaffolding time by about half, but I always review locators and assertions."
</details>

<details><summary><b>[H] What are the risks of AI-generated test code?</b></summary>

Tests that can't fail (weak or missing assertions, over-mocking), invented locators or APIs, hard waits and flakiness, duplicated setup that ignores the framework, outdated library usage, security issues (logged secrets), and false confidence from high test counts. Mitigate with conventions in instruction files, review checklists, running the tests, and mutation checks.
</details>

<details><summary><b>[H] How do you review a PR written mostly by AI?</b></summary>

The same bar as any PR, plus targeted checks: verify every locator and endpoint exists, make sure assertions fail when the feature breaks (try it), look for sleeps and over-mocking, check fixtures and factories are reused, and check library APIs are current. Ask the author to explain non-obvious parts. If they can't, it doesn't merge.
</details>

<details><summary><b>[SH] How would you measure whether AI assistants actually help your QA team?</b></summary>

Baseline, then measure: time-to-first-green-test for comparable tasks, review rework (comments per PR, revert rate), escaped defects and flake rate of AI-assisted tests vs others, and triage time. Add a qualitative survey. Run it as a time-boxed pilot on specific use cases with a control group where possible, and decide per use case, not globally.
</details>

#### 🤖 AI assist
- The task is AI-assisted by definition. Focus on the **review**, and write down every correction you made.

---

### P00-07 · Automate your task tracker with the GitHub CLI (optional)

**Level:** 🟣 Super Hero · **Time:** 3h · **App:** GitHub · **Deliverable:** `scripts/create_issues.py`

#### 📋 Task
Write a script that reads `learning-path/task-tracker.csv` and, for each task:
1. Ensures labels exist (`phase:P04`, `level:hero`, …).
2. Creates an issue titled `P04-02 · First API tests with requests` with the level, time and deliverable in the body, **only if it doesn't already exist** (idempotent).
3. Supports `--dry-run` and `--phase P04` filters.
4. (Stretch) Adds issues to a GitHub Project board.

**Done when**
- [ ] Running it twice creates no duplicates
- [ ] `--dry-run` prints what would happen and changes nothing
- [ ] Issues for at least P00–P03 exist in your repo

#### 📘 User guide

**Concepts**
- **gh CLI:** GitHub from the terminal. `gh issue create`, `gh label create`, `gh api` (raw REST/GraphQL).
- **Idempotency:** running an operation many times has the same effect as running it once. It's essential for scripts, CI jobs and test setup.
- **Dry run:** show the plan without side effects. It's how you make automation trustworthy.
- **Rate limits:** GitHub's API allows a limited number of requests per hour, so batch and cache reads.

**Deep dive**

This is "automating the automation", a Super Hero trait. Three design rules apply to any tooling script, including test-data seeding:

1. **Read state once, diff, then write.** Fetch all existing issue titles in *one* call (`gh issue list --state all --limit 1000 --json title`), then create only what's missing. This is idempotent and cheap on rate limits.
2. **Make destructive or noisy actions opt-in.** Default to `--dry-run`, or at least support it.
3. **Fail loudly and early.** Check `gh auth status` first, and use `check=True` on subprocess calls so a failure stops the script.

The same pattern (desired state vs actual state, then reconcile) is how Terraform, Kubernetes and good test fixtures work. Mention it in interviews.

**Examples**

🟢 **Low: one issue by hand**
```bash
gh label create "phase:P00" --color 0E8A16 --force
gh issue create --title "P00-01 · Toolchain and your own repo" \
  --body "Level: 🟢 Zero · Time: 2h" --label "phase:P00"
```

🔵 **Medium: a bash loop (fine for simple CSVs, fragile with commas in fields)**
```bash
tail -n +2 learning-path/task-tracker.csv | while IFS=, read -r id phase title level hours app deliverable status; do
  gh issue create --title "$id · $title" --body "Level: $level · ${hours}h" --label "phase:$phase"
done
```

🟣 **High/Complex: idempotent Python with dry-run and filters**
```python
# scripts/create_issues.py
import argparse, csv, json, subprocess
from pathlib import Path

CSV = Path("learning-path/task-tracker.csv")

def gh(*args: str) -> str:
    return subprocess.run(["gh", *args], check=True, capture_output=True, text=True).stdout

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--phase")
    a = p.parse_args()

    existing = {i["title"] for i in json.loads(gh("issue", "list", "--state", "all", "--limit", "1000", "--json", "title"))}
    rows = [r for r in csv.DictReader(CSV.open()) if not a.phase or r["phase"] == a.phase]

    for label in sorted({f"phase:{r['phase']}" for r in rows} | {f"level:{r['level'].lower()}" for r in rows}):
        if not a.dry_run:
            gh("label", "create", label, "--force")

    for r in rows:
        title = f"{r['id']} · {r['title']}"
        if title in existing:
            print(f"skip   {title}")
            continue
        body = f"**Level:** {r['level']} · **Time:** {r['hours']}h · **App:** {r['app']}\n\n**Deliverable:** {r['deliverable']}"
        print(f"{'would create' if a.dry_run else 'create'} {title}")
        if not a.dry_run:
            gh("issue", "create", "--title", title, "--body", body,
               "--label", f"phase:{r['phase']}", "--label", f"level:{r['level'].lower()}")

if __name__ == "__main__":
    main()
```

#### 🎤 Interview Q&A

<details><summary><b>[H] What does idempotent mean and why does it matter in test automation?</b></summary>

An operation is idempotent if repeating it gives the same result as doing it once. In automation: setup scripts can be re-run after a partial failure without creating duplicates, CI retries are safe, and in HTTP terms PUT and DELETE should be idempotent while POST usually isn't, which is why you test them differently.
</details>

<details><summary><b>[SH] How would you handle API rate limits in tooling or test setup?</b></summary>

Reduce calls (read once and cache, batch or bulk endpoints, GraphQL to fetch exactly what's needed), respect `Retry-After` and rate-limit headers with exponential backoff and jitter, spread load (fewer parallel workers against rate-limited services), and for tests prefer self-hosted or mocked dependencies over shared rate-limited ones.
</details>

<details><summary><b>[H] How do you track automation work in an agile team?</b></summary>

Automation tasks live in the same backlog as the features they cover, with acceptance criteria (which scenarios, which layer, which gate). Definition of Done includes "tests automated and in CI" for each story. I track coverage of critical flows and gate health (pass rate, duration, flakiness) rather than raw test counts.
</details>

#### 🤖 AI assist
- Let AI draft the script, **then** review it against the three design rules above and write down what it got wrong (duplicates? no dry-run? shell injection with `shell=True`?).

---

## 🏁 Phase checkpoint: P00

**Self-check:** without notes, can you explain: UI vs API tests; the three trees; reset vs revert; merge vs rebase; why a lockfile matters; what each step of your CI workflow does; and the four AI rules?

**AI mock interviewer prompt** (paste into your AI assistant):
```text
You are a QA-automation interviewer. Interview me on Git, GitHub PR workflow,
Python environments, repo quality tooling, a basic CI workflow and safe use of AI
assistants. Ask 8 questions one at a time, mixing
junior and mid-level. After each answer: score 1-5, say what a strong answer adds,
then ask the next. At the end, list my 3 weakest areas with study tips.
```
Record your score and gaps in `interview-notes/P00.md`.
