# Code taken in large part from https://github.com/jcpeterson/openwebtext

import io
import time
import json
import tarfile
import warnings
import argparse
import pickle
from pathlib import Path
from multiprocessing import Pool

import urllib
import urllib.request
import urllib.parse

import tqdm

def load_urls(fh, max_urls=-1, load_json=True):
    if load_json:
        url_entries = [ obj['url'] for obj in json.load(fh) ]
    else:
        url_entries = [ obj.strip() for obj in fh ]

    if max_urls != -1:
        url_entries = list(url_entries)[:max_urls]
    return url_entries

def raw_download(url, out):
    try:
        info = urllib.request.urlopen(url)
        content = info.headers['Content-Type']
        if 'text' in content:
            return False
        if info.status >= 400:
            return False

        urllib.request.urlretrieve(url, filename=out)
        return True
    except:
        return False

def download_imgur(url, out):
    info = urllib.request.urlopen(url)

    # was removed
    if 'removed' in info.geturl():
        return False

    urls_to_try = []

    path = urllib.parse.urlparse(url).path[1:]
    key = path.split('.')[0]
    if url.endswith(('.gifv', '.gif')):
        mp4_url = "http://i.imgur.com/" + key + '.mp4'
        urls_to_try.append(mp4_url)

    urls_to_try.append(url)
    urls_to_try.append("http://i.imgur.com/download/" + key)

    for u in urls_to_try:
        out_temp = str(out)
        if u.endswith('.gifv'):
            out_temp += '.mp4'
        elif not u.endswith('.gif'):
            if not out_temp.endswith('mp4'):
                out_temp += '.mp4'

        if raw_download(u, out_temp):
            return True

    return False

def download_gfy(url, out):
    url_meta = urllib.parse.urlparse(url)
    base_urls_to_try = [ 'https://fat.gfycat.com', 'https://zippy.gfycat.com', 'https://giant.gfycat.com' ]
    for base in base_urls_to_try:
        download_url = base + url_meta.path.replace('.mp4', '') + '.webm'
        temp_out = str(out)
        if not temp_out.endswith('.webm'):
            temp_out += '.webm'
        if raw_download(download_url, temp_out):
            return True
    return False

def download(url_entry, out_dir=None):
    file_name = from_url_to_path(url_entry)
    output = out_dir / file_name

    try:
        success = False
        if 'imgur' in url_entry:
            success = download_imgur(url_entry, output)
        elif 'gfycat' in url_entry:
            success = download_gfy(url_entry, output)
        else:
            success = raw_download(url_entry, output)
    except:
        return False, url_entry
        #import traceback
        #traceback.print_last()


    return success, url_entry

def from_url_to_path(url):
    parsed = urllib.parse.urlparse(url)
    return parsed.netloc + parsed.path.replace('/', '_')

def save_urls(all_urls, out):
    with open(out, 'w') as writer:
        for url in all_urls:
            writer.write('%s\n' % url)
        writer.flush()

def main(args):
    out_dir = Path(args.output_dir)
    if not out_dir.exists():
        out_dir.mkdir()

    urls_downloaded = {}
    if args.memory and Path(args.memory).exists():
        with open(args.memory) as in_f:
            urls_downloaded = { url: True for url in load_urls(in_f, -1, load_json=False) }

    def save_state():
        save_urls(urls_downloaded, args.memory)

    import atexit
    atexit.register(save_state)

    with open(args.url_file) as fh:
        url_entries = load_urls(fh, args.max_urls)
        url_entries = [ url for url in url_entries if url not in urls_downloaded ]

        with Pool(args.workers) as pool:
            from functools import partial
            dl = partial(download, out_dir=out_dir)
            
            downloads = pool.imap_unordered(dl, url_entries)
            for success, x in tqdm.tqdm(downloads, total=len(url_entries)):
                if success:
                    urls_downloaded[x] = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url_file", type=str, default='urls.txt')
    parser.add_argument(
        "--memory",
        type=str,
        default="memory.txt",
        help="memory to store already downloaded files",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="scraped",
        help="which folder in the working directory to use for output",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=10,
        help="how many processes (cores) to use for parallel scraping",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=-1,
        help="maximum scrape time for a single URL; -1 means no limit",
    )
    parser.add_argument(
        "--max_urls",
        type=int,
        default=-1,
        help="maximum # of URLs to scrape; mostly for debugging",
    )
    parser.add_argument(
        "--show_warnings",
        action="store_true",
        default=False,
        help="whether to show warnings in general during scraping",
    )
    args = parser.parse_args()
    main(args)
