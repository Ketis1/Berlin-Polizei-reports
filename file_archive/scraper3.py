import feedparser

rss_url = "https://www.berlin.de/polizei/polizeimeldungen/archiv/2025/index.php/rss"
feed = feedparser.parse(rss_url)

for entry in feed.entries:
    print(entry.published, entry.link, entry.title)
