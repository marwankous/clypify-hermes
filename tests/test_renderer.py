import os
import tempfile
from renderer import render_report

BASE_LEAD = {
    "score": 9,
    "source": "reddit",
    "subreddit": "r/Blogging",
    "title": "How to automate blog publishing?",
    "author": "u/blogger",
    "url": "https://reddit.com/r/Blogging/1",
    "posted_at": "2026-06-03T06:00:00Z",
    "reason": "Explicitly looking for an RSS-to-WordPress automation tool.",
    "outreach": "Saw your post about automating publishing. Clypify does this. Free plan at clypify.com — no card needed.",
}

def test_creates_html_file_with_lead_content():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = render_report([BASE_LEAD], output_dir=tmpdir, date_str="2026-06-03")
        assert os.path.exists(path)
        content = open(path).read()
        assert "2026-06-03" in content
        assert "u/blogger" in content
        assert "clypify.com" in content
        assert "Score: 9" in content
        assert "data-copy" in content

def test_sorts_leads_by_score_descending():
    low = {**BASE_LEAD, "score": 7, "title": "Low scorer"}
    high = {**BASE_LEAD, "score": 9, "title": "High scorer"}
    with tempfile.TemporaryDirectory() as tmpdir:
        path = render_report([low, high], output_dir=tmpdir, date_str="2026-06-03")
        content = open(path).read()
        assert content.index("High scorer") < content.index("Low scorer")

def test_empty_leads_shows_empty_state():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = render_report([], output_dir=tmpdir, date_str="2026-06-03")
        content = open(path).read()
        assert "No leads found" in content
