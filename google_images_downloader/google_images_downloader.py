import os
import grequests
from concurrent.futures import ThreadPoolExecutor, wait
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from PIL import Image
import logging
from fake_useragent import UserAgent
from selenium.common.exceptions import TimeoutException
import base64
from io import BytesIO
from tqdm import tqdm
import time

DEFAULT_DESTINATION = "downloads"
DEFAULT_LIMIT = 50
DEFAULT_RESIZE = None
DEFAULT_QUIET = False
DEFAULT_DEBUG = False
DEFAULT_SHOW = False
DEFAULT_FORMAT = None
DEFAULT_WEBDRIVER_WAIT_DURATION = 20
DEFAULT_BROWSER = "chrome"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

user_agent = UserAgent().chrome
headers = {'User-Agent': str(user_agent)}

WEBDRIVER_WAIT_DURATION = DEFAULT_WEBDRIVER_WAIT_DURATION


class GoogleImagesDownloader:
    def __init__(self, browser=DEFAULT_BROWSER, show=DEFAULT_SHOW, debug=DEFAULT_DEBUG, quiet=DEFAULT_QUIET):
        logger.debug(f"browser : {browser}")
        logger.debug(f"show : {show}")
        logger.debug(f"debug : {debug}")
        logger.debug(f"quiet : {quiet}")

        self.quiet = quiet

        if debug:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(funcName)s - %(message)s', "%H:%M:%S"))

            logger.addHandler(stream_handler)

            self.quiet = True  # If enable debug logs, disable progress bar

        if quiet:
            self.quiet = True

        if browser == DEFAULT_BROWSER:  # chrome
            options = webdriver.ChromeOptions()

            if not show:
                options.add_argument("-headless")

            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_experimental_option('excludeSwitches', ['enable-logging'])

            self.driver = webdriver.Chrome(options=options)
        elif browser == "firefox":
            options = webdriver.FirefoxOptions()

            if not show:
                options.add_argument("-headless")

            self.driver = webdriver.Firefox(options=options,
                                            service=webdriver.FirefoxService(log_output=os.devnull))

        self.__consent()

        self.__disable_safeui()

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
            WebDriverWait(self.driver, WEBDRIVER_WAIT_DURATION).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='list']"))
            )
        except TimeoutException:
            if not self.quiet:
                print("No results")
            return

        self.__scroll(limit)

        self.driver.execute_script(
            "document.getElementsByClassName('qs41qe')[0].style.display = 'none'")  # Fix firefox issue, when click on item after scrolling

        list_items = WebDriverWait(self.driver, WEBDRIVER_WAIT_DURATION).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='list']"))
        )

        image_items = list_items.find_elements(By.CSS_SELECTOR, "div[role='listitem']")

        if not self.quiet:
            print("Downloading...")

        downloads_count = len(image_items) if limit > len(image_items) else limit

        if self.quiet:
            self.__download_items(query, destination, image_items, resize, limit, file_format)
        else:
            with tqdm(total=downloads_count) as pbar:
                self.__download_items(query, destination, image_items, resize, limit, file_format, pbar=pbar)

    def __download_items(self, query, destination, image_items, resize, limit, file_format, pbar=None):
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_list = list()

            for index, image_item in enumerate(image_items):
                image_url, preview_src = self.__get_image_values(image_item)

                query_destination = os.path.join(destination, query)

                future_list.append(
                    executor.submit(download_image, index, query, query_destination, image_url, preview_src,
                                    resize, file_format, pbar=pbar))
                """
                download_image(index, query, query_destination, image_url, preview_src,
                               resize, file_format, pbar=pbar)
                """
                if index + 1 == limit:
                    break

                wait(future_list)

    def __get_image_values(self, image_item):
        preview_src_tag = None

        while not preview_src_tag:  # Sometimes image part is not displayed the first time
            self.driver.execute_script("arguments[0].scrollIntoView(true);", image_item)

            WebDriverWait(self.driver, WEBDRIVER_WAIT_DURATION).until(EC.element_to_be_clickable(image_item)).click()

            try:
                preview_src_tag = WebDriverWait(self.driver, WEBDRIVER_WAIT_DURATION).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div[jsname='CGzTgf'] div[jsname='figiqf'] img"))
                )
            except TimeoutException:
                logger.debug("can't reach images tag...retry")
                pass

        preview_src = preview_src_tag.get_attribute("src")

        image_url = None

        try:
            image_url = WebDriverWait(self.driver, WEBDRIVER_WAIT_DURATION).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "img[jsname='kn3ccd']"))
            ).get_attribute("src")
        except TimeoutException:  # No image available
            logger.debug("can't retrieve image_url")

        return image_url, preview_src

    def __disable_safeui(self):
        self.driver.get(f"https://www.google.com/search?q=google&tbm=isch")

        href = WebDriverWait(self.driver, WEBDRIVER_WAIT_DURATION).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.cj2HCb div[jsname='ibnC6b'] a"))
        ).get_attribute("href")

        href = href.replace("&prev=https://www.google.com/search?q%3Dgoogle%26tbm%3Disch", "").replace("safeui=on",
                                                                                                       "safeui=off")
        logger.debug(f"href : {href}")

        self.driver.get(href)

    def __consent(self):
        self.driver.get("https://www.google.com/")  # To add cookie with domain .google.com

        self.driver.add_cookie(
            {'domain': '.google.com', 'expiry': 1726576871, 'httpOnly': False, 'name': 'SOCS', 'path': '/',
             'sameSite': 'Lax', 'secure': False, 'value': 'CAESHAgBEhJnd3NfMjAyMzA4MTUtMF9SQzQaAmZyIAEaBgiAjICnBg'})

        self.driver.add_cookie(
            {'domain': 'www.google.com', 'expiry': 1695040872, 'httpOnly': False, 'name': 'OTZ', 'path': '/',
             'sameSite': 'Lax', 'secure': True, 'value': '7169081_48_52_123900_48_436380'})

    def __scroll(self, limit):
        if not self.quiet:
            print("Scrolling...")

        bottom_tag = WebDriverWait(self.driver, WEBDRIVER_WAIT_DURATION).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[jsname='wEwttd'][data-status='5']"))
        )

        display_more_tag = self.driver.find_element(By.CSS_SELECTOR, 'input[jsaction="Pmjnye"]')

        data_status = int(bottom_tag.get_attribute("data-status"))

        list_items = WebDriverWait(self.driver, WEBDRIVER_WAIT_DURATION).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='list']"))
        )

        while data_status != 3:
            if display_more_tag.is_displayed() and display_more_tag.is_enabled():
                display_more_tag.click()

            self.driver.execute_script("arguments[0].scrollIntoView(true);", bottom_tag)

            image_items = list_items.find_elements(By.CSS_SELECTOR, "div[role='listitem']")

            logger.debug(f"limit : {limit} - len(image_items) : {len(image_items)}")

            if limit <= len(image_items):
                return

            data_status = int(bottom_tag.get_attribute("data-status"))

            logger.debug(f"data_status : {data_status}")


def download_image(index, query, query_destination, image_url, preview_src, resize, file_format, pbar=None):
    image_bytes = None

    logger.debug(f"[{index}] -> image_url : {image_url}")

    if image_url:
        image_bytes = download_image_aux(image_url)  ## Try to download image_url

    if not image_bytes:  # Download failed, download the preview image
        logger.debug(f"[{index}] -> download with image_url failed, try to download the preview")

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

    logger.debug(f"[{index}] -> file downloaded : {complete_file_name}")

    if pbar:
        pbar.update(1)


def download_image_aux(image_url):
    logger.debug(f"Try to download - image_url : {image_url}")
    image_bytes = None

    request = grequests.get(image_url, headers=headers)
    result = grequests.map([request])[0]

    if result.status_code == 200:
        image_bytes = result.content
        logger.debug(f"Successfully get image_bytes with request - image_url : {image_url}")
    else:
        logger.debug(
            f"Failed to download with request - request.status_code : {result.status_code} - image_url : {image_url}")
    """
    except requests.exceptions.SSLError:  # If requests.get failed, try with urllib
        logger.debug(f"Failed to download with request, try with urllib - image_url : {image_url}")
        try:
            request = urllib.request.Request(image_url, headers=headers)
            image_bytes = urllib.request.urlopen(request).read()
            logger.debug(f"Successfully get image_bytes with urllib - image_url : {image_url}")
        except HTTPError:
            logger.debug(f"Failed to download with urllib - image_url : {image_url}")

    except requests.exceptions.ChunkedEncodingError:
        logger.debug(f"Failed to download with request, try with urllib - image_url : {image_url}")
        try:
            request = urllib.request.Request(image_url, headers=headers)
            image_bytes = urllib.request.urlopen(request).read()
            logger.debug(f"Successfully get image_bytes with urllib - image_url : {image_url}")
        except HTTPError:
            logger.debug(f"Failed to download with urllib - image_url : {image_url}")
    """
    return image_bytes


if __name__ == "__main__":
    downloader = GoogleImagesDownloader(show=True, debug=True)

    time.sleep(3000)

    downloader.driver.close()
