# Taken from: https://github.com/eukaryote31/openwebtext/blob/master/get_urls.py

import praw
import psaw
import tqdm
import datetime
import json


api = psaw.PushshiftAPI()


# all posts until the end of 2017
end_time = int(datetime.datetime(2016, 1, 1).timestamp())

AMOUNT=10000


query = api.search_submissions(before=end_time,
                               subreddit='gifs',
                               filter=['url', 'score', 'title', 'permalink', 'subreddit'],
                               limit=AMOUNT,
                               score='>5',
                               is_self=False,
                               over_18=False)

# download links from submissions
with open('urls.txt', 'w') as out_f:
    out_f.write('[\n')
    seen = {}

    total = 0
    for i, subm in enumerate(tqdm.tqdm(query, total=AMOUNT)):
        url = subm.url

        if url in seen:
            continue

        seen[url] = True

        # weird issue with psaw/pushshift that breaks score=">2"
        if subm.score < 5:
            continue

        entry = { 'url': url, 'score': subm.score, 'title': subm.title, 'permalink': subm.permalink, 'subreddit': subm.subreddit }

        out_f.write(json.dumps(entry))
        if i != AMOUNT - 1:
            out_f.write(',\n')

        total += 1

    print("Got: %d urls" % total)
    out_f.write(']\n')
    out_f.flush()
