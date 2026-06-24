# CLAUDE.md — Playwright Python Test Automation Project

## Commands

```bash
# Run web UI tests
pytest -s -v test_cases/test_web.py --alluredir=./allure-results

# Run API tests
pytest -s -v test_cases/test_api.py --alluredir=./allure-results

# View Allure report
allure serve allure-results

# Install dependencies
pip install -r requirements.txt
playwright install
```

> **Note:** `smart_assertions` is used in code (soft-assert support) but is **not** listed in `requirements.txt`. Install it manually: `pip install smart-assertions`.

---

## Architecture

Layered Page Object Model. Data flows top-down:

```
test_cases/
  └─▶ workflows/          ← cross-page orchestration
        └─▶ page_objects/web_objects/   ← one class per page
                └─▶ extentions/         ← thin Playwright wrappers
                └─▶ utilities/          ← shared state, config, helpers
```

### Layers

| Layer | Directory | Purpose |
|---|---|---|
| Tests | `test_cases/` | Class-based pytest tests + conftest fixtures |
| Workflows | `workflows/` | Multi-page flows (`WebFlows`, `APIFlows`) |
| Page Objects | `page_objects/web_objects/` | Per-page classes: selectors + atomic actions + single-page flows |
| Extensions | `extentions/` | `UiActions`, `APIActions`, `Verifications` wrappers (note: spelled "extentions") |
| Utilities | `utilities/` | `Base` (global state/factory), `CommonOps` (config/JSON/calc), `HelpersPage` (soft-assert helper) |
| Data | `data/` | `configuration.xml` (env config), `test_data.json` (per-test data) |

### Key Files

- `utilities/base.py` — module-level globals (`page`, `browser`, `context`, `request_context`, page-object instances); `Base.init_pages()` rebuilds page objects against the current page.
- `utilities/common_ops.py` — `get_data(node_name)` reads `configuration.xml`; `read_json_file`; `calculate_total_price`; `split_string`; constants `CONFIG_FILE_PATH`, `TEST_DATA_FILE_PATH`.
- `utilities/helpers_page.py` — `HelpersPage.verify_all_soft_equals(*checks)` takes `(actual, expected, message)` 3-tuples; the standard DRY soft-assert pattern.
- `extentions/ui_actions.py` — `UiActions` static methods (`click`, `double_click`, `update_text`, `get_text`, `select_option`, `get_attribute`, `clear_text`), all decorated with `@allure.step`.
- `extentions/verifications.py` — `Verifications`: `verify_equals` (hard assert), `verify_soft_assert_equals` (smart soft-assert), `verify_contains`.
- `extentions/api_actions.py` — `APIActions.get`; constant `PRODUCTS_ENDPOINT = "products.json"`.

### Configuration (`data/configuration.xml`)

Key nodes: `BROWSER_TYPE`, `SLOW_MODE`, `BASE_URL`, `BASE_URL_API`. Read via `get_data(node_name)` from `utilities/common_ops.py`.

### Test Data (`data/test_data.json`)

Keyed by suite name (derived from filename, e.g. `test_web.py` → `"web"`) and then by test name. Resolved automatically by the `test_data` fixture.

---

## Fixtures (`test_cases/conftest.py`)

| Fixture | Scope | Purpose |
|---|---|---|
| `init_page` | class | Launches browser, new context (tracing on), creates page, calls `Base.init_pages()`, navigates to `BASE_URL`. Teardown stops trace to `trace.zip`. |
| `init_api` | class | Creates Playwright API request context bound to `BASE_URL_API`. |
| `verify_after_test` | function (autouse) | Calls `verify_expectations()` after every test to flush smart soft-assertions. |
| `test_data` | function | Resolves current test's data from `test_data.json` by suite + test name. |
| `refresh_page` | function | Reloads the current page. |
| `main_page` | function | Navigates back to `BASE_URL`. |

Browser launchers (`get_chrome_driver`, `get_firefox_driver`, `get_edge_driver`) are dispatched by `get_web_driver` based on `BROWSER_TYPE`. All run headed with `slow_mo` from `SLOW_MODE`.

---

## Page Object Structure

Each page object file follows a strict three-section layout:

```python
class ProductsPage:
    def __init__(self, page: Page) -> None:
        # === SELECTORS ===
        self.cart_icon = page.locator("[class='cart-icon']")
        ...

    # === ACTIONS ===   (atomic, one-thing methods via UiActions)
    @allure.step("Click cart icon")
    def click_cart_icon(self) -> None:
        UiActions.click(self.cart_icon)

    # === FLOWS ===   (multi-step compositions + single-page verify methods)
    @allure.step("Add item to cart flow")
    def add_item_to_cart_flow(self, item_name: str) -> None:
        ...
```

Cross-page orchestration **always** goes in `workflows/`, not in page objects.

---

## Test Structure

```python
@pytest.mark.usefixtures("init_page", "test_data")
@allure.title("Test title")
@allure.description("Test description")
class Test_ExampleSuite:
    def test_example(self, test_data) -> None:
        # Test Data
        expected_value = test_data["expected_value"]

        # 1. First step description
        base.products_page.click_something()

        # 2. Second step description
        base.products_page.verify_something(expected_value)
```

---

## Coding Standards

Two enforced skills define the coding constitution for this project. **Always invoke them before writing or modifying code:**

- **`.claude/skills/python_standards`** — language-level rules: naming, type hints, docstrings, ≤20-line one-thing methods, ≤3–4 params, DRY/KISS/YAGNI, SOLID, f-strings, grouped imports. No `logging`, no bare globals.
- **`.claude/skills/automation_standards`** — POM/Playwright rules: injected `Page`, three-section layout, prefer `get_by_role`/`get_by_label`/`get_by_test_id` locators, web-first `expect` assertions (no `sleep`), DRY soft-asserts via `HelpersPage.verify_all_soft_equals`, cross-page flows in workflow layer.

---

## Gotchas

- **`extentions/`** — the directory and all imports use this misspelling. Match it exactly.
- **`smart_assertions`** — imported throughout but absent from `requirements.txt`.
- **Existing locators** — current page objects use CSS/XPath selectors (`.locator("[class='...']")`). The `automation_standards` skill prefers user-facing locators; use those for new code.
- **Shared state** — module-level globals in `utilities/base.py` (`base.page`, `base.products_page`, etc.) are the standard access pattern in tests and workflows.
- **Sync API** — this project uses `playwright.sync_api`, not the async variant.
