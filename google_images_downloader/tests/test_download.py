import os
import shutil
from PIL import Image
import pytest

from ..google_images_downloader import GoogleImagesDownloader, DEFAULT_LIMIT, download_image, \
    download_image_with_requests, \
    download_image_with_urllib

QUERY = "cat"
ANOTHER_QUERIES = ["dog", "fish", "bird", "car", "fruit"]
QUERY_WITHOUT_RESULTS = "77af778b51abd4a3c51c5ddd97204a9c3ae614ebccb75a606c3b6865aed6744e azerty"
DESTINATION = "downloads_tests"
ANOTHER_DESTINATIONS = ["downloads_tests_" + str(index) for index in
                        range(0, 5)]  # Create multiple another destinations
RESIZE_FORMATS = [
    (64, 64),
    (256, 256),
    (512, 512),
    (1024, 1024),
    (3840, 2160),
    (197, 302),
    (415, 213)
]
FILE_FORMATS = ["JPEG", "PNG"]
LIMITS = [10, 20, 75, 100, 200, 300]
NO_LIMIT = 9999
IMAGE_URL_FAIL_WITH_REQUESTS = "https://www.hindustantimes.com/ht-img/img/2023/08/25/1600x900/international_dog_day_1692974397743_1692974414085.jpg"


def remove_download_folders():
    shutil.rmtree(DESTINATION, ignore_errors=True)

    for another_destination in ANOTHER_DESTINATIONS:
        shutil.rmtree(another_destination, ignore_errors=True)


def test_download_fail_with_requests():
    image_bytes = download_image_with_requests(0, IMAGE_URL_FAIL_WITH_REQUESTS)

    assert not image_bytes


def test_download_works_with_urllib():
    image_bytes = download_image_with_urllib(0, IMAGE_URL_FAIL_WITH_REQUESTS)

    assert image_bytes


def test_download_fail_with_requests_2():
    image_bytes = download_image(0, IMAGE_URL_FAIL_WITH_REQUESTS)

    assert image_bytes


class BaseTestDownload:
    downloader = None
    browser = None

    def test_download(self):
        self.downloader.download(QUERY, destination=DESTINATION)

        files = os.listdir(os.path.join(DESTINATION, QUERY))

        assert len(files) == DEFAULT_LIMIT

    """
    @pytest.mark.parametrize("query", ANOTHER_QUERIES)
    def test_download_another_query(self, query):
        self.downloader.download(query, destination=DESTINATION)

        files = os.listdir(os.path.join(DESTINATION, query))

        assert len(files) == DEFAULT_LIMIT


    def test_download_no_results(self):
        self.downloader.download(QUERY_WITHOUT_RESULTS, destination=DESTINATION)

        files = os.listdir(os.path.join(DESTINATION, QUERY_WITHOUT_RESULTS))

        assert len(files) == 0

    @pytest.mark.parametrize("destination", ANOTHER_DESTINATIONS)
    def test_download_another_destination(self, destination):
        self.downloader.download(QUERY, destination=destination)

        files = os.listdir(os.path.join(destination, QUERY))

        assert len(files) == DEFAULT_LIMIT

    @pytest.mark.parametrize("limit", LIMITS)
    def test_download_limit(self, limit):
        self.downloader.download(QUERY, destination=DESTINATION, limit=limit)

        files = os.listdir(os.path.join(DESTINATION, QUERY))

        assert len(files) == limit

    def test_download_no_limit(self):
        self.downloader.download(QUERY, destination=DESTINATION,
                                 limit=NO_LIMIT)

        files = os.listdir(os.path.join(DESTINATION, QUERY))

        assert len(files) < NO_LIMIT  # Google Images returns ~600 images maximum

    @pytest.mark.parametrize("resize", RESIZE_FORMATS)
    def test_download_resize(self, resize):
        self.downloader.download(QUERY, destination=DESTINATION, resize=resize)

        files = os.listdir(os.path.join(DESTINATION, QUERY))
        for file in files:
            image = Image.open(os.path.join(DESTINATION, QUERY, file))

            assert image.size == resize

    @pytest.mark.parametrize("file_format", FILE_FORMATS)
    def test_download_format_format(self, file_format):
        self.downloader.download(QUERY, destination=DESTINATION, file_format=file_format)

        files = os.listdir(os.path.join(DESTINATION, QUERY))
        for file in files:
            file_extension = os.path.splitext(file)[1]

            if file_format == "JPEG":
                assert file_extension == ".jpg"
            elif file_format == "PNG":
                assert file_extension == ".png"

            image = Image.open(os.path.join(DESTINATION, QUERY, file))
            assert image.format == file_format

            if file_format == "JPEG":
                assert file_extension == ".jpg"
            elif file_format == "PNG":
                assert file_extension == ".png"

    def test_not_quiet_download(self, capsys):
        self.downloader.close()
        self.downloader = GoogleImagesDownloader(browser=self.browser)
        self.downloader.download(QUERY, destination=DESTINATION)

        captured = capsys.readouterr()
        assert captured.out != ""
        assert captured.err != ""

    def test_quiet_download(self, capsys):
        self.downloader.close()
        self.downloader = GoogleImagesDownloader(browser=self.browser, quiet=True)
        self.downloader.download(QUERY, destination=DESTINATION)

        captured = capsys.readouterr()
        assert captured.out == ""
        assert captured.err == ""
    """

    @pytest.fixture(autouse=True)
    def resource(self):
        remove_download_folders()

        self.downloader = GoogleImagesDownloader(browser=self.browser)

        yield

        remove_download_folders()

        self.downloader.close()


"""


class TestDownloadChrome(BaseTestDownload):
    browser = "chrome"


"""


class TestDownloadFirefox(BaseTestDownload):
    browser = "firefox"
