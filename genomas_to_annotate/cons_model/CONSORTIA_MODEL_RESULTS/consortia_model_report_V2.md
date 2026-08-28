# UC 8.1 Consortium Modeling Report V2

Gerado a partir dos insumos de `genomas_to_annotate/cons_model`.

## Racional da V2

O primeiro modelo de consorcios usava uma logica sequencial de set cover. Essa abordagem e util para maximizar cobertura, mas pode enviesar a selecao para o primeiro isolado com maior inventario de genes ou compostos. Depois dessa primeira escolha, os demais isolados podem entrar apenas por acrescentarem poucos genes ou poucos compostos novos, gerando um consorcio eficiente em cobertura, mas potencialmente redundante.

A V2 muda a regra de decisao: em vez de escolher isolados um por um, ela avalia todas as combinacoes possiveis de `3` isolados dentro do universo oficial da imagem de Metal. Cada trio e pontuado como um sistema completo. Assim, o modelo prioriza comportamento consorcial balanceado, e nao o efeito marginal de um primeiro membro dominante.

## Criterios de pontuacao V2

- Exatamente `3` isolados por consorcio.
- Universo candidato: os `17` isolados definidos pela imagem `UC_8.1/UC8.1_METAL.png`.
- Evidencia primaria: cobertura total de compostos da classe alvo.
- Evidencias secundarias: cobertura de KOs, media DCPIP alvo e media DCPIP geral.
- Evidencias anti-redundancia: perdas leave-one-out de compostos e genes, alem da sobreposicao media por Jaccard entre pares de isolados.
- Metrica DCPIP alvo: `PL_mean` para `Aliphatic`; `PP_mean` para `Polyaromatic`.

Pesos usados no score V2:

| Componente | Peso |
|---|---:|
| Cobertura de compostos | 0.30 |
| Cobertura de KOs | 0.10 |
| Media DCPIP alvo | 0.10 |
| Media DCPIP geral | 0.05 |
| Perda minima leave-one-out de compostos | 0.20 |
| Perda minima leave-one-out de genes | 0.10 |
| Complementaridade por compostos | 0.10 |
| Complementaridade por genes | 0.05 |

## Consorcios V2 selecionados com 3 isolados

| Classe alvo | Trio V2 selecionado | Cobertura de compostos | Cobertura de KOs | DCPIP alvo medio | Redundancia media | Score V2 |
|---|---|---:|---:|---:|---:|---:|
| Aliphatic | BD127 + BD54 + BG1 | 55/59 (93.22%) | 100/153 (65.36%) | 73.00 | 0.511 | 0.908 |
| Polyaromatic | BD120 + BD158 + BD61 | 40/44 (90.91%) | 59/83 (71.08%) | 66.66 | 0.509 | 0.891 |

## Analise de sensibilidade: cobertura bruta versus score balanceado

Esta etapa separa explicitamente dois criterios que competem entre si. O trio de maior cobertura bruta nem sempre e o melhor trio experimentalmente ou o menos redundante. A V2 permite aceitar uma pequena perda de cobertura quando isso melhora DCPIP, cobertura de KOs e contribuicao minima por membro.

| Classe alvo | Trio selecionado V2 | Cobertura V2 | Melhor trio por cobertura bruta | Cobertura maxima | Por que o V2 foi mantido |
|---|---|---:|---|---:|---|
| Aliphatic | BD127 + BD54 + BG1 | 55/59 (93.22%) | BD127 + BD54 + BG1 | 55/59 (93.22%) | Coincide com a melhor cobertura e tambem fica no topo do score V2. |
| Polyaromatic | BD120 + BD158 + BD61 | 40/44 (90.91%) | BD117 + BD120 + BD127 | 41/44 (93.18%) | Aceita pequena perda de cobertura bruta para ganhar em score balanceado, DCPIP e contribuicao minima por membro. |

## Resultado V2 para Aliphatic

Trio selecionado:

```text
BD127 + BD54 + BG1
```

Este trio cobre `55` de `59` compostos `Aliphatic` (`93.22%`) usando apenas tres isolados. Tambem cobre `100` de `153` KOs alifaticos (`65.36%`).

A perda minima leave-one-out de compostos e `4`. Isso significa que todo membro selecionado contribui com pelo menos essa quantidade de compostos que nao sao recuperados quando ele e removido do trio. Esse criterio reduz a tendencia anterior de manter isolados que acrescentam apenas um numero muito pequeno de alvos unicos.

| Isolado | Taxon | Grupo Metal | Compostos da classe | Genes da classe | KOs da classe | DCPIP alvo | Media geral |
|---|---|---|---:|---:|---:|---:|---:|
| BD127 | Achromobacter | Metal_Group_4 | 43 | 56 | 56 | 59.21 | 40.72 |
| BD54 | Acinetobacter | Metal_Group_1 | 34 | 60 | 60 | 82.22 | 75.96 |
| BG1 | Bacillus amyloliquefaciens | Metal_Group_4 | 30 | 53 | 53 | 77.56 | 76.49 |

Trios `Aliphatic` mais bem ranqueados:

| Rank | Trio | Cobertura | KOs | DCPIP alvo | Min. perda compostos | Jaccard compostos | Score V2 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | BD127 + BD54 + BG1 | 55/59 (93.22%) | 100/153 (65.36%) | 73.00 | 4 | 0.511 | 0.908 |
| 2 | BD127 + BG1 + E7 | 55/59 (93.22%) | 100/153 (65.36%) | 73.23 | 4 | 0.511 | 0.906 |
| 3 | BD120 + BD127 + BD54 | 54/59 (91.53%) | 100/153 (65.36%) | 75.13 | 4 | 0.567 | 0.895 |
| 4 | BD120 + BD127 + E7 | 54/59 (91.53%) | 100/153 (65.36%) | 75.36 | 4 | 0.567 | 0.893 |
| 5 | BD127 + BD162 + BD54 | 55/59 (93.22%) | 100/153 (65.36%) | 68.31 | 4 | 0.511 | 0.889 |
| 6 | BD127 + BD162 + E7 | 55/59 (93.22%) | 100/153 (65.36%) | 68.54 | 4 | 0.511 | 0.887 |
| 7 | BD120 + BD54 + BD61 | 51/59 (86.44%) | 107/153 (69.93%) | 82.60 | 3 | 0.563 | 0.880 |
| 8 | BD127 + BD54 + BD9 | 55/59 (93.22%) | 100/153 (65.36%) | 67.69 | 4 | 0.511 | 0.880 |
| 9 | BD120 + BD61 + E7 | 51/59 (86.44%) | 107/153 (69.93%) | 82.82 | 3 | 0.563 | 0.878 |
| 10 | BD127 + BD9 + E7 | 55/59 (93.22%) | 100/153 (65.36%) | 67.92 | 4 | 0.511 | 0.878 |

## Resultado V2 para Polyaromatic

Trio selecionado:

```text
BD120 + BD158 + BD61
```

Este trio cobre `40` de `44` compostos `Polyaromatic` (`90.91%`) usando apenas tres isolados. Tambem cobre `59` de `83` KOs poliaromaticos (`71.08%`).

A perda minima leave-one-out de compostos e `4`, mostrando que nenhum membro selecionado e meramente residual. Cada isolado contribui com uma fracao mensuravel e nao trivial da cobertura do trio.

| Isolado | Taxon | Grupo Metal | Compostos da classe | Genes da classe | KOs da classe | DCPIP alvo | Media geral |
|---|---|---|---:|---:|---:|---:|---:|
| BD120 | Bacillus subtilis | Metal_Group_4 | 27 | 40 | 40 | 81.81 | 82.89 |
| BD158 | Salinicola | Metal_Group_1 | 21 | 31 | 31 | 58.54 | 62.73 |
| BD61 | Ochrobactrum | Metal_Group_4 | 29 | 34 | 34 | 59.63 | 70.61 |

Trios `Polyaromatic` mais bem ranqueados:

| Rank | Trio | Cobertura | KOs | DCPIP alvo | Min. perda compostos | Jaccard compostos | Score V2 |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | BD120 + BD158 + BD61 | 40/44 (90.91%) | 59/83 (71.08%) | 66.66 | 4 | 0.509 | 0.891 |
| 2 | BD158 + BD61 + BG1 | 40/44 (90.91%) | 56/83 (67.47%) | 64.53 | 4 | 0.505 | 0.887 |
| 3 | BD158 + BD162 + BD61 | 40/44 (90.91%) | 56/83 (67.47%) | 64.22 | 4 | 0.505 | 0.883 |
| 4 | BD158 + BD61 + BD9 | 40/44 (90.91%) | 56/83 (67.47%) | 55.48 | 4 | 0.505 | 0.858 |
| 5 | BD126 + BD158 + BD61 | 40/44 (90.91%) | 59/83 (71.08%) | 52.41 | 4 | 0.509 | 0.846 |
| 6 | BD117 + BD120 + BD127 | 41/44 (93.18%) | 60/83 (72.29%) | 60.23 | 3 | 0.426 | 0.836 |
| 7 | BD117 + BD120 + BD54 | 40/44 (90.91%) | 53/83 (63.86%) | 76.05 | 3 | 0.439 | 0.832 |
| 8 | BD158 + BD163 + BD61 | 39/44 (88.64%) | 54/83 (65.06%) | 60.53 | 4 | 0.540 | 0.829 |
| 9 | BD117 + BD54 + BG1 | 40/44 (90.91%) | 50/83 (60.24%) | 73.92 | 3 | 0.435 | 0.828 |
| 10 | BD117 + BD162 + BD54 | 40/44 (90.91%) | 50/83 (60.24%) | 73.61 | 3 | 0.435 | 0.824 |

## Interpretacao

A V2 e mais conservadora para desenho experimental porque remove o quarto isolado marginal do primeiro modelo e obriga a selecao a ser explicavel como um sistema de tres membros. Os trios selecionados devem ser interpretados como consorcios compactos e menos redundantes, nao como solucoes de cobertura maxima absoluta.

Para `Aliphatic`, o trio V2 preserva cobertura relevante, aumenta o suporte medio de DCPIP e evita que a escolha seja dominada por um primeiro isolado de grande inventario. Para `Polyaromatic`, o trio V2 preserva a maior parte da cobertura e mantem boa contribuicao minima por membro.

O report V2 deve ser usado quando a prioridade experimental e testar consorcios menores, menos redundantes e mais faceis de interpretar. O modelo anterior permanece util como referencia de cobertura maxima, mas a V2 responde melhor a preocupacao de que um primeiro isolado dominante pode enviesar uma selecao sequencial.

## Arquivos gerados

- `consortia_model_report_V2.md`
- `consortia_model_v2_ranked_trios.csv`
- `consortia_model_v2_selected_trios.csv`
- `consortia_model_v2_validation.json`
