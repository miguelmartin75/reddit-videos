# Taken from: https://github.com/eukaryote31/openwebtext/blob/master/get_urls.py

import praw
import psaw
import tqdm
import datetime
import json

def get_urls(subreddit='gifs', max_urls=10000, end_time=None, score_threshold=5):

    api = psaw.PushshiftAPI()

    if end_time is None:
        end_time = int(datetime.datetime.now().timestamp())

    query = api.search_submissions(before=end_time,
                                   subreddit='gifs',
                                   filter=['url', 'score', 'title', 'permalink', 'subreddit'],
                                   limit=max_urls,
                                   score='>%d' % score_threshold,
                                   is_self=False,
                                   over_18=False)
    seen = {}

    for i, subm in enumerate(tqdm.tqdm(query, total=max_urls)):
        url = subm.url

        if url in seen:
            continue

        seen[url] = True

        # weird issue with psaw/pushshift that breaks score=">2"
        if subm.score < score_threshold:
            continue

        entry = { 'url': url, 'score': subm.score, 'title': subm.title, 'permalink': subm.permalink, 'subreddit': subm.subreddit }

        yield entry

def main(args):
    # download links from submissions
    with open(args.out, 'w') as out_f:
        out_f.write('[\n')

        def write_entry(entry):
            out_f.write(json.dumps(entry))

        # TODO: end_time
        all_urls = get_urls(subreddit=args.subreddit, max_urls=args.max_urls, score_threshold=args.threshold)

        curr = next(all_urls, None)
        total = 0
        while curr is not None:
            write_entry(curr)
            curr = next(all_urls, None)
            if curr is None:
                break

            out_f.write(',\n')
            total += 1

        print("Got: %d urls" % total)
        out_f.write(']\n')
        out_f.flush()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=str, default='urls.txt', help='output file')
    parser.add_argument('--subreddit', type=str, default='gifs', help='subreddit to scrape')
    parser.add_argument('--max_urls', type=int, default=10000, help='max amount of urls to scrape')
    parser.add_argument('--threshold', type=int, default=5, help='score each post must be (>=)')

    args = parser.parse_args()
    main(args)

