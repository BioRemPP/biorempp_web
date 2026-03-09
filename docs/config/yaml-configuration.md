# Declarative YAML Configuration

BioRemPP Web Service uses **declarative YAML configuration** to define analytical use cases and visualization behavior. Each use case is specified through configuration files that control data processing, visualization rendering, and scientific context—without requiring code changes.

This approach enables reproducible configuration states that can be versioned alongside analytical results.

---

## Scope

**This page covers:**

- The role of YAML as the declarative layer for analytical use cases
- File structure and naming conventions
- Key configuration sections and their purpose
- Parameter examples for common use case types

---

## Configuration File Structure

Each analytical use case requires **two configuration files**:

```
src/infrastructure/plot_configs/moduleX/
├── uc_X_Y_config.yaml    # Plot configuration (visualization + data processing)
└── uc_X_Y_panel.yaml     # Panel configuration (scientific context)
```

| File Type | Purpose | Content |
|-----------|---------|---------|
| `*_config.yaml` | Defines how to generate the visualization | Data source, processing steps, chart settings, caching |
| `*_panel.yaml` | Defines scientific context for users | Scientific question, interpretation guidelines, visual elements |

---

## Key Configuration Sections

### 1. Metadata

Identifies the use case and provides context for maintenance.

```yaml
metadata:
  use_case_id: "UC-2.1"
  module: "module2"
  title: "Ranking of Samples by Functional Richness"
  version: "1.0.0"
  plot_type: "bar_chart"
  scientific_context:
    domain: "Functional Genomics"
    application: "Comparative metagenomics"
```

### 2. Data Configuration

Specifies data source and processing pipeline.

```yaml
data:
  source: "biorempp-merged-data"
  source_type: "store"
  
  required_columns:
    - "Sample"
    - "KO"
  
  processing:
    steps:
      - name: "group_and_count"
        enabled: true
        params:
          group_by: "Sample"
          agg_column: "KO"
          agg_function: "nunique"
          result_column: "ko_count"
      
      - name: "sort"
        enabled: true
        params:
          by: "ko_count"
          ascending: false
```

### 3. Visualization Configuration

Controls chart rendering via Plotly.

```yaml
visualization:
  strategy: "BarChartStrategy"
  
  plotly:
    chart_type: "bar"
    x: "Sample"
    y: "ko_count"
    orientation: "v"
    color_discrete_sequence: ["mediumseagreen"]
    
    layout:
      height: 500
      template: "simple_white"
      xaxis:
        tickangle: -45
```

### 4. Validation Rules

Ensures data meets requirements before rendering.

```yaml
validation:
  rules:
    - rule: "not_empty"
      message: "Input data cannot be empty"
    
    - rule: "required_columns"
      columns: ["Sample", "KO"]
      message: "Data must contain 'Sample' and 'KO' columns"
    
    - rule: "minimum_samples"
      min_count: 1
      message: "At least 1 sample required"
```

### 5. Performance Configuration

Controls caching behavior.

```yaml
performance:
  cache:
    enabled: true
    layers:
      - layer: "dataframe"
        ttl: 7200
        key_template: "uc_2_1_df_{data_hash}"
      
      - layer: "graph"
        ttl: 3600
        key_template: "uc_2_1_fig_{data_hash}_{filters_hash}"
```

---

## Examples

### Minimal Bar Chart Configuration

```yaml
metadata:
  use_case_id: "UC-2.1"
  module: "module2"
  title: "Sample Richness"
  plot_type: "bar_chart"

data:
  source: "biorempp-merged-data"
  source_type: "store"
  required_columns: ["Sample", "KO"]
  processing:
    steps:
      - name: "group_and_count"
        enabled: true
        params:
          group_by: "Sample"
          agg_column: "KO"
          agg_function: "nunique"
          result_column: "ko_count"

visualization:
  strategy: "BarChartStrategy"
  plotly:
    chart_type: "bar"
    x: "Sample"
    y: "ko_count"
    layout:
      height: 500
      template: "simple_white"
```

### Panel Configuration Example

```yaml
use_case_id: "uc-2-1"

scientific_question: >
  How many unique genes are present in each sample?

description: >
  Bar chart showing samples ranked by unique KO count.

visual_elements:
  - label: "X-axis"
    description: "Sample identifiers"
  - label: "Y-axis"
    description: "Count of unique KO identifiers"

interpretation_guidelines:
  - >
    Higher KO counts suggest greater functional diversity.

color_scheme: "info"
```

---

## Common Pitfalls

1. **Missing required columns:** Ensure `required_columns` matches actual data column names

2. **Wrong data source:** Each database has a specific store ID; using the wrong one causes empty results

3. **Processing step order:** Steps execute sequentially; aggregation must come before sorting

4. **Cache key collisions:** Use unique `key_template` patterns per use case to avoid stale cache

5. **Strategy mismatch:** The `strategy` must match the `plot_type` (e.g., `BarChartStrategy` for `bar_chart`)

---

## See Also

- [Use Case YAML Methodology](../methods/use-case-yaml.md) — Complete schema reference with all fields
- [Environment Variables](environment-variables.md) — Runtime configuration
- [Logging Configuration](logging.md) — Log profiles and verbosity settings
- [Gunicorn Configuration](gunicorn.md) — Production WSGI server settings
- [Docker Integration](docker-integration.md) — Container deployment configuration
