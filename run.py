import json
import os
from datetime import date

from dotenv import load_dotenv

from scrapers import reddit, twitter, indie_hackers
from llm import score_and_draft
from renderer import render_report

load_dotenv()

_DEFAULT_SEEN = os.path.join(os.path.dirname(__file__), "seen.json")
_DEFAULT_OUTPUT = os.path.join(os.path.dirname(__file__), "output")

def _load_seen(path: str) -> set:
    if not os.path.exists(path):
        return set()
    try:
        with open(path) as f:
            data = json.load(f)
        return set(data.keys()) if isinstance(data, dict) else set()
    except (json.JSONDecodeError, AttributeError):
        return set()

def _save_seen(path: str, urls: list[str]) -> None:
    existing = {}
    if os.path.exists(path):
        try:
            with open(path) as f:
                data = json.load(f)
            if isinstance(data, dict):
                existing = data
        except (json.JSONDecodeError, AttributeError):
            pass
    for url in urls:
        existing[url] = date.today().isoformat()
    with open(path, "w") as f:
        json.dump(existing, f, indent=2)

def run(seen_path: str = _DEFAULT_SEEN, output_dir: str = _DEFAULT_OUTPUT) -> str:
    seen = _load_seen(seen_path)

    raw = (
        reddit.fetch_posts(lookback_hours=24, seen_urls=seen)
        + twitter.fetch_posts(seen_urls=seen)
        + indie_hackers.fetch_posts(seen_urls=seen)
    )
    print(f"Scraped {len(raw)} new posts.")

    leads = score_and_draft(raw)
    print(f"{len(leads)} leads scored 6+.")

    path = render_report(leads, output_dir=output_dir, date_str=date.today().isoformat())
    print(f"Report written to {path}")

    _save_seen(seen_path, [p["url"] for p in raw])
    return path

if __name__ == "__main__":
    run()
