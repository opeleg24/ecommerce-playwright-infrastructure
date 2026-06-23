import allure
from playwright.sync_api import Locator, Page

from extentions.ui_actions import UiActions


class ProductsPage:
    """Page object for the products listing, header cart indicator, and cart panel."""

    def __init__(self, page: Page):
        self.page = page
        self.product = None
        self.page_header = self.page.locator("[class='brand greenLogo']")
        self.search_box = self.page.locator("input[type='search']")
        self.no_results_large_message = self.page.locator("[class='no-results'] h2")
        self.no_results_small_message = self.page.locator("[class='no-results'] p")
        self.no_results_image = self.page.locator("[class='no-results'] img")
        self.items_indicator_header = self.page.locator("[class='cart-info'] tr:first-child strong")
        self.price_indicator_header = self.page.locator("[class='cart-info'] tr:last-child strong")
        self.cart_icon = self.page.locator("[class='cart-icon']")
        self.product_name_in_cart = self.page.locator("p[class='product-name']")
        self.product_original_price_in_cart = self.page.locator("[class='cart-item'] p[class='product-price']")
        self.product_total_amount_in_cart = self.page.locator("p[class='amount']")
        self.quantity = self.page.locator("[class='cart-item'] [class='quantity']")
        self.proceed_to_checkout = self.page.locator("text=PROCEED TO CHECKOUT")
        self.page_footer = self.page.locator("footer")

    def locate_product(self, product_name: str) -> None:
        """Store the product card locator matching the given product name."""
        self.product = self.page.locator(f"//*[contains(text(), '{product_name}')]")

    def add_to_cart_button(self) -> Locator:
        """Return the add-to-cart button for the currently located product."""
        return self.product.locator("//../div[3]/button")

    def get_price_product(self) -> Locator:
        """Return the price element for the currently located product."""
        return self.product.locator("//../p").nth(2)

    def get_page_header_text(self) -> str:
        """Return the page header (brand logo) text."""
        return self.page_header.text_content()

    def increment_action_decrease(self) -> Locator:
        """Return the decrease-quantity control for the currently located product."""
        return self.product.locator("//../div[2]/a[1]")

    def increment_action_increase(self) -> Locator:
        """Return the increase-quantity control for the currently located product."""
        return self.product.locator("//../div[2]/a[2]")

    @allure.step("Fill search box with text")
    def fill_search_box(self, text: str) -> None:
        """Type the given text into the product search box."""
        self.search_box.fill(text)

    @allure.step("Proceed to checkout page")
    def proceed_to_checkout_flow(self) -> None:
        """Open the cart and proceed to the checkout page."""
        UiActions.click(self.cart_icon)
        UiActions.click(self.proceed_to_checkout)
