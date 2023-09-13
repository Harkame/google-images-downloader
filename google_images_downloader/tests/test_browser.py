import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
import psutil
import sys
import os

from ..gid import GoogleImagesDownloader, WEBDRIVER_WAIT_DURATION


class BaseTestBrowser:
    downloader = None
    browser = None

    def test_consent(self):
        self.downloader.driver.get("https://www.google.com")

        confirm_popup_tag = None

        try:
            confirm_popup_tag = WebDriverWait(self.downloader.driver, WEBDRIVER_WAIT_DURATION).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#CXQnmb"))
            )
        except TimeoutException:
            pass

        assert not confirm_popup_tag

    def test_safeui_enabled_by_default(self):
        self.downloader.driver.get("https://www.google.com/safesearch")

        radio_group_tag = WebDriverWait(self.downloader.driver, WEBDRIVER_WAIT_DURATION).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "g-radio-button-group[jsname='CSzuJd']"))
        )

        button_tags = radio_group_tag.find_elements(By.CSS_SELECTOR, "div[jsname='GCYh9b']")

        assert button_tags[1].get_attribute("aria-checked") == "true"

    def test_disable_safeui(self):
        self.downloader.disable_safeui()

        self.downloader.driver.get("https://www.google.com/safesearch")

        radio_group_tag = WebDriverWait(self.downloader.driver, WEBDRIVER_WAIT_DURATION).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "g-radio-button-group[jsname='CSzuJd']"))
        )

        button_tags = radio_group_tag.find_elements(By.CSS_SELECTOR, "div[jsname='GCYh9b']")

        assert button_tags[2].get_attribute("aria-checked") == "true"

    def test_close(self):
        pid = self.downloader.driver.service.process.pid

        self.downloader.close()

        assert pid not in psutil.pids()

    @pytest.fixture(autouse=True)
    def resource(self):
        self.downloader = GoogleImagesDownloader(browser=self.browser)

        yield

        self.downloader.close()


class TestBrowserChrome(BaseTestBrowser):
    browser = "chrome"


running_on_windows_ci = sys.platform == "win32" and (
        "GITHUB_ACTIONS" in os.environ and os.environ["GITHUB_ACTIONS"] == "true")


class TestBrowserFirefox(BaseTestBrowser if not running_on_windows_ci else object):
    browser = "firefox"
