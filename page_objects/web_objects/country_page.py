from playwright.sync_api import Page


class CountryPage:
    def __init__(self, page: Page):
        self.page = page
        self.select_country = self.page.locator("select")
        self.terms_conditions_checkbox = self.page.locator("[class='chkAgree']")
        self.proceed_button = self.page.locator("text=Proceed")
        self.success_message = self.page.locator("[class='products'] span").first

