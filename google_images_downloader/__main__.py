import sys

import google_images_downloader


def main(argv):
    arguments = google_images_downloader.get_arguments(argv)

    google_images_downloader.WEBDRIVER_WAIT_DURATION = arguments.wait_duration

    downloader = google_images_downloader.GoogleImagesDownloader(browser=arguments.browser, show=arguments.show,
                                                                 debug=arguments.debug,
                                                                 quiet=arguments.quiet,
                                                                 disable_safeui=arguments.disable_safeui)

    for query in arguments.queries:
        downloader.download(query, destination=arguments.destination, limit=arguments.limit, resize=arguments.resize,
                            file_format=arguments.format)

    downloader.close()


if __name__ == "__main__":
    main(sys.argv[1:])
