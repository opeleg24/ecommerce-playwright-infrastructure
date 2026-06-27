---
name: python_standards
description: >
  Enforce clean code standards, design patterns, and best practices for Python.
  Use this skill EVERY TIME you write, modify, create, or refactor any Python code.
  Trigger on ANY code change, new file creation, bug fix, or feature addition.
  Covers naming, method design, comments, type hints, Python idioms,
  design patterns (DRY/KISS/YAGNI), and SOLID principles.
  This skill is the language-level coding constitution of this project.
  For UI/test-automation patterns, see the separate automation_standards skill.
---

# Python Standards — Clean Code

Every code change must pass through these standards before being considered complete.

For detailed bad/good comparisons and code examples, read `references/reference_examples_python_standards.md`.

---

## 1. Naming Conventions

- **Variables/parameters**: descriptive `snake_case` — e.g. `expected_patient_name`, `record_count`
- **Booleans**: must read as a question — `is_loaded`, `has_error`, `should_retry`
- **No generic names**: never use `data`, `info`, `temp`, `val`, `item`, `obj`, `result` alone — always add context
- **Functions/methods**: verb prefix describing WHAT, not HOW:
  - `get_`, `find_`, `fetch_` — retrieval
  - `verify_`, `assert_`, `validate_` — verification
  - `is_`, `has_`, `should_` — boolean returns
  - `create_`, `build_`, `setup_` — construction
  - `parse_`, `extract_`, `transform_` — data manipulation
  - `update_`, `set_`, `apply_` — mutations
  - `delete_`, `remove_`, `clear_` — cleanup
- **Classes**: `PascalCase` — `ReportGenerator`, `PatientService`
- **Constants**: `UPPER_SNAKE_CASE` — `DEFAULT_TIMEOUT`, `BASE_URL`

*(See `references/reference_examples_python_standards.md` section 3 for bad/good naming comparisons.)*

## 2. Method Rules

- Every method does **ONE thing**. If the name contains "and" — split it.
- Maximum method length: **~20 lines** (excluding docstring). If longer, decompose.
- Maximum parameters: **3–4**. If more, use a config object or dataclass.
- One level of abstraction per method — don't mix orchestration with low-level details.
- **Extract Method** (Martin Fowler's *Refactoring*): decompose large methods into small, single-responsibility helpers. Each helper does one thing, is named descriptively enough to replace a comment, and is reusable. High-level methods compose these helpers in sequence and read like a step-by-step script at one abstraction level.

*(See `references/reference_examples_python_standards.md` section 2 for method splitting examples.)*

## 3. Comments & Docstrings

**Docstrings** — every method gets a docstring describing its purpose:
- Format: `"""Fetch and validate the patient record, returning a normalized dict."""`
- Prefer one line, but two or three lines are fine when the method needs more explanation

**Inline step comments** — between logical blocks inside the method body:
- Describe each logical step: `# extract patient data`, `# normalize the fields`, `# persist the record`
- These act as section headers within the method, making the flow scannable

**Comments** — sparingly, only for WHY, never WHAT:
- Format: `# Reason: <why>` or `# Workaround: <what and why>`

**No logging** — do not add a `logging` logger or `logger.*` calls. This project does not
use the `logging` module; run/step visibility is provided by **Allure** reporting
(`@allure.step`, see the automation_standards skill). Don't introduce loggers.

*(See `references/reference_examples_python_standards.md` section 5 for comment examples.)*

## 4. Type Hints & Testability

- Type hints on **all** function signatures — no exceptions.
- Docstrings on **all** functions — no exceptions. Keep them concise.
- Use dependency injection — pass dependencies in, don't create them internally.
- Methods should be deterministic: same input → same output.
- Avoid global state. Pass state explicitly through parameters.

*(See `references/reference_examples_python_standards.md` section 7 for type hint examples, section 8 for dependency injection patterns.)*

## 5. Python Best Practices

- **Context managers**: Always use `with` for resources (files, connections, clients) — never manually open/close.
- **No hardcoded values**: Use constants (`UPPER_SNAKE_CASE`), config files, or environment variables for URLs, timeouts, credentials, and paths.
- **Exception handling**: Catch specific exceptions, never bare `except:` or `except Exception:`. Always log the error with context.
- **Imports**: No wildcard imports (`from module import *`). Organize in three groups: stdlib → third-party → local, separated by blank lines.
- **Docstrings**: Required on classes, public methods, and any function with non-obvious logic. Use triple quotes with a one-line summary.
- **f-strings**: Preferred over string concatenation (`+`) or `.format()`. Never use `%` formatting.

*(See `references/reference_examples_python_standards.md` section 13 for Python best practices examples.)*

## 6. Design Patterns

- **DRY**: Eliminate duplication. Repetitive blocks → loop with structured data. Same 3+ lines in multiple places → extract to helper. Use `zip`/`enumerate` over index-based loops.
- **KISS**: Simplest solution that works. No design pattern unless it solves a real problem. If a junior dev can't understand it in 2 minutes — simplify.
- **YAGNI**: No features, abstractions, or parameters "just in case." No base classes without 2+ implementations NOW.
- **Divide and Conquer**: Large functions → focused helpers. Complex classes → smaller collaborators.

*(See `references/reference_examples_python_standards.md` section 1 for DRY patterns, section 6 for readability, sections 10–11 for KISS/YAGNI, section 12 for dataclass patterns.)*

## 7. SOLID Principles

- **SRP**: Each class has one reason to change.
- **OCP**: Open for extension, closed for modification.
- **LSP**: Subclasses must be substitutable for base classes without breaking behavior.
- **ISP**: Don't force classes to depend on methods they don't use. Prefer small mixins over god classes.
- **DIP**: Depend on abstractions. Inject dependencies, don't hardcode them.

*(See `references/reference_examples_python_standards.md` section 9 for SOLID examples with bad/good comparisons.)*

---

## 8. Code Review Checklist

Before completing ANY code change, verify:

- [ ] All names are meaningful and follow naming conventions (section 1)
- [ ] Every method does ONE thing and is ≤ ~20 lines (section 2)
- [ ] Comments explain WHY, not WHAT. No logging — Allure provides visibility (section 3)
- [ ] Type hints present on all function signatures (section 4)
- [ ] Context managers used for resources, specific exceptions caught, f-strings used (section 5)
- [ ] No duplicate code — DRY violations extracted to shared methods (section 6)
- [ ] No unnecessary abstractions — YAGNI respected (section 6)
- [ ] Dependencies are injected, not hardcoded (section 4)
- [ ] Code is consistent with existing project patterns and style
- [ ] The simplest working solution was chosen — KISS (section 6)

If any rule is violated, fix it before presenting the code.
