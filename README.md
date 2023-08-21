# google-images-downloader

[![PyPI version](https://badge.fury.io/py/google-images-downloader.svg)](https://badge.fury.io/py/google-images-downloader)

## Requirements

- [Google Chrome](https://www.google.com/chrome/)

## Installation

``` console
$ pip install google-images-downloader
```

OR

``` console
$ git clone https://github.com/Harkame/GoogleImagesDownloader.git
$ cd GoogleImagesDownloader
$ pip install .
```

## Usage

### Command line

#### Basic usage

``` console
$ google-images-downloader -q QUERY
```

#### Usage with parameters

``` console
$ google-images-downloader [-h] -q QUERY [-d DESTINATION] [-l LIMIT] [-r RESIZE] [-Q QUIET] [-D DEBUG]
```

### Programmatically

``` python
from google_images_downloader import GoogleImagesDownloader

downloader = GoogleImagesDownloader()
```

#### Basic usage

``` python
downloader.download("cat", destination="downloads", limit=50, resize=None)
```

#### Download with images resizing

``` python
downloader.download("dog", resize=(180, 180))
```

#### Quiet download

``` python
downloader.quiet = True

downloader.download("fish")
```
