from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="google-images-downloader",
    version="1.0.0",
    author="Harkame",
    description="Script to download images from a \"Google Images\" query",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Harkame/JapScanDownloader",
    packages=find_packages(),
    classifiers=["Programming Language :: Python"],
    install_requires=[
    ],
    dependency_links=[],
    extras_require={
        "dev": [
        ]
    },
    entry_points={
        "console_scripts": ["google-images-downloader = google-images-downloader.main:main"],
    },
)
