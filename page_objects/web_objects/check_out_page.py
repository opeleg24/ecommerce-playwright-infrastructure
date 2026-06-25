import allure
from playwright.sync_api import Page

from extentions.ui_actions import UiActions
from extentions.verifications import Verifications
from utilities.helpers_page import HelpersPage


class CheckOutPage:
    """Page object for the checkout page table and order-summary panel."""

    def __init__(self, page: Page):
        self.page = page

        # =================== SELECTORS ===================

        # -- Middle page information --
        self.middle_page_no_of_items = self.page.locator("[style*='text-align']")
        self.middle_page_total_amount = self.page.locator("[class='totAmt']")
        self.middle_page_discount_perc = self.page.locator("[class='discountPerc']")
        self.total_after_discount = self.page.locator("[class='discountAmt']")

        # -- Buttons --
        self.place_order_button = self.page.locator("text=Place Order")
        self.apply_promo_button = self.page.locator("text=Apply")
        self.code_message = self.page.locator("[class='promoInfo']")
        self.code_input = self.page.locator("[class='promoCode']")

        # -- Table --
        self.table_product_name = self.page.locator("#productCartTables p[class='product-name']")
        self.table_product_quantity = self.page.locator("#productCartTables p[class='quantity']")
        self.table_product_price = self.page.locator("#productCartTables p[class='amount']")

    # =================== ACTIONS ===================
    # -- Table getters --
    def get_table_product_name(self) -> str:
        return UiActions.get_text(self.table_product_name)

    def get_table_product_price(self) -> str:
        return UiActions.get_text(self.table_product_price.first)

    def get_table_product_quantity(self) -> str:
        return UiActions.get_text(self.table_product_quantity)

    def get_table_total_price(self) -> str:
        return UiActions.get_text(self.table_product_price.last)

    # -- Middle page getters --
    def get_total_amount(self) -> str:
        return UiActions.get_text(self.middle_page_total_amount)

    def get_discount_percentage(self) -> str:
        return UiActions.get_text(self.middle_page_discount_perc)

    def get_total_after_discount(self) -> str:
        return UiActions.get_text(self.total_after_discount)

    def get_promo_code_message(self) -> str:
        return UiActions.get_text(self.code_message)

    # -- Promo code --
    def enter_promo_code(self, code: str) -> None:
        UiActions.update_text(self.code_input, code)

    def click_apply_promo(self) -> None:
        UiActions.click(self.apply_promo_button)

    # -- Navigation --
    def click_place_order(self) -> None:
        UiActions.click(self.place_order_button)

    # =================== FLOWS ===================
    @allure.step("Enter promo code")
    def apply_promo_code(self, code: str) -> None:
        """Enter a promo code and apply it."""
        # 1. Enter promo code
        self.enter_promo_code(code)
        # 2. Click apply
        self.click_apply_promo()

    @allure.step("Verify cart information in table inside checkout page")
    def verify_cart_information_in_table(self, product_name: str, price: str,
                                         counter: str, total_price: str) -> None:
        """Verify the checkout table row: name, price, quantity, and total."""
        HelpersPage.verify_all_soft_equals(
            (self.get_table_product_name(), product_name, "product name"),
            (self.get_table_product_price(), price, "product price"),
            (self.get_table_product_quantity(), counter, "product quantity"),
            (self.get_table_total_price(), total_price, "total price"),
        )

    @allure.step("Verify cart information in table inside checkout page - Middle page")
    def verify_cart_information_in_table_middle_page(self, total_price: str, discount_perc: str) -> None:
        """Verify the checkout summary panel: total amount, discount, and net total."""
        HelpersPage.verify_all_soft_equals(
            (self.get_total_amount(), total_price, "total amount"),
            (self.get_discount_percentage(), discount_perc, "discount percentage"),
            (self.get_total_after_discount(), total_price, "total after discount"),
        )

    @allure.step("Verify purchase flow with correct promo code")
    def verify_purchase_flow_with_correct_promo_code(self, promo_code_message: str, total_amount: str,
                                                     discount: str, total_after_discount: str) -> None:
        """Verify the promo-code message, totals, and discount on the checkout page."""
        HelpersPage.verify_all_soft_equals(
            (self.get_promo_code_message(), promo_code_message, "promo code message"),
            (self.get_total_amount(), total_amount, "total amount"),
            (self.get_discount_percentage(), discount, "discount percentage"),
            (self.get_total_after_discount(), total_after_discount, "total after discount"),
        )
