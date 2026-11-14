"""Sondagem: descobre, para cada fonte e ano desde 2009, se o dado existe e em que formato.

Roda ANTES de escrever os coletores. Só lê endereços públicos e grava o resultado em
dados_brutos/sondagem/rodada_N.json (status, tipo, tamanho, e o que der para descobrir:
conjuntos de dados de catálogos CKAN e links de páginas HTML).

Rodada 1: cobertura geral (Siconfi DCA, Portal da Transparência, INEP, IPCA, SIOPE).
  Achados: Siconfi DCA só a partir de 2013; Portal (orçamento) 403 até 2013;
  INEP com cadeia de certificado incompleta; endereço do SIOPE não encontrado.
Rodada 2: fechar 2009–2012 (FINBRA, RREO, SIOPE, SIOP, União) e INEP com a cadeia completada.

Uso: python sondar.py              # última rodada
     python sondar.py 1            # rodada 1
     python sondar.py 2 inep       # rodada 2, só uma fonte
"""
import json
import re
import sys
from pathlib import Path

import config
from coletor import http

SAIDA = Path(__file__).parent / "dados_brutos" / "sondagem"
PALAVRAS = re.compile(r"siope|finbra|dados.?abertos|download|csv|zip|xls|api|consulta|relat", re.I)
S = config.SICONFI_API
CKAN_TESOURO = "https://www.tesourotransparente.gov.br/ckan/api/3/action/package_search?rows=15&q="
CKAN_FNDE = "https://www.fnde.gov.br/dadosabertos/api/3/action/package_search?rows=15&q="


def rodada1():
    for ano in [2009, 2010, 2013, 2017, 2021, 2024]:
        yield "siconfi", ano, f"{S}/dca?an_exercicio={ano}&id_ente=23"
        yield "siconfi", ano, f"{S}/dca?an_exercicio={ano}&id_ente=2304400"
        yield "transparencia", ano, config.TRANSPARENCIA_ORCAMENTO.format(ano=ano)
        yield "inep", ano, config.INEP_CENSO_ESCOLAR.format(ano=ano)
    yield "siconfi", None, f"{S}/entes"
    yield "ipca", None, config.IPCA_SGS.format(ano=config.ANO_INICIAL)
    yield "siope", None, "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/siope"
    yield "siope", None, "https://www.fnde.gov.br/siope/"


def rodada2():
    # INEP, agora com a cadeia de certificado completada
    for ano in [2009, 2013, 2023]:
        yield "inep", ano, config.INEP_CENSO_ESCOLAR.format(ano=ano)
    yield "inep", 2013, config.INEP_CENSO_SUPERIOR.format(ano=2013)
    # Siconfi: em que ano começa o DCA, e se o RREO cobre 2009–2012
    for ano in [2011, 2012]:
        yield "siconfi_dca", ano, f"{S}/dca?an_exercicio={ano}&id_ente=23"
    for ano in [2009, 2012, 2015]:
        yield "siconfi_rreo", ano, (f"{S}/rreo?an_exercicio={ano}&nr_periodo=6"
                                    f"&co_tipo_demonstrativo=RREO&id_ente=23")
    for ano in [2013, 2015]:
        yield "siconfi_uniao", ano, f"{S}/dca?an_exercicio={ano}&id_ente=1"
    # Portal da Transparência: primeiro ano disponível do orçamento da União
    for ano in [2011, 2012, 2014, 2015, 2016]:
        yield "transparencia", ano, config.TRANSPARENCIA_ORCAMENTO.format(ano=ano)
    # Catálogos (descoberta): FINBRA, execução da União, SIOPE
    for q in ["finbra", "despesa+funcao", "execucao+orcamentaria+uniao", "siope", "educacao"]:
        yield "ckan_tesouro", None, CKAN_TESOURO + q
    for q in ["siope", "fundeb"]:
        yield "ckan_fnde", None, CKAN_FNDE + q
    # Páginas de entrada (descoberta de links)
    for url in ["https://www.fnde.gov.br/siope/", "https://www.fnde.gov.br/dadosabertos/",
                "https://siconfi.tesouro.gov.br/siconfi/pages/public/consulta_finbra/finbra_list.jsf",
                "https://www1.siop.planejamento.gov.br/", "https://www.siop.planejamento.gov.br/"]:
        yield "pagina", None, url


RODADAS = {1: rodada1, 2: rodada2}


def _descobrir(r, info):
    tipo = info.get("tipo") or ""
    if "json" in tipo:
        corpo = r.json()
        if isinstance(corpo, dict) and isinstance(corpo.get("result"), dict):   # CKAN
            info["conjuntos"] = [
                {"nome": p.get("title"),
                 "recursos": [x.get("url") for x in p.get("resources", [])][:6]}
                for p in corpo["result"].get("results", [])]
            info["total"] = corpo["result"].get("count")
        else:
            itens = corpo.get("items") if isinstance(corpo, dict) else corpo
            info["itens"] = len(itens) if isinstance(itens, list) else None
            if isinstance(itens, list) and itens and isinstance(itens[0], dict):
                info["campos"] = list(itens[0])[:20]
    elif "html" in tipo:
        html = r.text[:400_000]
        links = sorted(set(re.findall(r'href=["\']([^"\'#]+)', html)))
        info["links"] = [u for u in links if PALAVRAS.search(u)][:40]
        m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
        info["titulo"] = m.group(1).strip()[:120] if m else None
        info["redireciona_para"] = r.url if r.url else None


def sondar(url: str) -> dict:
    try:
        r = http.get(url, timeout=90, stream=True)
        info = {"status": r.status_code, "tipo": r.headers.get("Content-Type"),
                "tamanho": r.headers.get("Content-Length")}
        if not any(t in (info["tipo"] or "") for t in ("zip", "octet")):
            _descobrir(r, info)     # zip grande: só o cabeçalho
        r.close()
        return info
    except Exception as e:  # noqa: BLE001 — sondagem: registrar qualquer falha
        return {"erro": f"{type(e).__name__}: {e}"[:300]}


def main():
    args = sys.argv[1:]
    rodada = int(args.pop(0)) if args and args[0].isdigit() else max(RODADAS)
    so = set(args)
    SAIDA.mkdir(parents=True, exist_ok=True)
    res = []
    for fonte, ano, url in RODADAS[rodada]():
        if so and not any(fonte.startswith(s) for s in so):
            continue
        r = {"fonte": fonte, "ano": ano, "url": url, **sondar(url)}
        print(json.dumps(r, ensure_ascii=False))
        res.append(r)
    (SAIDA / f"rodada_{rodada}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
