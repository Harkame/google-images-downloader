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

IMAGE_HEIGHT = 180

ua = UserAgent()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

ch.setFormatter(formatter)

logger.addHandler(ch)

opener = urllib.request.URLopener()
opener.addheader('User-Agent', 'whatever')
headers = {'User-Agent': str(ua.chrome)}


class GoogleImagesDownloader:
    def __init__(self, download_destination="downloads", image_size=None, limit=10):
        self.image_size = image_size
        self.limit = limit

        self.download_destination = download_destination

        options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")

        self.driver = webdriver.Chrome(options=options, service=webdriver.ChromeService(executable_path=binary_path))

        self.__consent()

    def download(self, query):
        query_destination_folder = os.path.join(self.download_destination, query)
        os.makedirs(query_destination_folder, exist_ok=True)

        self.driver.get(f"https://www.google.com/search?q={query}&tbm=isch")

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='list']"))
        )

        self.__disable_saveui()

        list_items = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='list']"))
        )

        image_items = list_items.find_elements(By.CSS_SELECTOR, "div[role='listitem']")

        self.__scroll()

        with tqdm(total=self.limit) as pbar:
            for index, image_item in enumerate(image_items):
                logger.debug(f"index : {index}")
                WebDriverWait(self.driver, 20).until(
                    EC.element_to_be_clickable(image_item)).click()

                image_url = None
                image_bytes = None

                complete_file_name = os.path.join(query_destination_folder,
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

                with open(complete_file_name, 'wb') as handler:
                    if image_url is not None:
                        try:
                            handler.write(requests.get(
                                image_url,
                                headers=headers).content)
                        except requests.exceptions.SSLError:
                            opener.retrieve(image_url, complete_file_name)  # Try to download image with urllib

                image = None

                if image_url is not None:
                    image = Image.open(complete_file_name)
                else:
                    image = Image.open(BytesIO(image_bytes))

                if image.mode != 'RGB':
                    image = image.convert('RGB')

                if self.image_size is not None:
                    image = image.resize(self.image_size)

                image.save(complete_file_name, "jpeg")

                pbar.update(1)

                if index + 1 == self.limit:
                    return

    def __disable_saveui(self):
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

    def __scroll(self):
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

            if loaded_images >= self.limit:
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


if __name__ == "__main__":
    downloader = GoogleImagesDownloader(limit=999)

    downloader.download("cat")
