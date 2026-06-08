"""
RSS Fetcher — Indian pharma news from BSE, NSE, business newspapers,
and pharma-specific Indian media. No API key required.
"""

import feedparser
import datetime
import re

FEEDS = [
    # Indian Business News
    ("Economic Times - Pharma",     "https://economictimes.indiatimes.com/industry/healthcare/biotech/pharmaceuticals/rssfeeds/13358260.cms"),
    ("Economic Times - Markets",    "https://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms"),
    ("Business Standard - Pharma",  "https://www.business-standard.com/rss/companies-101.rss"),
    ("Mint - Pharma",               "https://www.livemint.com/rss/companies"),
    ("Financial Express",           "https://www.financialexpress.com/feed/"),
    ("Moneycontrol - Pharma",       "https://www.moneycontrol.com/rss/MCtopnews.xml"),
    ("NDTV Profit",                 "https://feeds.feedburner.com/ndtvprofit-latest"),
    # Pharma-specific India
    ("Pharma Biz",                  "https://www.pharmabiz.com/RssNews.aspx"),
    ("Express Pharma",              "https://www.expresspharma.in/feed/"),
    ("Pharmexcil",                  "https://pharmexcil.org/feed/"),
    # Regulatory India
    ("CDSCO",                       "https://cdsco.gov.in/opencms/opencms/en/Rss-Feeds/"),
    # Google News - Indian pharma specific searches
    ("GNews - India Pharma",        "https://news.google.com/rss/search?q=india+pharmaceutical+company+BSE+NSE&hl=en-IN&gl=IN&ceid=IN:en"),
    ("GNews - Sun Pharma",          "https://news.google.com/rss/search?q=Sun+Pharma+stock+results&hl=en-IN&gl=IN&ceid=IN:en"),
    ("GNews - Dr Reddys",           "https://news.google.com/rss/search?q=Dr+Reddys+Laboratories+results&hl=en-IN&gl=IN&ceid=IN:en"),
    ("GNews - Cipla",               "https://news.google.com/rss/search?q=Cipla+pharma+quarterly+results&hl=en-IN&gl=IN&ceid=IN:en"),
    ("GNews - Lupin",               "https://news.google.com/rss/search?q=Lupin+Ltd+pharma+results&hl=en-IN&gl=IN&ceid=IN:en"),
    ("GNews - Divi's",              "https://news.google.com/rss/search?q=Divis+Laboratories+results&hl=en-IN&gl=IN&ceid=IN:en"),
    ("GNews - Aurobindo",           "https://news.google.com/rss/search?q=Aurobindo+Pharma+results&hl=en-IN&gl=IN&ceid=IN:en"),
    ("GNews - Biocon",              "https://news.google.com/rss/search?q=Biocon+results+quarterly&hl=en-IN&gl=IN&ceid=IN:en"),
    ("GNews - Torrent Pharma",      "https://news.google.com/rss/search?q=Torrent+Pharmaceuticals+results&hl=en-IN&gl=IN&ceid=IN:en"),
    ("GNews - IPCA Labs",           "https://news.google.com/rss/search?q=IPCA+Laboratories+results&hl=en-IN&gl=IN&ceid=IN:en"),
    ("GNews - India Pharma Policy", "https://news.google.com/rss/search?q=india+pharma+NPPA+price+control+drug+policy&hl=en-IN&gl=IN&ceid=IN:en"),
    ("GNews - India Pharma Export", "https://news.google.com/rss/search?q=india+pharma+exports+USFDA+warning+letter&hl=en-IN&gl=IN&ceid=IN:en"),
    ("GNews - India Pharma M&A",    "https://news.google.com/rss/search?q=india+pharma+acquisition+merger+deal&hl=en-IN&gl=IN&ceid=IN:en"),
    ("GNews - Pharma Q Results",    "https://news.google.com/rss/search?q=pharma+quarterly+results+india+profit&hl=en-IN&gl=IN&ceid=IN:en"),
]


def fetch_rss(days_back: int = 1) -> list[dict]:
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=days_back)
    items = []

    for source_name, url in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                published = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        published = datetime.datetime(*entry.published_parsed[:6], tzinfo=datetime.timezone.utc)
                    except Exception:
                        pass

                if published and published < cutoff:
                    continue

                items.append({
                    "title":     entry.get("title", "").strip(),
                    "link":      entry.get("link", ""),
                    "summary":   _clean_html(entry.get("summary", "")),
                    "published": published.isoformat() if published else "",
                    "source":    source_name,
                    "type":      "news",
                })
        except Exception as e:
            print(f"[RSS] Error fetching {source_name}: {e}")

    print(f"[RSS] Fetched {len(items)} items")
    return items


def _clean_html(text: str) -> str:
    clean = re.sub(r"<[^>]+>", " ", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean[:500]
