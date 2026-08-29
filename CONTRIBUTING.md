# 🤝 Contribuindo com o LinkedIn Jobs Scraper

Obrigado por considerar contribuir! Este guia explica como participar do projeto.

---

## Antes de abrir um PR

1. **Rode o teste básico** e confirme que funciona:
   ```bash
   python3 scripts/scrape_jobs.py --keywords "Analista de Sistemas" --geoId 106057199 --remote --last24h
   ```
   O arquivo `data/linkedin_jobs.json` deve ser gerado com pelo menos 1 vaga.

2. **Se mudar parâmetros do endpoint**, atualize também `docs/ENDPOINTS.md`.

3. **Descreva no PR**:
   - O que foi alterado e por quê
   - O que foi testado e em que data (o LinkedIn muda o HTML sem aviso)
   - Sistema operacional e versão do Python

---

## Tipos de contribuição bem-vindos

| Tipo | Exemplos |
|---|---|
| 🐛 Bug fix | Parsing quebrou após mudança no HTML do LinkedIn |
| ✨ Feature | Novo filtro, novo campo extraído, novo formato de saída |
| 📝 Docs | Corrigir exemplos, adicionar geoIds, atualizar endpoints |
| 🧪 Testes | Scripts de validação automática |
| 🌐 Tradução | Melhorias no README.en.md |

---

## Fluxo de trabalho

```bash
# 1. Fork e clone
git clone https://github.com/SEU-USUARIO/linkedin-jobs-scraper.git
cd linkedin-jobs-scraper

# 2. Crie uma branch a partir de develop
git checkout develop
git checkout -b feature/minha-melhoria

# 3. Faça as mudanças e commit
git add .
git commit -m "feat: descrição da melhoria"

# 4. Push e abra um PR para develop (não para main)
git push origin feature/minha-melhoria
```

> [!IMPORTANT]
> PRs devem ser abertos contra a branch **`develop`**, não `main`.
> A `main` é a branch estável — merges para ela são feitos pelo mantenedor após validação.

---

## Padrão de commits

Use o padrão [Conventional Commits](https://www.conventionalcommits.org/):

| Prefixo | Quando usar |
|---|---|
| `feat:` | Nova funcionalidade |
| `fix:` | Correção de bug |
| `docs:` | Apenas documentação |
| `chore:` | Tarefas de manutenção (CI, deps) |
| `refactor:` | Refatoração sem mudança de comportamento |

---

## Dúvidas?

Abra uma [issue](https://github.com/felixskmarcio/linkedin-jobs-scraper/issues) com o label `question`.
