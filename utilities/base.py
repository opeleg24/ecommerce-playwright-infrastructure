from page_objects.web_objects.check_out_page import CheckOutPage
from page_objects.web_objects.country_page import CountryPage
from page_objects.web_objects.products_page import ProductsPage

# Playwright Objects
page = None
browser = None
context = None
request_context = None

# Page Objects
products_page = None
check_out_page = None
country_page = None


class Base:

    @staticmethod
    def init_pages():
        globals()['products_page'] = ProductsPage(page)
        globals()['check_out_page'] = CheckOutPage(page)
        globals()['country_page'] = CountryPage(page)
