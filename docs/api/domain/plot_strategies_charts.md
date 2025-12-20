# Chart Strategies

Concrete implementations of chart visualization strategies.

All chart strategies inherit from `BasePlotStrategy` and implement
the `create_plot()` method to generate specific visualization types.

## Available Charts

This package contains 19 different chart strategy implementations:

- **[Bar Chart](plot_strategies/charts/bar_chart_strategy.md)**: Standard bar chart visualization
- **[Box Scatter](plot_strategies/charts/box_scatter_strategy.md)**: Combined box and scatter plot
- **[Chord Diagram](plot_strategies/charts/chord_strategy.md)**: Circular relationship visualization
- **[Correlogram](plot_strategies/charts/correlogram_strategy.md)**: Correlation matrix heatmap
- **[Density Plot](plot_strategies/charts/density_plot_strategy.md)**: Probability density estimation
- **[Dot Plot](plot_strategies/charts/dot_plot_strategy.md)**: Simple dot visualization
- **[Faceted Heatmap](plot_strategies/charts/faceted_heatmap_strategy.md)**: Multi-panel heatmap
- **[Frozenset](plot_strategies/charts/frozenset_strategy.md)**: Set intersection visualization
- **[Heatmap](plot_strategies/charts/heatmap_strategy.md)**: Standard heatmap
- **[Heatmap Scored](plot_strategies/charts/heatmap_scored_strategy.md)**: Scored heatmap with annotations
- **[Hierarchical Clustering](plot_strategies/charts/hierarchical_clustering_strategy.md)**: Dendrogram and heatmap
- **[Network](plot_strategies/charts/network_strategy.md)**: Graph network visualization
- **[PCA](plot_strategies/charts/pca_strategy.md)**: Principal Component Analysis plot
- **[Radar Chart](plot_strategies/charts/radar_chart_strategy.md)**: Multi-variable comparison
- **[Sankey Diagram](plot_strategies/charts/sankey_strategy.md)**: Flow diagram
- **[Stacked Bar Chart](plot_strategies/charts/stacked_bar_chart_strategy.md)**: Stacked bar visualization
- **[Sunburst](plot_strategies/charts/sunburst_strategy.md)**: Hierarchical sunburst chart
- **[Treemap](plot_strategies/charts/treemap_strategy.md)**: Hierarchical treemap
- **[UpSet Plot](plot_strategies/charts/upset_strategy.md)**: Set intersection matrix

## Strategy Pattern

Each chart strategy:

1. Inherits from `BasePlotStrategy`
2. Implements the `create_plot()` method
3. Returns a Plotly figure object
4. Handles its own data validation and transformation

This design makes it easy to add new visualization types without modifying existing code.
