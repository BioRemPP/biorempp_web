# User Guide Interactive Demo - Visual Structure

## Page Flow

```
User Guide Page (/help/user-guide or /user-guide)
│
├─── Header (Navigation)
│
├─── Page Title & Intro
│
├─── Quick Start Alert
│
├─── Section 1: What is BioRemPP?
│    ├─── Framework overview
│    └─── 8 Modules list
│
├─── Section 2: How to Perform Analysis (Workflow)
│    ├─── Step 1: Upload Data
│    ├─── Step 2: File Validation
│    ├─── Step 3: Process Data
│    ├─── Step 4: Processing Feedback
│    └─── Step 5: View Results
│
├─── ═══════════════════════════════════════════════
│    GREEN SEPARATOR (New Section)
│    ═══════════════════════════════════════════════
│
├─── Section 3: Interactive Module Demo ⭐ NEW
│    │
│    ├─── Section Header
│    │    ├─── Title: "Interactive Module Demo"
│    │    └─── Lead text explaining the demo
│    │
│    ├─── Explanation Cards (3 columns)
│    │    ├─── [1] Module Header (blue border)
│    │    ├─── [2] Use Case Description (green border)
│    │    └─── [3] Interactive Controls (yellow border)
│    │
│    ├─── Horizontal Rule
│    │
│    ├─── Module Description Component
│    │    ├─── Overview Card
│    │    │    ├─── Title: "Module 2 — Exploratory Analysis..."
│    │    │    └─── Overview text
│    │    │
│    │    └─── Guiding Questions Card
│    │         ├─── Header: "Guiding questions for the upcoming charts"
│    │         └─── 3 Columns Grid
│    │              ├─── [2.1] Sample performance
│    │              ├─── [2.2] Compound coverage
│    │              └─── [2.3] Distribution patterns
│    │
│    ├─── Horizontal Rule
│    │
│    └─── Use Case Demo Card
│         │
│         ├─── Card Header
│         │    ├─── Title: "UC-2.1: Ranking of Samples..."
│         │    └─── Download Button (dropdown, disabled)
│         │         └─── Badge: "Demo Only"
│         │
│         └─── Card Body
│              │
│              ├─── Info Panel (Collapsible) 🔽
│              │    ├─── Button: "View Use Case Description"
│              │    └─── Collapse Content
│              │         ├─── Scientific Question (green border)
│              │         ├─── Description (info section)
│              │         ├─── Visual Elements (primary section)
│              │         └─── Interpretation (warning section)
│              │
│              ├─── Demo Alert (blue)
│              │    └─── "This is a demonstration..."
│              │
│              └─── Accordion: "View Results" 🔽 (Open by default)
│                   │
│                   ├─── Database Selection
│                   │    ├─── Label: "Select Database:"
│                   │    ├─── Button Group
│                   │    │    ├─── [BioRemPP] (active)
│                   │    │    ├─── [HADEG] (outline)
│                   │    │    └─── [KEGG] (outline)
│                   │    └─── Description Alert
│                   │         └─── Current database description
│                   │
│                   ├─── Horizontal Rule
│                   │
│                   └─── Visualization Section
│                        ├─── Title: "Visualization"
│                        └─── Plotly Bar Chart
│                             ├─── Title: "Sample Ranking by KO Richness - [DB]"
│                             ├─── X-axis: Unique KO Count
│                             ├─── Y-axis: Samples (A, B, C, D, E)
│                             └─── Bars: Color-coded, sorted by count
│
├─── ═══════════════════════════════════════════════
│    GRAY SEPARATOR
│    ═══════════════════════════════════════════════
│
├─── Section 4: Tips & Best Practices
│    ├─── Data Preparation (left column)
│    └─── Troubleshooting (right column)
│
└─── Footer

```

## Component Hierarchy

```
create_interactive_demo_section()
│
├─── section_header (html.Div)
│    ├─── html.H2 (title with icon)
│    └─── html.P (lead text)
│
├─── explanation_cards (dbc.Row)
│    ├─── dbc.Col [Module Header card]
│    ├─── dbc.Col [Use Case Description card]
│    └─── dbc.Col [Interactive Controls card]
│
├─── html.Hr (separator)
│
├─── module_description (from create_demo_module_description)
│    ├─── overview_card (dbc.Card)
│    │    └─── dbc.CardBody
│    │         ├─── html.H4 (module title)
│    │         └─── html.P (overview text)
│    │
│    └─── questions_card (dbc.Card)
│         ├─── dbc.CardHeader
│         └─── dbc.CardBody
│              └─── dbc.Row (3 columns)
│                   ├─── dbc.Col (question 2.1)
│                   ├─── dbc.Col (question 2.2)
│                   └─── dbc.Col (question 2.3)
│
├─── html.Hr (separator)
│
└─── use_case_layout (from create_demo_use_case_layout)
     │
     ├─── dbc.CardHeader
     │    └─── dbc.Row
     │         ├─── dbc.Col (title)
     │         └─── dbc.Col (download + badge)
     │
     └─── dbc.CardBody
          │
          ├─── info_panel (from create_demo_use_case_panel)
          │    ├─── dbc.Button (toggle)
          │    └─── dbc.Collapse
          │         └─── dbc.Card
          │              └─── dbc.CardBody
          │                   ├─── Scientific Question
          │                   ├─── Description
          │                   ├─── Visual Elements
          │                   └─── Interpretation
          │
          ├─── dbc.Alert (demo notice)
          │
          └─── dbc.Accordion
               └─── dbc.AccordionItem
                    ├─── Database Selection
                    │    ├─── html.Label
                    │    ├─── dbc.ButtonGroup
                    │    └─── html.Div (description)
                    │
                    └─── Visualization
                         ├─── html.H6
                         └─── dcc.Graph (chart)
```

## Interactive Callbacks

```
Callback Flow Diagram:

[User Action] ──────────────────> [Callback] ──────────> [Output]

1. Panel Toggle:
   Click "View Use Case Description"
      └──> toggle_demo_collapse()
            └──> Update collapse visibility (show/hide)

2. Database Selection:
   Click [BioRemPP] / [HADEG] / [KEGG]
      └──> update_demo_database_selection()
            ├──> Update button outlines (active/inactive)
            ├──> Update database description text
            └──> Regenerate chart with new title
```

## Data Flow

```
YAML Config (demo_config.yaml)
      │
      ├──> load_demo_config()
      │
      ├──> create_demo_module_description(config)
      │     └──> module_description (html.Div)
      │
      ├──> create_demo_use_case_panel(config)
      │     └──> info_panel (html.Div)
      │
      └──> create_mock_bar_chart(config, db_name)
            └──> go.Figure (Plotly chart)

User Interaction
      │
      └──> Callback triggered
            │
            ├──> Load config (demo_config.yaml)
            │
            ├──> Process user input (button click)
            │
            └──> Update outputs (UI changes)
```

## File Dependencies

```
user_guide_page.py
      │
      └──> imports: uc_user_guide/__init__.py
                     │
                     ├──> demo_layout.py
                     │     ├──> demo_config.yaml
                     │     ├──> yaml
                     │     ├──> plotly.graph_objects
                     │     ├──> dash_bootstrap_components
                     │     └──> dash
                     │
                     └──> demo_callbacks.py
                           ├──> demo_config.yaml
                           ├──> demo_layout.create_mock_bar_chart()
                           └──> dash callbacks

biorempp_app.py
      │
      └──> imports: uc_user_guide.register_demo_callbacks
            │
            └──> Registers 2 callbacks with app instance
```

## Color Scheme

```
Components by Color:

🟢 GREEN (Success)
   - Module title icon
   - Section separator (top)
   - Panel button color
   - Scientific Question border
   - Download button

🔵 BLUE (Primary/Info)
   - Database buttons (active)
   - Visual Elements icon/section
   - Demo alert
   - Module Header explanation card

🟡 YELLOW (Warning)
   - Interpretation icon/section
   - Interactive Controls explanation card

🔴 RED (Danger)
   - Not used in demo (reserved for errors)

⚪ LIGHT/GRAY
   - Database description alert
   - Card shadows
   - Separators
```

## Responsive Breakpoints

```
Mobile (<768px):
   - Explanation cards: 1 column (stacked)
   - Guiding questions: 1 column (stacked)
   - Chart: Full width, smaller height

Tablet (768px - 1024px):
   - Explanation cards: 2 columns + 1 row
   - Guiding questions: 3 columns (may wrap)
   - Chart: Full width, medium height

Desktop (>1024px):
   - Explanation cards: 3 columns (side by side)
   - Guiding questions: 3 columns (side by side)
   - Chart: Full width, optimal height (400px)
```

## Component IDs Reference

```
Section Level:
   interactive-demo-section

Module Description:
   (no IDs - static component)

Use Case Demo:
   demo-guide-card                    # Main card
   demo-guide-info-panel              # Panel container
   demo-guide-collapse-button         # Toggle button
   demo-guide-collapse                # Collapsible content
   demo-guide-db-biorempp            # BioRemPP button
   demo-guide-db-hadeg               # HADEG button
   demo-guide-db-kegg                # KEGG button
   demo-guide-db-description         # Database description
   demo-guide-chart                  # Plotly graph
   demo-guide-accordion              # Results accordion
   demo-guide-item                   # Accordion item
```

This structure provides a complete, realistic, and educational demonstration of how BioRemPP modules work!
