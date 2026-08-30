# Relatório de Auditoria de Segurança — LinkedIn Jobs Scraper

**Data:** 29/08/2026  
**Escopo:** Repositório local e remoto `felixskmarcio/linkedin-jobs-scraper` (branch `develop`, commit `c9f2607`)  
**Auditor:** Antigravity (Auditoria Estendida OWASP Top 10 2025)  
**Versão do prompt:** v1.0 (unificado)

---

## Nota metodológica

Este relatório aplica o **OWASP Top 10 (2025)** como framework de categorização, estendido com:

- Categoria 0: **Detecção de stack** (executada antes de qualquer análise)
- Categoria 11: **Saída estruturada** (Issues GitHub prontas para colar)

Cada categoria foi mapeada para os componentes da stack do projeto (CLI Python stdlib, gerador de templates HTML e scripts de automação via CDP/curl). Categorias não aplicáveis (como SQL Injection para projetos sem banco de dados) foram explicitamente documentadas como "N/A — fora de escopo" com evidência técnica.

**Estágios de execução:**
1. **Detecção de stack**
2. **Quick triage** (10 padrões de alto impacto)
3. **Análise por categoria** OWASP A01–A10 + XSS
4. **Cobertura explícita** (o que foi verificado e está correto)
5. **Geração de issues prontas para GitHub**

---

## 1. Detecção de stack (executada antes da auditoria)

| Aspecto | Detectado | Mecanismo de isolamento / Proteção |
|---|---|---|
| **Linguagem** | Python 3.10+ e Bash (`install.sh`) | Scripts CLI independentes |
| **Framework** | Nenhum (Python stdlib: `argparse`, `re`, `subprocess`, `json`) | Execução em processo local |
| **ORM / Query builder** | N/A — fora de escopo | Sem banco de dados relacional ou NoSQL |
| **Mecanismo de auth** | Guest API (sem auth) / Cookies de sessão (`li_at`, `JSESSIONID`) | Modo guest sem credenciais; injeção via CDP local |
| **Frontend** | Dashboard HTML gerado via script Python (`generate_dashboard.py`) | Arquivo HTML estático autônomo (Vanilla CSS inline) |
| **Deploy / CI** | GitHub Actions (`ci.yml`) / Scripts locais | Execução em runner `ubuntu-latest` |
| **LLM integrado?** | Projetado para atuar como skill do Hermes Agent | Comunicação via CLI (invocação de subprocesso) |
| **Modo de renderização** | Server/CLI string interpolation (`str.format`) | Gera arquivo local `data/dashboard.html` |

---

## 2. Quick Triage (10 padrões de alto impacto)

1. [x] **SQL injection:** N/A — Não há banco de dados SQL nem queries.
2. [x] **Chaves/segredos hardcoded:** ✅ **Aprovado** — Zero tokens ou credenciais reais no código ou histórico Git. O arquivo `examples/linkedin_cookies.example.json` contém apenas placeholders.
3. [x] **IDOR:** N/A — Não há servidor multi-tenant ou controle de acesso a objetos por ID.
4. [x] **JWT sem verificação de assinatura:** N/A — O projeto não emite nem valida JWTs.
5. [x] **SSRF:** ✅ **Aprovado** — A URL de coleta é pré-fixada para `linkedin.com/jobs-guest/...` e parâmetros são tratados.
6. [x] **Deserialização insegura:** ✅ **Aprovado** — Apenas `json.load()` e `json.loads()` são utilizados (sem `pickle`, `yaml` ou `eval`).
7. [x] **Debug mode em produção:** N/A — Ferramenta CLI sem servidor de aplicação.
8. [x] **TLS desabilitado:** ✅ **Aprovado** — O `curl` roda sem a flag `-k`/`--insecure`, garantindo validação de certificados TLS.
9. [x] **Mass assignment:** N/A — Não há modelos de dados expostos a requisições externas.
10. [x] **RLS off em Supabase:** N/A — Não utiliza Supabase ou BaaS.

---

## 3. Análise por categoria OWASP

### A01 — Broken Access Control / CDP Security

**Mapeamento:** Isolamento de portas de depuração de navegadores locais e controle de acesso a dados de sessão.

**Achados:**

| # | Severidade | Arquivo:linha | Descrição |
|---|---|---|---|
| 1 | 🟡 Média | `docs/COOKIES.md:34` e `scripts/inject_cookies.py:10` | O comando documentado instrui inicializar o Chrome com `--remote-allow-origins=*`, permitindo que sites maliciosos acessados no navegador do host se conectem à porta 9222 via WebSocket e sequestrem a sessão. |

**Verificações corretas (prova de cobertura):**
- O modo guest (`scrape_jobs.py`) não exige privilégios de acesso nem expõe portas de rede.

---

### A02 — Cryptographic Failures (Secrets e Tokens)

**Mapeamento:** Varredura de tokens de autenticação (`li_at`, `JSESSIONID`), chaves privadas e mascaramento de credenciais.

**Achados:**

| # | Severidade | Arquivo:linha | Descrição |
|---|---|---|---|
| 2 | 🔵 Baixa | `docs/COOKIES.md:60` | Armazenamento de cookies em texto claro em disco (`linkedin_cookies.json`). Embora mitigado pelo `.gitignore` e `chmod 600`, sistemas sem controle de permissão POSIX (como partições NTFS/FAT padrão) mantêm o arquivo legível para qualquer processo local. |

**Verificações corretas:**
- Histórico Git e arquivos rastreados auditados: nenhum token real foi commitado.
- `.gitignore` cobre explicitamente `linkedin_cookies.json` e `*.cookies.json`.

---

### A03 — Injection (Command Injection / URL Injection)

**Mapeamento:** Uso seguro de subprocessos (`subprocess.run`) e concatenação de URLs.

**Achados:**

| # | Severidade | Arquivo:linha | Descrição |
|---|---|---|---|
| 3 | 🔵 Baixa | `scripts/scrape_jobs.py:85` | Parâmetro `geoId` é concatenado diretamente na URL sem codificação (`quote_plus`), permitindo inserção de caracteres inesperados na URL se argumentos maliciosos forem passados via CLI. |

**Verificações corretas:**
- O comando `curl` em `fetch_page` (`scripts/scrape_jobs.py:44-50`) é executado como lista de argumentos com `shell=False` (padrão do Python), prevenindo command injection via operadores de shell (`;`, `|`, `&&`).

---

### A04 — Insecure Design

**Mapeamento:** Tratamento de erros, tolerância a falhas e políticas de taxa de requisições (rate limit).

**Achados:**

| # | Severidade | Arquivo:linha | Descrição |
|---|---|---|---|
| 4 | 🟢 Informativa | `scripts/scrape_jobs.py:42-52` | `fetch_page` ignora o código de status HTTP retornado pelo `curl`. Se o LinkedIn responder com `429 Too Many Requests` ou `999 Request Denied`, o script apenas falha silenciosamente sem orientar o usuário sobre o bloqueio temporário. |

---

### A05 — Security Misconfiguration

**Mapeamento:** Cabeçalhos de segurança web, permissões e práticas de ambiente de execução.

**Achados:**

| # | Severidade | Arquivo:linha | Descrição |
|---|---|---|---|
| 5 | 🔵 Baixa | `install.sh:13` | Uso da flag `--break-system-packages` no `pip install`, o que pode sobrescrever pacotes gerenciados pelo sistema operacional do usuário em distribuições Linux recentes (PEP 668). |
| 6 | 🔵 Baixa | `scripts/generate_dashboard.py:68-74` | Ausência de meta tag `Content-Security-Policy` no template HTML gerado, aumentando o impacto caso ocorra injeção de scripts (XSS). |

---

### A06 — Vulnerable and Outdated Components

**Mapeamento:** Auditoria de dependências em `requirements.txt`.

**Achados:** Nenhum achado. A única dependência declarada é `websocket-client>=1.6`, pacote ativo e sem vulnerabilidades críticas conhecidas nas versões recentes.

---

### A07 — Identification and Authentication Failures

**Mapeamento:** Validação de fluxos de login e gestão de sessão.

**Achados:** N/A — O projeto não provê autenticação própria; consome APIs públicas no modo guest e reutiliza cookies válidos no modo CDP.

---

### A08 — Software and Data Integrity Failures

**Mapeamento:** Pipelines de CI/CD e integridade de dependências.

**Achados:**

| # | Severidade | Arquivo:linha | Descrição |
|---|---|---|---|
| 7 | 🟢 Informativa | `ci.yml:15,17,35,36` | Ações do GitHub Actions (`actions/checkout@v4`, `actions/setup-python@v5`) utilizam tags de versão mutáveis em vez de hashes imutáveis de commit (SHA-256/SHA-1). |

---

### A09 — Security Logging and Monitoring Failures

**Mapeamento:** Rastreabilidade de erros e diagnóstico de segurança.

**Achados:**

| # | Severidade | Arquivo:linha | Descrição |
|---|---|---|---|
| 8 | 🟢 Informativa | `scripts/inject_cookies.py:108-109` | O script apenas imprime aviso em stdout caso seja detectado checkpoint ou authwall, sem códigos de saída distintos para automação em pipelines. |

---

### A10 — Server-Side Request Forgery (SSRF)

**Mapeamento:** Requisições originadas do backend para destinos fornecidos pelo usuário.

**Achados:** Nenhum achado. As requisições HTTP do scraper apontam estritamente para o domínio do LinkedIn (`linkedin.com`).

---

### Categoria Específica — XSS (Cross-Site Scripting no Dashboard)

**Mapeamento:** Tratamento e escape de dados externos renderizados no HTML (`generate_dashboard.py`).

**Achados:**

| # | Severidade | Arquivo:linha | Descrição |
|---|---|---|---|
| 9 | 🟡 Média | `scripts/generate_dashboard.py:28-32, 56-58` | **HTML Injection / XSS no Dashboard:** Os campos `title`, `company`, `location`, `salary` e `link` são interpolados diretamente no HTML sem `html.escape()`. Se uma vaga no LinkedIn contiver caracteres especiais ou se um JSON forjado for passado ao script, tags HTML e atributos podem ser injetados no documento local. |

---

## 4. Resumo executivo

| Severidade | Total |
|---|---|
| 🔴 Crítica | 0 |
| 🟠 Alta | 0 |
| 🟡 Média | 2 |
| 🔵 Baixa | 4 |
| 🟢 Informativa | 3 |
| **Total** | **9** |

---

## 5. Pontos fortes (prova de cobertura)

- ✅ **Sem credenciais expostas:** Varredura completa no histórico git confirmou ausência de chaves de API, senhas ou tokens `li_at`.
- ✅ **`.gitignore` efetivo:** Arquivos sensíveis (`linkedin_cookies.json`, `*.cookies.json`, `data/`) estão devidamente ignorados.
- ✅ **Execução de subprocessos segura:** O `fetch_page` executa o binário do `curl` sem invocar interpretador de shell (`shell=False`), prevenindo injeção de comandos arbitrários no sistema operacional.
- ✅ **Deserialização estrita:** Não há uso de bibliotecas inseguras como `pickle` ou `eval`; o parsing é estritamente via módulo `json`.
- ✅ **Comunicação criptografada:** Todas as URLs de consulta utilizam HTTPS por padrão.

---

## 6. Tabela de achados detalhados

| Sev | Arquivo:linha | Categoria | Descrição |
|---|---|---|---|
| 🟡 | `scripts/generate_dashboard.py:28-32` | XSS / A03 | Falta de escape de caracteres HTML (`html.escape`) ao renderizar dados das vagas no dashboard HTML. |
| 🟡 | `docs/COOKIES.md:34` | A01 / A05 | Orientação para uso de `--remote-allow-origins=*` no Chrome expõe a interface CDP a conexões locais de origens cruzadas. |
| 🔵 | `install.sh:13` | A05 | Flag `--break-system-packages` pode causar instabilidade no ambiente Python do sistema operacional hospedeiro. |
| 🔵 | `scripts/generate_dashboard.py:68` | A05 | Ausência de Content Security Policy (CSP) no HTML gerado pelo dashboard. |
| 🔵 | `scripts/scrape_jobs.py:85` | A03 | Interpolação de `geoId` na URL sem sanitização ou encode explícito. |
| 🔵 | `docs/COOKIES.md:60` | A02 | Sessão armazenada em arquivo JSON em texto claro no sistema de arquivos. |
| 🟢 | `scripts/scrape_jobs.py:42` | A04 / A09 | Falta de tratamento e log para códigos de status HTTP como 429 ou 999 no `curl`. |
| 🟢 | `ci.yml:15` | A08 | Uso de tags mutáveis (`v4`, `v5`) em vez de commit SHA nas GitHub Actions. |
| 🟢 | `scripts/inject_cookies.py:108` | A09 | Falha ao retornar exit code com código de erro específico quando cai em checkpoint anti-bot. |

---

## 7. Recomendações priorizadas

### P1 (Recomendado ajustar logo):
1. **Sanitizar dados no Dashboard (`generate_dashboard.py`):**
   - Envolver todos os textos inseridos no HTML (`title`, `company`, `location`, etc.) com `html.escape()`.
   - Validar que o `link` comece estritamente com `https://` antes de renderizar a tag `<a>`.

2. **Refinar a recomendação do Chrome CDP (`docs/COOKIES.md`):**
   - Adicionar nota de segurança explicando que o navegador aberto com depuração remota deve ser fechado após o uso do script.

### P2 (Próximas melhorias):
1. **Tratamento de status HTTP no Scraper (`scrape_jobs.py`):**
   - Capturar o status code do `curl` (`-w "%{http_code}"`) e exibir alerta explícito caso ocorra `429 (Rate Limit)` ou `999 (Bloqueio)`.
2. **Ambiente virtual no instalador (`install.sh`):**
   - Priorizar criação de um virtualenv (`python3 -m venv .venv`) antes de tentar instalar dependências no Python global com `--break-system-packages`.

### P3 (Boas práticas gerais):
1. Adicionar tag `<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline';">` no dashboard gerado.
2. Fixar as versões das GitHub Actions pelo hash SHA em `ci.yml`.

---

## 8. Issues para o GitHub (prontas para colar)

```markdown
--- ISSUE 1 ---
Título: [Segurança] Sanitizar dados de vagas contra XSS no gerador de dashboard HTML
Labels: security, bug, severity/medium

### Descrição
No arquivo `scripts/generate_dashboard.py`, os campos extraídos das vagas (`title`, `company`, `location`, `salary` e `link`) são interpolados diretamente no template HTML sem passar por `html.escape()`.

Se uma vaga contiver caracteres especiais ou payload forjado, tags HTML ou esquemas de URI perigosos (ex.: `javascript:`) podem ser executados ao abrir o arquivo `data/dashboard.html` no navegador.

### Correção sugerida
- Importar `html` na `generate_dashboard.py` e aplicar `html.escape()` nos valores de texto antes de montar as linhas da tabela e as barras de estatísticas.
- Garantir que o atributo `href` apenas aceite links iniciando com `https://`.
--- FIM ISSUE 1 ---

--- ISSUE 2 ---
Título: [Melhoria/Segurança] Alertar sobre encerramento do Chrome CDP e riscos de `--remote-allow-origins=*`
Labels: documentation, security, severity/medium

### Descrição
No arquivo `docs/COOKIES.md`, a instrução para iniciar o Chrome headless inclui o argumento `--remote-allow-origins=*`. 
Isso permite que qualquer página web aberta em outra aba na mesma máquina consiga interagir com a interface de depuração do Chrome na porta 9222.

### Correção sugerida
- Incluir uma recomendação explícita na documentação para fechar a instância do Chrome logo após a injeção/execução.
- Documentar boas práticas para restringir o acesso à interface de depuração a ambientes controlados.
--- FIM ISSUE 2 ---

--- ISSUE 3 ---
Título: [Melhoria] Tratar status HTTP 429/999 e isolar dependências em virtualenv no install.sh
Labels: enhancement, good first issue, severity/low

### Descrição
1. O comando `curl` em `scripts/scrape_jobs.py` não captura explicitamente o código de status HTTP retornado pelo LinkedIn. Em caso de rate-limit (429) ou bloqueio (999), o script falha silenciosamente retornando zero vagas.
2. No `install.sh`, o script tenta instalar pacotes com a flag `--break-system-packages`, o que pode afetar a estabilidade do Python do sistema em distribuições Linux recentes.

### Correção sugerida
- Capturar o HTTP status no `fetch_page` e emitir aviso de rate-limit/bloqueio com sugestão de espera.
- Atualizar `install.sh` para recomendar o uso de `venv`.
--- FIM ISSUE 3 ---
```

---

## Apêndice A — Coverage matrix

| Categoria | Aplicável? | Como foi mapeada |
|---|---|---|
| **A01 Broken Access Control** | Parcial | Exposição de portas de depuração do browser local (CDP). |
| **A02 Cryptographic Failures** | Sim | Verificação de tokens `li_at`/`JSESSIONID`, regex de segredos e histórico Git. |
| **A03 Injection** | Sim | Parâmetros de comando `curl` e montagem de URLs. |
| **A04 Insecure Design** | Sim | Resiliência contra bloqueios da API guest e rate limits. |
| **A05 Security Misconfiguration** | Sim | Flags de instalação de pacotes e cabeçalhos no dashboard gerado. |
| **A06 Vulnerable Components** | Sim | Auditoria de dependências no `requirements.txt`. |
| **A07 Auth Failures** | N/A | Projeto não implementa autenticação própria (consome API pública). |
| **A08 Integrity Failures** | Parcial | Configuração de ações e workflows em `ci.yml`. |
| **A09 Logging & Monitoring** | Sim | Tratamento de erros e visibilidade de falhas na CLI. |
| **A10 SSRF** | Parcial | Validação de destinos de requisição HTTP feitas pelo script. |
| **XSS** | Sim | Interpolação de dados externos no gerador de dashboard HTML. |
