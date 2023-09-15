import argparse
import re
import os

try:  # Normal way
    from gid import DEFAULT_DESTINATION, DEFAULT_LIMIT, DEFAULT_RESIZE, DEFAULT_QUIET, DEFAULT_DEBUG, DEFAULT_SHOW, \
        DEFAULT_FORMAT, DEFAULT_DISABLE_SAFEUI, DEFAULT_WEBDRIVER_WAIT_DURATION, DEFAULT_BROWSER
except ImportError:  # For main tests
    from .gid import DEFAULT_DESTINATION, DEFAULT_LIMIT, DEFAULT_RESIZE, DEFAULT_QUIET, DEFAULT_DEBUG, DEFAULT_SHOW, \
        DEFAULT_FORMAT, DEFAULT_DISABLE_SAFEUI, DEFAULT_WEBDRIVER_WAIT_DURATION, DEFAULT_BROWSER

try:  # Normal way
    from __dist_version__old import __version__
except ImportError:  # For tests
    from .__dist_version__old import __version__


def get_arguments(arguments):
    parser = argparse.ArgumentParser(
        description="Script to download images from a \"Google Images\" query",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-q",
        "--queries",
        help="Google Images queries" + os.linesep +
             "example (single)   : google-images-downloader -q cat" + os.linesep +
             "example (multiple) : google-images-downloader -q cat dog \"red car\"",
        nargs='+',
        required=True
    )

    parser.add_argument(
        "-d",
        "--destination",
        help="download destination" + os.linesep +
             "example : google-images-downloader -d C:\\my\\download\\destination" + os.linesep +
             "(default: %(default)s)",
        default=DEFAULT_DESTINATION
    )

    parser.add_argument(
        "-l",
        "--limit",
        help="maximum number of images downloaded" + os.linesep +
             "Google Images is returning ~600 images maximum" + os.linesep +
             "use a big number like 9999 to download every images" + os.linesep +
             "example : google-images-downloader -l 400" + os.linesep +
             "(default: %(default)s)",
        default=DEFAULT_LIMIT,
        type=int
    )

    parser.add_argument(
        "-r",
        "--resize",
        help="resize downloaded images to specified dimension at format <width>x<height>" + os.linesep +
             "by default, images are not resized" + os.linesep +
             "example : google-images-downloader -r 256x256" + os.linesep +
             "(default: %(default)s)",
        default=DEFAULT_RESIZE,
        type=get_formatted_resize,
    )

    parser.add_argument(
        "-f",
        "--format",
        help="format download images to specified format" + os.linesep +
             "by default, images keep their default format" + os.linesep +
             "example : google-images-downloader -f PNG" + os.linesep +
             "(default: %(default)s)",
        default=DEFAULT_FORMAT,
        choices=["JPEG", "PNG"])

    parser.add_argument(
        "-b",
        "--browser",
        help="specify browser to use for web scraping" + os.linesep +
             "example : google-images-downloader -b firefox" + os.linesep +
             "(default: %(default)s)",
        default=DEFAULT_BROWSER,
        choices=["chrome", "firefox"])

    parser.add_argument(
        "-s",
        "--show",
        help="show the browser by disabling headless option" + os.linesep +
             "useful for debugging" + os.linesep +
             "example : google-images-downloader -s",
        action="store_true",
        default=DEFAULT_SHOW
    )

    parser.add_argument(
        "-D",
        "--debug",
        help="enable debug logs, disable progression bar and messages" + os.linesep +
             "example : google-images-downloader -D",
        action="store_true",
        default=DEFAULT_DEBUG
    )

    parser.add_argument(
        "-Q",
        "--quiet",
        help="disable program output" + os.linesep +
             "example : google-images-downloader -Q",
        action="store_true",
        default=DEFAULT_QUIET
    )

    parser.add_argument(
        "-w",
        "--wait_duration",
        help="webdriver wait duration in seconds" + os.linesep +
             "example : google-images-downloader -w 100" + os.linesep +
             "(default: %(default)s)",
        default=DEFAULT_WEBDRIVER_WAIT_DURATION,
        type=int
    )

    parser.add_argument(
        "-S",
        "--disable_safeui",
        help="Disable safeui (blurred images)" + os.linesep +
             "example : google-images-downloader -S",
        action="store_true",
        default=DEFAULT_DISABLE_SAFEUI
    )

    parser.add_argument(
        "-v",
        "--version",
        help="Show google-images-downloader version",
        action="version"
    )

    parser.version = __version__

    return parser.parse_args(arguments)


def get_formatted_resize(resize):
    formatted_resize = None

    if resize is not None:
        if re.match('^[0-9]+x[0-9]+$', resize) is None:
            raise argparse.ArgumentTypeError(f"Invalid size format : {resize}" + os.linesep +
                                             "Expected format example : 256x256")
        else:
            formatted_resize = [int(x) for x in resize.split("x")]

    return formatted_resize
