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


CKAN_SHOW = "https://www.tesourotransparente.gov.br/ckan/api/3/action/package_show?id="
SIOPE = "https://www.fnde.gov.br/siope/"


def rodada3():
    """Abrir os candidatos para 2009–2012 achados na rodada 2."""
    # SIOPE: páginas públicas de relatórios e download (todos os links, sem filtro)
    for pag in ["download.do", "relatoriosEstaduais.jsp", "relatoriosMunicipais.jsp",
                "relatoriosDaUniao.jsp", "relatorio-gerencial/dist/"]:
        yield "siope_pagina", None, SIOPE + pag
    # Tesouro Transparente: todos os arquivos dos conjuntos candidatos
    for ident in ["bcd753b8-e79d-4964-a565-977d23bada0d",    # Despesas da União mensais desde 2008
                  "22d13d17-bf69-4a1a-add2-25cc1e25f2d7",    # Despesas por função (COFOG)
                  "c6537d6f-237e-4826-9396-2df7968c9417"]:   # Restos a pagar da União
        yield "ckan_conjunto", None, CKAN_SHOW + ident
    # Planilha da União desde 2008: abrir e ler o cabeçalho
    yield "planilha", None, ("https://www.tesourotransparente.gov.br/ckan/dataset/bcd753b8-e79d-4964-a565-977d23bada0d"
                             "/resource/1043f379-e7fb-4c18-be52-345b8672ccfb/download/despesauniao.xlsx")
    # INEP 2009 (na rodada 2 a conexão caiu): de novo, e o Censo Superior de 2009
    yield "inep", 2009, config.INEP_CENSO_ESCOLAR.format(ano=2009)
    yield "inep", 2009, config.INEP_CENSO_SUPERIOR.format(ano=2009)


DESPESA_UNIAO = ("https://www.tesourotransparente.gov.br/ckan/dataset/bcd753b8-e79d-4964-a565-977d23bada0d"
                 "/resource/1043f379-e7fb-4c18-be52-345b8672ccfb/download/despesauniao.xlsx")


def rodada4():
    """SIOPE: o que são os arquivos de download.do; União: Função 12 por ano na planilha desde 2008."""
    yield "siope_rotulos", None, SIOPE + "download.do"
    yield "uniao_funcao12", None, DESPESA_UNIAO
    yield "siope_municipal", None, SIOPE + "dadosInformadosMunicipio.do"
    yield "siope_municipal", None, SIOPE + "demonstrativoFuncaoEducacao.do"


def rodada5():
    """SIOPE: o formulário por município responde dados? (Fortaleza = 230440, IBGE sem dígito)."""
    yield "siope_form", None, SIOPE + "dadosInformadosMunicipio.do"
    yield "siope_form", None, SIOPE + "demonstrativoFuncaoEducacao.do"
    base = SIOPE + "dadosInformadosMunicipio.do?acao=pesquisar&pag=result&cod_uf=23&cod_muni=230440&num_ano=2010&num_peri=6"
    for tp in ["D", "R", "I", "P"]:
        yield "siope_consulta", 2010, f"{base}&tp_relatorio={tp}"
    yield "siope_consulta", 2010, (SIOPE + "demonstrativoFuncaoEducacao.do?acao=pesquisar&pag=result"
                                   "&cod_uf=23&municipios=230440&anos=2010&periodos=6")


RODADAS = {1: rodada1, 2: rodada2, 3: rodada3, 4: rodada4, 5: rodada5}


def _texto(html: str) -> str:
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _formulario(r, info):
    """Guarda o HTML do formulário (selects com nomes e opções, campos ocultos com valores)."""
    m = re.search(r"<form.*?</form>", r.text, re.S | re.I)
    form = m.group(0) if m else r.text
    info["selects"] = {n: re.findall(r'<option[^>]*value=["\']([^"\']*)', corpo)[:8]
                       for n, corpo in re.findall(r'<select[^>]*name=["\']([^"\']+)["\'][^>]*>(.*?)</select>', form, re.S | re.I)}
    info["inputs"] = re.findall(r"<input[^>]*>", form, re.I)[:25]
    info["scripts"] = re.findall(r"(?:submit|action|location)[^;]{0,160}", " ".join(re.findall(r"<script[^>]*>(.*?)</script>", r.text, re.S | re.I)))[:12]


def _rotulos(r, info):
    """Texto de cada link (o que é cada arquivo) e, para os 6 primeiros, nome e tamanho do arquivo."""
    html = r.text
    pares = re.findall(r'<a[^>]+href=["\']([^"\']+castor[^"\']+)["\'][^>]*>(.*?)</a>', html, re.S | re.I)
    texto = lambda t: re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", t)).strip()
    # o rótulo às vezes está na linha da tabela, antes do link
    linhas = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.S | re.I)
    por_link = {}
    for ln in linhas:
        for u in re.findall(r'href=["\']([^"\']+castor[^"\']+)', ln):
            por_link[u] = texto(ln)[:160]
    info["arquivos"] = [{"url": u, "rotulo": por_link.get(u) or texto(t)} for u, t in pares]
    for a in info["arquivos"][:6]:
        try:
            h = http.get(a["url"], timeout=60, stream=True)
            a["tipo"], a["disposicao"], a["tamanho"] = (h.headers.get("Content-Type"),
                                                       h.headers.get("Content-Disposition"),
                                                       h.headers.get("Content-Length"))
            h.close()
        except Exception as e:  # noqa: BLE001
            a["erro"] = str(e)[:120]


def _uniao_funcao12(r, info):
    """Soma a Função 12 (Educação) por ano: aplicação direta × transferência × intra (valor PAGO)."""
    import io
    import openpyxl
    from coletor import contas
    ws = openpyxl.load_workbook(io.BytesIO(r.content), read_only=True, data_only=True).worksheets[0]
    linhas = ws.iter_rows(values_only=True)
    cab = list(next(linhas))
    i = {c: cab.index(c) for c in ("Funcao_cod", "Subfuncao_cod", "Modalidade_cod", "Ano", "Valor", "Esfera_cod")}
    anos, esferas = {}, set()
    for row in linhas:
        esferas.add(row[i["Esfera_cod"]])
        if str(row[i["Funcao_cod"]]).zfill(2) != "12":
            continue
        ln = {"funcao": "12", "subfuncao": row[i["Subfuncao_cod"]], "modalidade": row[i["Modalidade_cod"]]}
        classe = contas.classificar(ln)
        a = anos.setdefault(str(row[i["Ano"]]), {"direta": 0.0, "transferencia": 0.0, "intra": 0.0,
                                                 "superior": 0.0, "basica": 0.0})
        v = float(row[i["Valor"]] or 0)
        a[classe] = a.get(classe, 0.0) + v
        if classe == "direta":
            nv = contas.nivel(ln)
            if nv in a:
                a[nv] += v
    info["esferas"] = sorted(map(str, esferas))
    info["funcao12_por_ano_bilhoes"] = {k: {c: round(v / 1e9, 2) for c, v in d.items()} for k, d in sorted(anos.items())}


def _planilha(r, info):
    """Baixa uma planilha .xlsx e guarda abas, cabeçalho e 3 linhas de amostra."""
    import io
    import openpyxl
    wb = openpyxl.load_workbook(io.BytesIO(r.content), read_only=True, data_only=True)
    info["abas"] = {}
    for ws in wb.worksheets[:6]:
        linhas = [[c for c in row if c is not None][:25] for row in ws.iter_rows(max_row=8, values_only=True)]
        info["abas"][ws.title] = [ln for ln in linhas if ln][:6]


def _descobrir(r, info, todos_links=False):
    tipo = info.get("tipo") or ""
    if "json" in tipo:
        corpo = r.json()
        if isinstance(corpo, dict) and isinstance(corpo.get("result"), dict) and "resources" in corpo["result"]:
            pk = corpo["result"]                                                  # CKAN package_show
            info["conjunto"] = pk.get("title")
            info["arquivos"] = [{"nome": x.get("name"), "formato": x.get("format"), "url": x.get("url")}
                                for x in pk["resources"]][:80]
        elif isinstance(corpo, dict) and isinstance(corpo.get("result"), dict):   # CKAN package_search
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
        info["links"] = (links if todos_links else [u for u in links if PALAVRAS.search(u)])[:80]
        # formulários (páginas JSP/JSF de consulta): campos e opções, p/ montar a consulta depois
        info["formularios"] = [
            {"acao": a, "campos": sorted(set(re.findall(r'name=["\']([^"\']+)', f)))[:30]}
            for a, f in re.findall(r'<form[^>]*action=["\']([^"\']*)["\'][^>]*>(.*?)</form>', html, re.S | re.I)][:5]
        opcoes = re.findall(r'<option[^>]*value=["\']([^"\']*)["\']', html)
        if opcoes:
            info["opcoes"] = opcoes[:60]
        m = re.search(r"<title>(.*?)</title>", html, re.S | re.I)
        info["titulo"] = m.group(1).strip()[:120] if m else None
        info["redireciona_para"] = r.url if r.url else None


def sondar(url: str, fonte: str = "") -> dict:
    try:
        r = http.get(url, timeout=90, stream=True)
        info = {"status": r.status_code, "tipo": r.headers.get("Content-Type"),
                "tamanho": r.headers.get("Content-Length")}
        if fonte == "uniao_funcao12":
            _uniao_funcao12(r, info)
        elif fonte == "siope_form":
            _formulario(r, info)
        elif fonte == "siope_consulta":
            info["bytes"] = len(r.content)
            info["texto"] = _texto(r.text)[:1800]
        elif fonte == "siope_rotulos":
            _rotulos(r, info)
        elif url.endswith(".xlsx"):
            _planilha(r, info)
        elif not any(t in (info["tipo"] or "") for t in ("zip", "octet")):
            _descobrir(r, info, todos_links="siope" in url)     # zip grande: só o cabeçalho
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
        r = {"fonte": fonte, "ano": ano, "url": url, **sondar(url, fonte)}
        print(json.dumps(r, ensure_ascii=False, default=str))
        res.append(r)
    (SAIDA / f"rodada_{rodada}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
