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

## Fontes e desde quando (a confirmar com `sondar.py`)
| Esfera | Fonte | Desde |
|---|---|---|
| União (MEC, FNDE, universidades, IFs, CAPES, INEP) | Portal da Transparência / SIOP | ~2004 |
| Estados | SIOPE (FNDE) + Siconfi | ~2009 |
| Municípios | SIOPE + Siconfi/FINBRA | ~2009, cobertura irregular |
| Matrículas | Censo Escolar / Censo da Ed. Superior (INEP) | anos 1990 |
| Resultados | IDEB / SAEB | 2005, a cada dois anos |
| PIB, população | IBGE | — |
| IPCA | BCB SGS 433 | — |

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
