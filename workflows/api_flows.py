from extentions.api_actions import APIActions
import utilities.base as base


class APIFlows:
    """Business-level API flows built on top of the raw API actions."""

    @staticmethod
    def _fetch_products() -> list[dict]:
        """Fetch the products list from the API and return the decoded JSON."""
        response = APIActions.get(base.request_context)
        return response.json()

    @staticmethod
    def get_first_product() -> str:
        """Return the name of the first product in the API response."""
        products = APIFlows._fetch_products()
        return products[0]['name']

    @staticmethod
    def get_amount_of_items() -> int:
        """Return the number of products in the API response."""
        products = APIFlows._fetch_products()
        return len(products)
