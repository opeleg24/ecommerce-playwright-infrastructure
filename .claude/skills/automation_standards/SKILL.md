---
name: automation_standards
description: >
  Enforce clean standards and design patterns for UI test automation with Playwright (Python).
  Use this skill EVERY TIME you write, modify, create, or refactor Playwright automation —
  page objects, test flows, locators, assertions, fixtures, or waits.
  Covers the Page Object Model with pytest-playwright fixtures, atomic action methods,
  Playwright locator best practices (role/label/test-id, web-first assertions, auto-waiting),
  and how to keep tests reliable and readable.
  Uses the Playwright sync API. For pure language-level rules (naming, typing, SOLID,
  DRY, idioms), see the separate python_standards skill — this skill assumes those and
  builds on them.
---

# Automation Standards — Playwright UI Test Automation (Python)

Every Playwright automation change must pass through these standards before being considered complete.
These rules sit on top of the `python_standards` skill — follow both.

This skill targets **Playwright for Python, sync API**, with **pytest-playwright** and the
**Page Object Model**. For detailed bad/good comparisons and code examples, read
`references/reference_examples_automation_standards.md`.

**Core Playwright principles to lean on (don't fight the framework):**
- **Auto-waiting** — Playwright waits for elements to be actionable before acting. Don't add manual sleeps.
- **Web-first assertions** — `expect(locator)` retries until the condition is met or times out.
- **Resilient locators** — prefer user-facing locators (`get_by_role`, `get_by_label`, `get_by_text`, `get_by_test_id`) over CSS/XPath tied to DOM structure.

---

## 1. Page Object Model (with pytest fixtures)

- One page object class per logical page or major component.
- The page object receives an injected **`Page`** in its constructor — it never creates its own browser, context, or page. The `page` comes from the pytest-playwright `page` fixture.
- Wrap each page object in its own pytest **fixture** so tests receive ready-to-use page objects, not raw `Page` plumbing.
- Page objects expose **locators** (as `Locator` properties) and **actions/verifications** — they don't contain the test's business assertions about overall outcomes; those read clearly in the test using `expect`.

*(See `references/reference_examples_automation_standards.md` section 2 for injected-`Page` objects and section 8 for the fixture wiring.)*

## 2. Page Object Internal Structure (SELECTORS → ATOMIC ACTIONS → FLOWS)

Every page object must be organised into three explicit sections, each marked with a comment banner:

```python
# =================== SELECTORS ===================
# =================== ATOMIC ACTIONS ===================
# =================== FLOWS ===================
```

**SELECTORS** (inside `__init__`)
- Declare every locator as an instance attribute. Group by UI area under short sub-comments.
- No logic here — only `self.<name> = self.page.locator(...)` assignments.

**ATOMIC ACTIONS**
- One method, one thing: a single click, fill, select, or get.
- Implement via `UiActions` wrappers (or equivalent `@allure.step`-decorated helpers) so allure instrumentation is preserved.
- No assertions, no multi-step compositions — each body is typically one line.
- Method names replace comments: `open_cart()` needs no `# click cart icon` annotation.

**FLOWS**
- Compose the same page's own atomic actions into multi-step sequences.
- Single-page verify methods (calling `Verifications.*` on the page's own getters) also live here.
- **A flow that touches more than one page object belongs in the workflow layer** (e.g. `WebFlows`), not in any page object. Keep cross-page orchestration in the workflow layer.

*(See `references/reference_examples_automation_standards.md` section 9 for a full three-part example drawn from this project.)*

## 3. Atomic Action Methods (Extract Method)

Large page object methods that mix UI actions, verifications, and data logic
should be decomposed into small **atomic action methods** — each doing ONE thing.
The high-level method then composes them into a readable, self-documenting flow.

**Pattern name**: Extract Method (Martin Fowler's *Refactoring*)

- Each atomic method does ONE thing: click, fill, select, or verify.
- Method names replace comments — if the name says what it does, no comment needed.
- Atomic methods are reusable building blocks across flows (create, edit, delete, etc.).
- The high-level method reads like a step-by-step script at one abstraction level.
- Each atomic method stays well under the ~20-line limit (usually ~3 lines with Playwright).

*(See `references/reference_examples_automation_standards.md` section 1 for the full Extract Method walkthrough.)*

## 4. Locators

- **Prefer user-facing locators** in this order: `get_by_role` → `get_by_label` → `get_by_placeholder` / `get_by_text` → `get_by_test_id`. Fall back to CSS only when nothing user-facing fits; avoid XPath and brittle structural chains.
- Define locators as **`Locator` properties** on the page object (lazy, defined once), not as raw strings repeated inside methods.
- Lean on Playwright's **strictness** — a locator that matches multiple elements raises, which surfaces ambiguity early. Narrow with `.filter()`, `name=`, or `.nth()` deliberately.
- Never build locators from volatile data (auto-generated ids, deep `div > div > div` paths).

*(See `references/reference_examples_automation_standards.md` section 3 for locator examples and section 4 for DRY locator loops.)*

## 5. Waiting & Synchronization

- **Rely on auto-waiting.** Playwright actions (`click`, `fill`, etc.) wait for the element to be visible, enabled, and stable automatically. Don't precede them with manual waits.
- **Use web-first assertions** for state: `expect(locator).to_be_visible()`, `.to_have_text(...)`, `.to_be_enabled()`. These retry automatically — no polling loops.
- **Never use `page.wait_for_timeout()` / `time.sleep()` for synchronization.** A fixed sleep is only acceptable as a documented `# Reason:` workaround for a genuine, unavoidable quirk.
- When you must wait for a non-element condition, use the targeted API: `page.wait_for_url(...)`, `page.wait_for_load_state(...)`, `expect.poll(...)`, or `page.expect_response(...)` — never a blind sleep.
- Timeouts come from config / fixtures, not hardcoded magic numbers scattered in tests.

*(See `references/reference_examples_automation_standards.md` section 5 for auto-waiting and assertion patterns.)*

## 6. Assertions

- Use Playwright's **`expect`** (web-first, auto-retrying) for anything UI-state related, not bare `assert` on a value read once.
- Assert on user-visible state (`to_be_visible`, `to_have_text`, `to_have_value`, `to_be_enabled`) rather than implementation details.
- Give failing assertions context — assert on a specific, named locator so the failure message points at the right element.
- **DRY verification — never repeat `Verifications.verify_soft_assert_equals(...)` line-by-line.** When two or more soft-assert checks share the same pattern, build a list of `(actual, expected, message)` 3-tuples and pass them to `HelpersPage.verify_all_soft_equals(...)` from `utilities/helpers_page.py`. Message is **always required** — no 2-tuples.

*(See `references/reference_examples_automation_standards.md` section 6 for assertion examples and section 10 for the data-driven verification pattern.)*

## 7. Test Data & Configuration

- Pass structured, typed test data (dataclasses) rather than loose dicts where practical.
- No hardcoded URLs, credentials, or environment values in tests — use `base_url` config, env vars, or fixtures.
- Configure `base_url`, timeouts, headed/headless, and tracing in `pytest.ini` / `conftest.py`, not inline in tests.

*(See `references/reference_examples_automation_standards.md` section 7 for dataclass test-data patterns and section 8 for config/fixtures.)*

## 8. Test Body Structure (Test Data → Numbered Steps) + Flow Methods

Every test method body follows a two-part layout:

1. **`# Test Data` block** — extract each `test_data["..."]` value into a local variable named after its key. Group all extractions at the top, before any actions.
2. **Numbered step comments** — put `# 1. <Action name>`, `# 2. <Action name>`, … directly above each action call. The label names the action (matches the called method). This is the one place "what" comments are intentional — they make test steps scannable at a glance.

**When a page-object method needs many fields — prefer *Introduce Parameter Object*:**
- If a verify or flow method would take more than ~3 parameters and all those values come from one test's data, pass the whole `test_data` dict and let the method destructure inside. This eliminates the long argument list at the call site.
- Keep the `# Test Data` block to the small set of values **reused across action steps** (added to cart, passed to multiple calls). Single-use verify arguments go via the data object, not extracted to locals.
- **Fallback — inline at the call site:** when the method is a generic helper reused by multiple tests with differently-named keys (e.g. `success_message` vs `unsuccess_message`), keep its explicit params and pass `test_data["key"]` inline. Do not convert to `data: dict` in this case — the key names would differ per caller.

**Spacing rules:**
- One blank line between the `# Test Data` block and the first step comment.
- No blank lines between consecutive numbered steps.

```python
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

*(See `references/reference_examples_automation_standards.md` section 11 for the full bad/good comparison.)*

### Flow methods — numbered steps only (no `# Test Data` block)

The same `# N. <description>` convention applies to every **multi-step FLOW method** in page objects and the workflow layer. Flow methods don't use a `# Test Data` block — they start directly with `# 1.`. Single-call methods (one atomic action or one verification call) need no step comments.

```python
# ❌ Bad — multi-step flow with no step labels
@allure.step("Filling country page information")
def filling_country_page_information_flow(self, country: str) -> None:
    """Select the country, accept terms, and proceed from the country page."""
    self.select_shipping_country(country)
    self.accept_terms_and_conditions()
    self.click_proceed()

# ✅ Good — same flow with numbered step comments
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

This applies equally to workflow-layer flows (e.g. `WebFlows`) and to verify-style flows that call multiple helper methods.

*(See `references/reference_examples_automation_standards.md` section 11 for bad/good comparisons covering both test bodies and flow methods.)*

---

## 9. Automation Review Checklist

Before completing ANY Playwright automation change, verify:

- [ ] Page objects receive an injected `Page` (from the `page` fixture) — none create their own (section 1)
- [ ] Each page object is exposed via its own pytest fixture; tests don't wire up raw `Page` (section 1)
- [ ] Each page object is split into SELECTORS / ATOMIC ACTIONS / FLOWS sections with comment banners; flows use only that page's own atomic actions; cross-page flows live in the workflow layer (section 2)
- [ ] Locators are `Locator` properties using `get_by_role`/`get_by_label`/`get_by_test_id`; no XPath or brittle CSS (section 4)
- [ ] Large flows are decomposed into atomic action methods; names replace comments (section 3)
- [ ] No manual sleeps or `wait_for_timeout` for sync — auto-waiting and `expect` used instead (section 5)
- [ ] UI state checked with web-first `expect(locator)` assertions, not one-shot `assert` (section 6)
- [ ] Repeated soft-assert checks use `HelpersPage.verify_all_soft_equals` with uniform `(actual, expected, message)` 3-tuples — no stacked `verify_soft_assert_equals` calls (section 6)
- [ ] Test data is structured/typed; `base_url`, creds, and timeouts come from config, not literals (section 7)
- [ ] Each test body opens with a `# Test Data` block and numbers each action step with `# N. <Action name>` comments; every multi-step FLOW method (page objects and workflow layer) also uses numbered step comments without a `# Test Data` block (section 8)
- [ ] All applicable `python_standards` rules also pass

If any rule is violated, fix it before presenting the code.
