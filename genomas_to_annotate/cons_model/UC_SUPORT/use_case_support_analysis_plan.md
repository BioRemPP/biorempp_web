# Plano de suporte por casos de uso para os consorcios UC 8.1

## Objetivo

Documentar o plano para avaliar quais casos de uso em `docs/use_cases` podem reforcar a analise e a tomada de decisao dos dois consorcios derivados do UC 8.1:

- consorcio com foco em `Aliphatic`;
- consorcio com foco em `Polyaromatic`;
- ambos interpretados a partir da restricao e reconciliacao do grupo otimizado de `Metal`.

Este documento e apenas um plano operacional. As analises por caso de uso, os scripts reprodutiveis e as execucoes especificas serao criados e rodados somente quando solicitados.

## Escopo

O levantamento deve usar os documentos em `docs/use_cases`, extraindo apenas as secoes relevantes:

- titulo do caso de uso;
- `Scientific Question and Rationale`;
- `Data and Inputs`;
- `Primary inputs`, quando disponivel;
- relacao do caso de uso com suporte a decisao dos consorcios.

Nao e necessario ler ou transcrever integralmente todos os documentos. O foco e identificar quais UCs sao uteis como reforco metodologico e quais evidencias eles podem adicionar.

## Contexto de decisao

O UC 8.1 continua sendo o caso central da modelagem dos consorcios, pois define a logica de cobertura minima por perfis de co-anotacao de compostos.

Os demais casos de uso devem ser avaliados como suporte para responder perguntas complementares:

- os isolados selecionados cobrem bem os compostos de `Aliphatic` e `Polyaromatic`?
- os isolados tem completude KO suficiente para essas classes?
- existe complementaridade funcional entre membros do consorcio?
- existe redundancia excessiva ou redundancia util?
- os candidatos tem suporte por pathways HADEG e KEGG?
- os compostos cobertos tem relevancia toxicologica ou regulatoria?
- a evidencia genomica e coerente com os dados experimentais DCPIP?

## Criterios de classificacao

Cada caso de uso sera classificado em uma destas categorias:

| Categoria | Definicao |
|---|---|
| `Strong support` | Reforca diretamente selecao, cobertura, completude, complementaridade, redundancia, risco toxicologico ou suporte pathway-level dos consorcios. |
| `Complementary support` | Ajuda na interpretacao biologica ou metodologica, mas nao deve decidir sozinho a composicao do consorcio. |
| `Context only` | Util como contexto geral do sistema BioRemPP, mas pouco acionavel para a decisao atual. |
| `Not recommended` | Redundante, muito geral ou desconectado do problema atual. |

## Casos de uso inicialmente priorizados

Estes casos de uso devem ser avaliados primeiro, pois sao os mais provaveis reforcos diretos para a modelagem dos consorcios:

| UC | Papel esperado no suporte a decisao |
|---|---|
| `UC 8.2` | Avaliar completude KO por classe quimica, especialmente `Aliphatic` e `Polyaromatic`. |
| `UC 8.3` | Avaliar completude KO por composto especifico coberto pelos consorcios. |
| `UC 8.4` | Validar completude por pathways HADEG. |
| `UC 8.5` | Validar completude por pathways KEGG. |
| `UC 8.6` | Avaliar complementaridade de KOs por pathway entre membros do consorcio. |
| `UC 8.7` | Medir intersecoes, redundancia e KOs unicos entre candidatos. |
| `UC 2.1` | Comparar riqueza funcional entre BioRemPP, HADEG e KEGG. |
| `UC 2.2` | Avaliar diversidade quimica por amostra. |
| `UC 3.4` | Medir similaridade entre amostras por perfil KO. |
| `UC 3.5` ou `UC 5.2` | Medir similaridade entre amostras por perfil quimico. |
| `UC 4.6` | Avaliar potencial funcional por composto e classe. |
| `UC 4.9` | Descrever perfil de atividade enzimatica por amostra. |
| `UC 4.10` | Identificar diversidade de atividades enzimaticas por amostra. |
| `UC 5.1` | Avaliar interacao amostra x classe quimica. |
| `UC 7.3` | Mapear resposta genetica a compostos de alto risco. |
| `UC 7.6` | Avaliar amplitude de mitigacao de risco por amostra. |
| `UC 7.7` | Avaliar profundidade de mitigacao de risco por amostra. |

## Estrutura esperada do report futuro

Quando solicitado, o report final deve ser gerado em `genomas_to_annotate/cons_model/UC_SUPORT` com pelo menos:

- `use_case_support_report.md`;
- `use_case_support_matrix.csv`;
- scripts reprodutiveis necessarios para extrair, classificar e auditar os UCs.

### `use_case_support_report.md`

O report em Markdown deve conter:

- resumo executivo;
- tabela ranqueada dos UCs recomendados;
- secao para `Strong support`;
- secao para `Complementary support`;
- secao para `Context only` e `Not recommended`, quando util;
- para cada UC recomendado:
  - pergunta cientifica;
  - data inputs;
  - primary inputs;
  - como reforca a escolha dos consorcios;
  - evidencia esperada;
  - limitacao interpretativa.

### `use_case_support_matrix.csv`

A matriz CSV deve conter as seguintes colunas:

| Coluna | Descricao |
|---|---|
| `use_case` | Identificador do caso de uso, por exemplo `UC 8.2`. |
| `module` | Modulo do caso de uso. |
| `title` | Titulo do documento. |
| `scientific_question` | Pergunta cientifica extraida da secao correspondente. |
| `primary_inputs` | Inputs primarios declarados no documento. |
| `data_inputs_summary` | Resumo curto dos dados e colunas exigidas. |
| `support_tier` | Classificacao: `Strong support`, `Complementary support`, `Context only` ou `Not recommended`. |
| `decision_support_role` | Papel do UC na decisao dos consorcios. |
| `relevance_to_aliphatic` | Relevancia para o consorcio `Aliphatic`. |
| `relevance_to_polyaromatic` | Relevancia para o consorcio `Polyaromatic`. |
| `relevance_to_metal_constraint` | Relevancia para a restricao/validacao baseada em `Metal`. |
| `recommended_for_report` | Booleano indicando se deve entrar no report principal. |

## Regras para execucao futura

Quando a analise for solicitada:

1. Nao modificar arquivos originais em `docs/use_cases`.
2. Ler todos os `uc_*.md` em `docs/use_cases/module*/`.
3. Extrair apenas as secoes necessarias.
4. Classificar cada UC conforme os criterios acima.
5. Gerar scripts reprodutiveis dentro de `genomas_to_annotate/cons_model/UC_SUPORT`.
6. Salvar outputs novos sem sobrescrever dados originais.
7. Registrar casos em que um documento nao contenha `Scientific Question and Rationale` ou `Data and Inputs`.

## Validacoes esperadas

- Confirmar o numero total de arquivos `uc_*.md` inspecionados.
- Confirmar que `UC 8.1` foi tratado como referencia central, nao como reforco externo.
- Confirmar que cada UC recomendado tem pergunta cientifica e inputs documentados.
- Confirmar que os UCs priorizados estao associados aos arquivos de resultados existentes quando aplicavel:
  - `BioRemPP_Results (9).csv`;
  - `HADEG_Results (4).csv`;
  - `KEGG_Results (1).csv`;
  - `toxCSM (3).csv`.
- Confirmar que a analise futura continua separada da modelagem ja gerada em `CONSORTIA_MODEL_RESULTS`.

## Premissas

- O report sera escrito em portugues tecnico.
- A finalidade e sustentar a decisao dos consorcios, nao redesenhar o UC 8.1.
- O foco permanece em `Aliphatic`, `Polyaromatic` e na restricao/validacao de `Metal`.
- DCPIP sera usado como evidencia experimental complementar, enquanto os UCs BioRemPP/HADEG/KEGG/toxCSM fornecem evidencia anotacional, funcional, regulatoria e toxicologica.
