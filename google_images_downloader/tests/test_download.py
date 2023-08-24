import unittest
import os
import shutil
import pytest
from PIL import Image

from ..google_images_downloader import GoogleImagesDownloader, DEFAULT_LIMIT

QUERY = "cat"
DESTINATION = "downloads_tests"
ANOTHER_DESTINATION = "downloads_tests_bis"
LIMIT = 100
MAX_LIMIT = 9999
RESIZE = (256, 256)


@pytest.fixture(autouse=True)
def resource():
    yield
    shutil.rmtree(DESTINATION, ignore_errors=True)
    shutil.rmtree(ANOTHER_DESTINATION, ignore_errors=True)


class TestDownload(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestDownload, self).__init__(*args, **kwargs)

        self.downloader = GoogleImagesDownloader()

    def test_download(self):
        self.downloader.download(QUERY, destination=DESTINATION)

        files = os.listdir(os.path.join(DESTINATION, QUERY))

        self.assertEqual(DEFAULT_LIMIT, len(files))

    def test_download_second_destination(self):
        self.downloader.download(QUERY, destination=ANOTHER_DESTINATION)

        files = os.listdir(os.path.join(ANOTHER_DESTINATION, QUERY))

        self.assertEqual(DEFAULT_LIMIT, len(files))

    def test_download_limit(self):
        self.downloader.download(QUERY, destination=DESTINATION, limit=LIMIT)

        files = os.listdir(os.path.join(DESTINATION, QUERY))

        self.assertEqual(LIMIT, len(files))

    @pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                        reason="Skipping this test on Travis CI, because of timeout")
    def test_download_no_limit(self):
        self.downloader.download(QUERY, destination=DESTINATION,
                                 limit=MAX_LIMIT)

        files = os.listdir(os.path.join(DESTINATION, QUERY))

        self.assertNotEquals(MAX_LIMIT, len(files))  # Google Images returns ~600 images maximum

    def test_download_resize(self):
        self.downloader.download(QUERY, destination=DESTINATION, resize=RESIZE)

        files = os.listdir(os.path.join(DESTINATION, QUERY))
        for file in files:
            image = Image.open(os.path.join(DESTINATION, QUERY, file))

            self.assertEqual(image.size, RESIZE)
