# 4 – Functional and Genetic Profiling

This module explores KO annotation coverage and gene-level composition of samples at finer resolution. After characterizing how samples cluster and rank in terms of their KO annotation profiles and co-annotated chemical space, the analyses in this section focus on *which pathways and genes are represented* in each sample and *how KO annotations are distributed* across the sample collection. The analyses are organized to support annotation-level exploration and hypothesis generation: from broad KO annotation fingerprints, to comparative sample ranking, down to gene-level annotation patterns. The goal is to provide annotation-interpretable profiles that can support hypothesis-driven experimental planning (experimental validation required to confirm functional capacity).

### 4.1. What are the KO annotation profiles of each individual sample?

We first construct a KO annotation profile—or "fingerprint"—for every sample. This involves characterizing the set of KEGG pathways for which KO annotations are present and quantifying the KO richness per pathway as key indicators. Through this lens, we can obtain a pathway-level view of each sample's annotation breadth and prominent annotated pathways. Samples can then be compared along a continuum from those with broad and diverse KO annotations across many pathways to those with annotations concentrated in a narrower set of pathways (experimental validation required to confirm functional roles).

### 4.2. For a specific pathway, which samples have the most extensive KO annotations?

Once individual profiles are established, the analysis shifts to a comparative perspective. Instead of asking "what can each sample do?", we ask: *for a given metabolic pathway, functional category, or chemical class of interest, which samples have the most extensive KO annotations?* We address this by ranking samples according to annotation-level metrics such as the number of unique KOs associated with the selected function. The result is an annotation-based ranking of samples that may serve as a starting point for hypothesis-driven investigation focused on a particular pathway or class of compounds (experimental validation required).

### 4.3. What is the gene-level and hierarchical annotation architecture of these pathways?

Finally, we examine the gene-level and structural composition of annotated pathways across samples. We map gene annotations associated with selected pathways to distinguish broadly represented genes (present across many samples) from those restricted to subsets of samples. In parallel, we explore the hierarchical organization of pathways—from genes and KOs to modules and metabolic routes—and provide tools to query specific gene–sample and gene–compound annotation associations. This level of resolution can support hypothesis generation and the design of targeted experimental validations (experimental validation is required to confirm mechanistic roles).
