# Automation Standards — Playwright Examples & Detailed Reference

This file contains detailed bad/good comparisons and code patterns referenced by the main SKILL.md.
Read the relevant section when you need concrete guidance on how to apply a rule.

**Target stack:** Playwright for Python, **sync API**, with **pytest-playwright** and the
Page Object Model. All examples assume:

```python
from playwright.sync_api import Page, Locator, expect
```

The `page` fixture is provided by `pytest-playwright`. Tests receive page objects through
their own fixtures (see section 8), never raw browser plumbing.

---

## Table of Contents

1. [Atomic Action Methods (Extract Method for Page Objects)](#1-atomic-action-methods-extract-method-for-page-objects)
2. [Page Objects with Injected `Page`](#2-page-objects-with-injected-page)
3. [Locators — Resilient vs Brittle](#3-locators--resilient-vs-brittle)
   - [3a. Selector-Builder Helpers](#3a-selector-builder-helpers)
4. [DRY Locator Loops](#4-dry-locator-loops)
5. [Auto-Waiting & Synchronization](#5-auto-waiting--synchronization)
6. [Assertions — Web-First `expect`](#6-assertions--web-first-expect)
7. [Test Data as Dataclass](#7-test-data-as-dataclass)
8. [Fixtures & Configuration](#8-fixtures--configuration)
9. [Page Object Internal Structure (SELECTORS → ATOMIC ACTIONS → FLOWS)](#9-page-object-internal-structure-selectors--atomic-actions--flows)
10. [Data-Driven Verification — Loop Over Checks](#10-data-driven-verification--loop-over-checks)
11. [Test Body Structure — Test Data Block + Numbered Steps](#11-test-body-structure--test-data-block--numbered-steps)
12. [Flow Method Numbered Steps](#12-flow-method-numbered-steps)

---

## 1. Atomic Action Methods (Extract Method for Page Objects)

Large page object methods that mix UI actions, verifications, and data logic
should be decomposed into small **atomic action methods** — each doing ONE thing.
The high-level method then composes them into a readable, self-documenting flow.

**Pattern name**: Extract Method (Martin Fowler's *Refactoring*)

```python
# ❌ Bad — one monolithic method mixing all abstraction levels
# Comments are needed because the code isn't self-explanatory
class SurgeryFormPage:
    def __init__(self, page: Page):
        self.page = page

    def add_current_surgery_form(self, create_surgery: dict):
        # verify name of diagnosis
        full_name = create_surgery['surgery_name'] + " (" + create_surgery[
            'surgery_code'] + ")"
        expect(self.page.get_by_test_id("selected-diagnosis-title")).to_have_text(full_name)
        # select side
        self.page.get_by_label("צד").select_option(create_surgery['side'])
        # select surgical method
        self.page.get_by_label("שיטה ניתוחית").select_option(create_surgery['surgery_method'])
        # open date picker
        self.page.get_by_test_id("surgery-date").click()
        create_surgery['surgery_date'] = get_today_date_format_d_m_y()
        # verify gynecologist is disabled
        expect(self.page.get_by_test_id("gynecolog-checkbox")).to_be_disabled()
        # remarks
        self.page.get_by_label("הערות").fill(create_surgery['remark'])
        # save
        self.page.get_by_role("button", name="שמור").click()
        create_surgery['created_date_and_time'] = get_today_date_format_time_day()
```

```python
# ✅ Good — atomic action methods + self-documenting high-level flow
class SurgeryFormPage:
    def __init__(self, page: Page):
        self.page = page

        # =================== SELECTORS ===================
        self.diagnosis_title = self.page.get_by_test_id("selected-diagnosis-title")
        self.side_dropdown = self.page.get_by_label("צד")
        self.surgical_method_dropdown = self.page.get_by_label("שיטה ניתוחית")
        self.date_field = self.page.get_by_test_id("surgery-date")
        self.gynecologist_checkbox = self.page.get_by_test_id("gynecolog-checkbox")
        self.remarks_field = self.page.get_by_label("הערות")
        self.save_button = self.page.get_by_role("button", name="שמור")

    # =================== ATOMIC ACTIONS ===================
    def verify_diagnosis_name(self, expected_name: str):
        """Assert the selected-diagnosis title matches the expected full name."""
        expect(self.diagnosis_title).to_have_text(expected_name)

    def select_side(self, side: str):
        """Select the surgery side from its dropdown."""
        self.side_dropdown.select_option(side)

    def select_surgical_method(self, method: str):
        """Select the surgical method from its dropdown."""
        self.surgical_method_dropdown.select_option(method)

    def open_date_picker(self):
        """Open the surgery date picker."""
        self.date_field.click()

    def verify_gynecologist_disabled(self):
        """Assert the gynecologist checkbox is disabled."""
        expect(self.gynecologist_checkbox).to_be_disabled()

    def fill_remarks(self, text: str):
        """Type the remarks text into the remarks field."""
        self.remarks_field.fill(text)

    def save(self):
        """Submit the form."""
        self.save_button.click()

    # --- High-level flow (reads like a script, no comments needed) ---
    def add_current_surgery_form(self, create_surgery: dict):
        """Fill and submit the surgery creation form, updating the dict with generated dates."""
        full_name = f"{create_surgery['surgery_name']} ({create_surgery['surgery_code']})"

        self.verify_diagnosis_name(full_name)
        self.select_side(create_surgery['side'])
        self.select_surgical_method(create_surgery['surgery_method'])
        self.open_date_picker()
        create_surgery['surgery_date'] = get_today_date_format_d_m_y()
        # Reason: gynecologist field is always disabled during historical surgery creation
        self.verify_gynecologist_disabled()
        self.fill_remarks(create_surgery['remark'])
        self.save()
        create_surgery['created_date_and_time'] = get_today_date_format_time_day()
```

**Key benefits:**
- Method names replace comments — `self.select_side(...)` needs no `# select side` comment
- Atomic methods are reusable — `select_side()`, `save()`, `fill_remarks()` work in edit/delete flows too
- The one remaining comment explains **WHY** (business rule), not WHAT
- Debugging is easier — stack traces point to the exact failing method
- Each method is ~1–3 lines thanks to Playwright's auto-waiting and `expect`

---

## 2. Page Objects with Injected `Page`

The `Page` comes from the pytest-playwright `page` fixture and is **passed in**.
Page objects never launch a browser, create a context, or open a page themselves.

```python
# ❌ Bad — page object launches its own browser and hardcodes the URL
from playwright.sync_api import sync_playwright

class LoginPage:
    def __init__(self):
        self._pw = sync_playwright().start()        # never do this in a page object
        self.browser = self._pw.chromium.launch()
        self.page = self.browser.new_page()
        self.page.goto("http://clinic.local/login")  # env hardcoded
```

```python
# ✅ Good — Page injected; navigation takes the environment as an argument
class LoginPage:
    def __init__(self, page: Page):
        self.page = page

        # =================== SELECTORS ===================
        self.email_input = self.page.get_by_label("Email")
        self.password_input = self.page.get_by_label("Password")
        self.sign_in_button = self.page.get_by_role("button", name="Sign in")

    def navigate(self):
        """Open the login page (base_url comes from pytest config)."""
        self.page.goto("/login")
        logger.info("Navigated to login page")

    def login(self, email: str, password: str):
        """Fill credentials and submit the login form."""
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.sign_in_button.click()
```

Because `base_url` is set in pytest config (section 8), `page.goto("/login")` resolves
against it — no hardcoded host in the page object.

> For the general dependency-injection principle, see the **python_standards**
> skill, reference section 8.

---

## 3. Locators — Project Conventions

This project uses three locator strategies, each for a specific role. Declare all stable
locators as instance attributes inside `__init__` under the SELECTORS banner — never as
raw strings repeated inside methods.

**Strategy order (use the first that fits):**

| Strategy | When to use | Example |
|---|---|---|
| **CSS — ID** | Element has a stable, unique id — most precise; use first | `#productCartTables`, `#productCartTables p[class='product-name']` |
| **CSS — class/attribute** | No id available — use the attribute-equals form | `[class='cart-icon']`, `[class='totAmt']`, `input[type='search']` |
| **Text engine** (`text=…`) | Buttons, links, CTAs identified by visible label | `text=Place Order`, `text=PROCEED TO CHECKOUT`, `text=Proceed` |
| **XPath** | (1) Dynamic visible-text lookup; (2) relative traversal from an anchored element | `//*[contains(text(), '{name}')]`, `//../div[2]/button` |

**What "brittle" means here:** absolute positional XPath from the document root or
auto-generated id chains — these are the forms that break on every DOM reshuffle.
Relative XPath anchored to an already-located element is the legitimate alternative.

---

### ❌ Bad — absolute positional XPath and deep unanchored CSS chains

```python
# ❌ Bad — position from root, breaks on any reorder
def open_first_product(self):
    self.page.locator("//div[3]/table/tr[2]/td[1]/a").click()           # absolute positional XPath
    self.page.locator("div.row > div:nth-child(2) > a.link").click()    # deep unanchored CSS chain
```

---

### ✅ Good — CSS attribute selectors as SELECTORS attributes

```python
class CheckOutPage:
    def __init__(self, page: Page):
        self.page = page

        # =================== SELECTORS ===================
        # -- Middle page information --
        self.middle_page_total_amount = self.page.locator("[class='totAmt']")
        self.middle_page_discount_perc = self.page.locator("[class='discountPerc']")
        self.total_after_discount = self.page.locator("[class='discountAmt']")

        # -- Buttons --
        self.place_order_button = self.page.locator("text=Place Order")
        self.apply_promo_button = self.page.locator("text=Apply")

        # -- Table --
        self.table_product_name = self.page.locator("#productCartTables p[class='product-name']")
        self.table_product_quantity = self.page.locator("#productCartTables p[class='quantity']")
        self.table_product_price = self.page.locator("#productCartTables p[class='amount']")
```

The `text=…` engine is the CSS attribute selector's sibling: both are stable and readable.
Use `text=` wherever the element's visible label is its identity.

---

### ✅ Good — XPath for dynamic text lookup and relative traversal

XPath is appropriate in two cases CSS can't cleanly handle:

```python
class ProductsPage:
    def __init__(self, page: Page):
        self.page = page

        # =================== SELECTORS ===================
        # -- Product card (dynamic; set by locate_product) --
        self.product = None     # resolved at runtime by locate_product()

    # =================== ATOMIC ACTIONS ===================
    def locate_product(self, product_name: str) -> None:
        """Store the product card locator matching the given product name."""
        # XPath: only way to find an element by interpolated runtime text
        self.product = self.page.locator(f"//*[contains(text(), '{product_name}')]")

    def get_product_price(self) -> str:
        # XPath relative traversal from self.product — navigates up then to sibling
        return UiActions.get_text(self.product.locator("//../p").nth(2))
```

The `self.product = None` pattern is the standard way to handle **dynamic runtime locators**:
initialise to `None` in `__init__`, assign in the action method that resolves the identity.

Parameterized locator methods that return a `Locator` directly (without storing an attribute)
are equally valid when the locator varies per call and never needs to be reused across methods.

---

### ✅ Good — narrowing a multi-match locator deliberately

Playwright locators are **strict**: if a locator matches more than one element, the
action raises instead of silently using the first. Narrow on purpose:

```python
# Narrow by index or position
self.table_product_price.first     # → first matching element
self.table_product_price.last      # → last matching element
self.product_name_in_cart.nth(0)   # → first cart product name
self.product_name_in_cart.nth(1)   # → second cart product name
```

---

### 3a. Selector-Builder Helpers

When the same container selector is repeated across SELECTOR attributes that differ only by a
child fragment, extract a private `_get_<area>_locator(part)` helper. Place it in a
`# =================== SELECTORS HELPERS ===================` banner between SELECTORS and
ATOMIC ACTIONS.

Helpers may produce **CSS or XPath** depending on the area's needs. For example,
`_get_product_card_locator(div_index, child_selector)` builds an XPath relative-traversal
string for product-card interactions — 2 params, within the acceptable ceiling. The same
param-cap and naming rules apply regardless of the selector engine used.

```python
# ❌ Bad (1) — container selector duplicated in every attribute
class ProductsPage:
    def __init__(self, page: Page):
        # =================== SELECTORS ===================
        self.no_results_heading     = self.page.locator("[class='no-results'] h2")  # "no-results" ×2
        self.no_results_description = self.page.locator("[class='no-results'] p")   # duplicated
        self.header_item_count  = self.page.locator("[class='cart-info'] tr:first-child strong")
        self.header_total_price = self.page.locator("[class='cart-info'] tr:last-child strong")  # duplicated
```

```python
# ❌ Bad (2) — over-generic "selector engine"; leaks raw DOM fragments to call sites
class ProductsPage:
    # 3 params + strategy param = building a DSL → too much
    def _get_locator(self, container: str, child: str, strategy: str = "css") -> Locator:
        return self.page.locator(f"[class='{container}'] {child}")

    def get_no_results_heading(self) -> str:
        return UiActions.get_text(self._get_locator("no-results", "h2"))          # fragment leaks out

    def get_header_item_count(self) -> str:
        return UiActions.get_text(self._get_locator("cart-info", "tr:first-child strong"))  # same
```

```python
# ✅ Good — one private 1-param helper per UI area; named atomic getters preserve the domain vocabulary
from playwright.sync_api import Locator, Page
from extentions.ui_actions import UiActions


class ProductsPage:
    def __init__(self, page: Page):
        self.page = page

        # =================== SELECTORS ===================
        # (no duplicated container strings — each helper owns its container)
        self.cart_icon = self.page.locator("[class='cart-icon']")
        ...

    # =================== SELECTORS HELPERS ===================
    def _get_no_results_locator(self, tag: str) -> Locator:
        """Build a locator for an element inside the no-results empty-state block."""
        return self.page.locator(f"[class='no-results'] {tag}")

    def _get_cart_info_locator(self, row: str) -> Locator:
        """Build a locator for a strong cell inside the cart-info summary table."""
        return self.page.locator(f"[class='cart-info'] {row} strong")

    # =================== ATOMIC ACTIONS ===================
    # Each getter encodes a unique domain fact.
    # Their shared UiActions.get_text(...) is a repeated *idiom*, not repeated *knowledge* — keep separate.
    def get_no_results_heading(self) -> str:
        return UiActions.get_text(self._get_no_results_locator("h2"))

    def get_no_results_description(self) -> str:
        return UiActions.get_text(self._get_no_results_locator("p"))

    def get_header_item_count(self) -> str:
        return UiActions.get_text(self._get_cart_info_locator("tr:first-child"))

    def get_header_total_price(self) -> str:
        return UiActions.get_text(self._get_cart_info_locator("tr:last-child"))
```

**Rules at a glance:**

| # params | Decision |
|---|---|
| 0 | It's a constant locator → belongs in `__init__` SELECTORS, not a helper |
| 1 | Sweet spot — fixed container, one varying child |
| 2 | Acceptable ceiling when genuinely needed |
| 3+ | You're building a selector DSL → stop |

**Why keep the four atomic getters separate?**
`get_no_results_heading` and `get_no_results_description` share the same `UiActions.get_text(...)` call.
That's a repeated *idiom* (a verb), not repeated *knowledge*. Each getter encodes a unique, independent
fact — "the heading is `h2`", "the description is `p`" — in exactly one place. Collapsing them into
`get_no_results_text("h2")` would leak `"h2"` to every caller and destroy the method's self-documenting name.
*Duplicated idiom is not duplicated knowledge.*

---

## 4. DRY Locator Loops

When the same fill pattern repeats with only the value changing, drive it from
structured data instead of copy-pasting blocks.

```python
# ❌ Bad — repetitive blocks doing the same thing with different values
self.page.get_by_label("Days").fill(side_effect_data['exposure_days'])
self.page.get_by_label("Hours").fill(side_effect_data['exposure_hours'])
self.page.get_by_label("Minutes").fill(side_effect_data['exposure_minutes'])

# ✅ Good — one loop, structured data, zero duplication
exposure_fields = [
    ("Days", 'exposure_days'),
    ("Hours", 'exposure_hours'),
    ("Minutes", 'exposure_minutes'),
]
for label, field in exposure_fields:
    self.page.get_by_label(label).fill(side_effect_data[field])
```

Extract a repeated multi-step sequence into one helper:

```python
# ✅ Good — one reusable helper instead of duplicated clear-and-fill logic
def clear_and_fill(self, field: Locator, value: str):
    """Clear a field and type a new value into it."""
    field.clear()
    field.fill(value)
```

---

## 5. Auto-Waiting & Synchronization

Playwright **auto-waits** for elements to be actionable before acting, and `expect`
retries until its condition holds. You almost never need an explicit wait — and you
should never use a fixed sleep for synchronization.

```python
# ❌ Bad — manual sleep hoping the element shows up in time
self.page.wait_for_timeout(5000)   # flaky and slow
self.page.get_by_role("button", name="Save").click()

# ✅ Good — auto-waiting handles it; the click waits for actionability itself
self.page.get_by_role("button", name="Save").click()
```

```python
# ❌ Bad — bare try/except swallowing failures
try:
    self.page.get_by_test_id("patient-name").click()
except Exception:
    pass

# ✅ Good — assert the element is ready with a web-first assertion, then act
expect(self.page.get_by_test_id("patient-name")).to_be_visible()
self.page.get_by_test_id("patient-name").click()
```

For **non-element** conditions, use the targeted API instead of a blind sleep:

```python
# ✅ Good — wait on the specific condition you care about
self.page.get_by_role("button", name="Sign in").click()
self.page.wait_for_url("**/dashboard")          # URL changed
self.page.wait_for_load_state("networkidle")    # network settled

# Waiting on a value that isn't a DOM assertion:
expect.poll(lambda: get_job_status(job_id)).to_be("completed")

# Asserting on a response triggered by an action:
with self.page.expect_response("**/api/patients") as response_info:
    self.page.get_by_role("button", name="Load").click()
assert response_info.value.ok
```

The only acceptable fixed wait is a documented workaround for a real quirk:

```python
# Reason: third-party animation has no settled state to await; 300ms avoids a flake
self.page.wait_for_timeout(300)
```

---

## 6. Assertions — Web-First `expect`

Use Playwright's `expect(locator)` for UI state. It auto-retries until the condition
is met or the timeout expires, which removes whole classes of flakiness. Reserve plain
`assert` for non-UI values.

```python
# ❌ Bad — reads state once, no retry; races against rendering
assert self.page.get_by_test_id("total").inner_text() == "₪1,250"
assert self.page.get_by_role("button", name="Submit").is_enabled() is True

# ✅ Good — web-first assertions retry until true (or fail with a clear message)
expect(self.page.get_by_test_id("total")).to_have_text("₪1,250")
expect(self.page.get_by_role("button", name="Submit")).to_be_enabled()
expect(self.page.get_by_text("Saved successfully")).to_be_visible()
expect(self.page.get_by_label("Email")).to_have_value("user@example.com")
```

Assert on a specific, named locator so the failure message points at the right element:

```python
# ✅ Good — the locator names the thing under test; failure output is self-explaining
def verify_order_total(self, expected_total: str):
    """Assert the displayed order total matches the expected value."""
    expect(self.total_label).to_have_text(expected_total)
```

---

## 7. Test Data as Dataclass

Pass structured, typed test data rather than loose dicts where practical — it's
self-documenting and catches typos early.

```python
# ❌ Bad — passing around loose dicts with no structure
patient_data = {
    "name": "ישראל ישראלי",
    "id": "123456789",
    "age": 45,
    "ward": "פנימית",
}

# ✅ Good — structured, typed, self-documenting
from dataclasses import dataclass

@dataclass
class PatientTestData:
    full_name: str
    patient_id: str
    age: int
    ward_name: str

patient = PatientTestData(
    full_name="ישראל ישראלי",
    patient_id="123456789",
    age=45,
    ward_name="פנימית",
)
```

---

## 8. Fixtures & Configuration

Wire page objects through pytest fixtures so tests stay clean and never touch raw
browser plumbing. Set environment-level config (`base_url`, timeouts, tracing) in
pytest config, not inline.

```python
# conftest.py — expose page objects as fixtures built on the pytest-playwright `page`
import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage
from pages.patient_list_page import PatientListPage


@pytest.fixture
def login_page(page: Page) -> LoginPage:
    """A LoginPage bound to the test's page."""
    return LoginPage(page)


@pytest.fixture
def patient_list_page(page: Page) -> PatientListPage:
    """A PatientListPage bound to the test's page."""
    return PatientListPage(page)
```

```python
# A test reads like plain English — no Page wiring, no waits, no hardcoded host
def test_login_shows_dashboard(login_page: LoginPage):
    """A valid login lands the user on the dashboard."""
    login_page.navigate()
    login_page.login(email=ADMIN_EMAIL, password=ADMIN_PASSWORD)
    expect(login_page.page.get_by_role("heading", name="Dashboard")).to_be_visible()
```

```ini
# pytest.ini — base_url and run settings live here, not in test code
[pytest]
addopts = --base-url https://app.example.com --tracing retain-on-failure
```

```python
# Environment values come from env vars, never hardcoded literals
import os

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
```

With `--base-url` set, page objects call `self.page.goto("/login")` and Playwright
resolves the path against the configured host — so switching environments is a config
change, not a code change.

---

## 9. Page Object Internal Structure (SELECTORS → ATOMIC ACTIONS → FLOWS)

Every page object must be split into three named sections. Comment banners make the
boundaries explicit and scannable.

### The rule in one sentence

**SELECTORS** hold locators; **ATOMIC ACTIONS** do exactly one thing each (via `UiActions`);
**FLOWS** compose atomic actions from the same page — cross-page flows stay in the workflow layer.

---

### ❌ Bad — flat class, no structure, raw locators inside flow methods

```python
class ProductsPage:
    def __init__(self, page: Page):
        self.page = page
        self.cart_icon = self.page.locator("[class='cart-icon']")
        self.proceed_to_checkout = self.page.locator("text=PROCEED TO CHECKOUT")
        self.items_indicator_header = self.page.locator("[class='cart-info'] tr:first-child strong")

    # mixes locator access, UiActions calls, and two-step composition — no structure
    def proceed_to_checkout_flow(self) -> None:
        UiActions.click(self.cart_icon)
        UiActions.click(self.proceed_to_checkout)

    # raw locators accessed from the workflow layer — page internals leak out
    # (web_flow.py): UiActions.get_text(base.products_page.items_indicator_header)
```

Problems:
- No visible structure — a reader must scan the whole class to understand its shape.
- The workflow layer reaches into raw locators instead of calling named methods, coupling it to the DOM.
- Single-page verify logic is scattered across `WebFlows` instead of living with its page.

---

### ✅ Good — three-part structure, clean boundary between layers

```python
import allure
from playwright.sync_api import Page

from extentions.ui_actions import UiActions
from extentions.verifications import Verifications


class ProductsPage:
    """Page object for the products listing, header cart indicator, and cart panel."""

    def __init__(self, page: Page):
        self.page = page

        # =================== SELECTORS ===================
        # -- Page header / footer --
        self.page_header = self.page.locator("[class='brand greenLogo']")
        self.page_footer = self.page.locator("footer")

        # -- Cart indicator (header) --
        self.items_indicator_header = self.page.locator("[class='cart-info'] tr:first-child strong")
        self.price_indicator_header = self.page.locator("[class='cart-info'] tr:last-child strong")
        self.cart_icon = self.page.locator("[class='cart-icon']")

        # -- Cart panel --
        self.proceed_to_checkout = self.page.locator("text=PROCEED TO CHECKOUT")

    # =================== ATOMIC ACTIONS ===================
    # -- Page header / footer --
    def get_page_header_text(self) -> str:
        return UiActions.get_text(self.page_header)

    def get_footer_text(self) -> str:
        return UiActions.get_text(self.page_footer)

    # -- Cart indicator (header) --
    def get_header_item_count(self) -> str:
        return UiActions.get_text(self.items_indicator_header)

    def get_header_total_price(self) -> str:
        return UiActions.get_text(self.price_indicator_header)

    # -- Cart panel --
    def open_cart(self) -> None:
        UiActions.click(self.cart_icon)

    def click_proceed_to_checkout(self) -> None:
        UiActions.click(self.proceed_to_checkout)

    # =================== FLOWS ===================
    @allure.step("Proceed to checkout page")
    def proceed_to_checkout_flow(self) -> None:
        """Open the cart and navigate to the checkout page."""
        self.open_cart()
        self.click_proceed_to_checkout()

    @allure.step("Verify page header text")
    def verify_page_header(self, expected: str) -> None:
        """Verify the brand header text matches the expected value."""
        Verifications.verify_soft_assert_equals(
            self.get_page_header_text().strip(), expected, "Page header"
        )

    @allure.step("Verify initial amount in header display")
    def verify_initial_amount_in_header_display(self, initial_items: str, initial_price: str) -> None:
        """Verify the header shows the expected initial item count and price."""
        Verifications.verify_soft_assert_equals(self.get_header_item_count(), initial_items)
        Verifications.verify_soft_assert_equals(self.get_header_total_price(), initial_price)
```

---

### The workflow layer — cross-page flows only

When a flow must touch **more than one page object**, it belongs in the workflow layer,
not inside any single page object.

```python
# workflows/web_flow.py
import allure
from utilities import base


class WebFlows:

    @staticmethod
    @allure.step("Proceed to final country page")
    def proceed_to_country_page_flow() -> None:
        """Navigate from the products page through checkout to the country page."""
        base.products_page.proceed_to_checkout_flow()   # ProductsPage
        base.check_out_page.click_place_order()          # CheckOutPage
```

This method coordinates two page objects, so it lives in `WebFlows`. Neither
`ProductsPage` nor `CheckOutPage` knows about the other.

---

### Decision guide — where does a method belong?

| Condition | Where it goes |
|---|---|
| Sets a locator attribute (`self.<x> = ...`) | `__init__` SELECTORS |
| Does exactly one UI action or reads one value | ATOMIC ACTIONS |
| Composes this page's own atomic actions | FLOWS (same page object) |
| Calls `Verifications.*` using this page's getters | FLOWS (same page object) |
| Touches locators / methods from two or more page objects | Workflow layer (`WebFlows`) |

---

## 10. Data-Driven Verification — Loop Over Checks

When a flow method contains the same `Verifications.verify_soft_assert_equals(actual, expected, message)`
call repeated line-by-line with only the values changing, collapse it into a list of
`(actual, expected, message)` tuples passed to `HelpersPage.verify_all_soft_equals`.

This is the automation-layer application of the DRY principle: repetitive blocks → structured
data + loop. See `python_standards` references section 1.1 for the general pattern.

`HelpersPage` lives in `utilities/helpers_page.py` and is stateless — import it directly
in any page object (exactly like `Verifications` or `UiActions`).

### ❌ Bad — repeated calls, same pattern copy-pasted

```python
@allure.step("Verify cart information in table")
def verify_cart_information_in_table(self, product_name: str, price: str,
                                     counter: str, total_price: str) -> None:
    """Verify the checkout table row: name, price, quantity, and total."""
    Verifications.verify_soft_assert_equals(self.get_table_product_name(), product_name, "product name")
    Verifications.verify_soft_assert_equals(self.get_table_product_price(), price, "product price")
    Verifications.verify_soft_assert_equals(self.get_table_product_quantity(), counter)   # message missing!
    Verifications.verify_soft_assert_equals(self.get_table_total_price(), total_price, "total price")
```

Problems:
- The `Verifications.verify_soft_assert_equals(...)` line is copy-pasted four times — only the
  arguments change.
- One check silently omits the message, giving a worse failure diagnostic.
- Adding or reordering checks means duplicating another line.

### ✅ Good — structured tuple list + single loop via `HelpersPage`

```python
from utilities.helpers_page import HelpersPage

@allure.step("Verify cart information in table")
def verify_cart_information_in_table(self, product_name: str, price: str,
                                     counter: str, total_price: str) -> None:
    """Verify the checkout table row: name, price, quantity, and total."""
    HelpersPage.verify_all_soft_equals(
        (self.get_table_product_name(), product_name, "product name"),
        (self.get_table_product_price(), price, "product price"),
        (self.get_table_product_quantity(), counter, "product quantity"),
        (self.get_table_total_price(), total_price, "total price"),
    )
```

**Rules:**
- Each check is a 3-tuple: `(actual, expected, message)` — **message is always required**.
- One tuple per line for readability; trailing comma on the last tuple.
- The flow method still carries its `@allure.step` and docstring — `verify_all_soft_equals`
  is a helper, not a replacement for the flow structure.
- A lone `verify_contains` or a single `verify_soft_assert_equals` call doesn't need the
  loop — only apply this pattern when two or more identical calls would otherwise repeat.

---

## 11. Test Body Structure — Test Data Block + Numbered Steps

Every test method body follows a two-part layout: a `# Test Data` block up top that
extracts `test_data[...]` values into named locals, then numbered step comments directly
above each action call. This keeps the data in one scannable place and labels each step
without burying the reader in noise.

### ❌ Bad — inline dict access, no structure, no step labels

```python
@allure.title("Test03 Add product to cart - verify amount in header display")
@allure.description("This test adds a product to the cart and verifies the amount in the header display")
def test_verify_add_product_to_cart(self, test_data):
    """Add a product to the cart and verify the header display amount."""
    base.products_page.add_product_to_cart(test_data["product"])
    base.products_page.open_cart()
    base.products_page.verify_cart_information_in_header_display(test_data["counter_one_product"],
                                                                  test_data["product_one_price"])
```

Problems:
- `test_data["..."]` keys are scattered across the action calls — you must read the calls
  to discover what data the test uses.
- No visual separation between setup data and test steps.
- A reader scanning quickly cannot tell how many steps the test has or what they are.

### ✅ Good — `# Test Data` block + numbered step comments

```python
@allure.title("Test03 Add product to cart - verify amount in header display")
@allure.description("This test adds a product to the cart and verifies the amount in the header display")
def test_verify_add_product_to_cart(self, test_data):
    """Add a product to the cart and verify the header display amount."""
    # Test Data
    product = test_data["product"]
    counter_one_product = test_data["counter_one_product"]
    product_one_price = test_data["product_one_price"]

    # 1. Add product to cart
    base.products_page.add_product_to_cart(product)
    # 2. Open cart
    base.products_page.open_cart()
    # 3. Verify cart information in header display
    base.products_page.verify_cart_information_in_header_display(counter_one_product, product_one_price)
```

**Rules:**

- **`# Test Data` block first** — extract `test_data["key"]` into a named local for each
  value that is **reused across multiple steps** or feeds an action step. All extractions
  together, before any actions.
- **One blank line** between the `# Test Data` block and the first step comment.
- **Numbered step comments** — `# 1. <Action name>` directly above each action call.
  The label names the action, matching the called method (e.g., `open_cart` → `# 2. Open cart`).
- **No blank lines between consecutive steps** — the comment and its call stay visually paired.
- Step labels are the one place "what" comments are intentional and welcome. They make the
  test read like a numbered checklist and speed up debugging by letting you scan step numbers
  in CI output.
- When a page-object method needs many fields, prefer **Introduce Parameter Object** (A) over
  a long parameter list. Fall back to **inline at the call site** (B) only for generic methods
  shared across tests.

---

### A. Prefer: Introduce Parameter Object

When a page-object method needs many fields that all come from **one test's data**, pass
the whole `test_data` dict. The method destructures inside; the test's call site stays clean.
Private helper methods keep their explicit, well-named params — destructuring happens only
at the public entry point.

#### ❌ Bad — 6-parameter list, test threads every field individually

```python
# products_page.py
@allure.step("Verify cart information in cart panel")
def verify_cart_information_in_cart(self, product_one: str, product_two: str,
                                    price_product_one: int, price_product_two: int,
                                    expected_total_price_for_one_product: int,
                                    expected_total_price_for_two_products: int) -> None:
    ...

# test_web.py
# 4. Verify cart information in cart
base.products_page.verify_cart_information_in_cart(product_one, product_two,
                                                   test_data["product_one_price"],
                                                   test_data["product_two_price"],
                                                   test_data["expected_total_price_prod_one"],
                                                   test_data["expected_total_price_prod_two"])
```

#### ✅ Good — data object passed in; method owns the destructuring

```python
# products_page.py
@allure.step("Verify cart information in cart panel")
def verify_cart_information_in_cart(self, data: dict) -> None:
    """Open the cart and verify product names, unit prices, and line totals."""
    self.open_cart()
    self._verify_cart_product_names(data["product_one"], data["product_two"])
    actual_price_one, actual_price_two = self._verify_cart_prices(
        data["product_one_price"], data["product_two_price"])
    self._verify_cart_totals(actual_price_one, actual_price_two,
                             data["expected_total_price_prod_one"],
                             data["expected_total_price_prod_two"])

# test_web.py
# Test Data
product_one = test_data["product_one"]   # reused: steps 1 and 2
product_two = test_data["product_two"]   # reused: steps 2 and 4

# 1. Add first product to cart
base.products_page.add_product_to_cart(product_one)
# 2. Add second product to cart
base.products_page.add_two_products_to_cart(product_two)
# 3. Open cart
base.products_page.open_cart()
# 4. Verify cart information in cart
base.products_page.verify_cart_information_in_cart(test_data)
```

The `# Test Data` block only names the two product values that are reused across steps.
The four price/total values belong to the verify method — the method, not the test, owns them.

---

### B. Fallback: Inline at the call site

Use this when the page-object method is a **generic helper reused by multiple tests with
differently-named data keys**. Converting such a method to `data: dict` would break because
each caller's dict has different key names — the method can't hard-code which key to read.
Keep its explicit params and pass `test_data["key"]` inline at each call site.

```python
# verify_purchase_flow_with_correct_promo_code is shared by Test06 AND Test07.
# Test06 data has: success_message, total_after_discount
# Test07 data has: unsuccess_message  (no total_after_discount — uses expected_total_price instead)
# → method must stay explicit; each test inlines its own keys.

# Test06 — correct promo code
base.check_out_page.verify_purchase_flow_with_correct_promo_code(test_data["success_message"],
                                                                  test_data["expected_total_price"],
                                                                  test_data["discount"],
                                                                  test_data["total_after_discount"])

# Test07 — incorrect promo code
base.check_out_page.verify_purchase_flow_with_correct_promo_code(test_data["unsuccess_message"],
                                                                  test_data["expected_total_price"],
                                                                  test_data["discount"],
                                                                  test_data["expected_total_price"])
```

**Decision rule:**

| Situation | Technique |
|---|---|
| Method called by one test; all fields from that test's data | **A — Introduce Parameter Object** (`data: dict`) |
| Method shared by multiple tests with different data key names | **B — Inline** (`test_data["key"]` at call site) |

---

## 12. Flow Method Numbered Steps

Every multi-step FLOW method in a page object or the workflow layer gets `# N. <description>`
comments — one directly above each call. No `# Test Data` block (flows don't receive
`test_data`). Single-call methods (one atomic action or one `verify_all_soft_equals(...)`)
need no step comments.

### ❌ Bad — multi-step flow with no step labels

```python
@allure.step("Filling country page information")
def filling_country_page_information_flow(self, country: str) -> None:
    """Select the country, accept terms, and proceed from the country page."""
    self.select_shipping_country(country)
    self.accept_terms_and_conditions()
    self.click_proceed()
```

A reader has to read each call to understand the sequence. Harder to scan and debug.

### ✅ Good — numbered steps, no `# Test Data` block

```python
@allure.step("Filling country page information")
def filling_country_page_information_flow(self, country: str) -> None:
    """Select the country, accept terms, and proceed from the country page."""
    # 1. Select shipping country
    self.select_shipping_country(country)
    # 2. Accept terms and conditions
    self.accept_terms_and_conditions()
    # 3. Click proceed
    self.click_proceed()
```

### ✅ Good — workflow-layer flow (cross-page)

```python
@staticmethod
@allure.step("Proceed to final country page")
def proceed_to_country_page_flow() -> None:
    """Proceed through checkout to the final country page."""
    # 1. Proceed to checkout
    base.products_page.proceed_to_checkout_flow()
    # 2. Click place order
    base.check_out_page.click_place_order()
```

### ✅ Good — verify-style flow with multiple helper calls

```python
@allure.step("Verify cart information in cart panel")
def verify_cart_information_in_cart(self, data: dict) -> None:
    """Open the cart and verify product names, unit prices, and line totals."""
    # 1. Open cart
    self.open_cart()
    # 2. Verify product names
    self._verify_cart_product_names(data["product_one"], data["product_two"])
    # 3. Verify unit prices
    actual_price_one, actual_price_two = self._verify_cart_prices(
        data["product_one_price"], data["product_two_price"])
    # 4. Verify line totals
    self._verify_cart_totals(actual_price_one, actual_price_two,
                             data["expected_total_price_prod_one"],
                             data["expected_total_price_prod_two"])
```

**Rules:**
- Number starts at `1`, increments by 1 for each call in the method body.
- Label is short and imperative: matches what the called method does (`open_cart` → `# 1. Open cart`).
- No blank lines between the comment and the call it labels — they stay visually paired.
- Single-call methods (atomic actions, single `verify_all_soft_equals`, fetch+return) need no step comments.
