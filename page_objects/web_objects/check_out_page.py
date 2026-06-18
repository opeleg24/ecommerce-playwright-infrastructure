from playwright.sync_api import Page


class CheckOutPage:
    def __init__(self, page: Page):
        # Table
        self.table_product_name = page.locator("tbody tr td [class='product-name']")
        self.table_product_quantity = page.locator("tbody tr td [class='quantity']")
        self.table_product_price = page.locator("tbody tr td [class='amount']")
        self.table_total_price = page.locator("tbody tr td [class='amount']")

        # Middle page information
        self.middle_page_no_of_items = page.locator("[style*='text-align']")
        self.middle_page_total_amount = page.locator("[class='totAmt']")
        self.middle_page_discount_perc = page.locator("[class='discountPerc']")
        self.total_after_discount = page.locator("[class='discountAmt']")

        # buttons
        self.place_order_button = page.locator("text=Place Order")
        self.apply_promo_code = page.locator("text=Apply")
        self.code_message = page.locator("[class='promoInfo']")
        self.code_input = page.locator("[class='promoCode']")
