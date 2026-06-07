import time
from unittest.mock import MagicMock, patch
from scrapers.reddit import fetch_posts

def make_response(posts_data):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "data": {"children": [{"data": p} for p in posts_data]}
    }
    mock_resp.raise_for_status = MagicMock()
    return mock_resp

@patch("scrapers.reddit.requests.get")
def test_fetch_posts_returns_matching_posts(mock_get):
    now = time.time()
    mock_get.return_value = make_response([
        {"title": "How do I automate my blog?", "selftext": "I want to auto publish RSS content",
         "url": "https://reddit.com/1", "author": "user1", "created_utc": now - 3600},
        {"title": "Old RSS post", "selftext": "content pipeline help",
         "url": "https://reddit.com/2", "author": "user2", "created_utc": now - 90000},
        {"title": "Unrelated post", "selftext": "nothing relevant here",
         "url": "https://reddit.com/3", "author": "user3", "created_utc": now - 3600},
    ])

    posts = fetch_posts(lookback_hours=24, seen_urls=set())
    urls = [p["url"] for p in posts]

    assert "https://reddit.com/1" in urls   # recent + keyword match
    assert "https://reddit.com/2" not in urls  # too old
    assert "https://reddit.com/3" not in urls  # no keyword match

@patch("scrapers.reddit.requests.get")
def test_fetch_posts_skips_seen_urls(mock_get):
    now = time.time()
    mock_get.return_value = make_response([
        {"title": "automate my blog now", "selftext": "RSS workflow help",
         "url": "https://reddit.com/seen", "author": "user1", "created_utc": now - 100},
    ])

    posts = fetch_posts(lookback_hours=24, seen_urls={"https://reddit.com/seen"})
    assert posts == []

@patch("scrapers.reddit.requests.get")
def test_fetch_posts_skips_failed_subreddit(mock_get):
    mock_get.side_effect = Exception("network error")
    posts = fetch_posts(lookback_hours=24, seen_urls=set())
    assert posts == []
