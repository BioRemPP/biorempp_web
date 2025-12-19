# UC User Guide - Interactive Module Demo

## Overview

This self-contained package provides an interactive demonstration of a BioRemPP module
for the User Guide page. It shows users exactly how the analysis interface works without
requiring real data processing.

## Package Structure

```
uc_user_guide/
├── demo_config.yaml        # Mock data and configuration
├── demo_layout.py          # Layout components and UI
├── demo_callbacks.py       # Interactive callbacks
├── __init__.py            # Package exports
└── README.md              # This file
```

## Features

### 1. Module Description Header
- Module overview card with title and context
- Guiding questions in responsive grid (3 columns)
- Follows real module2_layout pattern

### 2. Use Case Panel (Collapsible)
- Scientific question with blockquote styling
- Detailed description
- Visual elements guide
- Interpretation guidelines
- Color-coded sections (success/info/warning borders)

### 3. Interactive Controls
- **Database Selector**: Toggle between BioRemPP, HADEG, KEGG
- **Download Button**: Dropdown with CSV/Excel/JSON options (disabled for demo)
- **Accordion**: View Results section (starts open)

### 4. Mock Visualization
- Plotly bar chart with sample data
- 5 mock samples with varying KO counts
- Color-coded bars
- Updates dynamically when database changes
- Realistic styling matching real use cases

### 5. Explanatory Cards
- 3-column grid explaining each component
- Helps users understand the interface before using it

## Usage

### In User Guide Page

```python
from presentation.pages.uc_user_guide import create_interactive_demo_section

# Add to page layout
layout = html.Div([
    # ... other sections ...
    create_interactive_demo_section(),
    # ... more sections ...
])
```

### Registering Callbacks

```python
from presentation.pages.uc_user_guide import register_demo_callbacks

# In create_app() function
register_demo_callbacks(app)
```

## Component IDs

All component IDs use the prefix `demo-guide-` to avoid conflicts:

- `demo-guide-collapse`: Collapsible panel
- `demo-guide-collapse-button`: Toggle button
- `demo-guide-db-biorempp`: BioRemPP database button
- `demo-guide-db-hadeg`: HADEG database button
- `demo-guide-db-kegg`: KEGG database button
- `demo-guide-db-description`: Database description alert
- `demo-guide-chart`: Plotly chart component
- `demo-guide-accordion`: Results accordion
- `demo-guide-card`: Main card container

## Mock Data

The demo uses 5 sample datasets with realistic KO counts:

- **Sample_A**: 245 KOs (green)
- **Sample_B**: 189 KOs (blue)
- **Sample_C**: 312 KOs (pink)
- **Sample_D**: 156 KOs (orange)
- **Sample_E**: 278 KOs (purple)

## Callbacks

### 1. Toggle Panel Collapse
- **Inputs**: Button click (`demo-guide-collapse-button`)
- **Outputs**: Panel visibility (`demo-guide-collapse`)
- **Action**: Show/hide use case description

### 2. Database Selection
- **Inputs**: 3 database buttons (BioRemPP, HADEG, KEGG)
- **Outputs**: Button outlines, description text, chart figure
- **Action**: Update UI and regenerate chart with new title

## Integration Points

### biorempp_app.py
```python
from presentation.pages.uc_user_guide import register_demo_callbacks

# After other callback registrations
register_demo_callbacks(app)
```

### user_guide_page.py
```python
from .uc_user_guide import create_interactive_demo_section

# In create_user_guide_page()
layout = html.Div([
    # ... workflow section ...
    html.Hr(...),
    create_interactive_demo_section(),  # After Step 5
    html.Hr(...),
    # ... tips section ...
])
```

## Design Principles

1. **Self-Contained**: All code, configs, and callbacks in one package
2. **Realistic**: Mirrors real UC structure exactly
3. **Non-Interactive Downloads**: Download buttons disabled with "Demo Only" badge
4. **Educational**: Explanatory cards help users understand each component
5. **Responsive**: Uses Bootstrap grid for mobile/tablet/desktop compatibility

## File Descriptions

### demo_config.yaml
YAML configuration with:
- Module metadata (ID, title, overview)
- Guiding questions (3 questions)
- Panel information (scientific question, description, visual elements, interpretation)
- Mock sample data (5 samples with KO counts and colors)
- Database descriptions

### demo_layout.py
Layout functions:
- `load_demo_config()`: Load YAML configuration
- `create_demo_module_description()`: Module header with guiding questions
- `create_demo_use_case_panel()`: Collapsible informative panel
- `create_mock_bar_chart()`: Plotly bar chart generator
- `create_demo_use_case_layout()`: Complete UC card
- `create_interactive_demo_section()`: Main export (full demo section)

### demo_callbacks.py
Callback functions:
- `register_demo_callbacks(app)`: Main registration function
- `toggle_demo_collapse()`: Panel visibility callback
- `update_demo_database_selection()`: Database selector callback
- `_create_db_description()`: Helper for database alerts

### __init__.py
Exports:
- `create_interactive_demo_section`: Layout function
- `register_demo_callbacks`: Callback registration

## Styling

- Uses Bootstrap MINTY theme (from app)
- Font Awesome icons (fas fa-*)
- Shadow-sm for card elevation
- Border colors: primary, success, info, warning
- Responsive columns: md=4 for 3-column grid

## Future Enhancements

Potential additions:
- Range slider demonstration
- Multiple chart types (box plot, heatmap)
- Table component example
- Export functionality simulation
- Animated transitions

## Notes

- **No Real Data**: All data is mocked in YAML config
- **Callbacks Work**: Interactivity is fully functional
- **Isolated**: No dependencies on actual data stores or processing
- **Safe**: Cannot interfere with real use case functionality
- **Educational**: Primary purpose is user education, not analysis

## Author

BioRemPP Development Team
Date: 2025-12-05
Version: 1.0.0
