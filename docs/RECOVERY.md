# 🔧 Guia de Recuperação (Recovery)

Se você perdeu tudo (máquina nova, HD formatado, etc.) e precisa voltar a usar o scraper do zero.

---

## Recuperação em 4 passos

### Passo 1 — Clonar o repositório

```bash
git clone https://github.com/felixskmarcio/linkedin-jobs-scraper.git
cd linkedin-jobs-scraper
```

### Passo 2 — Instalar dependências

```bash
bash install.sh
```

Ou manualmente:

```bash
pip install websocket-client   # só para o modo logado (inject_cookies.py)
# scrape_jobs.py não tem dependências externas
```

### Passo 3 — Testar o modo guest (funciona imediatamente)

```bash
python3 scripts/scrape_jobs.py --keywords "Analista de Sistemas" --geoId 106057199 --remote --last24h
```

> [!NOTE]
> **O modo guest não depende de NENHUMA credencial.** É por isso que é a base da recuperação.
> Se este comando funcionar, o scraper está 100% operacional para coleta de vagas públicas.

Saída esperada: `data/linkedin_jobs.json` com vagas reais do LinkedIn.

### Passo 4 — (Opcional) Restaurar cookies de sessão

Se você precisar do **modo logado** (para acessar vagas restritas, aplicar a vagas, etc.):

1. Abra o Chrome e faça login no LinkedIn normalmente
2. Instale a extensão **Cookie-Editor** (Chrome Web Store)
3. Exporte os cookies do linkedin.com no formato JSON
4. Salve como `linkedin_cookies.json` na raiz do projeto
5. Inicie o Chrome com debugging habilitado:
   ```bash
   google-chrome --remote-debugging-port=9222 --remote-allow-origins=* --headless
   ```
6. Injete os cookies:
   ```bash
   python3 scripts/inject_cookies.py linkedin_cookies.json "https://www.linkedin.com/feed/"
   ```

Veja o guia completo em **[docs/COOKIES.md](COOKIES.md)**.

---

## Solução de problemas comuns

| Problema | Causa provável | Solução |
|---|---|---|
| `curl: command not found` | curl não instalado | `sudo apt install curl` (Linux) ou instalar via [curl.se](https://curl.se/windows/) |
| `ModuleNotFoundError: websocket` | Dependência faltando | `pip install websocket-client` |
| JSON vazio (`[]`) | LinkedIn mudou o HTML | Abra uma [issue](https://github.com/felixskmarcio/linkedin-jobs-scraper/issues) com a data |
| Rate limit (429) | Muitas requisições | Aumente o delay entre páginas no script |
| Cookies inválidos | Sessão expirada | Re-exporte os cookies do Chrome logado |

---

## Voltar para a versão estável (v1.0.0)

Se uma atualização quebrou algo, você pode voltar ao estado original validado:

```bash
git fetch --tags
git checkout v1.0.0
```

Para voltar para o código mais recente:

```bash
git checkout main
```
