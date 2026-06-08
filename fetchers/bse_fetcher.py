"""
BSE / NSE Corporate Filing Fetcher
-----------------------------------
BSE provides a public API for corporate announcements (no key needed).
NSE provides RSS and public endpoints.

This fetcher pulls:
 - BSE corporate announcements for pharma companies
 - Board meeting notices, financial results, dividend announcements
 - Insider trading disclosures
 - Bulk/block deal data
"""

import requests
import datetime
import time

# ── Major Indian pharma companies with their BSE scrip codes ──────────────
PHARMA_COMPANIES = {
    "524715": "Sun Pharmaceutical Industries",
    "500124": "Dr. Reddy's Laboratories",
    "500087": "Cipla",
    "500257": "Lupin",
    "532488": "Divis Laboratories",
    "524804": "Aurobindo Pharma",
    "532892": "Biocon",
    "500359": "Torrent Pharmaceuticals",
    "524494": "IPCA Laboratories",
    "500680": "Abbott India",
    "500825": "Alkem Laboratories",
    "539798": "Natco Pharma",
    "532955": "Ajanta Pharma",
    "590077": "Granules India",
    "507252": "Pfizer India",
    "500271": "Glaxosmithkline Pharma",
    "500820": "Sanofi India",
    "540687": "Laurus Labs",
    "524715": "Sun Pharma",
    "543213": "Gland Pharma",
    "524752": "Wockhardt",
    "532488": "Divis Lab",
    "500676": "Strides Pharma",
    "532523": "Jubilant Pharmova",
    "524230": "FDC Limited",
    "524570": "Indoco Remedies",
    "590086": "Sequent Scientific",
    "524208": "Marksans Pharma",
}

BSE_API = "https://api.bseindia.com/BseIndiaAPI/api"
BSE_ANNOUNCEMENT_URL = "https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bseindia.com/",
    "Accept": "application/json, text/plain, */*",
}


def fetch_bse_announcements(days_back: int = 1) -> list[dict]:
    """Fetch BSE corporate announcements for all pharma companies."""
    items = []
    today      = datetime.date.today().strftime("%Y%m%d")
    start_date = (datetime.date.today() - datetime.timedelta(days=days_back)).strftime("%Y%m%d")

    for scrip_code, company_name in PHARMA_COMPANIES.items():
        try:
            url = (
                f"https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w"
                f"?pageno=1&strCat=-1&strPrevDate={start_date}&strScrip={scrip_code}"
                f"&strSearch=P&strToDate={today}&strType=C&subcategory=-1"
            )
            resp = requests.get(url, headers=HEADERS, timeout=10)
            data = resp.json()

            announcements = data.get("Table", []) or []
            for ann in announcements[:10]:
                headline = ann.get("HEADLINE", "").strip()
                dt       = ann.get("DT_TM", "")[:10]
                news_id  = ann.get("NEWSID", "")
                category = ann.get("CATEGORYNAME", "")
                subcategory = ann.get("SUBCATNAME", "")

                if not headline:
                    continue

                link = f"https://www.bseindia.com/xml-data/corpfiling/AttachLive/{news_id}.pdf" if news_id else f"https://www.bseindia.com/corporates/ann.html?scrip={scrip_code}"

                items.append({
                    "title":     f"{company_name}: {headline}",
                    "link":      link,
                    "summary":   f"Category: {category} | Sub: {subcategory} | BSE Code: {scrip_code}",
                    "published": dt,
                    "source":    "BSE Filing",
                    "type":      "filing",
                    "company":   company_name,
                })

            time.sleep(0.2)

        except Exception as e:
            print(f"[BSE] Error for {company_name} ({scrip_code}): {e}")

    # Also try the bulk/general pharma announcement search
    items += _fetch_bse_category_announcements(start_date, today)

    print(f"[BSE] Fetched {len(items)} items")
    return items


def _fetch_bse_category_announcements(start_date: str, today: str) -> list[dict]:
    """Fetch BSE announcements filtered by pharma sector (SIC/industry group)."""
    items = []
    # BSE sector code for Pharmaceuticals
    pharma_sector_urls = [
        # Results & financials
        f"https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w?pageno=1&strCat=Result&strPrevDate={start_date}&strScrip=&strSearch=P&strToDate={today}&strType=C&subcategory=-1",
        # Dividend
        f"https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w?pageno=1&strCat=Dividend&strPrevDate={start_date}&strScrip=&strSearch=P&strToDate={today}&strType=C&subcategory=-1",
        # Board meetings
        f"https://api.bseindia.com/BseIndiaAPI/api/AnnSubCategoryGetData/w?pageno=1&strCat=Board+Meeting&strPrevDate={start_date}&strScrip=&strSearch=P&strToDate={today}&strType=C&subcategory=-1",
    ]

    for url in pharma_sector_urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            for ann in (resp.json().get("Table") or [])[:20]:
                company = ann.get("SLONGNAME", ann.get("NSURL", "")).strip()
                headline = ann.get("HEADLINE", "").strip()
                scrip    = ann.get("SCRIP_CD", "")

                # Only include if company is in our pharma list or keyword match
                is_pharma = (
                    str(scrip) in PHARMA_COMPANIES or
                    any(name.lower() in company.lower() for name in ["pharma", "bio", "lab", "drug", "chem", "medic"])
                )
                if not is_pharma or not headline:
                    continue

                items.append({
                    "title":     f"{company}: {headline}",
                    "link":      f"https://www.bseindia.com/corporates/ann.html?scrip={scrip}",
                    "summary":   f"BSE Code: {scrip}",
                    "published": ann.get("DT_TM", "")[:10],
                    "source":    "BSE Filing",
                    "type":      "filing",
                    "company":   company,
                })
        except Exception as e:
            print(f"[BSE category] Error: {e}")

    return items


def fetch_nse_announcements(days_back: int = 1) -> list[dict]:
    """Fetch NSE corporate announcements via NSE public API."""
    items = []

    NSE_SYMBOLS = [
        "SUNPHARMA", "DRREDDY", "CIPLA", "LUPIN", "DIVISLAB",
        "AUROPHARMA", "BIOCON", "TORNTPHARM", "IPCALAB", "ABBOTINDIA",
        "ALKEM", "NATCOPHARM", "AJANTPHARM", "GRANULES", "PFIZER",
        "GLAXO", "SANOFI", "LAURUSLABS", "GLAND", "WOCKPHARMA",
        "LALPATHLAB", "METROPOLIS", "THYROCARE", "APOLLOHOSP", "MAXHEALTH",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/",
        "Accept-Language": "en-US,en;q=0.9",
    }

    session = requests.Session()
    # Establish session cookie
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
    except Exception:
        pass

    for symbol in NSE_SYMBOLS:
        try:
            url = f"https://www.nseindia.com/api/corp-info?symbol={symbol}&market=capital&corpType=announcement&busDt=-1"
            resp = session.get(url, headers=headers, timeout=10)
            data = resp.json()

            announcements = data if isinstance(data, list) else data.get("data", [])
            for ann in (announcements or [])[:5]:
                subject  = ann.get("subject", ann.get("desc", "")).strip()
                ann_date = ann.get("an_dt", ann.get("date", ""))[:10]
                company  = ann.get("smIndustry", symbol)
                att_file = ann.get("attchmntFile", "")

                if not subject:
                    continue

                link = f"https://www.nseindia.com/api/corp-info?symbol={symbol}"
                if att_file:
                    link = f"https://nsearchives.nseindia.com/corporate/{att_file}"

                items.append({
                    "title":     f"{symbol}: {subject}",
                    "link":      link,
                    "summary":   f"NSE Symbol: {symbol}",
                    "published": ann_date,
                    "source":    "NSE Filing",
                    "type":      "filing",
                    "company":   symbol,
                })

            time.sleep(0.3)

        except Exception as e:
            print(f"[NSE] Error for {symbol}: {e}")

    print(f"[NSE] Fetched {len(items)} items")
    return items
