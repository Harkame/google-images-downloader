# google-images-downloader

[![PyPI version](https://badge.fury.io/py/google-images-downloader.svg)](https://badge.fury.io/py/google-images-downloader)
[![Build Status](https://app.travis-ci.com/Harkame/google-images-downloader.svg?branch=main)](https://app.travis-ci.com/Harkame/google-images-downloader)

## Requirements

- [Google Chrome](https://www.google.com/chrome/) (Used by default)

OR

- [Firefox](https://www.mozilla.org/en-US/firefox/new/)

## Installation

```shell
pip install google-images-downloader
```

OR

```shell
git clone https://github.com/Harkame/GoogleImagesDownloader.git

cd GoogleImagesDownloader

pip install .
```

## Usage

### Command line

#### Basic usage

```shell
google-images-downloader -q QUERY
```

For more information

```shell
google-images-downloader -h
```

### Programmatically

```python
from google_images_downloader import GoogleImagesDownloader

downloader = GoogleImagesDownloader() # Use chrome by default

downloader.download("bear")  # Download 50 images in ./downloads folder

downloader.download("cat", destination="C:\download\destination")  # Download at specified destination

downloader.download("bird", limit=100)  # Download 100 images

downloader.download("dog", resize=(256, 256))  # Download with images resizing

downloader.download("dog", format="JPEG")  # Download with images re-formatting (JPEG or PNG)

downloader.quiet = True  # Disable progression messages

downloader.download("fish")  # Quiet download
```

#### Specify browser to use for web scraping

```python
from google_images_downloader import GoogleImagesDownloader

downloader = GoogleImagesDownloader(browser="firefox") # Default : "chrome"
```

#### Show browser while web scraping

```python
from google_images_downloader import GoogleImagesDownloader

downloader = GoogleImagesDownloader(show=True)
```

## Tests

```shell
pip install tox

tox
```