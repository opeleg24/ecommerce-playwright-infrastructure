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
4. [DRY Locator Loops](#4-dry-locator-loops)
5. [Auto-Waiting & Synchronization](#5-auto-waiting--synchronization)
6. [Assertions — Web-First `expect`](#6-assertions--web-first-expect)
7. [Test Data as Dataclass](#7-test-data-as-dataclass)
8. [Fixtures & Configuration](#8-fixtures--configuration)
9. [Page Object Internal Structure (SELECTORS → ATOMIC ACTIONS → FLOWS)](#9-page-object-internal-structure-selectors--atomic-actions--flows)

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

    # --- Locators (defined once, lazy) ---
    @property
    def diagnosis_title(self) -> Locator:
        return self.page.get_by_test_id("selected-diagnosis-title")

    @property
    def side_dropdown(self) -> Locator:
        return self.page.get_by_label("צד")

    @property
    def surgical_method_dropdown(self) -> Locator:
        return self.page.get_by_label("שיטה ניתוחית")

    @property
    def date_field(self) -> Locator:
        return self.page.get_by_test_id("surgery-date")

    @property
    def gynecologist_checkbox(self) -> Locator:
        return self.page.get_by_test_id("gynecolog-checkbox")

    @property
    def remarks_field(self) -> Locator:
        return self.page.get_by_label("הערות")

    @property
    def save_button(self) -> Locator:
        return self.page.get_by_role("button", name="שמור")

    # --- Atomic action methods (reusable across create, edit, delete flows) ---
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

    @property
    def email_input(self) -> Locator:
        return self.page.get_by_label("Email")

    @property
    def password_input(self) -> Locator:
        return self.page.get_by_label("Password")

    @property
    def sign_in_button(self) -> Locator:
        return self.page.get_by_role("button", name="Sign in")

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

## 3. Locators — Resilient vs Brittle

Prefer user-facing locators that survive DOM refactors. Define them as `Locator`
properties, never as raw strings repeated inside methods.

```python
# ❌ Bad — brittle, structure-coupled locators inlined in methods
def open_first_patient(self):
    self.page.locator("//div[3]/table/tr[2]/td[1]/a").click()        # XPath, positional
    self.page.locator("div.row > div:nth-child(2) > a.link").click()  # deep CSS chain
```

```python
# ✅ Good — user-facing locators, declared once as properties
class PatientListPage:
    def __init__(self, page: Page):
        self.page = page

    @property
    def search_input(self) -> Locator:
        return self.page.get_by_role("searchbox", name="Search patients")

    @property
    def add_patient_button(self) -> Locator:
        return self.page.get_by_role("button", name="Add patient")

    def patient_row(self, full_name: str) -> Locator:
        """Return the table row locator for a patient by visible name."""
        return self.page.get_by_role("row", name=full_name)

    def open_patient(self, full_name: str):
        """Open a patient's record by their displayed name."""
        self.patient_row(full_name).get_by_role("link").click()
```

**Locator preference order:** `get_by_role` → `get_by_label` → `get_by_placeholder` /
`get_by_text` → `get_by_test_id` → CSS (last resort) → *avoid XPath*.

Playwright locators are **strict**: if a locator matches more than one element, the
action raises instead of silently using the first. Resolve ambiguity on purpose:

```python
# Narrow a multi-match locator deliberately
self.page.get_by_role("listitem").filter(has_text="Active").click()
self.page.get_by_role("button", name="Delete").nth(0).click()
```

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
