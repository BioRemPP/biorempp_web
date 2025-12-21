# Plot Strategies

Domain Layer - Plot Strategies Package.

Plot Strategies implement different visualization algorithms using the Strategy Pattern.
Each strategy encapsulates a specific plotting approach, making the system extensible.

## Architecture

The Plot Strategies follow these principles:

- **Strategy Pattern**: Each plot type is a separate strategy
- **Template Method**: Base class defines the execution flow
- **Single Responsibility**: Each strategy handles one visualization type
- **Open/Closed**: Easy to add new strategies without modifying existing code
- **Dependency Inversion**: Strategies depend on abstractions, not concrete implementations

## Package Structure

- **[Base](plot_strategies_base.md)**: Abstract base class for all strategies
- **[Charts](plot_strategies_charts.md)**: Concrete chart implementations (19 strategies)

## Available Strategies

### Chart Strategies (19 total)

- Bar Chart
- Box Scatter
- Chord Diagram
- Correlogram
- Density Plot
- Dot Plot
- Faceted Heatmap
- Frozenset
- Heatmap
- Heatmap Scored
- Hierarchical Clustering
- Network
- PCA (Principal Component Analysis)
- Radar Chart
- Sankey Diagram
- Stacked Bar Chart
- Sunburst
- Treemap
- UpSet Plot

## Usage Pattern

All strategies:

1. Inherit from `BasePlotStrategy`
2. Implement the `create_plot()` method
3. Return a Plotly figure object
4. Handle their own data validation

## Design Benefits

- **Extensibility**: New plot types easily added
- **Testability**: Each strategy independently testable
- **Maintainability**: Changes isolated to specific strategies
- **Flexibility**: Strategies can be swapped at runtime
    options:
      show_source: true
      heading_level: 3

---

