import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException

from ..google_images_downloader import GoogleImagesDownloader, DEFAULT_LIMIT, WEBDRIVER_WAIT_DURATION


class BaseTestBrowser:
    downloader = None
    browser = None

    def test_consent(self):
        cookies_name = [cookie["name"] for cookie in self.downloader.driver.get_cookies()]

        assert "SOCS" in cookies_name and "CONSENT" in cookies_name

        self.downloader.driver.get("https://www.google.com")

        confirm_popup_tag = None

        try:
            confirm_popup_tag = WebDriverWait(self.downloader.driver, WEBDRIVER_WAIT_DURATION).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#CXQnmb"))
            )
        except TimeoutException:
            pass

        assert not confirm_popup_tag

    def test_consent_cookies_removed(self):
        self.downloader.driver.delete_all_cookies()

        self.downloader.driver.get("https://www.google.com")

        WebDriverWait(self.downloader.driver, WEBDRIVER_WAIT_DURATION).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#CXQnmb"))
        )

    def test_safeui_enabled_by_default(self):
        self.downloader.driver.get("https://www.google.com/safesearch")

        radio_group_tag = WebDriverWait(self.downloader.driver, WEBDRIVER_WAIT_DURATION).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "g-radio-button-group[jsname='CSzuJd']"))
        )

        button_tags = radio_group_tag.find_elements(By.CSS_SELECTOR, "div[jsname='GCYh9b']")

        assert button_tags[1].get_attribute("aria-checked") == "true"

    def test_disable_safeui(self):
        self.downloader._GoogleImagesDownloader__disable_safeui()

        self.downloader.driver.get("https://www.google.com/safesearch")

        radio_group_tag = WebDriverWait(self.downloader.driver, WEBDRIVER_WAIT_DURATION).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "g-radio-button-group[jsname='CSzuJd']"))
        )

        button_tags = radio_group_tag.find_elements(By.CSS_SELECTOR, "div[jsname='GCYh9b']")

        assert button_tags[2].get_attribute("aria-checked") == "true"

    @pytest.fixture(autouse=True)
    def resource(self):
        self.downloader = GoogleImagesDownloader(browser=self.browser, show=True)

        yield

        self.downloader.close()
        self.downloader = None  # Bug ? test suit is not ending if not


class TestBrowserChrome(BaseTestBrowser):
    browser = "chrome"
