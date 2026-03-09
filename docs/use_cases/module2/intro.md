# 2 - Exploratory Analysis: Ranking the Functional Potential of Samples and Compounds

This module provides a quantitative overview of the annotation landscape captured by BioRemPP. Before interrogating higher-order relationships it is necessary to characterize how KO annotation coverage is distributed across samples and chemical targets. Here, we focus on ranking and describing both sides of the system: the input samples (as biological sources of annotations) and the compounds (as annotation targets in the dataset). Together, these analyses can define a baseline from which more complex network- and pathway-level interpretations can be derived.

### 2.1. What are the key annotation characteristics of the input samples?

We begin by profiling and ranking each sample using two core metrics: (i) the count of unique KO identifiers and (ii) the breadth of compound co-annotations. These metrics characterize a sample's annotation coverage and compound association breadth within the dataset. The resulting ranking can help orient exploratory analyses and hypothesis generation about which samples show broader or narrower annotation coverage, and may serve as a starting point for deeper experimental or computational follow-up.

### 2.2. Which compounds show the broadest sample co-annotation in the dataset?

In parallel, we invert the perspective and focus on the chemical scope. We rank compounds according to the number of unique samples and genes with which they are co-annotated in the dataset. This procedure can distinguish compounds with broad sample co-occurrence patterns from those with more limited annotation overlap. High-ranking compounds in this dimension may reflect widely annotated targets in the dataset, and may generate hypotheses about shared annotation coverage — though this does not confirm metabolic accessibility or degradation potential.

### 2.3. What is the overall distribution of KO annotation counts?

Finally, we examine the statistical distribution of these annotation metrics across the full dataset. By visualizing the variance, skewness, and range of KO annotation counts and compound co-annotation breadth, we move beyond individual rankings to characterize global annotation patterns — for example, whether annotation coverage is concentrated in a few samples or more evenly distributed. This baseline characterization can inform the interpretation of downstream analyses.
