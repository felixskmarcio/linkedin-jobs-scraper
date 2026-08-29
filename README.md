# 🔍 LinkedIn Jobs Scraper para Hermes Agent

> Coleta vagas do LinkedIn **sem login, sem API paga, sem anti-bot** — usando o endpoint guest público do LinkedIn.

Testado e validado em **28/08/2026**: 48 vagas reais do Brasil coletadas em ~8 segundos.

---

## ⚡ Instalação rápida (5 minutos)

```bash
git clone <este-repo> linkedin-jobs-scraper
cd linkedin-jobs-scraper
bash install.sh
```

Ou instalação mínima manual:

```bash
pip install websocket-client   # só necessário para injeção de cookies
# scrape_jobs.py usa apenas stdlib + curl
```

**Teste imediato (sem config nenhuma):**

```bash
python3 scripts/scrape_jobs.py --keywords "Analista de Sistemas" --geoId 106057199 --remote --last24h
```

Saída: `data/linkedin_jobs.json` com as vagas.

---

## 🧠 O segredo: endpoint guest

O LinkedIn mantém um endpoint **público e sem autenticação** que alimenta a página pública de vagas:

```
GET https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search
    ?keywords=Analista+de+Sistemas
    &geoId=106057199        ← Brasil (use geoId, NÃO location=Brasil)
    &f_WT=2                 ← 1=presencial, 2=remoto, 3=híbrido
    &f_TPR=r86400           ← r86400=24h, r604800=semana, r2592000=mês
    &start=0                ← paginação em blocos de ~10
```

Retorna **HTML com os cards de vagas** (não JSON) — parse com regex/BeautifulSoup.

### Por que funciona quando tudo mais falha

| Abordagem | Resultado |
|---|---|
| `linkedin.com/jobs/search` via browser | ❌ Authwall (login obrigatório) |
| Login programático | ❌ Security checkpoint (anti-bot) |
| API Voyager autenticada | ❌ 404 (migrou para GraphQL interno) |
| **jobs-guest API** | ✅ **200 OK, sem auth, sem cookies** |

### ⚠️ Pegadinha do filtro de localização

- `location=Brasil` → **retorna vagas dos EUA** (ignora/errado)
- `location=Brazil` → funciona parcialmente
- `geoId=106057199` → ✅ **funciona corretamente** (geoId oficial do Brasil)

Outros geoIds úteis: São Paulo=`106890317`, Rio de Janeiro=`106867723`. Descubra outros em `linkedin.com/jobs/search` logado, olhando o parâmetro `geoId` na URL.

---

## 📂 Estrutura do repositório

```
linkedin-jobs-scraper/
├── README.md                      ← este arquivo
├── install.sh                     ← instalação de dependências
├── requirements.txt
├── scripts/
│   ├── scrape_jobs.py             ← coletor principal (guest API, sem login)
│   ├── generate_dashboard.py      ← gera dashboard HTML das vagas
│   └── inject_cookies.py          ← injeta cookies no Chrome via CDP (modo logado)
├── docs/
│   ├── ENDPOINTS.md               ← referência de endpoints e parâmetros
│   └── COOKIES.md                 ← guia de exportação/injeção de cookies
├── examples/
│   └── linkedin_cookies.example.json
└── data/                          ← saída (json/html gerados)
```

---

## 🚀 Uso

### 1. Coletar vagas (modo guest — recomendado)

```bash
# Analista de Sistemas, Brasil, remoto, últimas 24h, 5 páginas
python3 scripts/scrape_jobs.py \
  --keywords "Analista de Sistemas" \
  --geoId 106057199 \
  --remote \
  --last24h \
  --pages 5 \
  --out data/vagas.json
```

Opções:

| Flag | Padrão | Descrição |
|---|---|---|
| `--keywords` | `Analista de Sistemas` | Termo de busca |
| `--geoId` | `106057199` | geoId do LinkedIn (Brasil) |
| `--remote` | off | f_WT=2 (home office) |
| `--hybrid` | off | f_WT=3 (híbrido) |
| `--onsite` | off | f_WT=1 (presencial) |
| `--last24h` | off | f_TPR=r86400 |
| `--week` | off | f_TPR=r604800 |
| `--month` | off | f_TPR=r2592000 |
| `--pages` | 5 | Páginas (~10 vagas cada) |
| `--out` | `data/linkedin_jobs.json` | Arquivo de saída |

### 2. Gerar dashboard HTML

```bash
python3 scripts/generate_dashboard.py data/vagas.json data/dashboard.html
```

### 3. Modo logado (avançado — cookies)

Para recursos que exigem sessão (aplicar a vagas, perfis completos), veja **[docs/COOKIES.md](docs/COOKIES.md)**.

---

## 🤖 Uso com Hermes Agent

Este repo está registrado como **skill do Hermes** (`linkedin-jobs-scraper`). O agente detecta automaticamente quando você pedir vagas do LinkedIn e usa estes scripts.

Também funciona via **cron do Hermes** para monitoramento diário:

```
Você: "Agende coleta diária de vagas de Analista de Sistemas às 8h"
Hermes: cria cronjob que roda scrape_jobs.py + generate_dashboard.py
```

---

## 🔧 Recuperação rápida (se perder tudo)

1. `git clone` deste repo
2. `bash install.sh`
3. `python3 scripts/scrape_jobs.py` → funciona imediatamente (guest não precisa de cookies)
4. (Opcional) Re-exporte cookies do seu Chrome → veja docs/COOKIES.md

**O modo guest não depende de NENHUMA credencial.** É por isso que é a base da recuperação.

---

## ⚖️ Avisos

- O endpoint guest é **público** (alimenta a página pública de vagas sem login), mas uso em escala pode gerar rate-limit. Respeite: delay entre páginas (o script já tem), volume moderado.
- Scraping de áreas logadas viola os Termos de Uso do LinkedIn (seção 8.2). O modo guest usa apenas dados públicos.
- Nunca commite `linkedin_cookies.json` real — contém seu token de sessão `li_at`.

---

## 📋 Validação (28/08/2026)

- ✅ 48 vagas BR coletadas (5 páginas), 43 empresas, 26 cidades
- ✅ Dashboard HTML gerado e servido
- ✅ Injeção de cookies via CDP testada (19/19 cookies, Chrome 151 headless)
- ✅ Testado em: Ubuntu 24.04, Python 3.11/3.12, curl 8.x
