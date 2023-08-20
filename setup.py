from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="google-images-downloader",
    version="1.0.1",
    author="Harkame",
    description="Script to download images from a \"Google Images\" query",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Harkame/GoogleImagesDownloader",
    packages=find_packages(),
    classifiers=["Programming Language :: Python"],
    install_requires=[
        "selenium",
        "requests",
        "pillow",
        "chromedriver-py",
        "fake_useragent",
        "tqdm",
    ],
    entry_points={
        "console_scripts": ["google-images-downloader = google_images_downloader.main:main"],
    },
)
