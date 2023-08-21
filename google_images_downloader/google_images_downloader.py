import os
import time
import urllib.request
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

DEFAULT_DESTINATION = "downloads"
DEFAULT_LIMIT = 50
DEFAULT_RESIZE = None
DEFAULT_QUIET = False
DEFAULT_DEBUG = False

IMAGE_HEIGHT = 180

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

user_agent = UserAgent().chrome
headers = {'User-Agent': str(user_agent)}


class GoogleImagesDownloader:
    def __init__(self):
        self.quiet = DEFAULT_QUIET

        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")

        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        self.driver = webdriver.Chrome(options=options, service=webdriver.ChromeService(executable_path=binary_path))

        self.__consent()

    def init_arguments(self, arguments):
        if arguments.debug:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.DEBUG)
            stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

            logger.addHandler(stream_handler)

        self.quiet = arguments.quiet

    def download(self, query, destination=DEFAULT_DESTINATION, limit=DEFAULT_LIMIT,
                 resize=DEFAULT_RESIZE):
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

        with tqdm(total=limit) as pbar:
            if self.quiet:
                pbar.disable = True

            for index, image_item in enumerate(image_items):
                self.__download_item(query, index, image_item, destination, resize)
                pbar.update(1)

                if index + 1 == limit:
                    break

    def __download_item(self, query, index, image_item, destination, resize):
        logger.debug(f"index : {index}")

        actions = ActionChains(self.driver)
        actions.move_to_element(image_item).perform()

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(image_item)).click()

        image_url = None
        image_bytes = None

        complete_file_name = os.path.join(destination, query,
                                          query.replace(" ", "_") + "_" + str(index) + ".jpg")

        try:
            image_url = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img[jsname='kn3ccd']"))
            ).get_attribute("src")
        except TimeoutException:  # No image available, download the preview instead
            preview_src = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div[jsname='CGzTgf'] div[jsname='figiqf'] img"))
            ).get_attribute("src")

            logger.debug(f"preview_src : {preview_src}")

            if preview_src.startswith("http"):
                image_url = preview_src
            else:
                image_bytes = base64.b64decode(
                    preview_src.replace("data:image/png;base64,", "").replace("data:image/jpeg;base64,", ""))

        logger.debug(f"image_url : {image_url}")
        logger.debug(f"image_bytes : {image_bytes}")

        download_success = True

        with open(complete_file_name, 'wb') as handler:
            if image_url is not None:
                try:
                    request = requests.get(image_url, headers=headers)

                    if request.status_code == 200:
                        handler.write(request.content)
                    else:
                        download_success = False

                    logger.debug(f"requests get")
                except requests.exceptions.SSLError:
                    try:
                        request = urllib.request.Request(image_url, headers=headers)
                        handler.write(urllib.request.urlopen(request).read())
                        logger.debug(f"urllib retrieve")
                    except HTTPError:
                        logger.debug(f"download failed")
                        download_success = False

        if not download_success:
            os.remove(complete_file_name)
            return

        image = None

        if image_url is not None:
            image = Image.open(complete_file_name)
        else:
            image = Image.open(BytesIO(image_bytes))

        if image.mode != 'RGB':
            image = image.convert('RGB')

        if resize is not None:
            image = image.resize(resize)

        image.save(complete_file_name, "jpeg")

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
