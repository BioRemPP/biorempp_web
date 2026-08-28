# Ranking de candidatos a controle negativo por baixa contagem genica

## Objetivo

Este report usa `BioRemPP_Results (9).csv` para ranquear isolados com menor numero de genes associados a `Aliphatic` e `Aromatic`. Em seguida, cruza esses rankings com os resultados DCPIP ja consolidados para identificar candidatos que combinam baixo potencial genomico e menor desempenho experimental.

A leitura proposta e conservadora: um bom controle negativo nao deve ser escolhido apenas por ter poucos genes. Ele deve, preferencialmente, tambem apresentar baixo `PL_mean`, `PP_mean` ou `overall_mean`, conforme o eixo experimental de interesse.

## Criterios usados

- Fonte de genes: `genomas_to_annotate/cons_model/TABLE_RESULTS/BioRemPP_Results (9).csv`.
- Unidade principal de ranking: numero de `genesymbol` unicos por `Sample` e `compoundclass`.
- Metricas auxiliares: KOs unicos, compostos unicos e numero de linhas de evidencia.
- Fonte DCPIP: `CONSORTIA_MODEL_RESULTS/isolate_consolidated_metrics.csv`.
- Para `Aliphatic`, o DCPIP primario usado no score foi `PL_mean`.
- Para `Aromatic`, o DCPIP primario usado no score foi `PP_mean`, por ser o eixo mais conservador para compostos aromaticos/pesados.
- O score de controle negativo combina ranking ascendente de genes e ranking ascendente do DCPIP primario. Quanto menor o score, mais forte o candidato como controle negativo.

## Candidatos prioritarios para controle negativo combinado

Estes isolados aparecem como os candidatos mais interessantes quando se exige baixa contagem genica em `Aliphatic` e `Aromatic`, junto com menor desempenho DCPIP.

| sample | taxon | aliphatic_gene_count | aromatic_gene_count | PL_mean | PP_mean | overall_mean | combined_negative_control_score | metal_authority | in_any_strict_consortium |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BD2 | Staphylococcus | 35 | 23 | 28.31 | 11.99 | 22.87 | 1.50 | False | False |
| BD161 | Rossellomorea | 50 | 33 | 32.66 | 47.57 | 40.12 | 10.12 | False | False |
| BD5 | Dermacoccus nishinomiyaensis | 38 | 26 | 67.11 | 47.27 | 57.19 | 12.25 | False | False |
| BD106 | Stutzerimonas frequens | 58 | 32 | 43.99 | 19.49 | 31.74 | 12.88 | False | False |
| BD83 | Bacillus | 51 | 41 | 49.17 | 23.98 | 36.57 | 14.25 | False | False |
| BD67 | Ochrobactrum | 52 | 33 | 56.50 | 39.36 | 47.93 | 14.50 | False | False |
| BD108 | Stutzerimonas balearica | 51 | 35 | 60.52 | 33.64 | 47.08 | 14.62 | False | False |
| BD96 | Stutzerimonas frequens | 51 | 41 | 41.06 | 39.03 | 40.39 | 15.00 | False | False |
| BD147 | Cellulomonas | 16 | 13 | 71.50 | 63.04 | 67.27 | 15.75 | False | False |
| BD95 | Stutzerimonas frequens | 51 | 41 | 36.70 | 45.26 | 39.55 | 16.00 | False | False |
| BD101 | Stutzerimonas balearica | 51 | 41 | 58.20 | 39.63 | 48.92 | 18.00 | False | False |
| BD8 | Rothia | 39 | 29 | 74.56 | 64.90 | 69.73 | 19.88 | False | False |

## Recomendacao pratica

O candidato mais forte para controle negativo e `BD2`. Ele combina baixa contagem de genes em `Aliphatic` (`35`) e `Aromatic` (`23`) com os menores valores DCPIP do ranking combinado (`PL_mean` 28.31, `PP_mean` 11.99, `overall_mean` 22.87). Isso torna `BD2` o isolado mais defensavel para testar a hipotese de que menor repertorio genico nessas classes acompanha menor degradacao experimental.

Como controles negativos adicionais ou secundarios, os melhores candidatos sao `BD161`, `BD106`, `BD83`, `BD96`, `BD95`, `BD67` e `BD108`, dependendo do eixo experimental priorizado. Para `Aromatic`, `BD106` e especialmente interessante porque une baixa contagem de genes aromaticos (`32`) com `PP_mean` baixo (`19.49`). Para `Aliphatic`, `BD161`, `BD95` e `BD96` aparecem como alternativas por combinarem contagem alifatica baixa/intermediaria com `PL_mean` reduzido.

`BD147` merece uma observacao: ele tem a menor contagem genica em ambas as classes (`16` genes alifaticos e `13` aromaticos), mas o DCPIP e alto (`PL_mean` 71.50, `PP_mean` 63.04). Portanto, ele nao e um bom controle negativo principal se o objetivo for demonstrar menor degradacao. Ele e mais util como contraexemplo biologico: baixa contagem anotacional nao garante, sozinha, baixo desempenho experimental.

## Contraste com os consorcios positivos strict

Este contraste ajuda a posicionar o controle negativo frente aos consorcios strict selecionados anteriormente.

| grupo | amostras | aliphatic_genes_mean | aromatic_genes_mean | PL_mean | PP_mean | overall_mean |
| --- | --- | --- | --- | --- | --- | --- |
| Controle negativo prioritario | BD2 | 35 | 23 | 28.31 | 11.99 | 22.87 |
| Consorcio strict Aliphatic | BD117, BD127, BD163, E7 | 54.75 |  | 71.34 | 54.77 | 63.05 |
| Consorcio strict Polyaromatic | BD117, BD120, BD158, BD61 |  | 34.75 | 77.92 | 69.16 | 73.54 |

## Ranking por baixa contagem genica em Aliphatic

| sample | taxon | unique_gene_count | unique_ko_count | unique_compound_count | PL_mean | PP_mean | overall_mean | negative_control_score | metal_authority | in_aliphatic_strict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BD2 | Staphylococcus | 35 | 35 | 21 | 28.31 | 11.99 | 22.87 | 1.50 | False | False |
| BD161 | Rossellomorea | 50 | 50 | 38 | 32.66 | 47.57 | 40.12 | 6.50 | False | False |
| BD95 | Stutzerimonas frequens | 51 | 51 | 33 | 36.70 | 45.26 | 39.55 | 9.75 | False | False |
| BD96 | Stutzerimonas frequens | 51 | 51 | 33 | 41.06 | 39.03 | 40.39 | 10.25 | False | False |
| BD83 | Bacillus | 51 | 51 | 33 | 49.17 | 23.98 | 36.57 | 11.25 | False | False |
| BD5 | Dermacoccus nishinomiyaensis | 38 | 38 | 26 | 67.11 | 47.27 | 57.19 | 14.75 | False | False |
| BD101 | Stutzerimonas balearica | 51 | 51 | 33 | 58.20 | 39.63 | 48.92 | 14.75 | False | False |
| BD147 | Cellulomonas | 16 | 16 | 17 | 71.50 | 63.04 | 67.27 | 15.00 | False | False |
| BD165 | Bacillus paralicheniformis | 52 | 52 | 31 | 50.71 | 65.80 | 58.26 | 15.75 | False | False |
| BD121 | Bacillus paralicheniformis | 52 | 52 | 31 | 51.12 | 33.19 | 42.16 | 16.25 | False | False |
| BD108 | Stutzerimonas balearica | 51 | 51 | 33 | 60.52 | 33.64 | 47.08 | 17.75 | False | False |
| BD67 | Ochrobactrum | 52 | 52 | 33 | 56.50 | 39.36 | 47.93 | 17.75 | False | False |

## Ranking por baixa contagem genica em Aromatic

| sample | taxon | unique_gene_count | unique_ko_count | unique_compound_count | PL_mean | PP_mean | overall_mean | negative_control_score | metal_authority | in_polyaromatic_strict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BD2 | Staphylococcus | 23 | 23 | 23 | 28.31 | 11.99 | 22.87 | 1.50 | False | False |
| BD106 | Stutzerimonas frequens | 32 | 32 | 27 | 43.99 | 19.49 | 31.74 | 5.75 | False | False |
| BD5 | Dermacoccus nishinomiyaensis | 26 | 26 | 15 | 67.11 | 47.27 | 57.19 | 9.75 | False | False |
| BD67 | Ochrobactrum | 33 | 33 | 29 | 56.50 | 39.36 | 47.93 | 11.25 | False | False |
| BD108 | Stutzerimonas balearica | 35 | 35 | 29 | 60.52 | 33.64 | 47.08 | 11.50 | False | False |
| BD161 | Rossellomorea | 33 | 33 | 31 | 32.66 | 47.57 | 40.12 | 13.75 | False | False |
| BD141 | Brevibacillus brevis | 39 | 39 | 28 | 59.12 | 31.45 | 45.28 | 14.25 | False | False |
| BD147 | Cellulomonas | 13 | 13 | 7 | 71.50 | 63.04 | 67.27 | 16.50 | False | False |
| BD83 | Bacillus | 41 | 41 | 32 | 49.17 | 23.98 | 36.57 | 17.25 | False | False |
| BD140 | Brevibacillus brevis | 39 | 39 | 28 | 59.24 | 44.28 | 51.76 | 18.25 | False | False |
| BD96 | Stutzerimonas frequens | 41 | 41 | 32 | 41.06 | 39.03 | 40.39 | 19.75 | False | False |
| BD126 | Bacillus | 41 | 41 | 39 | 60.26 | 39.05 | 49.66 | 20.25 | True | False |

## Correlacao entre contagem genica e DCPIP

| Classe | DCPIP | n | Pearson r | Spearman r | Interpretacao |
|---|---|---:|---:|---:|---|
| Aliphatic | PL_mean | 51 | -0.025 | -0.057 | Associacao fraca: usar como criterio auxiliar, nao isolado. |
| Aliphatic | PP_mean | 51 | -0.094 | -0.139 | Associacao fraca: usar como criterio auxiliar, nao isolado. |
| Aliphatic | overall_mean | 51 | -0.076 | -0.120 | Associacao fraca: usar como criterio auxiliar, nao isolado. |
| Aromatic | PL_mean | 51 | -0.021 | -0.098 | Associacao fraca: usar como criterio auxiliar, nao isolado. |
| Aromatic | PP_mean | 51 | -0.065 | -0.122 | Associacao fraca: usar como criterio auxiliar, nao isolado. |
| Aromatic | overall_mean | 51 | -0.058 | -0.133 | Associacao fraca: usar como criterio auxiliar, nao isolado. |

## Interpretacao

Os rankings devem ser usados para selecionar controles negativos de forma argumentativa. Isolados no topo do ranking combinado sao mais defensaveis porque unem duas evidencias: baixa capacidade anotacional nas classes alvo e menor desempenho experimental no DCPIP. Isso permite testar a hipotese de que menor repertorio genico para `Aliphatic` ou `Aromatic` se traduz em menor degradacao observada em bancada.

Se a correlacao global for fraca, isso nao invalida o uso de controles negativos. Significa apenas que a relacao gene-DCPIP nao e linear em todo o conjunto, possivelmente por diferencas de expressao, regulacao, crescimento, metabolismo complementar ou por DCPIP medir petroleo como mistura complexa. Nesse caso, a escolha de controles negativos deve priorizar os isolados que sao baixos em genes e tambem baixos em DCPIP, nao apenas um dos dois criterios.

## Arquivos gerados

- `negative_control_candidates_combined.csv`
- `negative_control_candidates_aliphatic.csv`
- `negative_control_candidates_aromatic.csv`
- `negative_control_gene_dcpip_correlations.csv`
- `negative_control_candidates_report.md`
