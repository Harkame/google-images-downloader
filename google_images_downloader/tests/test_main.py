import pytest
import os
import shutil

import google_images_downloader.__main__
import google_images_downloader.gid as gid

DESTINATION = "downloads_tests"

QUERY = ["cat"]
QUERIES = ["cat", "dog", "red car"]


def remove_download_folders():
    shutil.rmtree(DESTINATION, ignore_errors=True)


def test_main_single_query():
    google_images_downloader.__main__.main(["-q"] + QUERY + ["-d", DESTINATION])

    assert set(QUERY) == set([f.name for f in os.scandir(DESTINATION) if f.is_dir()])

    files = os.listdir(os.path.join(DESTINATION, QUERY[0]))

    assert len(files) == gid.DEFAULT_LIMIT


def test_main_single_multiple_queries():
    google_images_downloader.__main__.main(["-q"] + QUERIES + ["-d", DESTINATION])

    assert set(QUERIES) == set([f.name for f in os.scandir(DESTINATION) if f.is_dir()])

    for query in QUERIES:
        files = os.listdir(os.path.join(DESTINATION, query))

        assert len(files) == gid.DEFAULT_LIMIT


@pytest.fixture(autouse=True)
def resource():
    remove_download_folders()

    yield

    remove_download_folders()
