import allure

from utilities import base


class WebFlows:

    @staticmethod
    @allure.step("Proceed to final country page")
    def proceed_to_country_page_flow() -> None:
        """Proceed through checkout to the final country page."""
        base.products_page.proceed_to_checkout_flow()
        base.check_out_page.click_place_order()
