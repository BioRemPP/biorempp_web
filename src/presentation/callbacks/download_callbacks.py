"""
Download Callbacks - Data Export Functionality.

Provides download callbacks for all use cases following the pattern:
- Extract raw data from merged-result-store
- Apply use-case-specific data selection
- Export via ResultExporter
- Return dcc.send_bytes for browser download
- Show toast notifications for feedback

Author: BioRemPP Development Team
Date: 2025-11-28
Version: 1.0.0
"""

import logging
import time
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import yaml
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from src.application.core.result_exporter import ExportFormat, ResultExporter
from src.presentation.components.download_component import sanitize_filename

logger = logging.getLogger(__name__)


class DownloadCallbackFactory:
    """
    Factory for creating download callbacks for use cases.

    Uses factory pattern to generate standardized download callbacks
    based on use case configuration.
    """

    def __init__(
        self, config_path: Optional[Path] = None, rate_limit_seconds: float = 2.0
    ):
        """
        Initialize download callback factory.

        Parameters
        ----------
        config_path : Optional[Path]
            Path to download_config.yaml file
        rate_limit_seconds : float
            Minimum seconds between downloads per use case (default: 2.0)
        """
        if config_path is None:
            # Default to infrastructure/config/download_config.yaml
            current_dir = Path(__file__).parent
            biorempp_root = current_dir.parent.parent
            config_path = (
                biorempp_root / "infrastructure" / "config" / "download_config.yaml"
            )

        self.config_path = config_path
        self.use_case_configs = self._load_config()
        self.exporter = ResultExporter()
        self.rate_limit_seconds = rate_limit_seconds
        self._last_download_time: Dict[str, float] = (
            {}
        )  # Track last download per use case

        logger.info(
            f"[DOWNLOAD] Initialized with {len(self.use_case_configs)} use case configs, rate limit: {rate_limit_seconds}s"
        )

    def _load_config(self) -> Dict:
        """Load use case download configurations from YAML."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            logger.info(f"[DOWNLOAD] Loaded config from {self.config_path}")
            return config or {}
        except FileNotFoundError:
            logger.warning(f"[DOWNLOAD] Config file not found: {self.config_path}")
            return {}
        except Exception as e:
            logger.error(f"[DOWNLOAD] Error loading config: {e}")
            return {}

    def register_all_callbacks(self, app):
        """
        Register download callbacks for all configured use cases.

        Parameters
        ----------
        app : Dash
            Dash application instance
        """
        registered_count = 0

        for use_case_id, config in self.use_case_configs.items():
            try:
                self._register_use_case_callback(app, use_case_id, config)
                registered_count += 1
                logger.debug(f"[DOWNLOAD] Registered callback for {use_case_id}")
            except Exception as e:
                logger.error(f"[DOWNLOAD] Failed to register {use_case_id}: {e}")

        logger.info(f"[DOWNLOAD] Registered {registered_count} download callbacks")

    def _register_use_case_callback(self, app, use_case_id: str, config: Dict):
        """
        Register download callback for a single use case.

        Parameters
        ----------
        app : Dash
            Dash application instance
        use_case_id : str
            Use case identifier (e.g., "UC-2.1")
        config : Dict
            Use case download configuration
        """
        # Generate component IDs
        uc_id_safe = use_case_id.lower().replace(".", "-")
        button_id_base = f"{uc_id_safe}-download-btn"
        download_id = f"{uc_id_safe}-download"
        spinner_id = f"{button_id_base}-spinner"
        toast_id = f"{uc_id_safe}-download-toast"

        # Format button IDs
        csv_btn_id = f"{button_id_base}-csv"
        excel_btn_id = f"{button_id_base}-excel"
        json_btn_id = f"{button_id_base}-json"

        # Get configuration
        databases = config.get("databases", [])
        export_strategy = config.get("export_strategy", "single_file")
        db_selection_buttons = config.get("database_selection_buttons", [])
        dropdown_filters = config.get("dropdown_filters", [])
        relevant_columns = config.get("relevant_columns", None)
        data_processing = config.get("data_processing", None)

        # Build States dynamically based on config
        states = [
            State("merged-result-store", "data"),
            State(csv_btn_id, "n_clicks"),
            State(excel_btn_id, "n_clicks"),
            State(json_btn_id, "n_clicks"),
        ]

        # Add database selection button states if configured
        for btn_id in db_selection_buttons:
            states.append(State(btn_id, "outline"))

        # Add dropdown filter states if configured
        for dropdown_id in dropdown_filters:
            states.append(State(dropdown_id, "value"))

        # Register callback for each format
        @app.callback(
            [
                Output(download_id, "data"),
                Output(toast_id, "is_open"),
                Output(toast_id, "children"),
                Output(toast_id, "icon"),
                Output(spinner_id, "style"),
            ],
            [
                Input(csv_btn_id, "n_clicks"),
                Input(excel_btn_id, "n_clicks"),
                Input(json_btn_id, "n_clicks"),
            ],
            states,
            prevent_initial_call=True,
        )
        def download_callback(
            csv_click,
            excel_click,
            json_click,
            merged_data,
            csv_state,
            excel_state,
            json_state,
            *additional_states,  # DB buttons + dropdown filters
        ):
            """Download data for this use case."""
            from dash import callback_context

            # Determine which button was clicked
            ctx = callback_context
            if not ctx.triggered:
                raise PreventUpdate

            triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

            # Map button ID to format
            format_map = {
                csv_btn_id: ("csv", ExportFormat.CSV),
                excel_btn_id: ("excel", ExportFormat.EXCEL),
                json_btn_id: ("json", ExportFormat.JSON),
            }

            if triggered_id not in format_map:
                raise PreventUpdate

            format_name, format_enum = format_map[triggered_id]

            # Parse additional states (database buttons first, then dropdowns)
            n_db_buttons = len(db_selection_buttons)
            n_dropdowns = len(dropdown_filters)

            db_button_states = (
                additional_states[:n_db_buttons] if n_db_buttons > 0 else []
            )
            dropdown_values = (
                additional_states[n_db_buttons : n_db_buttons + n_dropdowns]
                if n_dropdowns > 0
                else []
            )

            # Determine selected database if this UC has database selection buttons
            selected_database = databases[0] if databases else None
            if db_selection_buttons and db_button_states:
                # Find which button is selected (outline=False)
                for i, outline_state in enumerate(db_button_states):
                    if outline_state is False:  # Selected button
                        # Map button index to database
                        selected_database = (
                            databases[i] if i < len(databases) else databases[0]
                        )
                        break

            # Collect dropdown filter values
            filter_values = {}
            if dropdown_filters and dropdown_values:
                for dropdown_id, value in zip(dropdown_filters, dropdown_values):
                    filter_values[dropdown_id] = value

            logger.info(
                f"[{use_case_id}] Download triggered, format={format_name}, database={selected_database}, filters={filter_values}"
            )

            # Rate limiting check
            current_time = time.time()
            last_download = self._last_download_time.get(use_case_id, 0)
            time_since_last = current_time - last_download

            if time_since_last < self.rate_limit_seconds:
                wait_time = self.rate_limit_seconds - time_since_last
                logger.warning(
                    f"[{use_case_id}] Rate limit exceeded. "
                    f"Please wait {wait_time:.1f}s before next download."
                )
                return (
                    None,
                    True,
                    f"Please wait {wait_time:.1f} seconds before downloading again.",
                    "warning",
                    {"display": "none"},
                )

            # Update last download time
            self._last_download_time[use_case_id] = current_time

            # Show spinner
            spinner_style = {"display": "inline-block"}

            # Validate data
            if not merged_data:
                logger.warning(f"[{use_case_id}] No data in store")
                return (
                    None,
                    True,
                    "No data available. Please process data first.",
                    "danger",
                    {"display": "none"},
                )

            try:
                # Extract data based on strategy
                if export_strategy == "single_file":
                    download_data, toast_msg, toast_icon = self._export_single_file(
                        use_case_id,
                        selected_database,
                        merged_data,
                        format_name,
                        format_enum,
                        relevant_columns,
                        data_processing,
                        filter_values,
                    )
                elif export_strategy == "multi_sheet":
                    if format_name != "excel":
                        # For CSV/JSON, export first database only
                        download_data, toast_msg, toast_icon = self._export_single_file(
                            use_case_id,
                            selected_database,
                            merged_data,
                            format_name,
                            format_enum,
                            relevant_columns,
                            data_processing,
                            filter_values,
                        )
                    else:
                        download_data, toast_msg, toast_icon = self._export_multi_sheet(
                            use_case_id, databases, merged_data
                        )
                else:
                    raise ValueError(f"Unknown export strategy: {export_strategy}")

                # Hide spinner
                spinner_style = {"display": "none"}

                return (download_data, True, toast_msg, toast_icon, spinner_style)

            except Exception as e:
                logger.error(f"[{use_case_id}] Download error: {str(e)}", exc_info=True)
                return (
                    None,
                    True,
                    f"Download failed: {str(e)}",
                    "danger",
                    {"display": "none"},
                )

    def _export_single_file(
        self,
        use_case_id: str,
        database: str,
        merged_data: Dict,
        format_name: str,
        format_enum: ExportFormat,
        relevant_columns: Optional[list] = None,
        data_processing: Optional[Dict] = None,
        filter_values: Optional[Dict] = None,
    ):
        """
        Export single database file.

        Parameters
        ----------
        use_case_id : str
            Use case identifier
        database : str
            Database key (e.g., 'biorempp_df')
        merged_data : Dict
            Data from merged-result-store
        format_name : str
            Format name ('csv', 'excel', 'json')
        format_enum : ExportFormat
            ExportFormat enum value
        relevant_columns : Optional[list]
            List of columns to include in export (if None, export all columns)
        data_processing : Optional[Dict]
            Data processing configuration for aggregation/transformation
        filter_values : Optional[Dict]
            Dictionary of dropdown filter values {dropdown_id: value}

        Returns
        -------
        tuple
            (download_data, toast_message, toast_icon)
        """
        # Extract DataFrame
        if database not in merged_data:
            raise KeyError(f"Database '{database}' not found in merged data")

        df = pd.DataFrame(merged_data[database])

        if df.empty:
            raise ValueError(f"Database '{database}' is empty")

        # Apply data processing if specified (e.g., aggregation for chart data)
        if data_processing:
            operation = data_processing.get("operation")
            logger.info(f"[{use_case_id}] Data processing operation: '{operation}'")
            if operation == "aggregate_ko_count":
                group_by = data_processing.get("group_by", "Sample")
                agg_column = data_processing.get("agg_column", "ko")
                result_column = data_processing.get("result_column", "ko_count")

                # Group by Sample and count unique KOs
                df = df.groupby(group_by)[agg_column].nunique().reset_index()
                df.columns = [group_by, result_column]

                logger.info(
                    f"[{use_case_id}] Applied aggregation: "
                    f"grouped by {group_by}, counted unique {agg_column} -> {result_column}"
                )
                logger.info(f"[{use_case_id}] Processed data shape: {df.shape}")

            elif operation == "aggregate_compound_count":
                # UC-2.2: Count unique compounds per sample
                group_by = data_processing.get("group_by", "Sample")
                agg_column = data_processing.get("agg_column", "cpd")
                result_column = data_processing.get("result_column", "Compound_Count")

                # Find compound column (flexible naming)
                compound_col = None
                compound_candidates = [
                    agg_column,
                    "cpd",
                    "Compound_ID",
                    "Compound",
                    "compound",
                    "Compound_Name",
                ]

                for candidate in compound_candidates:
                    if candidate in df.columns:
                        compound_col = candidate
                        break

                if not compound_col:
                    raise ValueError(
                        f"Compound column not found. "
                        f"Available: {df.columns.tolist()}, "
                        f"Expected one of: {compound_candidates}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using '{compound_col}' " f"as compound column"
                )

                # Group by Sample and count unique compounds
                df = df.groupby(group_by)[compound_col].nunique().reset_index()
                df.columns = [group_by, result_column]

                logger.info(
                    f"[{use_case_id}] Applied compound count aggregation: "
                    f"grouped by {group_by}, "
                    f"counted unique {compound_col} -> {result_column}"
                )
                logger.info(f"[{use_case_id}] Processed data shape: {df.shape}")

            elif operation == "aggregate_compound_sample_count":
                # UC-2.3: Count unique samples per compound grouped by class
                class_column = data_processing.get("class_column", "compoundclass")
                compound_column = data_processing.get("compound_column", "compoundname")
                sample_column = data_processing.get("sample_column", "sample")
                result_column = data_processing.get("result_column", "Sample_Count")

                logger.info(
                    f"[{use_case_id}] Computing " f"aggregate_compound_sample_count"
                )

                # Find columns (flexible naming)
                class_col = None
                compound_col = None
                sample_col = None

                # Compound class column
                class_candidates = [
                    class_column,
                    "Compound_Class",
                    "compoundclass",
                    "compound_class",
                    "class",
                ]
                for candidate in class_candidates:
                    if candidate in df.columns:
                        class_col = candidate
                        break

                # Compound name column
                compound_candidates = [
                    compound_column,
                    "Compound_Name",
                    "compoundname",
                    "compound_name",
                    "compound",
                    "cpd",
                ]
                for candidate in compound_candidates:
                    if candidate in df.columns:
                        compound_col = candidate
                        break

                # Sample column
                sample_candidates = [sample_column, "Sample", "sample", "sample_id"]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # Validate all columns found
                if not class_col or not compound_col or not sample_col:
                    raise ValueError(
                        f"Required columns not found. "
                        f"Available: {df.columns.tolist()}, "
                        f"Needed: class (one of {class_candidates}), "
                        f"compound (one of {compound_candidates}), "
                        f"sample (one of {sample_candidates})"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"class='{class_col}', compound='{compound_col}', "
                    f"sample='{sample_col}'"
                )

                # Remove rows with missing values
                initial_count = len(df)
                df_clean = df[[class_col, compound_col, sample_col]].dropna()

                logger.debug(
                    f"[{use_case_id}] After dropna: "
                    f"{len(df_clean)} rows (removed {initial_count - len(df_clean)})"
                )

                # Group by class and compound, count unique samples
                result_df = (
                    df_clean.groupby([class_col, compound_col])[sample_col]
                    .nunique()
                    .reset_index()
                )
                result_df.columns = ["Compound_Class", "Compound_Name", result_column]

                # Sort by class and sample count (descending within class)
                result_df = result_df.sort_values(
                    ["Compound_Class", result_column], ascending=[True, False]
                )

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Applied compound-sample aggregation: "
                    f"grouped by [{class_col}, {compound_col}], "
                    f"counted unique {sample_col} -> {result_column}"
                )
                logger.info(
                    f"[{use_case_id}] Processed data shape: {df.shape}, "
                    f"{df['Compound_Class'].nunique()} classes, "
                    f"{len(df)} compound-class pairs"
                )

            elif operation == "aggregate_compound_gene_count":
                # UC-2.4: Count unique genes per compound grouped by class
                class_column = data_processing.get("class_column", "compoundclass")
                compound_column = data_processing.get("compound_column", "compoundname")
                gene_column = data_processing.get("gene_column", "genesymbol")
                result_column = data_processing.get("result_column", "Gene_Count")

                logger.info(
                    f"[{use_case_id}] Computing " f"aggregate_compound_gene_count"
                )

                # Find columns (flexible naming)
                class_col = None
                compound_col = None
                gene_col = None

                # Compound class column
                class_candidates = [
                    class_column,
                    "Compound_Class",
                    "compoundclass",
                    "compound_class",
                    "class",
                ]
                for candidate in class_candidates:
                    if candidate in df.columns:
                        class_col = candidate
                        break

                # Compound name column
                compound_candidates = [
                    compound_column,
                    "Compound_Name",
                    "compoundname",
                    "compound_name",
                    "compound",
                    "cpd",
                ]
                for candidate in compound_candidates:
                    if candidate in df.columns:
                        compound_col = candidate
                        break

                # Gene symbol column
                gene_candidates = [
                    gene_column,
                    "Gene_Symbol",
                    "genesymbol",
                    "gene_symbol",
                    "gene",
                    "Gene",
                ]
                for candidate in gene_candidates:
                    if candidate in df.columns:
                        gene_col = candidate
                        break

                # Validate all columns found
                if not class_col or not compound_col or not gene_col:
                    raise ValueError(
                        f"Required columns not found. "
                        f"Available: {df.columns.tolist()}, "
                        f"Needed: class (one of {class_candidates}), "
                        f"compound (one of {compound_candidates}), "
                        f"gene (one of {gene_candidates})"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"class='{class_col}', compound='{compound_col}', "
                    f"gene='{gene_col}'"
                )

                # Remove rows with missing values
                initial_count = len(df)
                df_clean = df[[class_col, compound_col, gene_col]].dropna()

                logger.debug(
                    f"[{use_case_id}] After dropna: "
                    f"{len(df_clean)} rows (removed {initial_count - len(df_clean)})"
                )

                # Group by class and compound, count unique genes
                result_df = (
                    df_clean.groupby([class_col, compound_col])[gene_col]
                    .nunique()
                    .reset_index()
                )
                result_df.columns = ["Compound_Class", "Compound_Name", result_column]

                # Sort by class and gene count (descending within class)
                result_df = result_df.sort_values(
                    ["Compound_Class", result_column], ascending=[True, False]
                )

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Applied compound-gene aggregation: "
                    f"grouped by [{class_col}, {compound_col}], "
                    f"counted unique {gene_col} -> {result_column}"
                )
                logger.info(
                    f"[{use_case_id}] Processed data shape: {df.shape}, "
                    f"{df['Compound_Class'].nunique()} classes, "
                    f"{len(df)} compound-class pairs"
                )

            elif operation == "aggregate_pathway_sample_ko_count":
                # UC-4.1: Count unique KOs per Pathway-Sample combination
                pathway_column = data_processing.get("pathway_column", "pathway")
                sample_column = data_processing.get("sample_column", "sample")
                ko_column = data_processing.get("ko_column", "ko")
                result_column = data_processing.get("result_column", "KO_Count")

                logger.info(
                    f"[{use_case_id}] Computing " f"aggregate_pathway_sample_ko_count"
                )

                # Find columns (flexible naming)
                pathway_col = None
                sample_col = None
                ko_col = None

                # Pathway column
                pathway_candidates = [
                    pathway_column,
                    "Pathway",
                    "pathway",
                    "pathname",
                    "pathway_name",
                    "PathwayName",
                ]
                for candidate in pathway_candidates:
                    if candidate in df.columns:
                        pathway_col = candidate
                        break

                # Sample column
                sample_candidates = [
                    sample_column,
                    "Sample",
                    "sample",
                    "sample_id",
                    "SampleID",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # KO column
                ko_candidates = [ko_column, "KO", "ko", "ko_id", "KOID"]
                for candidate in ko_candidates:
                    if candidate in df.columns:
                        ko_col = candidate
                        break

                # Validate all columns found
                if not pathway_col or not sample_col or not ko_col:
                    raise ValueError(
                        f"Required columns not found. "
                        f"Available: {df.columns.tolist()}, "
                        f"Needed: pathway (one of {pathway_candidates}), "
                        f"sample (one of {sample_candidates}), "
                        f"ko (one of {ko_candidates})"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"pathway='{pathway_col}', sample='{sample_col}', "
                    f"ko='{ko_col}'"
                )

                # Remove rows with missing values
                initial_count = len(df)
                df_clean = df[[pathway_col, sample_col, ko_col]].dropna()

                logger.debug(
                    f"[{use_case_id}] After dropna: "
                    f"{len(df_clean)} rows (removed {initial_count - len(df_clean)})"
                )

                # Group by pathway and sample, count unique KOs
                result_df = (
                    df_clean.groupby([pathway_col, sample_col])[ko_col]
                    .nunique()
                    .reset_index()
                )
                result_df.columns = ["Pathway", "Sample", result_column]

                # Sort by pathway and sample
                result_df = result_df.sort_values(
                    ["Pathway", "Sample"], ascending=[True, True]
                )

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Applied pathway-sample-KO aggregation: "
                    f"grouped by [{pathway_col}, {sample_col}], "
                    f"counted unique {ko_col} -> {result_column}"
                )
                logger.info(
                    f"[{use_case_id}] Processed data shape: {df.shape}, "
                    f"{df['Pathway'].nunique()} pathways, "
                    f"{df['Sample'].nunique()} samples, "
                    f"{len(df)} pathway-sample pairs"
                )

            elif operation == "aggregate_sample_enzyme_gene_count":
                # UC-4.9: Count unique genes per Sample-Enzyme_Activity combination
                # Note: Filters out '#N/D' enzyme activities
                sample_column = data_processing.get("sample_column", "sample")
                enzyme_column = data_processing.get("enzyme_column", "enzyme_activity")
                gene_column = data_processing.get("gene_column", "genesymbol")
                result_column = data_processing.get("result_column", "Gene_Count")
                filter_value = data_processing.get("filter_value", "#N/D")

                logger.info(
                    f"[{use_case_id}] Computing " f"aggregate_sample_enzyme_gene_count"
                )

                # Find columns (flexible naming)
                sample_col = None
                enzyme_col = None
                gene_col = None

                # Sample column
                sample_candidates = [
                    sample_column,
                    "Sample",
                    "sample",
                    "sample_id",
                    "SampleID",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # Enzyme activity column
                enzyme_candidates = [
                    enzyme_column,
                    "Enzyme_Activity",
                    "enzyme_activity",
                    "enzymeactivity",
                    "EnzymeActivity",
                ]
                for candidate in enzyme_candidates:
                    if candidate in df.columns:
                        enzyme_col = candidate
                        break

                # Gene symbol column
                gene_candidates = [
                    gene_column,
                    "Gene_Symbol",
                    "genesymbol",
                    "gene_symbol",
                    "gene",
                    "Gene",
                ]
                for candidate in gene_candidates:
                    if candidate in df.columns:
                        gene_col = candidate
                        break

                # Validate all columns found
                if not sample_col or not enzyme_col or not gene_col:
                    raise ValueError(
                        f"Required columns not found. "
                        f"Available: {df.columns.tolist()}, "
                        f"Needed: sample (one of {sample_candidates}), "
                        f"enzyme (one of {enzyme_candidates}), "
                        f"gene (one of {gene_candidates})"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"sample='{sample_col}', enzyme='{enzyme_col}', "
                    f"gene='{gene_col}'"
                )

                # Remove rows with missing values
                initial_count = len(df)
                df_clean = df[[sample_col, enzyme_col, gene_col]].dropna()

                logger.debug(
                    f"[{use_case_id}] After dropna: "
                    f"{len(df_clean)} rows (removed {initial_count - len(df_clean)})"
                )

                # Filter out '#N/D' enzyme activities (important!)
                if filter_value:
                    before_filter = len(df_clean)
                    df_clean = df_clean[df_clean[enzyme_col] != filter_value]
                    logger.info(
                        f"[{use_case_id}] Filtered out '{filter_value}': "
                        f"{before_filter} -> {len(df_clean)} rows "
                        f"({before_filter - len(df_clean)} removed)"
                    )

                # Group by sample and enzyme_activity, count unique genes
                result_df = (
                    df_clean.groupby([sample_col, enzyme_col])[gene_col]
                    .nunique()
                    .reset_index()
                )
                result_df.columns = ["Sample", "Enzyme_Activity", result_column]

                # Sort by sample and enzyme activity
                result_df = result_df.sort_values(
                    ["Sample", "Enzyme_Activity"], ascending=[True, True]
                )

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Applied sample-enzyme-gene aggregation: "
                    f"grouped by [{sample_col}, {enzyme_col}], "
                    f"counted unique {gene_col} -> {result_column}"
                )
                logger.info(
                    f"[{use_case_id}] Processed data shape: {df.shape}, "
                    f"{df['Sample'].nunique()} samples, "
                    f"{df['Enzyme_Activity'].nunique()} enzyme activities, "
                    f"{len(df)} sample-enzyme pairs"
                )

            elif operation == "extract_super_category_endpoint_score":
                # UC-7.5: Extract Super_Category, Endpoint, and Toxicity_Score
                super_category_column = data_processing.get(
                    "super_category_column", "super_category"
                )
                endpoint_column = data_processing.get("endpoint_column", "endpoint")
                toxicity_score_column = data_processing.get(
                    "toxicity_score_column", "toxicity_score"
                )

                logger.info(
                    f"[{use_case_id}] Computing "
                    f"extract_super_category_endpoint_score"
                )

                # Find columns (flexible naming)
                super_category_col = None
                endpoint_col = None
                toxicity_score_col = None

                # Super category column
                super_category_candidates = [
                    super_category_column,
                    "Super_Category",
                    "super_category",
                    "supercategory",
                    "SuperCategory",
                    "category",
                ]
                for candidate in super_category_candidates:
                    if candidate in df.columns:
                        super_category_col = candidate
                        break

                # Endpoint column
                endpoint_candidates = [
                    endpoint_column,
                    "Endpoint",
                    "endpoint",
                    "EndPoint",
                    "end_point",
                ]
                for candidate in endpoint_candidates:
                    if candidate in df.columns:
                        endpoint_col = candidate
                        break

                # Toxicity score column
                toxicity_score_candidates = [
                    toxicity_score_column,
                    "Toxicity_Score",
                    "toxicity_score",
                    "ToxicityScore",
                    "score",
                ]
                for candidate in toxicity_score_candidates:
                    if candidate in df.columns:
                        toxicity_score_col = candidate
                        break

                # Validate all columns found
                if not super_category_col or not endpoint_col or not toxicity_score_col:
                    raise ValueError(
                        f"Required columns not found. "
                        f"Available: {df.columns.tolist()}, "
                        f"Needed: super_category (one of {super_category_candidates}), "
                        f"endpoint (one of {endpoint_candidates}), "
                        f"toxicity_score (one of {toxicity_score_candidates})"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"super_category='{super_category_col}', "
                    f"endpoint='{endpoint_col}', "
                    f"toxicity_score='{toxicity_score_col}'"
                )

                # Remove rows with missing values
                initial_count = len(df)
                df_clean = df[
                    [super_category_col, endpoint_col, toxicity_score_col]
                ].dropna()

                logger.debug(
                    f"[{use_case_id}] After dropna: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Select the three columns
                result_df = df_clean[
                    [super_category_col, endpoint_col, toxicity_score_col]
                ].copy()

                # Rename columns to standardized names
                result_df.columns = ["Super_Category", "Endpoint", "Toxicity_Score"]

                # Sort by super_category, endpoint, and toxicity_score
                result_df = result_df.sort_values(
                    ["Super_Category", "Endpoint", "Toxicity_Score"],
                    ascending=[True, True, True],
                )

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Applied super_category-endpoint-score extraction: "
                    f"extracted from [{super_category_col}, {endpoint_col}, {toxicity_score_col}]"
                )
                logger.info(
                    f"[{use_case_id}] Processed data shape: {df.shape}, "
                    f"{df['Super_Category'].nunique()} super-categories, "
                    f"{df['Endpoint'].nunique()} endpoints, "
                    f"{len(df)} rows"
                )

            elif operation == "extract_compound_toxicity_profile":
                # UC-7.1: Extract Compound_Name, Super_Category, Endpoint, and Toxicity_Score
                compound_column = data_processing.get("compound_column", "compoundname")
                super_category_column = data_processing.get(
                    "super_category_column", "super_category"
                )
                endpoint_column = data_processing.get("endpoint_column", "endpoint")
                toxicity_score_column = data_processing.get(
                    "toxicity_score_column", "toxicity_score"
                )

                logger.info(
                    f"[{use_case_id}] Computing " f"extract_compound_toxicity_profile"
                )

                # Find columns (flexible naming)
                compound_col = None
                super_category_col = None
                endpoint_col = None
                toxicity_score_col = None

                # Compound column
                compound_candidates = [
                    compound_column,
                    "compoundname",
                    "Compound_Name",
                    "CompoundName",
                    "compound",
                    "Compound",
                ]
                for candidate in compound_candidates:
                    if candidate in df.columns:
                        compound_col = candidate
                        break

                # Super category column
                super_category_candidates = [
                    super_category_column,
                    "Super_Category",
                    "super_category",
                    "supercategory",
                    "SuperCategory",
                    "category",
                ]
                for candidate in super_category_candidates:
                    if candidate in df.columns:
                        super_category_col = candidate
                        break

                # Endpoint column
                endpoint_candidates = [
                    endpoint_column,
                    "Endpoint",
                    "endpoint",
                    "EndPoint",
                    "end_point",
                ]
                for candidate in endpoint_candidates:
                    if candidate in df.columns:
                        endpoint_col = candidate
                        break

                # Toxicity score column
                toxicity_score_candidates = [
                    toxicity_score_column,
                    "Toxicity_Score",
                    "toxicity_score",
                    "ToxicityScore",
                    "score",
                ]
                for candidate in toxicity_score_candidates:
                    if candidate in df.columns:
                        toxicity_score_col = candidate
                        break

                # Validate all columns found
                if not all(
                    [compound_col, super_category_col, endpoint_col, toxicity_score_col]
                ):
                    raise ValueError(
                        f"Required columns not found. "
                        f"Available: {df.columns.tolist()}, "
                        f"Needed: compound, super_category, endpoint, toxicity_score"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"compound='{compound_col}', "
                    f"super_category='{super_category_col}', "
                    f"endpoint='{endpoint_col}', "
                    f"toxicity_score='{toxicity_score_col}'"
                )

                # Remove rows with missing values
                initial_count = len(df)
                df_clean = df[
                    [compound_col, super_category_col, endpoint_col, toxicity_score_col]
                ].dropna()

                # Strip whitespace from string columns
                for col in [compound_col, super_category_col, endpoint_col]:
                    df_clean[col] = df_clean[col].astype(str).str.strip()

                # Filter out empty strings
                df_clean = df_clean[
                    (df_clean[compound_col] != "")
                    & (df_clean[super_category_col] != "")
                    & (df_clean[endpoint_col] != "")
                ]

                # Ensure toxicity_score is numeric
                df_clean[toxicity_score_col] = pd.to_numeric(
                    df_clean[toxicity_score_col], errors="coerce"
                )
                df_clean = df_clean.dropna(subset=[toxicity_score_col])

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Select and rename columns
                result_df = df_clean[
                    [compound_col, super_category_col, endpoint_col, toxicity_score_col]
                ].copy()

                result_df.columns = [
                    "Compound_Name",
                    "Super_Category",
                    "Endpoint",
                    "Toxicity_Score",
                ]

                # Sort by compound, super_category, endpoint
                result_df = result_df.sort_values(
                    ["Compound_Name", "Super_Category", "Endpoint"],
                    ascending=[True, True, True],
                )

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Extracted compound toxicity profiles: "
                    f"{df['Compound_Name'].nunique()} compounds, "
                    f"{df['Super_Category'].nunique()} super-categories, "
                    f"{df['Endpoint'].nunique()} endpoints, "
                    f"{len(df)} total records"
                )

            elif operation == "extract_sample_compound_group_class_ko":
                # UC-8.1: Extract Sample, Compound_Name, Group, Compound_Class, and KO
                # NOTE: Group column doesn't exist in source data - must be computed
                # Replicates grouping logic from UC-8.1 callback

                sample_column = data_processing.get("sample_column", "sample")
                compound_column = data_processing.get("compound_column", "compoundname")
                class_column = data_processing.get("class_column", "compoundclass")
                ko_column = data_processing.get("ko_column", "ko")

                logger.info(
                    f"[{use_case_id}] Computing "
                    f"extract_sample_compound_group_class_ko with dynamic grouping"
                )

                # Find columns (flexible naming)
                sample_col = None
                compound_col = None
                class_col = None
                ko_col = None

                # Sample column
                sample_candidates = [
                    sample_column,
                    "sample",
                    "Sample",
                    "sample_id",
                    "SampleID",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # Compound column
                compound_candidates = [
                    compound_column,
                    "compoundname",
                    "Compound_Name",
                    "CompoundName",
                    "compound",
                    "Compound",
                ]
                for candidate in compound_candidates:
                    if candidate in df.columns:
                        compound_col = candidate
                        break

                # Compound class column
                class_candidates = [
                    class_column,
                    "compoundclass",
                    "Compound_Class",
                    "CompoundClass",
                    "class",
                ]
                for candidate in class_candidates:
                    if candidate in df.columns:
                        class_col = candidate
                        break

                # KO column
                ko_candidates = [ko_column, "ko", "KO", "ko_id", "KO_ID"]
                for candidate in ko_candidates:
                    if candidate in df.columns:
                        ko_col = candidate
                        break

                # Validate required columns found
                required_cols = {
                    "sample": sample_col,
                    "compound": compound_col,
                    "class": class_col,
                    "ko": ko_col,
                }
                missing = [k for k, v in required_cols.items() if not v]

                if missing:
                    raise ValueError(
                        f"Required columns not found: {missing}. "
                        f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"sample='{sample_col}', "
                    f"compound='{compound_col}', "
                    f"class='{class_col}', "
                    f"ko='{ko_col}'"
                )

                # Step 1: Clean data
                initial_count = len(df)
                df_clean = df[[sample_col, compound_col, class_col, ko_col]].dropna()

                # Standardize column names for processing
                df_clean = df_clean.rename(
                    columns={
                        sample_col: "sample",
                        compound_col: "compoundname",
                        class_col: "compoundclass",
                        ko_col: "ko",
                    }
                )

                # Strip whitespace
                for col in ["sample", "compoundname", "compoundclass", "ko"]:
                    df_clean[col] = df_clean[col].astype(str).str.strip()

                # Filter out placeholder values
                placeholder_values = ["#N/D", "#N/A", "N/D", "", "nan", "None"]
                for col in ["sample", "compoundname", "compoundclass", "ko"]:
                    df_clean = df_clean[~df_clean[col].isin(placeholder_values)]

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Step 2: Group samples by compound profile (frozenset)
                logger.debug(f"[{use_case_id}] Computing compound profiles")
                compound_profile_to_group = {}
                groups = []

                unique_samples = df_clean["sample"].unique()
                for sample in unique_samples:
                    compounds = frozenset(
                        df_clean.loc[
                            df_clean["sample"] == sample, "compoundname"
                        ].unique()
                    )

                    if compounds:
                        profile_hash = hash(compounds)
                        if profile_hash in compound_profile_to_group:
                            group_idx = compound_profile_to_group[profile_hash]
                            groups[group_idx]["samples"].append(sample)
                        else:
                            new_group = {
                                "compounds": list(compounds),
                                "samples": [sample],
                            }
                            groups.append(new_group)
                            compound_profile_to_group[profile_hash] = len(groups) - 1

                # Add group labels
                df_clean["_group"] = None
                for i, group in enumerate(groups):
                    label = f"Group {i + 1}"
                    df_clean.loc[
                        df_clean["sample"].isin(group["samples"]), "_group"
                    ] = label

                grouped_df = df_clean.dropna(subset=["_group"])
                logger.debug(f"[{use_case_id}] Created {len(groups)} initial groups")

                # Step 3: Apply greedy set cover minimization
                logger.debug(f"[{use_case_id}] Applying set cover minimization")
                group_compounds = (
                    grouped_df.groupby("_group")["compoundname"]
                    .apply(set)
                    .reset_index()
                )
                all_compounds = set(grouped_df["compoundname"].unique())
                selected_groups = []

                while all_compounds:
                    best_group = None
                    max_cover = -1

                    for _, row in group_compounds.iterrows():
                        coverage = len(all_compounds.intersection(row["compoundname"]))
                        if coverage > max_cover:
                            max_cover = coverage
                            best_group = row["_group"]

                    if best_group is None or max_cover == 0:
                        break

                    selected_groups.append(best_group)
                    covered = group_compounds.loc[
                        group_compounds["_group"] == best_group, "compoundname"
                    ].iloc[0]
                    all_compounds -= covered
                    group_compounds = group_compounds[
                        group_compounds["_group"] != best_group
                    ]

                logger.debug(
                    f"[{use_case_id}] Selected {len(selected_groups)} minimal groups"
                )

                # Step 4: Filter to selected groups only
                result_df = grouped_df[
                    grouped_df["_group"].isin(selected_groups)
                ].copy()

                # Rename columns to standardized names
                result_df = result_df[
                    ["sample", "compoundname", "_group", "compoundclass", "ko"]
                ]
                result_df.columns = [
                    "Sample",
                    "Compound_Name",
                    "Group",
                    "Compound_Class",
                    "KO",
                ]

                # Sort by group, sample, compound
                result_df = result_df.sort_values(
                    ["Group", "Sample", "Compound_Name"], ascending=[True, True, True]
                )

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Extracted minimal sample grouping: "
                    f"{df['Sample'].nunique()} samples, "
                    f"{df['Compound_Name'].nunique()} compounds, "
                    f"{df['Group'].nunique()} minimal groups, "
                    f"{df['Compound_Class'].nunique()} classes, "
                    f"{len(df)} total records"
                )

            elif operation == "calculate_regulatory_compliance_scores":
                # UC-1.5: Calculate compliance scores (Sample × Agency)
                # Replicates HeatmapScoredStrategy compound_compliance logic
                sample_column = data_processing.get("sample_column", "sample")
                agency_column = data_processing.get("agency_column", "referenceAG")
                compound_column = data_processing.get("compound_column", "compoundname")

                logger.info(f"[{use_case_id}] Computing regulatory compliance scores")

                # Find columns (flexible naming)
                sample_col = None
                agency_col = None
                compound_col = None

                # Sample column
                sample_candidates = [
                    sample_column,
                    "sample",
                    "Sample",
                    "sample_id",
                    "SampleID",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # Agency column
                agency_candidates = [
                    agency_column,
                    "Agency",
                    "agency",
                    "referenceAG",
                    "Regulatory_Agency",
                ]
                for candidate in agency_candidates:
                    if candidate in df.columns:
                        agency_col = candidate
                        break

                # Compound column
                compound_candidates = [
                    compound_column,
                    "compoundname",
                    "Compound_Name",
                    "Compound",
                    "compound",
                ]
                for candidate in compound_candidates:
                    if candidate in df.columns:
                        compound_col = candidate
                        break

                # Validate required columns
                required_cols = {
                    "sample": sample_col,
                    "agency": agency_col,
                    "compound": compound_col,
                }
                missing = [k for k, v in required_cols.items() if not v]

                if missing:
                    raise ValueError(
                        f"Required columns not found: {missing}. "
                        f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"sample='{sample_col}', "
                    f"agency='{agency_col}', "
                    f"compound='{compound_col}'"
                )

                # Clean data
                initial_count = len(df)
                df_clean = df[[sample_col, agency_col, compound_col]].dropna()

                # Standardize column names
                df_clean = df_clean.rename(
                    columns={
                        sample_col: "sample",
                        agency_col: "agency",
                        compound_col: "compound",
                    }
                )

                # Strip whitespace
                for col in ["sample", "agency", "compound"]:
                    df_clean[col] = df_clean[col].astype(str).str.strip()

                # Remove placeholder values
                placeholder_values = ["#N/D", "#N/A", "N/D", "", "nan", "None"]
                for col in ["sample", "agency", "compound"]:
                    df_clean = df_clean[~df_clean[col].isin(placeholder_values)]

                # Remove duplicates
                df_clean = df_clean.drop_duplicates()

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Calculate compliance scores
                # Step 1: Define compound universe for each agency
                agency_compounds = (
                    df_clean.groupby("agency")["compound"].unique().apply(set)
                )

                # Step 2: Identify compounds for each sample
                sample_compounds = (
                    df_clean.groupby("sample")["compound"].unique().apply(set)
                )

                logger.debug(
                    f"[{use_case_id}] Found {len(sample_compounds)} "
                    f"samples and {len(agency_compounds)} agencies"
                )

                # Step 3: Calculate compliance scores
                scorecard_data = []
                for sample, s_compounds in sample_compounds.items():
                    for agency, a_compounds in agency_compounds.items():
                        # Find intersection
                        shared = s_compounds.intersection(a_compounds)

                        # Calculate score as percentage
                        if len(a_compounds) > 0:
                            score = (len(shared) / len(a_compounds)) * 100
                        else:
                            score = 0

                        scorecard_data.append(
                            {
                                "Sample": sample,
                                "Regulatory_Agency": agency,
                                "Compliance_Score": round(score, 1),
                            }
                        )

                # Convert to DataFrame
                result_df = pd.DataFrame(scorecard_data)

                # Sort by sample and agency
                result_df = result_df.sort_values(
                    ["Sample", "Regulatory_Agency"], ascending=[True, True]
                )

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Calculated compliance scores: "
                    f"{df['Sample'].nunique()} samples, "
                    f"{df['Regulatory_Agency'].nunique()} agencies, "
                    f"{len(df)} total scores, "
                    f"score range: [{df['Compliance_Score'].min():.1f}%, "
                    f"{df['Compliance_Score'].max():.1f}%]"
                )

            elif operation == "calculate_ko_completeness_scores":
                # UC-8.2, 8.3, 8.5: Calculate KO completeness scores
                # Replicates HeatmapScoredStrategy ko_completeness logic
                sample_column = data_processing.get("sample_column", "Sample")
                category_column = data_processing.get(
                    "category_column", "Compound_Class"
                )
                ko_column = data_processing.get("ko_column", "KO")

                logger.info(f"[{use_case_id}] Computing KO completeness scores")

                # Find columns (flexible naming)
                sample_col = None
                category_col = None
                ko_col = None

                # Sample column
                sample_candidates = [
                    sample_column,
                    "sample",
                    "Sample",
                    "sample_id",
                    "SampleID",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # Category column (Compound_Class or Pathway)
                category_candidates = [
                    category_column,
                    "Compound_Class",
                    "compound_class",
                    "CompoundClass",
                    "Pathway",
                    "pathway",
                ]
                for candidate in category_candidates:
                    if candidate in df.columns:
                        category_col = candidate
                        break

                # KO column
                ko_candidates = [ko_column, "ko", "KO", "ko_id", "KO_ID"]
                for candidate in ko_candidates:
                    if candidate in df.columns:
                        ko_col = candidate
                        break

                # Validate required columns
                required_cols = {
                    "sample": sample_col,
                    "category": category_col,
                    "ko": ko_col,
                }
                missing = [k for k, v in required_cols.items() if not v]

                if missing:
                    raise ValueError(
                        f"Required columns not found: {missing}. "
                        f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"sample='{sample_col}', "
                    f"category='{category_col}', "
                    f"ko='{ko_col}'"
                )

                # Clean data
                initial_count = len(df)
                df_clean = df[[sample_col, category_col, ko_col]].dropna()

                # Standardize column names
                df_clean = df_clean.rename(
                    columns={
                        sample_col: "sample",
                        category_col: "category",
                        ko_col: "ko",
                    }
                )

                # Strip whitespace
                for col in ["sample", "category", "ko"]:
                    df_clean[col] = df_clean[col].astype(str).str.strip()

                # Remove placeholder values
                placeholder_values = ["#N/D", "#N/A", "N/D", "", "nan", "None"]
                for col in ["sample", "category", "ko"]:
                    df_clean = df_clean[~df_clean[col].isin(placeholder_values)]

                # Remove duplicates
                df_clean = df_clean.drop_duplicates()

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Calculate KO completeness scores
                # Step 1: Count unique KOs per (sample, category)
                sample_ko_counts = df_clean.groupby(["sample", "category"])[
                    "ko"
                ].nunique()

                # Step 2: Calculate total unique KOs per category
                total_ko_per_category = df_clean.groupby("category")["ko"].nunique()

                # Filter out categories with no KOs
                total_ko_per_category = total_ko_per_category[total_ko_per_category > 0]

                logger.debug(
                    f"[{use_case_id}] Found {len(sample_ko_counts)} "
                    f"sample-category pairs, "
                    f"{len(total_ko_per_category)} categories"
                )

                # Step 3: Calculate completeness scores
                scorecard_data = []
                for (sample, category), sample_kos in sample_ko_counts.items():
                    if category in total_ko_per_category.index:
                        total_kos = total_ko_per_category[category]
                        score = (sample_kos / total_kos) * 100

                        scorecard_data.append(
                            {
                                "Sample": sample,
                                "Category": category,
                                "Completeness_Score": round(score, 1),
                            }
                        )

                # Convert to DataFrame
                result_df = pd.DataFrame(scorecard_data)

                # Sort by sample and category
                result_df = result_df.sort_values(
                    ["Sample", "Category"], ascending=[True, True]
                )

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Calculated KO completeness scores: "
                    f"{df['Sample'].nunique()} samples, "
                    f"{df['Category'].nunique()} categories, "
                    f"{len(df)} total scores, "
                    f"score range: [{df['Completeness_Score'].min():.1f}%, "
                    f"{df['Completeness_Score'].max():.1f}%]"
                )

            elif operation == "aggregate_sample_compound_interactions":
                # UC-5.1: Count interactions between samples and compound classes
                sample_column = data_processing.get("sample_column", "sample")
                compound_class_column = data_processing.get(
                    "compound_class_column", "compoundclass"
                )
                result_column = data_processing.get(
                    "result_column", "Interaction_Count"
                )

                logger.info(
                    f"[{use_case_id}] Computing "
                    f"aggregate_sample_compound_interactions"
                )

                # Find columns (flexible naming)
                sample_col = None
                compound_class_col = None

                # Sample column
                sample_candidates = [
                    sample_column,
                    "Sample",
                    "sample",
                    "sample_id",
                    "SampleID",
                    "genome",
                    "Genome",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # Compound class column
                compound_class_candidates = [
                    compound_class_column,
                    "Compound_Class",
                    "compoundclass",
                    "compound_class",
                    "CompoundClass",
                    "chemical_class",
                ]
                for candidate in compound_class_candidates:
                    if candidate in df.columns:
                        compound_class_col = candidate
                        break

                # Validate all columns found
                if not sample_col or not compound_class_col:
                    raise ValueError(
                        f"Required columns not found. "
                        f"Available: {df.columns.tolist()}, "
                        f"Needed: sample (one of {sample_candidates}), "
                        f"compound_class (one of {compound_class_candidates})"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"sample='{sample_col}', "
                    f"compound_class='{compound_class_col}'"
                )

                # Remove rows with missing values
                initial_count = len(df)
                df_clean = df[[sample_col, compound_class_col]].dropna()

                # Strip whitespace and remove placeholders
                df_clean[sample_col] = df_clean[sample_col].astype(str).str.strip()
                df_clean[compound_class_col] = (
                    df_clean[compound_class_col].astype(str).str.strip()
                )

                # Filter out placeholder values
                df_clean = df_clean[
                    ~df_clean[compound_class_col].isin(["#N/D", "#N/A", "N/D", ""])
                ]
                df_clean = df_clean[
                    ~df_clean[sample_col].isin(["#N/D", "#N/A", "N/D", ""])
                ]

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Group by sample and compound_class, count interactions
                result_df = (
                    df_clean.groupby([sample_col, compound_class_col])
                    .size()
                    .reset_index()
                )
                result_df.columns = ["Sample", "Compound_Class", result_column]

                # Sort by sample and compound class
                result_df = result_df.sort_values(
                    ["Sample", "Compound_Class"], ascending=[True, True]
                )

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Applied sample-compound aggregation: "
                    f"grouped by [{sample_col}, {compound_class_col}], "
                    f"counted interactions -> {result_column}"
                )
                logger.info(
                    f"[{use_case_id}] Processed data shape: {df.shape}, "
                    f"{df['Sample'].nunique()} samples, "
                    f"{df['Compound_Class'].nunique()} compound classes, "
                    f"{len(df)} interactions"
                )

            elif operation == "aggregate_sample_similarity_pairwise":
                # UC-5.2: Compute pairwise similarity between samples based on shared compounds
                sample_column = data_processing.get("sample_column", "sample")
                shared_column = data_processing.get("shared_column", "compoundname")

                logger.info(
                    f"[{use_case_id}] Computing "
                    f"aggregate_sample_similarity_pairwise"
                )

                # Find columns (flexible naming)
                sample_col = None
                shared_col = None

                # Sample column
                sample_candidates = [
                    sample_column,
                    "Sample",
                    "sample",
                    "sample_id",
                    "SampleID",
                    "genome",
                    "Genome",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # Shared column (compound name)
                shared_candidates = [
                    shared_column,
                    "compoundname",
                    "Compound_Name",
                    "compound_name",
                    "CompoundName",
                    "compound",
                    "Compound",
                ]
                for candidate in shared_candidates:
                    if candidate in df.columns:
                        shared_col = candidate
                        break

                # Validate all columns found
                if not sample_col or not shared_col:
                    raise ValueError(
                        f"Required columns not found. "
                        f"Available: {df.columns.tolist()}, "
                        f"Needed: sample (one of {sample_candidates}), "
                        f"shared (one of {shared_candidates})"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"sample='{sample_col}', "
                    f"shared='{shared_col}'"
                )

                # Remove rows with missing values
                initial_count = len(df)
                df_clean = df[[sample_col, shared_col]].dropna()

                # Strip whitespace and remove placeholders
                df_clean[sample_col] = df_clean[sample_col].astype(str).str.strip()
                df_clean[shared_col] = df_clean[shared_col].astype(str).str.strip()

                # Filter out placeholder values
                df_clean = df_clean[
                    ~df_clean[shared_col].isin(["#N/D", "#N/A", "N/D", ""])
                ]
                df_clean = df_clean[
                    ~df_clean[sample_col].isin(["#N/D", "#N/A", "N/D", ""])
                ]

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Group by sample to get set of shared entities (compounds)
                sample_groups = (
                    df_clean.groupby(sample_col)[shared_col]
                    .apply(lambda x: set(x.unique()))
                    .to_dict()
                )

                # Get sorted list of samples
                samples = sorted(sample_groups.keys())

                logger.debug(f"[{use_case_id}] Processing {len(samples)} samples")

                # Compute pairwise intersections
                from itertools import combinations

                pairwise_data = []
                for sample1, sample2 in combinations(samples, 2):
                    shared_items = sample_groups[sample1] & sample_groups[sample2]
                    shared_count = len(shared_items)

                    if shared_count > 0:  # Only include pairs with shared compounds
                        pairwise_data.append(
                            {
                                "Sample_1": sample1,
                                "Sample_2": sample2,
                                "Shared_Compound_Count": shared_count,
                            }
                        )

                # Convert to DataFrame
                result_df = pd.DataFrame(pairwise_data)

                # Sort by shared count (descending) then by sample names
                if not result_df.empty:
                    result_df = result_df.sort_values(
                        ["Shared_Compound_Count", "Sample_1", "Sample_2"],
                        ascending=[False, True, True],
                    )

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Applied pairwise sample similarity: "
                    f"computed {len(df)} sample pairs with shared compounds"
                )
                logger.info(
                    f"[{use_case_id}] Processed data shape: {df.shape}, "
                    f"{len(samples)} unique samples, "
                    f"{len(df)} sample pairs"
                )

            elif operation == "aggregate_sample_agency_interactions":
                # UC-5.3: Count interactions between samples and regulatory agencies
                sample_column = data_processing.get("sample_column", "sample")
                agency_column = data_processing.get("agency_column", "referenceag")
                result_column = data_processing.get(
                    "result_column", "Interaction_Count"
                )

                logger.info(
                    f"[{use_case_id}] Computing "
                    f"aggregate_sample_agency_interactions"
                )

                # Find columns (flexible naming)
                sample_col = None
                agency_col = None

                # Sample column
                sample_candidates = [
                    sample_column,
                    "Sample",
                    "sample",
                    "sample_id",
                    "SampleID",
                    "genome",
                    "Genome",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # Agency column
                agency_candidates = [
                    agency_column,
                    "referenceAG",
                    "referenceag",
                    "ReferenceAG",
                    "reference_ag",
                    "Agency",
                    "agency",
                ]
                for candidate in agency_candidates:
                    if candidate in df.columns:
                        agency_col = candidate
                        break

                # Validate all columns found
                if not sample_col or not agency_col:
                    raise ValueError(
                        f"Required columns not found. "
                        f"Available: {df.columns.tolist()}, "
                        f"Needed: sample (one of {sample_candidates}), "
                        f"agency (one of {agency_candidates})"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"sample='{sample_col}', "
                    f"agency='{agency_col}'"
                )

                # Remove rows with missing values
                initial_count = len(df)
                df_clean = df[[sample_col, agency_col]].dropna()

                # Strip whitespace and remove placeholders
                df_clean[sample_col] = df_clean[sample_col].astype(str).str.strip()
                df_clean[agency_col] = df_clean[agency_col].astype(str).str.strip()

                # Filter out placeholder values
                df_clean = df_clean[
                    ~df_clean[agency_col].isin(["#N/D", "#N/A", "N/D", "", "nan"])
                ]
                df_clean = df_clean[
                    ~df_clean[sample_col].isin(["#N/D", "#N/A", "N/D", ""])
                ]

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Group by sample and agency, count interactions
                result_df = (
                    df_clean.groupby([sample_col, agency_col]).size().reset_index()
                )
                result_df.columns = ["Sample", "ReferenceAG", result_column]

                # Sort by sample and agency
                result_df = result_df.sort_values(
                    ["Sample", "ReferenceAG"], ascending=[True, True]
                )

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Applied sample-agency aggregation: "
                    f"grouped by [{sample_col}, {agency_col}], "
                    f"counted interactions -> {result_column}"
                )
                logger.info(
                    f"[{use_case_id}] Processed data shape: {df.shape}, "
                    f"{df['Sample'].nunique()} samples, "
                    f"{df['ReferenceAG'].nunique()} regulatory agencies, "
                    f"{len(df)} interactions"
                )

            elif operation == "aggregate_risk_agency_concordance":
                # UC-7.2: Compute intersections between regulatory agencies and high-risk compounds
                # Cross-database processing: BioRemPP + ToxCSM
                threshold = data_processing.get("threshold", 0.7)

                logger.info(
                    f"[{use_case_id}] Computing "
                    f"aggregate_risk_agency_concordance (threshold={threshold})"
                )

                # This operation requires BOTH databases
                if "toxcsm_df" not in merged_data:
                    raise ValueError(
                        "UC-7.2 requires ToxCSM database for risk assessment"
                    )

                # Get ToxCSM DataFrame
                toxcsm_data = merged_data["toxcsm_df"]
                df_toxcsm = pd.DataFrame(toxcsm_data)

                # Get BioRemPP DataFrame (df is already BioRemPP from primary database)
                df_biorempp = df.copy()

                logger.debug(
                    f"[{use_case_id}] BioRemPP: {len(df_biorempp)} rows, "
                    f"ToxCSM: {len(df_toxcsm)} rows"
                )

                # Find ToxCSM columns
                toxcsm_compound_col = None
                score_col = None

                compound_candidates = [
                    "compoundname",
                    "Compound_Name",
                    "compound_name",
                    "CompoundName",
                    "compound",
                    "Compound",
                ]
                for candidate in compound_candidates:
                    if candidate in df_toxcsm.columns:
                        toxcsm_compound_col = candidate
                        break

                score_candidates = ["toxicity_score", "ToxicityScore", "score", "Score"]
                for candidate in score_candidates:
                    if candidate in df_toxcsm.columns:
                        score_col = candidate
                        break

                if not toxcsm_compound_col or not score_col:
                    raise ValueError(
                        f"ToxCSM columns not found. Available: {df_toxcsm.columns.tolist()}"
                    )

                # Find BioRemPP columns
                agency_col = None
                biorempp_compound_col = None

                agency_candidates = [
                    "referenceAG",
                    "referenceag",
                    "ReferenceAG",
                    "reference_ag",
                    "Agency",
                    "agency",
                ]
                for candidate in agency_candidates:
                    if candidate in df_biorempp.columns:
                        agency_col = candidate
                        break

                for candidate in compound_candidates:
                    if candidate in df_biorempp.columns:
                        biorempp_compound_col = candidate
                        break

                if not agency_col or not biorempp_compound_col:
                    raise ValueError(
                        f"BioRemPP columns not found. Available: {df_biorempp.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using ToxCSM columns: "
                    f"compound='{toxcsm_compound_col}', score='{score_col}'"
                )
                logger.debug(
                    f"[{use_case_id}] Using BioRemPP columns: "
                    f"agency='{agency_col}', compound='{biorempp_compound_col}'"
                )

                # Extract high-risk compounds from ToxCSM
                df_toxcsm_clean = df_toxcsm[[toxcsm_compound_col, score_col]].dropna()
                df_toxcsm_clean[score_col] = pd.to_numeric(
                    df_toxcsm_clean[score_col], errors="coerce"
                )
                df_toxcsm_clean = df_toxcsm_clean.dropna()

                high_risk_df = df_toxcsm_clean[df_toxcsm_clean[score_col] >= threshold]
                high_risk_compounds = set(
                    high_risk_df[toxcsm_compound_col].astype(str).str.strip().unique()
                )

                logger.info(
                    f"[{use_case_id}] Found {len(high_risk_compounds)} "
                    f"high-risk compounds (>= {threshold})"
                )

                # Extract agency compound sets from BioRemPP
                df_biorempp_clean = df_biorempp[
                    [agency_col, biorempp_compound_col]
                ].dropna()

                df_biorempp_clean[agency_col] = (
                    df_biorempp_clean[agency_col].astype(str).str.strip()
                )
                df_biorempp_clean[biorempp_compound_col] = (
                    df_biorempp_clean[biorempp_compound_col].astype(str).str.strip()
                )

                # Remove placeholders
                df_biorempp_clean = df_biorempp_clean[
                    ~df_biorempp_clean[agency_col].isin(
                        ["#N/D", "#N/A", "N/D", "", "nan"]
                    )
                ]
                df_biorempp_clean = df_biorempp_clean[
                    ~df_biorempp_clean[biorempp_compound_col].isin(
                        ["#N/D", "#N/A", "N/D", "", "nan"]
                    )
                ]

                # Group by agency
                agency_compound_sets = (
                    df_biorempp_clean.groupby(agency_col)[biorempp_compound_col]
                    .apply(set)
                    .to_dict()
                )

                logger.info(
                    f"[{use_case_id}] Found {len(agency_compound_sets)} "
                    f"regulatory agencies"
                )

                # Compute pairwise intersections
                from itertools import combinations

                all_sets = agency_compound_sets.copy()
                all_sets["High Predicted Risk"] = high_risk_compounds

                set_names = list(all_sets.keys())
                links_list = []

                for name1, name2 in combinations(set_names, 2):
                    intersection_size = len(
                        all_sets[name1].intersection(all_sets[name2])
                    )
                    if intersection_size > 0:
                        links_list.append(
                            {
                                "Category_1": name1,
                                "Category_2": name2,
                                "Shared_Compound_Count": intersection_size,
                            }
                        )

                result_df = pd.DataFrame(links_list)

                # Sort by shared count (descending)
                if not result_df.empty:
                    result_df = result_df.sort_values(
                        "Shared_Compound_Count", ascending=False
                    )

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Applied risk-agency concordance: "
                    f"computed {len(df)} category pairs with shared compounds"
                )
                logger.info(
                    f"[{use_case_id}] Processed data shape: {df.shape}, "
                    f"{len(set_names)} categories (agencies + risk), "
                    f"{len(df)} intersection pairs"
                )

            elif operation == "aggregate_pathway_sample_gene":
                # UC-4.5: Aggregate pathway, sample, and gene data
                pathway_column = data_processing.get("pathway_column", "Pathway")
                sample_column = data_processing.get("sample_column", "Sample")
                gene_column = data_processing.get("gene_column", "GeneSymbol")

                logger.info(
                    f"[{use_case_id}] Computing " f"aggregate_pathway_sample_gene"
                )

                # Find columns (flexible naming)
                pathway_col = None
                sample_col = None
                gene_col = None

                # Pathway column
                pathway_candidates = [
                    pathway_column,
                    "pathway",
                    "pathname",
                    "pathway_name",
                    "Pathway_Name",
                ]
                for candidate in pathway_candidates:
                    if candidate in df.columns:
                        pathway_col = candidate
                        break

                # Sample column
                sample_candidates = [
                    sample_column,
                    "sample",
                    "sample_id",
                    "SampleID",
                    "genome",
                    "Genome",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # Gene column
                gene_candidates = [
                    gene_column,
                    "genesymbol",
                    "gene_symbol",
                    "Gene_Symbol",
                    "gene",
                    "Gene",
                ]
                for candidate in gene_candidates:
                    if candidate in df.columns:
                        gene_col = candidate
                        break

                # Validate all columns found
                if not pathway_col or not sample_col or not gene_col:
                    raise ValueError(
                        f"Required columns not found. "
                        f"Available: {df.columns.tolist()}, "
                        f"Needed: pathway (one of {pathway_candidates}), "
                        f"sample (one of {sample_candidates}), "
                        f"gene (one of {gene_candidates})"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"pathway='{pathway_col}', "
                    f"sample='{sample_col}', "
                    f"gene='{gene_col}'"
                )

                # Remove rows with missing values
                initial_count = len(df)
                df_clean = df[[pathway_col, sample_col, gene_col]].dropna()

                # Strip whitespace
                df_clean[pathway_col] = df_clean[pathway_col].astype(str).str.strip()
                df_clean[sample_col] = df_clean[sample_col].astype(str).str.strip()
                df_clean[gene_col] = df_clean[gene_col].astype(str).str.strip()

                # Filter out placeholder values
                df_clean = df_clean[
                    ~df_clean[pathway_col].isin(["#N/D", "#N/A", "N/D", ""])
                ]
                df_clean = df_clean[
                    ~df_clean[sample_col].isin(["#N/D", "#N/A", "N/D", ""])
                ]
                df_clean = df_clean[
                    ~df_clean[gene_col].isin(["#N/D", "#N/A", "N/D", ""])
                ]

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Get unique combinations (remove duplicates)
                result_df = df_clean[
                    [pathway_col, sample_col, gene_col]
                ].drop_duplicates()

                # Rename columns to standard names
                result_df.columns = ["Pathway", "Sample", "Gene"]

                # Sort by pathway, sample, gene
                result_df = result_df.sort_values(
                    ["Pathway", "Sample", "Gene"], ascending=[True, True, True]
                )

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Applied pathway-sample-gene extraction: "
                    f"extracted unique combinations from "
                    f"[{pathway_col}, {sample_col}, {gene_col}]"
                )
                logger.info(
                    f"[{use_case_id}] Processed data shape: {df.shape}, "
                    f"{df['Pathway'].nunique()} pathways, "
                    f"{df['Sample'].nunique()} samples, "
                    f"{df['Gene'].nunique()} genes, "
                    f"{len(df)} unique combinations"
                )

            elif operation == "aggregate_compound_sample_ko_count":
                # UC-4.6: Aggregate compound class, compound name, sample, and count unique KOs
                compound_class_column = data_processing.get(
                    "compound_class_column", "Compound_Class"
                )
                compound_name_column = data_processing.get(
                    "compound_name_column", "Compound_Name"
                )
                sample_column = data_processing.get("sample_column", "Sample")
                ko_column = data_processing.get("ko_column", "KO")
                result_column = data_processing.get("result_column", "Gene_Count")

                logger.info(
                    f"[{use_case_id}] Computing " f"aggregate_compound_sample_ko_count"
                )

                # Find columns (flexible naming)
                compound_class_col = None
                compound_name_col = None
                sample_col = None
                ko_col = None

                # Compound class column
                class_candidates = [
                    compound_class_column,
                    "compound_class",
                    "CompoundClass",
                    "Class",
                    "compoundclass",
                ]
                for candidate in class_candidates:
                    if candidate in df.columns:
                        compound_class_col = candidate
                        break

                # Compound name column
                name_candidates = [
                    compound_name_column,
                    "compound_name",
                    "CompoundName",
                    "compoundname",
                    "Compound",
                ]
                for candidate in name_candidates:
                    if candidate in df.columns:
                        compound_name_col = candidate
                        break

                # Sample column
                sample_candidates = [
                    sample_column,
                    "sample",
                    "sample_id",
                    "SampleID",
                    "genome",
                    "Genome",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # KO column
                ko_candidates = [ko_column, "ko", "KO_ID", "gene"]
                for candidate in ko_candidates:
                    if candidate in df.columns:
                        ko_col = candidate
                        break

                # Validate all columns found
                if not all([compound_class_col, compound_name_col, sample_col, ko_col]):
                    raise ValueError(
                        f"Required columns not found. "
                        f"Available: {df.columns.tolist()}, "
                        f"Needed: compound_class, compound_name, sample, ko"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"class='{compound_class_col}', "
                    f"name='{compound_name_col}', "
                    f"sample='{sample_col}', "
                    f"ko='{ko_col}'"
                )

                # Remove rows with missing values
                initial_count = len(df)
                df_clean = df[
                    [compound_class_col, compound_name_col, sample_col, ko_col]
                ].dropna()

                # Strip whitespace
                for col in [compound_class_col, compound_name_col, sample_col, ko_col]:
                    df_clean[col] = df_clean[col].astype(str).str.strip()

                # Filter out placeholder values
                for col in [compound_class_col, compound_name_col, sample_col]:
                    df_clean = df_clean[
                        ~df_clean[col].isin(["#N/D", "#N/A", "N/D", ""])
                    ]

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Group by compound_class, compound_name, sample and count unique KOs
                result_df = (
                    df_clean.groupby(
                        [compound_class_col, compound_name_col, sample_col]
                    )[ko_col]
                    .nunique()
                    .reset_index()
                )
                result_df.columns = [
                    "Compound_Class",
                    "Compound_Name",
                    "Sample",
                    result_column,
                ]

                # Sort by compound class, compound name, sample
                result_df = result_df.sort_values(
                    ["Compound_Class", "Compound_Name", "Sample"],
                    ascending=[True, True, True],
                )

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Applied compound-sample-KO aggregation: "
                    f"grouped by [{compound_class_col}, {compound_name_col}, {sample_col}], "
                    f"counted unique KOs -> {result_column}"
                )
                logger.info(
                    f"[{use_case_id}] Processed data shape: {df.shape}, "
                    f"{df['Compound_Class'].nunique()} compound classes, "
                    f"{df['Compound_Name'].nunique()} compounds, "
                    f"{df['Sample'].nunique()} samples, "
                    f"{len(df)} combinations"
                )

            elif operation == "extract_gene_compound_associations":
                # UC-4.7: Extract unique gene-compound associations
                gene_column = data_processing.get("gene_column", "GeneSymbol")
                compound_column = data_processing.get(
                    "compound_column", "Compound_Name"
                )

                logger.info(
                    f"[{use_case_id}] Computing " f"extract_gene_compound_associations"
                )

                # Find columns (flexible naming)
                gene_col = None
                compound_col = None

                # Gene column
                gene_candidates = [
                    gene_column,
                    "genesymbol",
                    "GeneSymbol",
                    "gene_symbol",
                    "Gene_Symbol",
                    "gene",
                    "Gene",
                ]
                for candidate in gene_candidates:
                    if candidate in df.columns:
                        gene_col = candidate
                        break

                # Compound column
                compound_candidates = [
                    compound_column,
                    "compoundname",
                    "CompoundName",
                    "compound_name",
                    "Compound_Name",
                    "compound",
                    "Compound",
                ]
                for candidate in compound_candidates:
                    if candidate in df.columns:
                        compound_col = candidate
                        break

                # Validate columns found
                if not gene_col:
                    raise ValueError(
                        f"Gene column not found. " f"Available: {df.columns.tolist()}"
                    )

                if not compound_col:
                    raise ValueError(
                        f"Compound column not found. "
                        f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"gene='{gene_col}', "
                    f"compound='{compound_col}'"
                )

                # Remove rows with missing values
                initial_count = len(df)
                df_clean = df[[gene_col, compound_col]].dropna()

                # Strip whitespace
                for col in [gene_col, compound_col]:
                    df_clean[col] = df_clean[col].astype(str).str.strip()

                # Filter out placeholder values
                for col in [gene_col, compound_col]:
                    df_clean = df_clean[
                        ~df_clean[col].isin(["#N/D", "#N/A", "N/D", ""])
                    ]

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Extract unique gene-compound associations
                result_df = (
                    df_clean[[gene_col, compound_col]]
                    .drop_duplicates()
                    .sort_values([gene_col, compound_col])
                )

                # Standardize column names
                result_df.columns = ["Gene", "Compound_Name"]

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Extracted unique gene-compound associations: "
                    f"{len(df)} unique pairs from {df['Gene'].nunique()} genes "
                    f"and {df['Compound_Name'].nunique()} compounds"
                )

            elif operation == "extract_gene_sample_associations":
                # UC-4.8: Extract unique gene-sample associations
                gene_column = data_processing.get("gene_column", "GeneSymbol")
                sample_column = data_processing.get("sample_column", "Sample")

                logger.info(
                    f"[{use_case_id}] Computing " f"extract_gene_sample_associations"
                )

                # Find columns (flexible naming)
                gene_col = None
                sample_col = None

                # Gene column
                gene_candidates = [
                    gene_column,
                    "genesymbol",
                    "GeneSymbol",
                    "gene_symbol",
                    "Gene_Symbol",
                    "gene",
                    "Gene",
                ]
                for candidate in gene_candidates:
                    if candidate in df.columns:
                        gene_col = candidate
                        break

                # Sample column
                sample_candidates = [
                    sample_column,
                    "sample",
                    "Sample",
                    "sample_id",
                    "SampleID",
                    "genome",
                    "Genome",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # Validate columns found
                if not gene_col:
                    raise ValueError(
                        f"Gene column not found. " f"Available: {df.columns.tolist()}"
                    )

                if not sample_col:
                    raise ValueError(
                        f"Sample column not found. " f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"gene='{gene_col}', "
                    f"sample='{sample_col}'"
                )

                # Remove rows with missing values
                initial_count = len(df)
                df_clean = df[[gene_col, sample_col]].dropna()

                # Strip whitespace
                for col in [gene_col, sample_col]:
                    df_clean[col] = df_clean[col].astype(str).str.strip()

                # Filter out placeholder values
                for col in [gene_col, sample_col]:
                    df_clean = df_clean[
                        ~df_clean[col].isin(["#N/D", "#N/A", "N/D", ""])
                    ]

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Extract unique gene-sample associations
                result_df = (
                    df_clean[[gene_col, sample_col]]
                    .drop_duplicates()
                    .sort_values([gene_col, sample_col])
                )

                # Standardize column names
                result_df.columns = ["Gene", "Sample"]

                df = result_df.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Extracted unique gene-sample associations: "
                    f"{len(df)} unique pairs from {df['Gene'].nunique()} genes "
                    f"and {df['Sample'].nunique()} samples"
                )

            elif operation == "upset_data":
                # UC-1.1: Generate Database-KO pairs for UpSet plot
                # Extract unique KOs from each database and format as 2 columns
                logger.info(
                    f"[{use_case_id}] Computing upset_data: "
                    f"extracting Database-KO pairs from all databases"
                )

                # Collect all Database-KO pairs
                all_pairs = []

                # Get database list from config (we need all 3 databases)
                databases_to_process = ["biorempp_df", "hadeg_df", "kegg_df"]

                for db_name in databases_to_process:
                    if db_name not in merged_data:
                        logger.warning(
                            f"[{use_case_id}] Database '{db_name}' not found, skipping"
                        )
                        continue

                    db_df = pd.DataFrame(merged_data[db_name])

                    if db_df.empty:
                        logger.warning(
                            f"[{use_case_id}] Database '{db_name}' is empty, skipping"
                        )
                        continue

                    # Find KO column (case-insensitive)
                    ko_col = None
                    ko_candidates = ["ko", "KO", "gene", "Gene", "kegg_ko", "KEGG_KO"]

                    for candidate in ko_candidates:
                        if candidate in db_df.columns:
                            ko_col = candidate
                            break

                    # Case-insensitive fallback
                    if not ko_col:
                        lower_cols = {col.lower(): col for col in db_df.columns}
                        for candidate in ["ko", "gene", "kegg_ko"]:
                            if candidate in lower_cols:
                                ko_col = lower_cols[candidate]
                                break

                    if not ko_col:
                        logger.warning(
                            f"[{use_case_id}] No KO column found in '{db_name}', "
                            f"available columns: {db_df.columns.tolist()}"
                        )
                        continue

                    # Extract and normalize KO identifiers
                    ko_series = (
                        db_df[ko_col].fillna("").astype(str).str.strip().str.upper()
                    )

                    # Remove empty strings and get unique KOs
                    unique_kos = ko_series[ko_series != ""].unique()

                    # Create Database name (clean format)
                    db_display_name = db_name.replace("_df", "").upper()
                    if db_display_name == "BIOREMPP":
                        db_display_name = "BioRemPP"
                    elif db_display_name == "HADEG":
                        db_display_name = "HADEG"
                    elif db_display_name == "KEGG":
                        db_display_name = "KEGG"

                    # Add pairs to list
                    for ko in unique_kos:
                        all_pairs.append({"Database": db_display_name, "KO": ko})

                    logger.debug(
                        f"[{use_case_id}] Extracted {len(unique_kos)} unique KOs "
                        f"from '{db_display_name}'"
                    )

                # Convert to DataFrame
                df = pd.DataFrame(all_pairs)

                if df.empty:
                    raise ValueError(
                        "No KO data found in any database for upset analysis"
                    )

                logger.info(
                    f"[{use_case_id}] Upset data generated: "
                    f"{len(df)} Database-KO pairs from "
                    f"{df['Database'].nunique()} databases"
                )
                logger.debug(
                    f"[{use_case_id}] Database distribution:\n"
                    f"{df['Database'].value_counts()}"
                )

            elif operation == "upset_agency_compound":
                # UC-1.2: Generate Agency-Compound pairs for UpSet plot
                # Extract unique compounds per regulatory agency
                logger.info(
                    f"[{use_case_id}] Computing upset_agency_compound: "
                    f"extracting Agency-Compound pairs from BioRemPP"
                )

                # Find compound and agency columns (case-insensitive)
                compound_col = None
                agency_col = None

                # Compound column candidates
                compound_candidates = [
                    "compoundname",
                    "Compound_Name",
                    "Compound Name",
                    "compound_name",
                    "compound",
                    "Chemical",
                    "chemical_name",
                ]

                for candidate in compound_candidates:
                    if candidate in df.columns:
                        compound_col = candidate
                        break

                # Case-insensitive fallback for compound
                if not compound_col:
                    lower_cols = {col.lower(): col for col in df.columns}
                    for candidate in [
                        "compoundname",
                        "compound_name",
                        "compound name",
                        "compound",
                        "chemical",
                    ]:
                        if candidate in lower_cols:
                            compound_col = lower_cols[candidate]
                            break

                # Agency column candidates
                agency_candidates = [
                    "referenceAG",
                    "Agency",
                    "reference_ag",
                    "agency",
                    "regulatory_agency",
                    "source",
                ]

                for candidate in agency_candidates:
                    if candidate in df.columns:
                        agency_col = candidate
                        break

                # Case-insensitive fallback for agency
                if not agency_col:
                    lower_cols = {col.lower(): col for col in df.columns}
                    for candidate in [
                        "referenceag",
                        "agency",
                        "reference_ag",
                        "regulatory_agency",
                        "source",
                    ]:
                        if candidate in lower_cols:
                            agency_col = lower_cols[candidate]
                            break

                if not compound_col or not agency_col:
                    raise ValueError(
                        f"Required columns not found in BioRemPP. "
                        f"Available: {df.columns.tolist()}, "
                        f"Needed: compound column (one of {compound_candidates}) "
                        f"and agency column (one of {agency_candidates})"
                    )

                logger.debug(
                    f"[{use_case_id}] Found columns: "
                    f"compound='{compound_col}', agency='{agency_col}'"
                )

                # Extract and normalize data
                compound_series = (
                    df[compound_col].fillna("").astype(str).str.strip().str.upper()
                )

                agency_series = df[agency_col].fillna("").astype(str).str.strip()

                # Create pairs (removing empty values)
                pairs_df = pd.DataFrame(
                    {"Reference": agency_series, "Compound": compound_series}
                )

                # Remove empty strings
                pairs_df = pairs_df[
                    (pairs_df["Reference"] != "") & (pairs_df["Compound"] != "")
                ]

                # Get unique pairs only
                df = pairs_df.drop_duplicates().reset_index(drop=True)

                if df.empty:
                    raise ValueError("No valid Agency-Compound pairs found in BioRemPP")

                logger.info(
                    f"[{use_case_id}] Upset agency-compound data generated: "
                    f"{len(df)} unique pairs from "
                    f"{df['Reference'].nunique()} agencies"
                )
                logger.debug(
                    f"[{use_case_id}] Agency distribution:\n"
                    f"{df['Reference'].value_counts()}"
                )

            elif operation == "sample_correlation_matrix":
                # UC-3.4: Generate Sample x Sample correlation matrix
                # This is the SAME data shown in the correlogram
                group_by = data_processing.get("group_by", "Sample")
                pivot_column = data_processing.get("pivot_column", "KO")
                correlation_method = data_processing.get(
                    "correlation_method", "pearson"
                )

                logger.info(
                    f"[{use_case_id}] Computing correlation matrix: "
                    f"group_by={group_by}, pivot={pivot_column}, "
                    f"method={correlation_method}"
                )

                # Step 1: Clean column names (flexible mapping)
                sample_col = None
                pivot_col_found = None

                # Try to find Sample column
                sample_candidates = [
                    "Sample",
                    "sample",
                    "sample_id",
                    "Sample_ID",
                    "sampleID",
                    "genome",
                    "Genome",
                    "organism",
                ]
                for col_name in sample_candidates:
                    if col_name in df.columns:
                        sample_col = col_name
                        break

                # Try to find pivot column based on config
                # (could be KO, Compound_Name, or other)
                if pivot_column == "KO":
                    pivot_candidates = [
                        "KO",
                        "ko",
                        "ko_id",
                        "KO_ID",
                        "kegg_orthology",
                        "KEGG_Orthology",
                        "orthology",
                    ]
                elif pivot_column == "Compound_Name":
                    pivot_candidates = [
                        "Compound_Name",
                        "compound_name",
                        "CompoundName",
                        "compound",
                        "Compound",
                        "chemical",
                        "Chemical",
                        "chemical_name",
                        "Chemical_Name",
                    ]
                else:
                    # Generic fallback
                    pivot_candidates = [pivot_column]

                for col_name in pivot_candidates:
                    if col_name in df.columns:
                        pivot_col_found = col_name
                        break

                if not sample_col or not pivot_col_found:
                    raise ValueError(
                        f"Required columns not found. "
                        f"Available: {df.columns.tolist()}, "
                        f"Needed: Sample (one of {sample_candidates}) "
                        f"and {pivot_column} "
                        f"(one of {pivot_candidates})"
                    )

                logger.debug(
                    f"[{use_case_id}] Mapped columns: "
                    f"Sample='{sample_col}', "
                    f"{pivot_column}='{pivot_col_found}'"
                )

                # Step 2: Prepare data - rename to standard names
                df_clean = df[[sample_col, pivot_col_found]].rename(
                    columns={sample_col: group_by, pivot_col_found: pivot_column}
                )

                # Step 3: Remove nulls and clean
                initial_count = len(df_clean)
                df_clean = df_clean.dropna()
                df_clean[group_by] = df_clean[group_by].astype(str).str.strip()
                df_clean[pivot_column] = (
                    df_clean[pivot_column].astype(str).str.strip().str.upper()
                )
                df_clean = df_clean[
                    (df_clean[group_by] != "") & (df_clean[pivot_column] != "")
                ]

                cleaned_count = len(df_clean)
                logger.debug(
                    f"[{use_case_id}] Data cleaned: "
                    f"{initial_count} -> {cleaned_count} rows "
                    f"({initial_count - cleaned_count} removed)"
                )

                if df_clean.empty:
                    raise ValueError(
                        f"No valid Sample-{pivot_column} combinations "
                        "found after cleaning"
                    )

                # Step 4: Create presence/absence matrix (crosstab)
                # Binary matrix: rows=Samples, columns=pivot items,
                # values=1 (present) or 0 (absent)
                presence_matrix = pd.crosstab(
                    df_clean[group_by], df_clean[pivot_column]
                )

                logger.debug(
                    f"[{use_case_id}] Presence matrix shape: "
                    f"{presence_matrix.shape} "
                    f"({presence_matrix.shape[0]} samples x "
                    f"{presence_matrix.shape[1]} {pivot_column}s)"
                )

                # Step 5: Compute correlation matrix between samples
                # Pearson correlation between each pair of samples
                correlation_matrix = presence_matrix.T.corr(method=correlation_method)

                logger.info(
                    f"[{use_case_id}] Correlation matrix computed: "
                    f"{correlation_matrix.shape[0]} samples x "
                    f"{correlation_matrix.shape[1]} samples"
                )

                # Step 6: Convert to downloadable format
                # Reset index to make Sample names a column
                df = correlation_matrix.reset_index()
                df.rename(columns={"index": "Sample"}, inplace=True)

                logger.info(
                    f"[{use_case_id}] Final correlation matrix " f"shape: {df.shape}"
                )
                logger.debug(
                    f"[{use_case_id}] Sample correlation matrix "
                    f"preview:\n{df.head()}"
                )

            elif operation == "feature_correlation_matrix":
                # UC-3.6: Generate Feature x Feature correlation matrix
                # (e.g., Gene x Gene correlation showing co-occurrence)
                group_by = data_processing.get("group_by", "Gene_Symbol")
                pivot_column = data_processing.get("pivot_column", "Sample")
                correlation_method = data_processing.get(
                    "correlation_method", "pearson"
                )

                logger.info(
                    f"[{use_case_id}] Computing feature correlation matrix: "
                    f"group_by={group_by}, pivot={pivot_column}, "
                    f"method={correlation_method}"
                )

                # Step 1: Clean column names (flexible mapping)
                feature_col = None
                pivot_col_found = None

                # Try to find feature column (Gene_Symbol, Compound_Name, etc.)
                if group_by == "Gene_Symbol":
                    feature_candidates = [
                        "Gene_Symbol",
                        "gene_symbol",
                        "GeneSymbol",
                        "gene",
                        "Gene",
                        "symbol",
                        "Symbol",
                        "gene_name",
                        "Gene_Name",
                    ]
                elif group_by == "Compound_Name":
                    feature_candidates = [
                        "Compound_Name",
                        "compound_name",
                        "CompoundName",
                        "compound",
                        "Compound",
                        "chemical_name",
                        "Chemical_Name",
                        "chemical",
                        "Chemical",
                    ]
                else:
                    feature_candidates = [group_by]

                for col_name in feature_candidates:
                    if col_name in df.columns:
                        feature_col = col_name
                        break

                # Try to find pivot column (Sample)
                pivot_candidates = [
                    "Sample",
                    "sample",
                    "sample_id",
                    "Sample_ID",
                    "sampleID",
                    "genome",
                    "Genome",
                    "organism",
                ]
                for col_name in pivot_candidates:
                    if col_name in df.columns:
                        pivot_col_found = col_name
                        break

                if not feature_col or not pivot_col_found:
                    raise ValueError(
                        f"Required columns not found. "
                        f"Available: {df.columns.tolist()}, "
                        f"Needed: {group_by} "
                        f"(one of {feature_candidates}) "
                        f"and {pivot_column} (one of {pivot_candidates})"
                    )

                logger.debug(
                    f"[{use_case_id}] Mapped columns: "
                    f"{group_by}='{feature_col}', "
                    f"{pivot_column}='{pivot_col_found}'"
                )

                # Step 2: Prepare data - rename to standard names
                df_clean = df[[feature_col, pivot_col_found]].rename(
                    columns={feature_col: group_by, pivot_col_found: pivot_column}
                )

                # Step 3: Remove nulls and clean
                initial_count = len(df_clean)
                df_clean = df_clean.dropna()
                df_clean[group_by] = df_clean[group_by].astype(str).str.strip()
                df_clean[pivot_column] = df_clean[pivot_column].astype(str).str.strip()
                df_clean = df_clean[
                    (df_clean[group_by] != "") & (df_clean[pivot_column] != "")
                ]

                cleaned_count = len(df_clean)
                logger.debug(
                    f"[{use_case_id}] Data cleaned: "
                    f"{initial_count} -> {cleaned_count} rows "
                    f"({initial_count - cleaned_count} removed)"
                )

                if df_clean.empty:
                    raise ValueError(
                        f"No valid {group_by}-{pivot_column} combinations "
                        "found after cleaning"
                    )

                # Step 4: Create presence/absence matrix (crosstab)
                # Binary matrix: rows=Features (genes), columns=Samples,
                # values=1 (present) or 0 (absent)
                presence_matrix = pd.crosstab(
                    df_clean[group_by], df_clean[pivot_column]
                )

                logger.debug(
                    f"[{use_case_id}] Presence matrix shape: "
                    f"{presence_matrix.shape} "
                    f"({presence_matrix.shape[0]} {group_by}s x "
                    f"{presence_matrix.shape[1]} {pivot_column}s)"
                )

                # Step 5: Compute correlation matrix between features
                # Note: We correlate features (rows), not samples (columns)
                # This shows which features co-occur across samples
                # We need to transpose the matrix to correlate rows instead of columns
                correlation_matrix = presence_matrix.T.corr(method=correlation_method)

                logger.info(
                    f"[{use_case_id}] Feature correlation matrix computed: "
                    f"{correlation_matrix.shape[0]} {group_by}s x "
                    f"{correlation_matrix.shape[1]} {group_by}s"
                )

                # Step 6: Convert to downloadable format
                # Reset index to make feature names a column
                df = correlation_matrix.reset_index()
                df.rename(columns={"index": group_by}, inplace=True)

                logger.info(
                    f"[{use_case_id}] Final feature correlation matrix "
                    f"shape: {df.shape}"
                )
                logger.debug(
                    f"[{use_case_id}] Feature correlation matrix "
                    f"preview:\n{df.head()}"
                )

            elif operation == "aggregate_sample_agency_ko_count":
                # UC-1.6: Count unique KOs per (Sample, Agency) pair
                # Replicates HeatmapStrategy aggregation logic
                sample_column = data_processing.get("sample_column", "sample")
                agency_column = data_processing.get("agency_column", "referenceAG")
                ko_column = data_processing.get("ko_column", "ko")

                logger.info(
                    f"[{use_case_id}] Aggregating unique KO counts per "
                    f"(Sample, Agency) pair"
                )

                # Find columns (flexible naming)
                sample_col = None
                agency_col = None
                ko_col = None

                # Sample column
                sample_candidates = [
                    sample_column,
                    "sample",
                    "Sample",
                    "sample_id",
                    "SampleID",
                    "genome",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # Agency column
                agency_candidates = [
                    agency_column,
                    "Agency",
                    "agency",
                    "referenceAG",
                    "Regulatory_Agency",
                    "ReferenceAG",
                    "AGENCY",
                ]
                for candidate in agency_candidates:
                    if candidate in df.columns:
                        agency_col = candidate
                        break

                # KO column
                ko_candidates = [
                    ko_column,
                    "KO",
                    "ko",
                    "ko_id",
                    "KO_ID",
                    "kegg_orthology",
                ]
                for candidate in ko_candidates:
                    if candidate in df.columns:
                        ko_col = candidate
                        break

                # Validate required columns
                required_cols = {
                    "sample": sample_col,
                    "agency": agency_col,
                    "ko": ko_col,
                }
                missing = [k for k, v in required_cols.items() if not v]

                if missing:
                    raise ValueError(
                        f"Required columns not found: {missing}. "
                        f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"sample='{sample_col}', "
                    f"agency='{agency_col}', "
                    f"ko='{ko_col}'"
                )

                # Clean data
                initial_count = len(df)
                df_clean = df[[sample_col, agency_col, ko_col]].dropna()

                # Standardize column names
                df_clean = df_clean.rename(
                    columns={
                        sample_col: "Sample",
                        agency_col: "ReferenceAG",
                        ko_col: "KO",
                    }
                )

                # Strip whitespace and normalize
                df_clean["Sample"] = df_clean["Sample"].astype(str).str.strip()
                df_clean["ReferenceAG"] = (
                    df_clean["ReferenceAG"].astype(str).str.strip().str.upper()
                )
                df_clean["KO"] = df_clean["KO"].astype(str).str.strip().str.upper()

                # Remove empty strings
                df_clean = df_clean[
                    (df_clean["Sample"] != "")
                    & (df_clean["ReferenceAG"] != "")
                    & (df_clean["KO"] != "")
                ]

                # Remove duplicates (Sample, Agency, KO) combinations
                df_clean = df_clean.drop_duplicates()

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Aggregate: Count unique KOs per (Sample, Agency)
                aggregated = (
                    df_clean.groupby(["Sample", "ReferenceAG"])["KO"]
                    .nunique()
                    .reset_index()
                )

                # Rename KO count column
                aggregated = aggregated.rename(columns={"KO": "Unique_KO_Count"})

                # Sort by Agency, then Sample
                aggregated = aggregated.sort_values(
                    ["ReferenceAG", "Sample"], ascending=[True, True]
                )

                df = aggregated.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Aggregated KO counts: "
                    f"{df['Sample'].nunique()} samples, "
                    f"{df['ReferenceAG'].nunique()} agencies, "
                    f"{len(df)} combinations, "
                    f"KO count range: [{df['Unique_KO_Count'].min()}, "
                    f"{df['Unique_KO_Count'].max()}]"
                )

            elif operation == "aggregate_gene_sample_ko_count":
                # UC-4.13: Count unique KOs per (Gene, Sample, Compound_Pathway)
                # Exports ALL pathways regardless of dropdown selection
                gene_column = data_processing.get("gene_column", "Gene")
                sample_column = data_processing.get("sample_column", "sample")
                ko_column = data_processing.get("ko_column", "ko")
                pathway_column = data_processing.get(
                    "pathway_column", "compound_pathway"
                )

                logger.info(
                    f"[{use_case_id}] Aggregating unique KO counts per "
                    f"(Gene, Sample, Compound_Pathway) - ALL pathways"
                )

                # Find columns (flexible naming)
                gene_col = None
                sample_col = None
                ko_col = None
                pathway_col = None

                # Gene column
                gene_candidates = [
                    gene_column,
                    "Gene",
                    "gene",
                    "GeneSymbol",
                    "gene_symbol",
                ]
                for candidate in gene_candidates:
                    if candidate in df.columns:
                        gene_col = candidate
                        break

                # Sample column
                sample_candidates = [
                    sample_column,
                    "sample",
                    "Sample",
                    "sample_id",
                    "SampleID",
                    "genome",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # KO column
                ko_candidates = [
                    ko_column,
                    "KO",
                    "ko",
                    "ko_id",
                    "KO_ID",
                    "kegg_orthology",
                ]
                for candidate in ko_candidates:
                    if candidate in df.columns:
                        ko_col = candidate
                        break

                # Pathway column
                pathway_candidates = [
                    pathway_column,
                    "Compound_Pathway",
                    "compound_pathway",
                    "Compound",
                    "compound",
                    "pathway",
                    "Pathway",
                ]
                for candidate in pathway_candidates:
                    if candidate in df.columns:
                        pathway_col = candidate
                        break

                # Validate required columns
                required_cols = {
                    "gene": gene_col,
                    "sample": sample_col,
                    "ko": ko_col,
                    "pathway": pathway_col,
                }
                missing = [k for k, v in required_cols.items() if not v]

                if missing:
                    raise ValueError(
                        f"Required columns not found: {missing}. "
                        f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"gene='{gene_col}', "
                    f"sample='{sample_col}', "
                    f"ko='{ko_col}', "
                    f"pathway='{pathway_col}'"
                )

                # Clean data
                initial_count = len(df)
                df_clean = df[[gene_col, sample_col, pathway_col, ko_col]].dropna()

                # Standardize column names
                df_clean = df_clean.rename(
                    columns={
                        gene_col: "Gene",
                        sample_col: "Sample",
                        pathway_col: "Compound_Pathway",
                        ko_col: "KO",
                    }
                )

                # Strip whitespace and normalize
                df_clean["Gene"] = df_clean["Gene"].astype(str).str.strip()
                df_clean["Sample"] = df_clean["Sample"].astype(str).str.strip()
                df_clean["Compound_Pathway"] = (
                    df_clean["Compound_Pathway"].astype(str).str.strip()
                )
                df_clean["KO"] = df_clean["KO"].astype(str).str.strip().str.upper()

                # Remove empty strings and placeholder values
                placeholder_values = ["#N/D", "#N/A", "N/D", "", "nan", "None", "NAN"]
                df_clean = df_clean[
                    (df_clean["Gene"] != "")
                    & (~df_clean["Gene"].isin(placeholder_values))
                    & (df_clean["Sample"] != "")
                    & (~df_clean["Sample"].isin(placeholder_values))
                    & (df_clean["Compound_Pathway"] != "")
                    & (~df_clean["Compound_Pathway"].isin(placeholder_values))
                    & (df_clean["KO"] != "")
                    & (~df_clean["KO"].isin(placeholder_values))
                ]

                # Remove duplicates (Gene, Sample, Pathway, KO) combinations
                df_clean = df_clean.drop_duplicates()

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Aggregate: Count unique KOs per (Gene, Sample, Compound_Pathway)
                aggregated = (
                    df_clean.groupby(["Gene", "Sample", "Compound_Pathway"])["KO"]
                    .nunique()
                    .reset_index()
                )

                # Rename KO count column
                aggregated = aggregated.rename(columns={"KO": "Unique_KO_Count"})

                # Sort by Pathway, Gene, Sample
                aggregated = aggregated.sort_values(
                    ["Compound_Pathway", "Gene", "Sample"], ascending=[True, True, True]
                )

                df = aggregated.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Aggregated KO counts: "
                    f"{df['Gene'].nunique()} genes, "
                    f"{df['Sample'].nunique()} samples, "
                    f"{df['Compound_Pathway'].nunique()} pathways, "
                    f"{len(df)} combinations, "
                    f"KO count range: [{df['Unique_KO_Count'].min()}, "
                    f"{df['Unique_KO_Count'].max()}]"
                )

            elif operation == "aggregate_pathway_compound_ko_count":
                # UC-4.12: Count unique KOs per (Pathway, Compound_Pathway, Sample)
                # Exports ALL samples regardless of dropdown selection
                pathway_column = data_processing.get("pathway_column", "Pathway")
                compound_pathway_column = data_processing.get(
                    "compound_pathway_column", "compound_pathway"
                )
                sample_column = data_processing.get("sample_column", "sample")
                ko_column = data_processing.get("ko_column", "ko")

                logger.info(
                    f"[{use_case_id}] Aggregating unique KO counts per "
                    f"(Pathway, Compound_Pathway, Sample) - ALL samples"
                )

                # Find columns (flexible naming)
                pathway_col = None
                compound_pathway_col = None
                sample_col = None
                ko_col = None

                # Pathway column
                pathway_candidates = [
                    pathway_column,
                    "Pathway",
                    "pathway",
                    "Path",
                    "metabolic_pathway",
                ]
                for candidate in pathway_candidates:
                    if candidate in df.columns:
                        pathway_col = candidate
                        break

                # Compound Pathway column
                compound_pathway_candidates = [
                    compound_pathway_column,
                    "Compound_Pathway",
                    "compound_pathway",
                    "Compound",
                    "compound",
                    "CompoundPathway",
                    "chemical_class",
                ]
                for candidate in compound_pathway_candidates:
                    if candidate in df.columns:
                        compound_pathway_col = candidate
                        break

                # Sample column
                sample_candidates = [
                    sample_column,
                    "sample",
                    "Sample",
                    "sample_id",
                    "SampleID",
                    "genome",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # KO column
                ko_candidates = [
                    ko_column,
                    "KO",
                    "ko",
                    "ko_id",
                    "KO_ID",
                    "kegg_orthology",
                ]
                for candidate in ko_candidates:
                    if candidate in df.columns:
                        ko_col = candidate
                        break

                # Validate required columns
                required_cols = {
                    "pathway": pathway_col,
                    "compound_pathway": compound_pathway_col,
                    "sample": sample_col,
                    "ko": ko_col,
                }
                missing = [k for k, v in required_cols.items() if not v]

                if missing:
                    raise ValueError(
                        f"Required columns not found: {missing}. "
                        f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"pathway='{pathway_col}', "
                    f"compound_pathway='{compound_pathway_col}', "
                    f"sample='{sample_col}', "
                    f"ko='{ko_col}'"
                )

                # Clean data
                initial_count = len(df)
                df_clean = df[
                    [pathway_col, compound_pathway_col, sample_col, ko_col]
                ].dropna()

                # Standardize column names
                df_clean = df_clean.rename(
                    columns={
                        pathway_col: "Pathway",
                        compound_pathway_col: "Compound_Pathway",
                        sample_col: "Sample",
                        ko_col: "KO",
                    }
                )

                # Strip whitespace and normalize
                df_clean["Pathway"] = df_clean["Pathway"].astype(str).str.strip()
                df_clean["Compound_Pathway"] = (
                    df_clean["Compound_Pathway"].astype(str).str.strip()
                )
                df_clean["Sample"] = df_clean["Sample"].astype(str).str.strip()
                df_clean["KO"] = df_clean["KO"].astype(str).str.strip().str.upper()

                # Remove empty strings and placeholder values
                placeholder_values = ["#N/D", "#N/A", "N/D", "", "nan", "None", "NAN"]
                df_clean = df_clean[
                    (df_clean["Pathway"] != "")
                    & (~df_clean["Pathway"].isin(placeholder_values))
                    & (df_clean["Compound_Pathway"] != "")
                    & (~df_clean["Compound_Pathway"].isin(placeholder_values))
                    & (df_clean["Sample"] != "")
                    & (~df_clean["Sample"].isin(placeholder_values))
                    & (df_clean["KO"] != "")
                    & (~df_clean["KO"].isin(placeholder_values))
                ]

                # Remove duplicates
                df_clean = df_clean.drop_duplicates()

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Aggregate: Count unique KOs per (Pathway, Compound, Sample)
                aggregated = (
                    df_clean.groupby(["Pathway", "Compound_Pathway", "Sample"])["KO"]
                    .nunique()
                    .reset_index()
                )

                # Rename KO count column
                aggregated = aggregated.rename(columns={"KO": "Unique_KO_Count"})

                # Sort by Pathway, Compound_Pathway, Sample
                aggregated = aggregated.sort_values(
                    ["Pathway", "Compound_Pathway", "Sample"],
                    ascending=[True, True, True],
                )

                df = aggregated.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Aggregated KO counts: "
                    f"{df['Pathway'].nunique()} pathways, "
                    f"{df['Compound_Pathway'].nunique()} compound pathways, "
                    f"{df['Sample'].nunique()} samples, "
                    f"{len(df)} combinations, "
                    f"KO count range: [{df['Unique_KO_Count'].min()}, "
                    f"{df['Unique_KO_Count'].max()}]"
                )

            elif operation == "aggregate_gene_sample_compound_count":
                # UC-7.3: Count unique genes per (Compound, Sample, Super_Category)
                # Exports ALL data (not filtered by dropdown super_category)
                gene_column = data_processing.get("gene_column", "Gene_Symbol")
                sample_column = data_processing.get("sample_column", "Sample")
                compound_column = data_processing.get(
                    "compound_column", "Compound_Name"
                )
                merge_toxcsm = data_processing.get("merge_toxcsm", False)
                category_column = data_processing.get(
                    "category_column", "super_category"
                )

                logger.info(
                    f"[{use_case_id}] Aggregating unique gene counts per "
                    f"(Compound_Name, Sample{', Super_Category' if merge_toxcsm else ''}) - ALL data"
                )

                # If merge_toxcsm, get ToxCSM data for super_category
                df_toxcsm = None
                if merge_toxcsm:
                    if "toxcsm_df" in merged_data:
                        df_toxcsm = pd.DataFrame(merged_data["toxcsm_df"])
                        logger.info(
                            f"[{use_case_id}] Loaded ToxCSM data: "
                            f"{len(df_toxcsm)} rows for category merge"
                        )
                    else:
                        logger.warning(
                            f"[{use_case_id}] merge_toxcsm=true but "
                            f"toxcsm_df not available in merged_data"
                        )

                # Find columns (flexible naming)
                gene_col = None
                sample_col = None
                compound_col = None

                # Gene column
                gene_candidates = [
                    gene_column,
                    "Gene_Symbol",
                    "genesymbol",
                    "Gene",
                    "gene",
                    "GeneSymbol",
                    "gene_symbol",
                ]
                for candidate in gene_candidates:
                    if candidate in df.columns:
                        gene_col = candidate
                        break

                # Sample column
                sample_candidates = [
                    sample_column,
                    "sample",
                    "Sample",
                    "sample_id",
                    "SampleID",
                    "genome",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # Compound column in BioRemPP
                compound_candidates = [
                    compound_column,
                    "Compound_Name",
                    "compoundname",
                    "Compound",
                    "compound",
                    "CompoundName",
                    "compound_name",
                ]
                for candidate in compound_candidates:
                    if candidate in df.columns:
                        compound_col = candidate
                        break

                # Validate required columns
                required_cols = {
                    "gene": gene_col,
                    "sample": sample_col,
                    "compound": compound_col,
                }
                missing = [k for k, v in required_cols.items() if not v]

                if missing:
                    raise ValueError(
                        f"Required columns not found: {missing}. "
                        f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"gene='{gene_col}', "
                    f"sample='{sample_col}', "
                    f"compound='{compound_col}'"
                )

                # Clean data
                initial_count = len(df)
                df_clean = df[[gene_col, sample_col, compound_col]].dropna()

                # Standardize column names
                df_clean = df_clean.rename(
                    columns={
                        gene_col: "Gene_Symbol",
                        sample_col: "Sample",
                        compound_col: "Compound_Name",
                    }
                )

                # Merge with ToxCSM to get super_category
                if merge_toxcsm and df_toxcsm is not None:
                    # Find compound column in ToxCSM
                    toxcsm_compound_col = None
                    for candidate in [
                        "compoundname",
                        "Compound_Name",
                        "compound",
                        "Compound",
                    ]:
                        if candidate in df_toxcsm.columns:
                            toxcsm_compound_col = candidate
                            break

                    # Find category column in ToxCSM
                    toxcsm_category_col = None
                    for candidate in [
                        category_column,
                        "super_category",
                        "Super_Category",
                        "category",
                    ]:
                        if candidate in df_toxcsm.columns:
                            toxcsm_category_col = candidate
                            break

                    if toxcsm_compound_col and toxcsm_category_col:
                        # Prepare ToxCSM lookup
                        toxcsm_lookup = df_toxcsm[
                            [toxcsm_compound_col, toxcsm_category_col]
                        ].drop_duplicates()

                        toxcsm_lookup = toxcsm_lookup.rename(
                            columns={
                                toxcsm_compound_col: "Compound_Name",
                                toxcsm_category_col: "Super_Category",
                            }
                        )

                        # Normalize compound names for merge
                        toxcsm_lookup["Compound_Name"] = (
                            toxcsm_lookup["Compound_Name"].astype(str).str.strip()
                        )
                        df_clean["Compound_Name"] = (
                            df_clean["Compound_Name"].astype(str).str.strip()
                        )

                        # Merge
                        df_clean = df_clean.merge(
                            toxcsm_lookup, on="Compound_Name", how="left"
                        )

                        logger.info(
                            f"[{use_case_id}] Merged with ToxCSM: "
                            f"{df_clean['Super_Category'].notna().sum()} "
                            f"rows with category info"
                        )
                    else:
                        logger.warning(
                            f"[{use_case_id}] Could not find required "
                            f"columns in ToxCSM for merge"
                        )
                        df_clean["Super_Category"] = "Unknown"

                # Strip whitespace and normalize
                df_clean["Gene_Symbol"] = (
                    df_clean["Gene_Symbol"].astype(str).str.strip()
                )
                df_clean["Sample"] = df_clean["Sample"].astype(str).str.strip()
                df_clean["Compound_Name"] = (
                    df_clean["Compound_Name"].astype(str).str.strip()
                )

                if "Super_Category" in df_clean.columns:
                    df_clean["Super_Category"] = (
                        df_clean["Super_Category"].astype(str).str.strip()
                    )
                    df_clean["Super_Category"] = (
                        df_clean["Super_Category"]
                        .fillna("Unknown")
                        .replace("nan", "Unknown")
                        .replace("", "Unknown")
                    )

                # Remove empty strings and placeholder values
                placeholder_values = ["#N/D", "#N/A", "N/D", "", "nan", "None", "NAN"]
                df_clean = df_clean[
                    (df_clean["Gene_Symbol"] != "")
                    & (~df_clean["Gene_Symbol"].isin(placeholder_values))
                    & (df_clean["Sample"] != "")
                    & (~df_clean["Sample"].isin(placeholder_values))
                    & (df_clean["Compound_Name"] != "")
                    & (~df_clean["Compound_Name"].isin(placeholder_values))
                ]

                # Remove duplicates
                df_clean = df_clean.drop_duplicates()

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} rows "
                    f"(removed {initial_count - len(df_clean)})"
                )

                # Aggregate: Count unique genes per (Compound, Sample, Category)
                # Note: Each row represents a unique gene, so we count rows
                group_cols = ["Compound_Name", "Sample"]
                if "Super_Category" in df_clean.columns:
                    group_cols.insert(2, "Super_Category")

                aggregated = (
                    df_clean.groupby(group_cols)
                    .size()
                    .reset_index(name="Unique_Gene_Count")
                )

                # Sort by Category (if exists), Compound, Sample
                sort_cols = group_cols.copy()
                aggregated = aggregated.sort_values(
                    sort_cols, ascending=[True] * len(sort_cols)
                )

                df = aggregated.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Aggregated gene counts: "
                    f"{df['Compound_Name'].nunique()} compounds, "
                    f"{df['Sample'].nunique()} samples, "
                    f"{'(' + str(df['Super_Category'].nunique()) + ' categories), ' if 'Super_Category' in df.columns else ''}"
                    f"{len(df)} combinations, "
                    f"Gene count range: [{df['Unique_Gene_Count'].min()}, "
                    f"{df['Unique_Gene_Count'].max()}]"
                )

            elif operation == "export_gene_compound_network_edges":
                # UC-5.4: Export gene-compound network edges (bipartite network)
                # Each row = one edge connecting a gene to a compound
                gene_column = data_processing.get("gene_column", "genesymbol")
                compound_column = data_processing.get("compound_column", "compoundname")

                logger.info(
                    f"[{use_case_id}] Exporting gene-compound network edges "
                    f"(bipartite network interactions)"
                )

                # Find columns (flexible naming)
                gene_col = None
                compound_col = None

                # Gene column
                gene_candidates = [
                    gene_column,
                    "genesymbol",
                    "Gene_Symbol",
                    "gene_symbol",
                    "GeneSymbol",
                    "Gene",
                    "gene",
                ]
                for candidate in gene_candidates:
                    if candidate in df.columns:
                        gene_col = candidate
                        break

                # Compound column
                compound_candidates = [
                    compound_column,
                    "compoundname",
                    "Compound_Name",
                    "compound_name",
                    "CompoundName",
                    "Compound",
                    "compound",
                ]
                for candidate in compound_candidates:
                    if candidate in df.columns:
                        compound_col = candidate
                        break

                # Validate required columns
                required_cols = {"gene": gene_col, "compound": compound_col}
                missing = [k for k, v in required_cols.items() if not v]

                if missing:
                    raise ValueError(
                        f"Required columns not found: {missing}. "
                        f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"gene='{gene_col}', "
                    f"compound='{compound_col}'"
                )

                # Clean data
                initial_count = len(df)
                df_clean = df[[gene_col, compound_col]].dropna()

                # Standardize column names
                df_clean = df_clean.rename(
                    columns={gene_col: "Gene_Symbol", compound_col: "Compound_Name"}
                )

                # Strip whitespace and normalize
                df_clean["Gene_Symbol"] = (
                    df_clean["Gene_Symbol"].astype(str).str.strip()
                )
                df_clean["Compound_Name"] = (
                    df_clean["Compound_Name"].astype(str).str.strip()
                )

                # Remove empty strings and placeholder values
                placeholder_values = ["#N/D", "#N/A", "N/D", "", "nan", "None", "NAN"]
                df_clean = df_clean[
                    (df_clean["Gene_Symbol"] != "")
                    & (~df_clean["Gene_Symbol"].isin(placeholder_values))
                    & (df_clean["Compound_Name"] != "")
                    & (~df_clean["Compound_Name"].isin(placeholder_values))
                ]

                # Remove duplicate edges (unique gene-compound pairs)
                df_clean = df_clean.drop_duplicates()

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} edges "
                    f"(removed {initial_count - len(df_clean)} duplicates)"
                )

                # Sort by Gene, then Compound
                df_clean = df_clean.sort_values(
                    ["Gene_Symbol", "Compound_Name"], ascending=[True, True]
                )

                df = df_clean.reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Network edges exported: "
                    f"{df['Gene_Symbol'].nunique()} unique genes, "
                    f"{df['Compound_Name'].nunique()} unique compounds, "
                    f"{len(df)} total edges (interactions)"
                )

            elif operation == "export_gene_similarity_network":
                # UC-5.5: Export gene-gene similarity network edges
                # Each row = edge between 2 genes (gene pair)
                gene_column = data_processing.get("gene_column", "genesymbol")
                compound_column = data_processing.get("compound_column", "compoundname")
                min_shared = data_processing.get("min_shared_compounds", 1)

                logger.info(
                    f"[{use_case_id}] Exporting gene-gene similarity "
                    f"network edges (gene pairs, min_shared={min_shared})"
                )

                # Find columns (flexible naming)
                gene_col = None
                compound_col = None

                # Gene column
                gene_candidates = [
                    gene_column,
                    "genesymbol",
                    "Gene_Symbol",
                    "gene_symbol",
                    "GeneSymbol",
                    "Gene",
                    "gene",
                ]
                for candidate in gene_candidates:
                    if candidate in df.columns:
                        gene_col = candidate
                        break

                # Compound column
                compound_candidates = [
                    compound_column,
                    "compoundname",
                    "Compound_Name",
                    "compound_name",
                    "CompoundName",
                    "Compound",
                    "compound",
                ]
                for candidate in compound_candidates:
                    if candidate in df.columns:
                        compound_col = candidate
                        break

                # Validate required columns
                required_cols = {"gene": gene_col, "compound": compound_col}
                missing = [k for k, v in required_cols.items() if not v]

                if missing:
                    raise ValueError(
                        f"Required columns not found: {missing}. "
                        f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"gene='{gene_col}', "
                    f"compound='{compound_col}'"
                )

                # Clean data
                df_clean = df[[gene_col, compound_col]].dropna()

                # Standardize column names
                df_clean = df_clean.rename(
                    columns={gene_col: "gene", compound_col: "compound"}
                )

                # Strip whitespace and normalize
                df_clean["gene"] = df_clean["gene"].astype(str).str.strip()
                df_clean["compound"] = df_clean["compound"].astype(str).str.strip()

                # Remove empty strings and placeholder values
                placeholder_values = ["#N/D", "#N/A", "N/D", "", "nan", "None", "NAN"]
                df_clean = df_clean[
                    (df_clean["gene"] != "")
                    & (~df_clean["gene"].isin(placeholder_values))
                    & (df_clean["compound"] != "")
                    & (~df_clean["compound"].isin(placeholder_values))
                ]

                # Remove duplicates
                df_clean = df_clean.drop_duplicates()

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} gene-compound pairs"
                )

                # Compute gene-gene similarity via shared compounds
                # Map each gene to set of compounds
                from itertools import combinations

                gene_compound_map = df_clean.groupby("gene")["compound"].apply(set)

                all_genes = list(gene_compound_map.index)
                edges_list = []

                logger.debug(
                    f"[{use_case_id}] Computing gene pairs "
                    f"for {len(all_genes)} genes..."
                )

                # Compute pairwise gene connections
                for gene1, gene2 in combinations(all_genes, 2):
                    shared = gene_compound_map[gene1].intersection(
                        gene_compound_map[gene2]
                    )
                    weight = len(shared)

                    if weight >= min_shared:
                        edges_list.append({"Gene_1": gene1, "Gene_2": gene2})

                df = pd.DataFrame(edges_list)

                if df.empty:
                    logger.warning(
                        f"[{use_case_id}] No gene pairs with "
                        f">= {min_shared} shared compounds found"
                    )
                    # Return empty DataFrame with correct columns
                    df = pd.DataFrame(columns=["Gene_1", "Gene_2"])
                else:
                    # Sort by gene names
                    df = df.sort_values(
                        ["Gene_1", "Gene_2"], ascending=[True, True]
                    ).reset_index(drop=True)

                    logger.info(
                        f"[{use_case_id}] Gene network edges exported: "
                        f"{len(all_genes)} unique genes, "
                        f"{len(df)} edges (gene pairs)"
                    )

            elif operation == "export_compound_similarity_network":
                # UC-5.6: Export compound-compound similarity network edges
                # Each row = edge between 2 compounds (compound pair)
                compound_column = data_processing.get("compound_column", "compoundname")
                gene_column = data_processing.get("gene_column", "genesymbol")
                min_shared = data_processing.get("min_shared_genes", 1)

                logger.info(
                    f"[{use_case_id}] Exporting compound-compound "
                    f"similarity network edges (compound pairs, "
                    f"min_shared={min_shared})"
                )

                # Find columns (flexible naming)
                compound_col = None
                gene_col = None

                # Compound column
                compound_candidates = [
                    compound_column,
                    "compoundname",
                    "Compound_Name",
                    "compound_name",
                    "CompoundName",
                    "Compound",
                    "compound",
                ]
                for candidate in compound_candidates:
                    if candidate in df.columns:
                        compound_col = candidate
                        break

                # Gene column
                gene_candidates = [
                    gene_column,
                    "genesymbol",
                    "Gene_Symbol",
                    "gene_symbol",
                    "GeneSymbol",
                    "Gene",
                    "gene",
                ]
                for candidate in gene_candidates:
                    if candidate in df.columns:
                        gene_col = candidate
                        break

                # Validate required columns
                required_cols = {"compound": compound_col, "gene": gene_col}
                missing = [k for k, v in required_cols.items() if not v]

                if missing:
                    raise ValueError(
                        f"Required columns not found: {missing}. "
                        f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"compound='{compound_col}', "
                    f"gene='{gene_col}'"
                )

                # Clean data
                df_clean = df[[compound_col, gene_col]].dropna()

                # Standardize column names
                df_clean = df_clean.rename(
                    columns={compound_col: "compound", gene_col: "gene"}
                )

                # Strip whitespace and normalize
                df_clean["compound"] = df_clean["compound"].astype(str).str.strip()
                df_clean["gene"] = df_clean["gene"].astype(str).str.strip()

                # Remove empty strings and placeholder values
                placeholder_values = ["#N/D", "#N/A", "N/D", "", "nan", "None", "NAN"]
                df_clean = df_clean[
                    (df_clean["compound"] != "")
                    & (~df_clean["compound"].isin(placeholder_values))
                    & (df_clean["gene"] != "")
                    & (~df_clean["gene"].isin(placeholder_values))
                ]

                # Remove duplicates
                df_clean = df_clean.drop_duplicates()

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} compound-gene pairs"
                )

                # Compute compound-compound similarity via shared genes
                # Map each compound to set of genes
                from itertools import combinations

                compound_gene_map = df_clean.groupby("compound")["gene"].apply(set)

                all_compounds = list(compound_gene_map.index)
                edges_list = []

                logger.debug(
                    f"[{use_case_id}] Computing compound pairs "
                    f"for {len(all_compounds)} compounds..."
                )

                # Compute pairwise compound connections
                for comp1, comp2 in combinations(all_compounds, 2):
                    shared = compound_gene_map[comp1].intersection(
                        compound_gene_map[comp2]
                    )
                    weight = len(shared)

                    if weight >= min_shared:
                        edges_list.append({"Compound_1": comp1, "Compound_2": comp2})

                df = pd.DataFrame(edges_list)

                if df.empty:
                    logger.warning(
                        f"[{use_case_id}] No compound pairs with "
                        f">= {min_shared} shared genes found"
                    )
                    # Return empty DataFrame with correct columns
                    df = pd.DataFrame(columns=["Compound_1", "Compound_2"])
                else:
                    # Sort by compound names
                    df = df.sort_values(
                        ["Compound_1", "Compound_2"], ascending=[True, True]
                    ).reset_index(drop=True)

                    logger.info(
                        f"[{use_case_id}] Compound network edges "
                        f"exported: {len(all_compounds)} unique compounds, "
                        f"{len(df)} edges (compound pairs)"
                    )

            elif operation == "export_pca_coordinates":
                # UC-3.1: Export PCA coordinates (Sample, PC1, PC2)
                # Each row = one sample with its PCA coordinates
                sample_column = data_processing.get("sample_column", "Sample")
                feature_column = data_processing.get("feature_column", "KO")
                n_components = data_processing.get("n_components", 2)

                logger.info(
                    f"[{use_case_id}] Computing PCA coordinates "
                    f"({n_components} components)"
                )

                # Find columns (flexible naming)
                sample_col = None
                feature_col = None

                # Sample column
                sample_candidates = [
                    sample_column,
                    "Sample",
                    "sample",
                    "sample_id",
                    "Sample_ID",
                    "sampleID",
                    "genome",
                    "Genome",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # Feature column
                feature_candidates = [
                    feature_column,
                    "KO",
                    "ko",
                    "ko_id",
                    "KO_ID",
                    "kegg_orthology",
                    "Compound_Name",
                    "compound",
                    "compoundname",
                ]
                for candidate in feature_candidates:
                    if candidate in df.columns:
                        feature_col = candidate
                        break

                # Validate required columns
                required_cols = {"sample": sample_col, "feature": feature_col}
                missing = [k for k, v in required_cols.items() if not v]

                if missing:
                    raise ValueError(
                        f"Required columns not found: {missing}. "
                        f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"sample='{sample_col}', feature='{feature_col}'"
                )

                # Clean data
                df_clean = df[[sample_col, feature_col]].dropna()

                # Strip whitespace
                df_clean[sample_col] = df_clean[sample_col].astype(str).str.strip()
                df_clean[feature_col] = df_clean[feature_col].astype(str).str.strip()

                # Remove empty strings
                df_clean = df_clean[
                    (df_clean[sample_col] != "") & (df_clean[feature_col] != "")
                ]

                logger.debug(
                    f"[{use_case_id}] After cleaning: " f"{len(df_clean)} records"
                )

                # Check minimum requirements
                n_samples = df_clean[sample_col].nunique()
                n_features = df_clean[feature_col].nunique()

                if n_samples < 2:
                    raise ValueError(
                        f"PCA requires at least 2 samples, found {n_samples}"
                    )

                if n_features < 2:
                    raise ValueError(
                        f"PCA requires at least 2 features, " f"found {n_features}"
                    )

                logger.info(
                    f"[{use_case_id}] Building presence/absence matrix: "
                    f"{n_samples} samples x {n_features} features"
                )

                # Create presence/absence matrix
                presence_matrix = pd.crosstab(
                    df_clean[sample_col], df_clean[feature_col]
                )

                # Convert to binary
                binary_matrix = (presence_matrix > 0).astype(int)

                # Standardize features
                from sklearn.decomposition import PCA
                from sklearn.preprocessing import StandardScaler

                scaler = StandardScaler()
                scaled_data = scaler.fit_transform(binary_matrix)

                # Apply PCA
                pca = PCA(n_components=n_components)
                principal_components = pca.fit_transform(scaled_data)

                # Get explained variance
                explained_var = pca.explained_variance_ratio_ * 100

                logger.info(
                    f"[{use_case_id}] PCA complete. "
                    f"Explained variance: "
                    f"PC1={explained_var[0]:.2f}%, "
                    f"PC2={explained_var[1]:.2f}%"
                )

                # Create result DataFrame
                df = pd.DataFrame(
                    data=principal_components,
                    columns=[f"PC{i+1}" for i in range(n_components)],
                    index=binary_matrix.index,
                )

                # Add sample column
                df["Sample"] = df.index

                # Reorder columns: Sample, PC1, PC2
                df = df[["Sample", "PC1", "PC2"]].reset_index(drop=True)

                # Sort by Sample name
                df = df.sort_values("Sample")

                logger.info(
                    f"[{use_case_id}] PCA coordinates exported: "
                    f"{len(df)} samples with {n_components} components"
                )

            elif operation == "export_agency_ko_percentage":
                # UC-1.3: Export Agency KO percentage distribution
                # Each row = one agency with its KO count and percentage
                agency_column = data_processing.get("agency_column", "Agency")
                ko_column = data_processing.get("ko_column", "KO")

                logger.info(
                    f"[{use_case_id}] Computing agency KO percentage " f"distribution"
                )

                # Find columns (flexible naming)
                agency_col = None
                ko_col = None

                # Agency column
                agency_candidates = [
                    agency_column,
                    "Agency",
                    "agency",
                    "referenceAG",
                    "ReferenceAG",
                    "reference_ag",
                    "ref_ag",
                ]
                for candidate in agency_candidates:
                    if candidate in df.columns:
                        agency_col = candidate
                        break

                # KO column
                ko_candidates = [ko_column, "KO", "ko", "ko_id", "KO_ID"]
                for candidate in ko_candidates:
                    if candidate in df.columns:
                        ko_col = candidate
                        break

                # Validate required columns
                required_cols = {"agency": agency_col, "ko": ko_col}
                missing = [k for k, v in required_cols.items() if not v]

                if missing:
                    raise ValueError(
                        f"Required columns not found: {missing}. "
                        f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"agency='{agency_col}', ko='{ko_col}'"
                )

                # Clean data
                df_clean = df[[agency_col, ko_col]].dropna()

                # Strip whitespace and normalize
                df_clean[agency_col] = (
                    df_clean[agency_col].astype(str).str.strip().str.upper()
                )
                df_clean[ko_col] = df_clean[ko_col].astype(str).str.strip().str.upper()

                # Remove duplicates
                df_clean = df_clean.drop_duplicates()

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} unique agency-KO pairs"
                )

                # Group by agency and count unique KOs
                agency_counts = (
                    df_clean.groupby(agency_col)[ko_col].nunique().reset_index()
                )
                agency_counts.columns = ["Agency", "KO_Count"]

                # Calculate percentages
                total_kos = agency_counts["KO_Count"].sum()
                agency_counts["Percentage"] = (
                    100 * agency_counts["KO_Count"] / total_kos
                )

                # Round percentage to 2 decimal places
                agency_counts["Percentage"] = agency_counts["Percentage"].round(2)

                # Sort by percentage descending
                df = agency_counts.sort_values(
                    "Percentage", ascending=False
                ).reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Agency KO distribution exported: "
                    f"{len(df)} agencies, {total_kos} total unique KOs"
                )

            elif operation == "export_sample_ko_percentage":
                # UC-1.4: Export Sample KO percentage distribution
                # Each row = one sample with its KO count and percentage
                sample_column = data_processing.get("sample_column", "Sample")
                ko_column = data_processing.get("ko_column", "KO")

                logger.info(
                    f"[{use_case_id}] Computing sample KO percentage " f"distribution"
                )

                # Find columns (flexible naming)
                sample_col = None
                ko_col = None

                # Sample column
                sample_candidates = [
                    sample_column,
                    "Sample",
                    "sample",
                    "sample_id",
                    "Sample_ID",
                    "sampleID",
                    "genome",
                    "Genome",
                ]
                for candidate in sample_candidates:
                    if candidate in df.columns:
                        sample_col = candidate
                        break

                # KO column
                ko_candidates = [ko_column, "KO", "ko", "ko_id", "KO_ID"]
                for candidate in ko_candidates:
                    if candidate in df.columns:
                        ko_col = candidate
                        break

                # Validate required columns
                required_cols = {"sample": sample_col, "ko": ko_col}
                missing = [k for k, v in required_cols.items() if not v]

                if missing:
                    raise ValueError(
                        f"Required columns not found: {missing}. "
                        f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"sample='{sample_col}', ko='{ko_col}'"
                )

                # Clean data
                df_clean = df[[sample_col, ko_col]].dropna()

                # Strip whitespace and normalize
                df_clean[sample_col] = (
                    df_clean[sample_col].astype(str).str.strip().str.upper()
                )
                df_clean[ko_col] = df_clean[ko_col].astype(str).str.strip().str.upper()

                # Remove duplicates
                df_clean = df_clean.drop_duplicates()

                logger.debug(
                    f"[{use_case_id}] After cleaning: "
                    f"{len(df_clean)} unique sample-KO pairs"
                )

                # Group by sample and count unique KOs
                sample_counts = (
                    df_clean.groupby(sample_col)[ko_col].nunique().reset_index()
                )
                sample_counts.columns = ["Sample", "KO_Count"]

                # Calculate percentages
                total_kos = sample_counts["KO_Count"].sum()
                sample_counts["Percentage"] = (
                    100 * sample_counts["KO_Count"] / total_kos
                )

                # Round percentage to 2 decimal places
                sample_counts["Percentage"] = sample_counts["Percentage"].round(2)

                # Sort by percentage descending
                df = sample_counts.sort_values(
                    "Percentage", ascending=False
                ).reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Sample KO distribution exported: "
                    f"{len(df)} samples, {total_kos} total unique KOs"
                )

            elif operation == "export_treemap_hierarchy":
                # UC-6.3, UC-6.4, UC-6.5: Export hierarchical treemap data
                # Processes path columns and aggregates value column
                path_columns = data_processing.get("path_columns", [])
                value_column = data_processing.get("value_column", "")
                aggregation = data_processing.get("aggregation", "nunique")

                logger.info(
                    f"[{use_case_id}] Processing treemap hierarchy with "
                    f"path={path_columns}, value='{value_column}', "
                    f"agg='{aggregation}'"
                )

                # Validate configuration
                if not path_columns:
                    raise ValueError("path_columns not configured for treemap export")
                if not value_column:
                    raise ValueError("value_column not configured for treemap export")

                # Map columns flexibly for each path level
                mapped_columns = []

                for target_col in path_columns:
                    col_found = None

                    # Define candidates based on common patterns
                    if "class" in target_col.lower():
                        candidates = [
                            target_col,
                            "Compound_Class",
                            "compound_class",
                            "compoundclass",
                            "CompoundClass",
                            "class",
                            "Class",
                        ]
                    elif (
                        "compound" in target_col.lower()
                        and "name" in target_col.lower()
                    ):
                        candidates = [
                            target_col,
                            "Compound_Name",
                            "compound_name",
                            "compoundname",
                            "CompoundName",
                            "compound",
                            "Compound",
                        ]
                    elif "sample" in target_col.lower():
                        candidates = [
                            target_col,
                            "Sample",
                            "sample",
                            "sample_id",
                            "Sample_ID",
                            "sampleID",
                            "genome",
                            "Genome",
                        ]
                    elif "gene" in target_col.lower() or "symbol" in target_col.lower():
                        candidates = [
                            target_col,
                            "Gene_Symbol",
                            "gene_symbol",
                            "genesymbol",
                            "GeneSymbol",
                            "gene",
                            "Gene",
                        ]
                    elif "enzyme" in target_col.lower():
                        candidates = [
                            target_col,
                            "Enzyme_Activity",
                            "enzyme_activity",
                            "enzymeactivity",
                            "EnzymeActivity",
                        ]
                    else:
                        candidates = [target_col]

                    # Find first matching candidate
                    for candidate in candidates:
                        if candidate in df.columns:
                            col_found = candidate
                            break

                    if not col_found:
                        raise ValueError(
                            f"Path column '{target_col}' not found. "
                            f"Available: {df.columns.tolist()}"
                        )

                    mapped_columns.append(col_found)
                    logger.debug(
                        f"[{use_case_id}] Mapped '{target_col}' -> " f"'{col_found}'"
                    )

                # Map value column
                value_col = None
                value_candidates = [
                    value_column,
                    "Gene_Symbol",
                    "gene_symbol",
                    "genesymbol",
                    "GeneSymbol",
                    "Compound_Name",
                    "compound_name",
                    "compoundname",
                ]
                for candidate in value_candidates:
                    if candidate in df.columns:
                        value_col = candidate
                        break

                if not value_col:
                    raise ValueError(
                        f"Value column '{value_column}' not found. "
                        f"Available: {df.columns.tolist()}"
                    )

                logger.debug(
                    f"[{use_case_id}] Using columns: "
                    f"path={mapped_columns}, value='{value_col}'"
                )

                # Select and rename columns
                df_hierarchy = df[mapped_columns + [value_col]].copy()

                # Rename to standard names (use path_columns as target names)
                rename_map = {
                    mapped_columns[i]: path_columns[i] for i in range(len(path_columns))
                }
                rename_map[value_col] = value_column
                df_hierarchy = df_hierarchy.rename(columns=rename_map)

                # Clean data
                initial_count = len(df_hierarchy)
                df_hierarchy = df_hierarchy.dropna()

                # Strip whitespace and remove placeholders
                for col in path_columns:
                    df_hierarchy[col] = df_hierarchy[col].astype(str).str.strip()
                    df_hierarchy = df_hierarchy[
                        ~df_hierarchy[col].isin(["#N/D", "#N/A", "N/D", "", "nan"])
                    ]

                cleaned_count = len(df_hierarchy)
                logger.debug(
                    f"[{use_case_id}] After cleaning: {cleaned_count} "
                    f"records ({initial_count - cleaned_count} removed)"
                )

                if df_hierarchy.empty:
                    raise ValueError("No valid data after cleaning")

                # Aggregate based on method
                if aggregation == "nunique":
                    agg_col_name = f"Unique_{value_column}_Count"
                    df = (
                        df_hierarchy.groupby(path_columns)[value_column]
                        .nunique()
                        .reset_index()
                    )
                elif aggregation == "count":
                    agg_col_name = f"{value_column}_Count"
                    df = (
                        df_hierarchy.groupby(path_columns)[value_column]
                        .count()
                        .reset_index()
                    )
                elif aggregation == "sum":
                    agg_col_name = f"{value_column}_Sum"
                    df = (
                        df_hierarchy.groupby(path_columns)[value_column]
                        .sum()
                        .reset_index()
                    )
                else:
                    raise ValueError(
                        f"Unknown aggregation: '{aggregation}'. "
                        f"Supported: nunique, count, sum"
                    )

                # Rename aggregated column
                df.columns = path_columns + [agg_col_name]

                # Sort by aggregated value descending
                df = df.sort_values(agg_col_name, ascending=False).reset_index(
                    drop=True
                )

                logger.info(
                    f"[{use_case_id}] Treemap hierarchy exported: "
                    f"{len(df)} nodes, "
                    f"value range [{df[agg_col_name].min()}, "
                    f"{df[agg_col_name].max()}]"
                )

            elif operation == "export_sample_toxicity_breadth":
                # UC-7.6: Export Sample Risk Mitigation Breadth
                # Requires merging BioRemPP + ToxCSM databases
                logger.info(
                    f"[{use_case_id}] Processing sample toxicity breadth "
                    f"(multi-database merge)"
                )

                # Access both databases from merged_data
                if "biorempp_df" not in merged_data:
                    raise ValueError("UC-7.6 requires biorempp_df in merged data")
                if "toxcsm_df" not in merged_data:
                    raise ValueError("UC-7.6 requires toxcsm_df in merged data")

                # Extract both DataFrames
                df_biorempp = pd.DataFrame(merged_data["biorempp_df"])
                df_toxcsm = pd.DataFrame(merged_data["toxcsm_df"])

                logger.debug(
                    f"[{use_case_id}] BioRemPP: {len(df_biorempp)} rows, "
                    f"ToxCSM: {len(df_toxcsm)} rows"
                )

                # Find Sample column in BioRemPP
                sample_col = None
                sample_candidates = [
                    "Sample",
                    "sample",
                    "sample_id",
                    "Sample_ID",
                    "genome",
                ]
                for candidate in sample_candidates:
                    if candidate in df_biorempp.columns:
                        sample_col = candidate
                        break

                if not sample_col:
                    raise ValueError("Sample column not found in BioRemPP data")

                # Find Compound column in BioRemPP
                compound_col_biorempp = None
                compound_candidates = [
                    "Compound_Name",
                    "compound_name",
                    "compoundname",
                    "CompoundName",
                    "compound",
                    "Compound",
                ]
                for candidate in compound_candidates:
                    if candidate in df_biorempp.columns:
                        compound_col_biorempp = candidate
                        break

                if not compound_col_biorempp:
                    raise ValueError("Compound column not found in BioRemPP data")

                # Find Compound column in ToxCSM
                compound_col_toxcsm = None
                toxcsm_compound_candidates = [
                    "compoundname",
                    "compound_name",
                    "Compound_Name",
                    "compound",
                ]
                for candidate in toxcsm_compound_candidates:
                    if candidate in df_toxcsm.columns:
                        compound_col_toxcsm = candidate
                        break

                if not compound_col_toxcsm:
                    raise ValueError("Compound column not found in ToxCSM data")

                # Check for super_category in ToxCSM
                if "super_category" not in df_toxcsm.columns:
                    raise ValueError("ToxCSM data missing 'super_category' column")

                # Filter ToxCSM for high-risk compounds
                if "toxicity_score" in df_toxcsm.columns:
                    df_risk = df_toxcsm[df_toxcsm["toxicity_score"] > 0.5].copy()
                    logger.debug(
                        f"[{use_case_id}] Filtered to {len(df_risk)} "
                        f"high-risk records (score > 0.5)"
                    )
                else:
                    df_risk = df_toxcsm.copy()
                    logger.warning(
                        f"[{use_case_id}] No toxicity_score column, "
                        f"using all ToxCSM data"
                    )

                if df_risk.empty:
                    raise ValueError("No high-risk compounds found in ToxCSM data")

                # Get unique compound-category pairs from ToxCSM
                df_risk_processed = df_risk[
                    [compound_col_toxcsm, "super_category"]
                ].drop_duplicates()
                df_risk_processed = df_risk_processed.rename(
                    columns={compound_col_toxcsm: "compoundname"}
                )

                # Prepare BioRemPP data
                df_biorempp_clean = df_biorempp[
                    [sample_col, compound_col_biorempp]
                ].copy()
                df_biorempp_clean = df_biorempp_clean.rename(
                    columns={
                        sample_col: "Sample",
                        compound_col_biorempp: "compoundname",
                    }
                )
                df_biorempp_clean = df_biorempp_clean.dropna()

                # Merge BioRemPP with risk data
                df_merged = pd.merge(
                    df_biorempp_clean, df_risk_processed, on="compoundname", how="inner"
                ).drop_duplicates()

                logger.debug(
                    f"[{use_case_id}] Merged data: {len(df_merged)} " f"records"
                )

                if df_merged.empty:
                    raise ValueError(
                        "No matching compounds between BioRemPP and "
                        "ToxCSM high-risk data"
                    )

                # Aggregate: count unique compounds per sample per category
                df_agg = (
                    df_merged.groupby(["Sample", "super_category"])["compoundname"]
                    .nunique()
                    .reset_index()
                )
                df_agg.columns = [
                    "Sample",
                    "Toxicity_Category",
                    "Unique_Compound_Count",
                ]

                # Sort by Sample then count descending
                df = df_agg.sort_values(
                    ["Sample", "Unique_Compound_Count"], ascending=[True, False]
                ).reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Sample toxicity breadth exported: "
                    f"{len(df)} rows, {df['Sample'].nunique()} samples, "
                    f"{df['Toxicity_Category'].nunique()} categories"
                )

            elif operation == "export_sample_toxicity_depth":
                # UC-7.7: Export Sample Risk Mitigation Depth Profile
                # Similar to UC-7.6 but with 3-level hierarchy and counts ALL interactions
                logger.info(
                    f"[{use_case_id}] Processing sample toxicity depth "
                    f"(multi-database merge with interaction counts)"
                )

                # Access both databases from merged_data
                if "biorempp_df" not in merged_data:
                    raise ValueError("UC-7.7 requires biorempp_df in merged data")
                if "toxcsm_df" not in merged_data:
                    raise ValueError("UC-7.7 requires toxcsm_df in merged data")

                # Extract both DataFrames
                df_biorempp = pd.DataFrame(merged_data["biorempp_df"])
                df_toxcsm = pd.DataFrame(merged_data["toxcsm_df"])

                logger.debug(
                    f"[{use_case_id}] BioRemPP: {len(df_biorempp)} rows, "
                    f"ToxCSM: {len(df_toxcsm)} rows"
                )

                # Find Sample column in BioRemPP
                sample_col = None
                sample_candidates = [
                    "Sample",
                    "sample",
                    "sample_id",
                    "Sample_ID",
                    "genome",
                ]
                for candidate in sample_candidates:
                    if candidate in df_biorempp.columns:
                        sample_col = candidate
                        break

                if not sample_col:
                    raise ValueError("Sample column not found in BioRemPP data")

                # Find Compound column in BioRemPP
                compound_col_biorempp = None
                compound_candidates = [
                    "Compound_Name",
                    "compound_name",
                    "compoundname",
                    "CompoundName",
                    "compound",
                    "Compound",
                ]
                for candidate in compound_candidates:
                    if candidate in df_biorempp.columns:
                        compound_col_biorempp = candidate
                        break

                if not compound_col_biorempp:
                    raise ValueError("Compound column not found in BioRemPP data")

                # Find Compound column in ToxCSM
                compound_col_toxcsm = None
                toxcsm_compound_candidates = [
                    "compoundname",
                    "compound_name",
                    "Compound_Name",
                    "compound",
                ]
                for candidate in toxcsm_compound_candidates:
                    if candidate in df_toxcsm.columns:
                        compound_col_toxcsm = candidate
                        break

                if not compound_col_toxcsm:
                    raise ValueError("Compound column not found in ToxCSM data")

                # Check for super_category in ToxCSM
                if "super_category" not in df_toxcsm.columns:
                    raise ValueError("ToxCSM data missing 'super_category' column")

                # Filter ToxCSM for high-risk compounds
                if "toxicity_score" in df_toxcsm.columns:
                    df_risk = df_toxcsm[df_toxcsm["toxicity_score"] > 0.5].copy()
                    logger.debug(
                        f"[{use_case_id}] Filtered to {len(df_risk)} "
                        f"high-risk records (score > 0.5)"
                    )
                else:
                    df_risk = df_toxcsm.copy()
                    logger.warning(
                        f"[{use_case_id}] No toxicity_score column, "
                        f"using all ToxCSM data"
                    )

                if df_risk.empty:
                    raise ValueError("No high-risk compounds found in ToxCSM data")

                # Get unique compound-category pairs from ToxCSM
                df_risk_processed = df_risk[
                    [compound_col_toxcsm, "super_category"]
                ].drop_duplicates()
                df_risk_processed = df_risk_processed.rename(
                    columns={compound_col_toxcsm: "Compound_Name"}
                )

                # Prepare BioRemPP data
                df_biorempp_clean = df_biorempp[
                    [sample_col, compound_col_biorempp]
                ].copy()
                df_biorempp_clean = df_biorempp_clean.rename(
                    columns={
                        sample_col: "Sample",
                        compound_col_biorempp: "Compound_Name",
                    }
                )
                df_biorempp_clean = df_biorempp_clean.dropna()

                # Merge BioRemPP with risk data
                # DO NOT drop duplicates - we want ALL interactions
                df_merged = pd.merge(
                    df_biorempp_clean,
                    df_risk_processed,
                    on="Compound_Name",
                    how="inner",
                )

                logger.debug(
                    f"[{use_case_id}] Merged data: {len(df_merged)} " f"interactions"
                )

                if df_merged.empty:
                    raise ValueError(
                        "No matching compounds between BioRemPP and "
                        "ToxCSM high-risk data"
                    )

                # Aggregate: count interactions per sample, category, compound
                # groupby + size() counts ALL rows (interactions)
                df_agg = (
                    df_merged.groupby(["Sample", "super_category", "Compound_Name"])
                    .size()
                    .reset_index(name="Interaction_Count")
                )
                df_agg = df_agg.rename(columns={"super_category": "Toxicity_Category"})

                # Sort by Sample, then Toxicity_Category, then count descending
                df = df_agg.sort_values(
                    ["Sample", "Toxicity_Category", "Interaction_Count"],
                    ascending=[True, True, False],
                ).reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Sample toxicity depth exported: "
                    f"{len(df)} rows, {df['Sample'].nunique()} samples, "
                    f"{df['Toxicity_Category'].nunique()} categories, "
                    f"{df['Compound_Name'].nunique()} compounds"
                )

            elif operation == "export_treemap_hierarchy_multidb":
                # UC-4.11: Export hierarchical treemap with database-specific structure
                # BioRemPP: Compound_Class → Compound_Name → Gene_Symbol
                # HADEG: Compound → Pathway → Gene
                logger.info(
                    f"[{use_case_id}] Processing multi-database treemap hierarchy "
                    f"for database '{database}'"
                )

                # Determine hierarchy based on database
                if database == "biorempp_df":
                    # BioRemPP hierarchy
                    level1_col = None
                    level2_col = None
                    value_col = None

                    # Find Compound_Class column
                    class_candidates = [
                        "Compound_Class",
                        "compound_class",
                        "compoundclass",
                        "CompoundClass",
                        "class",
                        "Class",
                    ]
                    for candidate in class_candidates:
                        if candidate in df.columns:
                            level1_col = candidate
                            break

                    # Find Compound_Name column
                    compound_candidates = [
                        "Compound_Name",
                        "compound_name",
                        "compoundname",
                        "CompoundName",
                        "compound",
                        "Compound",
                        "cpd",
                    ]
                    for candidate in compound_candidates:
                        if candidate in df.columns:
                            level2_col = candidate
                            break

                    # Find Gene_Symbol column
                    gene_candidates = [
                        "Gene_Symbol",
                        "gene_symbol",
                        "genesymbol",
                        "GeneSymbol",
                        "gene",
                        "Gene",
                        "Gene_ID",
                    ]
                    for candidate in gene_candidates:
                        if candidate in df.columns:
                            value_col = candidate
                            break

                    # Validate columns found
                    if not level1_col:
                        raise ValueError(
                            f"Compound_Class column not found in BioRemPP data. "
                            f"Available: {df.columns.tolist()}"
                        )
                    if not level2_col:
                        raise ValueError(
                            f"Compound_Name column not found in BioRemPP data. "
                            f"Available: {df.columns.tolist()}"
                        )
                    if not value_col:
                        raise ValueError(
                            f"Gene_Symbol column not found in BioRemPP data. "
                            f"Available: {df.columns.tolist()}"
                        )

                    logger.info(
                        f"[{use_case_id}] BioRemPP hierarchy: "
                        f"{level1_col} → {level2_col} → COUNT({value_col})"
                    )

                elif database == "hadeg_df":
                    # HADEG hierarchy
                    level1_col = None
                    level2_col = None
                    value_col = None

                    # Find Compound column
                    compound_candidates = [
                        "Compound",
                        "compound",
                        "compound_pathway",
                        "Compound_Pathway",
                        "compoundpathway",
                    ]
                    for candidate in compound_candidates:
                        if candidate in df.columns:
                            level1_col = candidate
                            break

                    # Find Pathway column
                    pathway_candidates = [
                        "Pathway",
                        "pathway",
                        "pathway_name",
                        "Pathway_Name",
                    ]
                    for candidate in pathway_candidates:
                        if candidate in df.columns:
                            level2_col = candidate
                            break

                    # Find Gene column
                    gene_candidates = [
                        "Gene",
                        "gene",
                        "Gene_Symbol",
                        "gene_symbol",
                        "genesymbol",
                        "GeneSymbol",
                    ]
                    for candidate in gene_candidates:
                        if candidate in df.columns:
                            value_col = candidate
                            break

                    # Validate columns found
                    if not level1_col:
                        raise ValueError(
                            f"Compound column not found in HADEG data. "
                            f"Available: {df.columns.tolist()}"
                        )
                    if not level2_col:
                        raise ValueError(
                            f"Pathway column not found in HADEG data. "
                            f"Available: {df.columns.tolist()}"
                        )
                    if not value_col:
                        raise ValueError(
                            f"Gene column not found in HADEG data. "
                            f"Available: {df.columns.tolist()}"
                        )

                    logger.info(
                        f"[{use_case_id}] HADEG hierarchy: "
                        f"{level1_col} → {level2_col} → COUNT({value_col})"
                    )

                else:
                    raise ValueError(
                        f"UC-4.11 only supports biorempp_df and hadeg_df, "
                        f"got '{database}'"
                    )

                # Select relevant columns
                df_hierarchy = df[[level1_col, level2_col, value_col]].copy()

                # Clean data
                initial_count = len(df_hierarchy)
                df_hierarchy = df_hierarchy.dropna()

                # Strip whitespace and remove placeholders
                for col in [level1_col, level2_col]:
                    df_hierarchy[col] = df_hierarchy[col].astype(str).str.strip()
                    df_hierarchy = df_hierarchy[
                        ~df_hierarchy[col].isin(
                            ["#N/D", "#N/A", "N/D", "", "nan", "None"]
                        )
                    ]

                cleaned_count = len(df_hierarchy)
                logger.debug(
                    f"[{use_case_id}] After cleaning: {cleaned_count} "
                    f"records ({initial_count - cleaned_count} removed)"
                )

                if df_hierarchy.empty:
                    raise ValueError(f"No valid data after cleaning for {database}")

                # Aggregate: Group by level1 and level2, count unique genes
                df = (
                    df_hierarchy.groupby([level1_col, level2_col])[value_col]
                    .nunique()
                    .reset_index()
                )

                # Rename columns to standard format
                if database == "biorempp_df":
                    df.columns = [
                        "Compound_Class",
                        "Compound_Name",
                        "Unique_Gene_Symbol_Count",
                    ]
                else:  # hadeg_df
                    df.columns = ["Compound", "Pathway", "Unique_Gene_Count"]

                # Sort by count descending
                count_col = df.columns[-1]  # Last column is the count
                df = df.sort_values(count_col, ascending=False).reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Treemap hierarchy exported: "
                    f"{len(df)} nodes, "
                    f"value range [{df[count_col].min()}, "
                    f"{df[count_col].max()}]"
                )

            elif operation == "export_toxicity_endpoint_distribution":
                # UC-7.4: Export toxicity endpoint distribution filtered by super-category
                logger.info(
                    f"[{use_case_id}] Processing toxicity endpoint distribution"
                )

                # Get selected super-category from dropdown filter
                selected_category = None
                if filter_values:
                    dropdown_id = "uc-7-4-category-dropdown"
                    selected_category = filter_values.get(dropdown_id)

                if not selected_category:
                    raise ValueError(
                        "No toxicity super-category selected. "
                        "Please select a category from the dropdown before downloading."
                    )

                logger.info(
                    f"[{use_case_id}] Filtering by super-category: "
                    f"'{selected_category}'"
                )

                # Validate required columns
                required_cols = [
                    "super_category",
                    "endpoint",
                    "compoundname",
                    "toxicity_score",
                ]
                missing_cols = [col for col in required_cols if col not in df.columns]

                if missing_cols:
                    raise ValueError(
                        f"Missing required columns: {missing_cols}. "
                        f"Available: {df.columns.tolist()}"
                    )

                # Filter by selected super-category
                df_filtered = df[df["super_category"] == selected_category].copy()

                if df_filtered.empty:
                    raise ValueError(
                        f"No data available for category: {selected_category}"
                    )

                # Select and rename columns for export
                df = df_filtered[
                    ["super_category", "endpoint", "compoundname", "toxicity_score"]
                ].copy()

                # Rename columns to standard format
                df.columns = [
                    "Super_Category",
                    "Endpoint",
                    "Compound_Name",
                    "Toxicity_Score",
                ]

                # Sort by endpoint and toxicity score descending
                df = df.sort_values(
                    ["Endpoint", "Toxicity_Score"], ascending=[True, False]
                ).reset_index(drop=True)

                logger.info(
                    f"[{use_case_id}] Toxicity endpoint distribution exported: "
                    f"{len(df)} records, "
                    f"{df['Endpoint'].nunique()} unique endpoints, "
                    f"category: {selected_category}"
                )

            else:
                # Unknown operation
                logger.error(
                    f"[{use_case_id}] Unknown data processing operation: "
                    f"'{operation}'. Available operations: "
                    f"aggregate_ko_count, aggregate_compound_count, "
                    f"calculate_regulatory_compliance_scores, "
                    f"calculate_ko_completeness_scores, "
                    f"aggregate_sample_agency_ko_count, "
                    f"aggregate_gene_sample_ko_count, "
                    f"aggregate_pathway_compound_ko_count, "
                    f"aggregate_gene_sample_compound_count, "
                    f"export_treemap_hierarchy_multidb, etc."
                )
                raise ValueError(
                    f"Unknown data processing operation: '{operation}'. "
                    f"Check download_config.yaml for UC-{use_case_id}"
                )
        else:
            # Filter columns if specified (only when NOT processing)
            if relevant_columns:
                # Only keep columns that exist in the DataFrame
                available_columns = [
                    col for col in relevant_columns if col in df.columns
                ]
                if available_columns:
                    df = df[available_columns]
                    logger.info(
                        f"[{use_case_id}] Filtered to {len(available_columns)} relevant columns: {available_columns}"
                    )
                else:
                    logger.warning(
                        f"[{use_case_id}] None of the relevant columns {relevant_columns} found in DataFrame"
                    )

        # Generate filename
        ext = (
            "csv"
            if format_name == "csv"
            else "xlsx" if format_name == "excel" else "json"
        )
        filename = sanitize_filename(use_case_id, database, ext)

        # Export
        result = self.exporter.export(data=df, format=format_enum, filename=filename)

        if result.success:
            logger.info(
                f"[{use_case_id}] Export successful: "
                f"{result.filename} ({result.size_bytes} bytes, {len(df)} rows)"
            )

            toast_msg = html.Div(
                [
                    html.Strong("Download successful!"),
                    html.Br(),
                    html.Small(
                        f"{result.filename} ({result.size_bytes / 1024:.2f} KB, {len(df):,} rows)"
                    ),
                ]
            )

            return (dcc.send_bytes(result.data, result.filename), toast_msg, "success")
        else:
            raise Exception(result.error)

    def _export_multi_sheet(self, use_case_id: str, databases: list, merged_data: Dict):
        """
        Export multiple databases as Excel multi-sheet.

        Parameters
        ----------
        use_case_id : str
            Use case identifier
        databases : list
            List of database keys
        merged_data : Dict
            Data from merged-result-store

        Returns
        -------
        tuple
            (download_data, toast_message, toast_icon)
        """
        from io import BytesIO

        # Generate filename
        filename = sanitize_filename(use_case_id, "all_databases", "xlsx")

        # Create multi-sheet Excel
        buffer = BytesIO()
        total_rows = 0

        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            for db_name in databases:
                if db_name not in merged_data:
                    logger.warning(
                        f"[{use_case_id}] Database '{db_name}' not in merged data, skipping"
                    )
                    continue

                df = pd.DataFrame(merged_data[db_name])
                if df.empty:
                    logger.warning(
                        f"[{use_case_id}] Database '{db_name}' is empty, skipping"
                    )
                    continue

                # Sheet name: remove '_df' suffix and uppercase
                sheet_name = db_name.replace("_df", "").upper()[
                    :31
                ]  # Excel limit: 31 chars

                df.to_excel(writer, sheet_name=sheet_name, index=False)
                total_rows += len(df)

                logger.debug(
                    f"[{use_case_id}] Added sheet '{sheet_name}' with {len(df)} rows"
                )

        buffer.seek(0)
        data_bytes = buffer.getvalue()
        size_kb = len(data_bytes) / 1024

        logger.info(
            f"[{use_case_id}] Multi-sheet Excel exported: "
            f"{filename} ({size_kb:.2f} KB, {total_rows:,} total rows, {len(databases)} sheets)"
        )

        toast_msg = html.Div(
            [
                html.Strong("Multi-database download successful!"),
                html.Br(),
                html.Small(
                    f"{filename} ({size_kb:.2f} KB, {total_rows:,} rows, {len(databases)} sheets)"
                ),
            ]
        )

        return (dcc.send_bytes(data_bytes, filename), toast_msg, "success")


def register_download_callbacks(app, config_path: Optional[Path] = None):
    """
    Register all download callbacks for the application.

    This is the main entry point for registering download callbacks.

    Parameters
    ----------
    app : Dash
        Dash application instance
    config_path : Optional[Path], optional
        Path to download_config.yaml, by default None (uses default path)

    Examples
    --------
    >>> from src.presentation.callbacks.download_callbacks import register_download_callbacks
    >>> register_download_callbacks(app)

    Notes
    -----
    - Call this function in biorempp_app.py after registering other callbacks
    - Requires download_config.yaml to be present
    - Automatically registers callbacks for all configured use cases
    """
    factory = DownloadCallbackFactory(config_path)
    factory.register_all_callbacks(app)
    logger.info("[DOWNLOAD] All download callbacks registered successfully")
