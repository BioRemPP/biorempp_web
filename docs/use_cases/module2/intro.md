# 2 - Exploratory Analysis: Ranking the Functional Potential of Samples and Compounds

This module provides a quantitative overview of the functional landscape captured by BioRemPP. Before interrogating higher-order relationships it is necessary to characterize how functional potential is distributed across samples and chemical targets. Here, we focus on ranking and describing both sides of the system: the input samples (as biological sources of functions) and the compounds (as substrates, pollutants, or intermediates that drive selective pressure). Together, these analyses can define a baseline from which more complex network- and pathway-level interpretations can be derived.

### 2.1. What are the key performance characteristics of the input samples?

We begin by profiling and ranking each sample using two core metrics: (i) the diversity of unique functional identifiers (KOs) and (ii) the breadth of compound interactions inferred from those functions. These metrics jointly capture the versatility of a sample—its potential to encode and express a wide range of bioremediation-relevant activities. The resulting ranking may highlight the most functionally potent "generalist" samples, which combine high functional richness with broad compound coverage and therefore may represent prime candidates for deeper experimental or computational follow-up.

### 2.2. What defines a high-priority chemical target from a biological perspective?

In parallel, we invert the perspective and focus on the chemical scope. We rank compounds according to the breadth and intensity of the biological response they elicit, quantified by the number of unique samples and genes that interact with each compound. This procedure can distinguish compounds that function as widely accessible substrates from those that pose more stringent or complex metabolic challenges. High-ranking compounds in this dimension may represent critical bottlenecks, key pollutants of concern, or central hubs in the bioremediation landscape.

### 2.3. What is the overall distribution of functional potential?

Finally, we examine the statistical distribution of these performance metrics across the full dataset. By visualizing the variance, skewness, and range of functional diversity and compound coverage, we move beyond individual rankings to characterize global system properties—for example, whether functional potential is concentrated in a few highly versatile samples or more evenly distributed. This baseline characterization is essential for interpreting downstream analyses of metabolic networks and pathways.
