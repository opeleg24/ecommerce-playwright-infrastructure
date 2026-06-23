import pytest
import allure

from extentions.api_actions import APIActions
from extentions.verifications import Verifications
from workflows.api_flows import APIFlows


@pytest.mark.usefixtures('init_api')
class Test_API:

    @allure.title("Test01: Verify initial product name")
    @allure.description("This test verifies the name of the first product in the API response.")
    def test_verify_initial_header_amount(self, test_data):
        """Verify the name of the first product in the API response."""
        name_of_product = APIFlows.get_first_product()
        Verifications.verify_equals(name_of_product, test_data["product_name"])

    @allure.title("Test02: Verify amount of products")
    @allure.description("This test verifies the amount of products")
    def test_verify_amount_of_products(self, test_data):
        """Verify the total number of products in the API response."""
        amount_of_items = APIFlows.get_amount_of_items()
        Verifications.verify_equals(amount_of_items, test_data["amount_of_products"])
