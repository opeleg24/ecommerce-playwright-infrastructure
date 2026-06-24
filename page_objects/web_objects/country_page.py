import allure
from playwright.sync_api import Page

from extentions.ui_actions import UiActions
from extentions.verifications import Verifications


class CountryPage:
    """Page object for the final country-selection and order-confirmation page."""

    def __init__(self, page: Page):
        self.page = page

        # =================== SELECTORS ===================
        self.select_country = self.page.locator("select")
        self.terms_conditions_checkbox = self.page.locator("[class='chkAgree']")
        self.proceed_button = self.page.locator("text=Proceed")
        self.success_message = self.page.locator("[class='products'] span").first

    # =================== ACTIONS ===================
    def select_shipping_country(self, country: str) -> None:
        UiActions.select_option(self.select_country, country)

    def accept_terms_and_conditions(self) -> None:
        UiActions.click(self.terms_conditions_checkbox)

    def click_proceed(self) -> None:
        UiActions.click(self.proceed_button)

    def get_success_message(self) -> str:
        return UiActions.get_text(self.success_message)

    # =================== FLOWS ===================
    @allure.step("Filling country page information")
    def filling_country_page_information_flow(self, country: str) -> None:
        """Select the country, accept terms, and proceed from the country page."""
        # 1. Select shipping country
        self.select_shipping_country(country)
        # 2. Accept terms and conditions
        self.accept_terms_and_conditions()
        # 3. Click proceed
        self.click_proceed()

    @allure.step("Verify order successful message")
    def verify_successful_order_message(self, expected_message: str) -> None:
        """Verify the success message contains the expected order confirmation text."""
        Verifications.verify_contains(self.get_success_message(), expected_message, "success order message")
