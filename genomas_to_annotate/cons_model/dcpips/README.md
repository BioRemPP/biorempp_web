# Documentacao dos dados DCPIP - petroleos por isolado

Este diretorio contem a transcricao da tabela experimental de DCPIP para JSON em duas formas complementares:

- `dcpips_measurements_normalized.json`: formato principal, normalizado, recomendado para analise de dados.
- `dcpips_measurements_by_isolate.json`: formato agrupado por isolado, recomendado para leitura, revisao e conferencia.
- `generate_dcpips_json.py`: script de reproducao usado para gerar os dois documentos JSON a partir da transcricao tabular.

A tabela original informa que os petroleos leve e pesado com sufixo `1` sao do grupo/projeto, enquanto os tratamentos com sufixo `2` correspondem ao petroleo obtido pela Patricia.

## Decisoes de modelagem

- O ensaio foi identificado como `DCPIP`.
- Os valores numericos representam percentual (`%`).
- `PL1`, `PL2`, `PP1` e `PP2` foram modelados como tratamentos experimentais.
- Cada tratamento possui tres replicatas, representadas por `replicate` de `1` a `3` no JSON normalizado.
- Celulas com `-` na tabela foram transcritas como `null`.
- Valores com virgula decimal foram convertidos para numeros JSON com ponto decimal.
- Os nomes taxonomicos foram preservados como aparecem na tabela. Nao foi feita correcao ortografica ou taxonomica durante a transcricao.

## Tratamentos

| Codigo | Tipo de petroleo | Origem | Descricao |
|---|---|---|---|
| `PL1` | leve | nosso | Petroleo leve do grupo/projeto. |
| `PL2` | leve | Patricia | Petroleo leve obtido pela Patricia. |
| `PP1` | pesado | nosso | Petroleo pesado do grupo/projeto. |
| `PP2` | pesado | Patricia | Petroleo pesado obtido pela Patricia. |

## Documento: `dcpips_measurements_normalized.json`

Este e o documento recomendado como fonte principal para analise. Cada linha experimental da tabela foi expandida em registros individuais, um por isolado, tratamento e replicata.

### Campos de nivel raiz

| Campo | Tipo | Descricao |
|---|---|---|
| `schema_version` | string | Versao do schema usado no documento. Atualmente `1.0`. |
| `document_type` | string | Identificador do tipo de documento. Neste arquivo: `dcpip_measurements_normalized`. |
| `experiment` | object | Metadados do experimento e das regras de transcricao. |
| `treatments` | array<object> | Lista controlada dos tratamentos experimentais. |
| `measurements` | array<object> | Registros normalizados de medicao. |

### Campos de `experiment`

| Campo | Tipo | Descricao |
|---|---|---|
| `name` | string | Nome curto do conjunto experimental: `validacao_dcpip_petroleos_isolados`. |
| `assay` | string | Ensaio usado, registrado como `DCPIP`. |
| `metric_name` | string | Nome generico da metrica, registrado como `percentual`. |
| `unit` | string | Unidade dos valores, registrada como `%`. |
| `source_note` | string | Observacao transcrita sobre a origem dos petroleos `1` e `2`. |
| `missing_value_policy` | string | Regra aplicada para valores ausentes. |
| `decimal_policy` | string | Regra aplicada para conversao decimal. |

### Campos de `treatments[]`

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---:|---|
| `code` | string | sim | Codigo do tratamento: `PL1`, `PL2`, `PP1` ou `PP2`. |
| `petroleum_type` | string | sim | Tipo do petroleo: `leve` ou `pesado`. |
| `source_id` | number | sim | Identificador numerico da origem: `1` ou `2`. |
| `source_origin` | string | sim | Origem interpretada: `nosso` ou `patricia`. |
| `description` | string | sim | Descricao textual do tratamento. |

### Campos de `measurements[]`

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---:|---|
| `isolate_code` | string | sim | Codigo do isolado, por exemplo `BD120`, `E7` ou `AP1BH01-1`. |
| `taxon` | string | sim | Identificacao taxonomica transcrita da tabela. |
| `source_label` | string | sim | Rotulo completo original no padrao `codigo - taxon`, usado para auditoria. |
| `treatment` | string | sim | Codigo do tratamento ao qual a medicao pertence. Deve existir em `treatments[].code`. |
| `replicate` | number | sim | Numero da replicata dentro do tratamento: `1`, `2` ou `3`. |
| `value` | number ou null | sim | Valor percentual medido. `null` indica celula ausente na tabela original. |

### Exemplo

```json
{
  "isolate_code": "AP1BH01-1",
  "taxon": "Ochrobactrum",
  "source_label": "AP1BH01-1 - Ochrobactrum",
  "treatment": "PL1",
  "replicate": 1,
  "value": 62.18
}
```

## Documento: `dcpips_measurements_by_isolate.json`

Este documento e uma visao agrupada dos mesmos dados. Ele favorece revisao manual, comparacao visual entre tratamentos e uso por scripts que processam um isolado por vez.

### Campos de nivel raiz

| Campo | Tipo | Descricao |
|---|---|---|
| `schema_version` | string | Versao do schema usado no documento. Atualmente `1.0`. |
| `document_type` | string | Identificador do tipo de documento. Neste arquivo: `dcpip_measurements_by_isolate`. |
| `experiment` | object | Metadados do experimento e das regras de transcricao. |
| `treatments` | array<object> | Lista controlada dos tratamentos experimentais. |
| `isolates` | array<object> | Lista de isolados com os valores agrupados por tratamento. |

### Campos de `isolates[]`

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---:|---|
| `isolate_code` | string | sim | Codigo do isolado. |
| `taxon` | string | sim | Identificacao taxonomica transcrita da tabela. |
| `source_label` | string | sim | Rotulo completo original no padrao `codigo - taxon`. |
| `measurements` | object | sim | Objeto com uma chave por tratamento. |

### Campos de `isolates[].measurements`

| Campo | Tipo | Obrigatorio | Descricao |
|---|---|---:|---|
| `PL1` | array<number|null> | sim | Tres valores percentuais do petroleo leve do grupo/projeto. |
| `PL2` | array<number|null> | sim | Tres valores percentuais do petroleo leve obtido pela Patricia. |
| `PP1` | array<number|null> | sim | Tres valores percentuais do petroleo pesado do grupo/projeto. |
| `PP2` | array<number|null> | sim | Tres valores percentuais do petroleo pesado obtido pela Patricia. |

Cada array deve manter exatamente tres posicoes. A posicao `0` equivale a replicata `1`, a posicao `1` equivale a replicata `2` e a posicao `2` equivale a replicata `3`.

### Exemplo

```json
{
  "isolate_code": "AP1BH01-1",
  "taxon": "Ochrobactrum",
  "source_label": "AP1BH01-1 - Ochrobactrum",
  "measurements": {
    "PL1": [62.18, 75.4, 52.6],
    "PL2": [81.06, 84.6, 88.86],
    "PP1": [76.56, 37.67, 62.3],
    "PP2": [33.11, 48.71, 53.88]
  }
}
```

## Como usar para analise

Para analises estatisticas, medias, desvios, testes de hipotese, graficos por tratamento ou integracao com Python/R, use `dcpips_measurements_normalized.json`.

Para revisao por isolado, comparacao rapida entre `PL1`, `PL2`, `PP1` e `PP2`, ou checagem contra a tabela original, use `dcpips_measurements_by_isolate.json`.

## Validacoes esperadas

- Total de isolados: `53`.
- Total de tratamentos por isolado: `4`.
- Total de replicatas por tratamento: `3`.
- Total de registros normalizados: `636`.
- Valores ausentes devem aparecer como `null`, nunca como `0`.
- O valor `0,133` da tabela foi preservado como `0.133`, com tres casas decimais significativas no valor transcrito.

