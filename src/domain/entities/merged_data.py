"""
MergedData Entity

Represents the result of merging the dataset with external databases.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional

from .dataset import Dataset


@dataclass
class MergedData:
    """
    Entity that represents the result of the merge with databases.

    This entity is immutable after creation to ensure consistency
    of the processed data. It contains the original dataset and the results
    of the merges with each of the 4 system databases.

    Parameters
    ----------
    original_dataset : Dataset
        Original dataset before the merges
    biorempp_data : Optional[Dict[str, Any]], default=None
        Data resulting from the merge with the BioRemPP database
    kegg_data : Optional[Dict[str, Any]], default=None
        Data resulting from the merge with the KEGG database
    hadeg_data : Optional[Dict[str, Any]], default=None
        Data resulting from the merge with the HADEG database
    toxcsm_data : Optional[Dict[str, Any]], default=None
        Data resulting from the merge with the ToxCSM database

    Raises
    ------
    ValueError
        If validated without a mandatory merge (BioRemPP)

    Notes
    -----
    BioRemPP, KEGG, and HADEG are considered mandatory merges.
    ToxCSM is optional as it depends on the presence of compounds in the data.
    """

    original_dataset: Dataset
    biorempp_data: Optional[Dict[str, Any]] = None
    kegg_data: Optional[Dict[str, Any]] = None
    hadeg_data: Optional[Dict[str, Any]] = None
    toxcsm_data: Optional[Dict[str, Any]] = None

    @property
    def is_biorempp_merged(self) -> bool:
        """
        Checks if the merge with BioRemPP was executed.

        Returns
        -------
        bool
            True if BioRemPP data is present and not empty.
        """
        return self.biorempp_data is not None and bool(self.biorempp_data)

    @property
    def is_kegg_merged(self) -> bool:
        """
        Checks if the merge with KEGG was executed.

        Returns
        -------
        bool
            True if KEGG data is present and not empty.
        """
        return self.kegg_data is not None and bool(self.kegg_data)

    @property
    def is_hadeg_merged(self) -> bool:
        """
        Checks if the merge with HADEG was executed.

        Returns
        -------
        bool
            True if HADEG data is present and not empty.
        """
        return self.hadeg_data is not None and bool(self.hadeg_data)

    @property
    def is_toxcsm_merged(self) -> bool:
        """
        Checks if the merge with ToxCSM was executed.

        Returns
        -------
        bool
            True if ToxCSM data is present and not empty.
        """
        return self.toxcsm_data is not None and bool(self.toxcsm_data)

    @property
    def is_fully_merged(self) -> bool:
        """
        Checks if all mandatory merges were executed.

        Returns
        -------
        bool
            True if BioRemPP, KEGG, and HADEG were merged.

        Notes
        -----
        ToxCSM is not considered mandatory as it depends on the presence
        of compounds in the data.
        """
        return all(
            [
                self.is_biorempp_merged,
                self.is_kegg_merged,
                self.is_hadeg_merged,
            ]
        )

    def get_merge_status(self) -> Dict[str, bool]:
        """
        Returns the status of all merges.

        Returns
        -------
        Dict[str, bool]
            Dictionary with the status of each database.

        Examples
        --------
        >>> status = merged.get_merge_status()
        >>> status
        {
            'biorempp': True,
            'kegg': True,
            'hadeg': True,
            'toxcsm': False
        }
        """
        return {
            "biorempp": self.is_biorempp_merged,
            "kegg": self.is_kegg_merged,
            "hadeg": self.is_hadeg_merged,
            "toxcsm": self.is_toxcsm_merged,
        }

    def validate(self) -> None:
        """
        Validates the merge state.

        Raises
        ------
        ValueError
            If the BioRemPP merge was not executed (mandatory).

        Notes
        -----
        Only BioRemPP is validated as it is the fundamental database.
        KEGG and HADEG may be optional depending on the context of use.
        """
        if not self.is_biorempp_merged:
            raise ValueError("BioRemPP merge is required")

    def __str__(self) -> str:
        """
        Returns the string representation of the merged data.

        Returns
        -------
        str
            Descriptive string of the merge status.
        """
        status = self.get_merge_status()
        merged_count = sum(status.values())
        return f"MergedData ({merged_count}/4 databases merged)"

    def __repr__(self) -> str:
        """
        Returns the debug representation of the merged data.

        Returns
        -------
        str
            Detailed representation.
        """
        return (
            f"MergedData("
            f"biorempp={self.is_biorempp_merged}, "
            f"kegg={self.is_kegg_merged}, "
            f"hadeg={self.is_hadeg_merged}, "
            f"toxcsm={self.is_toxcsm_merged})"
        )
