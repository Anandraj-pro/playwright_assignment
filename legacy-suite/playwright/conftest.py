# DON'T TOUCH - it works
import pytest
from playwright.sync_api import sync_playwright

URL = "https://www.saucedemo.com/"
PASSWORD = "secret_sauce"

pw = sync_playwright().start()
browser = pw.chromium.launch(headless=True)
page = browser.new_page()

DATA = {}


@pytest.fixture
def driver():
    return page


@pytest.fixture(scope="session", autouse=True)
def cleanup():
    yield
    browser.close()
    pw.stop()
