import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, wait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from PIL import Image
from chromedriver_py import binary_path
import urllib.request
import logging
import requests
from fake_useragent import UserAgent
from selenium.common.exceptions import TimeoutException
import base64
from io import BytesIO
from tqdm import tqdm
from urllib.request import HTTPError
from selenium.webdriver.common.action_chains import ActionChains
from pygeckodriver import geckodriver_path

DEFAULT_DESTINATION = "downloads"
DEFAULT_LIMIT = 50
DEFAULT_RESIZE = None
DEFAULT_QUIET = False
DEFAULT_DEBUG = False
DEFAULT_FORMAT = None

DEFAULT_BROWSER = "chrome"

IMAGE_HEIGHT = 180

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

user_agent = UserAgent().chrome
headers = {'User-Agent': str(user_agent)}


class GoogleImagesDownloader:
    def __init__(self, browser=DEFAULT_BROWSER, show=False):
        self.quiet = DEFAULT_QUIET

        if browser == DEFAULT_BROWSER: #chrome
            options = webdriver.ChromeOptions()

            if not show:
                options.headless = True

            options.add_experimental_option('excludeSwitches', ['enable-logging'])

            self.driver = webdriver.Chrome(options=options, service=webdriver.ChromeService(executable_path=binary_path))
        elif browser == "firefox":
            options = webdriver.FirefoxOptions()

            if not show:
                options.headless = True

            self.driver = webdriver.Firefox(options=options, service=webdriver.ChromeService(executable_path=geckodriver_path))

        self.__consent()

    def init_arguments(self, arguments):
        if arguments.debug:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', "%H:%M:%S"))

            logger.addHandler(stream_handler)

            self.quiet = True  # If enable debug logs, disable progress bar

        if arguments.quiet:
            self.quiet = True

    def download(self, query, destination=DEFAULT_DESTINATION, limit=DEFAULT_LIMIT,
                 resize=DEFAULT_RESIZE, format=DEFAULT_FORMAT):
        query_destination_folder = os.path.join(destination, query)
        os.makedirs(query_destination_folder, exist_ok=True)

        self.driver.get(f"https://www.google.com/search?q={query}&tbm=isch")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='list']"))
        )

        self.__disable_safeui()

        list_items = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='list']"))
        )

        self.__scroll(limit)

        image_items = list_items.find_elements(By.CSS_SELECTOR, "div[role='listitem']")

        if not self.quiet:
            print("Downloads...")

        downloads_count = len(image_items) if limit > len(image_items) else limit

        if self.quiet:
            self.__download_items(query, destination, image_items, resize, limit, format)
        else:
            with tqdm(total=downloads_count) as pbar:
                self.__download_items(query, destination, image_items, resize, limit, format, pbar=pbar)

    def __download_items(self, query, destination, image_items, resize, limit, format, pbar=None):
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_list = list()

            for index, image_item in enumerate(image_items):
                image_url, preview_src = self.__get_image_values(image_item)

                query_destination = os.path.join(destination, query)

                future_list.append(
                    executor.submit(download_image, index, query, query_destination, image_url, preview_src,
                                    resize, format, pbar=pbar))

                if index + 1 == limit:
                    break

            wait(future_list)

    def __scroll_shim(self, object):
        x = object.location['x']
        y = object.location['y']
        scroll_by_coord = 'window.scrollTo(%s,%s);' % (
            x,
            y
        )
        scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
        self.driver.execute_script(scroll_by_coord)
        self.driver.execute_script(scroll_nav_out_of_way)

    def __get_image_values(self, image_item):

        # Scroll to item it not working well on firefox
        # This functions seems to resolve the problem
        # https://stackoverflow.com/questions/44777053/selenium-movetargetoutofboundsexception-with-firefox
        if 'firefox' in self.driver.capabilities['browserName']:
            self.__scroll_shim(image_item)

        actions = ActionChains(self.driver)
        actions.move_to_element(image_item).perform()

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(image_item)).click()

        preview_src = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[jsname='CGzTgf'] div[jsname='figiqf'] img"))
        ).get_attribute("src")

        image_url = None

        try:
            image_url = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img[jsname='kn3ccd']"))
            ).get_attribute("src")
        except TimeoutException:  # No image available
            pass

        return image_url, preview_src

    def __disable_safeui(self):
        href = self.driver.find_element(By.CSS_SELECTOR, 'div.cj2HCb div[jsname="ibnC6b"] a').get_attribute("href")

        href = href.replace("safeui=on", "safeui=off")

        self.driver.get(href)

    def __consent(self):
        self.driver.get("https://www.google.com/")

        self.driver.add_cookie(
            {'domain': '.google.com', 'expiry': 1726576871, 'httpOnly': False, 'name': 'SOCS', 'path': '/',
             'sameSite': 'Lax', 'secure': False, 'value': 'CAESHAgBEhJnd3NfMjAyMzA4MTUtMF9SQzQaAmZyIAEaBgiAjICnBg'})

        self.driver.add_cookie(
            {'domain': 'www.google.com', 'expiry': 1695040872, 'httpOnly': False, 'name': 'OTZ', 'path': '/',
             'sameSite': 'Lax', 'secure': True, 'value': '7169081_48_52_123900_48_436380'})

    def __scroll(self, limit):
        if not self.quiet:
            print("Scrolling...")

        count = 0

        display_more = self.driver.find_element(By.CSS_SELECTOR, 'input[jsaction="Pmjnye"]')
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        scroll_try = 0

        loaded_images = 0

        while True:
            count += IMAGE_HEIGHT * 3
            self.driver.execute_script(f"window.scrollTo(0, {count});")
            loaded_images += 6

            time.sleep(1)

            if loaded_images >= limit:
                return

            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if display_more.is_displayed() and display_more.is_enabled():
                display_more.click()

            if last_height == new_height:
                scroll_try += 1
            else:
                scroll_try = 0

            if last_height == new_height and scroll_try > 10:
                break

            last_height = new_height


def download_image(index, query, query_destination, image_url, preview_src, resize, format, pbar=None):
    image_bytes = None

    logger.debug(f"[{index}] -> image_url : {image_url}")

    if image_url:
        image_bytes = download_image_aux(image_url)  ## Try to download image_url

    if not image_bytes:  # Download failed, download the preview image
        logger.debug(f"[{index}] -> Download with image_url failed, try to download the preview")

        if preview_src.startswith("http"):
            logger.debug(f"[{index}] -> preview_src is URL : {preview_src}")
            image_bytes = download_image_aux(preview_src)  # Download preview image
        else:
            logger.debug(f"[{index}] -> preview_src is bytes")
            image_bytes = base64.b64decode(
                preview_src.replace("data:image/png;base64,", "").replace("data:image/jpeg;base64,", ""))

    image = Image.open(BytesIO(image_bytes))

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
    if format == "PNG":
        image = image.convert("RGBA")  # Force image mode to RGBA (convert P, L modes)
        image_extension = ".png"
    elif format == "JPEG":
        image = image.convert("RGB")
        image_extension = ".jpg"

    if resize is not None:
        image = image.resize(resize)

    image_name = query.replace(" ", "_") + "_" + str(index) + image_extension
    complete_file_name = os.path.join(query_destination, image_name)

    image.save(complete_file_name, format)

    if pbar:
        pbar.update(1)


def download_image_aux(image_url):
    image_bytes = None

    try:
        request = requests.get(image_url, headers=headers)

        if request.status_code == 200:
            image_bytes = request.content
    except requests.exceptions.SSLError:  # If requests.get failed, try with urllib
        try:
            request = urllib.request.Request(image_url, headers=headers)
            image_bytes = urllib.request.urlopen(request).read()
        except HTTPError:
            pass

    return image_bytes
