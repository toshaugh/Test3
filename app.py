#!/usr/bin/env python3
"""Flask web service that serves the top dev.to posts as a markdown/HTML report."""

import html as html_mod
import os
import time
import threading
from flask import Flask, Response
from devto_utils import TOP_N, DAYS_BACK, fetch_top_articles, build_markdown

app = Flask(__name__)

CACHE_TTL = 3600  # seconds

_cache: dict = {"markdown": None, "generated_at": 0}
_lock = threading.Lock()


def get_report() -> tuple[str, str]:
    """Return (markdown, error_message). Uses an in-memory cache when fresh."""
    with _lock:
        if _cache["markdown"] and time.time() - _cache["generated_at"] < CACHE_TTL:
            return _cache["markdown"], ""

    try:
        articles = fetch_top_articles()
    except Exception as exc:
        return "", f"Failed to fetch articles from dev.to: {exc}"

    if not articles:
        return "", "No articles found published in the past 5 days."

    try:
        markdown = build_markdown(articles)
    except Exception as exc:
        return "", f"Failed to generate report: {exc}"

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
    """Return the report as an HTML page."""
    md, err = get_report()
    if err:
        body = f"<p style='color:red'>{html_mod.escape(err)}</p>"
    else:
        lines = []
        in_blockquote = False
        for line in md.splitlines():
            if line.startswith("> ") or line == ">":
                content = html_mod.escape(line[2:] if line.startswith("> ") else "")
                if not in_blockquote:
                    lines.append("<blockquote>")
                    in_blockquote = True
                lines.append(f"<p>{content}</p>" if content else "")
            else:
                if in_blockquote:
                    lines.append("</blockquote>")
                    in_blockquote = False
                escaped = html_mod.escape(line)
                if line.startswith("## "):
                    lines.append(f"<h2>{html_mod.escape(line[3:])}</h2>")
                elif line.startswith("### "):
                    lines.append(f"<h3>{html_mod.escape(line[4:])}</h3>")
                elif line.startswith("# "):
                    lines.append(f"<h1>{html_mod.escape(line[2:])}</h1>")
                elif line.startswith("---"):
                    lines.append("<hr>")
                elif line.startswith("_") and line.endswith("_"):
                    lines.append(f"<p><em>{html_mod.escape(line[1:-1])}</em></p>")
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
