# Validacao contra a tabela original

Data da validacao: 2026-08-25

## Resultado

Os arquivos JSON foram conferidos contra a tabela anexada na conversa. Nao foram identificadas divergencias entre os nomes dos isolados, os taxons transcritos e os valores associados aos tratamentos `PL1`, `PL2`, `PP1` e `PP2`.

## Escopo validado

- Total de isolados conferidos: `53`.
- Total de tratamentos por isolado: `4`.
- Total de posicoes por tratamento: `3`.
- Total de valores/posicoes conferidos: `636`.
- Valores numericos com virgula decimal na tabela foram convertidos para ponto decimal no JSON.
- Celulas com `-` na tabela foram conferidas como `null` no JSON.

## Arquivos validados

- `dcpips_measurements_normalized.json`
- `dcpips_measurements_by_isolate.json`

## Conferencias automatizadas internas

As validacoes internas executadas confirmaram:

- `dcpips_measurements_normalized.json` possui `636` registros em `measurements`.
- `dcpips_measurements_by_isolate.json` possui `53` registros em `isolates`.
- Todos os isolados possuem os quatro tratamentos esperados: `PL1`, `PL2`, `PP1`, `PP2`.
- Cada tratamento possui exatamente tres posicoes de replicata.
- A versao agrupada e equivalente a versao normalizada, ou seja, ambas representam os mesmos valores.
- Foram preservados `35` valores ausentes como `null`.

## Observacoes de transcricao

- Os nomes taxonomicos foram preservados como aparecem na tabela, sem correcao ortografica ou taxonomica.
- O campo `source_label` foi reconstruido no padrao `codigo - taxon` para facilitar auditoria; portanto, ele normaliza o separador textual, mas preserva o codigo do isolado e o taxon.
- A observacao de cabecalho da tabela foi registrada em metadados de forma sem acentos por consistencia com os demais arquivos do diretorio.
- O valor `0,133` de `BD158 - Salinicola`, tratamento `PP1`, replicata `1`, foi mantido como `0.133`.

## Conclusao

Com base na conferencia visual da tabela anexada e nas validacoes internas dos JSONs, os dados transcritos estao consistentes com a tabela original quanto a nomes, ordem dos isolados, tratamentos, replicatas, valores numericos e valores ausentes.

