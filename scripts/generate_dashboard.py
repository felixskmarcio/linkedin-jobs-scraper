#!/usr/bin/env python3
"""
Generate an HTML dashboard from scraped LinkedIn jobs JSON.

Usage:
    python3 generate_dashboard.py data/linkedin_jobs.json data/dashboard.html
"""
import json
import os
import sys
from collections import Counter
from datetime import datetime


def bar_row(label: str, cnt: int, total: int) -> str:
    pct = (cnt / total) * 100 if total else 0
    return (f'<div class="bar-row"><div class="bar-label">{label}</div>'
            f'<div class="bar-track"><div class="bar-fill" style="width:{pct:.0f}%"></div></div>'
            f'<div class="bar-count">{cnt}</div></div>')


def job_row(i: int, j: dict) -> str:
    salary = (f' <span class="tag tag-salary">{j["salary"]}</span>' if j.get("salary") else "")
    loc = j.get("location") or ""
    home = (' <span class="tag tag-home">Remoto</span>'
            if any(k in loc.lower() for k in ("remote", "home")) or loc.strip().lower() == "brazil"
            else "")
    return (f'<tr><td>{i + 1}</td>'
            f'<td><a class="job-title" href="{j.get("link") or "#"}" target="_blank">{j["title"]}</a>{salary}</td>'
            f'<td class="company">{j.get("company") or ""}</td>'
            f'<td class="location">{loc}{home}</td>'
            f'<td class="location">{j.get("posted") or "N/A"}</td></tr>')


def main() -> int:
    src = sys.argv[1] if len(sys.argv) > 1 else "data/linkedin_jobs.json"
    dst = sys.argv[2] if len(sys.argv) > 2 else "data/dashboard.html"

    with open(src, encoding="utf-8") as f:
        jobs = json.load(f)

    total = len(jobs)
    locations = [(j.get("location") or "").split(",")[0].strip() for j in jobs if j.get("location")]
    companies = [j["company"] for j in jobs if j.get("company")]
    top_locations = Counter(locations).most_common(10)
    top_companies = Counter(companies).most_common(10)
    salaried = sum(1 for j in jobs if j.get("salary"))
    today = datetime.now().strftime("%d/%m/%Y %H:%M")

    html = TEMPLATE.format(
        total=total,
        n_locations=len(set(locations)),
        n_companies=len(set(companies)),
        salaried=salaried,
        today=today,
        location_bars="".join(bar_row(l, c, total) for l, c in top_locations),
        company_bars="".join(bar_row(c, n, total) for c, n in top_companies),
        job_rows="".join(job_row(i, j) for i, j in enumerate(jobs)),
    )

    os.makedirs(os.path.dirname(dst) or ".", exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Dashboard: {dst} ({os.path.getsize(dst)} bytes, {total} vagas)")
    return 0


TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Vagas LinkedIn — Dashboard</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f3f6f8;color:#1d2226;line-height:1.5}}
.container{{max-width:1200px;margin:0 auto;padding:24px}}
header{{background:linear-gradient(135deg,#0a66c2 0%,#004182 100%);color:#fff;padding:32px 24px;border-radius:12px;margin-bottom:24px}}
h1{{font-size:28px;font-weight:700}}
.subtitle{{margin-top:8px;opacity:.9;font-size:14px}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:24px}}
.card,.section{{background:#fff;border-radius:10px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,.08)}}
.section{{margin-bottom:24px}}
.stat-num{{font-size:32px;font-weight:700;color:#0a66c2}}
.stat-label{{font-size:13px;color:#666;text-transform:uppercase;margin-top:4px}}
.section h2{{font-size:18px;margin-bottom:12px;color:#0a66c2;border-bottom:2px solid #e0e0e0;padding-bottom:8px}}
.bar-row{{display:flex;align-items:center;margin-bottom:6px}}
.bar-label{{width:180px;font-size:13px}}
.bar-track{{flex:1;background:#e8e8e8;height:8px;border-radius:4px;margin:0 12px}}
.bar-fill{{background:#0a66c2;height:100%;border-radius:4px}}
.bar-count{{font-size:12px;color:#666;min-width:24px;text-align:right}}
table{{width:100%;border-collapse:collapse}}
th,td{{padding:10px 8px;text-align:left;font-size:13px;border-bottom:1px solid #e0e0e0}}
th{{background:#f3f6f8;font-weight:600;color:#666;text-transform:uppercase;font-size:11px}}
tr:hover{{background:#fafbfc}}
.job-title{{font-weight:600;color:#0a66c2;text-decoration:none}}
.job-title:hover{{text-decoration:underline}}
.company{{color:#444}}
.location{{color:#666;font-size:12px}}
.tag{{display:inline-block;padding:2px 8px;background:#e7f3ff;color:#0a66c2;border-radius:12px;font-size:11px;font-weight:500}}
.tag-home{{background:#e7f7e8;color:#057642}}
.tag-salary{{background:#fff3cd;color:#915907}}
footer{{text-align:center;color:#666;font-size:12px;padding:20px 0}}
</style>
</head>
<body>
<div class="container">
<header>
<h1>🔍 Vagas LinkedIn — Dashboard</h1>
<div class="subtitle">Coletado via guest API (sem login) · Atualizado em {today}</div>
</header>
<div class="stats">
<div class="card"><div class="stat-num">{total}</div><div class="stat-label">Total de vagas</div></div>
<div class="card"><div class="stat-num">{n_locations}</div><div class="stat-label">Cidades únicas</div></div>
<div class="card"><div class="stat-num">{n_companies}</div><div class="stat-label">Empresas</div></div>
<div class="card"><div class="stat-num">{salaried}/{total}</div><div class="stat-label">Com salário</div></div>
</div>
<div class="section"><h2>📊 Top Localizações</h2>{location_bars}</div>
<div class="section"><h2>🏢 Top Empresas</h2>{company_bars}</div>
<div class="section"><h2>📋 Vagas ({total})</h2>
<table><thead><tr><th>#</th><th>Vaga</th><th>Empresa</th><th>Local</th><th>Publicada</th></tr></thead>
<tbody>{job_rows}</tbody></table></div>
<footer>Fonte: LinkedIn Jobs guest API · linkedin-jobs-scraper</footer>
</div>
</body>
</html>
"""

if __name__ == "__main__":
    sys.exit(main())
