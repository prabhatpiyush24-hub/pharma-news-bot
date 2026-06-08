"""
Digest Builder — tabbed HTML digest for Indian pharma investors.
Tabs: Stock Prices | BSE/NSE Filings | Results | Deals | Corporate Actions | Operations | Analyst | News
"""

import datetime
import os

CATEGORIES = [
    ("📊 BSE / NSE Filings",         ["BSE Filing", "NSE Filing"]),
    ("💰 Results & Financials",       ["quarterly results", "q1", "q2", "q3", "q4", "net profit",
                                       "revenue", "ebitda", "earnings", "annual results", "pat"]),
    ("🤝 Deals, M&A & Partnerships",  ["acquisition", "merger", "deal", "mou", "agreement",
                                       "partnership", "joint venture", "licensing", "divestment"]),
    ("💸 Corporate Actions",          ["dividend", "bonus", "buyback", "stock split", "rights issue",
                                       "agm", "egm", "record date", "ex-date", "qip"]),
    ("🏭 Operations & Approvals",     ["plant", "facility", "expansion", "launch", "capacity",
                                       "usfda", "anda", "who-gmp", "cdsco", "approval", "export"]),
    ("📉 Analyst & Brokerage Calls",  ["target price", "buy", "sell", "hold", "upgrade",
                                       "downgrade", "analyst", "brokerage", "rating"]),
    ("📰 Industry & Policy News",     []),
]

SOURCE_CATEGORY_MAP = {
    "BSE Filing": "📊 BSE / NSE Filings",
    "NSE Filing": "📊 BSE / NSE Filings",
}


def categorise(item: dict) -> str:
    if item.get("source", "") in SOURCE_CATEGORY_MAP:
        return SOURCE_CATEGORY_MAP[item["source"]]
    text = (item.get("title", "") + " " + item.get("summary", "")).lower()
    for cat_name, keywords in CATEGORIES:
        for kw in keywords:
            if kw.lower() in text:
                return cat_name
    return "📰 Industry & Policy News"


def _fmt_mcap(val) -> str:
    if not val:
        return "—"
    cr = val / 1e7  # convert to crores
    if cr >= 100000:
        return f"₹{cr/100000:.1f}L Cr"
    if cr >= 1000:
        return f"₹{cr/1000:.1f}K Cr"
    return f"₹{cr:.0f} Cr"


def _fmt_price(val) -> str:
    if val is None:
        return "—"
    return f"₹{val:,.2f}"


def build_html(items: list[dict], stocks: list[dict], output_dir: str = "digests") -> str:
    today = datetime.date.today().isoformat()
    os.makedirs(output_dir, exist_ok=True)

    # ── Stock table ───────────────────────────────────────────────────────
    stock_rows = ""
    for s in stocks:
        chg     = s.get("change_pct", 0.0)
        chg_abs = s.get("change", 0.0)
        sign    = "+" if chg >= 0 else ""
        color   = "#1a7a4a" if chg >= 0 else "#c0392b"
        arrow   = "▲" if chg >= 0 else "▼"

        price     = _fmt_price(s.get("price"))
        prev_cl   = _fmt_price(s.get("prev_close"))
        d_high    = _fmt_price(s.get("day_high"))
        d_low     = _fmt_price(s.get("day_low"))
        w52h      = _fmt_price(s.get("week_high_52"))
        w52l      = _fmt_price(s.get("week_low_52"))
        mcap      = _fmt_mcap(s.get("market_cap"))

        # Highlight rows near 52W high/low
        near_high = (s.get("week_high_52") and s.get("price") and
                     s["price"] >= s["week_high_52"] * 0.97)
        near_low  = (s.get("week_low_52") and s.get("price") and
                     s["price"] <= s["week_low_52"] * 1.03)
        row_cls   = "near-high" if near_high else ("near-low" if near_low else "")

        stock_rows += f"""
        <tr class="{row_cls}">
          <td><strong>{_esc(s['symbol'])}</strong></td>
          <td class="co-name">{_esc(s['name'])}</td>
          <td class="num"><strong>{price}</strong></td>
          <td class="num" style="color:{color};font-weight:600">{arrow} {sign}{chg:.2f}%</td>
          <td class="num" style="color:{color}">{sign}{_fmt_price(chg_abs)}</td>
          <td class="num">{prev_cl}</td>
          <td class="num">{d_high}</td>
          <td class="num">{d_low}</td>
          <td class="num">{w52h}</td>
          <td class="num">{w52l}</td>
          <td class="num">{mcap}</td>
        </tr>"""

    stocks_html = f"""
    <div class="section" id="tab_stocks">
      <h2>📈 Indian Pharma — NSE Stock Prices <span class="count">{len(stocks)}</span></h2>
      <p class="note">
        Prices in ₹ (INR) &nbsp;·&nbsp; Source: Yahoo Finance / NSE &nbsp;·&nbsp; As of {today}
        &nbsp;&nbsp;
        <span class="legend green-leg">■ Near 52W High</span>
        &nbsp;
        <span class="legend red-leg">■ Near 52W Low</span>
      </p>
      <div class="table-wrap">
        <table class="stock-table">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Company</th>
              <th class="num">Price (₹)</th>
              <th class="num">Change %</th>
              <th class="num">Change (₹)</th>
              <th class="num">Prev Close</th>
              <th class="num">Day High</th>
              <th class="num">Day Low</th>
              <th class="num">52W High</th>
              <th class="num">52W Low</th>
              <th class="num">Mkt Cap</th>
            </tr>
          </thead>
          <tbody>{stock_rows}</tbody>
        </table>
      </div>
    </div>"""

    # ── News sections ─────────────────────────────────────────────────────
    sections: dict[str, list[dict]] = {cat: [] for cat, _ in CATEGORIES}
    for item in items:
        sections[categorise(item)].append(item)

    news_html = ""
    for cat_name, _ in CATEGORIES:
        cat_items = sections.get(cat_name, [])
        if not cat_items:
            continue
        tab_id = _tab_id(cat_name)
        cards  = ""
        for item in cat_items:
            title  = _esc(item.get("title", "No title"))
            link   = _esc(item.get("link", "#"))
            summ   = _esc(item.get("summary", ""))[:300]
            source = _esc(item.get("source", ""))
            pub    = item.get("published", "")[:10]
            is_fil = source in ("BSE Filing", "NSE Filing")
            badge_bg = "#1a5276" if is_fil else "#546e7a"
            cards += f"""
            <div class="card">
              <a class="card-title" href="{link}" target="_blank" rel="noopener">{title}</a>
              {"<p class='card-summary'>" + summ + "</p>" if summ else ""}
              <div class="card-meta">
                <span class="badge" style="background:{badge_bg}">{source}</span>
                {"<span class='date'>" + pub + "</span>" if pub else ""}
              </div>
            </div>"""

        news_html += f"""
        <div class="section" id="{tab_id}">
          <h2>{cat_name} <span class="count">{len(cat_items)}</span></h2>
          <div class="cards">{cards}</div>
        </div>"""

    # ── Tabs nav ──────────────────────────────────────────────────────────
    tab_items = [("tab_stocks", f"📈 Stocks ({len(stocks)})")]
    for cat_name, _ in CATEGORIES:
        cnt = len(sections.get(cat_name, []))
        if cnt:
            tab_items.append((_tab_id(cat_name), f"{cat_name} ({cnt})"))

    tabs_nav = "".join(
        f'<button class="tab-btn" onclick="showTab(\'{tid}\')" id="btn-{tid}">{label}</button>'
        for tid, label in tab_items
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>India Pharma Digest — {today}</title>
<style>
  :root{{--bg:#f0f4f8;--surface:#fff;--border:#dde3ea;--primary:#1a3a5c;
        --accent:#1565c0;--muted:#607d8b;--green:#1a7a4a;--red:#c0392b;}}
  *{{box-sizing:border-box;margin:0;padding:0;}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
       background:var(--bg);color:#1a1a2e;line-height:1.6;}}

  /* Header */
  header{{background:var(--primary);color:#fff;padding:1.2rem 2rem;
          display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:.8rem;}}
  header h1{{font-size:1.4rem;font-weight:700;}}
  header .meta{{font-size:.82rem;opacity:.8;}}

  /* Tabs */
  .tabs{{background:#122740;padding:0 1rem;overflow-x:auto;display:flex;
         scrollbar-width:none;border-top:1px solid rgba(255,255,255,.08);}}
  .tabs::-webkit-scrollbar{{display:none;}}
  .tab-btn{{background:none;border:none;color:rgba(255,255,255,.65);
            padding:.65rem 1rem;font-size:.8rem;cursor:pointer;white-space:nowrap;
            border-bottom:3px solid transparent;transition:all .18s;}}
  .tab-btn:hover{{color:#fff;background:rgba(255,255,255,.06);}}
  .tab-btn.active{{color:#fff;border-bottom-color:#64b5f6;font-weight:600;}}

  /* Layout */
  .container{{max-width:1400px;margin:0 auto;padding:1.5rem 1rem;}}
  .section{{margin-bottom:2rem;}}
  h2{{font-size:1.1rem;font-weight:700;color:var(--primary);
      border-left:4px solid var(--accent);padding-left:.75rem;
      margin-bottom:.9rem;display:flex;align-items:center;gap:.5rem;}}
  .count{{background:var(--accent);color:#fff;border-radius:99px;
          font-size:.7rem;padding:.1rem .45rem;}}
  .note{{font-size:.8rem;color:var(--muted);margin-bottom:.75rem;}}
  .legend{{font-size:.78rem;font-weight:600;}}
  .green-leg{{color:var(--green);}}
  .red-leg  {{color:var(--red);}}

  /* Stock table */
  .table-wrap{{overflow-x:auto;border-radius:8px;border:1px solid var(--border);}}
  .stock-table{{width:100%;border-collapse:collapse;font-size:.82rem;}}
  .stock-table th{{background:var(--primary);color:#fff;padding:.6rem .75rem;
                   text-align:left;white-space:nowrap;font-weight:600;}}
  .stock-table td{{padding:.5rem .75rem;border-bottom:1px solid var(--border);
                   white-space:nowrap;}}
  .stock-table tbody tr:last-child td{{border-bottom:none;}}
  .stock-table tbody tr:hover td{{background:#f0f6ff;}}
  .stock-table tr.near-high td{{background:#e8f5e9;}}
  .stock-table tr.near-low  td{{background:#fdecea;}}
  .co-name{{max-width:160px;overflow:hidden;text-overflow:ellipsis;}}
  .num{{text-align:right;font-variant-numeric:tabular-nums;font-family:'SF Mono',Consolas,monospace;}}

  /* News cards */
  .cards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:.85rem;}}
  .card{{background:var(--surface);border:1px solid var(--border);border-radius:9px;
         padding:.95rem;display:flex;flex-direction:column;gap:.4rem;
         transition:box-shadow .15s;}}
  .card:hover{{box-shadow:0 3px 14px rgba(0,0,0,.09);}}
  .card-title{{font-weight:600;color:var(--accent);text-decoration:none;
               font-size:.88rem;line-height:1.45;}}
  .card-title:hover{{text-decoration:underline;}}
  .card-summary{{font-size:.8rem;color:#444;line-height:1.5;}}
  .card-meta{{display:flex;gap:.4rem;align-items:center;flex-wrap:wrap;margin-top:.15rem;}}
  .badge{{color:#fff;font-size:.7rem;padding:.12rem .45rem;border-radius:4px;font-weight:500;}}
  .date{{font-size:.7rem;color:var(--muted);}}

  footer{{text-align:center;padding:1.5rem;color:var(--muted);font-size:.78rem;}}
</style>
</head>
<body>
<header>
  <div>
    <h1>🏥 India Pharma Investor Digest</h1>
    <div class="meta">NSE · BSE · News · Filings</div>
  </div>
  <div class="meta">{today} &nbsp;·&nbsp; {len(stocks)} stocks &nbsp;·&nbsp; {len(items)} news items</div>
</header>
<nav class="tabs" id="tabNav">{tabs_nav}</nav>
<div class="container">
  {stocks_html}
  {news_html}
</div>
<footer>
  Auto-generated by india-pharma-digest &nbsp;·&nbsp;
  {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} &nbsp;·&nbsp;
  Data: Yahoo Finance, BSE, NSE, Economic Times, Moneycontrol
</footer>
<script>
  function showTab(id) {{
    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    var el  = document.getElementById(id);
    var btn = document.getElementById('btn-' + id);
    if (el)  el.style.display  = 'block';
    if (btn) btn.classList.add('active');
    // Scroll tab button into view
    if (btn) btn.scrollIntoView({{block:'nearest',inline:'center',behavior:'smooth'}});
  }}
  document.addEventListener('DOMContentLoaded', function() {{ showTab('tab_stocks'); }});
</script>
</body>
</html>"""

    html_path   = os.path.join(output_dir, f"{today}.html")
    latest_path = os.path.join(output_dir, "index.html")
    for p in (html_path, latest_path):
        with open(p, "w", encoding="utf-8") as f:
            f.write(html)

    print(f"[Digest] HTML written → {html_path}")
    return html_path


def build_markdown(items: list[dict], output_dir: str = "digests") -> str:
    today = datetime.date.today().isoformat()
    os.makedirs(output_dir, exist_ok=True)

    sections: dict[str, list[dict]] = {cat: [] for cat, _ in CATEGORIES}
    for item in items:
        sections[categorise(item)].append(item)

    lines = [f"# 🏥 India Pharma Investor Digest — {today}", "",
             f"> {len(items)} items · {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", ""]

    for cat_name, _ in CATEGORIES:
        cat_items = sections.get(cat_name, [])
        if not cat_items:
            continue
        lines += [f"## {cat_name} ({len(cat_items)})", ""]
        for item in cat_items:
            lines.append(f"### [{item.get('title','No title')}]({item.get('link','#')})")
            if item.get("summary"):
                lines += [item["summary"], ""]
            meta = []
            if item.get("source"):    meta.append(f"**Source:** {item['source']}")
            if item.get("published"): meta.append(f"**Date:** {item['published'][:10]}")
            if meta: lines += ["  ".join(meta), ""]
        lines += ["---", ""]

    content = "\n".join(lines)
    for p in (os.path.join(output_dir, f"{today}.md"), os.path.join(output_dir, "latest.md")):
        with open(p, "w", encoding="utf-8") as f:
            f.write(content)

    md_path = os.path.join(output_dir, f"{today}.md")
    print(f"[Digest] Markdown written → {md_path}")
    return md_path


def _tab_id(cat_name: str) -> str:
    return "tab_" + "".join(c if c.isalnum() else "_" for c in cat_name)


def _esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;")
                .replace(">", "&gt;").replace('"', "&quot;"))
