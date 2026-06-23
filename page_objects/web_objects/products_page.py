import allure
from playwright.sync_api import Page

from extentions.ui_actions import UiActions
from extentions.verifications import Verifications
from utilities.common_ops import calculate_total_price, split_string


class ProductsPage:
    """Page object for the products listing, header cart indicator, and cart panel."""

    def __init__(self, page: Page):
        self.page = page

        # =================== SELECTORS ===================
        # -- Page header / footer --
        self.page_header = self.page.locator("[class='brand greenLogo']")
        self.page_footer = self.page.locator("footer")

        # -- Product card (dynamic; set by locate_product) --
        self.product = None

        # -- Search --
        self.search_box = self.page.locator("input[type='search']")
        self.no_results_large_message = self.page.locator("[class='no-results'] h2")
        self.no_results_small_message = self.page.locator("[class='no-results'] p")
        self.no_results_image = self.page.locator("[class='no-results'] img")

        # -- Cart indicator (header) --
        self.items_indicator_header = self.page.locator("[class='cart-info'] tr:first-child strong")
        self.price_indicator_header = self.page.locator("[class='cart-info'] tr:last-child strong")
        self.cart_icon = self.page.locator("[class='cart-icon']")

        # -- Cart panel --
        self.product_name_in_cart = self.page.locator("p[class='product-name']")
        self.product_original_price_in_cart = self.page.locator("[class='cart-item'] p[class='product-price']")
        self.product_total_amount_in_cart = self.page.locator("p[class='amount']")
        self.quantity = self.page.locator("[class='cart-item'] [class='quantity']")
        self.proceed_to_checkout = self.page.locator("text=PROCEED TO CHECKOUT")

    # =================== ATOMIC ACTIONS ===================
    # -- Product card --
    def locate_product(self, product_name: str) -> None:
        """Store the product card locator matching the given product name."""
        self.product = self.page.locator(f"//*[contains(text(), '{product_name}')]")

    def decrease_quantity(self) -> None:
        UiActions.click(self.product.locator("//../div[2]/a[1]"))

    def increase_quantity(self) -> None:
        UiActions.click(self.product.locator("//../div[2]/a[2]"))

    def click_add_to_cart(self) -> None:
        UiActions.click(self.product.locator("//../div[3]/button"))

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
        return UiActions.get_text(self.no_results_large_message)

    def get_no_results_description(self) -> str:
        return UiActions.get_text(self.no_results_small_message)

    # -- Cart indicator (header) --
    def get_header_item_count(self) -> str:
        return UiActions.get_text(self.items_indicator_header)

    def get_header_total_price(self) -> str:
        return UiActions.get_text(self.price_indicator_header)

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
        self.locate_product(product_name)
        self.decrease_quantity()
        self.click_add_to_cart()

    @allure.step("Add two products to cart")
    def add_two_products_to_cart(self, product_name: str) -> None:
        """Locate the product and add two units to the cart."""
        self.locate_product(product_name)
        self.increase_quantity()
        self.click_add_to_cart()

    @allure.step("Proceed to checkout page")
    def proceed_to_checkout_flow(self) -> None:
        """Open the cart and proceed to the checkout page."""
        self.open_cart()
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
        Verifications.verify_soft_assert_equals(self.get_header_item_count(), initial_items_amount)
        Verifications.verify_soft_assert_equals(self.get_header_total_price(), initial_price)

    @allure.step("Verify cart information in top header display")
    def verify_cart_information_in_header_display(self, expected_items_counter: str, expected_price: str) -> None:
        """Verify the header item count and price after adding a product."""
        Verifications.verify_soft_assert_equals(self.get_header_item_count(), expected_items_counter, "num of items")
        Verifications.verify_soft_assert_equals(self.get_product_price(), expected_price, "price")
        Verifications.verify_soft_assert_equals(self.get_header_total_price(), expected_price, "price header")

    @allure.step("Verify no results products")
    def verify_no_results_products_display(self, text: str, no_results_large: str, no_results_small: str) -> None:
        """Search for a term that yields no products and verify the empty-state messages."""
        self.fill_search_box(text)
        Verifications.verify_soft_assert_equals(no_results_large, self.get_no_results_heading())
        Verifications.verify_soft_assert_equals(no_results_small, self.get_no_results_description())

    def _verify_cart_product_names(self, product_one: str, product_two: str) -> None:
        """Verify the two product names shown in the cart."""
        Verifications.verify_soft_assert_equals(self.get_cart_product_name(0), product_one, "product 1")
        Verifications.verify_soft_assert_equals(self.get_cart_product_name(1), product_two, "product 2")

    def _verify_cart_prices(self, price_product_one: int, price_product_two: int) -> tuple[int, int]:
        """Verify the two unit prices in the cart and return the actual values."""
        actual_price_one = int(self.get_cart_product_price(0))
        actual_price_two = int(self.get_cart_product_price(1))
        Verifications.verify_soft_assert_equals(actual_price_one, price_product_one, "price product 1")
        Verifications.verify_soft_assert_equals(actual_price_two, price_product_two, "price product 2")
        return actual_price_one, actual_price_two

    def _verify_cart_totals(self, actual_price_one: int, actual_price_two: int,
                            expected_total_for_one_product: int, expected_total_for_two_products: int) -> None:
        """Compute per-line totals from cart quantities and verify them."""
        actual_quantity_one = split_string(self.get_cart_quantity(0))
        actual_quantity_two = split_string(self.get_cart_quantity(1))
        total_for_one = calculate_total_price(actual_quantity_one, actual_price_one)
        total_for_two = calculate_total_price(actual_quantity_two, actual_price_two)
        Verifications.verify_soft_assert_equals(total_for_one, expected_total_for_one_product, "total price")
        Verifications.verify_soft_assert_equals(total_for_two, expected_total_for_two_products, "total price")

    @allure.step("Verify cart information in cart panel")
    def verify_cart_information_in_cart(self, product_one: str, product_two: str,
                                        price_product_one: int, price_product_two: int,
                                        expected_total_price_for_one_product: int,
                                        expected_total_price_for_two_products: int) -> None:
        """Open the cart and verify product names, unit prices, and line totals."""
        self.open_cart()
        self._verify_cart_product_names(product_one, product_two)
        actual_price_one, actual_price_two = self._verify_cart_prices(price_product_one, price_product_two)
        self._verify_cart_totals(actual_price_one, actual_price_two,
                                 expected_total_price_for_one_product, expected_total_price_for_two_products)
