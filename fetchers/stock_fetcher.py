"""
Stock Price Fetcher — Indian Pharma Companies (NSE)
----------------------------------------------------
Uses the `yfinance` library which correctly handles Yahoo Finance
authentication (crumb + cookie session). This is the most reliable
free method for NSE stock data.

Install: pip install yfinance (added to requirements.txt)
"""

import datetime
import time

# ── All major NSE-listed pharma & healthcare companies ──────────────────────
PHARMA_STOCKS = [
    # Large Cap Pharma
    ("SUNPHARMA.NS",   "Sun Pharmaceutical"),
    ("DRREDDY.NS",     "Dr. Reddy's Laboratories"),
    ("CIPLA.NS",       "Cipla"),
    ("LUPIN.NS",       "Lupin"),
    ("DIVISLAB.NS",    "Divis Laboratories"),
    ("AUROPHARMA.NS",  "Aurobindo Pharma"),
    ("BIOCON.NS",      "Biocon"),
    ("TORNTPHARM.NS",  "Torrent Pharmaceuticals"),
    ("IPCALAB.NS",     "IPCA Laboratories"),
    ("ALKEM.NS",       "Alkem Laboratories"),
    # Mid Cap Pharma
    ("ABBOTINDIA.NS",  "Abbott India"),
    ("NATCOPHARM.NS",  "Natco Pharma"),
    ("AJANTPHARM.NS",  "Ajanta Pharma"),
    ("GRANULES.NS",    "Granules India"),
    ("LAURUSLABS.NS",  "Laurus Labs"),
    ("GLAND.NS",       "Gland Pharma"),
    ("WOCKPHARMA.NS",  "Wockhardt"),
    ("JUBILANT.NS",    "Jubilant Pharmova"),
    ("MARKSANS.NS",    "Marksans Pharma"),
    ("INDOCO.NS",      "Indoco Remedies"),
    ("JBCHEPHARM.NS",  "JB Chemicals & Pharma"),
    ("ERIS.NS",        "Eris Lifesciences"),
    ("CAPLIPOINT.NS",  "Caplin Point Laboratories"),
    ("ZYDUSLIFE.NS",   "Zydus Lifesciences"),
    ("GLENMARK.NS",    "Glenmark Pharmaceuticals"),
    ("MANKIND.NS",     "Mankind Pharma"),
    # MNC Pharma in India
    ("PFIZER.NS",      "Pfizer India"),
    ("GLAXO.NS",       "GSK Pharma India"),
    ("SANOFI.NS",      "Sanofi India"),
    # API / Specialty
    ("LAURUSLABS.NS",  "Laurus Labs"),
    ("SEQUENT.NS",     "Sequent Scientific"),
    ("SOLARA.NS",      "Solara Active Pharma"),
    ("FDC.NS",         "FDC Limited"),
    ("SUVEN.NS",       "Suven Pharmaceuticals"),
    # Diagnostics / Healthcare
    ("LALPATHLAB.NS",  "Dr. Lal PathLabs"),
    ("METROPOLIS.NS",  "Metropolis Healthcare"),
    ("APOLLOHOSP.NS",  "Apollo Hospitals"),
    ("MAXHEALTH.NS",   "Max Healthcare"),
]

# De-duplicate the list while preserving order
_seen = set()
_deduped = []
for sym, name in PHARMA_STOCKS:
    if sym not in _seen:
        _seen.add(sym)
        _deduped.append((sym, name))
PHARMA_STOCKS = _deduped


def fetch_stock_prices() -> list[dict]:
    """
    Fetch previous close, current price, day change, and 52W range
    for all NSE pharma stocks using yfinance.

    yfinance handles Yahoo Finance cookie/crumb auth automatically.
    Returns a list of dicts sorted by absolute % change (biggest movers first).
    """
    try:
        import yfinance as yf
    except ImportError:
        print("[Stocks] yfinance not installed. Run: pip install yfinance")
        return []

    stocks = []
    symbols = [sym for sym, _ in PHARMA_STOCKS]
    name_map = {sym: name for sym, name in PHARMA_STOCKS}

    print(f"[Stocks] Fetching {len(symbols)} symbols via yfinance...")

    try:
        # Batch download — much faster than one-by-one, and yfinance
        # handles the Yahoo Finance session internally
        tickers = yf.Tickers(" ".join(symbols))

        for symbol in symbols:
            try:
                ticker = tickers.tickers[symbol]
                info   = ticker.fast_info          # lightweight, no heavy scraping

                # fast_info fields (reliable):
                #   last_price, previous_close, open, day_high, day_low
                #   fifty_two_week_high, fifty_two_week_low
                #   market_cap, currency, exchange

                current_price = getattr(info, "last_price",      None)
                prev_close    = getattr(info, "previous_close",  None)
                week_high     = getattr(info, "fifty_two_week_high", None)
                week_low      = getattr(info, "fifty_two_week_low",  None)
                market_cap    = getattr(info, "market_cap",      None)
                day_high      = getattr(info, "day_high",        None)
                day_low       = getattr(info, "day_low",         None)
                currency      = getattr(info, "currency",        "INR")

                # Skip if we couldn't get core data
                if current_price is None or prev_close is None:
                    print(f"[Stocks] No data for {symbol}, skipping")
                    continue

                # Correct calculation of day change
                change     = round(current_price - prev_close, 2)
                change_pct = round((change / prev_close) * 100, 2) if prev_close else 0.0

                stocks.append({
                    "symbol":       symbol.replace(".NS", ""),
                    "name":         name_map.get(symbol, symbol),
                    "price":        round(current_price, 2),
                    "prev_close":   round(prev_close, 2),
                    "change":       change,
                    "change_pct":   change_pct,
                    "day_high":     round(day_high, 2)    if day_high  else None,
                    "day_low":      round(day_low, 2)     if day_low   else None,
                    "week_high_52": round(week_high, 2)   if week_high else None,
                    "week_low_52":  round(week_low, 2)    if week_low  else None,
                    "market_cap":   market_cap,
                    "currency":     currency,
                    "as_of":        datetime.date.today().isoformat(),
                })

            except Exception as e:
                print(f"[Stocks] Error for {symbol}: {e}")
                continue

    except Exception as e:
        print(f"[Stocks] Batch fetch error: {e}")

    # Sort by absolute % change — biggest movers at the top
    stocks.sort(key=lambda x: abs(x["change_pct"]), reverse=True)

    print(f"[Stocks] Successfully fetched {len(stocks)} / {len(symbols)} stocks")
    return stocks
