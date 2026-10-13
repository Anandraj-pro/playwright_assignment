# Task Tracker: QE Learning Path (Zero → Super Hero)

> Generated from `phases/*.md` by `scripts/build_tracker.py`.
> Don't edit the table structure by hand; learners only change ⬜ to ✅ in their own copy.

**How to use:** work top to bottom. For each task, open its guide (the link),
create an issue and branch, build it, run `make check TASK=<id>`, open a PR,
write your interview answers in `interview-notes/Pxx.md`, then tick ⬜ → ✅.
⭐ marks the **Essentials** track: new engineers do these first.
*Target week* assumes ~10 h/week. Adjust to your pace.

## Summary

| Level | Tasks | Hours |
|---|---|---|
| 🟢 Zero | 26 | 71 |
| 🔵 Hero | 35 | 141 |
| 🟣 Super Hero | 17 | 89 |
| **Total** | **78** | **301** (~31 weeks) |
| ⭐ Essentials track | 30 | 89 |


## P00: Setup, Git, First Automation and Safe AI (8 tasks, 20 h)

| ✓ | ID | Task | Level | Time | Target week | App | Deliverable |
|---|---|---|---|---|---|---|---|
| ⬜ | P00-00 ⭐ | [Hello automation: your first UI and API tests](phases/P00-git-setup.md#p00-00--hello-automation-your-first-ui-and-api-tests) | 🟢 | 2h | W1 | SauceDemo, Restful-Booker | tests/hello/test_hello_api.py, tests/hello/test_hello_ui.py |
| ⬜ | P00-01 ⭐ | [Your toolchain: Codespaces, dev container or local](phases/P00-git-setup.md#p00-01--your-toolchain-codespaces-dev-container-or-local) | 🟢 | 2h | W1 | — | README.md, docs/setup.md |
| ⬜ | P00-02 ⭐ | [Git fundamentals](phases/P00-git-setup.md#p00-02--git-fundamentals) | 🟢 | 3h | W1 | — | docs/git-cheatsheet.md |
| ⬜ | P00-03 ⭐ | [PR workflow, conflicts and rebase](phases/P00-git-setup.md#p00-03--pr-workflow-conflicts-and-rebase) | 🔵 | 3h | W1 | — | .github/PULL_REQUEST_TEMPLATE.md, a merged PR |
| ⬜ | P00-04 ⭐ | [Tour the project skeleton and quality tooling](phases/P00-git-setup.md#p00-04--tour-the-project-skeleton-and-quality-tooling) | 🟢 | 2h | W2 | — | docs/tooling.md |
| ⬜ | P00-05 ⭐ | [First workflow: lint and unit tests on every PR](phases/P00-git-setup.md#p00-05--first-workflow-lint-and-unit-tests-on-every-pr) | 🟢 | 2h | W2 | — | .github/workflows/ci.yml, a status badge in README.md |
| ⬜ | P00-06 ⭐ | [AI pair-testing in your repo, safely](phases/P00-git-setup.md#p00-06--ai-pair-testing-in-your-repo-safely) | 🟢 | 3h | W2 | your repo | CLAUDE.md (or AGENTS.md), docs/ai/usage-log.md, interview-notes/ai-mock.md |
| ⬜ | P00-07 | [Automate your task tracker with the GitHub CLI (optional)](phases/P00-git-setup.md#p00-07--automate-your-task-tracker-with-the-github-cli-optional) | 🟣 | 3h | W2 | GitHub | scripts/create_issues.py |

## P01: QE Fundamentals: What to Test and Why (5 tasks, 17 h)

| ✓ | ID | Task | Level | Time | Target week | App | Deliverable |
|---|---|---|---|---|---|---|---|
| ⬜ | P01-01 ⭐ | [QA in the SDLC: levels, types, life cycles and the test pyramid](phases/P01-qe-fundamentals.md#p01-01--qa-in-the-sdlc-levels-types-life-cycles-and-the-test-pyramid) | 🟢 | 4h | W3 | Toolshop, SauceDemo | docs/fundamentals/qa-in-sdlc.md, docs/fundamentals/glossary.md |
| ⬜ | P01-02 ⭐ | [Test-design techniques: partitions, boundaries, decision tables, states and pairs](phases/P01-qe-fundamentals.md#p01-02--test-design-techniques-partitions-boundaries-decision-tables-states-and-pairs) | 🟢 | 4h | W3 | Toolshop registration, SauceDemo checkout | docs/test-design/registration.md, docs/test-design/checkout-states.md |
| ⬜ | P01-03 ⭐ | [Test scenarios, test cases and traceability](phases/P01-qe-fundamentals.md#p01-03--test-scenarios-test-cases-and-traceability) | 🟢 | 3h | W4 | Toolshop (search, filters, cart) | docs/test-cases/toolshop-search.md, docs/test-cases/traceability.md |
| ⬜ | P01-04 ⭐ | [Story review, risk analysis and shift-left](phases/P01-qe-fundamentals.md#p01-04--story-review-risk-analysis-and-shift-left) | 🔵 | 3h | W4 | Toolshop (checkout, favourites, admin invoices) | docs/fundamentals/story-review.md, docs/fundamentals/risk-matrix.md |
| ⬜ | P01-05 | [LLM fundamentals and prompting for QA](phases/P01-qe-fundamentals.md#p01-05--llm-fundamentals-and-prompting-for-qa) | 🟢 | 3h | W4 | Toolshop (user stories), SauceDemo bugs | ai/prompts/*.md, docs/ai/llm-basics.md |

## P02: Python for QE (7 tasks, 23 h)

| ✓ | ID | Task | Level | Time | Target week | App | Deliverable |
|---|---|---|---|---|---|---|---|
| ⬜ | P02-01 ⭐ | [Data types, collections and comprehensions](phases/P02-python.md#p02-01--data-types-collections-and-comprehensions) | 🟢 | 3h | W4 | SauceDemo | python_basics/products.py |
| ⬜ | P02-02 ⭐ | [Functions, type hints and exceptions](phases/P02-python.md#p02-02--functions-type-hints-and-exceptions) | 🟢 | 3h | W5 | SauceDemo checkout | python_basics/checkout.py |
| ⬜ | P02-03 | [Files and test-data formats](phases/P02-python.md#p02-03--files-and-test-data-formats) | 🟢 | 2h | W5 | SauceDemo, Toolshop | framework/data/saucedemo_users.csv, python_basics/data_io.py |
| ⬜ | P02-04 ⭐ | [OOP and dataclasses](phases/P02-python.md#p02-04--oop-and-dataclasses) | 🔵 | 3h | W5 | SauceDemo / Toolshop domain | framework/models.py, python_basics/cart.py |
| ⬜ | P02-05 | [Decorators, context managers, logging and config](phases/P02-python.md#p02-05--decorators-context-managers-logging-and-config) | 🔵 | 4h | W6 | all (framework plumbing) | framework/utils/retry.py, framework/utils/wait.py, framework/config.py, .env.example |
| ⬜ | P02-06 | [Coding interview drills](phases/P02-python.md#p02-06--coding-interview-drills) | 🔵 | 4h | W6 | — | python_basics/drills.py |
| ⬜ | P02-07 | [Advanced Python for framework authors](phases/P02-python.md#p02-07--advanced-python-for-framework-authors) | 🟣 | 4h | W6 | Toolshop API | framework/api/pagination.py, framework/types.py, framework passes mypy --strict |

## P03: pytest (6 tasks, 17 h)

| ✓ | ID | Task | Level | Time | Target week | App | Deliverable |
|---|---|---|---|---|---|---|---|
| ⬜ | P03-01 ⭐ | [First pytest suite: discovery, assertions, running](phases/P03-pytest.md#p03-01--first-pytest-suite-discovery-assertions-running) | 🟢 | 2h | W7 | — | tests/unit/test_products.py, tests/unit/test_checkout.py, tests/unit/test_drills.py |
| ⬜ | P03-02 ⭐ | [Debug a failing test: tracebacks, breakpoints and pytest's debugging flags](phases/P03-pytest.md#p03-02--debug-a-failing-test-tracebacks-breakpoints-and-pytests-debugging-flags) | 🟢 | 2h | W7 | — (a debugging lab) | tests/unit/test_debug_lab.py, docs/debugging.md |
| ⬜ | P03-03 ⭐ | [Parametrize and data-driven tests](phases/P03-pytest.md#p03-03--parametrize-and-data-driven-tests) | 🟢 | 2h | W7 | SauceDemo data | tests/unit/test_checkout_params.py, tests/unit/test_users_data.py |
| ⬜ | P03-04 ⭐ | [Fixtures deep dive and conftest](phases/P03-pytest.md#p03-04--fixtures-deep-dive-and-conftest) | 🔵 | 4h | W7 | Restful-Booker | tests/conftest.py, tests/api/conftest.py, tests/api/booker/test_booking_fixtures.py |
| ⬜ | P03-05 | [Markers, config and custom CLI options](phases/P03-pytest.md#p03-05--markers-config-and-custom-cli-options) | 🔵 | 3h | W8 | all | [tool.pytest.ini_options] in pyproject.toml, --env option in tests/conftest.py |
| ⬜ | P03-06 | [Hooks, plugins and coverage](phases/P03-pytest.md#p03-06--hooks-plugins-and-coverage) | 🟣 | 4h | W8 | all | framework/pytest_plugin.py, tests/unit/test_plugin.py |

## P04: API Testing with requests (8 tasks, 28 h)

| ✓ | ID | Task | Level | Time | Target week | App | Deliverable |
|---|---|---|---|---|---|---|---|
| ⬜ | P04-01 ⭐ | [HTTP fundamentals and manual API exploration](phases/P04-api-requests.md#p04-01--http-fundamentals-and-manual-api-exploration) | 🟢 | 2h | W8 | Restful-Booker | docs/api-exploration.md |
| ⬜ | P04-02 ⭐ | [First API tests with requests](phases/P04-api-requests.md#p04-02--first-api-tests-with-requests) | 🟢 | 3h | W9 | Restful-Booker | tests/api/booker/test_booking_basic.py |
| ⬜ | P04-03 ⭐ | [Auth, CRUD and negative testing](phases/P04-api-requests.md#p04-03--auth-crud-and-negative-testing) | 🔵 | 4h | W9 | Restful-Booker | tests/api/booker/test_booking_crud.py, tests/api/booker/test_booking_negative.py |
| ⬜ | P04-04 ⭐ | [API client layer and schema validation](phases/P04-api-requests.md#p04-04--api-client-layer-and-schema-validation) | 🔵 | 4h | W9 | Restful-Booker | framework/api/base_client.py, framework/api/booker_client.py, framework/api/models/booking.py |
| ⬜ | P04-05 ⭐ | [Docker as a user: images, containers, ports and volumes](phases/P04-api-requests.md#p04-05--docker-as-a-user-images-containers-ports-and-volumes) | 🟢 | 3h | W10 | The Internet (Docker image) | docs/docker-cheatsheet.md |
| ⬜ | P04-06 ⭐ | [Run the demo stack locally with Compose](phases/P04-api-requests.md#p04-06--run-the-demo-stack-locally-with-compose) | 🟢 | 3h | W10 | Toolshop, Restful-Booker, Pagila | docs/local-stack.md, Makefile targets stack-up, stack-down, stack-reset |
| ⬜ | P04-07 | [Toolshop API: bearer auth, pagination, filters, data factories](phases/P04-api-requests.md#p04-07--toolshop-api-bearer-auth-pagination-filters-data-factories) | 🔵 | 4h | W10 | Toolshop API | framework/api/toolshop_client.py, framework/data/factories.py, tests/api/toolshop/ |
| ⬜ | P04-08 | [Contract testing and API resilience](phases/P04-api-requests.md#p04-08--contract-testing-and-api-resilience) | 🟣 | 5h | W11 | Petstore v3 (self-hosted), Toolshop specs | tests/contract/, scripts/spec_diff.py, docs/contract-testing.md |

## P05: UI Testing with Playwright (8 tasks, 32 h)

| ✓ | ID | Task | Level | Time | Target week | App | Deliverable |
|---|---|---|---|---|---|---|---|
| ⬜ | P05-01 ⭐ | [First Playwright tests on SauceDemo](phases/P05-ui-playwright.md#p05-01--first-playwright-tests-on-saucedemo) | 🟢 | 3h | W11 | SauceDemo | tests/ui/saucedemo/test_login.py |
| ⬜ | P05-02 ⭐ | [Locator strategy and data-driven login](phases/P05-ui-playwright.md#p05-02--locator-strategy-and-data-driven-login) | 🟢 | 3h | W12 | SauceDemo | tests/ui/saucedemo/test_login_matrix.py, docs/locator-strategy.md |
| ⬜ | P05-03 ⭐ | [Page Object Model: SauceDemo purchase end-to-end](phases/P05-ui-playwright.md#p05-03--page-object-model-saucedemo-purchase-end-to-end) | 🔵 | 4h | W12 | SauceDemo | framework/pages/saucedemo/, tests/ui/saucedemo/test_checkout.py |
| ⬜ | P05-04 | [Rescue a legacy suite](phases/P05-ui-playwright.md#p05-04--rescue-a-legacy-suite) | 🔵 | 5h | W12 | SauceDemo (`legacy-suite/playwright/`) | docs/legacy-rescue.md, tests/ui/saucedemo/test_legacy_rescued.py |
| ⬜ | P05-05 | [The Internet: tricky UI patterns](phases/P05-ui-playwright.md#p05-05--the-internet-tricky-ui-patterns) | 🔵 | 4h | W13 | The Internet | tests/ui/internet/ (≥12 tests) |
| ⬜ | P05-06 | [Toolshop: auth state, hybrid API+UI, network mocking](phases/P05-ui-playwright.md#p05-06--toolshop-auth-state-hybrid-apiui-network-mocking) | 🔵 | 5h | W13 | Toolshop | framework/pages/toolshop/, tests/ui/toolshop/ |
| ⬜ | P05-07 | [Debugging, cross-browser, mobile, visual checks and bug hunt](phases/P05-ui-playwright.md#p05-07--debugging-cross-browser-mobile-visual-checks-and-bug-hunt) | 🟣 | 5h | W14 | SauceDemo, Toolshop with-bugs | tests/ui/test_visual.py, tests/ui/test_bug_hunt.py, docs/bugs/, docs/ui-debugging.md |
| ⬜ | P05-08 | [Selenium to Playwright migration](phases/P05-ui-playwright.md#p05-08--selenium-to-playwright-migration) | 🟣 | 3h | W14 | SauceDemo (`legacy-suite/selenium/`) | docs/selenium-migration.md, tests/ui/migrated/, scripts/parity.py |

## P06: Database Testing (5 tasks, 23 h)

| ✓ | ID | Task | Level | Time | Target week | App | Deliverable |
|---|---|---|---|---|---|---|---|
| ⬜ | P06-01 ⭐ | [SQL fundamentals on Chinook (SQLite)](phases/P06-db-testing.md#p06-01--sql-fundamentals-on-chinook-sqlite) | 🟢 | 4h | W15 | Chinook | sql/01_chinook_basics.sql, tests/db/test_chinook_queries.py |
| ⬜ | P06-02 | [Interview SQL on Pagila (PostgreSQL in Docker)](phases/P06-db-testing.md#p06-02--interview-sql-on-pagila-postgresql-in-docker) | 🔵 | 5h | W15 | Pagila | sql/02_pagila_interview.sql, docs/pagila-erd.png |
| ⬜ | P06-03 | [Python DB layer and data-integrity tests](phases/P06-db-testing.md#p06-03--python-db-layer-and-data-integrity-tests) | 🔵 | 4h | W15 | Pagila | framework/db/engine.py, tests/db/pagila/test_integrity.py |
| ⬜ | P06-04 | [API/UI → DB consistency on self-hosted Toolshop](phases/P06-db-testing.md#p06-04--apiui--db-consistency-on-self-hosted-toolshop) | 🔵 | 5h | W16 | Toolshop (local Docker) | docker-compose.override.yml (in your Toolshop clone), framework/db/toolshop.py, tests/db/toolshop/ |
| ⬜ | P06-05 | [Test data strategies, ephemeral DBs, schema and ETL checks](phases/P06-db-testing.md#p06-05--test-data-strategies-ephemeral-dbs-schema-and-etl-checks) | 🟣 | 5h | W16 | Pagila via testcontainers | tests/db/conftest.py, tests/db/test_schema_contract.py, tests/db/test_reconciliation.py, docs/test-data-strategy.md |

## P07: Parallel Execution (4 tasks, 13 h)

| ✓ | ID | Task | Level | Time | Target week | App | Deliverable |
|---|---|---|---|---|---|---|---|
| ⬜ | P07-01 | [Baseline and first parallel run](phases/P07-parallel.md#p07-01--baseline-and-first-parallel-run) | 🟢 | 2h | W17 | all | docs/parallel-baseline.md |
| ⬜ | P07-02 | [Make tests parallel-safe](phases/P07-parallel.md#p07-02--make-tests-parallel-safe) | 🔵 | 4h | W17 | Restful-Booker, SauceDemo, Toolshop | refactored tests/, framework/data/accounts.py |
| ⬜ | P07-03 | [Distribution modes and shared session resources](phases/P07-parallel.md#p07-03--distribution-modes-and-shared-session-resources) | 🔵 | 3h | W17 | all | tests/conftest.py (lock-based session setup), Makefile lanes, docs/parallel-safety.md (update) |
| ⬜ | P07-04 | [Sharding across machines and a parallel strategy](phases/P07-parallel.md#p07-04--sharding-across-machines-and-a-parallel-strategy) | 🟣 | 4h | W18 | self-hosted stack | .test_durations, scripts/shard_model.py, docs/parallel-strategy.md |

## P08: Docker: Build, Compose and Maintain (3 tasks, 12 h)

| ✓ | ID | Task | Level | Time | Target week | App | Deliverable |
|---|---|---|---|---|---|---|---|
| ⬜ | P08-01 | [Containerise your test runner](phases/P08-docker.md#p08-01--containerise-your-test-runner) | 🔵 | 4h | W18 | public demo apps | docker/tests.Dockerfile, .dockerignore, make docker-test |
| ⬜ | P08-02 | [Your own Compose: tests + apps, health checks, networks](phases/P08-docker.md#p08-02--your-own-compose-tests--apps-health-checks-networks) | 🔵 | 4h | W19 | Pagila, Petstore, The Internet (+ Toolshop via external network) | docker-compose.yml, .env.docker.example |
| ⬜ | P08-03 | [Maintain: pin, slim, scan, update, multi-arch, devcontainer](phases/P08-docker.md#p08-03--maintain-pin-slim-scan-update-multi-arch-devcontainer) | 🟣 | 4h | W19 | your images | docker/tests-slim.Dockerfile, .github/dependabot.yml, .devcontainer/devcontainer.json, docs/docker-maintenance.md |

## P09: GitHub Actions and CI Gates (5 tasks, 19 h)

| ✓ | ID | Task | Level | Time | Target week | App | Deliverable |
|---|---|---|---|---|---|---|---|
| ⬜ | P09-01 ⭐ | [API + UI smoke in CI with artifacts and summaries](phases/P09-ci-github-actions.md#p09-01--api--ui-smoke-in-ci-with-artifacts-and-summaries) | 🟢 | 3h | W19 | public demo apps | a smoke job in ci.yml, scripts/junit_summary.py |
| ⬜ | P09-02 | [Quality gates and branch protection](phases/P09-ci-github-actions.md#p09-02--quality-gates-and-branch-protection) | 🔵 | 3h | W20 | your repo | gate jobs in ci.yml, .github/CODEOWNERS, branch protection on main, docs/ci-gates.md |
| ⬜ | P09-03 | [Service containers, DB tests and the full stack in CI](phases/P09-ci-github-actions.md#p09-03--service-containers-db-tests-and-the-full-stack-in-ci) | 🔵 | 4h | W20 | Pagila, Toolshop | db and toolshop-e2e jobs |
| ⬜ | P09-04 | [Matrix, sharding, nightly regression and published reports](phases/P09-ci-github-actions.md#p09-04--matrix-sharding-nightly-regression-and-published-reports) | 🔵 | 4h | W20 | all | .github/workflows/nightly.yml |
| ⬜ | P09-05 | [Images in CI, reusable workflows, environments, self-hosted runners](phases/P09-ci-github-actions.md#p09-05--images-in-ci-reusable-workflows-environments-self-hosted-runners) | 🟣 | 5h | W21 | your images and workflows | .github/actions/setup-qe/action.yml, .github/workflows/image.yml, .github/workflows/run-suite.yml, docs/runners-security.md |

## P10: Reporting, Bugs and Flaky Tests (4 tasks, 14 h)

| ✓ | ID | Task | Level | Time | Target week | App | Deliverable |
|---|---|---|---|---|---|---|---|
| ⬜ | P10-01 ⭐ | [Bug reports that get fixed](phases/P10-reporting-flaky.md#p10-01--bug-reports-that-get-fixed) | 🟢 | 3h | W21 | Toolshop with-bugs, SauceDemo | docs/bugs/BUG-001.md … BUG-005.md, .github/ISSUE_TEMPLATE/bug_report.yml |
| ⬜ | P10-02 | [Rich reports: pytest-html and Allure with attachments](phases/P10-reporting-flaky.md#p10-02--rich-reports-pytest-html-and-allure-with-attachments) | 🔵 | 3h | W21 | all | report hooks in framework/pytest_plugin.py, Allure steps in page objects and clients, docs/reporting.md |
| ⬜ | P10-03 | [Flaky tests: detect, reproduce, quarantine](phases/P10-reporting-flaky.md#p10-03--flaky-tests-detect-reproduce-quarantine) | 🔵 | 4h | W22 | SauceDemo (`performance_glitch_user`), The Internet (dynamic loading), your suite | scripts/flake_rate.py, a quarantine lane in Makefile and CI, docs/flaky-policy.md |
| ⬜ | P10-04 | [Test metrics and a quality dashboard](phases/P10-reporting-flaky.md#p10-04--test-metrics-and-a-quality-dashboard) | 🟣 | 4h | W22 | your CI history | scripts/metrics_ingest.py, scripts/metrics_report.py, docs/quality-dashboard.md |

## P11: Non-functional Testing: Performance, Accessibility and Security (4 tasks, 18 h)

| ✓ | ID | Task | Level | Time | Target week | App | Deliverable |
|---|---|---|---|---|---|---|---|
| ⬜ | P11-01 | [Performance testing with Locust](phases/P11-non-functional.md#p11-01--performance-testing-with-locust) | 🔵 | 4h | W23 | Restful-Booker and Toolshop API (self-hosted) | perf/locustfile.py, docs/performance/report.md |
| ⬜ | P11-02 | [Accessibility testing: axe scans, keyboard and screen readers](phases/P11-non-functional.md#p11-02--accessibility-testing-axe-scans-keyboard-and-screen-readers) | 🔵 | 4h | W23 | Toolshop (hosted is fine: scans only read pages), SauceDemo | tests/a11y/test_axe_scans.py, tests/a11y/test_keyboard.py, docs/accessibility.md |
| ⬜ | P11-03 | [Security testing basics for QEs](phases/P11-non-functional.md#p11-03--security-testing-basics-for-qes) | 🔵 | 5h | W24 | Toolshop API (self-hosted) | tests/security/test_authz_matrix.py, tests/security/test_input_handling.py, tests/security/test_headers.py, docs/security-testing.md |
| ⬜ | P11-04 | [Non-functional gates in CI: performance smoke, ZAP baseline and accessibility](phases/P11-non-functional.md#p11-04--non-functional-gates-in-ci-performance-smoke-zap-baseline-and-accessibility) | 🟣 | 5h | W24 | your self-hosted stack in CI | .github/workflows/non-functional.yml, scripts/perf_gate.py, .zap/rules.tsv, docs/non-functional-gates.md |

## P12: AI in QA (MCP Servers, Skills, Agents, Adoption) (6 tasks, 29 h)

| ✓ | ID | Task | Level | Time | Target week | App | Deliverable |
|---|---|---|---|---|---|---|---|
| ⬜ | P12-01 | [Use MCP servers: Playwright MCP and friends](phases/P12-ai-in-qa.md#p12-01--use-mcp-servers-playwright-mcp-and-friends) | 🔵 | 4h | W24 | Toolshop | .mcp.json, docs/ai/mcp-usage.md, a PR with AI-drafted tests after your review |
| ⬜ | P12-02 | [Build your own MCP server](phases/P12-ai-in-qa.md#p12-02--build-your-own-mcp-server) | 🔵 | 5h | W25 | your framework, Pagila, Restful-Booker | ai/mcp_server/server.py, tests/unit/test_mcp_server.py, docs/ai/qe-tools-server.md |
| ⬜ | P12-03 | [Write skills for your QE workflows](phases/P12-ai-in-qa.md#p12-03--write-skills-for-your-qe-workflows) | 🔵 | 4h | W25 | your repo | .claude/skills/{write-api-test,write-page-object,triage-failure,mock-interview}/SKILL.md, docs/ai/skills-eval.md |
| ⬜ | P12-04 | [Build a failure-triage agent, with evals](phases/P12-ai-in-qa.md#p12-04--build-a-failure-triage-agent-with-evals) | 🟣 | 6h | W26 | Toolshop with-bugs, your CI results | ai/agents/triage/agent.py, ai/evals/triage_cases.json, tests/unit/test_triage_agent.py, docs/ai/triage-agent.md |
| ⬜ | P12-05 | [Testing AI/LLM features](phases/P12-ai-in-qa.md#p12-05--testing-aillm-features) | 🟣 | 5h | W26 | a small LLM feature you build | ai/features/bug_summarizer.py, tests/ai/, ai/evals/summarizer_golden.json, docs/ai/testing-llm-features.md |
| ⬜ | P12-06 | [AI in CI (advisory) and your team's adoption playbook](phases/P12-ai-in-qa.md#p12-06--ai-in-ci-advisory-and-your-teams-adoption-playbook) | 🟣 | 5h | W27 | your CI | .github/workflows/ai-advisory.yml, docs/ai-adoption-playbook.md, a 10-minute presentation |

## P13: Capstone and Interview Readiness (5 tasks, 36 h)

| ✓ | ID | Task | Level | Time | Target week | App | Deliverable |
|---|---|---|---|---|---|---|---|
| ⬜ | P13-01 | [Explain your framework: README, architecture and ADRs](phases/P13-capstone-interviews.md#p13-01--explain-your-framework-readme-architecture-and-adrs) | 🔵 | 4h | W27 | your repo | README.md, docs/architecture.md, docs/adr/0001-*.md … 0003-*.md |
| ⬜ | P13-02 | [Capstone: Toolshop end-to-end quality](phases/P13-capstone-interviews.md#p13-02--capstone-toolshop-end-to-end-quality) | 🟣 | 16h | W29 | Toolshop (normal and with-bugs) | capstone/strategy.md, capstone/test-plan.md, tests under tests/*/toolshop/, capstone/report.md, a 15-minute demo |
| ⬜ | P13-03 | [Timed live-coding drills](phases/P13-capstone-interviews.md#p13-03--timed-live-coding-drills) | 🔵 | 6h | W30 | SauceDemo, Restful-Booker, Pagila | interview-notes/drills/ (one folder per attempt, with time and score) |
| ⬜ | P13-04 | [Behavioural stories (STAR), resume and portfolio](phases/P13-capstone-interviews.md#p13-04--behavioural-stories-star-resume-and-portfolio) | 🔵 | 4h | W30 | your repo | interview-notes/stories.md, docs/portfolio.md, updated resume bullets |
| ⬜ | P13-05 | [Full mock interview loop](phases/P13-capstone-interviews.md#p13-05--full-mock-interview-loop) | 🟣 | 6h | W31 | — | interview-notes/mock-loop.md (scores, feedback and an improvement plan for 2 loops) |
