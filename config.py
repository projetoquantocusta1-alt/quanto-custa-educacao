"""Configuração do Projeto Quanto Custa — Educação.

Quanto o Brasil gasta com educação desde 2009: União, estados e municípios,
separando QUEM PAGA de QUEM GASTA para não contar o mesmo dinheiro duas vezes.

Decisões tomadas (ver PLANEJAMENTO.md): Brasil inteiro; gasto = liquidado, com o
empenhado não liquidado como indicador à parte; ensino superior separado da educação básica.
"""

ANO_INICIAL = 2009
ABRANGENCIA = "BR"             # União + 27 UFs + 5.570 municípios
VERSAO = 1                     # subir quando a regra de cálculo mudar: anos antigos são refeitos

USER_AGENT = "ProjetoQuantoCusta/1.0 (painel de transparencia com dados abertos)"
PAUSA_ENTRE_REQUISICOES = 0.3  # segundos entre chamadas ao mesmo site
ORCAMENTO_MINUTOS = 300        # o GitHub Actions corta em 6 h

# Fase da despesa usada nos totais: LIQUIDADA (o serviço foi entregue / a obra medida).
# Empenhado − liquidado no ano vira o indicador "empenhado não liquidado" (vira restos a pagar).
# Restos a pagar liquidados no ano seguinte NUNCA somam no ano seguinte (seria contar duas vezes):
# aparecem só no indicador de restos a pagar, ligados ao ano de origem.
FASE_DESPESA = "liquidada"

# --- Recorte: Função 12 – Educação (Portaria MOG 42/1999) ---
FUNCAO_EDUCACAO = "12"
SUBFUNCOES = {
    "361": "Ensino fundamental",
    "362": "Ensino médio",
    "363": "Ensino profissional",
    "364": "Ensino superior",
    "365": "Educação infantil",
    "366": "Educação de jovens e adultos",
    "367": "Educação especial",
    "368": "Educação básica",          # usada por alguns entes; conferir na sondagem desde quando
}
SUBFUNCAO_OUTRAS = "Outras (administração, previdência etc. dentro da Função 12)"

# Nível de ensino: o superior fica sempre separado da educação básica.
# 363 (profissional) é majoritariamente técnico de nível médio → básica.
SUBFUNCOES_SUPERIOR = {"364"}
SUBFUNCOES_BASICA = {"361", "362", "363", "365", "366", "367", "368"}
# Gasto sem subfunção de ensino (ex.: 122 administração) de uma universidade ou instituto
# federal conta como superior; nos demais entes fica em "nao_classificado".

# --- Dupla contagem ---
# Modalidades de aplicação que são TRANSFERÊNCIA para outro ente (o dinheiro será gasto lá).
# Saem do total "quem gasta" e entram no mapa "caminho do dinheiro".
MODALIDADES_TRANSFERENCIA = {
    "20": "Transferências à União",
    "22": "Execução orçamentária delegada à União",
    "30": "Transferências a estados e DF",
    "31": "Transferências a estados e DF — fundo a fundo",
    "32": "Execução orçamentária delegada a estados e DF",
    "35": "Transferências fundo a fundo a estados e DF (LC 141)",
    "36": "Transferências a estados e DF (LC 141)",
    "40": "Transferências a municípios",
    "41": "Transferências a municípios — fundo a fundo",
    "42": "Execução orçamentária delegada a municípios",
    "45": "Transferências fundo a fundo a municípios (LC 141)",
    "46": "Transferências a municípios (LC 141)",
}
# 71 (consórcios públicos) NÃO está na lista: os consórcios não são coletados, então o
# repasse a eles conta como gasto de quem repassou (senão o dinheiro sumiria do total).
MODALIDADE_INTRA = "91"        # intraorçamentária: nunca soma (é o ente pagando a si mesmo)

# Separados do total: mostrados à parte em vez de somar.
SEPARAR_EBSERH = True          # hospitais universitários
SEPARAR_INATIVOS = True        # aposentados e pensionistas pagos pela Função 12

# --- Mínimos legais ---
MINIMO_ESTADOS_MUNICIPIOS = 0.25       # CF art. 212: 25% da receita de impostos e transferências
MINIMO_UNIAO = 0.18                    # CF art. 212 (suspenso pela EC 95 em 2018–2023; conferir)
FUNDEB_PROFISSIONAIS = {2009: 0.60, 2021: 0.70}   # Lei 11.494/2007 → Lei 14.113/2020
META_PNE_PIB = 0.10                    # PNE 2014–2024, meta 20

# --- Fontes ---
# Sites que mandam o certificado sem o intermediário: a cadeia é completada (coletor/cadeia.py),
# a verificação TLS continua ligada.
HOSTS_CADEIA_INCOMPLETA = {"download.inep.gov.br"}

# URLs exatas a confirmar com sondar.py. As marcadas com "?" ainda não foram testadas.
SICONFI_API = "https://apidatalake.tesouro.gov.br/ords/siconfi/tt"
TRANSPARENCIA_ORCAMENTO = "https://portaldatransparencia.gov.br/download-de-dados/orcamento-despesa/{ano}"
INEP_CENSO_ESCOLAR = "https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_{ano}.zip"  # ?
INEP_CENSO_SUPERIOR = "https://download.inep.gov.br/microdados/microdados_censo_da_educacao_superior_{ano}.zip"  # ?
IBGE_PIB_MUNICIPAL = "https://apisidra.ibge.gov.br/values/t/5938/n6/all/v/37/p/all"   # ?
IBGE_POPULACAO = "https://apisidra.ibge.gov.br/values/t/6579/n6/all/v/9324/p/all"
IPCA_SGS = ("https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados"
            "?formato=json&dataInicial=01/01/{ano}")
