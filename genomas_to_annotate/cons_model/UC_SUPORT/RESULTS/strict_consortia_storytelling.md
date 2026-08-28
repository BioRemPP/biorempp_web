# Storytelling tecnico dos consorcios strict metal

## Sintese executiva

A selecao final dos consorcios foi conduzida como uma reducao progressiva do universo de isolados: primeiro, do conjunto experimental e genomico disponivel para o subset anotavel; depois, do subset anotavel para o universo otimizado de `Metal`; por fim, desse universo `Metal` para dois consorcios `strict_metal`, um orientado a `Aliphatic` e outro a `Polyaromatic`.

Nesta narrativa, a recomendacao final considera apenas os consorcios strict:

| Classe alvo | Consorcio strict metal | Cobertura anotacional |
|---|---|---:|
| `Aliphatic` | `BD163`, `BD127`, `E7`, `BD117` | 56/59 compostos, 94.92% |
| `Polyaromatic` | `BD61`, `BD120`, `BD158`, `BD117` | 43/44 compostos, 97.73% |

A versao `relaxed` foi util para demonstrar que ainda seria possivel fechar 100% da cobertura com amostras adicionais, mas ela nao e tratada aqui como recomendacao final. A decisao prioriza a versao strict porque ela preserva a restricao biologica definida pela visualizacao `UC8.1_METAL.png`: somente isolados pertencentes ao universo otimizado de `Metal` entram como candidatos.

## Como as imagens entram como evidencia

As imagens foram usadas como uma camada de validacao visual sobre os arquivos tabulares. Os CSVs sustentam as contagens e metricas, enquanto as figuras ajudam a verificar se a decisao faz sentido biologico: se os candidatos aparecem no universo correto, se ha complementaridade entre perfis, se existe diversidade de genes/enzimas e se a escolha nao depende de um unico isolado dominante.

| Figura/UC | Leitura usada no storytelling | Como reforca a decisao strict |
|---|---|---|
| `UC8.1 Metal` | Define o universo oficial de `17` isolados Metal e as guildas iniciais (`Group 1`, `Group 12`, `Group 4`, `Group 9`). | Justifica que a selecao final parta de Metal antes de escolher representantes para `Aliphatic` e `Polyaromatic`. |
| `UC8.1 Aliphatic` | Mostra `4` guildas e `6` candidatos; `Group 1` tem `E7`, `BD48` e `BD54`. | Explica por que era necessario desempatar candidatos anotacionalmente equivalentes usando DCPIP. |
| `UC8.1 Polyaromatic` | Mostra `4` guildas e `5` candidatos; `Group 4` tem `BD120` e `BD126`. | Sustenta a escolha de `BD120` como representante experimentalmente superior sem perda de papel anotacional. |
| `UC8.2` | Scorecard de completude por classe no universo Metal, com suporte distribuido para `Aliphatic`, `Polyaromatic`, `Metal` e classes relacionadas. | Mostra que os selecionados nao sao apenas positivos no alvo principal; eles preservam amplitude funcional em outras classes quimicas. |
| `UC8.3` | Heatmap de completude KO por composto, com blocos fortes distribuidos entre amostras e compostos. | Reforca que a cobertura depende de complementaridade entre isolados, nao de um unico organismo universal. |
| `UC8.7 Aliphatic` | Intersecoes KO entre `BD163`, `BD127`, `E7` e `BD117`; tamanhos de conjunto aproximados na imagem: `BD127` 233, `BD163` 223, `E7` 221, `BD117` 153. | Confirma um nucleo compartilhado com intersecoes parciais, preservando redundancia funcional e especializacao. |
| `UC8.7 Polyaromatic` | Intersecoes KO entre `BD61`, `BD120`, `BD158` e `BD117`; tamanhos de conjunto aproximados na imagem: `BD61` 229, `BD158` 227, `BD120` 217, `BD117` 153. | Mostra a mesma logica de consorcio: sobreposicao suficiente para robustez, mas com contribuicoes especificas. |
| `UC4.8` | Inventario genico por amostra; `BD127`, `BD163`, `E7`, `BD61`, `BD120` e `BD158` aparecem com repertorios amplos, enquanto `BD117` e mais compacto. | Ajuda a interpretar `BD117` como membro complementar e experimentalmente forte, nao como maximizador de inventario. |
| `UC4.10` | Diversidade de atividades enzimaticas no universo Metal, com faixas recorrentes de atividades como desidrogenases, dioxigenases e oxidoredutases. | Sustenta que os consorcios carregam capacidade enzimatica distribuida, coerente com degradacao/transformacao de compostos. |
| `UC7.7` | Treemap de profundidade de mitigacao de risco por investimento genetico. | Alinha visualmente os candidatos mais fortes com os totais tabulares de profundidade, especialmente `BD163`, `BD127`, `BD120` e `BD61`. |

Assim, a narrativa nao usa as imagens apenas como ilustracao. Elas funcionam como controle de coerencia: o que foi calculado nos arquivos de output tambem aparece como padrao visual de cobertura, completude, diversidade e complementaridade.

## 1. Do universo completo ao conjunto anotavel

O ponto de partida foi um conjunto amplo de isolados com duas camadas de evidencia:

- evidencia experimental de bancada, representada pelos ensaios DCPIP;
- evidencia genomica/anotacional, representada por KOs e resultados BioRemPP, HADEG, KEGG e toxCSM.

A tabela DCPIP continha `53` isolados, mas o conjunto genomico/anotacional consolidado continha `51` isolados com anotacoes compatíveis para a modelagem. Os isolados `BD78` e `BD130` apareceram nos dados experimentais, mas nao tinham anotacao correspondente no subset utilizado. Por isso, eles foram tratados como isolados `DCPIP-only`: relevantes como observacao experimental, mas fora da modelagem anotacional dos consorcios.

Essa decisao evita misturar dois niveis de evidencia de forma indevida. DCPIP mede desempenho experimental agregado sobre petroleo leve e pesado; a modelagem UC 8.1, por outro lado, depende de co-anotacoes amostra-composto-KO. Sem anotacao, um isolado nao pode contribuir para cobertura de compostos ou completude KO no modelo.

## 2. Por que o filtro Metal foi usado antes de Aliphatic e Polyaromatic

A etapa seguinte foi restringir o universo ao resultado otimizado de `Metal`, usando a imagem `UC8.1_METAL.png` como fonte oficial. Essa visualizacao indicou uma cobertura minima de `4` guildas funcionais, `17` amostras e `20` compostos para a classe `Metal`.

O universo oficial de `Metal` foi:

| Guilda Metal | Isolados |
|---|---|
| `Group 1` | `E7`, `BD48`, `BD54`, `BD158` |
| `Group 12` | `BD163` |
| `Group 4` | `BD120`, `BD126`, `BD127`, `BD50`, `BD61`, `BD132`, `BD139`, `BD160`, `BD162`, `BG1`, `BD9` |
| `Group 9` | `BD117` |

Esse filtro foi usado como uma camada de robustez. Em vez de selecionar os melhores isolados apenas para `Aliphatic` ou `Polyaromatic`, a estrategia perguntou: entre os isolados que ja ajudam a cobrir um eixo ambientalmente relevante como `Metal`, quais tambem sustentam uma cobertura forte para hidrocarbonetos alifaticos e poliaromaticos?

Assim, `Metal` nao foi tratado como objetivo final isolado, mas como um filtro de consistencia. A selecao strict privilegia isolados que ja fazem parte de uma solucao minima para metais e que, adicionalmente, carregam perfis anotacionais uteis para petroleo.

## 3. Consorcio strict para Aliphatic

Dentro do universo `Metal`, o UC 8.1 foi aplicado para `Aliphatic`. A imagem correspondente mostra `4` grupos funcionais e `6` amostras candidatas:

| Grupo UC 8.1 Aliphatic | Candidatos na imagem | Representante usado |
|---|---|---|
| `Group 1` | `E7`, `BD48`, `BD54` | `E7` |
| `Group 10` | `BD117` | `BD117` |
| `Group 3` | `BD163` | `BD163` |
| `Group 5` | `BD127` | `BD127` |

O consorcio strict final para `Aliphatic` foi:

```text
BD163 + BD127 + E7 + BD117
```

Essa combinacao cobre `56` dos `59` compostos alifaticos observados no universo anotacional global, chegando a `94.92%` de cobertura. A ordem de entrada no set cover mostra a contribuicao incremental de cada representante:

| Ordem | Isolado | Papel no set cover | Novos compostos cobertos | Cobertura acumulada |
|---:|---|---|---:|---:|
| 1 | `BD163` | nucleo de maior amplitude | 43 | 72.88% |
| 2 | `BD127` | complemento de cobertura | 7 | 84.75% |
| 3 | `E7` | representante do grupo com 3 candidatos | 4 | 91.53% |
| 4 | `BD117` | perfil de nicho e suporte experimental | 2 | 94.92% |

O resultado e biologicamente coerente: `BD163` e `BD127` trazem a maior expansao de cobertura de compostos; `E7` entra como representante de uma guilda redundante do ponto de vista anotacional; e `BD117`, embora cubra menos compostos, adiciona compostos que ainda estavam descobertos e apresenta suporte experimental forte.

## 4. Por que E7 foi escolhido em Aliphatic Group 1

No `Group 1` de `Aliphatic`, havia tres candidatos: `E7`, `BD48` e `BD54`. Eles compartilham o mesmo perfil de grupo na visualizacao UC 8.1, ou seja, do ponto de vista da cobertura de compostos alifaticos eles eram funcionalmente substituiveis dentro daquela guilda.

Nesse caso, o DCPIP foi usado como criterio experimental de desempate. Como `Aliphatic` foi interpretado em associacao ao desempenho em petroleo leve, a metrica principal foi `PL_mean`.

| Candidato | Taxon | `PL_mean` | `PP_mean` | `overall_mean` | Interpretacao |
|---|---|---:|---:|---:|---|
| `E7` | `Acinetobacter` | 82.91 | 56.77 | 69.84 | Melhor desempenho em petroleo leve dentro da guilda. |
| `BD54` | `Acinetobacter` | 82.23 | 69.69 | 75.96 | Muito proximo em petroleo leve e melhor em pesado; bom candidato reserva. |
| `BD48` | `Bacillus safensis` | 49.90 | 33.37 | 41.64 | Menor suporte experimental dentro da guilda. |

A escolha de `E7` e, portanto, defensavel porque ele preserva a mesma contribuicao anotacional do grupo e apresenta o maior desempenho experimental em `PL_mean`. A diferenca para `BD54` e pequena em petroleo leve, entao `BD54` permanece como alternativa tecnica caso a decisao futura passe a priorizar desempenho global ou petroleo pesado. Mas para o storytelling do consorcio alifatico strict, `E7` e o representante mais alinhado ao criterio principal.

## 5. Evidencias complementares para o consorcio Aliphatic

As imagens de UC 8.2 e UC 8.3 reforcam que a selecao nao depende apenas da presenca/ausencia de compostos. No scorecard de completude por classe, os candidatos strict aparecem com suporte distribuido para `Aliphatic`, `Metal` e outras classes. Na visualizacao UC 8.3, a completude por composto mostra um perfil heterogeneo: alguns compostos sao cobertos com maior intensidade por um membro, enquanto outros dependem da combinacao de perfis.

O UC 8.7 reforca a ideia de complementaridade. Para o consorcio alifatico strict, a visualizacao de intersecoes mostrou tamanhos de conjuntos de KOs:

| Isolado | Tamanho do conjunto no UC 8.7 |
|---|---:|
| `BD127` | 233 |
| `BD163` | 223 |
| `E7` | 221 |
| `BD117` | 153 |

As maiores intersecoes aparecem em blocos parciais, nao como uma sobreposicao total. Isso sustenta a interpretacao de que os quatro membros compartilham um nucleo funcional, mas ainda carregam componentes distintos. Em termos de desenho de consorcio, isso e desejavel: ha redundancia suficiente para robustez, mas nao tanta a ponto de tornar os membros intercambiaveis.

O arquivo `UC-4-8_biorempp_ALIPHATIC.csv` adiciona uma camada de inventario genico. A contagem de genes unicos por representante foi:

| Isolado | Genes unicos no UC 4.8 Aliphatic |
|---|---:|
| `BD127` | 232 |
| `BD163` | 222 |
| `E7` | 221 |
| `BD117` | 152 |

Essa distribuicao confirma que `BD127`, `BD163` e `E7` sao membros com inventarios genicos amplos, enquanto `BD117` entra mais como complemento de nicho e como forte suporte experimental.

Os resultados de UC 7.6 e UC 7.7 tambem favorecem o consorcio alifatico strict. Em UC 7.6, que mede amplitude de mitigacao de risco por compostos de alto risco, os totais por candidato foram:

| Isolado | Total UC 7.6 | Organic | Environmental | Genomic | Nuclear Response | Stress Response |
|---|---:|---:|---:|---:|---:|---:|
| `BD163` | 419 | 143 | 137 | 76 | 32 | 31 |
| `BD127` | 403 | 138 | 134 | 74 | 28 | 29 |
| `E7` | 356 | 126 | 120 | 60 | 23 | 27 |
| `BD117` | 289 | 101 | 94 | 46 | 21 | 27 |

Em UC 7.7, que mede profundidade por investimento genetico, os totais foram:

| Isolado | Total UC 7.7 | Exemplos de maiores contribuicoes |
|---|---:|---|
| `BD163` | 3230 | `Ammonia`, `Diuron` |
| `BD127` | 3190 | `Ammonia`, `Chloroform`, `Carbon tetrachloride` |
| `E7` | 2926 | `Ammonia`, `Catechol` |
| `BD117` | 1951 | `Ammonia`, `Diuron` |

Assim, o consorcio alifatico strict combina cobertura quimica, inventario genico, suporte por risco toxicologico e desempenho experimental em DCPIP.

## 6. Consorcio strict para Polyaromatic

Para `Polyaromatic`, o mesmo filtro `Metal` foi mantido. A imagem de UC 8.1 para `Polyaromatic` mostra `4` guildas funcionais e `5` amostras candidatas:

| Grupo UC 8.1 Polyaromatic | Candidatos na imagem | Representante usado |
|---|---|---|
| `Group 10` | `BD117` | `BD117` |
| `Group 2` | `BD158` | `BD158` |
| `Group 4` | `BD120`, `BD126` | `BD120` |
| `Group 7` | `BD61` | `BD61` |

O consorcio strict final para `Polyaromatic` foi:

```text
BD61 + BD120 + BD158 + BD117
```

Essa combinacao cobre `43` dos `44` compostos poliaromaticos observados no universo anotacional global, chegando a `97.73%` de cobertura. A contribuicao incremental foi:

| Ordem | Isolado | Papel no set cover | Novos compostos cobertos | Cobertura acumulada |
|---:|---|---|---:|---:|
| 1 | `BD61` | nucleo de maior amplitude | 29 | 65.91% |
| 2 | `BD120` | representante do grupo com 2 candidatos | 7 | 81.82% |
| 3 | `BD158` | complemento de cobertura | 4 | 90.91% |
| 4 | `BD117` | perfil de nicho e alto DCPIP | 3 | 97.73% |

O consorcio poliaromatico strict tem uma logica parecida com o alifatico, mas com outro centro funcional. `BD61` e o membro de maior ganho inicial; `BD120` resolve a guilda com dois candidatos e traz o maior suporte experimental para petroleo pesado; `BD158` adiciona cobertura complementar; e `BD117` aparece novamente como isolado de alto desempenho experimental e perfil de nicho.

## 7. Por que BD120 foi escolhido em Polyaromatic Group 4

No `Group 4` de `Polyaromatic`, havia dois candidatos: `BD120` e `BD126`. Assim como no grupo alifatico com tres candidatos, esses isolados compartilhavam o mesmo papel anotacional dentro da guilda. A decisao, portanto, foi transferida para a evidencia experimental.

Como `Polyaromatic` foi interpretado em associacao ao petroleo pesado, a metrica principal foi `PP_mean`.

| Candidato | Taxon | `PL_mean` | `PP_mean` | `overall_mean` | Interpretacao |
|---|---|---:|---:|---:|---|
| `BD120` | `Bacillus subtilis` | 83.97 | 81.81 | 82.89 | Melhor desempenho experimental em petroleo pesado e geral. |
| `BD126` | `Bacillus` | 60.26 | 39.05 | 49.66 | Mesmo papel anotacional, mas suporte experimental inferior. |

A escolha de `BD120` e forte porque ele domina `BD126` tanto em `PP_mean` quanto em `PL_mean` e `overall_mean`. Como os dois estavam no mesmo grupo funcional, selecionar `BD120` aumenta a plausibilidade experimental sem sacrificar cobertura anotacional.

## 8. Evidencias complementares para o consorcio Polyaromatic

No scorecard UC 8.2, `BD120` e `BD126` aparecem com completude poliaromatica equivalente na imagem, mas o DCPIP separa claramente os dois. Isso reforca o papel do ensaio experimental como criterio de desempate entre isolados anotacionalmente equivalentes.

O UC 8.3 mostra que a completude por composto poliaromatico nao e uniforme. Isso favorece a composicao em guildas: nenhum membro isolado e tratado como suficiente; a combinacao dos quatro representantes e que sustenta a cobertura quase completa.

No UC 8.7, a intersecao entre os membros poliaromaticos strict mostrou os seguintes tamanhos de conjuntos:

| Isolado | Tamanho do conjunto no UC 8.7 |
|---|---:|
| `BD61` | 229 |
| `BD158` | 227 |
| `BD120` | 217 |
| `BD117` | 153 |

As intersecoes principais foram parciais, novamente sugerindo equilibrio entre redundancia e complementaridade. A presenca de `BD117` com menor tamanho de conjunto, mas alto desempenho DCPIP, ajuda a sustentar o papel de membro complementar, nao apenas de maximizador de riqueza anotacional.

O arquivo `UC-4-8_biorempp_POLYAROMATIC.csv` reforca o inventario genico dos representantes:

| Isolado | Genes unicos no UC 4.8 Polyaromatic |
|---|---:|
| `BD61` | 229 |
| `BD158` | 227 |
| `BD120` | 216 |
| `BD117` | 152 |

Os resultados de UC 7.6 mostram que `BD120` e `BD61` tambem sao fortes em amplitude de mitigacao de risco:

| Isolado | Total UC 7.6 | Organic | Environmental | Genomic | Nuclear Response | Stress Response |
|---|---:|---:|---:|---:|---:|---:|
| `BD120` | 411 | 140 | 134 | 75 | 31 | 31 |
| `BD61` | 370 | 126 | 122 | 63 | 29 | 30 |
| `BD158` | 307 | 106 | 101 | 51 | 23 | 26 |
| `BD117` | 289 | 101 | 94 | 46 | 21 | 27 |

E em UC 7.7, a profundidade de investimento genetico foi:

| Isolado | Total UC 7.7 | Exemplos de maiores contribuicoes |
|---|---:|---|
| `BD120` | 3042 | `Ammonia`, `Diuron` |
| `BD61` | 2739 | `Ammonia`, `Acetaldehyde` |
| `BD158` | 2379 | `Ammonia`, `Formaldehyde` |
| `BD117` | 1951 | `Ammonia`, `Diuron` |

Esses resultados reforcam que o consorcio poliaromatico strict nao foi escolhido apenas por cobertura de compostos, mas tambem por carregar repertorios genicos amplos, intersecoes funcionais parciais e perfis relevantes de mitigacao de risco.

## 9. Papel transversal de BD117

`BD117` aparece nos dois consorcios strict. Isso nao significa redundancia indevida; significa que ele ocupa um papel transversal.

No consorcio alifatico, `BD117` adiciona `2` compostos que ainda estavam descobertos. No consorcio poliaromatico, adiciona `3` compostos. Embora tenha menor inventario genico do que outros membros, ele tem um dos melhores desempenhos experimentais:

| Isolado | `PL_mean` | `PP_mean` | `overall_mean` |
|---|---:|---:|---:|
| `BD117` | 79.18 | 76.65 | 77.92 |

Por isso, `BD117` funciona como ponte entre a logica anotacional e a evidencia de bancada. Ele nao e o membro de maior cobertura, mas e um membro de alta confiabilidade experimental e acrescenta cobertura complementar nos dois cenarios.

## 10. Conclusao interpretativa

A historia completa da selecao e uma sequencia de filtros e validacoes:

1. O universo experimental tinha `53` isolados DCPIP.
2. O universo anotacional efetivo tinha `51` isolados, excluindo `BD78` e `BD130` da modelagem por falta de anotacao.
3. A imagem `UC8.1_METAL.png` definiu um universo strict de `17` isolados ligados a cobertura minima de `Metal`.
4. Dentro desse universo, UC 8.1 foi reaplicado para `Aliphatic` e `Polyaromatic`.
5. Quando uma guilda tinha mais de um candidato, DCPIP foi usado como evidencia experimental para escolher o representante.
6. Os arquivos tabulares dos UCs de suporte quantificaram completude KO, inventario genico, complementaridade e mitigacao de risco.
7. As imagens dos UCs 8.2, 8.3, 8.7, 4.8, 4.10 e 7.7 foram usadas como validacao visual da mesma logica: perfis complementares, repertorios distribuidos e ausencia de dependencia de um unico isolado.

A selecao final strict e:

| Classe | Consorcio final strict | Racional principal |
|---|---|---|
| `Aliphatic` | `BD163`, `BD127`, `E7`, `BD117` | Alta cobertura anotacional, complementaridade por KOs, suporte genico e escolha de `E7` por melhor `PL_mean` dentro do grupo redundante. |
| `Polyaromatic` | `BD61`, `BD120`, `BD158`, `BD117` | Cobertura quase completa, suporte por risco e inventario genico, escolha de `BD120` por superioridade clara em `PP_mean` frente a `BD126`. |

Portanto, os consorcios strict representam uma decisao conservadora: nao buscam apenas maximizar cobertura absoluta, mas preservar um nucleo previamente validado por `Metal`, integrar suporte genômico e funcional, e usar DCPIP como criterio experimental de plausibilidade na escolha dos representantes.

Em conjunto, os CSVs fornecem a base quantitativa, o DCPIP fornece o criterio experimental de plausibilidade e as imagens confirmam visualmente que a escolha strict preserva complementaridade entre KOs, genes, enzimas e perfis de mitigacao de risco.
