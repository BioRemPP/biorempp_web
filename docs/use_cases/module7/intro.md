# 7 – Toxicological Risk Assessment and Profiling

This module transitions from purely annotation-level analysis to an application-oriented perspective centered on chemical safety and risk context. Using toxicity predictions from the toxCSM model, we systematically evaluate the hazard profile of the compounds present in the dataset and relate these risks to the KO annotation profiles of the input samples. The analyses are structured as a logical sequence of questions that progress from a broad characterization of the toxicological landscape to a detailed, sample-specific profiling of annotation-level responses. The objective is to provide a toxicology-aware framework for contextualizing annotation data and generating hypotheses for experimental follow-up.

### 7.1. What is the comprehensive toxicological landscape?

We first establish a "risk fingerprint" for each compound across a broad panel of toxicological endpoints predicted by toxCSM. This comprehensive profiling may reveal the full spectrum of potential adverse effects, enabling the identification of compounds that span several biological and environmental hazard categories (e.g., genomic damage, organism-level toxicity, environmental persistence). The result is a global toxicological landscape that may highlight which compounds are of localized concern and which may represent multi-category hazards. This landscape serves as the foundational layer upon which all subsequent risk-aware analyses are built.

### 7.2. How do these predicted risks align with established regulatory priorities?

To anchor the predictive toxicity data in real-world decision-making contexts, we next evaluate the concordance between high-risk compounds and those monitored or flagged by key environmental and regulatory agencies. This step addresses the critical question of which predicted hazards are also recognized as priorities in existing regulatory frameworks. The outcome is a refined set of "consensus priority compounds" that are important from both a toxicological and a compliance standpoint. Focusing on this consensus set can provide a more targeted and impactful basis for downstream assessments and policy-relevant discussions.

### 7.3. Which samples have the highest KO annotation counts linked to high-priority compounds?

Once the most critical chemical threats have been identified, we shift our attention to the KO annotation profiles of the input samples. For each sample, we quantify the diversity and richness of KO annotations co-annotated with consensus priority compounds. This allows us to identify samples with particularly high KO annotation coverage for specific high-risk compounds. The result is a mapping between high-priority compounds and the samples with the broadest annotation coverage, providing a hypothesis-generating starting point for further experimental investigation.

### 7.4. How can the broader annotation profiles of the samples be characterized relative to high-priority compounds?

Finally, we develop a view of each sample's KO annotation profile in the context of high-priority compounds. We characterize annotation coverage along two complementary axes: **breadth**, defined as the variety of distinct high-risk compounds co-annotated with a sample's KOs, and **depth**, defined as the magnitude and redundancy of KO annotations directed toward those compounds. By integrating these dimensions, we can generate a comparative annotation profile for each candidate sample. This provides an annotation-level basis for hypothesis generation; experimental validation is required to confirm functional or remediation capacity.
