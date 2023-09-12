import sys
import google_images_downloader

from google_images_downloader import GoogleImagesDownloader
from helpers.arguments_helper import get_arguments


def main():
    arguments = get_arguments(sys.argv[1:])

    google_images_downloader.WEBDRIVER_WAIT_DURATION = arguments.wait_duration

    downloader = GoogleImagesDownloader(browser=arguments.browser, show=arguments.show, debug=arguments.debug,
                                        quiet=arguments.quiet,
                                        disable_safeui=arguments.disable_safeui)

    for query in arguments.queries:
        downloader.download(query, destination=arguments.destination, limit=arguments.limit, resize=arguments.resize,
                            file_format=arguments.format)

    downloader.close()


if __name__ == "__main__":
    main()
