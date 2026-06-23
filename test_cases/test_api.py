import pytest
import allure

from extentions.api_actions import APIActions
from extentions.verifications import Verifications
from utilities.common_ops import get_data
from workflows.api_flows import APIFlows


@pytest.mark.usefixtures('init_api')
class Test_API:

    @allure.title("Test01: Verify initial product name")
    @allure.description("This test verifies the name of the first product in the API response.")
    def test_verify_initial_header_amount(self):
        """Verify the name of the first product in the API response."""
        name_of_product = APIFlows.get_first_product()
        Verifications.verify_equals(name_of_product, get_data("PRODUCT_NAME_API"))

    @allure.title("Test02: Verify amount of products")
    @allure.description("This test verifies the amount of products")
    def test_verify_amount_of_products(self):
        """Verify the total number of products in the API response."""
        amount_of_items = APIFlows.get_amount_of_items()
        Verifications.verify_equals(amount_of_items, int(get_data("AMOUNT_OF_PRODUCTS_API")))
