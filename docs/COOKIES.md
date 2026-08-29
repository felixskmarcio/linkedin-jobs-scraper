# 🍪 Guia de Cookies (modo logado)

> **Para coletar vagas você NÃO precisa disso** — use o guest API (`scrape_jobs.py`).
> Cookies só são necessários para recursos de conta logada: ver perfis completos,
> aplicar a vagas, feed, mensagens.

## Por que não automatizar o login?

Login programático no LinkedIn **sempre** dispara o security checkpoint
(anti-bot). A técnica correta, validada pela comunidade, é:

1. Você loga **manualmente** no seu navegador pessoal (uma vez)
2. Exporta os cookies
3. O bot reutiliza a sessão existente (LinkedIn vê continuação, não novo login)

## Passo a passo

### 1. Exportar cookies do seu Chrome (1 min)

1. Instale a extensão **Cookie-Editor**:  
   https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm
2. Abra `https://www.linkedin.com` **logado**
3. Clique no ícone do Cookie-Editor → **Export** → **JSON**
4. Salve como `linkedin_cookies.json`

### 2. Preparar o Chrome headless

O Chrome **precisa** da flag `--remote-allow-origins=*`, senão o WebSocket
do CDP rejeita conexões com 403:

```bash
google-chrome --headless --disable-gpu --no-sandbox \
  --remote-debugging-port=9222 \
  --remote-allow-origins=* \
  --user-data-dir=/var/lib/browser-harness-chrome \
  about:blank &
```

### 3. Injetar e validar

```bash
pip install websocket-client
python3 scripts/inject_cookies.py linkedin_cookies.json "https://www.linkedin.com/feed/"
```

O script valida:
- ✅/❌ `li_at` e `JSESSIONID` presentes após injeção
- URL final (se cair em `authwall`/`checkpoint`, os cookies foram rejeitados)

### 4. Manutenção

- `li_at` dura ~1 ano, mas o LinkedIn pode invalidar por mudança de IP/dispositivo
- Se cair em checkpoint: re-exporte os cookies do navegador (sessão fresca)
- Ideal: rodar o bot **do mesmo IP** onde você logou (ou IP residencial BR)

## 🔐 Segurança

- `li_at` = sua sessão completa. Quem tem esse valor **é você** para o LinkedIn.
- **NUNCA** commite `linkedin_cookies.json` (está no `.gitignore`)
- Guarde com permissão restrita: `chmod 600 linkedin_cookies.json`
- Se vazar: revoke em LinkedIn → Settings → Sign in & security → Where you're signed in

## ⚠️ Bug conhecido (corrigido neste repo)

A primeira versão do injetor chamava `Network.clearBrowserCookies()` **depois**
de injetar — apagando tudo. A versão em `scripts/inject_cookies.py` limpa
**antes** de injetar e valida o resultado com `Network.getCookies`.
