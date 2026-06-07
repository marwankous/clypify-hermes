import json
import os
import tempfile
from unittest.mock import patch

MOCK_POST = {
    "source": "reddit", "subreddit": "r/Blogging",
    "title": "Automate RSS", "body": "...",
    "url": "https://reddit.com/1", "author": "u/user1",
    "posted_at": "2026-06-03T06:00:00Z",
}
MOCK_LEAD = {
    **MOCK_POST,
    "score": 8,
    "reason": "Good fit.",
    "outreach": "Hey... Free plan at clypify.com — no card needed.",
}

@patch("run.render_report", return_value="/tmp/leads-2026-06-03.html")
@patch("run.score_and_draft", return_value=[MOCK_LEAD])
@patch("run.indie_hackers.fetch_posts", return_value=[])
@patch("run.twitter.fetch_posts", return_value=[])
@patch("run.reddit.fetch_posts", return_value=[MOCK_POST])
def test_run_writes_report_and_updates_seen(
    mock_reddit, mock_twitter, mock_ih, mock_score, mock_render
):
    with tempfile.TemporaryDirectory() as tmpdir:
        seen_path = os.path.join(tmpdir, "seen.json")
        with open(seen_path, "w") as f:
            json.dump({}, f)

        from run import run
        run(seen_path=seen_path, output_dir=tmpdir)

        seen = json.load(open(seen_path))
        assert "https://reddit.com/1" in seen
        mock_render.assert_called_once()
        mock_score.assert_called_once_with([MOCK_POST])
