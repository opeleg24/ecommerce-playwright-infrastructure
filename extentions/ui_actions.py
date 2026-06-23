from typing import Optional

import allure
from playwright.sync_api import Locator


class UiActions:
    """Thin, allure-instrumented wrappers around common Playwright locator actions."""

    @staticmethod
    @allure.step("Clicking element")
    def click(locator: Locator) -> None:
        """Click the given element."""
        locator.click()

    @staticmethod
    @allure.step("Double clicking element")
    def double_click(locator: Locator) -> None:
        """Double-click the given element."""
        locator.dblclick()

    @staticmethod
    @allure.step("Clearing text field")
    def clear_text(locator: Locator) -> None:
        """Clear the contents of the given text field."""
        locator.clear()

    @staticmethod
    @allure.step("Updating text field")
    def update_text(locator: Locator, value: str) -> None:
        """Fill the given text field with the provided value."""
        locator.fill(value)

    @staticmethod
    @allure.step("Getting text")
    def get_text(locator: Locator) -> str:
        """Return the inner text of the given element."""
        return locator.inner_text()

    @staticmethod
    @allure.step("Selecting option from dropdown")
    def select_option(locator: Locator, option: str) -> None:
        """Select the given option in the dropdown element."""
        locator.select_option(option)

    @staticmethod
    @allure.step("Getting attribute")
    def get_attribute(locator: Locator, attribute: str) -> Optional[str]:
        """Return the value of the given attribute, or None when absent."""
        return locator.get_attribute(attribute)
