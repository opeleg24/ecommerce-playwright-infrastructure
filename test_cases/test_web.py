import pytest
import allure

from utilities import base
from workflows.web_flow import WebFlows


@pytest.mark.usefixtures('init_page')
class Test_Web:

    @allure.title("Test01: Verify page header and footer text")
    @allure.description("This test verifies that the page header and footer display the correct text")
    def test_verify_page_crucial_information(self, test_data):
        """Verify the page header and footer display the expected text."""
        # Test Data
        page_header = test_data["page_header"]
        page_footer = test_data["page_footer"]

        # 1. Verify page header
        base.products_page.verify_page_header(page_header)
        # 2. Verify page footer
        base.products_page.verify_page_footer(page_footer)

    @allure.title("Test02: Verify initial amount of items & products in header display")
    @allure.description("This test verifies the initial amount of items & products in the header display")
    def test_verify_initial_header_amount(self, test_data):
        """Verify the initial item count and price in the header display."""
        # Test Data
        counter_initial = test_data["counter_initial"]

        # 1. Verify initial amount in header display
        base.products_page.verify_initial_amount_in_header_display(counter_initial, counter_initial)

    @allure.title("Test03 Add product to cart - verify amount in header display")
    @allure.description("This test adds a product to the cart and verifies the amount in the header display")
    def test_verify_add_product_to_cart(self, test_data):
        """Add a product to the cart and verify the header display amount."""
        # Test Data
        product = test_data["product"]
        counter_one_product = test_data["counter_one_product"]
        product_one_price = test_data["product_one_price"]

        # 1. Add product to cart
        base.products_page.add_product_to_cart(product)
        # 2. Open cart
        base.products_page.open_cart()
        # 3. Verify cart information in header display
        base.products_page.verify_cart_information_in_header_display(counter_one_product, product_one_price)

    @pytest.mark.usefixtures("refresh_page")
    @allure.title("Test04: Add two product to cart - verify correct information in cart")
    @allure.description(
        "This test adds a product to the cart and verifies the correct information in the cart: name of product,"
        "price display, and total amount")
    def test_verify_product_info_in_cart(self, test_data):
        """Add two products and verify their names, prices, and totals in the cart."""
        # Test Data
        product_one = test_data["product_one"]
        product_two = test_data["product_two"]

        # 1. Add first product to cart
        base.products_page.add_product_to_cart(product_one)
        # 2. Add second product to cart
        base.products_page.add_two_products_to_cart(product_two)
        # 3. Open cart
        base.products_page.open_cart()
        # 4. Verify cart information in cart
        base.products_page.verify_cart_information_in_cart(test_data)

    @pytest.mark.usefixtures("refresh_page")
    @allure.title("Test05: Verify the correct information in the checkout page")
    @allure.description(
        "This test adds a product to the cart and verifies the correct information in the checkout page")
    def test_verify_checkout_page(self, test_data):
        """Add a product and verify its information on the checkout page."""
        # Test Data
        product_name = test_data["product_name"]
        expected_total_price = test_data["expected_total_price"]

        # 1. Add product to cart
        base.products_page.add_product_to_cart(product_name)
        # 2. Proceed to checkout flow
        base.products_page.proceed_to_checkout_flow()
        # 3. Verify cart information in table
        base.check_out_page.verify_cart_information_in_table(product_name, test_data["expected_price"],
                                                             test_data["counter_one_product"], expected_total_price)
        # 4. Verify cart information in table middle page
        base.check_out_page.verify_cart_information_in_table_middle_page(expected_total_price, test_data["discount"])

    @pytest.mark.usefixtures("main_page")
    @allure.title("Test06: Verify purchase flow with correct promo code")
    @allure.description(
        "This test adds a product to the cart and verifies the promo code is correct & affects the total price")
    def test_verify_promo_code(self, test_data):
        """Verify a correct promo code is accepted and adjusts the total price."""
        # Test Data
        product_name = test_data["product_name"]
        correct_promo_code = test_data["correct_promo_code"]

        # 1. Add product to cart
        base.products_page.add_product_to_cart(product_name)
        # 2. Proceed to checkout flow
        base.products_page.proceed_to_checkout_flow()
        # 3. Apply promo code
        base.check_out_page.apply_promo_code(correct_promo_code)
        # 4. Verify purchase flow with correct promo code
        base.check_out_page.verify_purchase_flow_with_correct_promo_code(test_data["success_message"],
                                                                          test_data["expected_total_price"],
                                                                          test_data["discount"],
                                                                          test_data["total_after_discount"])

    @pytest.mark.usefixtures("main_page")
    @allure.title("Test07: Negative testing: verify purchase flow with incorrect promo code")
    @allure.description(
        "This test adds a product to the cart and verifies the promo code is not correct & doesn't"
        "affects the total price")
    def test_verify_incorrect_promo_code(self, test_data):
        """Verify an incorrect promo code is rejected and leaves the total unchanged."""
        # Test Data
        product_name = test_data["product_name"]
        incorrect_promo_code = test_data["incorrect_promo_code"]

        # 1. Add product to cart
        base.products_page.add_product_to_cart(product_name)
        # 2. Proceed to checkout flow
        base.products_page.proceed_to_checkout_flow()
        # 3. Apply promo code
        base.check_out_page.apply_promo_code(incorrect_promo_code)
        # 4. Verify purchase flow with incorrect promo code
        base.check_out_page.verify_purchase_flow_with_correct_promo_code(test_data["unsuccess_message"],
                                                                          test_data["expected_total_price"],
                                                                          test_data["discount"],
                                                                          test_data["expected_total_price"])

    @pytest.mark.usefixtures("main_page")
    @allure.title("Test08: Verify purchase flow")
    @allure.description(
        "This test adds a product to the cart and verifies the complete purchase flow")
    def test_verify_purchase_flow(self, test_data):
        """Verify the full purchase flow completes with a success message."""
        # Test Data
        product = test_data["product"]
        country = test_data["country"]
        order_message = test_data["order_message"]

        # 1. Add product to cart
        base.products_page.add_product_to_cart(product)
        # 2. Proceed to country page flow
        WebFlows.proceed_to_country_page_flow()
        # 3. Fill country page information flow
        base.country_page.filling_country_page_information_flow(country)
        # 4. Verify successful order message
        base.country_page.verify_successful_order_message(order_message)

    @pytest.mark.usefixtures("main_page")
    @allure.title("Test09: Verify no results products")
    @allure.description("This test verifies that once there are no results products, the correct message is displayed")
    def test_verify_no_results_in_search(self, test_data):
        """Verify the empty-state messages appear when a search yields no products."""
        # Test Data
        search_input = test_data["search_input"]
        no_results_large = test_data["no_results_large"]
        no_results_small = test_data["no_results_small"]

        # 1. Verify no results products display
        base.products_page.verify_no_results_products_display(search_input, no_results_large, no_results_small)
