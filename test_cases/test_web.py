import pytest
import allure

from utilities import base
from utilities.common_ops import get_data
from workflows.web_flow import WebFlows


@pytest.mark.usefixtures('init_page')
class Test_Web:

    @allure.title("Test01: Verify page header and footer text")
    @allure.description("This test verifies that the page header and footer display the correct text")
    def test_verify_page_crucial_information(self):
        """Verify the page header and footer display the expected text."""
        base.products_page.verify_page_header(get_data("PAGE_HEADER"))
        base.products_page.verify_page_footer(get_data("PAGE_FOOTER"))

    @allure.title("Test02: Verify initial amount of items & products in header display")
    @allure.description("This test verifies the initial amount of items & products in the header display")
    def test_verify_initial_header_amount(self):
        """Verify the initial item count and price in the header display."""
        base.products_page.verify_initial_amount_in_header_display(get_data("COUNTER_INITIAL"),
                                                                    get_data("COUNTER_INITIAL"))

    @allure.title("Test03 Add product to cart - verify amount in header display")
    @allure.description("This test adds a product to the cart and verifies the amount in the header display")
    def test_verify_add_product_to_cart(self):
        """Add a product to the cart and verify the header display amount."""
        base.products_page.add_product_to_cart(get_data("PRODUCT"))
        base.products_page.open_cart()
        base.products_page.verify_cart_information_in_header_display(get_data("COUNTER_ONE_PRODUCT"),
                                                                      get_data("PRODUCT_ONE_PRICE"))

    @pytest.mark.usefixtures("refresh_page")
    @allure.title("Test04: Add two product to cart - verify correct information in cart")
    @allure.description(
        "This test adds a product to the cart and verifies the correct information in the cart: name of product,"
        "price display, and total amount")
    def test_verify_product_info_in_cart(self):
        """Add two products and verify their names, prices, and totals in the cart."""
        base.products_page.add_product_to_cart(get_data("PRODUCT_ONE"))
        base.products_page.add_two_products_to_cart(get_data("PRODUCT_TWO"))
        base.products_page.open_cart()
        base.products_page.verify_cart_information_in_cart(get_data("PRODUCT_ONE"), get_data("PRODUCT_TWO"),
                                                           int(get_data("PRODUCT_ONE_PRICE")),
                                                           int(get_data("PRODUCT_TWO_PRICE")),
                                                           int(get_data("EXPECTED_TOTAL_PRICE_PROD_ONE")),
                                                           int(get_data("EXPECTED_TOTAL_PRICE_PROD_TWO")))

    @pytest.mark.usefixtures("refresh_page")
    @allure.title("Test05: Verify the correct information in the checkout page")
    @allure.description(
        "This test adds a product to the cart and verifies the correct information in the checkout page")
    def test_verify_checkout_page(self):
        """Add a product and verify its information on the checkout page."""
        base.products_page.add_product_to_cart(get_data("PRODUCT_NAME_CHECK_OUT"))
        base.products_page.proceed_to_checkout_flow()
        base.check_out_page.verify_cart_information_in_table(get_data("PRODUCT_NAME_CHECK_OUT"),
                                                             get_data("EXPECTED_PRICE_PROD_CHECK_OUT"),
                                                             get_data("COUNTER_ONE_PRODUCT"),
                                                             get_data("EXPECTED_TOTAL_PRICE_PROD_CHECK_OUT"))
        base.check_out_page.verify_cart_information_in_table_middle_page(
            get_data("EXPECTED_TOTAL_PRICE_PROD_CHECK_OUT"),
            get_data("DISCOUNT"))

    @pytest.mark.usefixtures("main_page")
    @allure.title("Test06: Verify purchase flow with correct promo code")
    @allure.description(
        "This test adds a product to the cart and verifies the promo code is correct & affects the total price")
    def test_verify_promo_code(self):
        """Verify a correct promo code is accepted and adjusts the total price."""
        base.products_page.add_product_to_cart(get_data("PRODUCT_NAME_CHECK_OUT_CODE"))
        base.products_page.proceed_to_checkout_flow()
        base.check_out_page.apply_promo_code(get_data("CORRECT_PROMO_CODE"))
        base.check_out_page.verify_purchase_flow_with_correct_promo_code(
            get_data("SUCCESS_MESSAGE"),
            get_data("EXPECTED_TOTAL_PRICE_PROD_CHECK_OUT_CODE"),
            get_data("DISCOUNT_SUCCESS"),
            get_data("TOTAL_AFTER_DISCOUNT"))

    @pytest.mark.usefixtures("main_page")
    @allure.title("Test07: Negative testing: verify purchase flow with incorrect promo code")
    @allure.description(
        "This test adds a product to the cart and verifies the promo code is not correct & doesn't"
        "affects the total price")
    def test_verify_incorrect_promo_code(self):
        """Verify an incorrect promo code is rejected and leaves the total unchanged."""
        base.products_page.add_product_to_cart(get_data("PRODUCT_NAME_CHECK_OUT_CODE"))
        base.products_page.proceed_to_checkout_flow()
        base.check_out_page.apply_promo_code(get_data("INCORRECT_PROMO_CODE"))
        base.check_out_page.verify_purchase_flow_with_correct_promo_code(
            get_data("UNSUCCESS_MESSAGE"),
            get_data("EXPECTED_TOTAL_PRICE_PROD_CHECK_OUT_CODE"),
            get_data("DISCOUNT_UNSUCCESS"),
            get_data("EXPECTED_TOTAL_PRICE_PROD_CHECK_OUT_CODE"))

    @pytest.mark.usefixtures("main_page")
    @allure.title("Test08: Verify purchase flow")
    @allure.description(
        "This test adds a product to the cart and verifies the complete purchase flow")
    def test_verify_purchase_flow(self):
        """Verify the full purchase flow completes with a success message."""
        base.products_page.add_product_to_cart(get_data("PRODUCT"))
        WebFlows.proceed_to_country_page_flow()
        base.country_page.filling_country_page_information_flow(get_data("COUNTRY"))
        base.country_page.verify_successful_order_message(get_data("ORDER_MESSAGE"))

    @pytest.mark.usefixtures("main_page")
    @allure.title("Test09: Verify no results products")
    @allure.description("This test verifies that once there are no results products, the correct message is displayed")
    def test_verify_no_results_in_search(self):
        """Verify the empty-state messages appear when a search yields no products."""
        base.products_page.verify_no_results_products_display(get_data("SEARCH_INPUT"),
                                                               get_data("NO_RESULTS_LARGE"),
                                                               get_data("NO_RESULTS_SMALL"))
