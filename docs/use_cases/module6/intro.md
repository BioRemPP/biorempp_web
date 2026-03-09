# 6 – Hierarchical and Flow-based Functional Analysis

While previous modules focus on ranking, clustering, and profiling individual entities (samples, genes, and compounds), here we explicitly examine *how* these annotation components are organized into hierarchical structures and *how* co-annotations flow between them. By combining flow-based and hierarchical visualizations, we aim to reveal dominant routes of co-annotation, internal composition of key annotation categories, and the structural context in which annotated functions are distributed across the dataset.

### 6.1. What are the primary pathways of co-annotation flow?

We first employ alluvial diagrams to visualize how co-annotations flow across different organizational levels of the system. These diagrams trace connections from high-level categories—such as regulatory agencies, chemical classes, or samples—down to specific genes and compounds. This can enable us to identify major routes by which regulatory priorities, sample annotation profiles, and molecular co-annotations intersect. The result is a clear, intuitive mapping of where co-annotations concentrate, which categories act as main "bridges," and which entities emerge as recurrent transition points along the flow.

### 6.2. What is the internal composition of the most important annotation and chemical categories?

To deepen this structural perspective, we then examine the internal composition of the system's most relevant annotation and chemical categories. Treemaps are used to decompose broad classes—such as compound families or annotated enzymatic groups—into their constituent elements and subcategories. This allows us to visualize heterogeneity within each category, identify where annotation diversity is greatest, and highlight subclasses that contribute disproportionately to overall annotation counts. In doing so, we provide a detailed compositional context for the major co-annotation pathways identified in the alluvial diagrams.

### 6.3. How do flow-based and hierarchical views combine to support structural interpretation?

Finally, we integrate the flow-based and hierarchical perspectives to support more informed, exploration-oriented interpretation. By overlaying key co-annotation pathways (from alluvial diagrams) with the internal structure of categories (from treemaps), we can pinpoint where prominent annotation flows intersect with highly diverse or enriched annotation subgroups. This combined view can help to identify leverage points—for example, specific compound classes, annotation modules, or sample groups—that are both structurally central and internally rich in annotation. Such points are natural candidates for prioritization in downstream analyses and experimental design.
