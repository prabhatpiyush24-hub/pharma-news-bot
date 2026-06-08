"""
Processor — filters to India-relevant pharma news, deduplicates, scores.
Focus: Indian pharma companies, regulatory events, investor news.
"""

import re
import hashlib

# ── Indian pharma companies (used to boost relevance score) ─────────────────
INDIAN_PHARMA_COMPANIES = [
    "sun pharma", "sun pharmaceutical", "dr reddy", "dr. reddy", "cipla",
    "lupin", "divi", "divis", "aurobindo", "biocon", "torrent", "ipca",
    "alkem", "natco", "ajanta", "granules", "laurus", "gland pharma",
    "wockhardt", "jubilant", "marksans", "indoco", "pfizer india",
    "gsk india", "glaxo india", "sanofi india", "abbott india",
    "sequent", "strides", "fdc limited", "jb chemicals", "eris",
    "caplin point", "suven", "solara", "zydus", "cadila", "panacea",
    "piramal", "mankind pharma", "emcure", "glenmark", "wallace",
    "medanta", "apollo", "fortis", "max health", "lal pathlabs",
    "metropolis", "thyrocare", "intas",
]

# ── Keywords that signal investor-relevant pharma news ──────────────────────
INVESTOR_KEYWORDS = [
    # Financial results
    "quarterly results", "q1 results", "q2 results", "q3 results", "q4 results",
    "annual results", "net profit", "revenue", "ebitda", "earnings", "pat",
    "operating profit", "margin", "guidance", "outlook", "order book",
    # Corporate actions
    "board meeting", "dividend", "bonus shares", "stock split", "buyback",
    "rights issue", "agm", "egm", "record date", "ex-date",
    "promoter holding", "shareholding", "stake sale", "block deal", "bulk deal",
    # Deals & business
    "acquisition", "merger", "deal", "partnership", "agreement", "mou",
    "licensing", "joint venture", "collaboration", "divestment", "spinoff",
    "fundraise", "ipo", "qip", "fpo", "ncd",
    # Regulatory India
    "usfda", "who-gmp", "cdsco", "dcgi", "drug controller", "nppa",
    "price cap", "price revision", "drug approval india",
    "anda approval", "tentative approval",
    # Operations
    "plant", "facility", "capacity", "expansion", "new product", "launch",
    "export", "api", "formulation", "generic", "biosimilar",
    "r&d", "research", "pipeline", "phase", "clinical",
    # Exchanges
    "bse", "nse", "sensex", "nifty pharma", "insider trading",
    "promoter", "pledge", "shares",
    # Investor signals
    "target price", "buy", "sell", "hold", "upgrade", "downgrade",
    "analyst", "brokerage", "rating", "recommendation",
    "52-week high", "52-week low", "multibagger",
]

# ── Exclude clearly irrelevant categories ───────────────────────────────────
EXCLUDE_PATTERNS = [
    r"\bus fda\b(?! warning| approval for india)",   # US FDA news not about India
    r"\beuropean medicines\b",
    r"\bclinical trial.*phase [12]\b",               # Early-stage global trials
    r"\bpubmed\b",
    r"\bpatentsview\b",
    r"\bsec edgar\b",
    r"\bwall street\b",
    r"\bnasdaq\b",
    r"\bnyse\b",
]


def is_relevant(item: dict) -> bool:
    """Return True if item is relevant to Indian pharma investor."""
    source = item.get("source", "")
    itype  = item.get("type", "")

    # BSE/NSE filings always relevant
    if source in ("BSE Filing", "NSE Filing"):
        return True

    text = (item.get("title", "") + " " + item.get("summary", "")).lower()

    # Exclude noise patterns
    for pat in EXCLUDE_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return False

    # Must mention an Indian pharma company OR investor keyword
    has_company = any(c in text for c in INDIAN_PHARMA_COMPANIES)
    has_keyword = any(k in text for k in INVESTOR_KEYWORDS)

    return has_company or has_keyword


def score_item(item: dict) -> int:
    source = item.get("source", "")
    itype  = item.get("type", "")
    text   = (item.get("title", "") + " " + item.get("summary", "")).lower()

    score = 0

    # Source priority
    if source in ("BSE Filing", "NSE Filing"):         score += 10
    elif "Economic Times" in source:                   score += 6
    elif "Mint" in source or "Business Standard" in source: score += 6
    elif "Moneycontrol" in source:                     score += 5
    elif "Pharma Biz" in source or "Express Pharma" in source: score += 4

    # High-value events
    high_value = [
        "quarterly results", "net profit", "revenue", "dividend", "board meeting",
        "acquisition", "merger", "block deal", "bulk deal", "fda approval",
        "anda approval", "plant shutdown", "import alert", "warning letter india",
        "price cap", "nppa", "promoter", "buyback", "stock split",
    ]
    for kw in high_value:
        if kw in text:
            score += 3

    # Indian company mention
    for c in INDIAN_PHARMA_COMPANIES:
        if c in text:
            score += 2
            break

    return score


def deduplicate(items: list[dict]) -> list[dict]:
    seen, unique = set(), []
    for item in items:
        key = re.sub(r"[^a-z0-9]", "", item.get("title", "").lower())[:80]
        fp  = hashlib.md5(key.encode()).hexdigest()
        if fp not in seen:
            seen.add(fp)
            unique.append(item)
    return unique


def process(all_items: list[dict]) -> list[dict]:
    filtered = [i for i in all_items if is_relevant(i)]
    deduped  = deduplicate(filtered)
    for item in deduped:
        item["_score"] = score_item(item)
    sorted_items = sorted(deduped, key=lambda x: x["_score"], reverse=True)
    print(f"[Processor] {len(all_items)} total → {len(filtered)} relevant → {len(deduped)} after dedup")
    return sorted_items
