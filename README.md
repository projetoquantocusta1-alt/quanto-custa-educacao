# Projeto Quanto Custa — Educação

Quanto o Brasil gasta com educação desde 2009 (União, estados e municípios), por etapa,
por aluno e contra os mínimos legais. Repositório-satélite do Projeto Quanto Custa.

**Estado: esqueleto.** Veja `PLANEJAMENTO.md`.

## Rodar
```bash
pip install -r requirements.txt
python -m pytest -q
python sondar.py          # mede o que cada fonte oferece por ano
```

## Arquivos do site (`docs/dados`, previstos)
`meta.json` · `brasil.json` · `uniao.json` · `ies/CODIGO.json` · `uf/XX.json` ·
`resumo_m.json` · `m/IBGE7.json`
