"""
Heatmap Scored Strategy - Completeness and Compliance Scoring.

This module implements the HeatmapScoredStrategy for creating heatmap
visualizations showing scoring/completeness metrics across samples and
various categories (compounds, pathways, agencies).

Classes
-------
HeatmapScoredStrategy
    Strategy for scored heatmap generation with completeness metrics.

Notes
-----
- Supports KO completeness scoring (unique KO counts)
- Supports compound compliance scoring (regulatory agencies)
- Scores displayed as percentages (0-100%)

For supported use cases, refer to the official documentation.
"""

import logging
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


class HeatmapScoredStrategy(BasePlotStrategy):
    """
    Strategy for scored heatmap completeness/compliance visualizations.

    This strategy creates heatmaps showing scoring metrics (0-100%) where
    rows represent samples, columns represent categories, and cell values
    represent completeness or compliance scores.

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
    scoring_mode : str
        Scoring algorithm: 'ko_completeness' or 'compound_compliance'.
    category_column : str
        Column containing categories (e.g., 'Pathway', 'referenceAG').
    sample_column : str
        Column containing sample identifiers (default: 'Sample').
    value_column : str
        Column for aggregation ('KO' for completeness, 'compoundname' for
        compliance).

    Methods
    -------
    validate_data(df)
        Validate input data for heatmap requirements
    process_data(df)
        Process data and calculate scoring matrix
    create_figure(processed_df)
        Create heatmap figure from scoring matrix

    Notes
    -----
    - Supports two scoring modes: KO completeness and compound compliance
    - Scores displayed as percentages (0-100%)
    - Heatmap uses color scale to represent score intensity
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

        # Extract strategy-specific parameters
        self.scoring_mode = self.plotly_config.get("scoring_mode", "ko_completeness")
        self.category_column = self.plotly_config.get("category_column", "Pathway")
        self.sample_column = self.plotly_config.get("sample_column", "Sample")
        self.value_column = self.plotly_config.get("value_column", "KO")

        logger.info(
            f"HeatmapScoredStrategy initialized for {self.metadata.get('use_case_id', 'unknown')}: "
            f"mode='{self.scoring_mode}', category='{self.category_column}', "
            f"sample='{self.sample_column}', value='{self.value_column}'"
        )

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for heatmap requirements.

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate.

        Raises
        ------
        ValueError
            If DataFrame is empty, required columns missing, or no valid
            samples/categories found.
        """
        logger.debug(
            f"Validating data - Shape: {df.shape}, " f"Columns: {df.columns.tolist()}"
        )

        # Check DataFrame not empty
        if df.empty:
            raise ValueError("Input DataFrame is empty")

        # Determine required columns based on scoring mode
        if self.scoring_mode == "compound_compliance":
            required_cols = [
                self.sample_column,
                self.category_column,
                self.value_column,  # compoundname
            ]
        else:  # ko_completeness
            required_cols = [
                self.sample_column,
                self.category_column,
                self.value_column,  # KO
            ]

        # Check required columns exist
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(
                f"Missing required columns: {missing_cols}. "
                f"Available columns: {df.columns.tolist()}"
            )

        # Drop rows with null values in critical columns
        df_clean = df.dropna(subset=required_cols)
        if df_clean.empty:
            raise ValueError(
                f"No valid data after removing nulls in columns: {required_cols}"
            )

        # Check at least one sample and category
        n_samples = df_clean[self.sample_column].nunique()
        n_categories = df_clean[self.category_column].nunique()

        if n_samples == 0:
            raise ValueError(f"No samples found in column '{self.sample_column}'")
        if n_categories == 0:
            raise ValueError(f"No categories found in column '{self.category_column}'")

        logger.info(
            f"✓ Data validation passed - "
            f"{n_samples} samples, {n_categories} categories, "
            f"{len(df_clean)} records"
        )

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data and calculate scoring matrix.

        Implements scoring algorithms based on configured mode: KO completeness
        or compound compliance.

        Parameters
        ----------
        df : pd.DataFrame
            Input data with required columns.

        Returns
        -------
        pd.DataFrame
            Heatmap matrix with samples as rows, categories as columns,
            and scores (0-100%) as values.
        """
        logger.info(f"Processing data with {self.scoring_mode} scoring mode...")

        # Clean data: remove nulls and empty strings
        df_clean = df.dropna(
            subset=[self.sample_column, self.category_column, self.value_column]
        ).copy()

        # Remove empty strings in value column
        df_clean = df_clean[df_clean[self.value_column] != ""]

        logger.debug(
            f"After cleaning: {len(df_clean)} records "
            f"({len(df) - len(df_clean)} removed)"
        )

        if self.scoring_mode == "compound_compliance":
            heatmap_matrix = self._calculate_compound_compliance(df_clean)
        else:  # ko_completeness (default)
            heatmap_matrix = self._calculate_ko_completeness(df_clean)

        logger.info(
            f"✓ Scoring matrix created - "
            f"Shape: {heatmap_matrix.shape}, "
            f"Score range: [{heatmap_matrix.min().min():.1f}%, "
            f"{heatmap_matrix.max().max():.1f}%]"
        )

        return heatmap_matrix

    def _calculate_ko_completeness(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate KO completeness scores.

        Computes percentage of unique KOs present in each sample-category
        combination relative to total KOs in that category.

        Parameters
        ----------
        df : pd.DataFrame
            Cleaned input data.

        Returns
        -------
        pd.DataFrame
            Scoring matrix (samples × categories).
        """
        logger.debug("Calculating KO completeness scores...")

        # Step 1: Count unique KOs per (sample, category)
        sample_ko_counts = df.groupby([self.sample_column, self.category_column])[
            self.value_column
        ].nunique()

        logger.debug(f"Sample-category KO counts: {len(sample_ko_counts)} pairs")

        # Step 2: Calculate total unique KOs per category (universe)
        total_ko_per_category = df.groupby(self.category_column)[
            self.value_column
        ].nunique()

        # Filter out categories with no KOs (avoid division by zero)
        total_ko_per_category = total_ko_per_category[total_ko_per_category > 0]

        if total_ko_per_category.empty:
            raise ValueError(f"No categories with associated {self.value_column} found")

        logger.debug(
            f"Total KOs per category: "
            f"{len(total_ko_per_category)} categories, "
            f"range: [{total_ko_per_category.min()}, "
            f"{total_ko_per_category.max()}]"
        )

        # Align sample counts with valid categories
        sample_ko_counts = sample_ko_counts.loc[
            sample_ko_counts.index.get_level_values(self.category_column).isin(
                total_ko_per_category.index
            )
        ]

        if sample_ko_counts.empty:
            raise ValueError("No sample-category KO counts available after filtering")

        # Step 3: Calculate completeness scores (%)
        completeness_scores = (
            sample_ko_counts.div(total_ko_per_category, level=self.category_column)
            * 100
        )

        # Step 4: Create heatmap matrix
        # unstack(level='sample') creates columns for each sample
        # fillna(0) fills missing combinations with 0%
        # .T transposes to get samples as rows
        heatmap_matrix = (
            completeness_scores.unstack(level=self.sample_column).fillna(0).T
        )

        return heatmap_matrix

    def _calculate_compound_compliance(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate compound compliance scores.

        Computes percentage of agency-defined compounds that are degradable
        by each sample.

        Parameters
        ----------
        df : pd.DataFrame
            Cleaned input data.

        Returns
        -------
        pd.DataFrame
            Scoring matrix (samples × agencies).
        """
        logger.debug("Calculating compound compliance scores...")

        # Step 1: Define compound universe for each category (agency)
        category_compounds = (
            df.groupby(self.category_column)[self.value_column].unique().apply(set)
        )

        logger.debug(f"Category compound sets: {len(category_compounds)} categories")

        # Step 2: Identify compounds for each sample
        sample_compounds = (
            df.groupby(self.sample_column)[self.value_column].unique().apply(set)
        )

        logger.debug(f"Sample compound sets: {len(sample_compounds)} samples")

        # Step 3: Calculate compliance scores
        scorecard_data = []
        for sample, s_compounds in sample_compounds.items():
            for category, c_compounds in category_compounds.items():
                # Find intersection
                shared_compounds = s_compounds.intersection(c_compounds)

                # Calculate score as percentage
                if len(c_compounds) > 0:
                    score = (len(shared_compounds) / len(c_compounds)) * 100
                else:
                    score = 0

                scorecard_data.append(
                    {
                        self.sample_column: sample,
                        self.category_column: category,
                        "compliance_score": score,
                    }
                )

        # Convert to DataFrame
        scorecard_df = pd.DataFrame(scorecard_data)

        # Step 4: Pivot to create matrix (samples × categories)
        heatmap_matrix = scorecard_df.pivot(
            index=self.sample_column,
            columns=self.category_column,
            values="compliance_score",
        ).fillna(0)

        return heatmap_matrix

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create heatmap figure from scoring matrix.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Scoring matrix (samples × categories).

        Returns
        -------
        go.Figure
            Configured Plotly heatmap.
        """
        logger.debug("Creating heatmap figure...")

        # Extract chart configuration
        chart_config = self.plotly_config.get("chart", {})
        layout_config = self.plotly_config.get("layout", {})

        # Get title configuration
        title_config = chart_config.get("title", {})
        title_text = title_config.get("text", "Completeness Scorecard")

        # Get axis labels
        x_label = chart_config.get("xaxis", {}).get("title", "Category")
        y_label = chart_config.get("yaxis", {}).get("title", "Sample")
        color_label = chart_config.get("color_label", "Completeness (%)")

        # Get text display settings
        show_values = chart_config.get("show_values", True)
        text_auto = chart_config.get("text_auto", ".1f") if show_values else False

        # Get color scale
        color_scale = chart_config.get("color_continuous_scale", "Greens")

        # Create heatmap using plotly express
        fig = px.imshow(
            processed_df,
            labels=dict(x=x_label, y=y_label, color=color_label),
            text_auto=text_auto,
            aspect="auto",
            color_continuous_scale=color_scale,
            zmin=0,
            zmax=100,
        )

        # Apply layout configuration
        template = layout_config.get("template", "simple_white")
        height = layout_config.get("height", 600)
        width = layout_config.get("width", 1000)

        # Get margin configuration
        margin_config = layout_config.get("margin", {})
        margin = dict(
            l=margin_config.get("l", 80),
            r=margin_config.get("r", 100),
            t=margin_config.get("t", 100),
            b=margin_config.get("b", 120),
        )

        # Get axis angles
        xaxis_tickangle = chart_config.get("xaxis_tickangle", -45)
        yaxis_tickangle = chart_config.get("yaxis_tickangle", 0)

        # Get colorbar configuration
        colorbar_config = chart_config.get("colorbar", {})
        colorbar_title = colorbar_config.get("title", color_label)

        # Get title display setting
        show_title = title_config.get("show", True)

        # Build layout update dict
        layout_update = {
            "height": height,
            "template": template,
            "xaxis_tickangle": xaxis_tickangle,
            "yaxis_tickangle": yaxis_tickangle,
            "margin": margin,
            "coloraxis_colorbar": dict(title=colorbar_title),
        }

        # Add title if enabled
        if show_title and title_text:
            layout_update["title"] = {
                "text": title_text,
                "x": title_config.get("x", 0.5),
                "xanchor": title_config.get("xanchor", "center"),
            }

        # Only set width if not using autosize
        if not layout_config.get("autosize", False):
            layout_update["width"] = width

        fig.update_layout(**layout_update)

        # Update text font size if configured
        text_font_size = chart_config.get("text_font_size", 10)
        fig.update_traces(textfont_size=text_font_size)

        # Set text color based on value for better contrast
        # Black text for light cells, white for dark cells
        text_font_color = chart_config.get("text_font_color", "black")
        fig.update_traces(textfont_color=text_font_color)

        logger.info(
            f"✓ Heatmap figure created - "
            f"Size: {width}×{height}px, "
            f"Template: {template}"
        )

        return fig
