from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="google-images-downloader",
    version="1.0.0",
    author="Harkame",
    description="Script to download images from a \"Google Images\" query",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Harkame/GoogleImagesDownloader",
    packages=find_packages(),
    classifiers=["Programming Language :: Python"],
    install_requires=[required],
    entry_points={
        "console_scripts": ["google-images-downloader = google_images_downloader.main:main"],
    },
)
