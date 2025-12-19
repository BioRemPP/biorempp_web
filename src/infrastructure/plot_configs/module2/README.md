# Module 2: Plot Configurations

This directory contains modular configuration files for Module 2 use cases.

## Directory Structure

```
infrastructure/plot_configs/module2/
├── README.md                    # This file
├── uc_2_1_config.yaml          # UC-2.1: Plot configuration
├── uc_2_1_panel.yaml           # UC-2.1: Panel configuration
├── uc_2_2_config.yaml          # UC-2.2: Plot configuration
└── uc_2_2_panel.yaml           # UC-2.2: Panel configuration
```

## Configuration Architecture

Each use case has **TWO modular configuration files**:

### 1. Panel Configuration (`*_panel.yaml`)
**Purpose**: Defines the informative collapsible panel content

**Location**: `infrastructure/plot_configs/module2/uc_X_Y_panel.yaml`

**Content**:
- `use_case_id`: Unique identifier
- `scientific_question`: Main research question
- `description`: Detailed explanation
- `visual_elements`: UI component descriptions
- `interpretation_guidelines`: How to interpret results
- `color_scheme`: Bootstrap color theme

**Loaded by**: `presentation/components/base/use_case_panel.py`

**Example**: `uc_2_1_panel.yaml`
```yaml
use_case_id: "uc-2-1"
scientific_question: "How does ranking change..."
description: "This visualization..."
visual_elements:
  - label: "Y-axis"
    description: "Represents samples"
interpretation_guidelines:
  - "Comparative Ranking: ..."
color_scheme: "info"
```

### 2. Plot Configuration (`*_config.yaml`)
**Purpose**: Defines plot generation, data processing, and validation

**Location**: `infrastructure/plot_configs/module2/uc_X_Y_config.yaml`

**Content**:
- `metadata`: Use case metadata, tags, scientific context
- `data`: Source, required columns, processing steps
- `visualization`: Plotly settings, strategy, layout
- `ui`: Container IDs, buttons, rendering modes
- `filters`: Range sliders, dropdowns, dynamic configs
- `validation`: Data validation rules
- `performance`: Caching, logging configuration

**Loaded by**: `application/plot_services/plot_service.py`

**Example**: `uc_2_1_config.yaml`
```yaml
metadata:
  use_case_id: "UC-2.1"
  title: "Ranking by Functional Richness"
  plot_type: "bar_chart"

data:
  required_columns: ["Sample", "KO"]
  processing:
    steps:
      - name: "group_and_count"
        params:
          group_by: "Sample"
          agg_column: "KO"

visualization:
  strategy: "BarChartStrategy"
  plotly:
    chart_type: "bar"
    x: "Sample"
    y: "ko_count"
```

## Configuration Flow

```
┌─────────────────────────────────────────────────────┐
│                  User Interaction                    │
└───────────────────┬─────────────────────────────────┘
                    │
        ┌───────────┴──────────┐
        │                      │
        ▼                      ▼
┌──────────────┐      ┌──────────────┐
│ Panel Config │      │ Plot Config  │
│ *_panel.yaml │      │ *_config.yaml│
└──────┬───────┘      └──────┬───────┘
       │                     │
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│ use_case_    │      │ plot_service │
│ panel.py     │      │ .py          │
└──────┬───────┘      └──────┬───────┘
       │                     │
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│ Informative  │      │ Interactive  │
│ Panel        │      │ Visualization│
└──────────────┘      └──────────────┘
```

## Module 2 Use Cases

### UC-2.1: Ranking of Samples by KO Richness
**Files**:
- `uc_2_1_panel.yaml`: Panel description
- `uc_2_1_config.yaml`: Plot configuration

**Description**: Ranks samples by unique KO count across databases (BioRemPP, HADEG, KEGG)

**Key Features**:
- Database selector (3 options)
- Dynamic range slider
- Horizontal bar chart
- On-demand rendering

### UC-2.2: Ranking of Samples by Compound Richness
**Files**:
- `uc_2_2_panel.yaml`: Panel description
- `uc_2_2_config.yaml`: Plot configuration

**Description**: Ranks samples by unique compound count (BioRemPP, KEGG)

**Key Features**:
- Database selector (2 options)
- Dynamic range slider
- Horizontal bar chart with color scale
- Accordion-based rendering

## Naming Conventions

### File Naming
- **Panel Config**: `uc_X_Y_panel.yaml` (lowercase, underscores)
- **Plot Config**: `uc_X_Y_config.yaml` (lowercase, underscores)

### Use Case IDs
- **Panel**: `"uc-X-Y"` (lowercase, hyphens)
- **Plot**: `"UC-X.Y"` (uppercase, dots)

**Example**:
```yaml
# uc_2_1_panel.yaml
use_case_id: "uc-2-1"

# uc_2_1_config.yaml
metadata:
  use_case_id: "UC-2.1"
```

## Configuration Loading

### Panel Configuration
```python
# In: presentation/components/base/use_case_panel.py

def create_uc_2_1_panel() -> html.Div:
    config_path = (
        current_dir / "infrastructure" / "plot_configs" /
        "module2" / "uc_2_1_panel.yaml"
    )
    config = load_use_case_config(str(config_path))
    return create_use_case_panel(**config)
```

### Plot Configuration
```python
# In: application/plot_services/plot_config_loader.py

def load_config(use_case_id: str) -> dict:
    # Loads: infrastructure/plot_configs/module2/uc_2_1_config.yaml
    # Based on use_case_id "UC-2.1"
    return config
```

## Benefits of Modular Structure

### ✅ Co-location
- Panel and plot configs for same use case are together
- Easy to find and maintain related configurations

### ✅ Separation of Concerns
- `*_panel.yaml`: UI/content (what users see and read)
- `*_config.yaml`: Technical (how data is processed and plotted)

### ✅ Scalability
- Clear pattern for adding new use cases
- Consistent structure across modules
- No conflicts between panel and plot settings

### ✅ Maintainability
- Changes to panel content don't affect plot logic
- Changes to plot config don't affect panel display
- Independent versioning possible

## Adding a New Use Case

1. **Create panel config**: `uc_X_Y_panel.yaml`
   ```yaml
   use_case_id: "uc-X-Y"
   scientific_question: "..."
   description: "..."
   visual_elements: [...]
   interpretation_guidelines: [...]
   color_scheme: "info"
   ```

2. **Create plot config**: `uc_X_Y_config.yaml`
   ```yaml
   metadata:
     use_case_id: "UC-X.Y"
     title: "..."
   data:
     required_columns: [...]
     processing: {...}
   visualization: {...}
   filters: [...]
   validation: {...}
   performance: {...}
   ```

3. **Add panel function**: `use_case_panel.py`
   ```python
   def create_uc_X_Y_panel() -> html.Div:
       config_path = (
           current_dir / "infrastructure" / "plot_configs" /
           "moduleX" / "uc_X_Y_panel.yaml"
       )
       config = load_use_case_config(str(config_path))
       return create_use_case_panel(**config)
   ```

4. **Update layout**: Import and use in module layout

5. **Create callbacks**: Implement rendering logic

## Validation

Both configuration types are validated at load time:

### Panel Config Validation
- Required fields: `use_case_id`, `scientific_question`, `description`
- Optional fields: `visual_elements`, `interpretation_guidelines`, `color_scheme`
- YAML syntax validation

### Plot Config Validation
- Complete schema validation
- Required sections: `metadata`, `data`, `visualization`
- Column requirements checked
- Processing steps validated

## Performance

### Panel Configs
- Loaded once per page load
- Minimal memory footprint
- No caching needed (static content)

### Plot Configs
- Cached with TTL
- Automatic invalidation on changes
- Hot reload in development mode

## Migration from Old Structure

### Before (Fragmented)
```
configs/use_cases/
├── uc_2_1.yaml    # Panel only
└── uc_2_2.yaml    # Panel only

infrastructure/plot_configs/module2/
├── uc_2_1_config.yaml    # Plot only
└── uc_2_2_config.yaml    # Plot only
```

### After (Modular, Co-located)
```
infrastructure/plot_configs/module2/
├── uc_2_1_panel.yaml     # Panel config
├── uc_2_1_config.yaml    # Plot config
├── uc_2_2_panel.yaml     # Panel config
└── uc_2_2_config.yaml    # Plot config
```

**Benefits**:
- ✅ All UC-2.1 configs in one place
- ✅ All UC-2.2 configs in one place
- ✅ Clear naming convention with suffixes
- ✅ Easier to maintain and update

## Best Practices

### Panel Config (`*_panel.yaml`)
- ✅ Focus on user-facing content
- ✅ Use clear, accessible language
- ✅ Keep descriptions concise but informative
- ✅ Use YAML multiline strings (>) for long text
- ✅ Provide actionable interpretation guidelines

### Plot Config (`*_config.yaml`)
- ✅ Document all processing steps
- ✅ Include validation rules
- ✅ Enable caching for performance
- ✅ Use descriptive error messages
- ✅ Keep metadata complete and up-to-date

### General
- ✅ Use consistent naming: `uc_X_Y_panel.yaml` and `uc_X_Y_config.yaml`
- ✅ Version control both files together
- ✅ Test changes to both configs together
- ✅ Keep README updated with new use cases

## Troubleshooting

### Panel not displaying
1. Check file path in `use_case_panel.py`
2. Verify YAML syntax in `*_panel.yaml`
3. Check required fields exist
4. Review browser console for errors

### Plot not rendering
1. Check `use_case_id` matches between panel and plot configs
2. Verify `*_config.yaml` exists and is valid
3. Check data validation rules
4. Review application logs

### Configuration not loading
1. Verify file paths are correct
2. Check YAML syntax (indentation, quotes)
3. Ensure required sections exist
4. Clear cache and reload

## Support

For issues or questions:
1. Check this README
2. Review existing configs as examples
3. Validate YAML syntax
4. Check application logs for errors
5. Ensure both `*_panel.yaml` and `*_config.yaml` exist

