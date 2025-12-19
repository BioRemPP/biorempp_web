"""
UpSet Strategy - Set Intersection Visualizations.

This module implements the UpSetStrategy for creating UpSet plots to visualize
set intersections and unique contributions across multiple categorical sources.

Classes
-------
UpSetStrategy
    Strategy for creating UpSet plots showing set intersections.

Notes
-----
- Compares overlap between databases (e.g., BioRemPP, HADEG, KEGG)
- Analyzes distribution across regulatory agencies
- Identifies consensus evidence vs. source-specific coverage
- Uses upsetplot library for publication-quality visualizations

For supported use cases, refer to the official documentation.
"""

from typing import Any, Dict

import pandas as pd
import plotly.graph_objects as go
from upsetplot import UpSet, from_contents

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy
from src.shared.logging import get_logger

logger = get_logger(__name__)


class UpSetStrategy(BasePlotStrategy):
    """
    Strategy for creating UpSet plots showing set intersections.

    UpSet plots visualize overlap and uniqueness of elements across multiple
    categories through three components: set size bars, intersection matrix,
    and intersection size bars.

    Parameters
    ----------
    config : Dict[str, Any]
        Complete configuration from YAML file.

    Attributes
    ----------
    entity_column : str
        Column name for entities to compare.
    category_column : str
        Column name for categories/sources.
    sort_by : str
        Sorting method ('cardinality' or 'degree').
    show_counts : bool
        Whether to display counts on bars.
    show_percentages : bool
        Whether to display percentages.
    min_subset_size : int
        Minimum subset size to display.
    max_subset_rank : Optional[int]
        Maximum subset rank limit.

    Methods
    -------
    generate(data)
        Generate UpSet plot from data
    validate_data(df)
        Validate input data
    process_data(df)
        Process and transform data for visualization
    create_figure(processed_df)
        Create Plotly figure from processed data

    Notes
    -----
    - Uses upsetplot library (matplotlib) converted to Plotly format
    - Maintains consistency with application's visualization framework
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize strategy with configuration.

        Parameters
        ----------
        config : Dict[str, Any]
            Full configuration dictionary from YAML.
        """
        super().__init__(config)

        # Extract plotly configuration from viz_config
        self.plotly_config = self.viz_config.get("plotly", {})

        # Extract UpSet-specific configuration
        plotly_config = self.plotly_config or {}

        # Required columns
        self.entity_column = plotly_config.get("entity_column")
        self.category_column = plotly_config.get("category_column")

        if not self.entity_column:
            raise ValueError("UpSetStrategy requires 'entity_column' in config")
        if not self.category_column:
            raise ValueError("UpSetStrategy requires 'category_column' in config")

        # Optional UpSet parameters
        self.sort_by = plotly_config.get("sort_by", "cardinality")
        self.show_counts = plotly_config.get("show_counts", True)
        self.show_percentages = plotly_config.get("show_percentages", False)
        self.min_subset_size = plotly_config.get("min_subset_size", 0)
        self.max_subset_rank = plotly_config.get("max_subset_rank", None)

        # Figure dimensions
        self.fig_width = plotly_config.get("fig_width", 14)
        self.fig_height = plotly_config.get("fig_height", 8)

        # Color scheme
        self.bar_color = plotly_config.get("bar_color", "#0d6efd")

        # Layout configuration
        self.layout_config = plotly_config.get("layout", {})

        logger.debug(
            f"UpSetStrategy initialized: "
            f"entity='{self.entity_column}', "
            f"category='{self.category_column}', "
            f"sort_by='{self.sort_by}'"
        )

    def generate(self, data: pd.DataFrame) -> go.Figure:
        """
        Generate UpSet plot from data.

        Validates data, cleans it, builds category sets, creates UpSet plot,
        and converts to Plotly format.

        Parameters
        ----------
        data : pd.DataFrame
            DataFrame containing entity and category columns.

        Returns
        -------
        go.Figure
            Plotly figure object containing the UpSet visualization.

        Raises
        ------
        ValueError
            If data is empty or required columns are missing.
        """
        logger.info(
            "Generating UpSet plot",
            extra={
                "entity_col": self.entity_column,
                "category_col": self.category_column,
                "rows": len(data),
            },
        )

        # Validate data
        self._validate_data(data)

        # Clean and prepare data
        df_clean = self._clean_data(data)

        # Build sets for each category
        category_sets = self._build_category_sets(df_clean)

        # Generate UpSet data structure
        upset_data = from_contents(category_sets)

        # Create UpSet plot (matplotlib)
        upset_plot = self._create_upset_plot(upset_data)

        # Convert to Plotly
        fig = self._convert_to_plotly(upset_plot, category_sets)

        # Apply layout
        self._apply_layout(fig)

        logger.info(
            "UpSet plot generated successfully",
            extra={
                "categories": len(category_sets),
                "total_intersections": len(upset_data),
            },
        )

        return fig

    def _validate_data(self, data: pd.DataFrame) -> None:
        """
        Validate input data structure.

        Parameters
        ----------
        data : pd.DataFrame
            Input dataframe to validate.

        Raises
        ------
        ValueError
            If data is empty or required columns are missing.
        """
        if data.empty:
            raise ValueError("Cannot create UpSet plot: DataFrame is empty")

        # Check entity column
        if self.entity_column not in data.columns:
            raise ValueError(
                f"Column '{self.entity_column}' not found in data. "
                f"Available columns: {list(data.columns)}"
            )

        # Check category column
        if self.category_column not in data.columns:
            raise ValueError(
                f"Column '{self.category_column}' not found in data. "
                f"Available columns: {list(data.columns)}"
            )

        logger.debug("Data validation passed")

    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize data for UpSet analysis.

        Parameters
        ----------
        data : pd.DataFrame
            Raw input data.

        Returns
        -------
        pd.DataFrame
            Cleaned dataframe with:
            - No null values in required columns
            - Stripped whitespace
            - No empty strings

        Notes
        -----
        Cleaning steps:
        1. Drop rows with null values in entity/category columns
        2. Strip whitespace from string columns
        3. Filter out empty strings
        4. Remove duplicate entity-category pairs
        """
        df = data.copy()

        # Drop nulls
        df.dropna(subset=[self.entity_column, self.category_column], inplace=True)

        # Strip whitespace
        if df[self.entity_column].dtype == "object":
            df[self.entity_column] = df[self.entity_column].str.strip()

        if df[self.category_column].dtype == "object":
            df[self.category_column] = df[self.category_column].str.strip()

        # Filter out empties
        df = df.query(f"{self.entity_column} != '' and {self.category_column} != ''")

        if df.empty:
            raise ValueError(
                "No valid data after cleaning. "
                f"Check '{self.entity_column}' and "
                f"'{self.category_column}' columns."
            )

        # Remove duplicates
        df = df[[self.entity_column, self.category_column]].drop_duplicates()

        logger.debug(f"Data cleaned: {len(df)} unique entity-category pairs")

        return df

    def _build_category_sets(self, data: pd.DataFrame) -> Dict[str, set]:
        """
        Build sets of unique entities for each category.

        Parameters
        ----------
        data : pd.DataFrame
            Cleaned dataframe.

        Returns
        -------
        Dict[str, set]
            Dictionary mapping category names to sets of unique entities.
            Example: {'BioRemPP': {'K00001', 'K00002'},
                     'KEGG': {'K00001', 'K00003'}}

        Notes
        -----
        This method groups data by category column and creates a set of
        unique entities for each group. This is the core data structure
        required by upsetplot.from_contents().
        """
        category_sets = (
            data.groupby(self.category_column)[self.entity_column].apply(set).to_dict()
        )

        if not category_sets:
            raise ValueError(f"Could not build sets from '{self.category_column}'")

        # Log statistics
        logger.info(f"Built sets for {len(category_sets)} categories:")
        for category, entities in category_sets.items():
            logger.info(f"  - {category}: {len(entities)} unique entities")

        return category_sets

    def _create_upset_plot(self, upset_data) -> UpSet:
        """
        Create UpSet plot object using upsetplot library.

        Parameters
        ----------
        upset_data
            UpSet data structure from from_contents().

        Returns
        -------
        UpSet
            Configured UpSet plot object.

        Notes
        -----
        The UpSet object is configured with:
        - Sorting method (cardinality or degree)
        - Count display toggle
        - Percentage display toggle
        - Minimum subset size filter
        - Maximum subset rank limit
        """
        upset = UpSet(
            upset_data,
            sort_by=self.sort_by,
            show_counts=self.show_counts,
            show_percentages=self.show_percentages,
            min_subset_size=self.min_subset_size,
            max_subset_rank=self.max_subset_rank,
        )

        logger.debug(
            f"UpSet plot configured: "
            f"sort_by={self.sort_by}, "
            f"show_counts={self.show_counts}"
        )

        return upset

    def _convert_to_plotly(
        self, upset_plot: UpSet, category_sets: Dict[str, set]
    ) -> go.Figure:
        """
        Convert matplotlib UpSet plot to Plotly format.

        Parameters
        ----------
        upset_plot : UpSet
            Configured UpSet plot object.
        category_sets : Dict[str, set]
            Category sets for metadata.

        Returns
        -------
        go.Figure
            Plotly figure with UpSet visualization.

        Notes
        -----
        Since upsetplot generates matplotlib figures, this method creates
        a Plotly wrapper that displays the matplotlib figure as an image.
        This maintains consistency with the application's visualization
        framework while leveraging the specialized UpSet library.

        Future Enhancement:
        Could implement pure Plotly version using subplots for more
        interactivity, but matplotlib version is publication-quality.
        """
        import matplotlib

        matplotlib.use("Agg")  # Use non-interactive backend (no Tkinter)
        import base64
        import io

        import matplotlib.pyplot as plt

        # Create matplotlib figure
        plt.figure(figsize=(self.fig_width, self.fig_height))
        upset_plot.plot()

        # Convert to image
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        plt.close()

        # Create Plotly figure with image
        fig = go.Figure()

        fig.add_layout_image(
            dict(
                source=f"data:image/png;base64,{img_base64}",
                xref="paper",
                yref="paper",
                x=0,
                y=1,
                sizex=1,
                sizey=1,
                sizing="stretch",
                layer="below",
            )
        )

        # Add metadata as annotation
        annotation_text = self._build_annotation_text(category_sets)

        fig.add_annotation(
            text=annotation_text,
            xref="paper",
            yref="paper",
            x=0.5,
            y=-0.1,
            showarrow=False,
            font=dict(size=10, color="gray"),
            align="center",
        )

        logger.debug("Converted UpSet plot to Plotly format")

        return fig

    def _build_annotation_text(self, category_sets: Dict[str, set]) -> str:
        """
        Build annotation text with set statistics.

        Parameters
        ----------
        category_sets : Dict[str, set]
            Category sets.

        Returns
        -------
        str
            Formatted annotation text.
        """
        lines = ["<b>Set Sizes:</b>"]
        for category, entities in sorted(
            category_sets.items(), key=lambda x: len(x[1]), reverse=True
        ):
            lines.append(f"{category}: {len(entities)}")

        return " | ".join(lines)

    def _apply_layout(self, fig: go.Figure) -> None:
        """
        Apply layout configuration to figure.

        Parameters
        ----------
        fig : go.Figure
            Figure to apply layout to.

        Notes
        -----
        Layout customizations:
        - Remove axes (image-based plot)
        - Set transparent background
        - Configure margins
        - Apply title from config
        """
        layout_config = self.layout_config or {}

        fig.update_layout(
            # Hide axes (image plot)
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            # Transparent background
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            # Margins
            margin=dict(
                l=layout_config.get("margin_left", 20),
                r=layout_config.get("margin_right", 20),
                t=layout_config.get("margin_top", 60),
                b=layout_config.get("margin_bottom", 80),
            ),
            # Title
            title=dict(
                text=layout_config.get("title", ""),
                x=0.5,
                xanchor="center",
                font=dict(
                    size=layout_config.get("title_size", 16),
                    color=layout_config.get("title_color", "#333"),
                ),
            ),
            # Size
            height=layout_config.get("height", 600),
        )

        # Only set width if not using autosize
        if not layout_config.get("autosize", False):
            fig.update_layout(width=layout_config.get("width", 1000))

        logger.debug("Layout applied to UpSet plot")

    # ========================================================================
    # Abstract Methods Implementation (Required by BasePlotStrategy)
    # ========================================================================

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data (required by BasePlotStrategy).

        This method wraps the internal _validate_data method to comply
        with the abstract base class interface.

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate.

        Raises
        ------
        ValueError
            If validation fails.
        """
        self._validate_data(df)

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process and transform data for visualization.

        This method cleans the data and builds category sets, then
        returns the cleaned DataFrame ready for visualization.

        Parameters
        ----------
        df : pd.DataFrame
            Input data.

        Returns
        -------
        pd.DataFrame
            Processed data ready for visualization.
        """
        # Clean data
        df_clean = self._clean_data(df)

        # Store category sets for use in create_figure
        self._category_sets = self._build_category_sets(df_clean)

        return df_clean

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create Plotly figure from processed data.

        This method generates the UpSet plot using the previously
        built category sets.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Processed data (not directly used, category sets are used).

        Returns
        -------
        go.Figure
            Configured Plotly figure with UpSet visualization.
        """
        # Generate UpSet data structure
        upset_data = from_contents(self._category_sets)

        # Create UpSet plot (matplotlib)
        upset_plot = self._create_upset_plot(upset_data)

        # Convert to Plotly
        fig = self._convert_to_plotly(upset_plot, self._category_sets)

        # Apply layout
        self._apply_layout(fig)

        return fig
