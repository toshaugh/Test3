#!/usr/bin/env python3
"""Fetches the top 5 dev.to posts from the past 5 days and writes a markdown report."""

import sys
import requests
from devto_utils import TOP_N, DAYS_BACK, fetch_top_articles, build_markdown

OUTPUT_FILE = "devto_top_posts.md"


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

    print(f"Found {len(articles)} article(s). Fetching content and generating AI summaries…")
    markdown = build_markdown(articles)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        fh.write(markdown)

    print(f"\nDone! Report saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
