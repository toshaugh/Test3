#!/usr/bin/env python3
"""Flask web service that serves the top dev.to posts as a markdown/HTML report."""

import os
import time
import threading
import requests
from datetime import datetime, timezone, timedelta
from flask import Flask, Response

app = Flask(__name__)

DEVTO_API = "https://dev.to/api"
DAYS_BACK = 5
TOP_N = 5
CACHE_TTL = 3600  # seconds

HEADERS = {
    "User-Agent": "devto-top-posts-scraper/1.0",
    "Accept": "application/json",
}

_cache: dict = {"markdown": None, "generated_at": 0}
_lock = threading.Lock()


# ---------------------------------------------------------------------------
# dev.to helpers (same logic as devto_scraper.py)
# ---------------------------------------------------------------------------

def fetch_top_articles() -> list[dict]:
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
    resp = requests.get(
        f"{DEVTO_API}/articles/{article_id}",
        headers=HEADERS,
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json().get("body_markdown", "")


def summarize(body: str, max_chars: int = 600) -> str:
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

        body = fetch_article_body(article["id"])
        summary = summarize(body)

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


def get_report() -> tuple[str, str]:
    """Return (markdown, error_message). Uses cache when fresh."""
    with _lock:
        age = time.time() - _cache["generated_at"]
        if _cache["markdown"] and age < CACHE_TTL:
            return _cache["markdown"], ""

    try:
        articles = fetch_top_articles()
    except Exception as exc:
        return "", f"Failed to fetch articles: {exc}"

    if not articles:
        return "", "No articles found published in the past 5 days."

    try:
        markdown = build_markdown(articles)
    except Exception as exc:
        return "", f"Failed to build report: {exc}"

    with _lock:
        _cache["markdown"] = markdown
        _cache["generated_at"] = time.time()

    return markdown, ""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/raw")
def raw():
    """Return the report as plain text markdown."""
    md, err = get_report()
    if err:
        return Response(f"Error: {err}", status=502, mimetype="text/plain")
    return Response(md, mimetype="text/plain; charset=utf-8")


@app.route("/")
def index():
    """Return the report as a simple HTML page."""
    md, err = get_report()
    if err:
        body = f"<p style='color:red'>{err}</p>"
    else:
        # Minimal markdown→HTML conversion for display
        import html
        lines = []
        in_blockquote = False
        for line in md.splitlines():
            if line.startswith("> ") or line == ">":
                content = html.escape(line[2:] if line.startswith("> ") else "")
                if not in_blockquote:
                    lines.append("<blockquote>")
                    in_blockquote = True
                lines.append(f"<p>{content}</p>" if content else "")
            else:
                if in_blockquote:
                    lines.append("</blockquote>")
                    in_blockquote = False
                escaped = html.escape(line)
                if line.startswith("## "):
                    lines.append(f"<h2>{html.escape(line[3:])}</h2>")
                elif line.startswith("### "):
                    lines.append(f"<h3>{html.escape(line[4:])}</h3>")
                elif line.startswith("# "):
                    lines.append(f"<h1>{html.escape(line[2:])}</h1>")
                elif line.startswith("---"):
                    lines.append("<hr>")
                elif line.startswith("_") and line.endswith("_"):
                    lines.append(f"<p><em>{html.escape(line[1:-1])}</em></p>")
                elif line.startswith("| "):
                    lines.append(f"<p style='font-family:monospace;font-size:0.9em'>{escaped}</p>")
                elif line.strip():
                    lines.append(f"<p>{escaped}</p>")
        if in_blockquote:
            lines.append("</blockquote>")
        body = "\n".join(lines)

    html_page = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Top dev.to Posts</title>
  <style>
    body {{ max-width: 860px; margin: 2rem auto; padding: 0 1rem;
            font-family: system-ui, sans-serif; line-height: 1.6; color: #1a1a1a; }}
    h1 {{ border-bottom: 2px solid #3b49df; padding-bottom: .4rem; }}
    h2 {{ margin-top: 2.5rem; color: #3b49df; }}
    blockquote {{ border-left: 3px solid #d1d5db; margin: 1rem 0;
                  padding: .5rem 1rem; background: #f9fafb; color: #374151; }}
    hr {{ border: none; border-top: 1px solid #e5e7eb; margin: 2rem 0; }}
    a {{ color: #3b49df; }}
    nav {{ margin-bottom: 1rem; font-size: .9em; }}
  </style>
</head>
<body>
  <nav><a href="/">HTML</a> · <a href="/raw">Raw Markdown</a></nav>
  {body}
</body>
</html>"""
    return Response(html_page, mimetype="text/html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
