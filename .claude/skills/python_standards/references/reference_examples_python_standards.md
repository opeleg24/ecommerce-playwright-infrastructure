# Python Standards — Examples & Detailed Reference

This file contains detailed bad/good comparisons and code patterns referenced by the main SKILL.md.
Read the relevant section when you need concrete guidance on how to apply a rule.

---

## Table of Contents

1. [DRY Patterns](#1-dry-patterns)
2. [Single Responsibility — Method Splitting](#2-single-responsibility--method-splitting)
3. [Naming — Bad vs Good](#3-naming--bad-vs-good)
4. [Logging — Not Used in This Project](#4-logging--not-used-in-this-project)
5. [Comments — Bad vs Good](#5-comments--bad-vs-good)
6. [Readability Patterns](#6-readability-patterns)
7. [Type Hints — Bad vs Good](#7-type-hints--bad-vs-good)
8. [Dependency Injection — Bad vs Good](#8-dependency-injection--bad-vs-good)
9. [SOLID Principles — Examples](#9-solid-principles--examples)
10. [KISS — Examples](#10-kiss--examples)
11. [YAGNI — Examples](#11-yagni--examples)
12. [Dataclass for Too Many Parameters](#12-dataclass-for-too-many-parameters)
13. [Python Best Practices](#13-python-best-practices)

---

## 1. DRY Patterns

### 1.1 Repetitive blocks → Loop with structured data

When you find the same sequence of actions repeated with slight variations,
group the varying parts into a list of tuples and iterate.

```python
# ❌ Bad — repetitive blocks doing the same thing with different values
days_value = side_effect_data['exposure_days']
record['exposure_days'] = normalize_duration(days_value)

hours_value = side_effect_data['exposure_hours']
record['exposure_hours'] = normalize_duration(hours_value)

minutes_value = side_effect_data['exposure_minutes']
record['exposure_minutes'] = normalize_duration(minutes_value)
```

```python
# ✅ Good — one loop, structured data, zero duplication
exposure_fields = ['exposure_days', 'exposure_hours', 'exposure_minutes']
for field in exposure_fields:
    record[field] = normalize_duration(side_effect_data[field])
```

### 1.2 Use `zip` and `enumerate` instead of index-based loops

```python
# ❌ Bad — manual indexing
for i in range(len(expected_values)):
    assert actual_values[i] == expected_values[i]

# ✅ Good — zip pairs them cleanly
for actual, expected in zip(actual_values, expected_values):
    assert actual == expected

# ✅ Good — enumerate when you need the index
for index, record in enumerate(patient_records):
    assert record['is_active'], f"Inactive record at position {index}: id={record['id']}"
```

### 1.3 Extract repeated logic into helpers

If the same 3+ lines appear in more than one place, extract to a shared method.

```python
# ❌ Bad — same normalize-and-store pattern duplicated across methods
def set_first_name(self, name: str):
    cleaned = name.strip().title()
    self.record['first_name'] = cleaned

def set_last_name(self, name: str):
    cleaned = name.strip().title()
    self.record['last_name'] = cleaned

# ✅ Good — one reusable helper
def set_name_field(self, field_name: str, value: str):
    cleaned = value.strip().title()
    self.record[field_name] = cleaned
```

---

## 2. Single Responsibility — Method Splitting

### 2.1 Methods that do too much

```python
# ❌ Bad — one method doing two unrelated things
def process_user_and_send_email(self, user_id, template):
    user = db.query(f"SELECT * FROM users WHERE id={user_id}")
    user['full_name'] = f"{user['first']} {user['last']}"
    html = template.render(name=user['full_name'])
    smtp = smtplib.SMTP('mail.server.com')
    smtp.send_message(html, to=user['email'])
    smtp.quit()
```

```python
# ✅ Good — each method has a single clear purpose
def process_user(self, user_id: int) -> dict:
    user = self.fetch_user(user_id)
    user['full_name'] = self.build_full_name(user)
    return user

def send_notification(self, user: dict, template: Template):
    html = self.render_template(template, user)
    self.send_email(user['email'], html)
```

### 2.2 Mixed abstraction levels

```python
# ❌ Bad — high-level orchestration mixed with low-level detail
def run_report(self, report_id: int):
    report = self.db.query(f"SELECT * FROM reports WHERE id={report_id}")
    rows = self.db.query(f"SELECT * FROM report_data WHERE report_id={report_id}")
    html = "<html><body>"
    for row in rows:
        html += f"<tr><td>{row['name']}</td><td>{row['value']}</td></tr>"
    html += "</body></html>"
    with open(f"/tmp/report_{report_id}.html", "w") as f:
        f.write(html)
```

```python
# ✅ Good — each method operates at one abstraction level
def run_report(self, report_id: int):
    report = self.fetch_report(report_id)
    report_rows = self.fetch_report_data(report_id)
    html_content = self.render_report_html(report, report_rows)
    self.save_report_file(report_id, html_content)
```

> For decomposing large UI/page-object methods into atomic action methods,
> see the **automation_standards** skill, reference section 1.

---

## 3. Naming — Bad vs Good

### Variables
```python
# ❌ Bad
d = get_data()
temp = process(d)
res = validate(temp)

# ✅ Good
patient_records = fetch_patient_records()
filtered_records = filter_active_patients(patient_records)
validation_result = validate_patient_data(filtered_records)
```

### Booleans
```python
# ❌ Bad
flag = True
status = check_login()
active = 1

# ✅ Good
is_authenticated = True
has_login_succeeded = check_login_status()
is_user_active = True
```

### Functions
```python
# ❌ Bad — vague, describes HOW not WHAT
def do_stuff(x):
def handle(data):
def run_process():

# ✅ Good — verb prefix, describes WHAT
def validate_patient_age(patient: dict) -> bool:
def fetch_active_prescriptions(patient_id: int) -> list:
def build_discharge_summary(visit: Visit) -> str:
```

---

## 4. Logging — Not Used in This Project

This project does **not** use the `logging` module. Do not add a `logger`, call
`logger.info/debug/warning/error(...)`, or sprinkle `print()` statements for visibility.

Run- and step-level visibility is provided entirely by **Allure** reporting via
`@allure.step` decorators (see the `automation_standards` skill). If you need a step to
show up in a report, wrap it in an Allure step — not a log line.

---

## 5. Comments — Bad vs Good

```python
# ❌ Bad — comments describing WHAT the code does (obvious from the code itself)
# Set the name
name = "John"
# Loop through the list
for item in items:
    # Check if active
    if item.is_active:
        # Add to results
        results.append(item)

# ✅ Good — comments explaining WHY
# Reason: legacy endpoint requires a short settle delay before the next call
time.sleep(0.5)

# Workaround: The API returns dates in non-standard format DD/MM/YYYY instead of ISO
parsed_date = datetime.strptime(raw_date, "%d/%m/%Y")
```

---

## 6. Readability Patterns

### 6.1 Break long expressions into named variables

```python
# ❌ Bad — one giant unreadable expression
if user.age >= 18 and user.country in ALLOWED_COUNTRIES and user.subscription != "expired" and not user.is_banned:
    grant_access(user)

# ✅ Good — each condition is named and self-documenting
is_adult = user.age >= 18
is_allowed_country = user.country in ALLOWED_COUNTRIES
has_active_subscription = user.subscription != "expired"
is_not_banned = not user.is_banned

if is_adult and is_allowed_country and has_active_subscription and is_not_banned:
    grant_access(user)
```

### 6.2 Prefer early returns over deep nesting

```python
# ❌ Bad — deeply nested
def process_order(order):
    if order is not None:
        if order.is_valid:
            if order.has_items:
                return calculate_total(order)
            else:
                return 0
        else:
            raise ValueError("Invalid order")
    else:
        raise ValueError("No order")

# ✅ Good — flat with guard clauses
def process_order(order: Order) -> float:
    if order is None:
        raise ValueError("No order provided")
    if not order.is_valid:
        raise ValueError(f"Invalid order: order_id={order.id}")
    if not order.has_items:
        return 0
    return calculate_total(order)
```

---

## 7. Type Hints — Bad vs Good

### 7.1 Function signatures

```python
# ❌ Bad — no type hints, caller has no idea what to pass or expect
def get_patient(id):
    ...

def process_results(data, flag):
    ...

def build_report(records, title, include_header):
    ...

# ✅ Good — every parameter and return type is explicit
def get_patient(patient_id: int) -> dict:
    ...

def process_test_results(test_results: list[dict], should_include_pending: bool) -> list[dict]:
    ...

def build_report(patient_records: list[dict], report_title: str, should_include_header: bool) -> str:
    ...
```

### 7.2 Complex types

```python
# ❌ Bad — what does this return? A list of what?
def fetch_medications(patient_id):
    ...

# ✅ Good — use typing for complex structures
from typing import Optional

def fetch_medications(patient_id: int) -> list[dict[str, str]]:
    ...

def get_patient_name(patient_id: int) -> Optional[str]:
    ...
```

### 7.3 Class attributes and instance variables

```python
# ❌ Bad — no types on attributes
class PatientService:
    def __init__(self, db):
        self.db = db
        self.timeout = 10
        self.base_url = ""

# ✅ Good — typed attributes
class PatientService:
    def __init__(self, db: DatabaseConnection):
        self.db: DatabaseConnection = db
        self.timeout: int = 10
        self.base_url: str = ""
```

---

## 8. Dependency Injection — Bad vs Good

### 8.1 Don't create dependencies internally

```python
# ❌ Bad — creates its own dependencies, impossible to test or swap
class PatientService:
    def __init__(self):
        self.db = DatabaseConnection("prod-server:5432")
        self.cache = RedisCache("redis-host:6379")

    def get_patient(self, patient_id: int) -> dict:
        cached = self.cache.get(f"patient:{patient_id}")
        if cached:
            return cached
        return self.db.query(f"SELECT * FROM patients WHERE id={patient_id}")
```

```python
# ✅ Good — dependencies passed in, easy to test with mocks
class PatientService:
    def __init__(self, db: DatabaseConnection, cache: CacheInterface):
        self.db = db
        self.cache = cache

    def get_patient(self, patient_id: int) -> dict:
        cached = self.cache.get(f"patient:{patient_id}")
        if cached:
            return cached
        return self.db.query(f"SELECT * FROM patients WHERE id={patient_id}")
```

> For injecting a driver / page context into a page object, see the
> **automation_standards** skill, reference section 2.

---

## 9. SOLID Principles — Examples

### 9.1 Single Responsibility (SRP)

```python
# ❌ Bad — one class doing reporting AND email AND file I/O
class PatientReporter:
    def generate_report(self, patient_id: int) -> str:
        patient = self.fetch_patient(patient_id)
        html = self.render_html(patient)
        self.save_to_disk(html)
        self.send_email(patient['email'], html)
        return html

# ✅ Good — each class has one job
class ReportGenerator:
    def generate(self, patient: dict) -> str:
        return self.render_html(patient)

class ReportSaver:
    def save(self, report_id: int, html_content: str):
        file_path = f"/reports/report_{report_id}.html"
        with open(file_path, "w") as f:
            f.write(html_content)
        logger.info(f"Report saved: path={file_path}")

class ReportNotifier:
    def notify(self, recipient_email: str, html_content: str):
        self.send_email(recipient_email, html_content)
        logger.info(f"Report sent: recipient={recipient_email}")
```

### 9.2 Open/Closed (OCP)

```python
# ❌ Bad — adding a new export format means modifying existing code
class ReportExporter:
    def export(self, report: str, format_type: str):
        if format_type == "pdf":
            self.export_pdf(report)
        elif format_type == "csv":
            self.export_csv(report)
        elif format_type == "html":
            self.export_html(report)
        # Every new format = change this method

# ✅ Good — extend by adding new classes, never modifying existing ones
from abc import ABC, abstractmethod

class ReportExporter(ABC):
    @abstractmethod
    def export(self, report: str) -> bytes:
        pass

class PdfExporter(ReportExporter):
    def export(self, report: str) -> bytes:
        logger.info("Exporting report as PDF")
        return self.render_pdf(report)

class CsvExporter(ReportExporter):
    def export(self, report: str) -> bytes:
        logger.info("Exporting report as CSV")
        return self.render_csv(report)

# Adding a new format = add a new class, touch nothing else
class ExcelExporter(ReportExporter):
    def export(self, report: str) -> bytes:
        logger.info("Exporting report as Excel")
        return self.render_excel(report)
```

### 9.3 Liskov Substitution (LSP)

```python
# ❌ Bad — subclass breaks the contract of the base class
class BaseExporter:
    def export(self, report: str) -> bytes:
        return self.render(report)

class NullExporter(BaseExporter):
    def export(self, report: str) -> bytes:
        raise NotImplementedError("This exporter can't export")
        # Breaks LSP — callers expecting export() to work will crash

# ✅ Good — if it can't export, it shouldn't inherit from something that promises it
class Exportable(ABC):
    @abstractmethod
    def export(self, report: str) -> bytes:
        pass

class PdfExporter(Exportable):
    def export(self, report: str) -> bytes:
        logger.info("Exporting report as PDF")
        return self.render_pdf(report)

class ReportPreview:
    """Does not extend Exportable — no false promises."""
    def __init__(self, html_content: str):
        self.html_content = html_content
```

### 9.4 Interface Segregation (ISP)

```python
# ❌ Bad — god base class forces every service to implement everything
class BaseService:
    def fetch(self): ...
    def export(self): ...
    def notify(self): ...
    def archive(self): ...
    def manage_users(self): ...

# ✅ Good — small focused mixins, each service uses only what it needs
class Fetchable:
    def fetch(self, record_id: int) -> dict:
        ...

class Notifiable:
    def notify(self, recipient: str, message: str):
        ...

class PatientLookupService(Fetchable, Notifiable):
    """Only uses fetch and notify — nothing else forced on it."""
    pass
```

### 9.5 Dependency Inversion (DIP)

```python
# ❌ Bad — high-level module depends on low-level concrete class
class TaskRunner:
    def __init__(self):
        self.reporter = JsonReporter()  # Hardcoded dependency

    def run(self, tasks: list):
        for task in tasks:
            result = task.execute()
            self.reporter.report(result)

# ✅ Good — depends on abstraction, any reporter can be swapped in
class ReporterInterface(ABC):
    @abstractmethod
    def report(self, result: TaskResult):
        pass

class JsonReporter(ReporterInterface):
    def report(self, result: TaskResult):
        logger.info(f"Reporting as JSON: task={result.name}, status={result.status}")
        ...

class ConsoleReporter(ReporterInterface):
    def report(self, result: TaskResult):
        print(f"[{result.status}] {result.name}")

class TaskRunner:
    def __init__(self, reporter: ReporterInterface):
        self.reporter = reporter

    def run(self, tasks: list[Task]):
        for task in tasks:
            result = task.execute()
            self.reporter.report(result)
```

---

## 10. KISS — Examples

### 10.1 Don't over-engineer simple logic

```python
# ❌ Bad — factory pattern for something that happens once
class ValidatorFactory:
    _validators = {}

    @classmethod
    def register(cls, name, validator_class):
        cls._validators[name] = validator_class

    @classmethod
    def create(cls, name):
        return cls._validators[name]()

ValidatorFactory.register("age", AgeValidator)
ValidatorFactory.register("email", EmailValidator)
validator = ValidatorFactory.create("age")

# ✅ Good — just call the function directly
def validate_patient_age(age: int) -> bool:
    return 0 < age < 150
```

### 10.2 Prefer standard library over custom solutions

```python
# ❌ Bad — custom implementation of something Python already does
def remove_duplicates(items: list) -> list:
    seen = {}
    result = []
    for item in items:
        key = str(item)
        if key not in seen:
            seen[key] = True
            result.append(item)
    return result

# ✅ Good — use built-in
unique_items = list(set(items))

# Or if order matters:
unique_items = list(dict.fromkeys(items))
```

---

## 11. YAGNI — Examples

### 11.1 Don't add unused parameters

```python
# ❌ Bad — parameters added "for future use"
def create_patient(
    name: str,
    age: int,
    email: str = None,        # "we might need this later"
    insurance_id: str = None,  # "just in case"
    preferred_language: str = None,  # "could be useful"
    emergency_contact: str = None,   # "someone might ask"
):
    return {"name": name, "age": age}  # Only uses 2 of 6 params

# ✅ Good — only what's needed NOW
def create_patient(name: str, age: int) -> dict:
    return {"name": name, "age": age}
```

### 11.2 Don't create base classes prematurely

```python
# ❌ Bad — abstract base with only one implementation
class BaseExporter(ABC):
    @abstractmethod
    def export(self): ...

    @abstractmethod
    def validate(self): ...

    @abstractmethod
    def transform(self): ...

class CsvExporter(BaseExporter):
    # The only implementation — the base class adds zero value
    ...

# ✅ Good — just a concrete class until you actually need a second one
class CsvExporter:
    def export(self, records: list[dict], output_path: str):
        logger.info(f"Exporting {len(records)} records to: path={output_path}")
        ...
```

---

## 12. Dataclass for Too Many Parameters

### 12.1 Replace long parameter lists with a config object

```python
# ❌ Bad — 7 parameters, hard to read and easy to mix up
def configure_client(
    client_type: str,
    is_async: bool,
    timeout: int,
    pool_size: int,
    retries: int,
    proxy_url: str,
    cache_dir: str,
):
    ...

# ✅ Good — group into a dataclass
from dataclasses import dataclass

@dataclass
class ClientConfig:
    client_type: str = "http"
    is_async: bool = False
    timeout_seconds: int = 30
    pool_size: int = 10
    retries: int = 3
    proxy_url: str = ""
    cache_dir: str = "/tmp/cache"

def configure_client(config: ClientConfig):
    logger.info(f"Configuring client: type={config.client_type}, async={config.is_async}")
    ...
```

### 12.2 Structured data as dataclass

```python
# ❌ Bad — passing around loose dicts with no structure
patient_data = {
    "name": "ישראל ישראלי",
    "id": "123456789",
    "age": 45,
    "ward": "פנימית",
}

# ✅ Good — structured, typed, self-documenting
@dataclass
class PatientRecord:
    full_name: str
    patient_id: str
    age: int
    ward_name: str

patient = PatientRecord(
    full_name="ישראל ישראלי",
    patient_id="123456789",
    age=45,
    ward_name="פנימית",
)
```

---

## 13. Python Best Practices

### 13.1 Context managers — always use `with` for resources

```python
# ❌ Bad — manually opening/closing, risk of leak on exception
file = open("test_data.json", "r")
data = json.load(file)
file.close()

# ✅ Good — with statement guarantees cleanup even on exceptions
with open("test_data.json", "r") as test_data_file:
    patient_data = json.load(test_data_file)
```

### 13.2 No hardcoded values

```python
# ❌ Bad — magic values scattered in code
connect("http://192.168.1.100:8080/clinic")
wait_for_ready(10)
authenticate("admin", "Pass123!")

# ✅ Good — constants and config
BASE_URL = os.getenv("CLINIC_BASE_URL", "http://192.168.1.100:8080/clinic")
DEFAULT_TIMEOUT = 10
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

connect(BASE_URL)
wait_for_ready(DEFAULT_TIMEOUT)
authenticate(ADMIN_USERNAME, ADMIN_PASSWORD)
```

### 13.3 Exception handling — specific exceptions, never bare `except`

```python
# ❌ Bad — bare except swallows all errors silently
try:
    record = repository.get(patient_id)
    process(record)
except:
    pass

# ❌ Bad — too broad, hides real bugs
try:
    record = repository.get(patient_id)
    process(record)
except Exception as e:
    print(e)

# ✅ Good — specific exception, logged with context
try:
    record = repository.get(patient_id)
    process(record)
except RecordNotFoundError:
    logger.error(f"Record not found: patient_id={patient_id}")
    raise
except ConnectionError:
    logger.warning(f"Connection lost, retrying: patient_id={patient_id}")
    record = repository.get(patient_id)
    process(record)
```

### 13.4 Imports — organized, no wildcards

```python
# ❌ Bad — wildcard, unorganized, mixed
from datetime import *
from services.patient_service import *
import os
import json
from services import patient_service

# ✅ Good — three groups (stdlib → third-party → local), separated by blank lines
import os
import json
from datetime import datetime

import requests
from dateutil import parser

from services.patient_service import PatientService
from utils.config import load_config
```

### 13.5 Docstrings — required on classes and public methods

```python
# ❌ Bad — no docstring, reader must reverse-engineer the purpose
def build_full_name(patient: dict) -> str:
    return f"{patient['first']} {patient['last']}"

# ✅ Good — one-line summary explains the purpose
def build_full_name(patient: dict) -> str:
    """Combine first and last name fields into a single display name."""
    return f"{patient['first']} {patient['last']}"
```

### 13.6 f-strings — preferred over concatenation and .format()

```python
# ❌ Bad — string concatenation, hard to read
full_name = patient['first'] + " " + patient['last']
logger.info("Processing patient: " + patient_id + " in ward: " + ward_name)

# ❌ Bad — .format() is verbose
full_name = "{} {}".format(patient['first'], patient['last'])
logger.info("Processing patient: {} in ward: {}".format(patient_id, ward_name))

# ✅ Good — f-strings, clean and readable
full_name = f"{patient['first']} {patient['last']}"
logger.info(f"Processing patient: patient_id={patient_id}, ward={ward_name}")
```
