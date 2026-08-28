# Report de suporte por casos de uso

## Resumo executivo

Este report identifica quais casos de uso em `docs/use_cases` podem reforcar a decisao dos consorcios `Aliphatic` e `Polyaromatic` modelados a partir do UC 8.1.

- Casos de uso inspecionados: `56`.
- Casos `Strong support`: `18`.
- Casos `Complementary support`: `31`.
- Casos `Context only`: `6`.
- Casos `Not recommended`: `0`.
- Referencia central: `UC 8.1`.
- DCPIP isolates na modelagem anterior: `53`.
- Amostras anotadas na modelagem anterior: `51`.
- Universo oficial Metal da imagem: `17` amostras.

## Contexto dos consorcios

- `Aliphatic`:
  - `strict_metal`: BD163, BD127, E7, BD117
  - `relaxed`: BD163, BD127, E7, BD117, BD145, BD67, CB13
- `Polyaromatic`:
  - `strict_metal`: BD61, BD120, BD158, BD117
  - `relaxed`: BD61, BD120, BD158, BD117, CB13

## Ranking dos UCs recomendados

| UC | Tier | Titulo | Papel na decisao |
|---|---|---|---|
| UC 8.2 | Strong support | UC-8.2 â€” BioRemPP Chemical Class Completeness Scorecard | Mede completude KO por classe quimica, validando profundidade funcional para Aliphatic e Polyaromatic. |
| UC 8.3 | Strong support | UC-8.3 â€” Compound-Specific KO Completeness Scorecard | Mede completude KO por composto, validando compostos cobertos por cada consorcio. |
| UC 8.4 | Strong support | UC-8.4 â€” HADEG Pathways Completeness Scorecard | Mede completude por pathways HADEG, reforcando suporte de degradacao especializado. |
| UC 8.5 | Strong support | UC-8.5 â€” KEGG Pathways Completeness Scorecard | Mede completude por pathways KEGG, reforcando consistencia metabolica em banco externo. |
| UC 8.6 | Strong support | UC-8.6 â€” Pathway-Centric Consortium Design by KO Coverage | Analisa cobertura e complementaridade de KOs por pathway, diretamente alinhada a desenho de consorcios. |
| UC 8.7 | Strong support | UC-8.7 â€” Sample-Sample KO Intersection Profile | Quantifica intersecoes, KOs compartilhados e KOs unicos entre candidatos, validando redundancia e complementaridade. |
| UC 7.6 | Strong support | UC-7.6 â€” Sample Risk Mitigation Breadth | Avalia amplitude de mitigacao de risco por amostra, diretamente util para validar candidatos contra compostos de alto risco. |
| UC 7.7 | Strong support | UC-7.7 â€” Sample Risk Mitigation Depth | Avalia profundidade de mitigacao de risco por KOs, complementando cobertura com intensidade anotacional. |
| UC 3.4 | Strong support | UC-3.4 â€” Sample Similarity (Based on KO Profiles) | Mede similaridade entre amostras por KOs, diretamente util para evitar consorcios redundantes demais. |
| UC 3.5 | Strong support | UC-3.5 â€” Sample Similarity (Based on Chemical Profiles) | Mede similaridade entre amostras por compostos, diretamente alinhado a perfis de cobertura do UC 8.1. |
| UC 4.6 | Strong support | UC-4.6 â€” Functional Potential by Chemical Compound | Avalia potencial funcional por composto e classe, conectando diretamente candidatos aos compostos de Aliphatic/Polyaromatic. |
| UC 4.9 | Strong support | UC-4.9 â€” Profiling of Sample Enzymatic Activity | Perfil de atividades enzimaticas por amostra; reforca plausibilidade funcional dos membros escolhidos. |
| UC 4.10 | Strong support | UC-4.10 â€” Diversity of Enzymatic Activities Across Samples | Diversity de atividades enzimaticas por amostra, apoiando escolha de representantes com maior variedade funcional. |
| UC 5.1 | Strong support | UC-5.1 â€” Sample-Compound Class Interaction | Matriz amostra x classe quimica, diretamente util para mostrar associacao dos candidatos com Aliphatic, Polyaromatic e Metal. |
| UC 5.2 | Strong support | UC-5.2 â€” Sample Similarity (Based on Chemical Profiles) | Similaridade por perfil quimico, alternativa/confirmacao ao UC 3.5 para avaliar redundancia quimica. |
| UC 7.3 | Strong support | UC-7.3 â€” Mapping of Genetic Response to High-Priority Threats | Mapeia resposta genetica a compostos de alto risco, priorizando candidatos com KOs ligados a ameaças toxicologicas. |
| UC 2.1 | Strong support | UC-2.1 â€” Ranking of Sample Functional Richness Across Databases | Compara riqueza funcional dos candidatos entre BioRemPP, HADEG e KEGG; bom reforco para escolher representantes com suporte multi-banco. |
| UC 2.2 | Strong support | UC-2.2 â€” Ranking of Samples by Chemical Diversity | Ranqueia amostras por diversidade quimica, reforcando se candidatos cobrem amplo espectro de compostos. |
| UC 6.5 | Complementary support | UC-6.5 â€” Chemicalâ€“Enzymatic Hierarchy | Hierarquia quimico-enzimatica por classe, atividade e genes; bom suporte mecanistico agregado. |
| UC 6.2 | Complementary support | UC-6.2 â€” Biological Interaction Flow | Fluxo amostra -> classe -> atividade enzimatica, alinhado ao racional funcional dos consorcios. |
| UC 4.13 | Complementary support | UC-4.13 â€” Genetic Profile by Compound Class | Perfil genetico por classe de degradacao HADEG, especialmente util para Alkanes/Aromatics. |
| UC 3.3 | Complementary support | UC-3.3 â€” Hierarchical Clustering of Samples by Functional Profile | Clustering hierarquico por perfil KO, reforcando analise de redundancia ou distancia funcional entre membros. |
| UC 3.2 | Complementary support | UC-3.2 â€” Principal Component Analysis of Samples by Chemical Profile | PCA por perfil quimico, util para avaliar separacao dos candidatos conforme compostos co-anotados. |
| UC 3.1 | Complementary support | UC-3.1 â€” Principal Component Analysis of Samples by Functional Profile | PCA por perfil funcional, util para ver se candidatos selecionados ocupam espacos funcionais distintos. |
| UC 2.3 | Complementary support | UC-2.3 â€” Ranking of Compound Richness by Sample per Chemical Class | Identifica compostos mais compartilhados por classe, ajudando a separar compostos comuns de compostos que exigem membros especificos. |
| UC 2.4 | Complementary support | UC-2.4 â€” Ranking of Compounds Richness by Gene Count per Chemical Classes | Ranqueia compostos por diversidade de genes, apoiando a priorizacao de compostos com maior complexidade funcional. |
| UC 1.5 | Complementary support | UC-1.5 â€” Regulatory Reference Compliance Scorecard | Avalia sobreposicao entre repertorio de compostos das amostras e agencias regulatorias, adicionando relevancia regulatoria a escolha. |
| UC 1.6 | Complementary support | UC-1.6 â€” Functional Potential of Samples Across Regulatory References | Mede amplitude de KOs por amostra e agencia regulatoria, conectando potencial funcional a escopos regulatorios. |
| UC 2.5 | Complementary support | UC-2.5 â€” Descriptive Statistics of Samples Across Databases | Fornece estatisticas descritivas de KOs por banco, util para auditar se os candidatos estao acima ou abaixo da distribuicao geral. |
| UC 1.4 | Complementary support | UC-1.4 â€” Proportional Contribution of Samples Unique KO Pool | Quantifica a contribuicao relativa de cada amostra ao pool total de KOs, apoiando a distincao entre isolados generalistas e especialistas. |
| UC 1.1 | Complementary support | UC-1.1 â€” Intersections across BioRemPP, HADEG, and KEGG | Compara concordancia e contribuicoes unicas entre BioRemPP, HADEG e KEGG, ajudando a qualificar a confiabilidade multi-banco das evidencias usadas nos consorcios. |
| UC 4.1 | Complementary support | UC-4.1 â€” Functional Profiling of Samples by Metabolic Pathway | Perfila KOs por pathways KEGG para cada amostra, ajudando a interpretar profundidade funcional dos candidatos. |
| UC 4.2 | Complementary support | UC-4.2 â€” Ranking of Samples by Pathway Richness | Ranqueia amostras por riqueza em pathway KEGG especifico, util quando um pathway alvo for priorizado. |
| UC 4.3 | Complementary support | UC-4.3 â€” Functional Fingerprint of Pathway by Samples | Mostra footprint funcional de um pathway entre amostras, apoiando comparacoes pathway-level. |
| UC 4.4 | Complementary support | UC-4.4 - Functional Fingerprint of Samples by Pathway | Mostra fingerprint de pathways por amostra, util para explicar a especializacao de membros selecionados. |
| UC 4.5 | Complementary support | UC-4.5 â€” Gene Presence Map by Metabolic Pathway | Mapa de presenca de genes por pathway KEGG, util para validar genes especificos em candidatos. |
| UC 4.7 | Complementary support | UC-4.7 â€” Geneâ€“Compound Association Explorer | Explora associacoes gene-composto e quais amostras carregam essas co-anotacoes. |
| UC 4.8 | Complementary support | UC-4.8 â€” Gene Inventory Explorer | Inventario de genes por amostra, util para investigacao manual de genes de interesse nos candidatos. |
| UC 4.11 | Complementary support | UC-4.11 â€” Hierarchical View of Genetic Diversity in HADEG Pathways | Hierarquia da diversidade genetica em HADEG, util para contextualizar quais classes/pathways sao mais diversos. |
| UC 3.6 | Complementary support | UC-3.6 â€” Gene Co-occurrence Across Samples | Estrutura, similaridade e co-ocorrencia. |
| UC 3.7 | Complementary support | UC-3.7 â€” Compound Co-occurrence Across Samples | Estrutura, similaridade e co-ocorrencia. |
| UC 4.12 | Complementary support | UC-4.12 â€” Pathway Funcional Map by Sample | Distribuicao de pathways HADEG por amostra, util para detalhar membros selecionados individualmente. |
| UC 5.3 | Complementary support | UC-5.3 â€” Regulatory Relevance of Samples | Relevancia regulatoria por amostra, adicionando contexto de prioridade ambiental aos candidatos. |
| UC 5.4 | Complementary support | UC-5.4 â€” Geneâ€“Compound Interaction Network | Rede gene-composto para identificar hubs funcionais associados aos compostos cobertos. |
| UC 6.1 | Complementary support | UC-6.1 â€” Regulatory-to-Molecular Interaction Flow | Fluxo agencia -> amostra -> gene -> composto, conectando candidatos a contexto regulatorio e molecular. |
| UC 6.3 | Complementary support | UC-6.3 â€” Chemical Hierarchy | Hierarquia quimica por classe, composto, amostra e gene; boa sintese para explicar contribuicoes por classe. |
| UC 6.4 | Complementary support | UC-6.4 â€” Enzymatic Hierarchy | Hierarquia enzimatica por atividade, classe e genes; reforca quais funcoes sustentam a cobertura. |
| UC 7.1 | Complementary support | UC-7.1 â€” Predicted Compound Toxicity Profiles | Perfil toxicologico dos compostos, util para explicar prioridade dos compostos cobertos. |
| UC 7.2 | Complementary support | UC-7.2 â€” Concordance Between Predicted Risk and Regulatory Scope | Concordancia entre risco predito e escopo regulatorio, adicionando peso ambiental aos alvos. |

## Referencia central

### UC 8.1 - UC-8.1 â€” Minimal Sample Grouping for Complete Compound Coverage

- **Tier:** `Central reference`
- **Pergunta cientifica:** What is the minimum number of distinct compound co-annotation profiles (i.e., groups of samples with identical compound co-annotation sets) required to collectively cover all observed compound co-annotations within a given chemical class?
- **Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sampleâ€“compound associations)
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `compoundclass` â€“ chemical class to which a compound belongs - `compoundname` â€“ name of the chemical compound interacted with by the sample - **Core concept: Annotation Groups** An **annotation group** is defined as a group of samples that share the **exact same set of compound co-annotations** within a selected chemical class. Samples within the same group have identical annotation profiles with respect to that class.
- **Como reforca a decisao:** Caso central ja usado para modelar cobertura minima e guildas funcionais dos consorcios.
- **Relevancia para Aliphatic:** Referencia central.
- **Relevancia para Polyaromatic:** Referencia central.
- **Relevancia para Metal:** Referencia central para restricao pela imagem UC8.1_METAL.png.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

## Strong support

### UC 8.2 - UC-8.2 â€” BioRemPP Chemical Class Completeness Scorecard

- **Tier:** `Strong support`
- **Pergunta cientifica:** Which samples have the most "complete" KO annotation coverage for a given chemical class, and how can this be used to identify samples with high annotation completeness?
- **Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sampleâ€“KOâ€“compound class associations)
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `ko` â€“ KEGG Orthology (KO) identifier - `compoundclass` â€“ chemical class associated with the KOâ€“sample interaction - **Scorecard structure:** - **Rows:** Samples - **Columns:** Compound Classes - **Cell value:** Completeness Score (%) for a given `(sample, compoundclass)` pair
- **Como reforca a decisao:** Mede completude KO por classe quimica, validando profundidade funcional para Aliphatic e Polyaromatic.
- **Relevancia para Aliphatic:** Alta: mede completude da classe.
- **Relevancia para Polyaromatic:** Alta: mede completude da classe.
- **Relevancia para Metal:** Alta: pode confirmar completude dos membros Metal.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 8.3 - UC-8.3 â€” Compound-Specific KO Completeness Scorecard

- **Tier:** `Strong support`
- **Pergunta cientifica:** For any given chemical compound, which sample has the most "complete" KO annotation coverage?
- **Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sampleâ€“KOâ€“compound associations)
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `ko` â€“ KEGG Orthology (KO) identifier - `compoundname` â€“ chemical compound associated with the KOâ€“sample interaction - **Scorecard structure:** - **Rows:** Samples - **Columns:** Individual Compound Names - **Cell value:** KO Completeness Score (%) for each `(sample, compoundname)` pair
- **Como reforca a decisao:** Mede completude KO por composto, validando compostos cobertos por cada consorcio.
- **Relevancia para Aliphatic:** Alta: identifica lacunas por composto alifatico.
- **Relevancia para Polyaromatic:** Alta: identifica lacunas por composto poliaromatico.
- **Relevancia para Metal:** Media a alta: aplica-se aos compostos Metal da restricao.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 8.4 - UC-8.4 â€” HADEG Pathways Completeness Scorecard

- **Tier:** `Strong support`
- **Pergunta cientifica:** Which samples have the most "complete" KO annotation coverage for a given HADEG degradation pathway, and how can this be used to compare pathway-level annotation completeness across samples?
- **Primary inputs:** `HADEG_Results.xlsx or HADEG_Results.csv` (sampleâ€“KOâ€“pathway associations)
- **Data inputs:** - **Primary data source:** `HADEG_Results.xlsx or HADEG_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `ko` â€“ KEGG Orthology (KO) identifier annotated for that sample - `compound_pathway` â€“ HADEG pathway label associated with the KO - **Scorecard structure:** - **Rows:** Samples - **Columns:** HADEG degradation pathways (`compound_pathway`) - **Cell value:** Pathway Completeness Score (%) for each `(sample, pathway)` pair
- **Como reforca a decisao:** Mede completude por pathways HADEG, reforcando suporte de degradacao especializado.
- **Relevancia para Aliphatic:** Alta quando mapeado para Alkanes.
- **Relevancia para Polyaromatic:** Alta quando mapeado para Aromatics.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 8.5 - UC-8.5 â€” KEGG Pathways Completeness Scorecard

- **Tier:** `Strong support`
- **Pergunta cientifica:** Which samples have the most "complete" KO annotation coverage for a given KEGG metabolic pathway, and how can this be used to compare KO annotation completeness across samples?
- **Primary inputs:** `KEGG_Results.xlsx or KEGG_Results.csv` (sampleâ€“KOâ€“KEGG pathway associations)
- **Data inputs:** - **Primary data source:** `KEGG_Results.xlsx or KEGG_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `ko` â€“ KEGG Orthology (KO) identifier - `pathname` â€“ KEGG pathway name or identifier associated with the KO - **Scorecard structure:** - **Rows:** Samples - **Columns:** KEGG Pathways (`pathname`) - **Cell value:** Pathway Completeness Score (%) for each `(sample, pathname)` pair
- **Como reforca a decisao:** Mede completude por pathways KEGG, reforcando consistencia metabolica em banco externo.
- **Relevancia para Aliphatic:** Alta.
- **Relevancia para Polyaromatic:** Alta.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 8.6 - UC-8.6 â€” Pathway-Centric Consortium Design by KO Coverage

- **Tier:** `Strong support`
- **Pergunta cientifica:** For a specific metabolic pathway, how are its annotated KO identifiers distributed across different samples, and what does their overlap reveal about annotation redundancy and complementarity?
- **Primary inputs:** `HADEG_Results.xlsx or HADEG_Results.csv` (sampleâ€“KOâ€“pathway associations)
- **Data inputs:** - **Primary data source:** `HADEG_Results.xlsx or HADEG_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `ko` â€“ KEGG Orthology (KO) identifier annotated for that sample - `compound_pathway` â€“ HADEG pathway label associated with the KO - **Set-based elements:** - **Sets:** Individual `sample`s (each represented by the KOs it contributes to the selected pathway). - **Elements:** Unique **KOs required for that pathway** within the dataset.
- **Como reforca a decisao:** Analisa cobertura e complementaridade de KOs por pathway, diretamente alinhada a desenho de consorcios.
- **Relevancia para Aliphatic:** Alta: valida complementaridade para pathways de hidrocarbonetos.
- **Relevancia para Polyaromatic:** Alta: valida complementaridade para pathways aromaticos.
- **Relevancia para Metal:** Media a alta.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 8.7 - UC-8.7 â€” Sample-Sample KO Intersection Profile

- **Tier:** `Strong support`
- **Pergunta cientifica:** How many KO identifiers are shared across the selected samples, and which samples carry unique or rare KO annotations?
- **Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sampleâ€“KO associations)
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `ko` â€“ KEGG Orthology (KO) identifier associated with that sample - **Set definition:** - **Sets:** Individual `sample`s (each represented by its KO repertoire) - **Elements:** Unique **KO identifiers** (`ko`) observed in the selected subset of samples - **User control:** - A **multi-select dropdown** allowing selection of **two or more samples** to include in the intersection analysis.
- **Como reforca a decisao:** Quantifica intersecoes, KOs compartilhados e KOs unicos entre candidatos, validando redundancia e complementaridade.
- **Relevancia para Aliphatic:** Alta.
- **Relevancia para Polyaromatic:** Alta.
- **Relevancia para Metal:** Alta.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 7.6 - UC-7.6 â€” Sample Risk Mitigation Breadth

- **Tier:** `Strong support`
- **Pergunta cientifica:** Which samples have the broadest compound co-annotation coverage, as measured by the variety of distinct high-risk compounds they are co-annotated with within each toxicological category?
- **Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sampleâ€“compound interactions) and `ToxCSM.xlsx or ToxCSM.csv` (predicted toxicity and categories)
- **Data inputs:** - **Primary data sources:** - `BioRemPP_Results.xlsx or BioRemPP_Results.csv` â€“ KO annotation data linking samples and compounds - `ToxCSM.xlsx or ToxCSM.csv` â€“ predicted toxicity scores and qualitative labels for compounds - **Key columns:** - From `ToxCSM.xlsx or ToxCSM.csv`: - `compoundname` â€“ chemical compound name - `endpoint` / `label_*` â€“ endpoint-specific toxicity labels (e.g., "High Toxicity", "High Safety") - `supercategory` (derived) â€“ mapped toxicological category (e.g., Genomic, Environmental, Organic) - From `BioRemPP_Results.xlsx or BioRemPP_Results.csv`: - `sample` â€“ identifier for each biological sample - `compoundname` â€“ compound associated with the sample - **Hierarchy represented in the treemap:** - Level 1: **Sample** - Level 2: **Toxicity Category** (toxicological super-category) The quantitative value displayed is the **count of distinct high-risk com
- **Como reforca a decisao:** Avalia amplitude de mitigacao de risco por amostra, diretamente util para validar candidatos contra compostos de alto risco.
- **Relevancia para Aliphatic:** Media a alta.
- **Relevancia para Polyaromatic:** Alta.
- **Relevancia para Metal:** Alta.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 7.7 - UC-7.7 â€” Sample Risk Mitigation Depth

- **Tier:** `Strong support`
- **Pergunta cientifica:** Which samples have the highest number of KO annotation co-occurrences linked to different categories of predicted toxicological risk?
- **Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sampleâ€“compoundâ€“gene interactions) and `ToxCSM.xlsx or ToxCSM.csv` (predicted toxicity and categories)
- **Data inputs:** - **Primary data sources:** - `BioRemPP_Results.xlsx or BioRemPP_Results.csv` â€“ KO annotation data linking samples, compounds, and genes - `ToxCSM.xlsx or ToxCSM.csv` â€“ predicted toxicity scores and qualitative labels for compounds - **Key columns:** - From `BioRemPP_Results.xlsx or BioRemPP_Results.csv`: - `sample` â€“ identifier for each biological sample - `compoundname` â€“ name of the chemical compound - `genesymbol` â€“ gene symbol or identifier associated with the interaction - From `ToxCSM.xlsx or ToxCSM.csv`: - `compoundname` â€“ chemical compound name (to be matched with BioRemPP) - `endpoint` / `label_*` â€“ endpoint-specific toxicity labels (e.g., "High Toxicity", "High Safety") - `supercategory` (derived) â€“ mapped toxicological super-category (e.g., Genomic, Environmental, Organic) - **Hierarchy represented in the treemap:** - Level 1: **Sample** - Level 2: **Toxicity
- **Como reforca a decisao:** Avalia profundidade de mitigacao de risco por KOs, complementando cobertura com intensidade anotacional.
- **Relevancia para Aliphatic:** Media a alta.
- **Relevancia para Polyaromatic:** Alta.
- **Relevancia para Metal:** Alta.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 3.4 - UC-3.4 â€” Sample Similarity (Based on KO Profiles)

- **Tier:** `Strong support`
- **Pergunta cientifica:** How similar are the samples to one another in terms of their shared KEGG Orthology (KO) annotation profiles?
- **Primary inputs:** BioRemPP results table with `sample` and `ko` columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `sample` â€“ identifier for each biological sample - `ko` â€“ KEGG Orthology identifier associated with the sample - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Derived structure:** binary presence/absence matrix with: - rows = samples - columns = unique KOs - cell = `1` if the sample possesses that KO, `0` otherwise
- **Como reforca a decisao:** Mede similaridade entre amostras por KOs, diretamente util para evitar consorcios redundantes demais.
- **Relevancia para Aliphatic:** Alta: valida complementaridade funcional dos membros.
- **Relevancia para Polyaromatic:** Alta: valida complementaridade funcional dos membros.
- **Relevancia para Metal:** Alta: compara membros do universo Metal oficial.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 3.5 - UC-3.5 â€” Sample Similarity (Based on Chemical Profiles)

- **Tier:** `Strong support`
- **Pergunta cientifica:** How similar are the samples to one another, based on the shared repertoire of chemical compounds they are co-annotated with?
- **Primary inputs:** BioRemPP results table with `sample` and `compoundname` columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `sample` â€“ identifier for each biological sample - `compoundname` â€“ name (or identifier) of the chemical compound associated with the sample - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Derived structure:** binary presence/absence matrix with: - rows = samples - columns = unique compound names - cell = `1` if the sample is associated with that compound, `0` otherwise
- **Como reforca a decisao:** Mede similaridade entre amostras por compostos, diretamente alinhado a perfis de cobertura do UC 8.1.
- **Relevancia para Aliphatic:** Alta: valida se membros alifaticos cobrem perfis quimicos distintos.
- **Relevancia para Polyaromatic:** Alta: valida se membros poliaromaticos cobrem perfis quimicos distintos.
- **Relevancia para Metal:** Media: compara diversidade quimica dentro/fora do universo Metal.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 4.6 - UC-4.6 â€” Functional Potential by Chemical Compound

- **Tier:** `Strong support`
- **Pergunta cientifica:** For a given class of chemical compounds, which samples have the highest KO annotation diversity co-annotated with specific compounds?
- **Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sampleâ€“compoundâ€“KO associations, with chemical class)
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `compoundclass` â€“ chemical class for each compound - `compoundname` â€“ individual compound names - `ko` â€“ KEGG Orthology identifier(s) associated with each sampleâ€“compound interaction - **User control:** - A **dropdown menu** to select the **Compound Class** (`compoundclass`) to be analyzed. - **Output structure:** - **X-axis:** samples - **Y-axis:** compounds (within the selected class) - **Point size/color:** unique KO count for each `(sample, compound)` pair (functional potential)
- **Como reforca a decisao:** Avalia potencial funcional por composto e classe, conectando diretamente candidatos aos compostos de Aliphatic/Polyaromatic.
- **Relevancia para Aliphatic:** Alta: evidencia KO por composto alifatico.
- **Relevancia para Polyaromatic:** Alta: evidencia KO por composto poliaromatico.
- **Relevancia para Metal:** Media: pode comparar compostos Metal como restricao secundaria.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 4.9 - UC-4.9 â€” Profiling of Sample Enzymatic Activity

- **Tier:** `Strong support`
- **Pergunta cientifica:** For any given sample, which enzymatic functions are most broadly represented, as measured by the diversity of unique gene annotations associated with them?
- **Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sampleâ€“enzymeâ€“gene associations)
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `enzyme_activity` â€“ functional label for enzymatic activity (e.g., *oxidoreductase*, *transferase*) - `genesymbol` â€“ gene symbols mapped to that enzymatic activity in a given sample - **User control:** - **Dropdown â€“ Sample:** all unique `sample` identifiers available in the dataset. - **Output structure:** - **X-axis:** enzymatic activities (`enzyme_activity`) - **Y-axis:** number of distinct `genesymbol` values per activity for the selected sample - **Bars:** one bar per enzymatic activity, ranked by gene diversity
- **Como reforca a decisao:** Perfil de atividades enzimaticas por amostra; reforca plausibilidade funcional dos membros escolhidos.
- **Relevancia para Aliphatic:** Alta: verifica atividades enzimas associadas a hidrocarbonetos alifaticos.
- **Relevancia para Polyaromatic:** Alta: verifica atividades enzimas associadas a compostos aromaticos/poliaromaticos.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 4.10 - UC-4.10 â€” Diversity of Enzymatic Activities Across Samples

- **Tier:** `Strong support`
- **Pergunta cientifica:** Which enzymatic functions in which samples have the greatest diversity of unique gene annotations?
- **Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sampleâ€“enzymeâ€“gene associations)
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `enzyme_activity` â€“ enzymatic function label (e.g., *oxidoreductase*, *hydrolase*) - `genesymbol` â€“ gene symbols assigned to that enzymatic activity in each sample - **Pre-processing rules:** - Remove rows with invalid or placeholder `enzyme_activity` labels (e.g., `#N/D`) - Remove rows with missing `sample`, `enzyme_activity`, or `genesymbol` - **Output structure:** - **X-axis:** enzymatic activities - **Y-axis:** samples - **Bubbles:** one bubble per `(sample, enzyme_activity)` pair, sized and colored by gene diversity
- **Como reforca a decisao:** Diversity de atividades enzimaticas por amostra, apoiando escolha de representantes com maior variedade funcional.
- **Relevancia para Aliphatic:** Alta.
- **Relevancia para Polyaromatic:** Alta.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 5.1 - UC-5.1 â€” Sample-Compound Class Interaction

- **Tier:** `Strong support`
- **Pergunta cientifica:** Which samples are most co-annotated with which chemical classes, and what might this reveal about their annotation coverage patterns?
- **Primary inputs:** BioRemPP results table with `sample` and `compoundclass` columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `sample` â€“ identifier for each biological sample - `compoundclass` â€“ categorical label for the chemical class of each compound - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Derived structure:** interaction matrix with: - rows = samples - columns = compound classes - cell = interaction count for each sampleâ€“class pair
- **Como reforca a decisao:** Matriz amostra x classe quimica, diretamente util para mostrar associacao dos candidatos com Aliphatic, Polyaromatic e Metal.
- **Relevancia para Aliphatic:** Alta.
- **Relevancia para Polyaromatic:** Alta.
- **Relevancia para Metal:** Alta.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 5.2 - UC-5.2 â€” Sample Similarity (Based on Chemical Profiles)

- **Tier:** `Strong support`
- **Pergunta cientifica:** How similar are the samples to one another in their compound co-annotation profiles, and what is the structure of these annotation-based sample groups?
- **Primary inputs:** BioRemPP results table with `sample` and `compoundname` columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `sample` â€“ identifier for each biological sample - `compoundname` â€“ name (or identifier) of the chemical compound associated with that sample - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Derived structures:** - a mapping from each sample to its set of unique compounds - a pairwise similarity table where each entry is the count of shared compounds between two samples
- **Como reforca a decisao:** Similaridade por perfil quimico, alternativa/confirmacao ao UC 3.5 para avaliar redundancia quimica.
- **Relevancia para Aliphatic:** Alta.
- **Relevancia para Polyaromatic:** Alta.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 7.3 - UC-7.3 â€” Mapping of Genetic Response to High-Priority Threats

- **Tier:** `Strong support`
- **Pergunta cientifica:** For a given high-level toxicological category (e.g., Genomic Toxicity), which samples have the most diverse KO annotations co-annotated with the associated high-priority compounds?
- **Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sampleâ€“compoundâ€“gene associations) and `ToxCSM.xlsx or ToxCSM.csv` (predicted toxicity per compound and endpoint)
- **Data inputs:** - **Primary data sources:** - `BioRemPP_Results.xlsx or BioRemPP_Results.csv` â€“ KO annotations linking samples, compounds, and genes - `ToxCSM.xlsx or ToxCSM.csv` â€“ predicted toxicity scores and labels for compounds across multiple endpoints - **Key columns:** - From `ToxCSM.xlsx or ToxCSM.csv`: - `compoundname` â€“ name of the chemical compound - `endpoint` / `label_*` â€“ toxicity endpoints and their qualitative labels (e.g., "High Toxicity") - `supercategory` (derived) â€“ toxicological super-category (e.g., Genomic, Environmental, Organic) - From `BioRemPP_Results.xlsx or BioRemPP_Results.csv`: - `sample` â€“ identifier for each biological sample - `compoundname` â€“ compound associated with the interaction - `genesymbol` â€“ gene symbol or identifier - **Entities of interest:** - **High-Risk Compounds** within a chosen toxicological super-category - **Samples** and their associa
- **Como reforca a decisao:** Mapeia resposta genetica a compostos de alto risco, priorizando candidatos com KOs ligados a ameaças toxicologicas.
- **Relevancia para Aliphatic:** Media a alta.
- **Relevancia para Polyaromatic:** Alta.
- **Relevancia para Metal:** Alta.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 2.1 - UC-2.1 â€” Ranking of Sample Functional Richness Across Databases

- **Tier:** `Strong support`
- **Pergunta cientifica:** How does the ranking of functional richness for each sample change when viewed through the lens of different annotation databases (BioRemPP, HADEG, KEGG)?
- **Primary inputs:** BioRemPP, HADEG, and KEGG results tables with sample-level KO annotations
- **Data inputs:** - **Primary data sources:** - BioRemPP results table - HADEG results table - KEGG results table - **Key columns (per selected database):** - `sample` â€“ identifier for each biological sample - `ko` or `Gene` â€“ KEGG Orthology identifier (or equivalent column used to store KO IDs) - **Accepted format:** semicolon-delimited text tables (`.txt` or `.csv`) - **Entity of interest:** unique KO identifiers counted per sample for the selected database
- **Como reforca a decisao:** Compara riqueza funcional dos candidatos entre BioRemPP, HADEG e KEGG; bom reforco para escolher representantes com suporte multi-banco.
- **Relevancia para Aliphatic:** Alta: qualifica candidatos do consorcio alifatico por riqueza funcional.
- **Relevancia para Polyaromatic:** Alta: qualifica candidatos do consorcio poliaromatico por riqueza funcional.
- **Relevancia para Metal:** Media: testa se candidatos da imagem Metal sao funcionalmente ricos em bancos distintos.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 2.2 - UC-2.2 â€” Ranking of Samples by Chemical Diversity

- **Tier:** `Strong support`
- **Pergunta cientifica:** Which biological samples are co-annotated with the widest variety of unique chemical compounds?
- **Primary inputs:** BioRemPP results table with `sample` and `compoundname` columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `sample` â€“ identifier for each biological sample - `compoundname` â€“ name of the chemical compound associated with that sample - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Entity of interest:** unique compound names associated with each sample
- **Como reforca a decisao:** Ranqueia amostras por diversidade quimica, reforcando se candidatos cobrem amplo espectro de compostos.
- **Relevancia para Aliphatic:** Alta: contextualiza cobertura ampla para compostos alifaticos.
- **Relevancia para Polyaromatic:** Alta: contextualiza cobertura ampla para compostos poliaromaticos.
- **Relevancia para Metal:** Media: avalia se universo Metal contem candidatos quimicamente diversos.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

## Complementary support

### UC 6.5 - UC-6.5 â€” Chemicalâ€“Enzymatic Hierarchy

- **Tier:** `Complementary support`
- **Pergunta cientifica:** For each class of chemical compounds, which enzymatic functions are most frequently co-annotated, and which specific genes show the broadest compound co-annotation coverage within that class?
- **Primary inputs:** BioRemPP results table with `compoundclass`, `enzyme_activity`, `genesymbol`, and `compoundname`
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `compoundclass` â€“ high-level chemical class or category - `enzyme_activity` â€“ functional label for the enzymatic activity - `genesymbol` â€“ gene symbol or identifier associated with that activity - `compoundname` â€“ specific compound name or identifier - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Hierarchical structure:** 1. **Compound Class** (`compoundclass`) 2. **Enzyme Activity** (`enzyme_activity`) 3. **Gene Symbol** (`genesymbol`)
- **Como reforca a decisao:** Hierarquia quimico-enzimatica por classe, atividade e genes; bom suporte mecanistico agregado.
- **Relevancia para Aliphatic:** Alta.
- **Relevancia para Polyaromatic:** Alta.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 6.2 - UC-6.2 â€” Biological Interaction Flow

- **Tier:** `Complementary support`
- **Pergunta cientifica:** How are sample co-annotations distributed across different chemical classes, and which enzymatic activities are most frequently co-annotated with each?
- **Primary inputs:** BioRemPP results table with `sample`, `compoundclass`, and `enzyme_activity`
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `sample` â€“ identifier for each biological sample - `compoundclass` â€“ chemical class/category of the compound - `enzyme_activity` â€“ functional label for the enzymatic activity (e.g., monooxygenase, dehydrogenase) - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Conceptual flow (stages):** 1. **Sample** (`sample`) 2. **Compound Class** (`compoundclass`) 3. **Enzyme Activity** (`enzyme_activity`)
- **Como reforca a decisao:** Fluxo amostra -> classe -> atividade enzimatica, alinhado ao racional funcional dos consorcios.
- **Relevancia para Aliphatic:** Alta.
- **Relevancia para Polyaromatic:** Alta.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 4.13 - UC-4.13 â€” Genetic Profile by Compound Class

- **Tier:** `Complementary support`
- **Pergunta cientifica:** For a given class of degradation pathways (e.g., *Alkanes*), which genes are annotated in which samples, and how diverse is their KO annotation?
- **Primary inputs:** `HADEG_Results.xlsx or HADEG_Results.csv` (sampleâ€“KOâ€“Geneâ€“compound_pathway)
- **Data inputs:** - **Primary data source:** `HADEG_Results.xlsx or HADEG_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier of the analyzed biological sample - `Gene` â€“ gene identifier used in the HADEG mapping - `ko` â€“ KEGG Orthology identifier linked to the gene - `compound_pathway` â€“ broader degradation pathway / compound class (e.g., *Alkanes*, *Aromatics*) - **Pre-processing rules:** - Discard rows with missing `sample`, `Gene`, `ko`, or `compound_pathway` - Optionally standardize string fields (trim, case normalization) to avoid artificial duplicates - **Output structure:** - 2D matrix for a **selected compound_pathway**: - Rows: `Gene` - Columns: `sample` - Cell value: count of **unique KOs** per geneâ€“sample pair
- **Como reforca a decisao:** Perfil genetico por classe de degradacao HADEG, especialmente util para Alkanes/Aromatics.
- **Relevancia para Aliphatic:** Alta se mapeado para Alkanes.
- **Relevancia para Polyaromatic:** Alta se mapeado para Aromatics.
- **Relevancia para Metal:** Baixa.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 3.3 - UC-3.3 â€” Hierarchical Clustering of Samples by Functional Profile

- **Tier:** `Complementary support`
- **Pergunta cientifica:** How do samples group together in a hierarchical structure based on the similarity of their KO annotation profiles, and how do different clustering algorithms and distance metrics affect these relationships?
- **Primary inputs:** BioRemPP results table with `sample` and `ko` columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `sample` â€“ identifier for each biological sample - `ko` â€“ KEGG Orthology identifier associated with the sample - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Derived structure:** binary presence/absence matrix with: - rows = samples - columns = unique KOs - cell = 1 if the sample has that KO, 0 otherwise
- **Como reforca a decisao:** Clustering hierarquico por perfil KO, reforcando analise de redundancia ou distancia funcional entre membros.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 3.2 - UC-3.2 â€” Principal Component Analysis of Samples by Chemical Profile

- **Tier:** `Complementary support`
- **Pergunta cientifica:** How do the samples cluster or separate based on their compound co-annotation profiles (the compounds they are co-annotated with), and which samples have the most similar or distinct compound annotation patterns?
- **Primary inputs:** BioRemPP results table with `sample` and `cpd` (compound) columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `sample` â€“ identifier for each biological sample - `cpd` â€“ identifier or name of the chemical compound associated with that sample - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Derived structure:** binary presence/absence matrix with: - rows = samples - columns = unique compounds (`cpd`) - cell = `1` if the sample is associated with the compound, `0` otherwise
- **Como reforca a decisao:** PCA por perfil quimico, util para avaliar separacao dos candidatos conforme compostos co-anotados.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 3.1 - UC-3.1 â€” Principal Component Analysis of Samples by Functional Profile

- **Tier:** `Complementary support`
- **Pergunta cientifica:** How do the samples cluster or separate based on their overall KO annotation profiles, and which samples are the most similar or distinct in their KO annotation patterns?
- **Primary inputs:** BioRemPP results table with `sample` and `ko` columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `sample` â€“ identifier for each biological sample - `ko` â€“ KEGG Orthology identifier associated with the sample - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Derived structure:** binary presence/absence matrix with: - rows = samples - columns = unique KOs - cell = 1 if the sample has the KO, 0 otherwise
- **Como reforca a decisao:** PCA por perfil funcional, util para ver se candidatos selecionados ocupam espacos funcionais distintos.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 2.3 - UC-2.3 â€” Ranking of Compound Richness by Sample per Chemical Class

- **Tier:** `Complementary support`
- **Pergunta cientifica:** Within a specific chemical class, which compounds are co-annotated with the widest range of biological samples in the dataset, and what hypotheses might this pattern suggest about shared functional potential?
- **Primary inputs:** BioRemPP results table with `sample`, `compoundclass`, and `compoundname` columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `sample` â€“ identifier for each biological sample - `compoundclass` â€“ categorical label defining the chemical class (e.g., Aromatics, Chlorinated, Alkanes) - `compoundname` â€“ name of the chemical compound - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Entities of interest:** compounds, grouped by chemical class, with counts of unique co-annotated samples
- **Como reforca a decisao:** Identifica compostos mais compartilhados por classe, ajudando a separar compostos comuns de compostos que exigem membros especificos.
- **Relevancia para Aliphatic:** Alta.
- **Relevancia para Polyaromatic:** Alta.
- **Relevancia para Metal:** Baixa.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 2.4 - UC-2.4 â€” Ranking of Compounds Richness by Gene Count per Chemical Classes

- **Tier:** `Complementary support`
- **Pergunta cientifica:** Within a specific chemical class, which compounds are associated with the greatest diversity of unique genes in the dataset, and what hypotheses might this pattern suggest about the involvement of varied enzymatic functions?
- **Primary inputs:** BioRemPP results table with `compoundclass`, `compoundname`, and `genesymbol` columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `compoundclass` â€“ categorical label defining the chemical class (e.g., Aromatics, Aliphatics, Chlorinated) - `compoundname` â€“ name of the chemical compound - `genesymbol` â€“ gene symbol or identifier associated with the interaction - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Entities of interest:** compounds, grouped by chemical class, with counts of unique associated genes
- **Como reforca a decisao:** Ranqueia compostos por diversidade de genes, apoiando a priorizacao de compostos com maior complexidade funcional.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Baixa.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 1.5 - UC-1.5 â€” Regulatory Reference Compliance Scorecard

- **Tier:** `Complementary support`
- **Pergunta cientifica:** To what extent does the annotated compound repertoire of each biological sample overlap with the compound lists of different regulatory agencies, as measured by the percentage of monitored compounds co-annotated in each sample?
- **Primary inputs:** BioRemPP results table with `sample`, `referenceAG`, and `compoundname` columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `sample` â€“ identifier for each biological sample - `referenceAG` â€“ identifier for the regulatory or scientific agency (e.g., WFD, CONAMA, EPC) - `compoundname` â€“ name of the chemical compound associated with the interaction - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Entities of interest:** - **Samples:** biological sources with co-annotated compounds in the dataset - **Regulatory agencies:** references defining sets of monitored or priority compounds
- **Como reforca a decisao:** Avalia sobreposicao entre repertorio de compostos das amostras e agencias regulatorias, adicionando relevancia regulatoria a escolha.
- **Relevancia para Aliphatic:** Media: indica se compostos alifaticos cobertos tambem tem relevancia regulatoria.
- **Relevancia para Polyaromatic:** Media: indica se compostos poliaromaticos cobertos tambem tem relevancia regulatoria.
- **Relevancia para Metal:** Media: pode reforcar o peso regulatorio dos compostos Metal.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 1.6 - UC-1.6 â€” Functional Potential of Samples Across Regulatory References

- **Tier:** `Complementary support`
- **Pergunta cientifica:** To what extent does the KO annotation breadth of different samples overlap with the compound lists of various environmental regulatory agencies, as measured by unique KO counts at each sample-agency intersection?
- **Primary inputs:** BioRemPP results table with `sample`, `referenceAG`, and `ko` columns
- **Data inputs:** - **Primary data source:** BioRemPP - **Key columns:** - `sample` â€“ identifier for each biological sample - `referenceAG` â€“ identifier for the regulatory or scientific agency (e.g., WFD, CONAMA, EPC) - `ko` â€“ KEGG Orthology identifier associated with the annotated function - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Entity of interest:** unique KO identifiers counted per `(sample, referenceAG)` pair
- **Como reforca a decisao:** Mede amplitude de KOs por amostra e agencia regulatoria, conectando potencial funcional a escopos regulatorios.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 2.5 - UC-2.5 â€” Descriptive Statistics of Samples Across Databases

- **Tier:** `Complementary support`
- **Pergunta cientifica:** How does the statistical distribution of KO annotation counts compare across different samples and annotation databases, and what insights might this provide about their scope and focus?
- **Primary inputs:** BioRemPP, HADEG, and KEGG results tables with sample-level KO annotations
- **Data inputs:** - **Primary data sources:** - BioRemPP results table - HADEG results table - KEGG results table - **Key columns (per selected database):** - `sample` â€“ identifier for each biological sample - `ko` or `Gene` â€“ KEGG Orthology identifier (or equivalent KO column) - **Accepted format:** semicolon-delimited text tables (`.txt` or `.csv`) - **Entity of interest:** unique KO counts per sample for the selected database
- **Como reforca a decisao:** Fornece estatisticas descritivas de KOs por banco, util para auditar se os candidatos estao acima ou abaixo da distribuicao geral.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 1.4 - UC-1.4 â€” Proportional Contribution of Samples Unique KO Pool

- **Tier:** `Complementary support`
- **Pergunta cientifica:** What is the relative KO annotation breadth of each biological sample compared to the total unique KO pool observed across the entire dataset?
- **Primary inputs:** BioRemPP results table with `sample` and `ko` columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `sample` â€“ identifier for each biological sample - `ko` â€“ KEGG Orthology identifier associated with the annotated function - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Entity of interest:** unique KO identifiers associated with each sample
- **Como reforca a decisao:** Quantifica a contribuicao relativa de cada amostra ao pool total de KOs, apoiando a distincao entre isolados generalistas e especialistas.
- **Relevancia para Aliphatic:** Media: ajuda a explicar candidatos com grande repertorio funcional.
- **Relevancia para Polyaromatic:** Media: ajuda a explicar candidatos com grande repertorio funcional.
- **Relevancia para Metal:** Media: permite verificar se o universo Metal concentra amostras funcionalmente amplas.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 1.1 - UC-1.1 â€” Intersections across BioRemPP, HADEG, and KEGG

- **Tier:** `Complementary support`
- **Pergunta cientifica:** To what extent do the functional annotations from different databases agree, and what unique contributions does each source provide for bioremediation-focused analysis?
- **Primary inputs:** BioRemPP, HADEG, KEGG KO annotation tables
- **Data inputs:** - **Annotation sources:** BioRemPP, HADEG, KEGG - **Required identifier column:** `ko` (KO identifiers) - **Accepted formats:** semicolon-delimited (`.txt` or `.csv`) tables - **Identifier handling:** KOs are treated as strings and normalized prior to set operations
- **Como reforca a decisao:** Compara concordancia e contribuicoes unicas entre BioRemPP, HADEG e KEGG, ajudando a qualificar a confiabilidade multi-banco das evidencias usadas nos consorcios.
- **Relevancia para Aliphatic:** Media: reforca se as anotacoes de classe tambem aparecem em bancos complementares.
- **Relevancia para Polyaromatic:** Media: reforca se as anotacoes de classe tambem aparecem em bancos complementares.
- **Relevancia para Metal:** Baixa a media: apoia a interpretacao geral da restricao Metal, mas nao testa diretamente o universo da imagem.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 4.1 - UC-4.1 â€” Functional Profiling of Samples by Metabolic Pathway

- **Tier:** `Complementary support`
- **Pergunta cientifica:** What is the KO annotation profile of each sample, as defined by the richness of annotated KOs across its metabolic pathways?
- **Primary inputs:** `KEGG_Results.xlsx or KEGG_Results.csv` (sampleâ€“KOâ€“KEGG pathway associations)
- **Data inputs:** - **Primary data source:** `KEGG_Results.xlsx or KEGG_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `pathname` â€“ KEGG pathway name or identifier - `ko` â€“ KEGG Orthology (KO) identifier associated with that sample and pathway - **User control:** - A **dropdown menu** allowing selection of a single `sample` to be profiled. - **Output structure:** - **Bars:** KEGG pathways present in the selected sample - **Bar value:** count of **unique KOs** per `(sample, pathname)` pair (pathway-level KO richness)
- **Como reforca a decisao:** Perfila KOs por pathways KEGG para cada amostra, ajudando a interpretar profundidade funcional dos candidatos.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 4.2 - UC-4.2 â€” Ranking of Samples by Pathway Richness

- **Tier:** `Complementary support`
- **Pergunta cientifica:** For any given metabolic pathway, which samples have the highest KO annotation richness, as measured by their unique KO count?
- **Primary inputs:** `KEGG_Results.xlsx or KEGG_Results.csv` (sampleâ€“KOâ€“KEGG pathway associations)
- **Data inputs:** - **Primary data source:** `KEGG_Results.xlsx or KEGG_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `pathname` â€“ KEGG pathway name or identifier - `ko` â€“ KEGG Orthology (KO) identifier associated with that sample and pathway - **User control:** - A **dropdown menu** allowing selection of a single **metabolic pathway** (`pathname`) to analyze. - **Output structure:** - **Bars:** samples associated with the selected pathway - **Bar value:** pathway-level KO richness per sample (count of unique KOs for that `sample`â€“`pathname` pair)
- **Como reforca a decisao:** Ranqueia amostras por riqueza em pathway KEGG especifico, util quando um pathway alvo for priorizado.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Baixa a media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 4.3 - UC-4.3 â€” Functional Fingerprint of Pathway by Samples

- **Tier:** `Complementary support`
- **Pergunta cientifica:** For a given metabolic pathway, what is the relative KO annotation richness of each sample, and which samples have the most extensive KO annotations?
- **Primary inputs:** `KEGG_Results.xlsx or KEGG_Results.csv` (sampleâ€“KOâ€“KEGG pathway associations)
- **Data inputs:** - **Primary data source:** `KEGG_Results.xlsx or KEGG_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `pathname` â€“ KEGG pathway name or identifier - `ko` â€“ KEGG Orthology (KO) identifier associated with that sample and pathway - **User control:** - A **dropdown menu** for selecting a single **metabolic pathway** (`pathname`) to analyze. - **Output structure:** - **Axes (Î¸):** one axis per `sample`, arranged around the circle - **Radius (r):** for each axis, the unique KO count for the selected pathway in that sample - **Polygon:** a closed shape connecting all sample points, representing the pathway's distribution of functional richness across the consortium
- **Como reforca a decisao:** Mostra footprint funcional de um pathway entre amostras, apoiando comparacoes pathway-level.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Baixa a media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 4.4 - UC-4.4 - Functional Fingerprint of Samples by Pathway

- **Tier:** `Complementary support`
- **Pergunta cientifica:** What is the KO annotation fingerprint of each sample, as defined by the distribution of unique KO annotations across its metabolic pathways?
- **Primary inputs:** `KEGG_Results.xlsx or KEGG_Results.csv` (sampleâ€“KOâ€“KEGG pathway associations)
- **Data inputs:** - **Primary data source:** `KEGG_Results.xlsx or KEGG_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `pathname` â€“ KEGG pathway name or identifier - `ko` â€“ KEGG Orthology (KO) identifier associated with that sample and pathway - **User control:** - A **dropdown menu** allowing selection of a single **Sample** (`sample`) for detailed profiling. - **Output structure:** - **Axes (Î¸):** one axis per KEGG pathway (`pathname`) present in the selected sample - **Radius (r):** unique KO count for each `(sample, pathway)` pair - **Polygon:** a closed shape connecting all pathway points, representing the sample's functional fingerprint
- **Como reforca a decisao:** Mostra fingerprint de pathways por amostra, util para explicar a especializacao de membros selecionados.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 4.5 - UC-4.5 â€” Gene Presence Map by Metabolic Pathway

- **Tier:** `Complementary support`
- **Pergunta cientifica:** For a given metabolic pathway, which specific genes are annotated in which samples, and how do these patterns reveal broadly versus narrowly distributed gene annotations across samples?
- **Primary inputs:** `KEGG_Results.xlsx or KEGG_Results.csv` (sampleâ€“geneâ€“KOâ€“pathway associations)
- **Data inputs:** - **Primary data source:** `KEGG_Results.xlsx or KEGG_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `pathname` â€“ KEGG pathway name or identifier - `genesymbol` â€“ gene symbol associated with the KO(s) for that pathway - `ko` â€“ KEGG Orthology identifier(s) linked to the gene and pathway - **User control:** - A **dropdown menu** to select a single **Metabolic Pathway** (`pathname`) for inspection. - **Output structure:** - **X-axis:** samples - **Y-axis:** gene symbols associated with the selected pathway - **Dots:** presence of a given gene in a given sample for that pathway, optionally with KO-based summaries in hover
- **Como reforca a decisao:** Mapa de presenca de genes por pathway KEGG, util para validar genes especificos em candidatos.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Baixa a media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 4.7 - UC-4.7 â€” Geneâ€“Compound Association Explorer

- **Tier:** `Complementary support`
- **Pergunta cientifica:** What are the specific co-annotation relationships between individual genes and chemical compounds, and which samples carry these co-annotations?
- **Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sampleâ€“compoundâ€“geneâ€“KO associations)
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `compoundname` â€“ individual chemical compound names - `genesymbol` â€“ gene symbols associated with the interaction - `ko` â€“ KEGG Orthology identifier(s) mapped to the gene in that context - **User controls:** - **Dropdown â€“ Compound Name:** `compoundname` (optional filter) - **Dropdown â€“ Gene Symbol:** `genesymbol` (optional filter) - **Output structure:** - **X-axis:** gene symbols - **Y-axis:** compound names - **Points:** observed geneâ€“compound associations, with hover metadata exposing the underlying samples and KOs
- **Como reforca a decisao:** Explora associacoes gene-composto e quais amostras carregam essas co-anotacoes.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 4.8 - UC-4.8 â€” Gene Inventory Explorer

- **Tier:** `Complementary support`
- **Pergunta cientifica:** What is the gene annotation inventory of each sample, and which samples carry a particular gene annotation of interest?
- **Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (sampleâ€“geneâ€“compoundâ€“KO associations)
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier for each biological sample - `genesymbol` â€“ gene symbols detected and functionally annotated - `compoundname` â€“ compounds associated with that gene in a given sample - `ko` â€“ KEGG Orthology identifier(s) mapped to the gene in that context - **User controls:** - **Dropdown â€“ Sample:** all unique `sample` identifiers - **Dropdown â€“ Gene Symbol:** all unique `genesymbol` entries - **Output structure:** - **Y-axis:** samples - **X-axis:** gene symbols - **Points:** confirmed presence of a given gene in a given sample, with hover metadata exposing associated compounds and KOs
- **Como reforca a decisao:** Inventario de genes por amostra, util para investigacao manual de genes de interesse nos candidatos.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 4.11 - UC-4.11 â€” Hierarchical View of Genetic Diversity in HADEG Pathways

- **Tier:** `Complementary support`
- **Pergunta cientifica:** What is the overall hierarchical structure of gene annotation diversity within the HADEG dataset, and how is this diversity distributed among compound pathway classes and their specific metabolic routes?
- **Primary inputs:** `HADEG_Results.xlsx or HADEG_Results.csv` (compound_pathwayâ€“pathwayâ€“gene associations)
- **Data inputs:** - **Primary data source:** `HADEG_Results.xlsx or HADEG_Results.csv` (semicolon-delimited) - **Key columns:** - `compound_pathway` â€“ broad degradation class (e.g., *Alkanes*, *Aromatics*) - `Pathway` â€“ specific metabolic pathway within that compound class - `Gene` â€“ gene identifier (or symbol) associated with that pathway - **Pre-processing rules:** - Remove rows with missing `compound_pathway`, `Pathway`, or `Gene` - Optionally standardize identifiers (trim whitespace, harmonize case) to avoid artificial duplicates - **Output structure (hierarchy):** - Root node: **All Pathways** - Inner ring: **compound_pathway** - Outer ring: **Pathway** (children of each compound_pathway) - Slice size: number of **unique genes**
- **Como reforca a decisao:** Hierarquia da diversidade genetica em HADEG, util para contextualizar quais classes/pathways sao mais diversos.
- **Relevancia para Aliphatic:** Media se HADEG Alkanes for alvo.
- **Relevancia para Polyaromatic:** Media se HADEG Aromatics for alvo.
- **Relevancia para Metal:** Baixa.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 3.6 - UC-3.6 â€” Gene Co-occurrence Across Samples

- **Tier:** `Complementary support`
- **Pergunta cientifica:** Which genes tend to co-occur across the samples, and what might this pattern suggest about potential functional relationships, co-regulation, or participation in the same metabolic pathways?
- **Primary inputs:** BioRemPP results table with `sample` and `genesymbol` columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `sample` â€“ identifier for each biological sample - `genesymbol` â€“ gene symbol or identifier associated with the sample - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Derived structure:** binary presence/absence matrix with: - rows = samples - columns = unique gene symbols - cell = `1` if the gene is present in that sample, `0` otherwise
- **Como reforca a decisao:** Estrutura, similaridade e co-ocorrencia.
- **Relevancia para Aliphatic:** Baixa a media.
- **Relevancia para Polyaromatic:** Baixa a media.
- **Relevancia para Metal:** Baixa.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 3.7 - UC-3.7 â€” Compound Co-occurrence Across Samples

- **Tier:** `Complementary support`
- **Pergunta cientifica:** Which chemical compounds tend to co-occur in the same sample annotations, and what might this pattern suggest about shared annotation contexts, co-contamination scenarios, or chemical similarity?
- **Primary inputs:** BioRemPP results table with `sample` and `compoundname` columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `sample` â€“ identifier for each biological sample - `compoundname` â€“ name (or identifier) of the chemical compound associated with the sample - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Derived structure:** binary presence/absence matrix with: - rows = samples - columns = unique compound names - cell = `1` if the compound is associated with that sample, `0` otherwise
- **Como reforca a decisao:** Estrutura, similaridade e co-ocorrencia.
- **Relevancia para Aliphatic:** Baixa a media.
- **Relevancia para Polyaromatic:** Baixa a media.
- **Relevancia para Metal:** Baixa.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 4.12 - UC-4.12 â€” Pathway Funcional Map by Sample

- **Tier:** `Complementary support`
- **Pergunta cientifica:** For a given sample, how are its specific metabolic pathway KO annotations distributed across the broader chemical families (`compound_pathway`) with which they are associated?
- **Primary inputs:** `HADEG_Results.xlsx or HADEG_Results.csv` (sampleâ€“KOâ€“Pathwayâ€“compound_pathway)
- **Data inputs:** - **Primary data source:** `HADEG_Results.xlsx or HADEG_Results.csv` (semicolon-delimited) - **Key columns:** - `sample` â€“ identifier of the analyzed biological sample - `ko` â€“ KEGG Orthology identifier associated with HADEG - `Pathway` â€“ specific HADEG/KEGG-like metabolic pathway - `compound_pathway` â€“ broader compound class (e.g., *Aromatics*, *Alkanes*) - **Pre-processing rules:** - Remove rows with missing `sample`, `ko`, `Pathway`, or `compound_pathway` - Optionally standardize string fields (trim, harmonize case) to avoid spurious duplicates - **Output structure:** - 2D matrix for a **single selected sample**: - Rows: specific `Pathway` - Columns: `compound_pathway` - Cell value: count of **unique KOs**
- **Como reforca a decisao:** Distribuicao de pathways HADEG por amostra, util para detalhar membros selecionados individualmente.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 5.3 - UC-5.3 â€” Regulatory Relevance of Samples

- **Tier:** `Complementary support`
- **Pergunta cientifica:** Which samples are most co-annotated with compounds monitored by different environmental regulatory agencies?
- **Primary inputs:** BioRemPP results table with `sample` and `referenceAG` columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `sample` â€“ identifier for each biological sample - `referenceAG` â€“ regulatory or scientific agency label (e.g., WFD, CONAMA, EPC) - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Derived structure:** interaction matrix with: - rows = samples - columns = regulatory agencies - cell = interaction count for each sampleâ€“agency pair
- **Como reforca a decisao:** Relevancia regulatoria por amostra, adicionando contexto de prioridade ambiental aos candidatos.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Alta se regulacoes incluem metais relevantes.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 5.4 - UC-5.4 â€” Geneâ€“Compound Interaction Network

- **Tier:** `Complementary support`
- **Pergunta cientifica:** What is the overall structure of the interaction network between genes and chemical compounds, and which entities may act as central "hubs" connecting disparate functions?
- **Primary inputs:** BioRemPP results table with `genesymbol` and `compoundname` columns
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` **Key columns:** - `genesymbol` â€“ gene symbol or identifier - `compoundname` â€“ name (or identifier) of the associated chemical compound - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Derived structures:** - node set of **genes** - node set of **compounds** - edge list of observed **geneâ€“compound interactions**
- **Como reforca a decisao:** Rede gene-composto para identificar hubs funcionais associados aos compostos cobertos.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 6.1 - UC-6.1 â€” Regulatory-to-Molecular Interaction Flow

- **Tier:** `Complementary support`
- **Pergunta cientifica:** How do high-level regulatory contexts flow through specific samples and their gene co-annotations to reach individual chemical compounds?
- **Primary inputs:** BioRemPP results table with `referenceAG`, `sample`, `genesymbol`, and `compoundname`
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `referenceAG` â€“ regulatory or scientific agency label - `sample` â€“ identifier for each biological sample - `genesymbol` â€“ gene symbol or identifier - `compoundname` â€“ chemical compound name or identifier - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Conceptual flow (stages):** 1. **Regulatory Agency** (`referenceAG`) 2. **Sample** (`sample`) 3. **Gene Symbol** (`genesymbol`) 4. **Compound Name** (`compoundname`)
- **Como reforca a decisao:** Fluxo agencia -> amostra -> gene -> composto, conectando candidatos a contexto regulatorio e molecular.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 6.3 - UC-6.3 â€” Chemical Hierarchy

- **Tier:** `Complementary support`
- **Pergunta cientifica:** Which chemical classes and specific compounds are co-annotated with the most diverse gene sets, and which samples contribute the most to this annotation diversity?
- **Primary inputs:** BioRemPP results table with `compoundclass`, `compoundname`, `sample`, and `genesymbol`
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `compoundclass` â€“ high-level chemical class or category - `compoundname` â€“ specific compound or pollutant name - `sample` â€“ identifier for each biological sample - `genesymbol` â€“ gene symbol or identifier associated with that sampleâ€“compound pair - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Hierarchical structure:** 1. **Compound Class** (`compoundclass`) 2. **Compound Name** (`compoundname`) 3. **Sample** (`sample`)
- **Como reforca a decisao:** Hierarquia quimica por classe, composto, amostra e gene; boa sintese para explicar contribuicoes por classe.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 6.4 - UC-6.4 â€” Enzymatic Hierarchy

- **Tier:** `Complementary support`
- **Pergunta cientifica:** Which enzymatic functions are co-annotated with the widest range of unique compounds, how is this co-annotation breadth distributed across different chemical classes, and which specific genes are the primary contributors?
- **Primary inputs:** BioRemPP results table with `enzyme_activity`, `compoundclass`, `genesymbol`, and `compoundname`
- **Data inputs:** - **Primary data source:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` - **Key columns:** - `enzyme_activity` â€“ functional category/label of the enzymatic activity - `compoundclass` â€“ chemical class/category of the substrates - `genesymbol` â€“ gene symbol or identifier implementing that activity in at least one sample - `compoundname` â€“ specific compound name or identifier - **Accepted format:** semicolon-delimited text table (`.txt` or `.csv`) - **Hierarchical structure:** 1. **Enzyme Activity** (`enzyme_activity`) 2. **Compound Class** (`compoundclass`) 3. **Gene Symbol** (`genesymbol`)
- **Como reforca a decisao:** Hierarquia enzimatica por atividade, classe e genes; reforca quais funcoes sustentam a cobertura.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Media.
- **Relevancia para Metal:** Media.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 7.1 - UC-7.1 â€” Predicted Compound Toxicity Profiles

- **Tier:** `Complementary support`
- **Pergunta cientifica:** What is the comprehensive toxicological profile of each chemical compound across a wide range of risk categories, and which compounds pose the most significant and multi-endpoint hazards?
- **Primary inputs:** ToxCSM results table (`ToxCSM.xlsx or ToxCSM.csv`) with paired `value_` and `label_` columns
- **Data inputs:** - **Primary data source:** `ToxCSM.xlsx or ToxCSM.csv` (semicolon-delimited) - **Key columns:** - `compoundname` â€“ name of the chemical compound - `value_*` â€“ numerical toxicity scores predicted by ToxCSM (e.g., `value_Gen_Carcinogenesis`) - `label_*` â€“ qualitative categories corresponding to each score (e.g., "High", "Low", "Non-toxic") - **Derived fields:** - `endpoint` â€“ specific toxicological endpoint (e.g., `Gen_Carcinogenesis`) - `supercategory` â€“ grouped toxicity domain (e.g., `Genomic`) - **Toxicity super-categories:** - Nuclear Response - Stress Response - Genomic - Environmental - Organic
- **Como reforca a decisao:** Perfil toxicologico dos compostos, util para explicar prioridade dos compostos cobertos.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Alta.
- **Relevancia para Metal:** Alta.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

### UC 7.2 - UC-7.2 â€” Concordance Between Predicted Risk and Regulatory Scope

- **Tier:** `Complementary support`
- **Pergunta cientifica:** What is the structure and magnitude of the overlap between compounds monitored by regulatory agencies and those predicted to be of high toxicological risk?
- **Primary inputs:** `BioRemPP_Results.xlsx or BioRemPP_Results.csv` (regulatory annotation) and `ToxCSM.xlsx or ToxCSM.csv` (predicted toxicity labels)
- **Data inputs:** - **Primary data sources:** - `BioRemPP_Results.xlsx or BioRemPP_Results.csv` â€“ regulatory annotation for compounds - `ToxCSM.xlsx or ToxCSM.csv` â€“ predicted toxicity scores and labels for compounds - **Key columns:** - From `BioRemPP_Results.xlsx or BioRemPP_Results.csv`: - `referenceAG` â€“ identifier for the regulatory or scientific agency (e.g., WFD, CONAMA, EPC) - `compoundname` â€“ name of the chemical compound - From `ToxCSM.xlsx or ToxCSM.csv`: - `compoundname` â€“ name of the chemical compound (must be linkable to BioRemPP) - `label_*` â€“ qualitative toxicity labels for individual endpoints (e.g., "High Toxicity") - **Entities represented in the chord diagram:** - Individual **Regulatory Agencies** (`referenceAG`) - A synthetic **"High Predicted Risk"** category, aggregating all compounds predicted as highly toxic by ToxCSM
- **Como reforca a decisao:** Concordancia entre risco predito e escopo regulatorio, adicionando peso ambiental aos alvos.
- **Relevancia para Aliphatic:** Media.
- **Relevancia para Polyaromatic:** Alta.
- **Relevancia para Metal:** Alta.
- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.

## Context only

| UC | Titulo | Papel |
|---|---|---|
| UC 5.5 | UC-5.5 â€” Geneâ€“Gene Interaction Network (Based on Shared Compounds) | Rede gene-gene baseada em compostos compartilhados; mais util para mecanismo geral do que para decidir membros do consorcio. |
| UC 5.6 | UC-5.6 â€” Compoundâ€“Compound Interaction Network (Based on Shared Genes) | Rede composto-composto baseada em genes compartilhados; ajuda a entender estrutura quimica, mas nao seleciona isolados diretamente. |
| UC 7.4 | UC-7.4 â€” Distribution of Toxicity Scores by Endpoint | Distribuicao de scores toxicológicos por endpoint; informa risco geral dos compostos, mas sem foco em amostras. |
| UC 7.5 | UC-7.5 â€” Probability Distributions of Toxicity Scores by Endpoint | Distribuicoes probabilisticas de scores toxicológicos; util para contexto de risco, pouco decisivo para membros. |
| UC 1.2 | UC-1.2 â€” Overlap of Compounds Across Regulatory References | Contexto regulatorio e comparativo geral. |
| UC 1.3 | UC-1.3 â€” Proportional Contribution of Regulatory References | Contexto regulatorio e comparativo geral. |

## Not recommended

Nenhum UC classificado como `Not recommended` nesta rodada.

## Limitacoes

- Esta etapa classifica e documenta UCs de suporte; ela nao recalcula todos os graficos ou metricas originais.
- A classificacao e metodologica e deve ser usada como roteiro para analises subsequentes por UC.
- `UC 8.1` foi mantido como referencia central porque ja fundamenta a modelagem dos consorcios.
- A interpretacao experimental DCPIP deve permanecer complementar as evidencias anotacionais.

## Validacao da extracao

Todos os UCs inspecionados possuem as secoes esperadas de pergunta cientifica e dados de entrada.

