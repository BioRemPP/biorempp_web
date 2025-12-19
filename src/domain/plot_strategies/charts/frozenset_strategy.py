"""
Frozenset Strategy - Minimal Sample-Group Visualization.

This module implements the FrozensetStrategy for creating grouped scatter plots
that visualize samples organized by their compound profiles (frozenset) with
set cover minimization to reduce redundancy.

Classes
-------
FrozensetStrategy
    Strategy for frozenset-based sample grouping visualization.

Notes
-----
- Groups samples by compound profile (frozenset)
- Applies greedy set cover algorithm for minimization
- Color-codes markers by unique KO count per compound

For supported use cases, refer to the official documentation.
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


# Default configuration
DEFAULT_COLOR_SCALE = "Greens"
DEFAULT_MARKER_SIZE = 10
DEFAULT_CHART_HEIGHT = 600
DEFAULT_CHART_WIDTH = 900
DEFAULT_TEMPLATE = "simple_white"


class FrozensetStrategy(BasePlotStrategy):
    """
    Strategy for minimal sample-group visualization using frozensets.

    This strategy creates grouped scatter plots showing samples organized by
    their compound profiles (frozenset), with set cover minimization to reduce
    redundancy and maximize compound coverage.

    Parameters
    ----------
    config : Dict[str, Any]
        Complete configuration from YAML file.

    Attributes
    ----------
    data_config : Dict[str, Any]
        Data processing configuration.
    plotly_config : Dict[str, Any]
        Plotly-specific configuration.
    sample_column : str
        Column name for sample identifiers.
    compound_column : str
        Column name for compound identifiers.
    compoundclass_column : str
        Column name for compound class filtering.
    ko_column : str
        Column name for KO identifiers (for color scaling).
    color_scale : str
        Plotly color scale for markers.
    marker_size : int
        Size of scatter markers.

    Methods
    -------
    validate_data(df)
        Validate input data for frozenset visualization requirements
    process_data(df)
        Process data with filtering, grouping, and set cover minimization
    create_figure(processed_df)
        Create frozenset visualization figure from processed data
    apply_filters(df, filters)
        Apply filters including compound class selection
    get_available_compound_classes(df)
        Get list of available compound classes
    get_group_statistics(processed_df)
        Calculate statistics for visualization

    Notes
    -----
    - Applies greedy set cover algorithm for group minimization
    - Color-codes by unique KO count per compound
    - Supports compound class filtering
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize strategy with configuration.

        Parameters
        ----------
        config : Dict[str, Any]
            Complete configuration from YAML file.
        """
        super().__init__(config)
        self.data_config = config.get("data", {})
        self.plotly_config = self.viz_config.get("plotly", {})

        # Column configuration
        self.sample_column: str = self.plotly_config.get("sample_column", "sample")
        self.compound_column: str = self.plotly_config.get(
            "compound_column", "compoundname"
        )
        self.compoundclass_column: str = self.plotly_config.get(
            "compoundclass_column", "compoundclass"
        )
        self.ko_column: str = self.plotly_config.get("ko_column", "ko")

        # Visual configuration
        self.color_scale: str = self.plotly_config.get(
            "color_scale", DEFAULT_COLOR_SCALE
        )
        self.marker_size: int = self.plotly_config.get(
            "marker_size", DEFAULT_MARKER_SIZE
        )

        # Selected compound class (set via filters)
        self._selected_compoundclass: Optional[str] = None

        # Internal state for processed data
        self._grouped_df: Optional[pd.DataFrame] = None
        self._minimized_groups: List[str] = []
        self._ko_counts: Optional[pd.Series] = None

        logger.info(
            f"FrozensetStrategy initialized for "
            f"{self.metadata.get('use_case_id', 'unknown')}: "
            f"sample='{self.sample_column}', "
            f"compound='{self.compound_column}', "
            f"compoundclass='{self.compoundclass_column}'"
        )

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for frozenset visualization requirements.

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate.

        Raises
        ------
        ValueError
            If DataFrame is empty or required columns missing.
        """
        logger.debug(
            f"Validating data - Shape: {df.shape}, " f"Columns: {df.columns.tolist()}"
        )

        if df.empty:
            raise ValueError("Input DataFrame is empty")

        # Validate required columns exist
        required_cols = [
            self.sample_column,
            self.compound_column,
            self.compoundclass_column,
        ]

        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            raise ValueError(
                f"Missing required columns: {missing_cols}. "
                f"Available: {df.columns.tolist()}"
            )

        # KO column is optional but recommended for color scaling
        if self.ko_column and self.ko_column not in df.columns:
            logger.warning(
                f"KO column '{self.ko_column}' not found. "
                f"Color scaling will use default values."
            )

        logger.info(f"Data validation passed - {len(df)} records")

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data for frozenset visualization.

        Applies filtering by compound class, groups samples by compound profile
        (frozenset), applies set cover minimization, and calculates KO counts.

        Parameters
        ----------
        df : pd.DataFrame
            Input data with required columns.

        Returns
        -------
        pd.DataFrame
            Processed data with group labels and KO counts.
        """
        logger.info("Processing frozenset data...")

        # Clean data
        df_clean = df.dropna(
            subset=[self.sample_column, self.compound_column, self.compoundclass_column]
        ).copy()

        if df_clean.empty:
            raise ValueError("No valid data after removing nulls")

        # Get compound classes available
        compound_classes = df_clean[self.compoundclass_column].unique().tolist()
        logger.info(f"Available compound classes: {len(compound_classes)}")

        # If no compound class selected, use first one
        if not self._selected_compoundclass:
            self._selected_compoundclass = compound_classes[0]
            logger.info(
                f"No compound class selected, using: "
                f"'{self._selected_compoundclass}'"
            )

        # Filter by selected compound class
        df_filtered = df_clean[
            df_clean[self.compoundclass_column] == self._selected_compoundclass
        ].copy()

        if df_filtered.empty:
            raise ValueError(
                f"No data for compound class: {self._selected_compoundclass}"
            )

        logger.info(
            f"Filtered to {len(df_filtered)} rows for class "
            f"'{self._selected_compoundclass}'"
        )

        # Step 1: Group samples by compound profile (frozenset)
        self._grouped_df = self._group_by_compound_profile(df_filtered)

        if self._grouped_df.empty:
            raise ValueError("No groups found after grouping by compound profile")

        # Step 2: Minimize groups using set cover
        self._minimized_groups = self._minimize_groups(self._grouped_df)

        if not self._minimized_groups:
            raise ValueError("No minimized groups found")

        # Filter to minimized groups only
        final_df = self._grouped_df[
            self._grouped_df["_group"].isin(self._minimized_groups)
        ].copy()

        # Step 3: Calculate KO counts per compound (for color)
        self._ko_counts = self._calculate_ko_counts(df_clean, df_filtered)

        # Merge KO counts into final dataframe
        if self._ko_counts is not None:
            final_df = final_df.merge(
                self._ko_counts,
                left_on=self.compound_column,
                right_index=True,
                how="left",
            )
            final_df["_unique_ko_count"] = (
                final_df["_unique_ko_count"].fillna(0).astype(int)
            )
        else:
            final_df["_unique_ko_count"] = 1

        logger.info(
            f"Processing complete: {len(final_df)} rows, "
            f"{len(self._minimized_groups)} minimized groups"
        )

        return final_df

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create frozenset visualization figure from processed data.

        Creates subplots with one scatter plot per minimized group, with
        markers color-coded by unique KO count.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Processed data with group labels and KO counts.

        Returns
        -------
        go.Figure
            Configured Plotly figure with subplots.
        """
        logger.debug("Creating frozenset visualization figure...")

        chart_config = self.plotly_config.get("chart", {})
        layout_config = self.plotly_config.get("layout", {})

        # Get unique groups (sorted)
        unique_groups = sorted(processed_df["_group"].unique())
        n_groups = len(unique_groups)

        if n_groups == 0:
            raise ValueError("No groups to visualize")

        # Get horizontal spacing
        horizontal_spacing = chart_config.get("horizontal_spacing", 0.03)

        # Create subplots
        fig = make_subplots(
            rows=1,
            cols=n_groups,
            shared_yaxes=True,
            subplot_titles=unique_groups,
            horizontal_spacing=horizontal_spacing,
        )

        # Get color range
        cmin = int(processed_df["_unique_ko_count"].min())
        cmax = int(processed_df["_unique_ko_count"].max())
        if cmin == cmax and cmax == 0:
            cmax = 1  # Avoid colorbar range [0, 0]

        # Get colorbar configuration
        colorbar_title = chart_config.get("colorbar_title", "Unique<br>KO Count")

        # Add traces for each group
        for i, group in enumerate(unique_groups, 1):
            group_df = processed_df[processed_df["_group"] == group]

            fig.add_trace(
                go.Scatter(
                    x=group_df[self.sample_column],
                    y=group_df[self.compound_column],
                    mode="markers",
                    name=str(group),
                    showlegend=False,
                    marker=dict(
                        size=self.marker_size,
                        color=group_df["_unique_ko_count"],
                        colorscale=self.color_scale,
                        cmin=cmin,
                        cmax=cmax,
                        showscale=(i == 1),  # Show colorbar only on first
                        colorbar=dict(title=colorbar_title, thickness=15, len=0.8),
                    ),
                    customdata=group_df[["_unique_ko_count"]].values,
                    hovertemplate=(
                        f"Sample: %{{x}}<br>"
                        f"Compound: %{{y}}<br>"
                        f"Unique KOs: %{{customdata[0]}}<extra></extra>"
                    ),
                ),
                row=1,
                col=i,
            )

        # Handle title configuration (support both string and dict)
        title_config = chart_config.get("title", {})
        if isinstance(title_config, str):
            # Backward compatibility: string title
            show_title = True
            title_text = title_config
            title_font_size = 16
        else:
            # New format: dict with show, text, font_size
            show_title = title_config.get("show", True)
            title_text = (
                title_config.get(
                    "text",
                    f"Minimal Sample-Group Visualization: {self._selected_compoundclass}",
                )
                if show_title
                else ""
            )
            title_font_size = title_config.get("font_size", 16)

        # Get layout options
        height = layout_config.get("height", DEFAULT_CHART_HEIGHT)
        use_autosize = layout_config.get("autosize", False)
        template = layout_config.get("template", DEFAULT_TEMPLATE)

        # Get margin configuration
        margin_config = layout_config.get("margin", {})
        margin = dict(
            l=margin_config.get("l", 150),
            r=margin_config.get("r", 50),
            t=margin_config.get("t", 80),
            b=margin_config.get("b", 50),
        )

        # Build layout update dict
        layout_update = {
            "title": dict(
                text=title_text,
                x=0.5,
                xanchor="center",
                font=dict(size=title_font_size),
            ),
            "template": template,
            "height": height,
            "margin": margin,
            "paper_bgcolor": "white",
        }

        # Add autosize or width
        if use_autosize:
            layout_update["autosize"] = True
        else:
            if layout_config.get("width"):
                layout_update["width"] = layout_config.get("width", DEFAULT_CHART_WIDTH)

        fig.update_layout(**layout_update)

        # Update X-axes: rotation and title
        xaxis_tickangle = chart_config.get("xaxis_tickangle", -45)
        xaxis_title = chart_config.get("xaxis_title", "")

        for i in range(1, n_groups + 1):
            fig.update_xaxes(
                tickangle=xaxis_tickangle,
                title_text=xaxis_title if i == 1 else "",
                row=1,
                col=i,
            )

        # Update Y-axis: rotation and title on first column
        yaxis_tickangle = chart_config.get("yaxis_tickangle", 0)
        yaxis_title = chart_config.get("yaxis_title", "Compound")

        fig.update_yaxes(
            title_text=yaxis_title, tickangle=yaxis_tickangle, row=1, col=1
        )

        # Log statistics
        n_compounds = processed_df[self.compound_column].nunique()
        n_samples = processed_df[self.sample_column].nunique()
        logger.info(
            f"Frozenset figure created - {n_groups} groups, "
            f"{n_samples} samples, {n_compounds} compounds"
        )

        return fig

    def _group_by_compound_profile(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Group samples by their compound profile (frozenset of compounds).

        Samples with identical compound profiles are grouped together.

        Parameters
        ----------
        df : pd.DataFrame
            Filtered data for a single compound class.

        Returns
        -------
        pd.DataFrame
            DataFrame with '_group' column added.
        """
        logger.debug("Grouping samples by compound profile...")

        compound_profile_to_group: Dict[int, int] = {}
        groups: List[Dict[str, Any]] = []

        # Build groups based on frozenset of compounds per sample
        for sample in df[self.sample_column].unique():
            compounds = frozenset(
                df.loc[df[self.sample_column] == sample, self.compound_column].unique()
            )

            if compounds:
                profile_hash = hash(compounds)

                if profile_hash in compound_profile_to_group:
                    group_idx = compound_profile_to_group[profile_hash]
                    groups[group_idx]["samples"].append(sample)
                else:
                    new_group = {"compounds": list(compounds), "samples": [sample]}
                    groups.append(new_group)
                    compound_profile_to_group[profile_hash] = len(groups) - 1

        # Add group labels to dataframe
        df_grouped = df.copy()
        df_grouped["_group"] = None

        for i, group in enumerate(groups):
            label = f"Group {i + 1}"
            df_grouped.loc[
                df_grouped[self.sample_column].isin(group["samples"]), "_group"
            ] = label

        result = df_grouped.dropna(subset=["_group"])
        logger.info(f"Created {len(groups)} groups from compound profiles")

        return result

    def _minimize_groups(self, df: pd.DataFrame) -> List[str]:
        """
        Apply greedy set cover algorithm to minimize groups.

        Selects minimal set of groups that cover all compounds.

        Parameters
        ----------
        df : pd.DataFrame
            Grouped data with '_group' column.

        Returns
        -------
        List[str]
            List of selected group labels.
        """
        logger.debug("Minimizing groups using set cover algorithm...")

        if df.empty:
            return []

        # Get compounds per group
        group_compounds = (
            df.groupby("_group")[self.compound_column].apply(set).reset_index()
        )

        all_compounds: Set[str] = set(df[self.compound_column].unique())
        selected_groups: List[str] = []

        # Greedy set cover
        while all_compounds:
            best_group = None
            max_cover = -1

            for _, row in group_compounds.iterrows():
                coverage = len(all_compounds.intersection(row[self.compound_column]))
                if coverage > max_cover:
                    max_cover = coverage
                    best_group = row["_group"]

            if best_group is None or max_cover == 0:
                break

            selected_groups.append(best_group)

            # Remove covered compounds
            covered = group_compounds.loc[
                group_compounds["_group"] == best_group, self.compound_column
            ].iloc[0]
            all_compounds -= covered

            # Remove selected group from candidates
            group_compounds = group_compounds[group_compounds["_group"] != best_group]

        logger.info(f"Selected {len(selected_groups)} minimized groups")
        return selected_groups

    def _calculate_ko_counts(
        self, df_full: pd.DataFrame, df_filtered: pd.DataFrame
    ) -> Optional[pd.Series]:
        """
        Calculate unique KO counts per compound within selected class.

        Parameters
        ----------
        df_full : pd.DataFrame
            Full cleaned dataset.
        df_filtered : pd.DataFrame
            Data filtered to selected compound class.

        Returns
        -------
        Optional[pd.Series]
            Series mapping compound name to unique KO count, or None if
            KO column not available.
        """
        if self.ko_column not in df_full.columns:
            logger.warning("KO column not found, skipping KO count calculation")
            return None

        logger.debug("Calculating unique KO counts per compound...")

        # Filter to selected class and drop KO nulls
        df_ko = df_filtered.dropna(subset=[self.compound_column, self.ko_column])

        if df_ko.empty:
            logger.warning("No valid KO data found")
            return None

        # Count unique KOs per compound
        ko_counts = (
            df_ko.groupby(self.compound_column)[self.ko_column]
            .nunique()
            .rename("_unique_ko_count")
        )

        logger.info(f"Calculated KO counts for {len(ko_counts)} compounds")
        return ko_counts

    def apply_filters(
        self, df: pd.DataFrame, filters: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Apply filters including compound class selection.

        Parameters
        ----------
        df : pd.DataFrame
            Data to filter.
        filters : Optional[Dict[str, Any]], default=None
            Filter specifications including 'compoundclass'.

        Returns
        -------
        pd.DataFrame
            Filtered data.
        """
        if filters and "compoundclass" in filters:
            self._selected_compoundclass = filters["compoundclass"]
            logger.info(f"Set compound class filter: '{self._selected_compoundclass}'")

        return super().apply_filters(df, filters)

    def get_available_compound_classes(self, df: pd.DataFrame) -> List[str]:
        """
        Get list of available compound classes from data.

        Parameters
        ----------
        df : pd.DataFrame
            Input data.

        Returns
        -------
        List[str]
            Sorted list of unique compound classes.
        """
        if self.compoundclass_column not in df.columns:
            return []

        return sorted(df[self.compoundclass_column].dropna().unique().tolist())

    def get_group_statistics(self, processed_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate statistics for visualization.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Processed data.

        Returns
        -------
        Dict[str, Any]
            Statistics including group counts, samples, compounds.
        """
        return {
            "compound_class": self._selected_compoundclass,
            "total_groups": len(self._minimized_groups),
            "groups": self._minimized_groups,
            "total_samples": processed_df[self.sample_column].nunique(),
            "total_compounds": processed_df[self.compound_column].nunique(),
            "ko_range": {
                "min": int(processed_df["_unique_ko_count"].min()),
                "max": int(processed_df["_unique_ko_count"].max()),
            },
        }
