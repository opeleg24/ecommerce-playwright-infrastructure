import allure
from smart_assertions import verify_expectations

from extentions.ui_actions import UiActions
from extentions.verifications import Verifications
from utilities import base
from utilities.common_ops import calculate_total_price, split_string


class WebFlows:

    @staticmethod
    @allure.step("Verify page header text")
    def verify_page_header(expected_header: str) -> None:
        """Verify the page header text matches the expected value."""
        actual_header = base.products_page.get_page_header_text()
        Verifications.verify_soft_assert_equals(actual_header.strip(), expected_header, "Page header")

    @staticmethod
    @allure.step("Verify initial amount in header display")
    def verify_initial_amount_in_header_display(initial_items_amount: str, initial_price: str) -> None:
        """Verify the header shows the expected initial item count and price."""
        actual_initial_product_amount = UiActions.get_text(base.products_page.items_indicator_header)
        actual_initial_price = UiActions.get_text(base.products_page.price_indicator_header)
        Verifications.verify_soft_assert_equals(actual_initial_product_amount, initial_items_amount)
        Verifications.verify_soft_assert_equals(actual_initial_price, initial_price)

    @staticmethod
    @allure.step("Add one product to cart")
    def add_product_to_cart(product_name: str) -> None:
        """Locate the product and add a single unit to the cart."""
        base.products_page.locate_product(product_name)
        UiActions.click(base.products_page.increment_action_decrease())
        UiActions.click(base.products_page.add_to_cart_button())

    @staticmethod
    @allure.step("Verify cart information in top header display")
    def verify_cart_information_in_header_display(expected_items_counter: str, expected_price: str) -> None:
        """Verify the header item count and price after adding a product."""
        actual_num_of_items = UiActions.get_text(base.products_page.items_indicator_header)
        Verifications.verify_soft_assert_equals(actual_num_of_items, expected_items_counter, "num of items")
        actual_price_product = UiActions.get_text(base.products_page.get_price_product())
        Verifications.verify_soft_assert_equals(actual_price_product, expected_price, "price")
        actual_price_header = UiActions.get_text(base.products_page.price_indicator_header)
        Verifications.verify_soft_assert_equals(actual_price_header, expected_price, "price header")
        verify_expectations()

    @staticmethod
    @allure.step("Add two product to cart")
    def add_two_products_to_cart(product_name: str) -> None:
        """Locate the product and add two units to the cart."""
        base.products_page.locate_product(product_name)
        UiActions.click(base.products_page.increment_action_increase())
        UiActions.click(base.products_page.add_to_cart_button())

    @staticmethod
    def _verify_cart_product_names(product_one: str, product_two: str) -> None:
        """Verify the two product names shown in the cart."""
        actual_product_one = UiActions.get_text(base.products_page.product_name_in_cart.first)
        actual_product_two = UiActions.get_text(base.products_page.product_name_in_cart.last)
        Verifications.verify_soft_assert_equals(actual_product_one, product_one, "product 1")
        Verifications.verify_soft_assert_equals(actual_product_two, product_two, "product 2")

    @staticmethod
    def _verify_cart_prices(price_product_one: int, price_product_two: int) -> tuple[int, int]:
        """Verify the two unit prices in the cart and return the actual values."""
        actual_price_product_one = int(UiActions.get_text(base.products_page.product_original_price_in_cart.first))
        actual_price_product_two = int(UiActions.get_text(base.products_page.product_original_price_in_cart.last))
        Verifications.verify_soft_assert_equals(actual_price_product_one, price_product_one, "price product 1")
        Verifications.verify_soft_assert_equals(actual_price_product_two, price_product_two, "price product 2")
        return actual_price_product_one, actual_price_product_two

    @staticmethod
    def _verify_cart_totals(actual_price_one: int, actual_price_two: int,
                            expected_total_for_one_product: int, expected_total_for_two_products: int) -> None:
        """Compute per-line totals from cart quantities and verify them."""
        actual_quantity_one = split_string(UiActions.get_text(base.products_page.quantity.first))
        actual_quantity_two = split_string(UiActions.get_text(base.products_page.quantity.last))
        total_for_one_product = calculate_total_price(actual_quantity_one, actual_price_one)
        total_for_two_products = calculate_total_price(actual_quantity_two, actual_price_two)
        Verifications.verify_soft_assert_equals(total_for_one_product, expected_total_for_one_product, "total price")
        Verifications.verify_soft_assert_equals(total_for_two_products, expected_total_for_two_products, "total price")

    @staticmethod
    @allure.step("Verify cart information in top header display")
    def verify_cart_information_in_cart(product_one: str, product_two: str, price_product_one: int,
                                        price_product_two: int,
                                        expected_total_price_for_one_product: int,
                                        expected_total_price_for_two_products: int) -> None:
        """Open the cart and verify product names, unit prices, and line totals."""
        UiActions.click(base.products_page.cart_icon)
        WebFlows._verify_cart_product_names(product_one, product_two)
        actual_price_one, actual_price_two = WebFlows._verify_cart_prices(price_product_one, price_product_two)
        WebFlows._verify_cart_totals(actual_price_one, actual_price_two,
                                     expected_total_price_for_one_product,
                                     expected_total_price_for_two_products)
        verify_expectations()

    @staticmethod
    @allure.step("Verify cart information in table inside checkout page")
    def verify_cart_information_in_table(product_name: str, price: str, counter: str, total_price: str) -> None:
        """Verify the checkout table row: name, price, quantity, and total."""
        actual_name = UiActions.get_text(base.check_out_page.table_product_name)
        Verifications.verify_soft_assert_equals(actual_name, product_name, "product name")
        actual_price = UiActions.get_text(base.check_out_page.table_product_price.first)
        Verifications.verify_soft_assert_equals(actual_price, price, "product price")
        actual_quantity = UiActions.get_text(base.check_out_page.table_product_quantity)
        Verifications.verify_soft_assert_equals(actual_quantity, counter)
        actual_total_price = UiActions.get_text(base.check_out_page.table_total_price.last)
        Verifications.verify_soft_assert_equals(actual_total_price, total_price, "total price")
        verify_expectations()

    @staticmethod
    @allure.step("Verify cart information in table inside checkout page - Middle page")
    def verify_cart_information_in_table_middle_page(total_price: str, discount_perc: str) -> None:
        """Verify the checkout summary panel: total amount, discount, and net total."""
        actual_total_amount = UiActions.get_text(base.check_out_page.middle_page_total_amount)
        Verifications.verify_soft_assert_equals(actual_total_amount, total_price, "total amount")
        actual_discount_perc = UiActions.get_text(base.check_out_page.middle_page_discount_perc)
        Verifications.verify_soft_assert_equals(actual_discount_perc, discount_perc, "discount percentage")
        total_after_discount = UiActions.get_text(base.check_out_page.total_after_discount)
        Verifications.verify_soft_assert_equals(total_after_discount, total_price, "total after discount")
        verify_expectations()

    @staticmethod
    @allure.step("Enter promo code")
    def apply_promo_code(promo_code: str) -> None:
        """Enter a promo code and apply it."""
        UiActions.update_text(base.check_out_page.code_input, promo_code)
        UiActions.click(base.check_out_page.apply_promo_code)

    @staticmethod
    @allure.step("Verify purchase flow with correct promo code")
    def verify_purchase_flow_with_correct_promo_code(promo_code_message: str, total_amount: str,
                                                     discount: str, total_after_discount: str) -> None:
        """Verify the promo-code message, totals, and discount on the checkout page."""
        actual_message = UiActions.get_text(base.check_out_page.code_message)
        Verifications.verify_soft_assert_equals(actual_message, promo_code_message, "promo code message")
        actual_total_amount = UiActions.get_text(base.check_out_page.middle_page_total_amount)
        Verifications.verify_soft_assert_equals(actual_total_amount, total_amount, "total amount")
        actual_discount = UiActions.get_text(base.check_out_page.middle_page_discount_perc)
        Verifications.verify_soft_assert_equals(actual_discount, discount, "discount percentage")
        actual_total_after_discount = UiActions.get_text(base.check_out_page.total_after_discount)
        Verifications.verify_soft_assert_equals(actual_total_after_discount, total_after_discount, "total after discount")
        verify_expectations()

    @staticmethod
    @allure.step("Filling country page information")
    def filling_country_page_information_flow(country: str) -> None:
        """Select the country, accept terms, and proceed from the country page."""
        UiActions.select_option(base.country_page.select_country, country)
        UiActions.click(base.country_page.terms_conditions_checkbox)
        UiActions.click(base.country_page.proceed_button)

    @staticmethod
    @allure.step("Verify order successful message")
    def verify_successful_order_message(expected_message: str) -> None:
        """Verify the success message contains the expected order confirmation text."""
        actual_message = UiActions.get_text(base.country_page.success_message)
        Verifications.verify_contains(actual_message, expected_message, "success order message")

    @staticmethod
    @allure.step("Click the cart button & Proceed to checkout")
    def proceed_to_checkout_page_flow() -> None:
        """Open the cart and proceed to the checkout page."""
        base.products_page.proceed_to_checkout_flow()

    @staticmethod
    @allure.step("Click the cart button")
    def click_cart_button() -> None:
        """Open the cart panel from the header."""
        UiActions.click(base.products_page.cart_icon)

    @staticmethod
    @allure.step("Proceed to final country page")
    def proceed_to_country_page_flow() -> None:
        """Proceed through checkout to the final country page."""
        base.products_page.proceed_to_checkout_flow()
        UiActions.click(base.check_out_page.place_order_button)

    @staticmethod
    @allure.step("Verify no results products")
    def verify_no_results_products_display(text: str, no_results_large: str, no_results_small: str) -> None:
        """Search for a term that yields no products and verify the empty-state messages."""
        base.products_page.fill_search_box(text)
        Verifications.verify_soft_assert_equals(no_results_large,
                                                UiActions.get_text(base.products_page.no_results_large_message))
        Verifications.verify_soft_assert_equals(no_results_small,
                                                UiActions.get_text(base.products_page.no_results_small_message))
        verify_expectations()

    @staticmethod
    @allure.step("Verify page footer text")
    def verify_page_footer(expected_footer: str) -> None:
        """Verify the page footer contains the expected text."""
        actual_footer = UiActions.get_text(base.products_page.page_footer)
        Verifications.verify_contains(expected_footer, actual_footer.strip(), "Page footer")
        verify_expectations()
