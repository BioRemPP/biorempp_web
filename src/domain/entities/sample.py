"""
Sample Entity

Represents a biological sample with its associated KOs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List

from src.shared.logging import get_logger

from ..value_objects.kegg_orthology import KO
from ..value_objects.sample_id import SampleId

# Logger for this module
logger = get_logger(__name__)


@dataclass
class Sample:
    """
    Aggregate Root - Represents a biological sample.

    Encapsulates business rules related to samples and their associated KOs.
    A sample is uniquely identified by its SampleId and contains a list
    of KOs (KEGG Orthology) that were detected in it.

    Parameters
    ----------
    id : SampleId
        Unique sample identifier
    ko_list : List[KO], default=[]
        List of KOs associated with the sample
    created_at : datetime, default=datetime.now()
        Sample creation timestamp
    metadata : Dict[str, Any], default={}
        Additional sample metadata

    Raises
    ------
    ValueError
        If sample is validated without at least one KO

    Notes
    -----
    This is an Aggregate Root entity in DDD context, responsible for
    maintaining consistency of its invariants (e.g., every valid sample must
    have at least one KO).
    """

    id: SampleId
    ko_list: List[KO] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_ko(self, ko: KO) -> None:
        """
        Adds a KO to the sample with duplicate validation.

        Parameters
        ----------
        ko : KO
            KO to be added.

        Notes
        -----
        Duplicate KOs are automatically ignored.
        """
        if ko not in self.ko_list:
            self.ko_list.append(ko)
            logger.debug(
                "KO added to sample",
                extra={
                    "sample_id": str(self.id),
                    "ko": str(ko),
                    "total_kos": len(self.ko_list),
                },
            )
        else:
            logger.debug(
                "Duplicate KO ignored", extra={"sample_id": str(self.id), "ko": str(ko)}
            )

    def remove_ko(self, ko: KO) -> None:
        """
        Removes a KO from the sample if it exists.

        Parameters
        ----------
        ko : KO
            KO to be removed.

        Notes
        -----
        If KO does not exist in the list, operation is silently ignored.
        """
        if ko in self.ko_list:
            self.ko_list.remove(ko)

    @property
    def ko_count(self) -> int:
        """
        Returns quantity of KOs associated with the sample.

        Returns
        -------
        int
            Number of KOs in the list.
        """
        return len(self.ko_list)

    def has_ko(self, ko: KO) -> bool:
        """
        Checks if sample has a specific KO.

        Parameters
        ----------
        ko : KO
            KO to be checked.

        Returns
        -------
        bool
            True if KO is present in the sample.
        """
        return ko in self.ko_list

    def get_unique_kos(self) -> List[KO]:
        """
        Returns list of unique KOs (without duplicates).

        Returns
        -------
        List[KO]
            List of unique KOs.

        Notes
        -----
        In practice, ko_list should not contain duplicates due to
        add_ko() method, but this method ensures uniqueness.
        """
        return list(set(self.ko_list))

    def validate(self) -> None:
        """
        Validates entity business rules.

        Raises
        ------
        ValueError
            If sample does not have at least one KO.

        Notes
        -----
        This validation ensures the business invariant: every processed
        sample must contain at least one valid KO.
        """
        if self.ko_count == 0:
            logger.error(
                "Sample validation failed: No KOs", extra={"sample_id": str(self.id)}
            )
            raise ValueError(f"Sample {self.id} must have at least one KO")

        logger.debug(
            "Sample validation successful",
            extra={"sample_id": str(self.id), "ko_count": self.ko_count},
        )

    def __str__(self) -> str:
        """
        Returns string representation of sample.

        Returns
        -------
        str
            String in format "Sample(id) with X KOs".
        """
        return f"Sample({self.id}) with {self.ko_count} KOs"

    def __repr__(self) -> str:
        """
        Returns debug representation of sample.

        Returns
        -------
        str
            Detailed representation.
        """
        return (
            f"Sample(id={self.id}, "
            f"ko_count={self.ko_count}, "
            f"created_at={self.created_at})"
        )

    def __eq__(self, other: object) -> bool:
        """
        Compares samples by identity (SampleId).

        Parameters
        ----------
        other : object
            Object to be compared.

        Returns
        -------
        bool
            True if both samples have the same ID.
        """
        if not isinstance(other, Sample):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """
        Hash based on sample identifier.

        Returns
        -------
        int
            Hash of SampleId.
        """
        return hash(self.id)
