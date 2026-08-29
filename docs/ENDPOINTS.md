# 📡 Referência de Endpoints LinkedIn

## ✅ Guest API (sem login) — RECOMENDADO

```
GET https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search
```

Alimenta a página pública de vagas. Retorna HTML com cards `.base-search-card`.

### Parâmetros

| Parâmetro | Valores | Descrição |
|---|---|---|
| `keywords` | texto (URL-encoded) | Termo de busca |
| `geoId` | número | **Use geoId, não `location=`** |
| `f_WT` | 1/2/3 | 1=presencial, 2=remoto, 3=híbrido |
| `f_TPR` | r86400 / r604800 / r2592000 | 24h / semana / mês |
| `start` | 0, 10, 20... | Paginação (~10 por página) |

### geoIds conhecidos

| Local | geoId |
|---|---|
| Brasil | `106057199` |
| São Paulo | `106890317` |
| Rio de Janeiro | `106867723` |

Descobrir outros: abra `linkedin.com/jobs/search` logado, filtre a localização, copie o `geoId` da URL.

### Detalhe de uma vaga (também guest)

```
GET https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{jobId}
```

Retorna HTML com descrição completa, critérios, etc.

---

## ❌ Endpoints que NÃO funcionam mais (2026)

| Endpoint | Status |
|---|---|
| `/voyager/api/jobs/search` | 404 (migrou para GraphQL interno) |
| `/voyager/api/graphql` | Requer tokens de query internos (`queryId`) que mudam |
| `/jobs/search` (HTML) | Authwall sem login |

---

## Headers mínimos (guest)

```
User-Agent: Mozilla/5.0 ... Chrome/151.0.0.0 Safari/537.36
Accept: application/json, text/plain, */*
x-li-lang: pt_BR
```

Sem headers → possível 999/redirect. Com eles → 200 OK consistente.

---

## Rate limiting

O endpoint guest tolera volume moderado. Boas práticas (já no script):
- `delay >= 1s` entre páginas
- Não paralelize agressivamente
- Se receber 429/999: pare por 15–30 min
