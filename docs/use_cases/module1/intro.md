# 1 - Comparative Assessment of Databases, Samples, and Regulatory Frameworks

This module establishes the analytical and methodological foundation of the entire BioRemPP workflow. Before exploring higher-level biological or ecological inferences, it is essential to: (i) evaluate the reliability and complementarity of the reference databases; (ii) align the resulting annotations with environmentally relevant regulatory frameworks; and (iii) position the input samples within this validated and regulation-aware landscape. Together, these analyses can help ensure that subsequent results are not only biologically plausible but also interpretable in terms of compliance, priority, and practical applicability to bioremediation scenarios.

### 1.1. What is the reliability of the data sources?

We begin by validating the BioRemPP pipeline against established reference resources. By systematically comparing its annotations to those from the HADEG and Degradation pathways from KEGG databases, we quantify both the agreement between sources and the unique contribution of the BioRemPP compound-centric approach. This comparative assessment can enable us to identify shared and exclusive signals, highlighting how much novel or refined information is gained by our strategy. The impact of this step is twofold: it may reinforce the robustness of the pipeline and can support the originality of the resulting bioremediation-focused database and analyses.

### 1.2. What is the landscape of regulatory relevance?

Next, we characterize the regulatory landscape associated with the annotated compounds. We do so by examining the overlap and coverage between compound lists from key environmental agencies and regulatory frameworks. This transforms raw lists of compounds into a structured set of "priority targets," defined by their regulatory status, environmental concern, or monitoring requirements. In practice, this step can direct the analytical focus toward compounds with the greatest potential impact on environmental policy, risk assessment, and regulatory decision-making.

### 1.3. Which input samples show the broadest annotation overlap with regulatory compound lists?

Finally, we situate each input sample within this validated and regulation-aware context. We assess both their KO annotation richness and compound annotation richness, and compute an annotation-level overlap score that reflects the percentage of an agency's listed compounds associated with KOs present in each sample's annotation. Rather than implying operational readiness, this step characterizes samples according to their annotation-level representation within regulatory compound spaces, providing a basis for prioritizing samples for further exploration and hypothesis generation.
