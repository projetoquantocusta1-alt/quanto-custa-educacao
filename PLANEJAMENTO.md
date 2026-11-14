# Planejamento — Quanto Custa Educação

Esqueleto local. **Nada foi publicado.**

## Decisões tomadas
- **Abrangência:** Brasil inteiro — União, 27 UFs e 5.570 municípios, desde 2009.
- **Fase da despesa:** **liquidado** do exercício.
- **Indicador "empenhado não liquidado":** empenhado − liquidado, em R$ e em %, por ente, ano e nível.
  Mostra o dinheiro comprometido que não virou serviço entregue no ano (vai para restos a pagar).
- **Superior separado da básica:** subfunção 364 = superior; 361, 362, 363, 365–368 = básica.
  O gasto administrativo de universidade ou instituto federal conta como superior.
  Hospitais universitários (EBSERH) e aposentados ficam à parte.
- **Ordem de construção:** mantida (abaixo).

## Como não contar o dinheiro duas vezes (`coletor/contas.py`, com testes)
1. **Entre esferas:** o repasse (modalidades 20–46) sai do total de quem repassou; o dinheiro
   é contado uma vez só, no ente que o gastou. Isso vale para União→estado/município e estado→município.
   O repasse aparece só no "caminho do dinheiro".
2. **Dentro do ente:** modalidade 91 (intraorçamentária) nunca soma.
3. **Entre anos:** restos a pagar liquidados no ano seguinte não somam nesse ano.
   Ficam ligados ao ano de origem, num indicador próprio.
4. **FUNDEB:** a contribuição de estados e municípios é dedução de receita, não despesa.
   O gasto entra uma vez só, quando o ente aplica o dinheiro do fundo.
5. **Consórcios (71):** contam com quem repassou, porque os consórcios não são coletados.
6. **Conferência:** o que a origem diz ter repassado é comparado com o que os destinos declaram
   ter recebido (`conferir_transferencias`). Diferenças grandes aparecem em Pontos de atenção.

## Fontes e desde quando (medido pelas sondagens 1–4, novembro de 2026)
| Esfera | Fonte | Anos | Fase | Observação |
|---|---|---|---|---|
| União | Portal da Transparência — orçamento da despesa (zip anual) | **2014+** | empenhado, liquidado, pago | 2009–2013 dão 403 |
| União | Tesouro — "Despesas da União mensais desde 2008" (xlsx) | **2008 → início de 2019** | **pago** | tem função, subfunção, ação e modalidade, sem órgão; pode incluir restos a pagar pagos |
| União | Tesouro — COFOG do governo central (csv) | 2010–2024 | — | classificação internacional, para conferência |
| União | Siconfi — DCA da União (API) | 2013+ | empenhado, liquidado, pago | conferência |
| Estados e municípios | Siconfi — DCA (API) | **2013+** | empenhado, liquidado, pago | 2009–2012 vêm vazios; 5.598 entes |
| Estados e municípios | Siconfi — RREO (API) | 2015+ | — | conferência e mínimos legais |
| Estados e municípios | SIOPE — consultas públicas por município e UF | 2005+ (no formulário) | — | **consultas protegidas por captcha** (rodada 5): o robô não pode usá-las; os "downloads" do SIOPE são só instaladores |
| Matrículas | INEP — Censo Escolar e Censo da Educação Superior | 2009+ (superior), 2013+ testado (escolar) | — | precisa da cadeia de certificado completada (`coletor/cadeia.py`); o zip de 2009 do Censo Escolar cortou a conexão |
| IPCA | Banco Central (SGS 433) | 2009+ | — | ok |

Primeiro número real (planilha do Tesouro, Função 12, **valor pago**, R$ bilhões):
2009: aplicação direta 21,0 · repasses 9,7 · intra 3,5. Em 2018: 71,0 · 23,9 · 8,7.
Pela subfunção, o superior aparece com 13,0 em 2009. Sem a coluna de órgão, a administração das
universidades não pode ser somada ao superior, então para 2009–2013 a divisão básica × superior é aproximada.

Consequências:
- **União 2014+:** liquidado, com órgão (separa universidades e institutos federais com precisão).
- **União 2009–2013:** valor pago do Tesouro, marcado no site como "série aproximada".
  Falta separar os restos a pagar pagos. Seguir procurando o liquidado desse período.
- **Estados e municípios 2013+:** Siconfi.
- **Estados e municípios 2009–2012: ainda sem fonte automática.** O SIOPE exige captcha, e o robô não vai
  contorná-lo. Próximas candidatas: FINBRA antigo no Siconfi ("Consultar Contas Anuais", página JSF) e os
  conjuntos do FNDE/SIOPE no dados.gov.br (a API exige chave gratuita). Se nenhuma servir, o site começa
  estados e municípios em 2013 e mostra só a União desde 2009.

## Ordem
1. Sondagem: rodar `sondar.yml` no Actions, porque esta máquina não alcança os sites do governo.
2. União.
3. Estados + INEP.
4. Municípios (5.570, em fila com limite de tempo).
5. FUNDEB, programas e emendas.

## Páginas
Início · Visão geral (% do PIB × meta do PNE; básica e superior lado a lado) · Por aluno × IDEB ·
União/universidades · Estados e municípios (25%, 70% do FUNDEB, piso) · FUNDEB · Programas federais ·
**Empenhado não liquidado** (ranking por ente, evolução, básica × superior) · Emendas para educação ·
Pontos de atenção · Metodologia · Histórico.
