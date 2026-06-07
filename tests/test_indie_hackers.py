from unittest.mock import patch, MagicMock
from scrapers.indie_hackers import fetch_posts

def make_entry(title, summary, link):
    e = MagicMock()
    e.title = title
    e.summary = summary
    e.link = link
    e.author = "unknown"
    e.published = "Tue, 03 Jun 2026 05:00:00 +0000"
    return e

@patch("scrapers.indie_hackers.feedparser.parse")
def test_returns_keyword_matches(mock_parse):
    mock_parse.return_value.entries = [
        make_entry("Automate content publishing with RSS", "I want to auto publish blog posts", "https://indiehackers.com/1"),
        make_entry("My SaaS revenue update", "unrelated content", "https://indiehackers.com/2"),
    ]
    posts = fetch_posts(seen_urls=set())
    urls = [p["url"] for p in posts]
    assert "https://indiehackers.com/1" in urls
    assert "https://indiehackers.com/2" not in urls

@patch("scrapers.indie_hackers.feedparser.parse")
def test_skips_seen_urls(mock_parse):
    mock_parse.return_value.entries = [
        make_entry("RSS content pipeline tool", "publishing workflow", "https://indiehackers.com/seen"),
    ]
    posts = fetch_posts(seen_urls={"https://indiehackers.com/seen"})
    assert posts == []
