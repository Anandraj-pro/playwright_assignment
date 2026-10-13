# P08: Docker: Build, Compose and Maintain

> **Goal:** you already *use* Docker (P04-05, P04-06). Now containerise your own test runner, orchestrate apps and tests with Compose, and keep images small, pinned and secure.
> **Apps:** The Internet, Toolshop, Restful-Booker, Pagila, Petstore. **Prerequisites:** P04-05 and P04-06 (Docker as a user), P03–P05. **Time:** ~12 h.

| ID | Task | Level | Time |
|---|---|---|---|
| P08-01 | Containerise your test runner | 🔵 | 4h |
| P08-02 | Your own Compose: tests + apps, health checks, networks | 🔵 | 4h |
| P08-03 | Maintain: pin, slim, scan, update, multi-arch, devcontainer | 🟣 | 4h |

---

### P08-01 · Containerise your test runner

**Level:** 🔵 Hero · **Time:** 4h · **App:** public demo apps · **Deliverable:** `docker/tests.Dockerfile`, `.dockerignore`, `make docker-test`

#### 📋 Task
1. Write `docker/tests.Dockerfile` based on the **official Playwright Python image**, with the image version **matching** your `playwright` package version.
2. Install dependencies with `uv` using a **cache-friendly layer order** (lockfiles first, source code last).
3. Run as a **non-root** user and add a `.dockerignore`.
4. `ENTRYPOINT` runs pytest and `CMD` supplies the default args (smoke), so any args can be overridden at run time.
5. Mount `./test-results` so reports and traces land on your host.
6. `make docker-test` builds and runs smoke against the public apps.

**Done when**
- [ ] `make docker-test` passes from a fresh clone
- [ ] Changing only a test file rebuilds in seconds (the dependency layer is cached)
- [ ] Traces from a failing UI test appear in `./test-results` on the host

#### 📘 User guide

**Concepts**
- **Dockerfile instructions:** `FROM`, `ARG`, `ENV`, `WORKDIR`, `COPY`, `RUN`, `USER`, `ENTRYPOINT`, `CMD`.
- **Build context:** the files sent to the builder. `.dockerignore` excludes junk (`.venv`, `.git`, `test-results`).
- **Layer caching:** each instruction is a layer. If a layer's inputs didn't change, it's reused.
- **`ENTRYPOINT` vs `CMD`:** ENTRYPOINT is the executable, CMD provides default arguments (replaced by anything after the image name in `docker run`).

**Deep dive**

**Why the official Playwright image?** Browsers need many OS libraries (fonts, codecs, GTK and so on). The image ships them plus the browsers at `/ms-playwright`. The catch: **the image's browser build must match your `playwright` Python package version**, or you get "Executable doesn't exist at /ms-playwright/…". Pin both together.

**Cache-friendly order:**
```text
FROM → system deps → copy pyproject.toml + uv.lock → install deps → copy source → default command
```
Source code changes daily and dependencies rarely, so put dependencies *before* source. Then editing a test rebuilds only the last layers.

**Non-root:** running as root inside containers is a security smell. The Playwright image provides the user `pwuser`. Make sure the working directory and caches are writable by that user.

**Chromium in Docker:** Playwright recommends `--ipc=host` (Chromium can run out of shared memory and crash) and `--init` (reaps zombie processes) for `docker run`.

**Examples**

🟢 **Low: a first working Dockerfile**
```dockerfile
# docker/tests.Dockerfile
FROM mcr.microsoft.com/playwright/python:v1.55.0-noble
WORKDIR /app
COPY . .
RUN pip install uv && uv sync --frozen
ENTRYPOINT ["uv", "run", "pytest"]
CMD ["-m", "smoke", "-q"]
```
```bash
docker build -f docker/tests.Dockerfile -t qe-tests .
docker run --rm --ipc=host qe-tests
```
> Replace `v1.55.0` with **your** version: `uv run python -c "import importlib.metadata as m; print(m.version('playwright'))"`.

🔵 **Medium: cache-friendly, non-root, with a results volume**
```dockerfile
# docker/tests.Dockerfile
ARG PLAYWRIGHT_VERSION=1.55.0
FROM mcr.microsoft.com/playwright/python:v${PLAYWRIGHT_VERSION}-noble

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1

RUN mkdir -p /app/test-results && chown -R pwuser:pwuser /app
WORKDIR /app
USER pwuser

COPY --chown=pwuser:pwuser pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project          # dependency layer: cached until the lockfile changes

COPY --chown=pwuser:pwuser . .
RUN uv sync --frozen                                # installs your project (framework) itself

ENTRYPOINT ["uv", "run", "pytest"]
CMD ["-m", "smoke", "-q", "--junitxml=test-results/junit.xml"]
```
```gitignore
# .dockerignore
.venv
.git
**/__pycache__
test-results
playwright-report
.env
*.sqlite
```
```makefile
docker-test:
	docker build -f docker/tests.Dockerfile -t qe-tests .
	docker run --rm --ipc=host --init -v "$(PWD)/test-results:/app/test-results" qe-tests
```

🟣 **High/Complex: fail the build on version drift, and parametrise runs**
```dockerfile
# add after the final `uv sync` in the Medium Dockerfile
# re-declare: an ARG before FROM isn't visible after it (Dockerfiles have no trailing comments)
ARG PLAYWRIGHT_VERSION
ENV EXPECTED_PLAYWRIGHT=${PLAYWRIGHT_VERSION}
RUN uv run python -c "import importlib.metadata as m, os, sys; \
pkg = m.version('playwright'); img = os.environ['EXPECTED_PLAYWRIGHT']; \
print(f'playwright package={pkg} image={img}'); \
sys.exit(0 if pkg == img else f'Version mismatch: package {pkg} != image {img}. Bump both together.')"
```
```bash
# Same image, different runs, with config injected at run time (never baked in)
docker run --rm --ipc=host --init \
  -e QE_ENV=public -e QE_TOOLSHOP_API_URL=https://api.practicesoftwaretesting.com \
  -v "$PWD/test-results:/app/test-results" \
  qe-tests tests/api -m "not db" -n 4 --junitxml=test-results/api.xml

# Debug inside the image
docker run --rm -it --entrypoint bash qe-tests
```
> Build with `--build-arg PLAYWRIGHT_VERSION=$(uv run python -c "import importlib.metadata as m; print(m.version('playwright'))")` to keep the two in lockstep.

#### 🎤 Interview Q&A

<details><summary><b>[Z] Why run tests inside Docker?</b></summary>

Reproducibility: the same OS, browsers, fonts and dependency versions on every laptop and CI runner, which kills "works on my machine". It's also a one-command setup, isolated from host tooling, and easy to scale (N identical containers). Visual tests in particular need identical rendering environments.
</details>

<details><summary><b>[H] CMD vs ENTRYPOINT?</b></summary>

ENTRYPOINT defines the executable the container runs. CMD provides default arguments (or the default command if there's no ENTRYPOINT). Arguments after the image name in `docker run` replace CMD. With `ENTRYPOINT ["pytest"]` and `CMD ["-m","smoke"]`, `docker run img tests/api -n 4` runs `pytest tests/api -n 4`.
</details>

<details><summary><b>[H] How does layer caching work, and how do you structure a Dockerfile for it?</b></summary>

Each instruction creates a layer keyed by its instruction and inputs. If unchanged, the cached layer is reused, and all later layers are invalidated once one changes. So put rarely-changing steps first (base image, OS packages, dependency lockfile plus install) and frequently-changing ones last (source code). Keep the build context small with `.dockerignore`.
</details>

<details><summary><b>[Z] COPY vs ADD?</b></summary>

`COPY` copies local files, which is predictable and preferred. `ADD` can also fetch URLs and auto-extract tar archives, and that implicit behaviour can surprise you. Use COPY unless you specifically need ADD's features.
</details>

<details><summary><b>[SH] "Executable doesn't exist at /ms-playwright/chromium-…" in CI. Why?</b></summary>

The Playwright Python package version doesn't match the browsers in the image (or browsers were never installed for this version). Each Playwright release expects specific browser builds. Fix: align the image tag with the locked package version (and add a build-time check), or run `playwright install` for the installed version. Let Dependabot bump both together.
</details>

<details><summary><b>[H] Why run containers as non-root?</b></summary>

Defence in depth: if something in the container is compromised (a malicious dependency, for example), a non-root user limits what it can do, and some platforms forbid root containers. Set `USER`, and make the required paths writable by that user.
</details>

<details><summary><b>[Z] Walk me through a simple Dockerfile: what do FROM, WORKDIR, COPY, RUN and CMD do?</b></summary>

`FROM` picks the base image to build on. `WORKDIR` sets the directory later instructions run in. `COPY` copies files from the build context into the image. `RUN` executes a command at *build* time and saves the result as a layer (installing dependencies, for example). `CMD` sets the default command the container runs when it *starts*. Each instruction creates a layer, which is why their order matters for caching.
</details>

#### 🤖 AI assist
- Ask AI to review your Dockerfile for cache efficiency and security, then run `hadolint` (P08-03) and compare the findings.

---

### P08-02 · Your own Compose: tests + apps, health checks, networks

**Level:** 🔵 Hero · **Time:** 4h · **App:** Pagila, Petstore, The Internet (+ Toolshop via external network) · **Deliverable:** `docker-compose.yml`, `.env.docker.example`

#### 📋 Task
Create a `docker-compose.yml` in your repo that runs **apps plus tests** together:
1. Services: `pagila-db` (Postgres + Pagila init scripts), `petstore`, `the-internet`, and `tests` (built from P08-01).
2. A **health check** on `pagila-db` that proves data is loaded (not just that the process is up), and `tests` waiting with `depends_on: condition: service_healthy`.
3. Config through `environment` / `env_file` (`.env.docker`, git-ignored) and **service-name URLs**.
4. `docker compose up --build --exit-code-from tests` returns the test exit code (the CI contract).
5. **Toolshop:** join Toolshop's network as an **external network** so API and DB tests can reach it by service name. Then investigate why Toolshop **UI** tests from inside a container behave differently (see the deep dive) and document it.

**Done when**
- [ ] One command runs apps plus tests and exits with pytest's exit code
- [ ] Tests never start before Pagila's data is loaded
- [ ] `docs/local-stack.md` explains the SPA/localhost networking issue and your solution

#### 📘 User guide

**Concepts**
- **`healthcheck`:** a command Compose runs periodically. The container becomes `healthy` when it passes.
- **`depends_on` conditions:** `service_started` (default), `service_healthy`, `service_completed_successfully`.
- **`--exit-code-from tests`:** stop everything when `tests` exits and return its exit code (implies `--abort-on-container-exit`).
- **External networks:** attach to a network created by another Compose project.
- **Profiles:** optional services started only with `--profile x`.

**Deep dive**

**Healthy ≠ running.** `depends_on` without a condition only waits for the container to *start*. Postgres takes seconds (and Pagila's init scripts longer) before queries work. A health check that runs a **real query over TCP** (`psql -h 127.0.0.1 … SELECT 1 FROM rental`) is precise. During init the official Postgres image runs a temporary server that *only* listens on a Unix socket, so a TCP check can't pass too early. A plain `pg_isready` over the socket can.

**The SPA/localhost trap (senior-level insight):** Toolshop's Angular app runs *in the browser* and calls the API at the URL it was configured with, e.g. `http://localhost:8091`. When the browser runs **inside your test container**, `localhost` is the test container, so the UI loads but every API call fails. Options:
- run the test container with `network_mode: host` (Linux, and so GitHub-hosted runners), so `localhost` means the host;
- configure the SPA's API URL to a name reachable from both places;
- intercept and rewrite API calls with `page.route` (last resort).
API and DB tests don't have this problem because *your code* makes the calls, using service names.

**Exit codes are the CI contract.** A pipeline decides pass or fail from the exit code. `--exit-code-from tests` propagates pytest's code (0, 1, 5…) through Compose.

**Examples**

🟢 **Low: tests + petstore**
```yaml
# docker-compose.yml
services:
  petstore:
    image: swaggerapi/petstore3:unstable

  tests:
    build: { context: ., dockerfile: docker/tests.Dockerfile }
    depends_on: [petstore]
    environment:
      QE_PETSTORE_URL: http://petstore:8080
    volumes:
      - ./test-results:/app/test-results
    command: ["tests/contract", "-q", "--junitxml=test-results/contract.xml"]
```
```bash
docker compose up --build --exit-code-from tests; echo "exit=$?"
```

🔵 **Medium: Pagila with a *real* readiness health check**
```yaml
services:
  pagila-db:
    image: postgres:18
    environment:
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: pagila
    volumes:
      - ${PAGILA_DIR:-../pagila}/pagila-schema.sql:/docker-entrypoint-initdb.d/01-schema.sql:ro
      - ${PAGILA_DIR:-../pagila}/pagila-data.sql:/docker-entrypoint-initdb.d/02-data.sql:ro
    healthcheck:
      # TCP (-h 127.0.0.1) + real query: can't pass during the init phase
      test: ["CMD-SHELL", "psql -h 127.0.0.1 -U postgres -d pagila -tAc 'SELECT 1 FROM rental LIMIT 1' | grep -q 1"]
      interval: 5s
      timeout: 3s
      retries: 60
      start_period: 20s

  tests:
    build: { context: ., dockerfile: docker/tests.Dockerfile }
    depends_on:
      pagila-db: { condition: service_healthy }
      petstore: { condition: service_started }
    env_file: [.env.docker]              # git-ignored; commit .env.docker.example
    environment:
      QE_ENV: docker
      QE_PAGILA_URL: postgresql+psycopg://postgres:postgres@pagila-db:5432/pagila
    volumes: ["./test-results:/app/test-results"]
    command: ["-m", "db or api", "-n", "4", "--env", "docker", "--junitxml=test-results/junit.xml"]
```

🟣 **High/Complex: joining Toolshop's network, profiles, and host networking for SPA UI tests**
```yaml
services:
  the-internet:
    image: gprestes/the-internet
    profiles: ["ui"]                                   # started only with --profile ui

  tests:
    # …as above…
    networks: [default, toolshop]

  tests-ui-host:                                       # Linux/CI only: browser's "localhost" = host
    build: { context: ., dockerfile: docker/tests.Dockerfile }
    profiles: ["ui-host"]
    network_mode: host
    ipc: host
    environment:
      QE_ENV: local                                    # uses localhost:4200 / :8091 published by Toolshop
    volumes: ["./test-results:/app/test-results"]
    command: ["tests/ui/toolshop", "--junitxml=test-results/ui-toolshop.xml"]

networks:
  toolshop:
    external: true
    name: pst_default                                  # find the real name: docker network ls
```
```bash
docker compose up --build --exit-code-from tests                              # api + db
docker compose --profile ui-host run --rm tests-ui-host                      # Toolshop UI (Linux/CI)
docker compose run --rm tests tests/api/toolshop -m smoke --env docker       # ad-hoc override of CMD
```
> In `--env docker`, point `toolshop_api_url` at Toolshop's **API service name and container port** on the shared network (find them with `docker compose config` in the Toolshop folder).

#### 🎤 Interview Q&A

<details><summary><b>[H] <code>depends_on</code> alone vs with <code>condition: service_healthy</code>?</b></summary>

Plain `depends_on` only orders start-up: the dependency's container has started, but the app may not be ready. With a health check and `condition: service_healthy`, Compose waits until the dependency passes its readiness check. That avoids connection-refused failures and flaky starts.
</details>

<details><summary><b>[H] How do you get the pass/fail result of tests run with Compose into CI?</b></summary>

`docker compose up --exit-code-from tests` (or `docker compose run --rm tests …`) so the command's exit code is pytest's exit code. Mount a results directory for JUnit/HTML/traces, upload them as CI artifacts, and always run `docker compose down -v` afterwards.
</details>

<details><summary><b>[SH] UI tests inside a container load the page, but all API calls fail. Why?</b></summary>

The front end is a SPA running in the browser, and it calls the API at a URL configured for the host (e.g. `localhost:8091`). Inside the test container, localhost is the container itself. Fixes: host networking for the test container (Linux), configuring the SPA's API base URL to a hostname resolvable in both contexts, running the browser outside and the tests inside, or rewriting requests with network interception.
</details>

<details><summary><b>[H] env vs env_file vs secrets in Compose?</b></summary>

`environment` sets values inline (visible in the compose file, so fine for non-secret config). `env_file` loads from a file (keep it git-ignored for local secrets). Compose `secrets` mount secret files into the container at `/run/secrets/…`, which keeps them out of the environment and image layers. In CI, inject secrets from the CI secret store. Never bake secrets into images.
</details>

<details><summary><b>[SH] How would you run the full test environment for every PR?</b></summary>

Compose (or ephemeral namespaces in Kubernetes) started per CI job from pinned images, seeded deterministically, with health checks gating the tests, tests in a container on the same network, artifacts uploaded, and teardown always executed. Keep start-up fast (pre-built images, cached layers, slim seed data) and share nothing between runs.
</details>

<details><summary><b>[Z] What is a health check in Docker Compose, and why do tests need one?</b></summary>

A command Compose runs periodically inside a container to decide whether the service is actually ready (for example, the database accepts queries or an HTTP endpoint returns 200). With `depends_on: condition: service_healthy`, the test container waits until its dependencies are healthy rather than merely started, which prevents flaky failures at the start of every run.
</details>

#### 🤖 AI assist
- Ask AI to draw (in Mermaid) the network diagram of your Compose setup, including which hostnames each component uses. Check it against `docker network inspect`.

---

### P08-03 · Maintain: pin, slim, scan, update, multi-arch, devcontainer

**Level:** 🟣 Super Hero · **Time:** 4h · **App:** your images · **Deliverable:** `docker/tests-slim.Dockerfile`, `.github/dependabot.yml`, `.devcontainer/devcontainer.json`, `docs/docker-maintenance.md`

#### 📋 Task
1. **Pin** everything: the base image tag (and, for CI, digest), the `uv` image version, and Postgres. Explain your pin-and-update policy.
2. **Lint:** run `hadolint` and fix the findings (or justify ignoring them).
3. **Scan:** run `trivy` on your image. Fix what you can by upgrading, and record accepted risks in `.trivyignore` with a reason and review date.
4. **Slim:** build a Chromium-only variant from `python:3.13-slim` and compare its size with the full Playwright image. Document the trade-off.
5. **Update automation:** `dependabot.yml` for `docker`, `uv` and `github-actions`.
6. **Multi-arch:** build for `linux/amd64,linux/arm64` with `buildx`.
7. **Devcontainer:** you've used the template's `.devcontainer/devcontainer.json` since P00-00. Now *maintain* it: pin the base image to a digest, add a Dependabot entry for the `devcontainers` ecosystem, cut build time (e.g. a prebuild or a slimmer feature set), and make sure it installs the same Python and Playwright versions as your CI image.

**Done when**
- [ ] `docs/docker-maintenance.md` has a size table, scan results and your update policy
- [ ] Zero CRITICAL vulnerabilities without a documented exception
- [ ] The devcontainer still opens and `make test` passes inside it after your changes, and Dependabot watches it

#### 📘 User guide

**Concepts**
- **Pinning:** `image:1.2.3` (a readable tag) vs `image@sha256:…` (an immutable digest). `latest` is unpinned.
- **Linting Dockerfiles:** `hadolint` flags bad practice (unpinned apt packages, missing `--no-install-recommends`, `cd` instead of `WORKDIR`).
- **Vulnerability scanning:** `trivy` / Docker Scout match OS and library packages against CVE databases.
- **Dependabot:** opens PRs when dependencies (including base images and Actions) have updates.
- **Multi-arch images:** one tag serving amd64 (CI) and arm64 (Apple Silicon laptops).
- **Dev containers:** a JSON spec that defines a reproducible development environment.

**Deep dive**

**Pin and update deliberately.** Unpinned images change under you, so a green build turns red with no commit. Pinned images are reproducible but go stale and accumulate CVEs. The answer is **pin + automated update PRs + CI gates**: Dependabot proposes a bump, CI runs the full suite on it, and you merge knowing it works.

**Image size matters** for CI time (pull on every job), storage and attack surface. The full Playwright image carries 3 browsers. If CI only runs Chromium, a slim image with just Chromium can be much smaller. The trade-off: you now own OS-dependency maintenance (`playwright install --with-deps` handles most of it).

**CVE triage:** not every CVE matters. Ask whether it's in a package you use at runtime, whether it's reachable, and whether a fix exists. Upgrade when possible. Otherwise document the risk with an expiry date. Test images aren't production, but they run in CI with secrets, so they aren't risk-free either.

**Multi-arch:** Apple Silicon developers pulling amd64-only images run them under emulation (slow, occasionally broken). `docker buildx build --platform linux/amd64,linux/arm64` publishes both.

**Examples**

🟢 **Low: lint, scan and size**
```bash
docker run --rm -i hadolint/hadolint < docker/tests.Dockerfile
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy \
  image --severity CRITICAL,HIGH --exit-code 1 qe-tests:latest
docker images qe-tests --format '{{.Repository}}:{{.Tag}} {{.Size}}'
docker history qe-tests:latest --format '{{.Size}}\t{{.CreatedBy}}' | head -15
docker system df && docker builder prune -f
```

🔵 **Medium: pinned references plus Dependabot**
```dockerfile
ARG PLAYWRIGHT_VERSION=1.55.0
FROM mcr.microsoft.com/playwright/python:v${PLAYWRIGHT_VERSION}-noble
# pinned uv version: choose the current release
COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/
```
```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "uv"
    directory: "/"
    schedule: { interval: "weekly" }
    groups:
      playwright: { patterns: ["playwright", "pytest-playwright"] }
  - package-ecosystem: "docker"
    directory: "/docker"
    schedule: { interval: "weekly" }
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule: { interval: "weekly" }
```
> Bumps to the `playwright` package and to the Playwright base image must land **together**. The P08-01 version check will fail the build if they don't, which is exactly what you want.

🟣 **High/Complex: a slim Chromium image, multi-arch build and devcontainer**
```dockerfile
# docker/tests-slim.Dockerfile
FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project \
 && uv run playwright install --with-deps chromium \
 && rm -rf /var/lib/apt/lists/*
RUN useradd --create-home qe && chown -R qe:qe /app /ms-playwright
USER qe
COPY --chown=qe:qe . .
RUN uv sync --frozen
ENTRYPOINT ["uv", "run", "pytest"]
CMD ["-m", "smoke", "--browser", "chromium", "-q"]
```
```bash
docker buildx create --use --name qe-builder 2>/dev/null || docker buildx use qe-builder
docker buildx build --platform linux/amd64,linux/arm64 -f docker/tests-slim.Dockerfile -t qe-tests:slim .
# add --push -t ghcr.io/<you>/qe-tests:slim to publish (P09-05)
```
```yaml
# .github/dependabot.yml (add to what you already have): keep the devcontainer image and features current
version: 2
updates:
  - package-ecosystem: "devcontainers"
    directory: "/"
    schedule:
      interval: "weekly"
```
```bash
# Pin the devcontainer base image to a digest, the same way you pinned your test image
docker pull mcr.microsoft.com/devcontainers/python:1-3.12-bookworm
docker image inspect mcr.microsoft.com/devcontainers/python:1-3.12-bookworm --format '{{index .RepoDigests 0}}'
# then set "image": "mcr.microsoft.com/devcontainers/python@sha256:<digest>" in .devcontainer/devcontainer.json
```

#### 🎤 Interview Q&A

<details><summary><b>[Z] What's wrong with using the <code>latest</code> tag?</b></summary>

It's mutable. The image behind it changes without any change in your repo, so builds aren't reproducible and failures appear "randomly". Pin versions (and digests for maximum immutability) and update deliberately through PRs.
</details>

<details><summary><b>[H] How do you reduce a Docker image's size?</b></summary>

Choose a smaller base (slim or distroless where possible), install only what's needed (one browser, not three), use multi-stage builds to leave build tools behind, combine and clean package-manager steps (`rm -rf /var/lib/apt/lists/*`, `--no-install-recommends`), use `.dockerignore`, and avoid copying caches and artefacts. Measure with `docker history`.
</details>

<details><summary><b>[SH] How do you keep container images secure and up to date?</b></summary>

Pin versions, automate update PRs (Dependabot or Renovate) gated by CI, scan images in CI (trivy/Scout) and fail on critical issues with a documented exception process, rebuild regularly to pick up base patches, run as non-root, keep secrets out of layers, use minimal bases, and sign or verify images for production supply chains.
</details>

<details><summary><b>[SH] A critical CVE is reported in your base image but no fix exists yet. What do you do?</b></summary>

Assess exploitability in context (is the package used at runtime or reachable, and is this a test-only image?), check for alternative bases or versions, add a time-boxed documented exception (`.trivyignore` with a reason and review date), monitor for the fix and rebuild when it's available, and add mitigations (non-root, no network where possible, least-privilege secrets).
</details>

<details><summary><b>[H] What do dev containers give a QE team?</b></summary>

A one-click, identical development environment (Python, uv, browsers, Docker, extensions) locally or in Codespaces. Onboarding drops from hours to minutes, "works on my machine" disappears, and CI and dev environments converge.
</details>

<details><summary><b>[SH] Why build multi-arch images for a test team?</b></summary>

Developers on Apple Silicon (arm64) and CI on amd64 both get native images. There's no slow, occasionally broken emulation, and results are consistent. `buildx` builds and pushes a single manifest list that serves both architectures.
</details>

#### 🤖 AI assist
- Paste trivy output (it's public CVE data) and ask AI to triage it into *fix now / upgrade base / accept with reason*. Verify each fixed version it claims actually exists.

---

## 🏁 Phase checkpoint: P08

**Whiteboard (20 min, no AI):** draw your Compose architecture: services, networks, ports, health checks, volumes and where reports go. Explain the SPA/localhost trap.

**AI mock interviewer prompt**
```text
Interview me on Docker for test automation: images vs containers, Dockerfile best
practices, layer caching, compose networking, health checks, running Playwright
in Docker, secrets, image maintenance and security. 8 questions, one at a time,
then a debugging scenario: "tests in the container can't connect to the database".
Score each 1-5 with senior-level additions.
```
Record your results in `interview-notes/P08.md`.
