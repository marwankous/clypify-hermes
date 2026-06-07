from unittest.mock import patch, MagicMock
from scrapers.twitter import fetch_posts

def make_entry(title, summary, link):
    e = MagicMock()
    e.title = title
    e.summary = summary
    e.link = link
    e.author = "unknown"
    e.published = "Tue, 03 Jun 2026 05:00:00 +0000"
    return e

@patch("scrapers.twitter.feedparser.parse")
def test_returns_keyword_matches(mock_parse):
    mock_parse.return_value.entries = [
        make_entry("automate my blog with RSS", "publishing workflow help", "https://x.com/1"),
        make_entry("Unrelated tweet about cats", "nothing here", "https://x.com/2"),
    ]
    posts = fetch_posts(seen_urls=set())
    urls = [p["url"] for p in posts]
    assert "https://x.com/1" in urls
    assert "https://x.com/2" not in urls

@patch("scrapers.twitter.feedparser.parse")
def test_skips_seen_urls(mock_parse):
    mock_parse.return_value.entries = [
        make_entry("automate my blog now", "RSS pipeline", "https://x.com/seen"),
    ]
    posts = fetch_posts(seen_urls={"https://x.com/seen"})
    assert posts == []
