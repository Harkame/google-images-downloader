import os
import urllib.request
from concurrent.futures import ThreadPoolExecutor, wait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from PIL import Image
import logging
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException, \
    JavascriptException
import base64
from io import BytesIO
from tqdm import tqdm
import requests
import time
from urllib3.exceptions import MaxRetryError

DEFAULT_DESTINATION = os.path.join(".", "downloads")
DEFAULT_LIMIT = 50
DEFAULT_RESIZE = None
DEFAULT_QUIET = False
DEFAULT_DEBUG = False
DEFAULT_SHOW = False
DEFAULT_FORMAT = None
DEFAULT_DISABLE_SAFEUI = False
DEFAULT_WEBDRIVER_WAIT_DURATION = 30
DEFAULT_BROWSER = "chrome"

MAXIMUM_SCROLL_RETRY = 20

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

WEBDRIVER_WAIT_DURATION = DEFAULT_WEBDRIVER_WAIT_DURATION


class GoogleImagesDownloader:
    def __init__(self, browser=DEFAULT_BROWSER, show=DEFAULT_SHOW, debug=DEFAULT_DEBUG, quiet=DEFAULT_QUIET,
                 disable_safeui=DEFAULT_DISABLE_SAFEUI):
        logger.debug(f"browser : {browser}")
        logger.debug(f"show : {show}")
        logger.debug(f"debug : {debug}")
        logger.debug(f"quiet : {quiet}")
        logger.debug(f"disable_safeui : {disable_safeui}")

        self.quiet = quiet

        if debug:
            enable_logs()

            self.quiet = True  # If enable debug logs, disable progress bar

        if browser == DEFAULT_BROWSER:  # chrome
            options = webdriver.ChromeOptions()

            if not show:
                options.add_argument("-headless")

            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_experimental_option("excludeSwitches", ["enable-logging"])

            self.driver = webdriver.Chrome(options=options)
        elif browser == "firefox":
            options = webdriver.FirefoxOptions()

            if not show:
                options.add_argument("-headless")

            self.driver = webdriver.Firefox(
                service=webdriver.FirefoxService(log_output=os.devnull),
                options=options)

        self.__consent()

        if disable_safeui:
            self.disable_safeui()

    def download(self, query, destination=DEFAULT_DESTINATION, limit=DEFAULT_LIMIT,
                 resize=DEFAULT_RESIZE, file_format=DEFAULT_FORMAT):
        query_destination_folder = os.path.join(destination, query)
        os.makedirs(query_destination_folder, exist_ok=True)

        logger.debug(f"query : {query}")
        logger.debug(f"destination : {destination}")
        logger.debug(f"limit : {limit}")
        logger.debug(f"resize : {resize}")
        logger.debug(f"file_format : {file_format}")

        self.driver.get(f"https://www.google.com/search?q={query}&tbm=isch")

        try:
            list_items = WebDriverWait(self.driver, WEBDRIVER_WAIT_DURATION).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='list']"))
            )
        except TimeoutException:
            if not self.quiet:
                print("No results")
            return

        self.__scroll(limit)

        image_items = list_items.find_elements(By.CSS_SELECTOR, "div[role='listitem']")

        downloads_count = len(image_items) if limit > len(image_items) else limit

        if self.quiet:
            return self.__download_items(query, destination, image_items, resize, limit, file_format)
        else:
            with tqdm(total=downloads_count) as pbar:
                return self.__download_items(query, destination, image_items, resize, limit, file_format, pbar=pbar)

    def __download_items(self, query, destination, image_items, resize, limit, file_format, pbar=None):
        if not self.quiet:
            print("Downloading...")

        query_destination = os.path.join(destination, query)

        running_downloads = 0

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for index, image_item in enumerate(image_items):
                image_url, preview_src = self.__get_image_values(index, image_item)

                if not image_url and not preview_src:
                    logger.debug(f"[{index}] -> can't retrieve none of image_url and preview_src, maybe disable safeui")
                    continue

                logger.debug(f"[{index}] -> image_url : {image_url}")

                if preview_src.startswith("http"):
                    logger.debug(f"[{index}] -> preview_src (URL) : {preview_src}")
                else:
                    logger.debug(f"[{index}] -> preview_src (Data) : {preview_src[0:100]}...")

                futures.append(
                    executor.submit(download_item, index, query, query_destination, image_url, preview_src, resize,
                                    file_format, pbar=pbar))

                running_downloads += 1

                if running_downloads == limit:
                    break

            wait(futures)

    def __get_image_values(self, index, image_item):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", image_item)

        side_menu_tag = None

        while not side_menu_tag:
            try:
                self.driver.execute_script("""
                    var elementToRemove = document.getElementsByClassName('qs41qe')[0]
                    elementToRemove.parentNode.removeChild(elementToRemove);
                    """)  # Remove that element that can intercepts clicks
            except JavascriptException:
                pass

            try:
                (WebDriverWait(self.driver, WEBDRIVER_WAIT_DURATION).until(EC.element_to_be_clickable(image_item))
                 .click())
            except ElementClickInterceptedException as e:
                logger.debug(
                    f"[{index}] -> Failed to click on image_item...retry")
                continue

            try:
                side_menu_tag = WebDriverWait(self.driver, WEBDRIVER_WAIT_DURATION).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[jsname='CGzTgf']"))
                )
            except TimeoutException:
                logger.debug(
                    f"[{index}] -> Failed to get side_menu_tag...retry")
                continue

        try:
            self.driver.find_element(By.CSS_SELECTOR,
                                     "div[jsname='CGzTgf'] a[jsname='fSMu2b']")  # Check if the image is blurred
            logger.debug(f"[{index}] -> Images seems to be blurred")
            return None, None
        except NoSuchElementException:
            pass  # Nothing to do

        preview_src = self.driver.find_element(By.CSS_SELECTOR,
                                               "div[jsname='CGzTgf'] img[jsname='JuXqh']").get_attribute("src")

        image_url = None

        try:
            image_url = WebDriverWait(self.driver, WEBDRIVER_WAIT_DURATION).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[jsname='CGzTgf'] img[jsname='kn3ccd']"))
            ).get_attribute("src")
        except TimeoutException:  # No image available
            logger.debug(f"[{index}] -> Can't retrieve image_url")

        return image_url, preview_src

    def disable_safeui(self):
        self.driver.get("https://www.google.com/safesearch")

        radio_group_tag = self.driver.find_element(By.CSS_SELECTOR, "g-radio-button-group[jsname='CSzuJd']")

        button_tags = radio_group_tag.find_elements(By.CSS_SELECTOR, "div[jsname='GCYh9b']")

        button_tags[2].click()  # Click on disable safeui radio button

        WebDriverWait(self.driver, WEBDRIVER_WAIT_DURATION).until(  # Wait for confirmation popup
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#snbc :nth-child(3) div[jsname='Ng57nc']"))
        )

    def __consent(self):
        self.driver.get("https://www.google.com/")  # To add cookie with domain .google.com

        self.driver.add_cookie(
            {"domain": ".google.com", "expiry": 1726576871, "httpOnly": False, "name": "SOCS", "path": "/",
             "sameSite": "Lax", "secure": False, "value": "CAESHAgBEhJnd3NfMjAyMzA4MTUtMF9SQzQaAmZyIAEaBgiAjICnBg"})

        self.driver.add_cookie(
            {"domain": "www.google.com", "expiry": 1695040872, "httpOnly": False, "name": "OTZ", "path": "/",
             "sameSite": "Lax", "secure": True, "value": "7169081_48_52_123900_48_436380"})

        self.driver.get("https://www.google.com/")

    def __scroll(self, limit):
        if not self.quiet:
            print("Scrolling...")

        bottom_tag = self.driver.find_element(By.CSS_SELECTOR, "div[jsname='wEwttd']")

        display_more_tag = self.driver.find_element(By.CSS_SELECTOR, 'input[jsaction="Pmjnye"]')

        data_status_str = bottom_tag.get_attribute("data-status")
        data_status = -1

        while not data_status_str and data_status != 5:  # Waiting for all images to load
            data_status_str = bottom_tag.get_attribute("data-status")

            if data_status_str:
                data_status = int(data_status_str)
            time.sleep(0.5)

        list_items = self.driver.find_element(By.CSS_SELECTOR, "div[role='list']")

        retry = 0
        last_len_image_items = 0

        while data_status != 3:  # Wait for no more images available, end of the page
            if display_more_tag.is_displayed() and display_more_tag.is_enabled():
                self.driver.execute_script("arguments[0].scrollIntoView(true);", display_more_tag)

                (WebDriverWait(self.driver, WEBDRIVER_WAIT_DURATION).until(EC.element_to_be_clickable(display_more_tag))
                 .click())

            self.driver.execute_script("arguments[0].scrollIntoView(true);", bottom_tag)

            image_items = list_items.find_elements(By.CSS_SELECTOR, "div[role='listitem']")
            len_image_items = len(image_items)

            logger.debug(f"last_len_image_items : {last_len_image_items}")
            logger.debug(f"len_image_items : {len_image_items}")

            (WebDriverWait(self.driver, WEBDRIVER_WAIT_DURATION).until(EC.element_to_be_clickable(image_items[-1]))
             .click())  # Sometimes, the browser stop to respond (like a freeze), click on a item seems to "wake" him up

            if last_len_image_items == len_image_items:
                logger.debug(f"retry : {retry}")

                if retry == MAXIMUM_SCROLL_RETRY:
                    logger.debug("maximum retry reached")
                    return

                retry += 1
            else:
                retry = 0

            last_len_image_items = len_image_items

            logger.debug(f"limit : {limit} - len_image_items : len_image_items")

            if limit <= len_image_items:
                return

            data_status = int(bottom_tag.get_attribute("data-status"))

            logger.debug(f"data_status : {data_status}")

            if data_status == 1:  # Some images are loading
                time.sleep(0.75)

    def close(self):
        try:
            self.driver.quit()
        except MaxRetryError as e:
            logger.debug(f"Driver seems to be already closed - e : {e}")


def download_item(index, query, query_destination, image_url, preview_src, resize, file_format, pbar=None):
    image = None

    if image_url:
        image = download_image(index, image_url)  # Try to download image_url

    if not image:  # Download with image_url failed or no image_url, download the preview image
        logger.debug(f"[{index}] -> download with image_url failed, try to download the preview")
        image = download_preview(index, preview_src)

    if not image:
        logger.debug(f"[{index}] -> Can't download none of image_url and preview_src")
        return

    save_image(index, image, query, query_destination, resize, file_format)

    if pbar:
        pbar.update(1)


def download_preview(index, preview_src):
    if preview_src.startswith("http"):
        logger.debug(f"[{index}] -> preview_src is URL")
        return download_image(index, preview_src)  # Try to download preview_src
    else:
        logger.debug(f"[{index}] -> preview_src is data")
        return Image.open(BytesIO(base64.b64decode(
            preview_src.replace("data:image/png;base64,", "").replace("data:image/jpeg;base64,", ""))))


def save_image(index, image, query, query_destination, resize, file_format):
    logger.debug(f"[{index}] -> image.format : {image.format}")
    logger.debug(f"[{index}] -> image.mode : {image.mode}")

    # Standardise downloaded image format
    if image.format == "PNG":
        image = image.convert("RGBA")  # Force image mode to RGBA (convert P, L modes)
        image_extension = ".png"
    else:
        image = image.convert("RGB")
        image_extension = ".jpg"

    # Re-format image
    if file_format == "PNG":
        image = image.convert("RGBA")  # Force image mode to RGBA (convert P, L modes)
        image_extension = ".png"
    elif file_format == "JPEG":
        image = image.convert("RGB")
        image_extension = ".jpg"

    if resize is not None:
        image = image.resize(resize)

    image_name = query.replace(" ", "_") + "_" + str(index) + image_extension
    complete_file_name = os.path.join(query_destination, image_name)

    image.save(complete_file_name, file_format)
    image.close()

    logger.debug(f"[{index}] -> file downloaded : {complete_file_name}")


def download_image(index, image_url):
    image = download_image_with_requests(index, image_url)

    # Some downloads failed with requests but works with urllib
    if image is None:
        logger.debug(
            f"[{index}] -> download_image_with_requests failed, try with download_image_with_urllib - image_url : {image_url}")
        image = download_image_with_urllib(index, image_url)

    return image


def download_image_with_requests(index, image_url):
    logger.debug(f"[{index}] -> Try to download_image_with_requests - image_url : {image_url}")
    image = None

    try:
        response = requests.get(image_url, allow_redirects=True, timeout=30)

        if response.status_code == 200:
            logger.debug(f"[{index}] -> Successfully get image_bytes")
            image = Image.open(BytesIO(response.content))
        else:
            logger.debug(
                f"[{index}] -> Failed to download - request.status_code : {response.status_code}")
    except Exception as e:  # requests.exceptions.SSLError, PIL.UnidentifiedImageError
        logger.debug(
            f"[{index}] -> Exception : {e}")

    return image


def download_image_with_urllib(index, image_url):
    logger.debug(f"[{index}] -> Try to download_image_with_urllib - image_url : {image_url}")
    image = None

    try:
        with urllib.request.urlopen(image_url, timeout=30) as response:
            if response.status == 200:
                logger.debug(f"[{index}] -> Successfully get image_bytes")
                image = Image.open(BytesIO(response.read()))
            else:
                logger.debug(
                    f"[{index}] -> Failed to download - request.status_code : {response.status}")
    except Exception as e:  # urllib.request.HTTPError
        logger.debug(
            f"[{index}] -> Exception : {e}")

    return image


def enable_logs():
    # Useful if multiple downloader are created
    while len(logger.handlers) > 0:
        logger.removeHandler(logger.handlers[0])

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter("%(asctime)s - %(funcName)s - %(message)s", "%H:%M:%S"))

    logger.addHandler(stream_handler)
