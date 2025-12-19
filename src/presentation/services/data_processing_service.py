"""
BioRemPP Web - Data Processing Service
======================================

Service for processing uploaded files and merging with databases.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

logger = logging.getLogger(__name__)


class DataProcessingService:
    """
    Service for processing uploaded KO data and merging with databases.

    Handles:
    - File parsing (sample-based KO format)
    - Database loading and merging
    - Result aggregation
    - Metadata generation
    """

    def __init__(self, database_path: Optional[Path] = None):
        """
        Initialize data processing service.

        Parameters
        ----------
        database_path : Optional[Path]
            Path to databases directory. If None, uses default location.
        """
        if database_path is None:
            # Default to data/databases relative to biorempp_web root
            current_dir = Path(__file__).parent  # services/
            biorempp_web_root = current_dir.parent.parent  # biorempp_web/
            database_path = biorempp_web_root / "data" / "databases"

        self.database_path = Path(database_path)
        self._databases: Dict[str, pd.DataFrame] = {}
        self._load_databases()

    def _load_databases(self) -> None:
        """Load all databases into memory."""
        db_files = {
            "biorempp": "biorempp_db.csv",
            "hadeg": "hadeg_db.csv",
            "toxcsm": "toxcsm_db.csv",
            "kegg": "kegg_degradation_db.csv",
        }

        for db_name, filename in db_files.items():
            db_path = self.database_path / filename
            if db_path.exists():
                # All databases use semicolon separator
                self._databases[db_name] = pd.read_csv(
                    db_path, sep=";", encoding="utf-8"
                )
            else:
                raise FileNotFoundError(f"Database not found: {db_path}")

    def parse_upload_content(self, content: str, filename: str) -> pd.DataFrame:
        """
        Parse uploaded file content into sample-KO DataFrame.

        Expected format:
        >Sample Name
        K00001
        K00002
        >Another Sample
        K00003

        Parameters
        ----------
        content : str
            File content string
        filename : str
            Original filename

        Returns
        -------
        pd.DataFrame
            DataFrame with columns: Sample, KO
        """
        lines = content.strip().split("\n")

        data = []
        current_sample = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith(">"):
                # Sample name line
                current_sample = line[1:].strip()
            elif current_sample:
                # KO line
                ko = line.strip()
                if ko.startswith("K"):  # Validate KO format
                    data.append({"Sample": current_sample, "KO": ko})

        return pd.DataFrame(data)

    def merge_with_biorempp(self, sample_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge sample data with BioRemPP database.

        Parameters
        ----------
        sample_df : pd.DataFrame
            Sample-KO DataFrame

        Returns
        -------
        pd.DataFrame
            Merged results with BioRemPP annotations
        """
        biorempp_db = self._databases["biorempp"]

        # Merge on KO
        merged = sample_df.merge(biorempp_db, left_on="KO", right_on="ko", how="inner")

        # Select and rename columns for output
        result = merged[
            [
                "Sample",
                "KO",
                "cpd",
                "compoundname",
                "genesymbol",
                "referenceAG",
                "compoundclass",
                "enzyme_activity",
            ]
        ].copy()

        result.columns = [
            "Sample",
            "KO",
            "Compound_ID",
            "Compound_Name",
            "Gene_Symbol",
            "Agency",
            "Compound_Class",
            "Enzyme_Activity",
        ]

        return result

    def merge_with_hadeg(self, sample_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge sample data with HADEG database.

        Parameters
        ----------
        sample_df : pd.DataFrame
            Sample-KO DataFrame

        Returns
        -------
        pd.DataFrame
            Merged results with HADEG pathways
        """
        hadeg_db = self._databases["hadeg"]

        # Merge on KO
        merged = sample_df.merge(hadeg_db, left_on="KO", right_on="ko", how="inner")

        # Select and rename columns
        result = merged[["Sample", "KO", "Gene", "Pathway", "compound_pathway"]].copy()

        result.columns = ["Sample", "KO", "Gene", "Pathway", "Compound"]

        return result

    def merge_with_toxcsm(self, biorempp_df: pd.DataFrame) -> pd.DataFrame:
        """
        Process ToxCSM database to long format with all value_ columns.

        Transforms wide ToxCSM data into long format containing:
        - compoundname: Compound identifier
        - endpoint: Toxicity endpoint name (without 'value_' prefix)
        - toxicity_score: Numeric toxicity score (0-1)
        - super_category: Mapped category (Nuclear Response, Genomic, etc.)
        - prefix: Original endpoint prefix (NR, SR, Gen, Env, Org)

        Parameters
        ----------
        biorempp_df : pd.DataFrame
            BioRemPP merged results (not used, kept for compatibility)

        Returns
        -------
        pd.DataFrame
            Long-format toxicity data with all endpoints
        """
        toxcsm_db = self._databases["toxcsm"]

        # Category mapping for super-categories
        category_mapping = {
            "NR": "Nuclear Response",
            "SR": "Stress Response",
            "Gen": "Genomic",
            "Env": "Environmental",
            "Org": "Organic",
        }

        # Identify value_ columns
        value_columns = [col for col in toxcsm_db.columns if col.startswith("value_")]

        if not value_columns:
            logger.warning("[ToxCSM] No value_ columns found in database")
            return pd.DataFrame()

        # Select compoundname + value_ columns and remove duplicates
        required_cols = ["compoundname"] + value_columns
        df_tox = toxcsm_db[required_cols].drop_duplicates()

        # Convert to long format (wide → long)
        df_long = df_tox.melt(
            id_vars=["compoundname"],
            value_vars=value_columns,
            var_name="endpoint",
            value_name="toxicity_score",
        )

        # Convert score to numeric and remove NAs
        df_long["toxicity_score"] = pd.to_numeric(
            df_long["toxicity_score"], errors="coerce"
        )
        df_long = df_long.dropna(subset=["toxicity_score"])

        # Extract prefix from endpoint (e.g., 'value_NR_AR' → 'NR')
        df_long["prefix"] = df_long["endpoint"].str.split("_").str[1]

        # Map prefix to super-category
        df_long["super_category"] = df_long["prefix"].map(category_mapping)

        # Remove rows without mapped category
        df_long = df_long.dropna(subset=["super_category"])

        # Clean endpoint name (remove 'value_' prefix)
        df_long["endpoint"] = df_long["endpoint"].str.replace("value_", "", regex=False)

        # Keep unique compounds
        result = df_long.drop_duplicates()

        return result

    def merge_with_kegg(self, sample_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge sample data with KEGG pathways database.

        Parameters
        ----------
        sample_df : pd.DataFrame
            Sample-KO DataFrame

        Returns
        -------
        pd.DataFrame
            Merged results with KEGG pathway annotations
            Columns: Sample, KO, Pathway, Gene_Symbol
        """
        kegg_db = self._databases["kegg"]

        # Merge on KO
        merged = sample_df.merge(kegg_db, left_on="KO", right_on="ko", how="inner")

        # Select and rename columns for TABLE display
        result = merged[["Sample", "KO", "pathname", "genesymbol"]].copy()

        result.columns = ["Sample", "KO", "Pathway", "Gene_Symbol"]

        return result

    def _get_toxcsm_wide_format(self, biorempp_df: pd.DataFrame) -> pd.DataFrame:
        """
        Get ToxCSM data in wide format (66 columns) merged with user samples.

        This uses the same merge logic as graphs but returns wide format instead of long.
        Merges: User Input → BioRemPP (gets cpd) → ToxCSM (gets toxicity data)

        Parameters
        ----------
        biorempp_df : pd.DataFrame
            BioRemPP merged data (contains Sample and cpd columns)

        Returns
        -------
        pd.DataFrame
            ToxCSM wide format with Sample column
            Columns: Sample, cpd, SMILES, ChEBI, compoundname, value_*, label_* (66 total)
        """
        logger.info(f"[DEBUG] _get_toxcsm_wide_format called")
        logger.info(f"  - biorempp_df shape: {biorempp_df.shape}")
        logger.info(f"  - biorempp_df columns: {biorempp_df.columns.tolist()}")

        if biorempp_df.empty:
            logger.info(f"  - biorempp_df is empty, returning empty DataFrame")
            return pd.DataFrame()

        # Check for Compound_ID column (biorempp uses Compound_ID, not cpd)
        if "Compound_ID" not in biorempp_df.columns:
            logger.error(f"  - 'Compound_ID' column NOT FOUND in biorempp_df!")
            logger.error(f"  - Available columns: {biorempp_df.columns.tolist()}")
            return pd.DataFrame()

        # Get unique Sample-compound pairs from BioRemPP (user's matches)
        sample_compounds = biorempp_df[["Sample", "Compound_ID"]].drop_duplicates()

        # Rename to match ToxCSM database column name
        sample_compounds = sample_compounds.rename(columns={"Compound_ID": "cpd"})

        logger.info(f"  - Sample-compound pairs: {len(sample_compounds)}")
        logger.info(
            f"  - Sample compounds (first 5): {sample_compounds['cpd'].head().tolist()}"
        )

        # Merge with ToxCSM database (wide format, 66 columns)
        toxcsm_wide = pd.merge(
            sample_compounds, self._databases["toxcsm"], on="cpd", how="inner"
        )

        logger.info(f"  - ToxCSM wide merged shape: {toxcsm_wide.shape}")

        return toxcsm_wide

    def process_upload(self, content: str, filename: str) -> Dict[str, any]:
        """
        Complete processing pipeline for uploaded file.

        Parameters
        ----------
        content : str
            File content
        filename : str
            Original filename

        Returns
        -------
        Dict[str, any]
            Dictionary with:
            - biorempp_df: BioRemPP results DataFrame (for display)
            - biorempp_raw_df: BioRemPP merged data (for download - includes Sample column)
            - hadeg_df: HADEG results DataFrame (for display)
            - hadeg_raw_df: HADEG merged data (for download - includes Sample column)
            - toxcsm_df: ToxCSM results DataFrame (long format, 5 columns for graphs)
            - toxcsm_raw_df: ToxCSM merged data (wide format, 66 columns for table & download - includes Sample column)
            - kegg_df: KEGG results DataFrame (for display)
            - kegg_raw_df: KEGG merged data (for download - includes Sample column)
            - metadata: Processing metadata dict
        """
        start_time = time.time()

        # 1. Parse uploaded file
        sample_df = self.parse_upload_content(content, filename)

        if sample_df.empty:
            raise ValueError(
                "No valid data found in uploaded file. "
                "Check format: >Sample_Name followed by KO IDs"
            )

        # 2. Merge with each database
        # BioRemPP: Merged data with samples
        biorempp_df = self.merge_with_biorempp(sample_df)
        biorempp_raw_df = biorempp_df.copy()  # For download (has Sample column)

        # HADEG: Merged data with samples
        hadeg_df = self.merge_with_hadeg(sample_df)
        hadeg_raw_df = hadeg_df.copy()  # For download (has Sample column)

        # KEGG: Merged data with samples
        kegg_df = self.merge_with_kegg(sample_df)
        kegg_raw_df = kegg_df.copy()  # For download (has Sample column)

        # ToxCSM: Long format for graphs, wide format for download
        toxcsm_df = self.merge_with_toxcsm(
            biorempp_df
        )  # Long format (5 columns) for graphs
        toxcsm_raw_df = self._get_toxcsm_wide_format(
            biorempp_df
        )  # Wide format (66 columns) for download

        # 3. Generate metadata
        processing_time = time.time() - start_time

        sample_count = sample_df["Sample"].nunique()
        total_kos = len(sample_df)
        matched_kos = len(biorempp_df["KO"].unique())

        metadata = {
            "filename": filename,
            "sample_count": sample_count,
            "ko_count": total_kos,
            "processing_time": round(processing_time, 2),
            "matched_kos": matched_kos,
            "total_kos": total_kos,
            "databases": ["BioRemPP", "HADEG", "ToxCSM", "KEGG"],
            "timestamp": datetime.now().isoformat(),
        }

        # Debug logging for ToxCSM data
        logger.info(f"[DEBUG] ToxCSM data fields:")
        logger.info(f"  - toxcsm_df (graphs): {len(toxcsm_df)} rows")
        logger.info(f"  - toxcsm_raw_df (table & download): {len(toxcsm_raw_df)} rows")

        return {
            "biorempp_df": biorempp_df,  # For display
            "biorempp_raw_df": biorempp_raw_df,  # For download (merged data with Sample)
            "hadeg_df": hadeg_df,  # For display
            "hadeg_raw_df": hadeg_raw_df,  # For download (merged data with Sample)
            "toxcsm_df": toxcsm_df,  # For graphs (long format, 5 columns)
            "toxcsm_raw_df": toxcsm_raw_df,  # For table & download (wide format, 66 columns with Sample)
            "kegg_df": kegg_df,  # For display
            "kegg_raw_df": kegg_raw_df,  # For download (merged data with Sample)
            "metadata": metadata,
        }

    def get_database_stats(self) -> Dict[str, int]:
        """
        Get statistics about loaded databases.

        Returns
        -------
        Dict[str, int]
            Dictionary with row counts for each database
        """
        return {db_name: len(df) for db_name, df in self._databases.items()}
