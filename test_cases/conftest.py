import pytest
from playwright.sync_api import Browser, Playwright

from utilities import base
from utilities.base import Base
from utilities.common_ops import get_data

DEFAULT_TIMEOUT_MS = 10000


@pytest.fixture(scope='class')
def init_page(playwright: Playwright):
    """Launch a browser, open a traced page, build page objects, and navigate home."""
    slow_motion = int(get_data('SLOW_MODE'))
    base.browser = get_web_driver(playwright, slow_motion)
    base.context = base.browser.new_context(no_viewport=True)
    # Start tracing before creating a context
    base.context.tracing.start(screenshots=True, snapshots=True, sources=True)
    base.page = base.context.new_page()
    base.page.set_default_timeout(DEFAULT_TIMEOUT_MS)
    Base.init_pages()
    base.page.goto(get_data('BASE_URL'))

    yield

    base.context.tracing.stop(path="trace.zip")
    base.context.close()
    base.browser.close()


@pytest.fixture(scope='class')
def init_api(playwright: Playwright):
    """Create an API request context bound to the API base URL for the test class."""
    base.request_context = playwright.request.new_context(
        base_url=get_data("BASE_URL_API"))

    yield

    base.request_context.dispose()


@pytest.fixture()
def refresh_page():
    """Reload the current page before a test."""
    base.page.reload()


@pytest.fixture()
def main_page():
    """Navigate back to the application home page before a test."""
    base.page.goto(get_data('BASE_URL'))


def get_chrome_driver(playwright: Playwright, slow_motion: int) -> Browser:
    """Launch a maximized Chrome browser."""
    return playwright.chromium.launch(headless=False, channel="chrome",
                                      slow_mo=slow_motion, args=["--start-maximized"])


def get_firefox_driver(playwright: Playwright, slow_motion: int) -> Browser:
    """Launch a full-screen Firefox browser."""
    return playwright.firefox.launch(headless=False, channel="firefox",
                                     slow_mo=slow_motion, args=["--kiosk"])


def get_edge_driver(playwright: Playwright, slow_motion: int) -> Browser:
    """Launch a maximized Edge browser."""
    return playwright.chromium.launch(headless=False, channel="msedge",
                                      slow_mo=slow_motion, args=["--start-maximized"])


def get_web_driver(playwright: Playwright, slow_motion: int) -> Browser:
    """Dispatch to the correct browser launcher based on the BROWSER_TYPE config value."""
    browser_type = get_data('BROWSER_TYPE').lower()
    if browser_type == "chrome":
        return get_chrome_driver(playwright, slow_motion)
    elif browser_type == "firefox":
        return get_firefox_driver(playwright, slow_motion)
    elif browser_type == "edge":
        return get_edge_driver(playwright, slow_motion)
    else:
        raise ValueError(f"Unsupported web driver: browser_type={browser_type}")
