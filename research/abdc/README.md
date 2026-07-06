# ABDC Journal Database (A*, A, B) with Author Guidelines

A local database of the [ABDC Journal Quality List](https://abdc.edu.au/abdc-journal-quality-list/)
(Australian Business Deans Council), filtered to **A\*, A and B** journals, with a
best-known **author-guidelines link per journal** and a cache of fetched guidelines.
It is refreshed automatically once a month from the official ABDC spreadsheet.

Built to be consulted by the paper-building / lit-search skills when targeting a journal.

## Layout

```
research/abdc/
├── data/
│   ├── journals.json      # THE database: A*/A/B journals + guidelines links/cache
│   ├── abdc_jql_full.csv  # full official list (all ratings, raw columns)
│   └── meta.json          # source URL, JQL year, sha256, counts, timestamp
├── guidelines/            # cached author-guidelines pages, one markdown file per journal
├── overrides.json         # hand-curated guidelines URLs (beat derived ones)
└── scripts/
    ├── update_jql.py      # download official xlsx → rebuild data/
    ├── lookup.py          # fuzzy title lookup, prints JSON
    ├── fetch_guidelines.py# fetch + cache one journal's guidelines page
    └── common.py          # shared helpers / publisher URL patterns
```

## How a skill should consult it

1. **Find the journal** (fuzzy match on title):
   ```bash
   python research/abdc/scripts/lookup.py "journal of operations management"
   ```
   Returns rating, publisher, ISSNs, FoR, and a `guidelines` object.

2. **Read the guidelines.** If `guidelines.cache` is set, read that markdown file
   directly. Otherwise fetch and cache it:
   ```bash
   python research/abdc/scripts/fetch_guidelines.py "journal of operations management"
   ```

3. **Guideline URL quality** — check `guidelines.source`:
   - `override` / `manual` — hand-curated direct link (best)
   - `publisher-pattern` — derived from the publisher's URL convention (usually right)
   - `publisher-search` / `web-search` — only a search page. Find the real
     guidelines page (web search: `"<title>" author guidelines`), then cache it with
     `fetch_guidelines.py "<title>" --url <real-url>`; this also upgrades the entry
     in `journals.json`. Commit the result so it accumulates.

## Monthly automation

`.github/workflows/update-abdc-jql.yml` runs on the 3rd of each month (and on
manual dispatch). It downloads the current official xlsx from abdc.edu.au on a
GitHub-hosted runner, rebuilds `data/`, and commits the diff. New JQL releases
(e.g. 2025 → next review) are picked up automatically because the script scrapes
the download link from the ABDC site rather than pinning a file.

Cached guideline files are never deleted by the updater; entries keep pointing at
their cache across refreshes (slugs are stable).

## Local run

```bash
pip install -r research/abdc/requirements.txt
python research/abdc/scripts/update_jql.py
```

Note: abdc.edu.au sits behind bot protection; if a local/sandboxed run gets 403,
trigger the GitHub workflow instead (`Actions → Update ABDC Journal Quality List → Run workflow`).
