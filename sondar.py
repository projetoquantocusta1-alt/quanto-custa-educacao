"""Sondagem: descobre, para cada fonte e ano desde 2009, se o dado existe e em que formato.

Roda ANTES de escrever os coletores. Só lê endereços públicos e grava o
resultado em dados_brutos/sondagem/resultado.json (status, tipo, tamanho).

Uso: python sondar.py            # todas as fontes, anos de amostra
     python sondar.py siconfi    # só uma fonte
"""
import json
import sys
from pathlib import Path

import config
from coletor import http

ANOS_AMOSTRA = [2009, 2010, 2013, 2017, 2021, 2024]
SAIDA = Path(__file__).parent / "dados_brutos" / "sondagem"


def alvos():
    s = config.SICONFI_API
    for ano in ANOS_AMOSTRA:
        # Siconfi: DCA anual de um estado (CE=23) e de uma capital (Fortaleza=2304400)
        yield "siconfi", ano, f"{s}/dca?an_exercicio={ano}&id_ente=23"
        yield "siconfi", ano, f"{s}/dca?an_exercicio={ano}&id_ente=2304400"
        yield "transparencia", ano, config.TRANSPARENCIA_ORCAMENTO.format(ano=ano)
        yield "inep", ano, config.INEP_CENSO_ESCOLAR.format(ano=ano)
    yield "siconfi", None, f"{s}/entes"
    yield "ipca", None, config.IPCA_SGS.format(ano=config.ANO_INICIAL)
    # SIOPE (FNDE): endereço dos dados abertos ainda não confirmado — sondar as páginas de entrada.
    yield "siope", None, "https://www.gov.br/fnde/pt-br/acesso-a-informacao/acoes-e-programas/programas/siope"
    yield "siope", None, "https://www.fnde.gov.br/siope/"


def sondar(url: str) -> dict:
    try:
        # stream=True: só o cabeçalho; não baixa os zips grandes do INEP
        r = http.get(url, timeout=60, stream=True)
        info = {"status": r.status_code, "tipo": r.headers.get("Content-Type"),
                "tamanho": r.headers.get("Content-Length")}
        if "json" in (info["tipo"] or ""):
            corpo = r.json()
            itens = corpo.get("items") if isinstance(corpo, dict) else corpo
            info["itens"] = len(itens) if isinstance(itens, list) else None
        r.close()
        return info
    except Exception as e:  # noqa: BLE001 — sondagem: registrar qualquer falha
        return {"erro": f"{type(e).__name__}: {e}"[:300]}


def main():
    so = set(sys.argv[1:])
    SAIDA.mkdir(parents=True, exist_ok=True)
    res = []
    for fonte, ano, url in alvos():
        if so and fonte not in so:
            continue
        r = {"fonte": fonte, "ano": ano, "url": url, **sondar(url)}
        print(json.dumps(r, ensure_ascii=False))
        res.append(r)
    (SAIDA / "resultado.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
