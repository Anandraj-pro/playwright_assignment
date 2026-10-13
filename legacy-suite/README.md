# Legacy suite (inherited)

> "This is the checkout suite from the old team. It mostly works on Dave's laptop. If a test goes red,
> just rerun it. Don't touch conftest.py." (handover note)

This folder is **deliberately bad test code**, shipped with the template so you can practise what new
QEs actually do on day 1 of a real job: read, run, diagnose and rescue someone else's suite.

| Folder | Used in | What you do |
|---|---|---|
| `playwright/` | [P05-04](../learning-path/phases/P05-ui-playwright.md#p05-04--rescue-a-legacy-suite) | Find the smells, measure the damage, rewrite it with your page objects |
| `selenium/` | [P05-08](../learning-path/phases/P05-ui-playwright.md#p05-08--selenium-to-playwright-migration) | Plan and carry out a migration to Playwright |

**Rules:** don't fix the files in here. Keep them as the "before" so you can measure "after".
Your rescued tests live in `tests/`. ruff and the default `make test` run both skip this folder.

## Run it

```bash
uv run pytest legacy-suite/playwright -v                  # in file order: usually green, and slow
uv run pytest legacy-suite/playwright -v --durations=0    # where does the time go?
uv run pytest "legacy-suite/playwright/test_shop.py::test_3" -v    # one test on its own. What happens?
uv run --with selenium python -m pytest legacy-suite/selenium -v   # needs Chrome; Selenium Manager fetches the driver
```

There are **at least 15 smells** in `playwright/`. Don't look for a list; finding them is the exercise.
