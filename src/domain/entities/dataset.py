"""
Dataset Entity

Represents a collection of biological samples.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from src.shared.logging import get_logger

from ..value_objects.kegg_orthology import KO
from ..value_objects.sample_id import SampleId
from .sample import Sample

# Logger for this module
logger = get_logger(__name__)


@dataclass
class Dataset:
    """
    Aggregate - Collection of samples with high-level operations.

    Manages a set of biological samples and provides operations
    for queries and aggregate analysis on these samples.

    Parameters
    ----------
    samples : List[Sample], default=[]
        List of samples in dataset

    Notes
    -----
    Dataset is an Aggregate in DDD context that manages the collection
    of samples ensuring consistency through validations.
    """

    samples: List[Sample] = field(default_factory=list)

    def add_sample(self, sample: Sample) -> None:
        """
        Adds validated sample to dataset.

        Parameters
        ----------
        sample : Sample
            Sample to be added.

        Raises
        ------
        ValueError
            If sample does not pass validation.

        Notes
        -----
        Sample is validated before being added ensuring
        only valid samples enter the dataset.
        """
        try:
            sample.validate()
            self.samples.append(sample)
            logger.debug(
                "Sample added to dataset",
                extra={
                    "sample_id": str(sample.id),
                    "ko_count": sample.ko_count,
                    "total_samples": len(self.samples),
                },
            )
        except ValueError as e:
            logger.error(
                "Failed to add sample to dataset",
                extra={"sample_id": str(sample.id), "error": str(e)},
            )
            raise

    def remove_sample(self, sample_id: SampleId) -> bool:
        """
        Removes sample from dataset by ID.

        Parameters
        ----------
        sample_id : SampleId
            ID of sample to be removed.

        Returns
        -------
        bool
            True if sample was removed, False if not found.
        """
        sample = self.get_sample_by_id(sample_id)
        if sample:
            self.samples.remove(sample)
            return True
        return False

    @property
    def total_samples(self) -> int:
        """
        Returns total samples in dataset.

        Returns
        -------
        int
            Number of samples.
        """
        return len(self.samples)

    @property
    def total_kos(self) -> int:
        """
        Returns total unique KOs in dataset.

        Returns
        -------
        int
            Number of unique KOs considering all samples.

        Notes
        -----
        This property iterates through all samples and collects unique
        KOs using a set to eliminate duplicates.
        """
        unique_kos = set()
        for sample in self.samples:
            unique_kos.update(sample.ko_list)
        return len(unique_kos)

    def get_sample_by_id(self, sample_id: SampleId) -> Optional[Sample]:
        """
        Searches for sample by ID.

        Parameters
        ----------
        sample_id : SampleId
            ID of sample to be searched.

        Returns
        -------
        Optional[Sample]
            Found sample or None.
        """
        for sample in self.samples:
            if sample.id == sample_id:
                return sample
        return None

    def get_all_kos(self) -> List[KO]:
        """
        Returns list of all unique KOs from dataset.

        Returns
        -------
        List[KO]
            List of unique KOs.
        """
        unique_kos = set()
        for sample in self.samples:
            unique_kos.update(sample.ko_list)
        return list(unique_kos)

    def get_ko_distribution(self) -> Dict[KO, int]:
        """
        Returns KO distribution across samples.

        Returns
        -------
        Dict[KO, int]
            Dictionary mapping each KO to the number of samples
            in which it appears.

        Examples
        --------
        >>> distribution = dataset.get_ko_distribution()
        >>> distribution[KO('K00001')]
        5  # KO appears in 5 samples
        """
        distribution: Dict[KO, int] = {}
        for sample in self.samples:
            for ko in sample.ko_list:
                distribution[ko] = distribution.get(ko, 0) + 1
        return distribution

    def get_samples_with_ko(self, ko: KO) -> List[Sample]:
        """
        Returns samples containing a specific KO.

        Parameters
        ----------
        ko : KO
            KO to be searched.

        Returns
        -------
        List[Sample]
            List of samples containing the KO.
        """
        return [sample for sample in self.samples if sample.has_ko(ko)]

    def to_dict(self) -> Dict[str, List[str]]:
        """
        Converts dataset to dictionary format.

        Returns
        -------
        Dict[str, List[str]]
            Dictionary with format {'sample': [...], 'ko': [...]}.

        Notes
        -----
        This format is useful for later conversion to DataFrame.
        """
        records = {"sample": [], "ko": []}

        for sample in self.samples:
            for ko in sample.ko_list:
                records["sample"].append(str(sample.id))
                records["ko"].append(str(ko))

        return records

    def is_empty(self) -> bool:
        """
        Checks if dataset is empty.

        Returns
        -------
        bool
            True if there are no samples.
        """
        return self.total_samples == 0

    def validate(self) -> None:
        """
        Validates entire dataset.

        Raises
        ------
        ValueError
            If dataset is empty or if any sample is invalid.
        """
        if self.is_empty():
            raise ValueError("Dataset cannot be empty")

        for sample in self.samples:
            sample.validate()

    def __str__(self) -> str:
        """
        Returns string representation of dataset.

        Returns
        -------
        str
            Descriptive string.
        """
        return (
            f"Dataset with {self.total_samples} samples and {self.total_kos} unique KOs"
        )

    def __repr__(self) -> str:
        """
        Returns debug representation of dataset.

        Returns
        -------
        str
            Detailed representation.
        """
        return f"Dataset(samples={self.total_samples}, unique_kos={self.total_kos})"
