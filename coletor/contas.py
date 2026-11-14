"""Regras de contagem: o coração do projeto.

Cada linha de despesa (de qualquer esfera) é classificada antes de somar:
  - "direta":        o ente gastou com educação → entra no total "quem gasta";
  - "transferencia": o ente repassou a outro ente → entra só no "caminho do dinheiro"
                     (o dinheiro é contado UMA vez, no ente que o gastou);
  - "intra":         modalidade 91 → descartada;
  - "separada":      EBSERH / inativos → mostrada à parte (config.SEPARAR_*);
  - "fora":          não é Função 12.

Os gastos diretos ainda são divididos por nível: "basica", "superior" ou "nao_classificado".

Fase: o total usa o LIQUIDADO do exercício. O empenhado − liquidado vira o indicador
"nao_liquidado". Restos a pagar de anos anteriores (linha com 'restos_a_pagar': True)
nunca entram no total do ano em que foram liquidados.

Formato de uma linha:
  {'funcao', 'subfuncao', 'modalidade', 'empenhado', 'liquidado',
   'ies'?, 'ebserh'?, 'inativos'?, 'restos_a_pagar'?}
"""
import config

CLASSES = ("direta", "transferencia", "intra", "separada", "fora")
NIVEIS = ("basica", "superior", "nao_classificado")


def classificar(linha: dict) -> str:
    if str(linha.get("funcao", "")).zfill(2) != config.FUNCAO_EDUCACAO:
        return "fora"
    mod = str(linha.get("modalidade", "")).zfill(2)
    if mod == config.MODALIDADE_INTRA:
        return "intra"
    if mod in config.MODALIDADES_TRANSFERENCIA:
        return "transferencia"
    if (config.SEPARAR_EBSERH and linha.get("ebserh")) or (config.SEPARAR_INATIVOS and linha.get("inativos")):
        return "separada"
    return "direta"


def etapa(subfuncao) -> str:
    return config.SUBFUNCOES.get(str(subfuncao).zfill(3), config.SUBFUNCAO_OUTRAS)


def nivel(linha: dict) -> str:
    sub = str(linha.get("subfuncao", "")).zfill(3)
    if sub in config.SUBFUNCOES_SUPERIOR:
        return "superior"
    if sub in config.SUBFUNCOES_BASICA:
        return "basica"
    # administração, TI etc. de universidade/instituto federal: é custo do superior
    return "superior" if linha.get("ies") else "nao_classificado"


def _v(linha, campo) -> float:
    return float(linha.get(campo) or 0)


def somar(linhas: list[dict]) -> dict:
    """Totais (liquidado) por classe; e, para os gastos diretos, por nível e etapa,
    com o empenhado não liquidado ao lado."""
    out = {
        "liquidado": {c: 0.0 for c in CLASSES},
        "por_nivel": {n: {"liquidado": 0.0, "empenhado": 0.0} for n in NIVEIS},
        "por_etapa": {},
        "restos_a_pagar_liquidados": 0.0,   # informativo, NÃO soma no ano
    }
    for ln in linhas:
        c = classificar(ln)
        if ln.get("restos_a_pagar"):
            if c == "direta":
                out["restos_a_pagar_liquidados"] += _v(ln, "liquidado")
            continue
        liq = _v(ln, "liquidado")
        out["liquidado"][c] += liq
        if c != "direta":
            continue
        n = out["por_nivel"][nivel(ln)]
        n["liquidado"] += liq
        n["empenhado"] += _v(ln, "empenhado")
        e = etapa(ln.get("subfuncao", ""))
        out["por_etapa"][e] = out["por_etapa"].get(e, 0.0) + liq
    for n in out["por_nivel"].values():
        n.update(nao_liquidado(n["empenhado"], n["liquidado"]))
    return out


def nao_liquidado(empenhado: float, liquidado: float) -> dict:
    """Indicador: quanto foi comprometido (empenhado) e não entregue (liquidado) no ano."""
    valor = max(empenhado - liquidado, 0.0)
    return {"nao_liquidado": valor,
            "pct_nao_liquidado": valor / empenhado if empenhado else None}


def conferir_transferencias(enviado_pela_origem: float, recebido_no_destino: float,
                            tolerancia: float = 0.02) -> dict:
    """Conferência da dupla contagem: o que a União/estado diz que repassou
    deve bater (com folga) com o que os destinos declaram ter recebido."""
    dif = recebido_no_destino - enviado_pela_origem
    rel = dif / enviado_pela_origem if enviado_pela_origem else None
    return {"diferenca": dif, "relativa": rel,
            "confere": None if rel is None else abs(rel) <= tolerancia}


def minimo_fundeb_profissionais(ano: int) -> float:
    if ano < min(config.FUNDEB_PROFISSIONAIS):
        return 0.0
    return max(p for a, p in config.FUNDEB_PROFISSIONAIS.items() if a <= ano)


def cumpre_25(aplicado_mde: float, receita_impostos: float) -> dict:
    """Mínimo constitucional (art. 212) para estados e municípios."""
    pct = aplicado_mde / receita_impostos if receita_impostos else None
    return {"percentual": pct, "minimo": config.MINIMO_ESTADOS_MUNICIPIOS,
            "cumpre": None if pct is None else pct >= config.MINIMO_ESTADOS_MUNICIPIOS}


def por_aluno(gasto: float, matriculas: int | None):
    return gasto / matriculas if matriculas else None
