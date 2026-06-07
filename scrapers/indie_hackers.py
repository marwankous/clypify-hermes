import time
import requests

# Hacker News via Algolia — Ask HN and Show HN posts are high-signal
HN_SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"

# More varied queries to cast a wider net
SEARCH_QUERIES = [
    "blog automation",
    "content publishing",
    "rss feed",
    "wordpress automation",
    "content workflow",
    "blog tool",
    "auto publish",
    "content schedule",
    "newsletter automation",
    "scale blog",
]

# Broad keywords — keep more posts for the LLM to score
KEYWORDS = [
    # Tool-seeking
    "looking for", "recommend", "anyone use", "what do you use",
    "best tool", "is there a tool", "suggest", "which tool",
    # Content pain
    "blog", "content", "publish", "rss", "wordpress", "medium",
    "automate", "workflow", "newsletter", "schedule",
    # General pain
    "too much time", "manual", "scale", "consistent", "keep up",
]

# Search Ask HN separately — these are the richest leads
ASK_HN_QUERIES = [
    "blog content tool",
    "publishing workflow",
    "content automation",
]


def _matches_keywords(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in KEYWORDS)


def fetch_posts(seen_urls: set = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = set()

    cutoff = int(time.time()) - 72 * 3600
    posts = []
    seen_in_run: set = set()

    # Regular stories
    for query in SEARCH_QUERIES:
        try:
            resp = requests.get(HN_SEARCH_URL, params={
                "query": query,
                "tags": "story",
                "numericFilters": f"created_at_i>{cutoff}",
                "hitsPerPage": 30,
            }, timeout=10)
            resp.raise_for_status()
            hits = resp.json().get("hits", [])
        except Exception:
            continue

        for hit in hits:
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            if url in seen_urls or url in seen_in_run:
                continue
            text = f"{hit.get('title', '')} {hit.get('story_text') or ''}"
            if not _matches_keywords(text):
                continue
            seen_in_run.add(url)
            posts.append({
                "source": "hacker_news",
                "subreddit": None,
                "title": hit.get("title", "")[:200],
                "body": (hit.get("story_text") or "")[:500],
                "url": url,
                "author": hit.get("author", "unknown"),
                "posted_at": hit.get("created_at", ""),
            })

    # Ask HN posts — people explicitly seeking solutions
    for query in ASK_HN_QUERIES:
        try:
            resp = requests.get(HN_SEARCH_URL, params={
                "query": query,
                "tags": "ask_hn",
                "numericFilters": f"created_at_i>{cutoff}",
                "hitsPerPage": 20,
            }, timeout=10)
            resp.raise_for_status()
            hits = resp.json().get("hits", [])
        except Exception:
            continue

        for hit in hits:
            url = f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
            if url in seen_urls or url in seen_in_run:
                continue
            seen_in_run.add(url)
            posts.append({
                "source": "ask_hn",
                "subreddit": None,
                "title": hit.get("title", "")[:200],
                "body": (hit.get("story_text") or "")[:500],
                "url": url,
                "author": hit.get("author", "unknown"),
                "posted_at": hit.get("created_at", ""),
            })

    return posts
