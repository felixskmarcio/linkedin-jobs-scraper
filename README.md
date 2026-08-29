<div align="center">
  <img src="media/logo.png" alt="LinkedIn Jobs Scraper" width="160"/>
  <h1>🔍 LinkedIn Jobs Scraper</h1>
  <h3><em>Vagas do LinkedIn sem login, sem API paga, sem anti-bot.</em></h3>
</div>

<p align="center">
  <strong>Coleta vagas pelo endpoint guest público do LinkedIn, gera um dashboard HTML e roda como skill do Hermes Agent — só Python stdlib + curl.</strong>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square" alt="Python 3.10+"/></a>
  <a href="https://github.com/felixskmarcio/linkedin-jobs-scraper/blob/main/LICENSE"><img src="https://img.shields.io/github/license/felixskmarcio/linkedin-jobs-scraper?style=flat-square" alt="License"/></a>
  <a href="https://github.com/felixskmarcio/linkedin-jobs-scraper/commits/main"><img src="https://img.shields.io/github/last-commit/felixskmarcio/linkedin-jobs-scraper?style=flat-square" alt="Last commit"/></a>
  <a href="https://github.com/felixskmarcio/linkedin-jobs-scraper/stargazers"><img src="https://img.shields.io/github/stars/felixskmarcio/linkedin-jobs-scraper?style=social" alt="GitHub stars"/></a>
</p>

<p align="center">
  <strong>Português</strong> · <a href="./README.en.md">English</a>
</p>

> [!NOTE]
> Testado e validado em **28/08/2026**: 48 vagas reais do Brasil coletadas em ~8 segundos, sem cookies e sem login.

---

## Sumário

- [🤔 Por que este scraper?](#-por-que-este-scraper)
- [⚡ Quick Start](#-quick-start)
- [🚀 Uso](#-uso)
- [🤖 Integração com Hermes Agent](#-integração-com-hermes-agent)
- [📂 Estrutura do repositório](#-estrutura-do-repositório)
- [📚 Documentação](#-documentação)
- [🔧 Pré-requisitos](#-pré-requisitos)
- [🤝 Contribuindo](#-contribuindo)
- [📄 Licença](#-licença)

---

## 🤔 Por que este scraper?

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

### Como nos comparamos

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

## ⚡ Quick Start

```bash
git clone https://github.com/felixskmarcio/linkedin-jobs-scraper.git
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

<details>
<summary><strong>Exemplo de saída (JSON)</strong></summary>

```json
[
  {
    "title": "Analista de Sistemas Sênior",
    "company": "Empresa XYZ",
    "location": "São Paulo, SP",
    "url": "https://www.linkedin.com/jobs/view/..."
  }
]
```

</details>

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

**Opções:**

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

## 🤖 Integração com Hermes Agent

Este repo está registrado como **skill do Hermes** (`linkedin-jobs-scraper`). O agente detecta automaticamente quando você pedir vagas do LinkedIn e usa estes scripts.

Também funciona via **cron do Hermes** para monitoramento diário:

```
Você:   "Agende coleta diária de vagas de Analista de Sistemas às 8h"
Hermes: cria cronjob que roda scrape_jobs.py + generate_dashboard.py
```

---

## 📂 Estrutura do repositório

```
linkedin-jobs-scraper/
├── README.md                      ← este arquivo
├── LICENSE
├── CONTRIBUTING.md
├── install.sh                     ← instalação de dependências
├── requirements.txt
├── scripts/
│   ├── scrape_jobs.py             ← coletor principal (guest API, sem login)
│   ├── generate_dashboard.py      ← gera dashboard HTML das vagas
│   └── inject_cookies.py          ← injeta cookies no Chrome via CDP (modo logado)
├── docs/
│   ├── ENDPOINTS.md               ← referência de endpoints e parâmetros
│   ├── COOKIES.md                 ← guia de exportação/injeção de cookies
│   └── RECOVERY.md                ← reinstalação do zero
├── examples/
│   └── linkedin_cookies.example.json
├── media/                         ← logo e screenshots
└── data/                          ← saída (json/html gerados)
```

---

## 📚 Documentação

| Documento | Conteúdo |
|---|---|
| [docs/ENDPOINTS.md](docs/ENDPOINTS.md) | Referência completa do endpoint guest, parâmetros e geoIds |
| [docs/COOKIES.md](docs/COOKIES.md) | Exportar cookies do Chrome e injetar via CDP (modo logado) |
| [docs/RECOVERY.md](docs/RECOVERY.md) | Reinstalar tudo do zero em 4 passos |

---

## 🔧 Pré-requisitos

- Python 3.10+
- `curl` disponível no PATH
- `websocket-client` — apenas para o modo logado (`inject_cookies.py`)
- Google Chrome — apenas para o modo logado

---

## 🤝 Contribuindo

Issues e PRs são bem-vindos. Antes de abrir um PR:

1. Rode o teste imediato do [Quick Start](#-quick-start) e confirme que o JSON foi gerado.
2. Se mudar parâmetros do endpoint, atualize também `docs/ENDPOINTS.md`.
3. Descreva no PR o que foi testado e em que data (o LinkedIn muda o HTML sem aviso).

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para o guia completo.

---

## ⚖️ Avisos

- O endpoint guest é **público** (alimenta a página pública de vagas sem login), mas uso em escala pode gerar rate-limit. Respeite: delay entre páginas (o script já tem), volume moderado.
- Scraping de áreas logadas viola os Termos de Uso do LinkedIn (seção 8.2). O modo guest usa apenas dados públicos.
- Nunca commite `linkedin_cookies.json` real — contém seu token de sessão `li_at`.

---

## 📄 Licença

Distribuído sob a licença MIT. Veja [LICENSE](LICENSE) para detalhes.

---

<p align="center">
  Feito por <a href="https://github.com/felixskmarcio">@felixskmarcio</a> · Se este projeto te ajudou, deixe uma ⭐
</p>
