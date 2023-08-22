# google-images-downloader

[![PyPI version](https://badge.fury.io/py/google-images-downloader.svg)](https://badge.fury.io/py/google-images-downloader)

## Requirements

- [Google Chrome](https://www.google.com/chrome/)

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

downloader = GoogleImagesDownloader()

downloader.download("bear")  # Download 50 images in ./downloads folder

downloader.download("cat", destination="C:\download\destination")  # Download at specified destination

downloader.download("bird", limit=100)  # Download 100 images

downloader.download("dog", resize=(180, 180))  # Download with images resizing

downloader.quiet = True  # Disable status messages

downloader.download("fish")  # Quiet download
```

## Tests

```shell
pip install tox

tox
```