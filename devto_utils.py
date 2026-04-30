"""Shared utilities for fetching dev.to articles and building the markdown report."""

import os
import anthropic
import requests
from datetime import datetime, timezone, timedelta

DEVTO_API = "https://dev.to/api"
DAYS_BACK = 5
TOP_N = 5

HEADERS = {
    "User-Agent": "devto-top-posts-scraper/1.0",
    "Accept": "application/json",
}

_anthropic_client: anthropic.Anthropic | None = None


def _claude() -> anthropic.Anthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.Anthropic()
    return _anthropic_client


def fetch_top_articles() -> list[dict]:
    """Return up to TOP_N articles published within the last DAYS_BACK days, sorted by reactions."""
    resp = requests.get(
        f"{DEVTO_API}/articles",
        params={"top": DAYS_BACK, "per_page": 30},
        headers=HEADERS,
        timeout=20,
    )
    resp.raise_for_status()
    cutoff = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)
    articles = []
    for article in resp.json():
        published_raw = article.get("published_at", "")
        if not published_raw:
            continue
        published_at = datetime.fromisoformat(published_raw.replace("Z", "+00:00"))
        if published_at >= cutoff:
            articles.append(article)
    return articles[:TOP_N]


def fetch_article_body(article_id: int) -> str:
    """Return the full markdown body of a single article."""
    resp = requests.get(
        f"{DEVTO_API}/articles/{article_id}",
        headers=HEADERS,
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json().get("body_markdown", "")


def ai_summarize(title: str, body: str) -> str:
    """Use Claude to generate a concise 2-3 sentence summary of an article."""
    # Limit input to keep costs predictable
    excerpt = body[:5000]
    response = _claude().messages.create(
        model="claude-opus-4-7",
        max_tokens=300,
        system="You summarize technical blog posts in 2-3 concise sentences. Capture the core insight or takeaway. Write in present tense. Do not use phrases like 'This article' or 'The author'.",
        messages=[{
            "role": "user",
            "content": f"Title: {title}\n\n{excerpt}",
        }],
    )
    return next(b.text for b in response.content if b.type == "text").strip()


def build_markdown(articles: list[dict]) -> str:
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cutoff_str = (datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)).strftime("%Y-%m-%d")

    sections: list[str] = [
        f"# Top {TOP_N} dev.to Posts — Past {DAYS_BACK} Days",
        "",
        f"_Generated on {now_str} · Posts published since {cutoff_str}_",
        "",
        "---",
        "",
    ]

    for rank, article in enumerate(articles, start=1):
        title = article.get("title", "Untitled")
        url = article.get("url", "")
        author = article.get("user", {}).get("name", "Unknown")
        reactions = article.get("public_reactions_count", 0)
        comments = article.get("comments_count", 0)
        reading_time = article.get("reading_time_minutes", "?")
        published = (article.get("published_at") or "")[:10]
        tags = ", ".join(f"`{t}`" for t in article.get("tag_list", []))

        body = fetch_article_body(article["id"])
        summary = ai_summarize(title, body)

        sections += [
            f"## {rank}. {title}",
            "",
            "| | |",
            "|---|---|",
            f"| **Author** | {author} |",
            f"| **Published** | {published} |",
            f"| **Reactions** | {reactions} |",
            f"| **Comments** | {comments} |",
            f"| **Reading time** | {reading_time} min |",
            f"| **Tags** | {tags or '—'} |",
            f"| **URL** | [{url}]({url}) |",
            "",
            "### Summary",
            "",
            summary,
            "",
            "### Article Content",
            "",
        ]

        for line in body.splitlines():
            sections.append(f"> {line}" if line.strip() else ">")

        sections += ["", "---", ""]

    return "\n".join(sections)
