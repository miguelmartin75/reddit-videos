# reddit-videos

Basic script to download URLs to gfy, gifs, and html5 videos from reddit and download them.

Code is based off: https://github.com/eukaryote31/openwebtext (thanks)

# Usage

Requires python 3

1. Get urls: e.g. `python get_urls.py --out urls.txt --threshold 5 --subreddit gifs`
2. Download them, e.g. `python download.py --url_file urls.txt --workers 10`
