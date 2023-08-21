import sys
from google_images_downloader import GoogleImagesDownloader, DEFAULT_DESTINATION, DEFAULT_LIMIT, \
    DEFAULT_RESIZE, DEFAULT_QUIET, DEFAULT_DEBUG
import argparse
import os
import re


def get_arguments(arguments):
    argument_parser = argparse.ArgumentParser(
        description="Script to download images from a \"Google Images\" query",
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=99999),
    )

    argument_parser.add_argument(
        "-q",
        "--query",
        help="Google Images query" + os.linesep +
             "Example : python google_images_downloader/main.py -q cat",
        required=True
    )

    argument_parser.add_argument(
        "-d",
        "--destination",
        help="Download destination" + os.linesep +
             "Default : ./downloads\n" + os.linesep +
             "Example : python google_images_downloader/main.py -d C:\\my\\download\\destination",
        default=DEFAULT_DESTINATION
    )

    argument_parser.add_argument(
        "-l",
        "--limit",
        help="Downloads limit" + os.linesep +
             "Default : 50\n" + os.linesep +
             "Example : python google_images_downloader/main.py -l 500",
        default=DEFAULT_LIMIT,
        type=int
    )

    argument_parser.add_argument(
        "-r",
        "--resize",
        help="Resize images" + os.linesep +
             "Default : No resizing\n" + os.linesep +
             "Example : python google_images_downloader/main.py -r 180x180",
        default=DEFAULT_RESIZE,
    )

    argument_parser.add_argument(
        "-Q",
        "--quiet",
        help="Disable program output" + os.linesep +
             "Example : python google_images_downloader/main.py -q",
        default=DEFAULT_QUIET
    )

    argument_parser.add_argument(
        "-D",
        "--debug",
        help="Enable debug logs" + os.linesep +
             "Example : python google_images_downloader/main.py -D",
        default=DEFAULT_DEBUG
    )

    return argument_parser.parse_args(arguments)


def main():
    arguments = get_arguments(sys.argv[1:])

    downloader = GoogleImagesDownloader()

    downloader.init_arguments(arguments)

    resize = None

    if arguments.resize is not None:
        if re.match('^[0-9]+x[0-9]+$', arguments.resize) is None:
            raise Exception(f"Invalid size format" + os.linesep +
                            "Expected format example : 180x180")
        else:
            resize = [int(x) for x in arguments.resize.split("x")]

    downloader.download(arguments.query, destination=arguments.destination, limit=arguments.limit, resize=resize)

    if __name__ == "__main__":
        main()
