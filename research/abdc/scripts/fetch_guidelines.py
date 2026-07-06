#!/usr/bin/env python3
"""Fetch and cache a journal's author guidelines page as markdown.

Usage:  python research/abdc/scripts/fetch_guidelines.py "journal of operations management"
        python research/abdc/scripts/fetch_guidelines.py some-slug --url https://... (override URL)

The page is saved to research/abdc/guidelines/<slug>.md with a metadata header,
and the journal's entry in journals.json is updated to point at the cache.
Direct publisher links work best; for "publisher-search" / "web-search" sources
pass --url with the real guidelines page once known (e.g. found via web search).
"""

import argparse
import json
import sys
from datetime import datetime, timezone

import html2text
import requests
from bs4 import BeautifulSoup

from common import BROWSER_HEADERS, JOURNALS_JSON, GUIDELINES_DIR, guidelines_cache_path
from lookup import search


def page_to_markdown(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    converter = html2text.HTML2Text()
    converter.ignore_images = True
    converter.body_width = 0
    return converter.handle(str(main))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="+", help="journal title or slug")
    ap.add_argument("--url", help="explicit guidelines URL (overrides the derived one)")
    ap.add_argument("--force", action="store_true", help="refetch even if cached")
    args = ap.parse_args()

    db = json.loads(JOURNALS_JSON.read_text())
    journals = db["journals"]
    query = " ".join(args.query)
    by_slug = {j["slug"]: j for j in journals}
    entry = by_slug.get(query) or next(iter(search(query, journals, 1)), None)
    if entry is None:
        print(f"error: no A*/A/B journal matching {query!r}", file=sys.stderr)
        return 1

    cache = guidelines_cache_path(entry["slug"])
    if cache.exists() and not args.force and not args.url:
        print(f"already cached: {cache}")
        return 0

    url = args.url or entry["guidelines"].get("url")
    if not url:
        print("error: no guidelines URL known — pass --url", file=sys.stderr)
        return 1
    if not args.url and entry["guidelines"]["source"] in {"publisher-search", "web-search"}:
        print(
            f"warning: derived URL is only a search page ({entry['guidelines']['source']}); "
            "caching it anyway — prefer --url with the real guidelines page",
            file=sys.stderr,
        )

    print(f"fetching {url}")
    resp = requests.get(url, headers=BROWSER_HEADERS, timeout=90)
    resp.raise_for_status()
    body = page_to_markdown(resp.text)
    if len(body.strip()) < 200:
        print("error: page fetched but yielded almost no text (JS-only page?)", file=sys.stderr)
        return 1

    GUIDELINES_DIR.mkdir(parents=True, exist_ok=True)
    fetched = datetime.now(timezone.utc).isoformat(timespec="seconds")
    header = (
        f"---\n"
        f"journal: \"{entry['title']}\"\n"
        f"rating: \"{entry['rating']}\"\n"
        f"publisher: \"{entry['publisher']}\"\n"
        f"source_url: {url}\n"
        f"fetched_utc: {fetched}\n"
        f"---\n\n"
    )
    cache.write_text(header + body, encoding="utf-8")

    entry["guidelines"]["cache"] = f"guidelines/{entry['slug']}.md"
    if args.url:
        entry["guidelines"]["url"] = args.url
        entry["guidelines"]["source"] = "manual"
    JOURNALS_JSON.write_text(json.dumps(db, indent=1, ensure_ascii=False))
    print(f"cached: {cache} ({len(body):,} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
