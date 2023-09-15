import sys

try:  # Normal way
    from gid import GoogleImagesDownloader, set_webdriver_wait_duration
    from arguments_helper import get_arguments
except ImportError:  # For main tests
    from google_images_downloader import GoogleImagesDownloader, set_webdriver_wait_duration, \
        get_arguments


def main(argv=None):
    if not argv:
        argv = sys.argv[1:]

    arguments = get_arguments(argv)

    set_webdriver_wait_duration(arguments.wait_duration)

    downloader = GoogleImagesDownloader(browser=arguments.browser, show=arguments.show,
                                        debug=arguments.debug,
                                        quiet=arguments.quiet,
                                        disable_safeui=arguments.disable_safeui)

    for query in arguments.queries:
        downloader.download(query, destination=arguments.destination, limit=arguments.limit, resize=arguments.resize,
                            file_format=arguments.format)

    downloader.close()


if __name__ == "__main__":
    main(sys.argv[1:])
