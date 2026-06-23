from typing import Any

import allure

from extentions.verifications import Verifications


class HelpersPage:
    """Shared, page-agnostic web verification helpers."""

    @staticmethod
    @allure.step("Verifying multiple values")
    def verify_all_soft_equals(*checks: tuple[Any, Any, str]) -> None:
        """Soft-assert each (actual, expected, message) check in turn."""
        for actual, expected, message in checks:
            Verifications.verify_soft_assert_equals(actual, expected, message)
