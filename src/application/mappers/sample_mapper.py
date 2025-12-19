"""
Application Layer - Sample Mapper.

Maps between Sample domain entities and pandas DataFrames for
application layer operations.

Classes
-------
SampleMapper
    Bidirectional mapping between Sample entities and DataFrames

Notes
-----
- Stateless mapper (can be used as static methods)
- Preserves data integrity during conversion
- Handles validation at boundaries
"""

from typing import List

import pandas as pd

from src.domain.entities.dataset import Dataset
from src.domain.entities.sample import Sample
from src.domain.value_objects.kegg_orthology import KO
from src.domain.value_objects.sample_id import SampleId


class SampleMapper:
    """
    Map between Sample entities and DataFrames.

    Provides bidirectional conversion between domain entities (Sample,
    Dataset) and pandas DataFrames used by the application layer.

    Methods
    -------
    to_dataframe(dataset)
        Convert Dataset to DataFrame
    from_dataframe(df)
        Convert DataFrame to Dataset
    samples_to_dict(dataset)
        Convert Dataset to dictionary format

    Notes
    -----
    - All methods are static (stateless)
    - Preserves KO identifiers exactly
    - Handles empty datasets gracefully
    """

    @staticmethod
    def to_dataframe(dataset: Dataset) -> pd.DataFrame:
        """
        Convert Dataset to DataFrame.

        Parameters
        ----------
        dataset : Dataset
            Domain entity containing samples

        Returns
        -------
        pd.DataFrame
            DataFrame with columns: Sample, KO (each row is one Sample-KO pair)

        Notes
        -----
        - Each KO creates a new row
        - Sample ID is repeated for multiple KOs
        - Empty datasets return empty DataFrame with correct columns
        """
        if not dataset.samples:
            return pd.DataFrame(columns=["Sample", "KO"])

        data = []
        for sample in dataset.samples:
            sample_id_str = sample.id.value
            for ko in sample.ko_list:
                data.append({"Sample": sample_id_str, "KO": ko.id})

        return pd.DataFrame(data)

    @staticmethod
    def from_dataframe(df: pd.DataFrame) -> Dataset:
        """
        Convert DataFrame to Dataset.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame with columns: Sample, KO

        Returns
        -------
        Dataset
            Domain entity with reconstructed samples

        Raises
        ------
        ValueError
            If DataFrame missing required columns
        ValueError
            If DataFrame contains invalid KO identifiers

        Notes
        -----
        - Groups KOs by Sample ID
        - Validates KO format during conversion
        - Preserves original order of samples
        """
        if df.empty:
            return Dataset([])

        if "Sample" not in df.columns or "KO" not in df.columns:
            raise ValueError("DataFrame must have 'Sample' and 'KO' columns")

        # Group by Sample to collect KOs
        samples = []
        for sample_id, group in df.groupby("Sample", sort=False):
            # Create KO value objects
            kos = [KO(ko_id) for ko_id in group["KO"].values]

            # Create Sample entity
            sample = Sample(id=SampleId(str(sample_id)), ko_list=kos)
            samples.append(sample)

        return Dataset(samples)

    @staticmethod
    def samples_to_dict(dataset: Dataset) -> dict:
        """
        Convert Dataset to dictionary format.

        Parameters
        ----------
        dataset : Dataset
            Domain entity with samples

        Returns
        -------
        dict
            Dictionary with sample_id as keys, list of KO IDs as values

        Notes
        -----
        - Useful for JSON serialization
        - Preserves all KOs per sample
        - Returns empty dict for empty dataset
        """
        if not dataset.samples:
            return {}

        result = {}
        for sample in dataset.samples:
            sample_id = sample.id.value
            ko_ids = [ko.id for ko in sample.ko_list]
            result[sample_id] = ko_ids

        return result

    @staticmethod
    def dict_to_dataset(data: dict) -> Dataset:
        """
        Convert dictionary to Dataset.

        Parameters
        ----------
        data : dict
            Dictionary with sample_id as keys, list of KO IDs as values

        Returns
        -------
        Dataset
            Reconstructed domain entity

        Notes
        -----
        - Validates KO format during conversion
        - Preserves dictionary key order (Python 3.7+)
        """
        if not data:
            return Dataset([])

        samples = []
        for sample_id, ko_ids in data.items():
            kos = [KO(ko_id) for ko_id in ko_ids]
            sample = Sample(id=SampleId(str(sample_id)), ko_list=kos)
            samples.append(sample)

        return Dataset(samples)
