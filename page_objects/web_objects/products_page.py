import allure
from playwright.sync_api import Locator, Page

from extentions.ui_actions import UiActions
from extentions.verifications import Verifications
from utilities.common_ops import calculate_total_price, split_string
from utilities.helpers_page import HelpersPage


class ProductsPage:
    """Page object for the products listing, header cart indicator, and cart panel."""

    def __init__(self, page: Page):
        self.page = page

        # =================== SELECTORS ===================
        # -- Page header / footer --
        self.page_header = self.page.locator("[class='brand greenLogo']")
        self.page_footer = self.page.get_by_role("contentinfo")

        # -- Product card (dynamic; set by locate_product) --
        self.product = None
        # -- Search --
        self.search_box = self.page.get_by_role("searchbox")
        self.no_results_image = self.page.locator("[class='no-results'] img")

        # -- Cart indicator (header) --
        self.cart_icon = self.page.locator("[class='cart-icon']")

        # -- Cart panel --
        self.product_name_in_cart = self.page.locator("p[class='product-name']")
        self.product_original_price_in_cart = self.page.locator("[class='cart-item'] p[class='product-price']")
        self.product_total_amount_in_cart = self.page.locator("p[class='amount']")
        self.quantity = self.page.locator("[class='cart-item'] [class='quantity']")
        self.proceed_to_checkout = self.page.get_by_role("button", name="PROCEED TO CHECKOUT")

    # =================== SELECTORS HELPERS ===================
    def _get_no_results_locator(self, tag: str) -> Locator:
        """Build a locator for an element inside the no-results empty-state block."""
        return self.page.locator(f"[class='no-results'] {tag}")

    def _get_cart_info_locator(self, row: str) -> Locator:
        """Build a locator for a strong cell inside the cart-info summary table."""
        return self.page.locator(f"[class='cart-info'] {row} strong")

    def _get_product_card_locator(self, div_index: int, child_selector: str) -> Locator:
        """Build a locator for an interactive control inside a product card's action area."""
        return self.product.locator(f"//../div[{div_index}]/{child_selector}")

    # =================== ACTIONS ===================

    # -- Product card --
    def locate_product(self, product_name: str) -> None:
        """Store the product card locator matching the given product name."""
        self.product = self.page.locator(f"//*[contains(text(), '{product_name}')]")

    def decrease_quantity(self) -> None:
        UiActions.click(self._get_product_card_locator(2, "a[1]"))

    def increase_quantity(self) -> None:
        UiActions.click(self._get_product_card_locator(2, "a[2]"))

    def click_add_to_cart(self) -> None:
        UiActions.click(self._get_product_card_locator(3, "button"))

    def get_product_price(self) -> str:
        return UiActions.get_text(self.product.locator("//../p").nth(2))

    # -- Page header / footer --
    def get_page_header_text(self) -> str:
        return UiActions.get_text(self.page_header)

    def get_footer_text(self) -> str:
        return UiActions.get_text(self.page_footer)

    # -- Search --
    @allure.step("Fill search box with text")
    def fill_search_box(self, text: str) -> None:
        UiActions.update_text(self.search_box, text)

    def get_no_results_heading(self) -> str:
        return UiActions.get_text(self._get_no_results_locator('h2'))

    def get_no_results_description(self) -> str:
        return UiActions.get_text(self._get_no_results_locator('p'))
    # -- Cart indicator (header) --
    def get_header_item_count(self) -> str:
        return UiActions.get_text(self._get_cart_info_locator("tr:first-child"))

    def get_header_total_price(self) -> str:
        return UiActions.get_text(self._get_cart_info_locator("tr:last-child"))

    # -- Cart panel --
    def open_cart(self) -> None:
        UiActions.click(self.cart_icon)

    def get_cart_product_name(self, index: int) -> str:
        return UiActions.get_text(self.product_name_in_cart.nth(index))

    def get_cart_product_price(self, index: int) -> str:
        return UiActions.get_text(self.product_original_price_in_cart.nth(index))

    def get_cart_quantity(self, index: int) -> str:
        return UiActions.get_text(self.quantity.nth(index))

    def click_proceed_to_checkout(self) -> None:
        UiActions.click(self.proceed_to_checkout)

    # =================== FLOWS ===================
    # -- Cart actions --
    @allure.step("Add one product to cart")
    def add_product_to_cart(self, product_name: str) -> None:
        """Locate the product and add a single unit to the cart."""
        # 1. Locate product
        self.locate_product(product_name)
        # 2. Decrease quantity to one
        self.decrease_quantity()
        # 3. Add to cart
        self.click_add_to_cart()

    @allure.step("Add two products to cart")
    def add_two_products_to_cart(self, product_name: str) -> None:
        """Locate the product and add two units to the cart."""
        # 1. Locate product
        self.locate_product(product_name)
        # 2. Increase quantity to two
        self.increase_quantity()
        # 3. Add to cart
        self.click_add_to_cart()

    @allure.step("Proceed to checkout page")
    def proceed_to_checkout_flow(self) -> None:
        """Open the cart and proceed to the checkout page."""
        # 1. Open cart
        self.open_cart()
        # 2. Proceed to checkout
        self.click_proceed_to_checkout()

    # -- Verifications --
    @allure.step("Verify page header text")
    def verify_page_header(self, expected: str) -> None:
        """Verify the page header text matches the expected value."""
        Verifications.verify_soft_assert_equals(self.get_page_header_text().strip(), expected, "Page header")

    @allure.step("Verify page footer text")
    def verify_page_footer(self, expected: str) -> None:
        """Verify the page footer contains the expected text."""
        Verifications.verify_contains(expected, self.get_footer_text().strip(), "Page footer")

    @allure.step("Verify initial amount in header display")
    def verify_initial_amount_in_header_display(self, initial_items_amount: str, initial_price: str) -> None:
        """Verify the header shows the expected initial item count and price."""
        HelpersPage.verify_all_soft_equals(
            (self.get_header_item_count(), initial_items_amount, "initial item count"),
            (self.get_header_total_price(), initial_price, "initial total price"),
        )

    @allure.step("Verify cart information in top header display")
    def verify_cart_information_in_header_display(self, expected_items_counter: str, expected_price: str) -> None:
        """Verify the header item count and price after adding a product."""
        HelpersPage.verify_all_soft_equals(
            (self.get_header_item_count(), expected_items_counter, "num of items"),
            (self.get_product_price(), expected_price, "price"),
            (self.get_header_total_price(), expected_price, "price header"),
        )

    @allure.step("Verify no results products")
    def verify_no_results_products_display(self, text: str, no_results_large: str, no_results_small: str) -> None:
        """Search for a term that yields no products and verify the empty-state messages."""
        # 1. Search for a term that yields no results
        self.fill_search_box(text)
        # 2. Verify no-results heading and description
        HelpersPage.verify_all_soft_equals(
            (self.get_no_results_heading(), no_results_large, "no results heading"),
            (self.get_no_results_description(), no_results_small, "no results description"),
        )

    def _verify_cart_product_names(self, product_one: str, product_two: str) -> None:
        """Verify the two product names shown in the cart."""
        HelpersPage.verify_all_soft_equals(
            (self.get_cart_product_name(0), product_one, "product 1 name"),
            (self.get_cart_product_name(1), product_two, "product 2 name"),
        )

    def _verify_cart_prices(self, *expected_prices: int) -> tuple[int, ...]:
        """Verify unit prices in the cart and return the actual values."""
        actual_prices = tuple(
            int(self.get_cart_product_price(i))
            for i in range(len(expected_prices))
        )

        comparisons = []
        for i, (actual, expected) in enumerate(zip(actual_prices, expected_prices)):
            comparisons.append((actual, expected, f"price product {i + 1}"))

        HelpersPage.verify_all_soft_equals(*comparisons)

        return actual_prices

    def _verify_cart_totals(self, actual_prices: tuple[int, ...], *expected_totals: int) -> None:
        """Compute per-line totals from cart quantities and verify them."""
        comparisons = []
        for i, (actual_price, expected_total) in enumerate(zip(actual_prices, expected_totals)):
            actual_quantity = split_string(self.get_cart_quantity(i))
            total = calculate_total_price(actual_quantity, actual_price)
            comparisons.append((total, expected_total, f"total price product {i + 1}"))

        HelpersPage.verify_all_soft_equals(*comparisons)

    @allure.step("Verify cart information in cart panel")
    def verify_cart_information_in_cart(self, data: dict) -> None:
        """Open the cart and verify product names, unit prices, and line totals."""
        # 1. Open cart
        self.open_cart()
        # 2. Verify product names
        self._verify_cart_product_names(data["product_one"], data["product_two"])
        # 3. Verify unit prices
        actual_prices = self._verify_cart_prices(
            data["product_one_price"], data["product_two_price"])
        # 4. Verify line totals
        self._verify_cart_totals(actual_prices,
                                 data["expected_total_price_prod_one"],
                                 data["expected_total_price_prod_two"])
