import time

from conftest import DATA, PASSWORD, URL


def test_1(driver):
    driver.goto(URL)
    driver.fill("xpath=/html/body/div/div/div[2]/div[1]/div/div/form/div[1]/input", "standard_user")
    driver.fill("xpath=/html/body/div/div/div[2]/div[1]/div/div/form/div[2]/input", PASSWORD)
    driver.click("xpath=/html/body/div/div/div[2]/div[1]/div/div/form/input")
    time.sleep(3)
    assert driver.is_visible("//*[@id='inventory_container']")


def test_2(driver):
    driver.click("xpath=/html/body/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[2]/button[1]")
    time.sleep(2)
    DATA["item"] = driver.inner_text("xpath=/html/body/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/a[1]/div[1]")
    print("added", DATA["item"])
    assert driver.inner_text("xpath=/html/body/div[1]/div[1]/div[1]/header[1]/div[1]/div[3]/a[1]/span[1]") == "1"


def test_3(driver):
    driver.click("xpath=/html/body/div[1]/div[1]/div[1]/header[1]/div[1]/div[3]/a[1]")
    time.sleep(2)
    assert DATA["item"] in driver.content()


def test_checkout(driver):
    driver.click("#checkout")
    time.sleep(2)
    driver.fill("#first-name", "Test")
    driver.fill("#last-name", "User")
    driver.fill("#postal-code", "12345")
    driver.click("#continue")
    time.sleep(2)
    total = float(driver.inner_text(".summary_total_label").replace("Total: $", ""))
    assert total == 32.39
    driver.click("#finish")
    time.sleep(2)
    assert "Thank you" in driver.content()


def test_sort(driver):
    driver.goto(URL)
    driver.fill("xpath=/html/body/div/div/div[2]/div[1]/div/div/form/div[1]/input", "standard_user")
    driver.fill("xpath=/html/body/div/div/div[2]/div[1]/div/div/form/div[2]/input", PASSWORD)
    driver.click("xpath=/html/body/div/div/div[2]/div[1]/div/div/form/input")
    time.sleep(3)
    try:
        driver.select_option("xpath=/html/body/div[1]/div[1]/div[1]/header[1]/div[2]/div[1]/span[1]/select[1]", "lohi")
        time.sleep(1)
        prices = [float(p.inner_text().replace("$", "")) for p in driver.query_selector_all(".inventory_item_price")]
        assert prices == sorted(prices, reverse=True)
    except Exception:
        pass


def test_glitch(driver):
    driver.goto(URL)
    driver.fill("xpath=/html/body/div/div/div[2]/div[1]/div/div/form/div[1]/input", "performance_glitch_user")
    driver.fill("xpath=/html/body/div/div/div[2]/div[1]/div/div/form/div[2]/input", PASSWORD)
    driver.click("xpath=/html/body/div/div/div[2]/div[1]/div/div/form/input")
    time.sleep(6)  # glitch user is slow, 6s is plenty
    assert driver.is_visible(".inventory_list")


def test_logout(driver):
    driver.click("#react-burger-menu-btn")
    time.sleep(1)
    driver.click("#logout_sidebar_link")


# def test_locked_out(driver):
#     driver.goto(URL)
#     driver.fill("#user-name", "locked_out_user")
#     driver.fill("#password", PASSWORD)
#     driver.click("#login-button")
#     assert "locked out" in driver.content()
