import json
import time

import pytest
from playwright.sync_api import Playwright

from utilities.base import Base

from utilities import base
from utilities.common_ops import get_data




@pytest.fixture(scope='class')
def init_page(playwright: Playwright):
    slow_motion = int(get_data('SLOW_MODE'))
    base.browser = get_web_driver(playwright, slow_motion)
    base.context = base.browser.new_context(no_viewport=True)
    # Start tracing before creating a context
    base.context.tracing.start(screenshots=True, snapshots=True, sources=True)
    base.page = base.context.new_page()
    base.page.set_default_timeout(10000)
    Base.init_pages()
    base.page.goto(get_data('BASE_URL'))

    yield
    # Results in end of test
    #time.sleep(1)

    base.context.tracing.stop(path="trace.zip")
    base.context.close()
    base.browser.close()


@pytest.fixture(scope='class')
def init_api(playwright: Playwright):
    base.request_context = playwright.request.new_context(
        base_url=get_data("BASE_URL_API"))

    yield
    base.request_context.dispose()


@pytest.fixture()
def refresh_page():
    base.page.reload()


@pytest.fixture()
def main_page():
    base.page.goto(get_data('BASE_URL'))

####################################################################################################################
# Function Name: get_chrome_driver
# Function Description: Launches a maximized Chrome browser
# Function Parameters: playwright, slow_motion
# Function Return: Browser - launched chrome browser
####################################################################################################################
def get_chrome_driver(playwright: Playwright, slow_motion: int):
    return playwright.chromium.launch(headless=False, channel="chrome",
                                      slow_mo=slow_motion, args=["--start-maximized"])


####################################################################################################################
# Function Name: get_firefox_driver
# Function Description: Launches a full-screen Firefox browser
# Function Parameters: playwright, slow_motion
# Function Return: Browser - launched firefox browser
####################################################################################################################
def get_firefox_driver(playwright: Playwright, slow_motion: int):
    return playwright.firefox.launch(headless=False, channel="firefox",
                                     slow_mo=slow_motion, args=["--kiosk"])


####################################################################################################################
# Function Name: get_edge_driver
# Function Description: Launches a maximized Edge browser
# Function Parameters: playwright, slow_motion
# Function Return: Browser - launched edge browser
####################################################################################################################
def get_edge_driver(playwright: Playwright, slow_motion: int):
    return playwright.chromium.launch(headless=False, channel="msedge",
                                      slow_mo=slow_motion, args=["--start-maximized"])


####################################################################################################################
# Function Name: get_web_driver
# Function Description: Dispatches to the correct browser launcher based on the BROWSER_TYPE config value
# Function Parameters: playwright, slow_motion
# Function Return: Browser - launched browser
####################################################################################################################
def get_web_driver(playwright: Playwright, slow_motion: int):
    browser_type = get_data('BROWSER_TYPE').lower()
    if browser_type == "chrome":
        return get_chrome_driver(playwright, slow_motion)
    elif browser_type == "firefox":
        return get_firefox_driver(playwright, slow_motion)
    elif browser_type == "edge":
        return get_edge_driver(playwright, slow_motion)
    else:
        raise Exception('Unsupported web driver')


# def pytest_exception_interact(node, call, report):
#     if report.failed:
#         # if globals()['driver'] is not None:  # if it is None-> this is for API tests
#         # image = "./playwright_project/screen-shots/screen_" + str(get_time_stamp()) + ".png"
#         image_path = "./screen-shots/screen.png"
#         image = base.page.screenshot(path=image_path, full_page=True)
#         allure.attach.file(image_path, attachment_type=allure.attachment_type.PNG)
