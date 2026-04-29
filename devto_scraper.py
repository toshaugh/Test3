#!/usr/bin/env python3
"""Fetches the top 5 dev.to posts from the past 5 days and writes a markdown report."""

import sys
import requests
from datetime import datetime, timezone, timedelta

DEVTO_API = "https://dev.to/api"
DAYS_BACK = 5
TOP_N = 5
OUTPUT_FILE = "devto_top_posts.md"

HEADERS = {
    "User-Agent": "devto-top-posts-scraper/1.0",
    "Accept": "application/json",
}


def fetch_top_articles(days: int = DAYS_BACK, fetch_limit: int = 30) -> list[dict]:
    """Return up to TOP_N articles published within the last `days` days, sorted by reactions."""
    resp = requests.get(
        f"{DEVTO_API}/articles",
        params={"top": days, "per_page": fetch_limit},
        headers=HEADERS,
        timeout=20,
    )
    resp.raise_for_status()

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
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


def summarize(body: str, max_chars: int = 600) -> str:
    """Return a plain-text summary from the first `max_chars` characters of the body."""
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    prose = " ".join(lines)
    if len(prose) <= max_chars:
        return prose
    return prose[:max_chars].rsplit(" ", 1)[0] + "…"


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

        print(f"  [{rank}/{TOP_N}] Fetching: {title}")
        body = fetch_article_body(article["id"])
        summary = summarize(body)

        sections += [
            f"## {rank}. {title}",
            "",
            f"| | |",
            f"|---|---|",
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


def main() -> None:
    print(f"Fetching top {TOP_N} dev.to posts from the past {DAYS_BACK} days…")

    try:
        articles = fetch_top_articles()
    except requests.exceptions.ConnectionError as exc:
        print(f"Error: Could not connect to dev.to — {exc}", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.HTTPError as exc:
        print(f"Error: dev.to API returned {exc.response.status_code}", file=sys.stderr)
        sys.exit(1)

    if not articles:
        print("No articles found published in the past 5 days.")
        sys.exit(0)

    print(f"Found {len(articles)} article(s). Fetching full content…")
    markdown = build_markdown(articles)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        fh.write(markdown)

    print(f"\nDone! Report saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
