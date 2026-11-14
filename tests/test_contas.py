import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from coletor import contas  # noqa: E402


def L(**kw):
    base = {"funcao": "12", "subfuncao": "361", "modalidade": "90", "empenhado": 100, "liquidado": 100}
    base.update(kw)
    return base


def test_classificar():
    assert contas.classificar(L()) == "direta"
    assert contas.classificar(L(funcao="10")) == "fora"
    assert contas.classificar(L(modalidade="91")) == "intra"
    assert contas.classificar(L(modalidade="40")) == "transferencia"
    assert contas.classificar(L(modalidade=30)) == "transferencia"
    assert contas.classificar(L(modalidade="71")) == "direta"     # consórcio: fica com quem repassou
    assert contas.classificar(L(ebserh=True)) == "separada"


def test_nao_conta_duas_vezes_entre_esferas():
    fnde_repassa = L(modalidade="40", empenhado=50, liquidado=50)    # União → município (PNAE)
    estado_repassa = L(modalidade="40", empenhado=30, liquidado=30)  # estado → município (transporte)
    municipio_gasta = L(empenhado=80, liquidado=80)                  # o mesmo dinheiro, na escola
    t = contas.somar([fnde_repassa, estado_repassa, municipio_gasta])
    assert t["liquidado"]["direta"] == 80
    assert t["liquidado"]["transferencia"] == 80


def test_nao_conta_duas_vezes_entre_anos():
    do_ano = L(empenhado=100, liquidado=70)
    rp_do_ano_anterior = L(empenhado=0, liquidado=40, restos_a_pagar=True)
    t = contas.somar([do_ano, rp_do_ano_anterior])
    assert t["liquidado"]["direta"] == 70
    assert t["restos_a_pagar_liquidados"] == 40


def test_superior_separado_da_basica():
    t = contas.somar([
        L(subfuncao="361", liquidado=10, empenhado=10),
        L(subfuncao="363", liquidado=5, empenhado=5),          # técnico de nível médio → básica
        L(subfuncao="364", liquidado=20, empenhado=20),
        L(subfuncao="122", liquidado=7, empenhado=7, ies=True),  # administração da universidade
        L(subfuncao="122", liquidado=3, empenhado=3),            # administração da secretaria
    ])
    assert t["por_nivel"]["basica"]["liquidado"] == 15
    assert t["por_nivel"]["superior"]["liquidado"] == 27
    assert t["por_nivel"]["nao_classificado"]["liquidado"] == 3


def test_indicador_nao_liquidado():
    t = contas.somar([L(empenhado=100, liquidado=75), L(subfuncao="364", empenhado=40, liquidado=40)])
    b = t["por_nivel"]["basica"]
    assert b["nao_liquidado"] == 25 and b["pct_nao_liquidado"] == 0.25
    assert t["por_nivel"]["superior"]["nao_liquidado"] == 0
    assert t["por_nivel"]["nao_classificado"]["pct_nao_liquidado"] is None


def test_conferir_transferencias():
    assert contas.conferir_transferencias(100, 101)["confere"] is True
    assert contas.conferir_transferencias(100, 120)["confere"] is False
    assert contas.conferir_transferencias(0, 5)["confere"] is None


def test_fundeb_e_minimos():
    assert contas.minimo_fundeb_profissionais(2008) == 0.0
    assert contas.minimo_fundeb_profissionais(2015) == 0.60
    assert contas.minimo_fundeb_profissionais(2023) == 0.70
    assert contas.cumpre_25(26, 100)["cumpre"] is True
    assert contas.cumpre_25(24, 100)["cumpre"] is False
    assert contas.cumpre_25(1, 0)["cumpre"] is None
    assert contas.por_aluno(1000, 0) is None
