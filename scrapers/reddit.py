import time
import feedparser

SUBREDDITS = [
    # Core audience
    "Blogging", "SEO", "juststart", "WordPressPlugins", "ContentMarketing",
    # High-signal — builders and small business owners who need content tools
    "Entrepreneur", "SideProject", "SaaS", "smallbusiness", "startups",
    # WordPress / publishing
    "Wordpress", "webdev",
    # Marketing practitioners
    "digital_marketing", "marketing", "Affiliatemarketing",
]

# Broad signal words — intentionally loose so the LLM does the heavy scoring
KEYWORDS = [
    # Tool-seeking signals
    "looking for", "recommend", "suggestion", "anyone use", "what do you use",
    "is there a tool", "is there a way", "how do you", "what's your workflow",
    "what tool", "which tool", "best tool", "any tool", "any app",
    # Content pain points
    "content", "blog", "publish", "posting", "rss", "rewrite", "automate",
    "workflow", "schedule", "takes forever", "manual", "time-consuming",
    "wordpress", "medium", "substack", "newsletter",
    # Volume / scale pain
    "scale", "bulk", "consistent", "every day", "every week", "keep up",
    "struggle", "behind on", "can't keep",
]

_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def _matches_keywords(text: str) -> bool:
    lower = text.lower()
    return any(kw in lower for kw in KEYWORDS)


def fetch_posts(lookback_hours: int = 48, seen_urls: set = None) -> list[dict]:
    if seen_urls is None:
        seen_urls = set()

    cutoff = time.time() - (lookback_hours * 3600)
    posts = []

    for name in SUBREDDITS:
        url = f"https://old.reddit.com/r/{name}/new.rss?limit=100"
        try:
            feed = feedparser.parse(url, request_headers={"User-Agent": _UA})
        except Exception:
            continue
        for entry in feed.entries:
            link = getattr(entry, "link", "")
            if link in seen_urls:
                continue
            published = getattr(entry, "published_parsed", None)
            if published and time.mktime(published) < cutoff:
                continue
            text = f"{getattr(entry, 'title', '')} {getattr(entry, 'summary', '')}"
            if not _matches_keywords(text):
                continue
            posts.append({
                "source": "reddit",
                "subreddit": f"r/{name}",
                "title": getattr(entry, "title", "")[:200],
                "body": getattr(entry, "summary", "")[:500],
                "url": link,
                "author": getattr(entry, "author", "unknown"),
                "posted_at": getattr(entry, "published", ""),
            })

    return posts
