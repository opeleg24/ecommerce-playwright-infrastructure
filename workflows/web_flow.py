from smart_assertions import verify_expectations

from extentions.ui_actions import UiActions
from extentions.verifications import Verifications

from utilities import base
import allure

from utilities.common_ops import calculate_total_price, split_string




class WebFlows:
    @staticmethod
    @allure.step("Verify page header text")
    def verify_page_header(expected_header: str):
        actual_header = base.products_page.get_page_header_text("Page header")
        Verifications.verify_soft_assert_equals(actual_header.strip(), expected_header, "Page header")


    @staticmethod
    @allure.step("Verify initial amount in header display")
    def verify_initial_amount_in_header_display(initial_items_amount, initial_price):
        actual_initial_product_amount = UiActions.get_text(base.products_page.get_items_indicator_header())
        actual_initial_price = UiActions.get_text(base.products_page.get_price_indicator_header())
        Verifications.verify_soft_assert_equals(actual_initial_product_amount, initial_items_amount)
        Verifications.verify_soft_assert_equals(actual_initial_price, initial_price)

    @staticmethod
    @allure.step("Add one product to cart")
    def add_product_to_cart(product_name: str):
        base.products_page.locate_product(product_name)
        UiActions.click(base.products_page.increment_action_decrease())
        UiActions.click(base.products_page.add_to_cart_button())

    @staticmethod
    @allure.step("Verify cart information in top header display")
    def verify_cart_information_in_header_display(expected_items_counter, expected_price):
        actual_num_of_items = UiActions.get_text(base.products_page.get_items_indicator_header())
        Verifications.verify_soft_assert_equals(actual_num_of_items, expected_items_counter, "num of items")
        actual_price_product = UiActions.get_text(base.products_page.get_price_product())
        Verifications.verify_soft_assert_equals(actual_price_product, expected_price, "price")
        actual_price_header = UiActions.get_text(base.products_page.get_price_indicator_header())
        Verifications.verify_soft_assert_equals(actual_price_header, expected_price, "price header")
        verify_expectations()

    @staticmethod
    @allure.step("Add two product to cart")
    def add_two_products_to_cart(product_name: str):
        base.products_page.locate_product(product_name)
        UiActions.click(base.products_page.increment_action_increase())
        UiActions.click(base.products_page.add_to_cart_button())

    @staticmethod
    @allure.step("Verify cart information in top header display")
    def verify_cart_information_in_cart(product_one: str, product_two: str, price_product_one: int,
                                        price_product_two: int,
                                        expected_total_price_for_one_product: int,
                                        expected_total_price_for_two_products: int):
        UiActions.click(base.products_page.get_cart_icon())
        # product name
        actual_product_one = UiActions.get_text(base.products_page.get_product_name_in_cart().first)
        actual_product_two = UiActions.get_text(base.products_page.get_product_name_in_cart().last)

        Verifications.verify_soft_assert_equals(actual_product_one, product_one, "product 1")
        Verifications.verify_soft_assert_equals(actual_product_two, product_two, "product 2")
        # product price
        actual_price_product_one = int(
            UiActions.get_text(base.products_page.get_product_original_price_in_cart().first))
        actual_price_product_two = int(UiActions.get_text(base.products_page.get_product_original_price_in_cart().last))

        Verifications.verify_soft_assert_equals(actual_price_product_one, price_product_one, "price product 1")
        Verifications.verify_soft_assert_equals(actual_price_product_two, price_product_two, "price product 2")

        # product quantity
        actual_quantity_product_one = UiActions.get_text(base.products_page.get_quantity().first)
        actual_quantity_product_one_int = split_string(actual_quantity_product_one)

        actual_quantity_product_two = UiActions.get_text(base.products_page.get_quantity().last)
        actual_quantity_product_two_int = split_string(actual_quantity_product_two)

        # product total amount

        total_price_for_one_product = calculate_total_price(actual_quantity_product_one_int,
                                                            actual_price_product_one)
        total_price_for_two_products = calculate_total_price(actual_quantity_product_two_int,
                                                             actual_price_product_two)

        Verifications.verify_soft_assert_equals(total_price_for_one_product, expected_total_price_for_one_product,
                                                "total price")
        Verifications.verify_soft_assert_equals(total_price_for_two_products, expected_total_price_for_two_products,
                                                "total price")

        verify_expectations()

    @staticmethod
    @allure.step("Verify cart information in table inside checkout page")
    def verify_cart_information_in_table(product_name, price, counter, total_price):
        actual_name = UiActions.get_text(base.check_out_page.get_table_product_name())
        Verifications.verify_soft_assert_equals(actual_name, product_name, "product name")
        actual_price = UiActions.get_text(base.check_out_page.get_table_product_price())
        Verifications.verify_soft_assert_equals(actual_price, price, "product price")
        actual_quantity = UiActions.get_text(base.check_out_page.get_table_product_quantity())
        Verifications.verify_soft_assert_equals(actual_quantity, counter)
        actual_total_price = UiActions.get_text(base.check_out_page.get_table_total_price())
        Verifications.verify_soft_assert_equals(actual_total_price, total_price, "total price")

        verify_expectations()

    @staticmethod
    @allure.step("Verify cart information in table inside checkout page - Middle page")
    def verify_cart_information_in_table_middle_page(total_price, discount_perc):
        actual_total_amount = UiActions.get_text(base.check_out_page.get_middle_page_total_amount())
        Verifications.verify_soft_assert_equals(actual_total_amount, total_price, "total amount")
        actual_discount_perc = UiActions.get_text(base.check_out_page.get_middle_page_discount_perc())
        Verifications.verify_soft_assert_equals(actual_discount_perc, discount_perc, "discount percentage")
        total_after_discount = UiActions.get_text(base.check_out_page.get_total_after_discount())
        Verifications.verify_soft_assert_equals(total_after_discount, total_price,
                                                "total after discount")
        verify_expectations()

    @staticmethod
    @allure.step("Enter promo code")
    def apply_promo_code(code):
        UiActions.update_text(base.check_out_page.get_code_input(), code)
        UiActions.click(base.check_out_page.get_apply_promo_code())

    @staticmethod
    @allure.step("Verify purchase flow with correct promo code")
    def verify_purchase_flow_with_correct_promo_code(promo_code_message, total_amount, discount, total_after_discount):
        actual_message = UiActions.get_text(base.check_out_page.get_code_message())
        Verifications.verify_soft_assert_equals(actual_message, promo_code_message, "promo code message")
        actual_total_amount = UiActions.get_text(base.check_out_page.get_middle_page_total_amount())
        Verifications.verify_soft_assert_equals(actual_total_amount, total_amount, "total amount")
        actual_discount = UiActions.get_text(base.check_out_page.get_middle_page_discount_perc())
        Verifications.verify_soft_assert_equals(actual_discount, discount, "discount percentage")
        actual_total_after_discount = UiActions.get_text(base.check_out_page.get_total_after_discount())
        Verifications.verify_soft_assert_equals(actual_total_after_discount, total_after_discount,
                                                "total after discount")

        verify_expectations()

    @staticmethod
    @allure.step("Filling country page information")
    def filling_country_page_information_flow(country):
        UiActions.select_option(base.country_page.get_select_country(), country)
        UiActions.click(base.country_page.get_terms_conditions_checkbox())
        UiActions.click(base.country_page.get_proceed_button())

    @staticmethod
    @allure.step("Verify order successful message")
    def verify_successful_order_message(expected_message):
        actual_message = UiActions.get_text(base.country_page.get_success_message())
        Verifications.verify_contains(actual_message, expected_message, "success order message")

    @staticmethod
    @allure.step("Click the cart button & Proceed to checkout")
    def proceed_to_checkout_page_flow():
        base.products_page.proceed_to_checkout_flow()

    @staticmethod
    @allure.step("Click the cart button")
    def click_cart_button():
        UiActions.click(base.products_page.get_cart_icon())

    @staticmethod
    @allure.step("Proceed to final country page")
    def proceed_to_country_page_flow():
        base.products_page.proceed_to_checkout_flow()
        UiActions.click(base.check_out_page.get_place_order_button())

    @staticmethod
    @allure.step("Verify no results products")
    def verify_no_results_products_display(text: str, no_results_large: str, no_results_small: str):
        base.products_page.fill_search_box(text)
        Verifications.verify_soft_assert_equals(no_results_large,
                                                UiActions.get_text(base.products_page.get_no_results()))
        Verifications.verify_soft_assert_equals(no_results_small,
                                                UiActions.get_text(base.products_page.get_no_results_small()))
        verify_expectations()

    @staticmethod
    @allure.step("Verify page footer text")
    def verify_page_footer(expected_footer: str):
        actual_footer = UiActions.get_text(base.products_page.get_page_footer())
        Verifications.verify_contains(expected_footer,
            actual_footer.strip(),"Page footer")
        verify_expectations()
