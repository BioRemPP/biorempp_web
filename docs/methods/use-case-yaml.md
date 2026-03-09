# Use Case YAML Configuration Methodology

## Overview

BioRemPP employs a **declarative YAML-based configuration system** to define analytical use cases. This approach separates visualization logic from business rules, enabling reproducible, auditable, and maintainable analytical configurations.

Each use case is fully described through YAML files that specify:

- **What data** to process
- **How to transform** the data
- **How to visualize** the results
- **What validation rules** to apply
- **How to handle errors**

This methodology supports the scientific requirement of **traceability**: analytical outputs can be linked to a specific, versioned configuration state.

---

## Design Principles

### Declarative Over Imperative

Configuration files describe the **desired outcome**, not the procedural steps to achieve it. The system interprets these declarations and executes the appropriate logic.

```yaml
# Declarative: WHAT to do
processing:
  steps:
    - name: "group_and_count"
      params:
        group_by: "Sample"
        agg_function: "nunique"
```

### Separation of Concerns

| Layer | Responsibility | File |
|-------|----------------|------|
| **Configuration** | What to compute and display | `*_config.yaml` |
| **Scientific Context** | Interpretation guidelines | `*_panel.yaml` |
| **Implementation** | How to execute | Python strategies |

### Reproducibility

Given identical:
- Input data
- Configuration version
- Database snapshot

The system produces **identical outputs**.

---

## File Structure

Each analytical module contains use case configurations organized by module number:

```
src/infrastructure/plot_configs/
├── module1/
│   ├── uc_1_1_config.yaml
│   ├── uc_1_1_panel.yaml
│   ├── uc_1_2_config.yaml
│   └── ...
├── module2/
├── module3/
└── ...
```

### Naming Convention

| Pattern | Description | Example |
|---------|-------------|---------|
| `uc_X_Y_config.yaml` | Plot configuration | `uc_2_1_config.yaml` |
| `uc_X_Y_panel.yaml` | Scientific panel | `uc_2_1_panel.yaml` |

Where `X` = module number, `Y` = use case number within module.

---

## Data Flow

```
┌─────────────────┐
│   YAML Config   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Loading   │ ← Store ID from config
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Validation    │ ← Rules from config
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Processing    │ ← Steps from config
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Visualization  │ ← Strategy from config
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Plotly Figure │
└─────────────────┘
```

---

## Configuration Schema

### Plot Configuration (`*_config.yaml`)

A complete plot configuration contains the following sections:

#### 1. Metadata Section

Identifies the use case and provides context.

| Field | Required | Description |
|-------|----------|-------------|
| `use_case_id` | Yes | Unique identifier (e.g., "UC-2.1") |
| `module` | Yes | Parent module (e.g., "module2") |
| `title` | Yes | Human-readable title |
| `description` | Yes | Brief explanation of the visualization |
| `version` | Yes | Semantic version (e.g., "1.0.0") |
| `plot_type` | Yes | Chart type (bar_chart, heatmap, upset, etc.) |
| `tags` | No | Categorization keywords |
| `scientific_context` | No | Domain, application, interpretation |

#### 2. Data Section

Specifies data source and processing pipeline.

| Field | Required | Description |
|-------|----------|-------------|
| `source` | Yes | Store identifier (e.g., "biorempp-merged-data") |
| `source_type` | Yes | Source type ("store", "file", "api") |
| `required_columns` | Yes | Columns that must exist in input data |
| `optional_columns` | No | Columns that enhance functionality |
| `processing.steps` | Yes | Ordered list of transformation steps |

**Processing Steps:**

| Step Name | Purpose | Key Parameters |
|-----------|---------|----------------|
| `validate` | Check data validity | `validator` |
| `group_and_count` | Aggregate data | `group_by`, `agg_column`, `agg_function`, `result_column` |
| `sort` | Order results | `by`, `ascending` |
| `filter_range` | Apply value filters | `column`, `min`, `max` |
| `limit` | Restrict row count | `n` |
| `normalize_identifiers` | Clean identifiers | `strip_whitespace`, `convert_uppercase` |

#### 3. Visualization Section

Controls chart rendering.

| Field | Required | Description |
|-------|----------|-------------|
| `strategy` | Yes | Rendering strategy class |
| `plotly.chart_type` | Yes | Plotly chart type |
| `plotly.x` | Depends | X-axis column |
| `plotly.y` | Depends | Y-axis column |
| `plotly.orientation` | No | "v" (vertical) or "h" (horizontal) |
| `plotly.color_discrete_sequence` | No | Color palette |
| `plotly.layout` | Yes | Chart layout configuration |

## Available Strategies

**Total strategies:** 19

| Strategy | Plot Type | Use Case |
|----------|-----------|----------|
| `BarChartStrategy` | Bar charts | Rankings, counts |
| `StackedBarChartStrategy` | Stacked bar charts | Composition across groups |
| `BoxScatterStrategy` | Box + scatter | Distribution + point-level variability |
| `DensityPlotStrategy` | Density plots | Distribution shape comparison |
| `DotPlotStrategy` | Dot plots | Compact comparisons across categories |
| `HeatmapStrategy` | Heatmaps | Matrices, intensities, correlations |
| `HeatmapScoredStrategy` | Scored heatmaps | Heatmaps with scoring or ranking overlays |
| `FacetedHeatmapStrategy` | Multi-panel heatmaps | Category-based comparisons |
| `CorrelogramStrategy` | Correlograms | Correlation structure analysis |
| `HierarchicalClusteringStrategy` | Clustering / dendrograms | Similarity grouping and cluster discovery |
| `PcaStrategy` | PCA plots | Dimensionality reduction and sample separation |
| `RadarChartStrategy` | Radar charts | Multi-metric profiling |
| `UpSetStrategy` | UpSet plots | Set intersection analysis |
| `SankeyStrategy` | Sankey diagrams | Flow and transition visualization |
| `ChordStrategy` | Chord diagrams | Inter-group relationships |
| `NetworkStrategy` | Network graphs | Connectivity and interaction patterns |
| `SunburstStrategy` | Sunburst charts | Hierarchical composition |
| `TreemapStrategy` | Treemaps | Hierarchical part-to-whole analysis |
| `FrozensetStrategy` | Set-based utilities | Canonical set handling and deterministic grouping |


#### 4. Interactivity Section

Defines UI component interactions.

| Field | Required | Description |
|-------|----------|-------------|
| `triggers` | Yes | Components that trigger rendering |
| `outputs` | Yes | Components that receive output |
| `states` | No | Additional state dependencies |

**Trigger Types:**

- `accordion_open` — Render when accordion expands
- `button_click` — Render on button click
- `dropdown_selection` — Render on dropdown change
- `filter_change` — Update on filter modification

#### 5. Validation Section

Ensures data meets requirements before rendering.

| Rule | Purpose | Parameters |
|------|---------|------------|
| `not_empty` | Check data exists | — |
| `required_columns` | Check columns exist | `columns` |
| `no_nulls` | Check for null values | `columns` |
| `minimum_samples` | Check minimum row count | `min_count` |
| `minimum_databases` | Check database count | `min_count` |
| `numeric_scores` | Check numeric type | `column` |

#### 6. Performance Section

Controls caching and logging.

| Field | Description |
|-------|-------------|
| `cache.enabled` | Enable/disable caching |
| `cache.layers` | Cache layer definitions |
| `cache.layers[].ttl` | Time-to-live in seconds |
| `cache.layers[].key_template` | Cache key pattern |
| `cache.invalidation` | Invalidation triggers |
| `logging.enabled` | Enable performance logging |
| `logging.level` | Log verbosity |

#### 7. Error Handling Section

Defines error responses.

| Error Type | Action Options |
|------------|----------------|
| `missing_columns` | `display_message`, `display_placeholder` |
| `empty_dataframe` | `display_placeholder` |
| `processing_errors` | `log_and_notify`, `display_error_message` |

---

### Panel Configuration (`*_panel.yaml`)

Provides scientific context for users.

| Field | Required | Description |
|-------|----------|-------------|
| `use_case_id` | Yes | Identifier matching config file |
| `scientific_question` | Yes | Research question addressed |
| `description` | Yes | What the visualization shows |
| `visual_elements` | Yes | Explanation of chart elements |
| `interpretation_guidelines` | Yes | How to interpret results |
| `color_scheme` | Yes | Bootstrap color scheme |

---

## Aggregation Functions Reference

| Function | Description | Example Result |
|----------|-------------|----------------|
| `nunique` | Count unique values | 15 unique KOs |
| `count` | Count all occurrences | 150 total entries |
| `sum` | Sum numeric values | 1,250 total abundance |
| `mean` | Average of values | 0.75 mean score |
| `median` | Median of values | 0.68 median score |
| `min` | Minimum value | 0.1 minimum |
| `max` | Maximum value | 0.95 maximum |

---

## Color Scales Reference

| Scale | Use Case | Description |
|-------|----------|-------------|
| `Reds` | Toxicity | Intuitive danger gradient |
| `Blues` | General | Neutral gradient |
| `Viridis` | Scientific | Perceptually uniform, colorblind-friendly |
| `Plasma` | High contrast | Wide color range |
| `Greens` | Positive values | Growth, abundance |

---

## Layout Templates Reference

| Template | Description |
|----------|-------------|
| `simple_white` | Clean white background |
| `plotly_white` | Plotly white theme |
| `plotly_dark` | Dark theme |
| `ggplot2` | R ggplot2 style |
| `seaborn` | Seaborn style |

---

## Best Practices

1. **Version all configurations:** Include `version` field and track changes in version control

2. **Use descriptive identifiers:** Use case IDs should follow `UC-X.Y` pattern

3. **Document scientific context:** Panel files should explain interpretation to users

4. **Set appropriate cache TTL:** Balance freshness vs. performance

5. **Define comprehensive validation:** Catch data issues before rendering

6. **Use consistent naming:** Follow established patterns across modules

---

## Related Pages

- [YAML Configuration Overview](../config/yaml-configuration.md) — Quick configuration guide for deployment
- [Methods Overview](methods-overview.md) — High-level methodological framework
- [Data Sources](data-sources.md) — Database inventory and provenance
- [Mapping Strategy](mapping-strategy.md) — Technical mapping pipeline and join logic
- [Limitations and Scope Boundaries](limitations.md) — Interpretation constraints and usage restrictions
- [Use Cases Index](../use_cases/index.md) — Analytical use case catalog
- [Environment Variables](../config/environment-variables.md) — Runtime configuration for YAML processing
