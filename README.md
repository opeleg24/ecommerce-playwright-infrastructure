# E-Commerce Playwright Infrastructure Automation

A scalable QA automation infrastructure for Web UI and REST API testing, implemented with **Python** and **Playwright**. It uses a layered Page Object Model to separate test logic from page interactions, keeping the suite maintainable, reusable, and easy to extend.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-1.54-2EAD33?logo=playwright&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-8.3-0A9EDC?logo=pytest&logoColor=white)
![Allure](https://img.shields.io/badge/Allure-2.15-orange?logo=data:image/svg+xml;base64,)
![Multi-browser](https://img.shields.io/badge/Browsers-Chrome%20%7C%20Firefox%20%7C%20Edge-brightgreen)

---

## Table of Contents

1. [Application Under Test](#application-under-test)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Key Engineering Highlights](#key-engineering-highlights)
5. [Project Structure](#project-structure)
6. [Architecture Deep-Dive](#architecture-deep-dive)
7. [Installation](#installation)
8. [Usage](#usage)
9. [Configuration](#configuration)

---

## Application Under Test

The suite targets [GreenKart](https://rahulshettyacademy.com/seleniumPractise/#/), a public demo e-commerce site for buying fresh vegetables and produce online. It's a practice application built for learning automation, which makes it a safe, stable target for demonstrating UI and API testing flows across product search, cart management, promo codes, checkout, and order placement.

---

## Features

- **Web UI testing** — end-to-end flows covering product browsing, cart management, checkout, promo codes, and order placement
- **REST API testing** — endpoint-level validation of product data (count, names, payloads)
- **Multi-browser support** — single config switch selects Chrome, Firefox, or Edge
- **Smart soft-assertions** — collect multiple failures per test before raising; no intermediate noise
- **Hard assertions** — instant fail on critical conditions
- **Allure reporting** — rich, step-level HTML reports with screenshots and traces
- **Playwright tracing** — full `trace.zip` written on teardown for every test session
- **Data-driven design** — all environment config in `configuration.xml`, all test inputs in `test_data.json`
- **Negative testing** — invalid promo codes, empty search states, and boundary conditions covered

---

## Tech Stack

| Tool / Library | Version | Role |
|---|---|---|
| Python | 3.11+ | Primary language |
| Playwright (sync API) | ~1.54 | Browser automation & API request contexts |
| pytest | ~8.3 | Test runner, fixtures, class-based test organisation |
| allure-python-commons | ~2.15 | Step-level reporting, `@allure.step` decorators |
| smart-assertions | 1.0.2 | Soft-assert collection (`soft_assert` / `verify_expectations`) |

---

## Key Engineering Highlights

- **Layered Page Object Model** — strict five-layer architecture (tests → workflows → page objects → extensions → utilities) keeps each layer responsible for exactly one concern
- **DRY principle** — every repeated Playwright interaction lives in a single `UiActions` wrapper; every soft-assert pattern flows through `HelpersPage.verify_all_soft_equals`
- **SOLID design** — each class has a single responsibility; page objects expose only their own page's behaviour; cross-page orchestration is isolated to `workflows/`
- **Three-section page object layout** — every page class is divided into `SELECTORS`, `ACTIONS`, and `FLOWS`, making it trivial to navigate and extend
- **Allure-instrumented wrappers** — `UiActions` and `Verifications` are decorated with `@allure.step`, giving every test a self-documenting execution trace
- **Class-scoped fixtures with tracing** — `init_page` starts a Playwright trace before the browser opens and writes `trace.zip` on teardown, giving full replay capability on failure
- **Data-driven config** — environment values (`BROWSER_TYPE`, `BASE_URL`, `SLOW_MODE`) come from `data/configuration.xml`; per-test inputs come from `data/test_data.json`, resolved automatically by the `test_data` fixture
- **KISS / YAGNI** — no third-party test framework abstractions; the stack is deliberately minimal

---

## Project Structure

```
ecommerce-playwright-automation/
│
├── test_cases/                  # pytest test classes + conftest fixtures
│   ├── conftest.py              #   init_page, init_api, test_data, verify_after_test, ...
│   ├── test_web.py              #   Test_Web  (9 UI scenarios)
│   └── test_api.py              #   Test_API  (2 API scenarios)
│
├── workflows/                   # Cross-page orchestration (multi-page flows only)
│   ├── web_flow.py              #   WebFlows.proceed_to_country_page_flow()
│   └── api_flows.py             #   APIFlows.get_first_product(), get_amount_of_items()
│
├── page_objects/
│   └── web_objects/             # One class per page (SELECTORS / ACTIONS / FLOWS)
│       ├── products_page.py     #   ProductsPage
│       ├── check_out_page.py    #   CheckOutPage
│       └── country_page.py      #   CountryPage
│
├── extentions/                  # Thin Playwright wrappers (allure-instrumented)
│   ├── ui_actions.py            #   UiActions  — click, fill, get_text, select_option, ...
│   ├── verifications.py         #   Verifications — verify_equals, verify_soft_assert_equals, verify_contains
│   └── api_actions.py           #   APIActions — GET requests; PRODUCTS_ENDPOINT constant
│
├── utilities/                   # Shared state, config, helpers
│   ├── base.py                  #   Module-level Playwright globals + Base.init_pages()
│   ├── common_ops.py            #   get_data(), read_json_file(), calculate_total_price(), split_string()
│   └── helpers_page.py          #   HelpersPage.verify_all_soft_equals(*checks)
│
├── data/
│   ├── configuration.xml        # Environment config (browser, URLs, slow-mo)
│   └── test_data.json           # Per-test input/expected values
│
├── requirements.txt
└── README.md
```

---

## Architecture Deep-Dive

### Layer responsibilities and data flow

```
test_cases/         ← entry point; tests read test_data, call page objects or workflows
    │
    ▼
workflows/          ← cross-page orchestration only (never access the DOM directly)
    │
    ▼
page_objects/       ← per-page classes: own selectors, atomic actions, single-page flows
web_objects/
    │
    ▼
extentions/         ← allure-instrumented wrappers around raw Playwright locator calls
    │
    ▼
utilities/          ← global Playwright state (base.py) + config/data helpers
```

### Page object three-section layout

Every page object class follows an enforced three-section structure:

```python
class ProductsPage:
    def __init__(self, page: Page) -> None:
        # =================== SELECTORS ===================
        self.cart_icon = page.locator("[class='cart-icon']")
        self.search_box = page.locator("input[type='search']")
        # ...

    # =================== ACTIONS ===================
    def open_cart(self) -> None:
        UiActions.click(self.cart_icon)

    def fill_search_box(self, text: str) -> None:
        UiActions.update_text(self.search_box, text)

    # =================== FLOWS ===================
    @allure.step("Add one product to cart")
    def add_product_to_cart(self, product_name: str) -> None:
        self.locate_product(product_name)
        self.decrease_quantity()
        self.click_add_to_cart()
```

**Selectors** — all locators declared once in `__init__`; no magic strings scattered across methods.  
**Actions** — single-step, atomic wrappers (one Playwright call each) delegating to `UiActions`.  
**Flows** — multi-step compositions within the same page; decorated with `@allure.step`.

### Soft-assertion pattern

Multiple assertions inside one test are batched via `HelpersPage.verify_all_soft_equals`, which accepts any number of `(actual, expected, message)` tuples. The `verify_after_test` fixture (autouse) flushes all collected failures after every test via `verify_expectations()` from `smart_assertions`. This prevents a single wrong value from silently masking other failures.

```python
HelpersPage.verify_all_soft_equals(
    (self.get_header_item_count(), expected_items, "item count"),
    (self.get_header_total_price(), expected_price, "total price"),
)
```

### Shared state (`utilities/base.py`)

The active `page`, `browser`, `context`, `request_context`, and all page-object instances are stored as module-level globals in `base.py`. Pytest fixtures populate them once per class; tests and workflows import `base` directly. `Base.init_pages()` re-binds every page object to the current page after a new browser session is created.

### Test-data resolution

The `test_data` fixture derives a **suite key** from the test module filename (`test_web.py` → `"web"`) and looks up the current test function name inside `data/test_data.json`. Each test receives exactly its own data dict — no hard-coded strings in test code.

---

## Installation

### Prerequisites

- Python 3.11+
- [Allure CLI](https://allurereport.org/docs/install/) (for viewing reports)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/ecommerce-playwright-automation.git
cd ecommerce-playwright-automation

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Install Playwright browsers
playwright install
```

---

## Usage

### Run web UI tests

```bash
pytest -s -v test_cases/test_web.py --alluredir=./allure-results
```

### Run API tests

```bash
pytest -s -v test_cases/test_api.py --alluredir=./allure-results
```

### View the Allure report

```bash
allure serve allure-results
```

A browser window will open with the full step-level HTML report.

> **Tip:** After any failed test run, open `trace.zip` in the [Playwright Trace Viewer](https://playwright.dev/python/docs/trace-viewer) to replay the session step by step.

---

## CI/CD

This project is integrated with **Jenkins**. The pipeline is configured directly in the Jenkins UI (no Jenkinsfile in the repository) and runs two steps on every execution:

1. Runs the full pytest test suite
2. Generates and publishes the Allure report

The Allure report provides a detailed breakdown of every test run — pass/fail status, step-level execution details, and screenshots captured during the run — making it easy to track, monitor, and investigate failures without re-running tests locally.

---

## Configuration

### Environment config — `data/configuration.xml`

| Node | Default value | Purpose |
|---|---|---|
| `BROWSER_TYPE` | `chrome` | Which browser to launch (`chrome`, `firefox`, `edge`) |
| `SLOW_MODE` | `100` | Millisecond delay between Playwright actions (useful for visual debugging) |
| `BASE_URL` | `https://rahulshettyacademy.com/seleniumPractise/#/` | Web UI base URL |
| `BASE_URL_API` | `https://rahulshettyacademy.com/seleniumPractise/data/` | REST API base URL |

Switch browsers by changing `BROWSER_TYPE` — no test code changes required.

### Test data — `data/test_data.json`

Test inputs and expected values are organised by suite section and test name:

```json
{
  "web": {
    "test_verify_page_crucial_information": {
      "page_header": "GREENKART",
      "page_footer": "..."
    },
    ...
  },
  "api": {
    "test_verify_initial_header_amount": {
      "product_name": "Brocolli"
    },
    ...
  }
}
```

The `test_data` pytest fixture resolves the correct block automatically — tests never reference the JSON file directly.
