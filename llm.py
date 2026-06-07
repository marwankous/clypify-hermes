import os
import json
import time
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

SCORE_THRESHOLD = 5
BATCH_SIZE = 20        # posts per LLM call — keeps prompts within Groq's TPM limit
BATCH_DELAY = 12       # seconds between batches — safe for llama-3.1-8b-instant 20K TPM
RETRY_DELAY = 65       # seconds to wait after a 429 before retrying once

_PROMPT_HEADER = """You are a lead scoring agent for Clypify — a content orchestration SaaS that aggregates RSS feeds, rewrites with AI, audits for SEO, and auto-publishes to WordPress and Medium.

Given posts from Reddit, dev.to, and Hacker News, return a JSON array. For each post include:
- index: the post's position in the input array (integer)
- score: 1-10 intent score (10 = strongest buying signal)
- reason: one sentence explaining the fit
- outreach: a 3-4 sentence direct message. Reference their specific pain. One sentence on Clypify. End with "Free plan at clypify.com — no card needed." Tone: direct, fellow builder, not salesy.

Score HIGH (7-10) if they: seek a tool explicitly, mention WordPress/Medium/RSS/newsletter, struggle with publishing volume or time, or ask "how do you manage content".
Score MEDIUM (5-6) if they: have relevant pain but not actively seeking a tool.
Score LOW (1-4) if they: vent without seeking solutions, discuss theory, are happy with current setup, or post pure tutorials.

Only include items with score >= 5. Return ONLY a valid JSON array, no prose, no markdown fences.

Posts:
"""


def _build_prompt(posts: list[dict]) -> str:
    lines = []
    for i, p in enumerate(posts):
        lines.append(f"[{i}] Source: {p['source']} | Author: {p['author']}")
        lines.append(f"Title: {p['title']}")
        lines.append(f"Body: {p['body']}")
        lines.append("")
    return _PROMPT_HEADER + "\n".join(lines)


def _call_gemini(prompt: str) -> str:
    """Gemini Developer API — free tier (1500 req/day). Requires billing for higher quota."""
    genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))
    model = genai.GenerativeModel("gemini-2.5-flash")
    return model.generate_content(prompt).text


def _call_groq(prompt: str) -> str:
    """Groq — free, primary when Gemini quota is exhausted."""
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ.get('GROK_API_KEY', '')}",
            "Content-Type": "application/json",
        },
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def _call_llm(prompt: str) -> str:
    """Gemini free tier first, Groq fallback."""
    try:
        return _call_gemini(prompt)
    except Exception:
        pass
    try:
        return _call_groq(prompt)
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            print(f"    Groq rate limited — waiting {RETRY_DELAY}s…")
            time.sleep(RETRY_DELAY)
            return _call_groq(prompt)
        raise


def _parse_response(raw: str, posts: list[dict]) -> list[dict]:
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return []
    leads = []
    for item in data:
        idx = item.get("index")
        if idx is None or not (0 <= idx < len(posts)):
            continue
        if item.get("score", 0) < SCORE_THRESHOLD:
            continue
        post = posts[idx]
        leads.append({
            **post,
            "score": item["score"],
            "reason": item["reason"],
            "outreach": item["outreach"],
        })
    return leads


def score_and_draft(posts: list[dict]) -> list[dict]:
    if not posts:
        return []

    all_leads = []
    batches = [posts[i:i + BATCH_SIZE] for i in range(0, len(posts), BATCH_SIZE)]

    for batch_num, batch in enumerate(batches, 1):
        print(f"  Scoring batch {batch_num}/{len(batches)} ({len(batch)} posts)…")
        prompt = _build_prompt(batch)
        try:
            raw = _call_llm(prompt)
            all_leads.extend(_parse_response(raw, batch))
        except Exception as e:
            print(f"  Batch {batch_num} failed: {e}")
        if batch_num < len(batches):
            time.sleep(BATCH_DELAY)

    return sorted(all_leads, key=lambda x: x["score"], reverse=True)
