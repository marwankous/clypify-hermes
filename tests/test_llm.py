from unittest.mock import patch, MagicMock
from llm import score_and_draft

SAMPLE_POSTS = [
    {
        "source": "reddit",
        "subreddit": "r/Blogging",
        "title": "How do I automate my blog?",
        "body": "I want to publish RSS content to WordPress automatically",
        "url": "https://reddit.com/1",
        "author": "u/blogger99",
        "posted_at": "2026-06-03T06:00:00Z",
    }
]

GOOD_RESPONSE = '''[
  {
    "index": 0,
    "score": 8,
    "reason": "Explicitly seeking RSS-to-WordPress automation — direct Clypify fit.",
    "outreach": "Saw your post about automating WordPress publishing from RSS feeds. Built something for this — Clypify pulls RSS, rewrites with AI, and auto-posts to WordPress. Free plan at clypify.com — no card needed."
  }
]'''

LOW_SCORE_RESPONSE = '''[{"index": 0, "score": 4, "reason": "Just venting.", "outreach": "..."}]'''

@patch("llm.genai.GenerativeModel")
def test_returns_leads_above_threshold(mock_model_cls):
    mock_response = MagicMock()
    mock_response.text = GOOD_RESPONSE
    mock_model_cls.return_value.generate_content.return_value = mock_response

    leads = score_and_draft(SAMPLE_POSTS)

    assert len(leads) == 1
    assert leads[0]["score"] == 8
    assert leads[0]["url"] == "https://reddit.com/1"
    assert "clypify.com" in leads[0]["outreach"]

@patch("llm.genai.GenerativeModel")
def test_filters_leads_below_threshold(mock_model_cls):
    mock_response = MagicMock()
    mock_response.text = LOW_SCORE_RESPONSE
    mock_model_cls.return_value.generate_content.return_value = mock_response

    leads = score_and_draft(SAMPLE_POSTS)
    assert leads == []

@patch("llm.requests.post")
@patch("llm.genai.GenerativeModel", side_effect=Exception("Gemini unavailable"))
def test_falls_back_to_ollama_cloud(mock_model_cls, mock_post):
    mock_post.return_value.json.return_value = {
        "choices": [{"message": {"content": GOOD_RESPONSE}}]
    }
    mock_post.return_value.raise_for_status = MagicMock()

    leads = score_and_draft(SAMPLE_POSTS)
    assert len(leads) == 1
    assert mock_post.called
