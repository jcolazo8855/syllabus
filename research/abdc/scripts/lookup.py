#!/usr/bin/env python3
"""Look up a journal in the ABDC database by (fuzzy) title.

Usage:  python research/abdc/scripts/lookup.py "strategic management journal"
        python research/abdc/scripts/lookup.py --rating A* --limit 20 management

Prints matching entries as JSON so the paper-building skill can consume them.
"""

import argparse
import difflib
import json
import sys

from common import load_journals


def search(query: str, journals: list[dict], limit: int) -> list[dict]:
    q = query.lower().strip()
    exact = [j for j in journals if j["title"].lower() == q]
    if exact:
        return exact
    substr = [j for j in journals if q in j["title"].lower()]
    if substr:
        return substr[:limit]
    titles = {j["title"].lower(): j for j in journals}
    close = difflib.get_close_matches(q, titles.keys(), n=limit, cutoff=0.6)
    return [titles[t] for t in close]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query", nargs="+", help="journal title (full or partial)")
    ap.add_argument("--rating", choices=["A*", "A", "B"], help="filter by rating")
    ap.add_argument("--limit", type=int, default=10)
    args = ap.parse_args()

    journals = load_journals()
    if args.rating:
        journals = [j for j in journals if j["rating"] == args.rating]
    matches = search(" ".join(args.query), journals, args.limit)
    if not matches:
        print(json.dumps({"matches": [], "note": "no match — journal may not be rated A*/A/B"}))
        return 1
    print(json.dumps({"matches": matches}, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
