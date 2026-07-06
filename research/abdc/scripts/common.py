"""Shared helpers for the ABDC journal database scripts."""

import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import quote_plus

ABDC_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ABDC_DIR / "data"
GUIDELINES_DIR = ABDC_DIR / "guidelines"
OVERRIDES_PATH = ABDC_DIR / "overrides.json"
JOURNALS_JSON = DATA_DIR / "journals.json"

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://abdc.edu.au/",
}


def slugify(title: str) -> str:
    """ASCII-fold a journal title into a filesystem/URL-safe slug."""
    text = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return re.sub(r"-{2,}", "-", text)


def load_overrides() -> dict:
    if OVERRIDES_PATH.exists():
        return json.loads(OVERRIDES_PATH.read_text())
    return {}


def load_journals() -> list[dict]:
    return json.loads(JOURNALS_JSON.read_text())["journals"]


def guidelines_cache_path(slug: str) -> Path:
    return GUIDELINES_DIR / f"{slug}.md"


def derive_guidelines(title: str, slug: str, publisher: str, issn: str, issn_online: str) -> dict:
    """Best-effort author-guidelines URL from publisher URL conventions.

    Returns {"url": str|None, "source": str} where source is one of:
      "publisher-pattern"  — direct link derived from a known URL convention
      "publisher-search"   — search page on the publisher's site
      "web-search"         — generic search fallback
    """
    pub = (publisher or "").lower()
    q = quote_plus(title)
    eissn_compact = re.sub(r"[^0-9xX]", "", issn_online or "").lower()

    if "elsevier" in pub:
        if issn:
            return {
                "url": f"https://www.elsevier.com/journals/{slug}/{issn}/guide-for-authors",
                "source": "publisher-pattern",
            }
        return {
            "url": f"https://www.sciencedirect.com/journal/{slug}",
            "source": "publisher-pattern",
        }
    if "wiley" in pub or "blackwell" in pub:
        if len(eissn_compact) == 8:
            return {
                "url": f"https://onlinelibrary.wiley.com/hub/journal/{eissn_compact}/forauthors",
                "source": "publisher-pattern",
            }
        return {
            "url": f"https://onlinelibrary.wiley.com/action/doSearch?AllField={q}",
            "source": "publisher-search",
        }
    if "springer" in pub or "palgrave" in pub:
        return {"url": f"https://link.springer.com/search?query={q}", "source": "publisher-search"}
    if "taylor" in pub and "francis" in pub or "routledge" in pub:
        return {
            "url": f"https://www.tandfonline.com/action/doSearch?AllField={q}",
            "source": "publisher-search",
        }
    if "emerald" in pub:
        return {"url": f"https://www.emerald.com/insight/search?q={q}", "source": "publisher-search"}
    if "sage" in pub:
        return {
            "url": f"https://journals.sagepub.com/action/doSearch?AllField={q}",
            "source": "publisher-search",
        }
    if "informs" in pub:
        return {
            "url": f"https://pubsonline.informs.org/action/doSearch?AllField={q}",
            "source": "publisher-search",
        }
    if "oxford" in pub:
        return {
            "url": f"https://academic.oup.com/journals/search-results?q={q}",
            "source": "publisher-search",
        }
    if "cambridge" in pub:
        return {"url": f"https://www.cambridge.org/core/search?q={q}", "source": "publisher-search"}
    return {
        "url": f"https://www.google.com/search?q={quote_plus(title + ' author guidelines submission')}",
        "source": "web-search",
    }
