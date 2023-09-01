import google_images_downloader
from google_images_downloader import GoogleImagesDownloader
import sys
import argparse
import os
import re


def get_arguments():
    argument_parser = argparse.ArgumentParser(
        description="Script to download images from a \"Google Images\" query",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    argument_parser.add_argument(
        "-q",
        "--query",
        help="Google Images query" + os.linesep +
             "example : google-images-downloader -q cat",
        required=True
    )

    argument_parser.add_argument(
        "-d",
        "--destination",
        help="download destination" + os.linesep +
             "example : google-images-downloader -d C:\\my\\download\\destination" + os.linesep +
             "(default: %(default)s)",
        default=google_images_downloader.DEFAULT_DESTINATION
    )

    argument_parser.add_argument(
        "-l",
        "--limit",
        help="maximum number of images downloaded" + os.linesep +
             "Google Images is returning ~600 images maximum" + os.linesep +
             "use a big number like 9999 to download every images" + os.linesep +
             "example : google-images-downloader -l 400" + os.linesep +
             "(default: %(default)s)",
        default=google_images_downloader.DEFAULT_LIMIT,
        type=int
    )

    argument_parser.add_argument(
        "-r",
        "--resize",
        help="resize downloaded images to specified dimension at format <width>x<height>" + os.linesep +
             "by default, images are not resized" + os.linesep +
             "example : google-images-downloader -r 256x256" + os.linesep +
             "(default: %(default)s)",
        default=google_images_downloader.DEFAULT_RESIZE,
    )

    argument_parser.add_argument(
        "-f",
        "--format",
        help="format download images to specified format" + os.linesep +
             "by default, images keep their default format" + os.linesep +
             "example : google-images-downloader -f PNG" + os.linesep +
             "(default: %(default)s)",
        default=google_images_downloader.DEFAULT_FORMAT,
        choices=["JPEG", "PNG"])

    argument_parser.add_argument(
        "-b",
        "--browser",
        help="specify browser to use for web scraping" + os.linesep +
             "example : google-images-downloader -b firefox" + os.linesep +
             "(default: %(default)s)",
        default=google_images_downloader.DEFAULT_BROWSER,
        choices=["chrome", "firefox"])

    argument_parser.add_argument(
        "-s",
        "--show",
        help="show the browser by disabling headless option" + os.linesep +
             "useful for debugging" + os.linesep +
             "example : google-images-downloader -s",
        action="count"
    )

    argument_parser.add_argument(
        "-D",
        "--debug",
        help="enable debug logs, disable progression bar and messages" + os.linesep +
             "example : google-images-downloader -D",
        action="count"
    )

    argument_parser.add_argument(
        "-Q",
        "--quiet",
        help="disable program output" + os.linesep +
             "example : google-images-downloader -Q",
        action="count"
    )

    argument_parser.add_argument(
        "-w",
        "--wait_duration",
        help="webdriver wait duration in seconds" + os.linesep +
             "example : google-images-downloader -w 30" + os.linesep +
             "(default: %(default)s)",
        default=google_images_downloader.DEFAULT_WEBDRIVER_WAIT_DURATION,
        type=int
    )

    return argument_parser.parse_args(sys.argv[1:])


def get_formatted_resize(resize):
    formatted_resize = None

    if resize is not None:
        if re.match('^[0-9]+x[0-9]+$', resize) is None:
            raise Exception(f"Invalid size format : {resize}" + os.linesep +
                            "Expected format example : 256x256")
        else:
            formatted_resize = [int(x) for x in resize.split("x")]

    return formatted_resize


def main():
    arguments = get_arguments()

    google_images_downloader.WEBDRIVER_WAIT_DURATION = arguments.wait_duration

    show = True if arguments.show else False
    quiet = True if arguments.quiet else False

    downloader = GoogleImagesDownloader(browser=arguments.browser, show=show, debug=arguments.debug, quiet=quiet)

    resize = get_formatted_resize(arguments.resize)  # Transform resizing format, example : 256x256 to (256, 256) tuple

    downloader.download(arguments.query, destination=arguments.destination, limit=arguments.limit, resize=resize,
                        file_format=arguments.format)

    downloader.close()


if __name__ == "__main__":
    main()
