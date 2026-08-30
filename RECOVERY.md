# Recuperação rápida

Reinstalar tudo do zero em uma máquina nova (ou depois de perder o ambiente).

## 1. Clonar

```bash
git clone https://github.com/felixskmarcio/linkedin-jobs-scraper.git
cd linkedin-jobs-scraper
```

## 2. Instalar

```bash
bash install.sh
```

Só instala `websocket-client`. O coletor principal usa apenas stdlib + curl.

## 3. Validar

```bash
python3 scripts/scrape_jobs.py --keywords "Analista de Sistemas" --geoId 106057199 --remote --last24h
```

Deve gerar `data/linkedin_jobs.json`. O modo guest não precisa de cookies — se isso funcionou, o essencial está de pé.

## 4. (Opcional) Modo logado

Re-exporte os cookies do seu Chrome seguindo [COOKIES.md](COOKIES.md) e salve como `examples/linkedin_cookies.json` (arquivo ignorado pelo git).

## 5. (Opcional) Registrar como skill do Hermes

Aponte o Hermes para a pasta do repo. Consulte a doc do Hermes Agent para o caminho de skills da sua instalação.
