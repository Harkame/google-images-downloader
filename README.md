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

For more informations

```shell
google-images-downloader -h
```

### Programmatically

#### Basic usage

```python
from google_images_downloader import GoogleImagesDownloader

downloader = GoogleImagesDownloader()

downloader.download("cat", destination="downloads", limit=50, resize=None)
```

#### Download with images resizing

```python
from google_images_downloader import GoogleImagesDownloader

downloader = GoogleImagesDownloader()

downloader.download("dog", resize=(180, 180))
```

#### Quiet download

```python
from google_images_downloader import GoogleImagesDownloader

downloader = GoogleImagesDownloader()

downloader.quiet = True

downloader.download("fish")
```
