"""
main.py — India Pharma News Bot

Sources:
  - BSE corporate announcements (filings, results, dividends, board meetings)
  - NSE corporate announcements
  - Indian business news RSS (ET, Mint, BS, Moneycontrol, PharmaBiz, etc.)
  - NSE stock prices via Yahoo Finance (last close, change, 52W range, mcap)

Run locally:
  python main.py
  DAYS_BACK=3 python main.py
  SMTP_USER=you@gmail.com SMTP_PASS=xxxx EMAIL_TO=you@gmail.com python main.py
"""

import os
import sys
import datetime

from fetchers.rss_fetcher   import fetch_rss
from fetchers.bse_fetcher   import fetch_bse_announcements, fetch_nse_announcements
from fetchers.stock_fetcher import fetch_stock_prices

from processor      import process
from digest_builder import build_html, build_markdown
from emailer        import send_digest


def main():
    days_back = int(os.environ.get("DAYS_BACK", "1"))
    print(f"\n{'='*60}")
    print(f"  India Pharma Bot — {datetime.date.today()}  (days_back={days_back})")
    print(f"{'='*60}\n")

    # ── 1. Fetch news & filings ──────────────────────────────────
    print("[Step 1/4] Fetching news & filings...")
    all_items = []
    all_items += fetch_rss(days_back=days_back)
    all_items += fetch_bse_announcements(days_back=days_back)
    all_items += fetch_nse_announcements(days_back=days_back)
    print(f"\n  Raw items: {len(all_items)}\n")

    # ── 2. Fetch stock prices ─────────────────────────────────────
    print("[Step 2/4] Fetching stock prices...")
    stocks = fetch_stock_prices()
    print()

    # ── 3. Process news ───────────────────────────────────────────
    print("[Step 3/4] Processing & filtering...")
    processed = process(all_items)
    print(f"  Final news count: {len(processed)}\n")

    # ── 4. Build outputs ──────────────────────────────────────────
    print("[Step 4/4] Building digest...")
    html_path = build_html(processed, stocks)
    md_path   = build_markdown(processed)

    # ── 5. Email (optional) ───────────────────────────────────────
    send_digest(html_path, md_path)

    print(f"\n{'='*60}")
    print(f"  Done!")
    print(f"    HTML  → {html_path}")
    print(f"    MD    → {md_path}")
    print(f"    Stocks tracked: {len(stocks)}")
    print(f"    News items: {len(processed)}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
