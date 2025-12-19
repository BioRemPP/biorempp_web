"""
Database Download Callbacks

Handles download functionality for merged database data (BioRemPP, HADEG, KEGG, ToxCSM).
Users can download their merged results in CSV, Excel, or JSON format.
"""

import logging

import pandas as pd
from dash import Input, Output, State, ctx, dcc

from src.application.core.result_exporter import ResultExporter

logger = logging.getLogger(__name__)

# Column name mappings to restore original CSV headers for downloads
BIOREMPP_COLUMN_MAP = {
    "Sample": "Sample",
    "KO": "ko",
    "Gene_Symbol": "genesymbol",
    "Gene_Name": "genename",
    "Compound_ID": "cpd",
    "Compound_Class": "compoundclass",
    "Agency": "referenceAG",
    "Compound_Name": "compoundname",
    "Enzyme_Activity": "enzyme_activity",
}

HADEG_COLUMN_MAP = {
    "Sample": "Sample",
    "KO": "ko",
    "Gene": "Gene",
    "Pathway": "Pathway",
    "Compound": "compound_pathway",
}

KEGG_COLUMN_MAP = {
    "Sample": "Sample",
    "KO": "ko",
    "Pathway": "pathname",
    "Gene_Symbol": "genesymbol",
}


def register_database_download_callbacks(app):
    """
    Register all database download callbacks.

    Args:
        app: Dash application instance
    """
    logger.info("[OK] Registering database download callbacks...")

    # BioRemPP Database Download
    @app.callback(
        Output("biorempp-db-download", "data"),
        [
            Input("biorempp-db-download-btn-csv", "n_clicks"),
            Input("biorempp-db-download-btn-excel", "n_clicks"),
            Input("biorempp-db-download-btn-json", "n_clicks"),
        ],
        [State("merged-result-store", "data")],
        prevent_initial_call=True,
    )
    def download_biorempp_database(csv_clicks, excel_clicks, json_clicks, merged_data):
        """Download BioRemPP merged database in selected format."""
        logger.info(
            f"[DEBUG] BioRemPP download triggered: csv={csv_clicks}, excel={excel_clicks}, json={json_clicks}"
        )

        if not ctx.triggered or not merged_data:
            logger.info("  - No trigger or no data, returning None")
            return None

        # Determine format from triggered button
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]
        logger.info(f"  - Triggered ID: {triggered_id}")

        if "csv" in triggered_id:
            format_type = "csv"
        elif "excel" in triggered_id:
            format_type = "excel"
        elif "json" in triggered_id:
            format_type = "json"
        else:
            return None

        # Get merged data
        biorempp_raw = merged_data.get("biorempp_raw_df", [])
        if not biorempp_raw:
            return None

        # Convert to DataFrame
        df = pd.DataFrame(biorempp_raw)

        # Restore original CSV column names
        df = df.rename(columns=BIOREMPP_COLUMN_MAP)

        # Export using ResultExporter
        exporter = ResultExporter()

        if format_type == "csv":
            result = exporter.export_to_csv(df, "BioRemPP_Results.csv")
        elif format_type == "excel":
            result = exporter.export_to_excel(
                df, "BioRemPP_Results.xlsx", sheet_name="BioRemPP"
            )
        elif format_type == "json":
            result = exporter.export_to_json(df, "BioRemPP_Results.json")
        else:
            return None

        if result.success:
            return dcc.send_bytes(result.data, result.filename)

        return None

    # HADEG Database Download
    @app.callback(
        Output("hadeg-db-download", "data"),
        [
            Input("hadeg-db-download-btn-csv", "n_clicks"),
            Input("hadeg-db-download-btn-excel", "n_clicks"),
            Input("hadeg-db-download-btn-json", "n_clicks"),
        ],
        [State("merged-result-store", "data")],
        prevent_initial_call=True,
    )
    def download_hadeg_database(csv_clicks, excel_clicks, json_clicks, merged_data):
        """Download HADEG merged database in selected format."""
        if not ctx.triggered or not merged_data:
            return None

        # Determine format
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if "csv" in triggered_id:
            format_type = "csv"
        elif "excel" in triggered_id:
            format_type = "excel"
        elif "json" in triggered_id:
            format_type = "json"
        else:
            return None

        # Get merged data
        hadeg_raw = merged_data.get("hadeg_raw_df", [])
        if not hadeg_raw:
            return None

        df = pd.DataFrame(hadeg_raw)

        # Restore original CSV column names
        df = df.rename(columns=HADEG_COLUMN_MAP)

        # Export
        exporter = ResultExporter()

        if format_type == "csv":
            result = exporter.export_to_csv(df, "HADEG_Results.csv")
        elif format_type == "excel":
            result = exporter.export_to_excel(
                df, "HADEG_Results.xlsx", sheet_name="HADEG"
            )
        elif format_type == "json":
            result = exporter.export_to_json(df, "HADEG_Results.json")
        else:
            return None

        if result.success:
            return dcc.send_bytes(result.data, result.filename)

        return None

    # KEGG Database Download
    @app.callback(
        Output("kegg-db-download", "data"),
        [
            Input("kegg-db-download-btn-csv", "n_clicks"),
            Input("kegg-db-download-btn-excel", "n_clicks"),
            Input("kegg-db-download-btn-json", "n_clicks"),
        ],
        [State("merged-result-store", "data")],
        prevent_initial_call=True,
    )
    def download_kegg_database(csv_clicks, excel_clicks, json_clicks, merged_data):
        """Download KEGG merged database in selected format."""
        if not ctx.triggered or not merged_data:
            return None

        # Determine format
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if "csv" in triggered_id:
            format_type = "csv"
        elif "excel" in triggered_id:
            format_type = "excel"
        elif "json" in triggered_id:
            format_type = "json"
        else:
            return None

        # Get merged data
        kegg_raw = merged_data.get("kegg_raw_df", [])
        if not kegg_raw:
            return None

        df = pd.DataFrame(kegg_raw)

        # Restore original CSV column names
        df = df.rename(columns=KEGG_COLUMN_MAP)

        # Export
        exporter = ResultExporter()

        if format_type == "csv":
            result = exporter.export_to_csv(df, "KEGG_Results.csv")
        elif format_type == "excel":
            result = exporter.export_to_excel(
                df, "KEGG_Results.xlsx", sheet_name="KEGG"
            )
        elif format_type == "json":
            result = exporter.export_to_json(df, "KEGG_Results.json")
        else:
            return None

        if result.success:
            return dcc.send_bytes(result.data, result.filename)

        return None

    # ToxCSM Database Download
    @app.callback(
        Output("toxcsm-db-download", "data"),
        [
            Input("toxcsm-db-download-btn-csv", "n_clicks"),
            Input("toxcsm-db-download-btn-excel", "n_clicks"),
            Input("toxcsm-db-download-btn-json", "n_clicks"),
        ],
        [State("merged-result-store", "data")],
        prevent_initial_call=True,
    )
    def download_toxcsm_database(csv_clicks, excel_clicks, json_clicks, merged_data):
        """Download ToxCSM merged database in selected format (wide format, 66 columns)."""
        if not ctx.triggered or not merged_data:
            return None

        # Determine format
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if "csv" in triggered_id:
            format_type = "csv"
        elif "excel" in triggered_id:
            format_type = "excel"
        elif "json" in triggered_id:
            format_type = "json"
        else:
            return None

        # Get merged data (wide format with 66 columns)
        toxcsm_raw = merged_data.get("toxcsm_raw_df", [])
        if not toxcsm_raw:
            return None

        df = pd.DataFrame(toxcsm_raw)

        # Export
        exporter = ResultExporter()

        if format_type == "csv":
            result = exporter.export_to_csv(df, "toxCSM.csv")
        elif format_type == "excel":
            result = exporter.export_to_excel(df, "toxCSM.xlsx", sheet_name="ToxCSM")
        elif format_type == "json":
            result = exporter.export_to_json(df, "toxCSM.json")
        else:
            return None

        if result.success:
            return dcc.send_bytes(result.data, result.filename)

        return None
