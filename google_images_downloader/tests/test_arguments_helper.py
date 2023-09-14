import pytest

import google_images_downloader

from ..helpers.arguments_helper import get_arguments

DESTINATIONS = ["downloads_tests_" + str(index) for index in
                range(0, 5)]
LIMITS = [10, 20, 75, 100, 200, 300]
RESIZE_FORMATS = [
    "64x64",
    "256x256",
    "512x512",
    "1024x1024",
    "3840x2160",
    "197x302",
    "415x213"
]

INVALID_RESIZE_FORMATS = [
    "64.64",
    "256256",
    "512xx512"
    "x1024"
    "3840x",
    "197x302x402"
]
REQUIRED_QUERY = ["-q", "cat"]
QUERIES_GROUP = [
    ["cat"],
    ["cat", "dog"],
    ["cat", "dog", "fish"],
    ["cat", "dog", "fish", "red car"],
]

FILE_FORMATS = ["JPEG", "PNG"]
INVALID_FILE_FORMATS = ["AVI", "JSON", "EXE"]

BROWSERS = ["chrome", "firefox"]
UNSUPPORTED_BROWSERS = ["opera", "safari", "internet explorer", "edge"]

WAIT_DURATIONS = ["10", "20", "40", "100", "200"]


def test_get_arguments_single_query():
    arguments = get_arguments(REQUIRED_QUERY)

    assert arguments.queries == ["cat"]


@pytest.mark.parametrize("queries", QUERIES_GROUP)
def test_get_arguments_multiple_queries(queries):
    arguments = get_arguments(["-q"] + queries)

    assert arguments.queries == queries


@pytest.mark.parametrize("destination", DESTINATIONS)
def test_get_arguments_destination(destination):
    arguments = get_arguments(REQUIRED_QUERY + ["-d", destination])

    assert arguments.destination == destination


@pytest.mark.parametrize("resize", RESIZE_FORMATS)
def test_get_arguments_resize(resize):
    arguments = get_arguments(REQUIRED_QUERY + ["-r", resize])

    assert arguments.resize == [int(x) for x in resize.split("x")]


@pytest.mark.parametrize("resize", INVALID_RESIZE_FORMATS)
def test_get_arguments_resize_invalid(resize):
    error_raised = False

    try:
        get_arguments(REQUIRED_QUERY + ["-r", resize])
    except SystemExit:
        error_raised = True

    assert error_raised


@pytest.mark.parametrize("file_format", FILE_FORMATS)
def test_get_arguments_format(file_format):
    arguments = get_arguments(REQUIRED_QUERY + ["-f", file_format])

    assert arguments.format == file_format


@pytest.mark.parametrize("file_format", INVALID_FILE_FORMATS)
def test_get_arguments_format_invalid(file_format):
    error_raised = False

    try:
        get_arguments(REQUIRED_QUERY + ["-f", file_format])
    except SystemExit:
        error_raised = True

    assert error_raised


@pytest.mark.parametrize("browser", BROWSERS)
def test_get_arguments_browser(browser):
    arguments = get_arguments(REQUIRED_QUERY + ["-b", browser])

    assert arguments.browser == browser


@pytest.mark.parametrize("browser", UNSUPPORTED_BROWSERS)
def test_get_arguments_browser_unsupported(browser):
    error_raised = False

    try:
        get_arguments(REQUIRED_QUERY + ["-b", browser])
    except SystemExit:
        error_raised = True

    assert error_raised


def test_get_arguments_show():
    arguments = get_arguments(REQUIRED_QUERY + ["-s"])

    assert arguments.show


def test_get_arguments_debug():
    arguments = get_arguments(REQUIRED_QUERY + ["-D"])

    assert arguments.debug


def test_get_arguments_quiet():
    arguments = get_arguments(REQUIRED_QUERY + ["-Q"])

    assert arguments.quiet


@pytest.mark.parametrize("wait_duration", WAIT_DURATIONS)
def test_get_arguments_wait_duration(wait_duration):
    arguments = get_arguments(REQUIRED_QUERY + ["-w", wait_duration])

    assert arguments.wait_duration == int(wait_duration)


def test_get_arguments_disable_safeui():
    arguments = get_arguments(REQUIRED_QUERY + ["-S"])

    assert arguments.disable_safeui


def test_get_arguments_default_values():
    arguments = get_arguments(["-q", "cat"])

    assert arguments.destination == google_images_downloader.DEFAULT_DESTINATION
    assert arguments.limit == google_images_downloader.DEFAULT_LIMIT
    assert arguments.resize == google_images_downloader.DEFAULT_RESIZE
    assert arguments.format == google_images_downloader.DEFAULT_FORMAT
    assert arguments.browser == google_images_downloader.DEFAULT_BROWSER
    assert arguments.show == google_images_downloader.DEFAULT_SHOW
    assert arguments.debug == google_images_downloader.DEFAULT_DEBUG
    assert arguments.quiet == google_images_downloader.DEFAULT_QUIET
    assert arguments.wait_duration == google_images_downloader.DEFAULT_WEBDRIVER_WAIT_DURATION
    assert arguments.disable_safeui == google_images_downloader.DEFAULT_DISABLE_SAFEUI


def test_get_arguments_missing_required():
    try_to_exit = False

    try:
        get_arguments([])
    except SystemExit as e:
        try_to_exit = True

    assert try_to_exit
