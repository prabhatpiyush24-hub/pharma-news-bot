# 🏥 India Pharma Investor Digest

Free, automated daily digest of Indian pharma companies — BSE/NSE filings, stock prices, news, results, and deals. Runs on GitHub Actions, no paid APIs.

---

## What you get

| Tab | Content |
|---|---|
| 📈 Stock Prices | Live closing prices, % change, 52W high/low, market cap for 35+ NSE pharma stocks |
| 📊 BSE/NSE Filings | Board meetings, results, dividends, shareholding changes, insider trading |
| 💰 Results & Financials | Quarterly results, profit/revenue coverage from ET, Mint, BS |
| 🤝 Deals & M&A | Acquisitions, licensing deals, partnerships |
| 💸 Corporate Actions | Dividends, buybacks, stock splits, QIPs, rights issues |
| 🏭 Operations & Approvals | Plant expansions, USFDA/CDSCO approvals, new launches |
| 📉 Analyst Calls | Brokerage upgrades/downgrades, target price revisions |
| 📰 Industry News | Policy, NPPA pricing, exports, general developments |

**Companies tracked (35+):** Sun Pharma, Dr. Reddy's, Cipla, Lupin, Divi's, Aurobindo, Biocon, Torrent, IPCA, Alkem, Laurus, Gland, Zydus, Mankind, Glenmark, and more.

---

## Quick start (local)

```bash
# 1. Clone
git clone https://github.com/YOURUSERNAME/india-pharma-digest.git
cd india-pharma-digest

# 2. Install (only 2 packages needed)
pip install -r requirements.txt

# 3. Run
python main.py

# Open your digest
open digests/index.html    # macOS
# or just double-click the file in Windows/Linux
```

---

## GitHub Actions setup (automated, free)

### 1. Push to GitHub
```bash
git init && git add . && git commit -m "init"
git branch -M main
git remote add origin https://github.com/YOURUSERNAME/india-pharma-digest.git
git push -u origin main
```

### 2. Add email secrets (optional)
Repo → **Settings → Secrets → Actions → New repository secret**

| Secret | Value |
|---|---|
| `SMTP_USER` | your Gmail (e.g. you@gmail.com) |
| `SMTP_PASS` | Gmail App Password (16 chars) — NOT your account password |
| `EMAIL_TO` | destination email |

Get App Password: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

### 3. Enable GitHub Pages (browse digest in browser)
Repo → **Settings → Pages → Branch: main → Folder: /digests**

Browse at: `https://YOURUSERNAME.github.io/india-pharma-digest/`

### 4. First run
Repo → **Actions → India Pharma Daily Digest → Run workflow**

**Schedule:** Runs automatically at **9:30 AM IST** (market open) and **5:30 PM IST** (market close), Monday–Friday.

---

## Customise

**Add/remove stocks** — edit `PHARMA_STOCKS` in `fetchers/stock_fetcher.py`

**Add/remove news sources** — edit `FEEDS` in `fetchers/rss_fetcher.py`

**Add/remove companies for filing tracking** — edit `PHARMA_COMPANIES` in `fetchers/bse_fetcher.py`

**Adjust keyword filters** — edit `processor.py`

---

## Project files

```
india-pharma-digest/
├── .github/workflows/daily_digest.yml   ← Runs at 9:30 AM + 5:30 PM IST Mon-Fri
├── fetchers/
│   ├── rss_fetcher.py     ← ET, Mint, BS, Moneycontrol, PharmaBiz, Google News
│   ├── bse_fetcher.py     ← BSE + NSE corporate filings API
│   └── stock_fetcher.py   ← Yahoo Finance closing prices for 35+ NSE pharma stocks
├── processor.py           ← Filters to India-relevant news, deduplicates, scores
├── digest_builder.py      ← Tabbed HTML + Markdown output
├── emailer.py             ← Gmail SMTP delivery
├── main.py                ← Entry point
└── digests/               ← Output: index.html + YYYY-MM-DD.html + .md
```

---

MIT License
"# pharma-news-bot" 
