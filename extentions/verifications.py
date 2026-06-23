from typing import Any, Optional

import allure
from smart_assertions import soft_assert


class Verifications:
    """Allure-instrumented assertion helpers for value comparisons."""

    @staticmethod
    @allure.step("Verifying equals")
    def verify_equals(actual: Any, expected: Any) -> None:
        """Hard-assert that actual equals expected."""
        assert actual == expected, f"Expected: {expected}, but got: {actual}"

    @staticmethod
    @allure.step("Verifying equals using smart assertions")
    def verify_soft_assert_equals(actual: Any, expected: Any, message: Optional[str] = None) -> None:
        """Soft-assert that actual equals expected, collecting failures for later."""
        soft_assert(actual == expected, f"Expected: {expected}, but got: {actual} when verifying {message}")

    @staticmethod
    @allure.step("Verifying contains")
    def verify_contains(actual: Any, expected: Any, message: Optional[str] = None) -> None:
        """Hard-assert that expected is contained within actual."""
        assert expected in actual, f"Expected: {expected}, but got: {actual} when verifying {message}"
