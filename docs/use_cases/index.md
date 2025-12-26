
# Use Case Documentation (Index)

This page centralizes the documented use cases for BioRemPP grouped by analysis module. Use the links below to open each module Module Description and the individual use-case markdown pages.

## How to Navigate the Use Case Documentation

The BioRemPP use case documentation is organized into **analysis modules**, each composed of a set of **self-contained analytical use cases**. This structure is designed to guide users from high-level methodological questions to detailed, reproducible analytical workflows.

Each **module** represents a thematic analytical block (e.g., database comparison, functional ranking, regulatory assessment), while each **use case** within a module corresponds to a **specific scientific question** addressed through a standardized computational and visualization pipeline.

### Standard Structure of a Use Case

All use cases follow a consistent documentation pattern to ensure clarity, interpretability, and reproducibility:

1. **Use Case Overview**  
   Each use case begins with a concise summary describing:

   - The associated module and analytical scope  
   - The visualization or analytical strategy employed  
   - The primary data sources and outputs involved  

2. **Scientific Question and Rationale**  
   A clearly stated scientific question motivates the analysis, followed by a rationale explaining:

   - Why the analysis is relevant for bioremediation research  
   - What biological, functional, or regulatory insight is being explored  

3. **Data and Inputs**  
   This section specifies:

   - Required input data sources and identifiers  
   - Accepted formats and preprocessing assumptions  
   - Any normalization or validation steps applied to the inputs  

4. **Analytical Workflow**  
   A step-by-step description of the computational process, typically covering:
   
   - Data loading and parsing  
   - Identifier standardization and filtering  
   - Core analytical or statistical operations  
   - Visualization or aggregation logic  

5. **How to Read the Results**  
   Guidance on interpreting the generated plots or tables, explaining:

   - The meaning of each visual component  
   - How to relate patterns in the visualization to biological or functional hypotheses  

6. **Interpretation and Key Messages**  
   A synthesis of the main insights that can be drawn from the analysis, including:

   - Consensus signals across databases or samples  
   - Database- or sample-specific patterns  
   - Limitations or caveats in interpretation  

7. **Reproducibility and Assumptions**  
   Explicit documentation of assumptions, constraints, and reproducibility conditions, such as:

   - Identifier handling and deduplication rules  
   - Input resolution limitations  
   - Fixed database versions used at analysis time  

8. **Activity Diagram**  
   Each use case concludes with an **activity diagram** that visually summarizes the analytical flow, from input ingestion to result generation. These diagrams provide a high-level operational view of how the pipeline components interact.

### Intended Usage

Users may:

- Read individual use cases independently, based on specific analytical needs  
- Navigate sequentially within a module to understand complementary analyses  
- Use the activity diagrams as a conceptual reference for reproducing or extending analyses programmatically  

This modular and standardized structure allows BioRemPP use cases to function both as **executable analytical documentation** and as **methodological references** for bioremediation-focused functional analysis workflows.


- Module 1 - Comparative Assessment of Databases, Samples, and Regulatory Frameworks
	- [Module Description](module1/intro.md)
	- [UC 1.1 — Intersections across BioRemPP, HADEG, and KEGG](module1/uc_1.1.md)
	- [UC 1.2 — Overlap of Compounds Across Regulatory References](module1/uc_1.2.md)
	- [UC 1.3 — Proportional Contribution of Regulatory References](module1/uc_1.3.md)
	- [UC 1.4 — Proportional Contribution of Samples Unique KO Pool](module1/uc_1.4.md)
	- [UC 1.5 — Regulatory Reference Compliance Scorecard](module1/uc_1.5.md)
	- [UC 1.6 — Functional Potential of Samples Across Regulatory References](module1/uc_1.6.md)
- Module 2 - Exploratory Analysis: Ranking the Functional Potential of Samples and Compounds
	- [Module Description](module2/intro.md)
	- [UC 2.1 — Ranking of Sample Functional Richness Across Databases](module2/uc_2.1.md)
	- [UC 2.2 — Ranking of Samples by Chemical Diversity](module2/uc_2.2.md)
	- [UC 2.3 — Ranking of Compound Richness by Sample per Chemical Class](module2/uc_2.3.md)
	- [UC 2.4 — Ranking of Compounds Richness by Gene Count per Chemical Classes ](module2/uc_2.4.md)
	- [UC 2.5 — Descriptive Statistics of Samples Across Databases](module2/uc_2.5.md)
- Module 3 - System Structure: Clustering, Similarity, and Co-occurrence
	- [Module Description](module3/intro.md)
	- [UC 3.1  — Principal Component Analysis of Samples by Functional Profile](module3/uc_3.1.md)
	- [UC 3.2 — Principal Component Analysis of Samples by Chemical Profile](module3/uc_3.2.md)
	- [UC 3.3 — Hierarchical Clustering of Samples by Functional Profile](module3/uc_3.3.md)
	- [UC 3.4 — Sample Similarity (Based on KO Profiles) ](module3/uc_3.4.md)
	- [UC 3.5 — Sample Similarity (Based on Chemical Profiles)](module3/uc_3.5.md)
	- [UC 3.6 — Gene Co-occurrence Across Samples](module3/uc_3.6.md)
	- [UC 3.7 — Compound Co-occurrence Across Samples](module3/uc_3.7.md)
- Module 4 - Functional and Genetic Profiling
	- [Module Description](module4/intro.md)
	- [UC 4.1 — Functional Profiling of Samples by Metabolic Pathway](module4/uc_4.1.md)
	- [UC 4.2 — Ranking of Samples by Pathway Richness](module4/uc_4.2.md)
	- [UC 4.3 — Functional Fingerprint of Pathway by Samples](module4/uc_4.3.md)
	- [UC 4.4 - Functional Fingerprint of Samples by Pathway](module4/uc_4.4.md)
	- [UC 4.5 — Gene Presence Map by Metabolic Pathway](module4/uc_4.5.md)
	- [UC 4.6 — Functional Potential by Chemical Compound](module4/uc_4.6.md)
	- [UC 4.7 — Gene–Compound Association Explorer](module4/uc_4.7.md)
	- [UC 4.8 —  Gene Inventory Explorer](module4/uc_4.8.md)
	- [UC 4.9 — Profiling of Sample Enzymatic Activity](module4/uc_4.9.md)
	- [UC 4.10 — Diversity of Enzymatic Activities Across Samples](module4/uc_4.10.md)
	- [UC 4.11 —  Hierarchical View of Genetic Diversity in HADEG Pathways](module4/uc_4.11.md)
	- [UC 4.12 —  Pathway Funcional Map by Sample](module4/uc_4.12.md)
	- [UC 4.13 — Genetic Profile by Compound Class](module4/uc_4.13.md)
- Module 5 - Modeling Interactions among Samples, Genes, and Compounds
	- [Module Description](module5/intro.md)
	- [UC 5.1 — Sample-Compound Class Interaction](module5/uc_5.1.md)
	- [UC 5.2 — Sample Similarity (Based on Chemical Profiles)](module5/uc_5.2.md)
	- [UC 5.3 — Regulatory Relevance of Samples ](module5/uc_5.3.md)
	- [UC 5.4 — Gene–Compound Interaction Network](module5/uc_5.4.md)
	- [UC 5.5 — Gene–Gene Interaction Network (Based on Shared Compounds) ](module5/uc_5.5.md)
	- [UC 5.6 — Compound–Compound Interaction Network (Based on Shared Genes)](module5/uc_5.6.md)
- Module 6 - Hierarchical and Flow-based Functional Analysis
	- [Module Description](module6/intro.md)
	- [UC 6.1 — Regulatory-to-Molecular Interaction Flow](module6/uc_6.1.md)
	- [UC 6.2 — Biological Interaction Flow](module6/uc_6.2.md)
	- [UC 6.3 — Chemical Hierarchy](module6/uc_6.3.md)
	- [UC 6.4 — Enzymatic Hierarchy](module6/uc_6.4.md)
	- [UC 6.5 — Chemical–Enzymatic Hierarchy](module6/uc_6.5.md)
- Module 7 - Toxicological Risk Assessment and Profiling
	- [Module Description](module7/intro.md)
	- [UC 7.1 — Predicted Compound Toxicity Profiles](module7/uc_7.1.md)
	- [UC 7.2 — Concordance Between Predicted Risk and Regulatory Scope](module7/uc_7.2.md)
	- [UC 7.3 — Mapping of Genetic Response to High-Priority Threats](module7/uc_7.3.md)
	- [UC 7.4 — Distribution of Toxicity Scores by Endpoint](module7/uc_7.4.md)
	- [UC 7.5 — Probability Distributions of Toxicity Scores by Endpoint](module7/uc_7.5.md)
	- [UC 7.6 — Sample Risk Mitigation Breadth](module7/uc_7.6.md)
	- [UC 7.7 — Sample Risk Mitigation Depth](module7/uc_7.7.md)
- Module 8 - Minimal Sample Grouping for Complete Compound Coverage
	- [Module Description](module8/intro.md)
	- [UC 8.1 — Minimal Sample Grouping for Complete Compound Coverage](module8/uc_8.1.md)
	- [UC 8.2 — BioRemPP Chemical Class Completeness Scorecard](module8/uc_8.2.md)
	- [UC 8.3 — Compound-Specific KO Completeness Scorecard](module8/uc_8.3.md)
	- [UC 8.4 — HADEG Pathways Completeness Scorecard](module8/uc_8.4.md)
	- [UC 8.5 — KEGG Pathways Completeness Scorecard](module8/uc_8.5.md)
	- [UC 8.6 — Pathway-Centric Consortium Design by KO Coverage](module8/uc_8.6.md)
	- [UC 8.7 — Sample-Sample KO Intersection Profile](module8/uc_8.7.md)
