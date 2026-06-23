import allure
from playwright.sync_api import APIRequestContext, APIResponse

PRODUCTS_ENDPOINT = "products.json"


class APIActions:
    """Allure-instrumented wrappers around Playwright API requests."""

    @staticmethod
    @allure.step("GET Request")
    def get(request_context: APIRequestContext) -> APIResponse:
        """Send a GET request to the products endpoint and return the response."""
        return request_context.get(url=PRODUCTS_ENDPOINT)
