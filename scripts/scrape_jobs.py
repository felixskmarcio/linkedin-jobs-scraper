#!/usr/bin/env python3
"""
LinkedIn Jobs Scraper — guest API (no login required).

Uses the public guest endpoint that powers LinkedIn's public jobs page:
  /jobs-guest/jobs/api/seeMoreJobPostings/search

No cookies, no auth, no browser. Just curl + HTML parsing.

Usage:
    python3 scrape_jobs.py --keywords "Analista de Sistemas" --geoId 106057199 --remote --last24h --pages 5
"""
import argparse
import html as html_mod
import json
import os
import re
import subprocess
import sys
import time
from urllib.parse import quote_plus

GUEST_ENDPOINT = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36"
)

# Common geoIds (discover others via linkedin.com/jobs/search URL while logged in)
GEOIDS = {
    "brasil": "106057199",
    "brazil": "106057199",
    "sao-paulo": "106890317",
    "rio-de-janeiro": "106867723",
}

WORK_MODES = {"onsite": "1", "remote": "2", "hybrid": "3"}
TIME_RANGES = {"last24h": "r86400", "week": "r604800", "month": "r2592000"}


def fetch_page(url: str) -> str:
    """Fetch one results page via curl (subprocess keeps us stdlib-only)."""
    cmd = [
        "curl", "-s", "-m", "20", url,
        "-H", f"User-Agent: {USER_AGENT}",
        "-H", "Accept: application/json, text/plain, */*",
        "-H", "x-li-lang: pt_BR",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    return r.stdout


def clean(text: str) -> str:
    return html_mod.unescape(text).strip()


def parse_jobs(html: str) -> list[dict]:
    """Extract job cards from guest-API HTML."""
    ids = re.findall(r'data-entity-urn="urn:li:jobPosting:(\d+)"', html)
    titles = re.findall(r'<h3 class="base-search-card__title">\s*(.*?)\s*</h3>', html, re.DOTALL)
    companies = re.findall(r'<h4 class="base-search-card__subtitle">\s*<a[^>]*>(.*?)</a>', html, re.DOTALL)
    locations = re.findall(r'<span class="job-search-card__location"[^>]*>(.*?)</span>', html, re.DOTALL)
    # Links may use regional hosts (br.linkedin.com, www.linkedin.com, ...)
    links = re.findall(r'<a class="base-card__full-link[^"]*" href="(https://[a-z.]*linkedin\.com/jobs/view/[^"]+)"', html)
    dates = re.findall(r'<time class="job-search-card__listdate[^"]*"[^>]*datetime="([^"]+)"', html)
    salaries = re.findall(r'<span class="job-search-card__salary-info"[^>]*>(.*?)</span>', html, re.DOTALL)

    jobs = []
    for i, title in enumerate(titles):
        jobs.append({
            "id": ids[i] if i < len(ids) else None,
            "title": clean(re.sub(r"<[^>]+>", "", title)),
            "company": clean(re.sub(r"<[^>]+>", "", companies[i])) if i < len(companies) else None,
            "location": clean(re.sub(r"<[^>]+>", "", locations[i])) if i < len(locations) else None,
            "link": links[i].split("?")[0] if i < len(links) else None,  # strip tracking params
            "posted": dates[i] if i < len(dates) else None,
            "salary": clean(re.sub(r"<[^>]+>", "", salaries[i])) if i < len(salaries) else None,
        })
    return jobs


def build_url(keywords: str, geo_id: str, work_mode: str | None,
              time_range: str | None, start: int) -> str:
    params = [f"keywords={quote_plus(keywords)}", f"geoId={geo_id}", f"start={start}"]
    if work_mode:
        params.append(f"f_WT={WORK_MODES[work_mode]}")
    if time_range:
        params.append(f"f_TPR={TIME_RANGES[time_range]}")
    return f"{GUEST_ENDPOINT}?{'&'.join(params)}"


def main() -> int:
    p = argparse.ArgumentParser(description="LinkedIn Jobs guest-API scraper")
    p.add_argument("--keywords", default="Analista de Sistemas")
    p.add_argument("--geoId", default="106057199",
                   help="LinkedIn geoId (Brasil=106057199). Aliases: brasil, sao-paulo, rio-de-janeiro")
    p.add_argument("--remote", action="store_true", help="Home office (f_WT=2)")
    p.add_argument("--hybrid", action="store_true", help="Híbrido (f_WT=3)")
    p.add_argument("--onsite", action="store_true", help="Presencial (f_WT=1)")
    p.add_argument("--last24h", action="store_true", help="Últimas 24h")
    p.add_argument("--week", action="store_true", help="Última semana")
    p.add_argument("--month", action="store_true", help="Último mês")
    p.add_argument("--pages", type=int, default=5)
    p.add_argument("--delay", type=float, default=1.0, help="Delay entre páginas (s)")
    p.add_argument("--out", default="data/linkedin_jobs.json")
    args = p.parse_args()

    geo_id = GEOIDS.get(args.geoId.lower(), args.geoId)
    work_mode = "remote" if args.remote else "hybrid" if args.hybrid else "onsite" if args.onsite else None
    time_range = "last24h" if args.last24h else "week" if args.week else "month" if args.month else None

    all_jobs, seen = [], set()
    for page in range(args.pages):
        url = build_url(args.keywords, geo_id, work_mode, time_range, page * 10)
        html = fetch_page(url)
        jobs = parse_jobs(html)
        print(f"[page {page + 1}/{args.pages}] {len(jobs)} vagas ({len(html)} bytes)", file=sys.stderr)
        if not jobs:
            break  # no more results
        for job in jobs:
            key = job["id"] or job["link"]
            if key and key not in seen:
                seen.add(key)
                all_jobs.append(job)
        if page < args.pages - 1:
            time.sleep(args.delay)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, indent=2, ensure_ascii=False)

    print(f"\n✅ {len(all_jobs)} vagas únicas salvas em {args.out}", file=sys.stderr)
    print(json.dumps(all_jobs[:3], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
