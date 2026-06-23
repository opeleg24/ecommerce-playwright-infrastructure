"""Shared Playwright state holder for the test suite.

This module deliberately keeps a single set of module-level globals — the active
Playwright ``page``/``context``/``browser``, the API ``request_context``, and the
page-object instances. The pytest fixtures in ``conftest.py`` populate these once
per test class, and the workflow/test layers read them from here.

Reason: the suite is built around one shared browser session per class, so a single
central holder keeps every layer pointing at the same live ``page`` without threading
it through every call.
"""

from page_objects.web_objects.check_out_page import CheckOutPage
from page_objects.web_objects.country_page import CountryPage
from page_objects.web_objects.products_page import ProductsPage

# Playwright Objects
page = None
browser = None
context = None
request_context = None

# Page Objects
products_page = None
check_out_page = None
country_page = None


class Base:
    """Factory for the shared page-object instances bound to the active page."""

    @staticmethod
    def init_pages() -> None:
        """Build each page object against the current global page and store it."""
        globals()['products_page'] = ProductsPage(page)
        globals()['check_out_page'] = CheckOutPage(page)
        globals()['country_page'] = CountryPage(page)
