<div align="center">
  <img src="media/logo.png" alt="LinkedIn Jobs Scraper" width="160"/>
  <h1>🔍 LinkedIn Jobs Scraper</h1>
  <h3><em>LinkedIn jobs without login, without paid APIs, without anti-bot headaches.</em></h3>
</div>

<p align="center">
  <strong>Scrape jobs via LinkedIn's public guest endpoint, generate an HTML dashboard, and run as a Hermes Agent skill — Python stdlib + curl only.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square" alt="Python 3.10+"/></a>
  <a href="https://github.com/felixskmarcio/linkedin-jobs-scraper/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License: MIT"/></a>
  <a href="https://github.com/felixskmarcio/linkedin-jobs-scraper/commits/main"><img src="https://img.shields.io/github/last-commit/felixskmarcio/linkedin-jobs-scraper?style=flat-square" alt="Last commit"/></a>
  <a href="https://github.com/felixskmarcio/linkedin-jobs-scraper/stargazers"><img src="https://img.shields.io/github/stars/felixskmarcio/linkedin-jobs-scraper?style=social" alt="GitHub stars"/></a>
</p>

<p align="center">
  <a href="./README.md">Português</a> · <strong>English</strong>
</p>

> [!NOTE]
> Tested and validated on **08/28/2026**: 48 real jobs from Brazil collected in ~8 seconds, without cookies and without login.

---

## Table of Contents

- [🤔 Why this scraper?](#-why-this-scraper)
- [⚡ Quick Start](#-quick-start)
- [🚀 Usage](#-usage)
- [🤖 Hermes Agent Integration](#-hermes-agent-integration)
- [📂 Repository Structure](#-repository-structure)
- [📚 Documentation](#-documentation)
- [🔧 Prerequisites](#-prerequisites)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🤔 Why this scraper?

LinkedIn maintains a **public and unauthenticated** endpoint powering its public job search page:

```
GET https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search
    ?keywords=Systems+Analyst
    &geoId=106057199        ← Brazil (use geoId, NOT location=Brazil)
    &f_WT=2                 ← 1=onsite, 2=remote, 3=hybrid
    &f_TPR=r86400           ← r86400=24h, r604800=week, r2592000=month
    &start=0                ← pagination in chunks of ~10
```

Returns **HTML with job cards** (not JSON) — parsed with regex/BeautifulSoup.

### How it compares

| Approach | Result |
|---|---|
| `linkedin.com/jobs/search` via browser | ❌ Authwall (login required) |
| Programmatic login | ❌ Security checkpoint (anti-bot challenge) |
| Authenticated Voyager API | ❌ 404 (migrated to internal GraphQL) |
| **jobs-guest API** | ✅ **200 OK, no auth, no cookies** |

### ⚠️ Location filter catch

- `location=Brasil` → **returns US jobs** (ignored/wrong)
- `location=Brazil` → works partially
- `geoId=106057199` → ✅ **works reliably** (official LinkedIn geoId for Brazil)

Other useful geoIds: São Paulo=`106890317`, Rio de Janeiro=`106867723`. Discover others at `linkedin.com/jobs/search` while logged in, checking the `geoId` parameter in the URL.

---

## ⚡ Quick Start

```bash
git clone https://github.com/felixskmarcio/linkedin-jobs-scraper.git
cd linkedin-jobs-scraper
bash install.sh
```

Or minimal manual installation:

```bash
pip install websocket-client   # only required for cookie injection
# scrape_jobs.py uses standard library + curl only
```

**Immediate test (zero configuration needed):**

```bash
python3 scripts/scrape_jobs.py --keywords "Software Engineer" --geoId 106057199 --remote --last24h
```

Output: `data/linkedin_jobs.json` with collected jobs.

<details>
<summary><strong>Output example (JSON)</strong></summary>

```json
[
  {
    "title": "Senior Systems Analyst",
    "company": "Company XYZ",
    "location": "São Paulo, SP",
    "url": "https://www.linkedin.com/jobs/view/..."
  }
]
```

</details>

---

## 🚀 Usage

### 1. Scrape jobs (guest mode — recommended)

```bash
# Systems Analyst, Brazil, remote, last 24h, 5 pages
python3 scripts/scrape_jobs.py \
  --keywords "Systems Analyst" \
  --geoId 106057199 \
  --remote \
  --last24h \
  --pages 5 \
  --out data/jobs.json
```

**Options:**

| Flag | Default | Description |
|---|---|---|
| `--keywords` | `Analista de Sistemas` | Search query term |
| `--geoId` | `106057199` | LinkedIn geoId (Brazil) |
| `--remote` | off | f_WT=2 (remote / home office) |
| `--hybrid` | off | f_WT=3 (hybrid) |
| `--onsite` | off | f_WT=1 (onsite) |
| `--last24h` | off | f_TPR=r86400 (past 24 hours) |
| `--week` | off | f_TPR=r604800 (past week) |
| `--month` | off | f_TPR=r2592000 (past month) |
| `--pages` | 5 | Pages to scrape (~10 jobs per page) |
| `--out` | `data/linkedin_jobs.json` | Output JSON file path |

### 2. Generate HTML dashboard

```bash
python3 scripts/generate_dashboard.py data/jobs.json data/dashboard.html
```

### 3. Logged-in mode (advanced — cookies)

For features requiring an active session (apply for jobs, full profile inspection), see **[docs/COOKIES.md](docs/COOKIES.md)**.

---

## 🤖 Hermes Agent Integration

This repository is registered as a **Hermes skill** (`linkedin-jobs-scraper`). The agent automatically detects when you ask for LinkedIn jobs and triggers these scripts.

It also works via **Hermes cron** for daily automated monitoring:

```
You:    "Schedule daily job scraping for Systems Analyst at 8 AM"
Hermes: creates cronjob that runs scrape_jobs.py + generate_dashboard.py
```

---

## 📂 Repository Structure

```
linkedin-jobs-scraper/
├── README.md                      ← Portuguese documentation
├── README.en.md                   ← English documentation
├── LICENSE                        ← MIT License
├── CONTRIBUTING.md                ← Contribution guidelines
├── install.sh                     ← Dependency installer & smoke test
├── requirements.txt
├── scripts/
│   ├── scrape_jobs.py             ← Main scraper (guest API, no login)
│   ├── generate_dashboard.py      ← Generates HTML jobs dashboard
│   └── inject_cookies.py          ← Injects cookies into Chrome via CDP (logged-in mode)
├── docs/
│   ├── ENDPOINTS.md               ← Endpoints reference and parameters
│   ├── COOKIES.md                 ← Cookie export/injection guide
│   ├── SECURITY_AUDIT.md          ← OWASP Top 10 security audit report
│   └── RECOVERY.md                ← Reinstallation from scratch
├── examples/
│   └── linkedin_cookies.example.json
├── media/                         ← Logo and visual assets
└── data/                          ← Generated output (JSON/HTML)
```

---

## 📚 Documentation

| Document | Content |
|---|---|
| [docs/ENDPOINTS.md](docs/ENDPOINTS.md) | Complete guest endpoint reference, parameters, and geoIds |
| [docs/COOKIES.md](docs/COOKIES.md) | Export Chrome cookies and inject via CDP (logged-in mode) |
| [docs/RECOVERY.md](docs/RECOVERY.md) | Reinstall everything from scratch in 4 steps |
| [docs/SECURITY_AUDIT.md](docs/SECURITY_AUDIT.md) | Full OWASP Top 10 security audit report |

---

## 🔧 Prerequisites

- Python 3.10+
- `curl` available in PATH
- `websocket-client` — only for logged-in mode (`inject_cookies.py`)
- Google Chrome — only for logged-in mode

---

## 🤝 Contributing

Issues and Pull Requests are welcome. Before opening a PR:

1. Run the smoke test from [Quick Start](#-quick-start) and confirm that JSON data was generated.
2. If changing endpoint parameters, update `docs/ENDPOINTS.md` as well.
3. Describe in your PR what was tested and on what date (LinkedIn changes its HTML without notice).

See [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines.

---

## ⚖️ Disclaimers

- The guest endpoint is **public** (powers the public job search page without login), but heavy usage may trigger rate limits. Best practice: respect delay between pages (built into the script) and keep requests moderate.
- Scraping authenticated private areas may violate LinkedIn Terms of Service (section 8.2). Guest mode only queries publicly available listings.
- Never commit real `linkedin_cookies.json` — it contains your private session token `li_at`.

---

## 📄 License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  Made by <a href="https://github.com/felixskmarcio">@felixskmarcio</a> · If this project helped you, please leave a ⭐
</p>
