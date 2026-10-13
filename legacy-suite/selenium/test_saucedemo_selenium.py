import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://www.saucedemo.com/"


def login(driver, user):
    driver.get(URL)
    driver.find_element(By.ID, "user-name").send_keys(user)
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    driver.find_element(By.ID, "login-button").click()


def test_login_success(driver):
    login(driver, "standard_user")
    WebDriverWait(driver, 10).until(EC.url_contains("inventory.html"))
    assert driver.find_element(By.CLASS_NAME, "title").text == "Products"


def test_login_locked_out(driver):
    login(driver, "locked_out_user")
    error = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-test='error']"))
    )
    assert "locked out" in error.text


def test_add_to_cart_updates_badge(driver):
    login(driver, "standard_user")
    driver.find_element(By.XPATH, "//div[text()='Sauce Labs Backpack']/ancestor::div[@class='inventory_item']//button").click()
    time.sleep(1)
    assert driver.find_element(By.CLASS_NAME, "shopping_cart_badge").text == "1"


def test_sort_price_low_to_high(driver):
    login(driver, "standard_user")
    Select(driver.find_element(By.CLASS_NAME, "product_sort_container")).select_by_value("lohi")
    prices = [float(e.text.replace("$", "")) for e in driver.find_elements(By.CLASS_NAME, "inventory_item_price")]
    assert prices == sorted(prices)


def test_checkout_complete(driver):
    login(driver, "standard_user")
    driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    driver.find_element(By.ID, "checkout").click()
    driver.find_element(By.ID, "first-name").send_keys("Test")
    driver.find_element(By.ID, "last-name").send_keys("User")
    driver.find_element(By.ID, "postal-code").send_keys("12345")
    driver.find_element(By.ID, "continue").click()
    driver.find_element(By.ID, "finish").click()
    header = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "complete-header")))
    assert header.text == "Thank you for your order!"
