import requests

# Dev.to discussions endpoint — "ask" and "help" type posts are actual leads,
# not regular articles. Regular top articles are published content, not seekers.
DEVTO_API = "https://dev.to/api/articles"

# Tags that attract people asking for help or sharing pain points
TAGS = ["blogging", "seo", "contentmarketing", "wordpress", "webdev", "productivity", "discuss"]

# Broad — let the LLM score; pre-filter only removes completely off-topic posts
KEYWORDS = [
    # Tool-seeking
    "looking for", "recommend", "anyone use", "what do you use", "best tool",
    "how do you", "what tool", "suggestion", "which tool", "any tool",
    # Content pain
    "blog", "content", "publish", "rss", "automate", "workflow", "schedule",
    "wordpress", "medium", "newsletter", "time", "manual",
    # Scale pain
    "scale", "consistent", "keep up", "too much", "bulk", "multiple sites",
]


def _matches_keywords(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in KEYWORDS)


def fetch_posts(seen_urls: set = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = set()

    posts = []
    seen_in_run: set = set()

    for tag in TAGS:
        try:
            # Fetch recent articles (not top) — "ask" and discussion posts are recent
            resp = requests.get(DEVTO_API, params={
                "tag": tag,
                "per_page": 30,
                "state": "fresh",   # recent posts, not curated top
            }, timeout=10)
            resp.raise_for_status()
            articles = resp.json()
        except Exception:
            continue

        for article in articles:
            url = article.get("url", "")
            if url in seen_urls or url in seen_in_run:
                continue
            # Skip pure tutorials/guides — we want pain-point posts
            type_of = article.get("type_of", "")
            if type_of not in ("article", ""):
                continue
            text = f"{article.get('title', '')} {article.get('description', '')}"
            if not _matches_keywords(text):
                continue
            seen_in_run.add(url)
            posts.append({
                "source": "devto",
                "subreddit": None,
                "title": article.get("title", "")[:200],
                "body": article.get("description", "")[:500],
                "url": url,
                "author": article.get("user", {}).get("username", "unknown"),
                "posted_at": article.get("published_at", ""),
            })

    return posts
