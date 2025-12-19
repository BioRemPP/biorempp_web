"""
Merge Service.

Domain service to orchestrate merges with databases.

Classes
-------
DatabaseRepository
    Protocol defining repository interface
MergeService
    Service coordinating merges with 4 databases
"""

import logging
from typing import Any, Dict, Protocol

from src.shared.logging import get_logger, log_execution, log_performance

from ..entities.dataset import Dataset
from ..entities.merged_data import MergedData

# Logger for this module
logger = get_logger(__name__)


class DatabaseRepository(Protocol):
    """
    Protocol (interface) for database repositories.

    Defines the contract that all database repositories
    must implement.

    Notes
    -----
    This is a Python Protocol (PEP 544) that allows duck typing
    while maintaining type safety. Concrete implementations will be in
    the Infrastructure layer.
    """

    def load(self) -> Dict[str, Any]:
        """
        Load data from the database.

        Returns
        -------
        Dict[str, Any]
            Database data in dictionary format
        """
        ...


class MergeService:
    """
    Domain service to orchestrate merges with databases.

    Coordinates the process of merging the input dataset with the
    4 system databases: BioRemPP, KEGG, HADEG, and ToxCSM.

    Parameters
    ----------
    biorempp_repo : DatabaseRepository
        Repository for the BioRemPP database
    kegg_repo : DatabaseRepository
        Repository for the KEGG database
    hadeg_repo : DatabaseRepository
        Repository for the HADEG database
    toxcsm_repo : DatabaseRepository
        Repository for the ToxCSM database

    Notes
    -----
    This service depends on repositories that will be injected,
    following the Dependency Inversion Principle (SOLID).
    """

    def __init__(
        self,
        biorempp_repo: DatabaseRepository,
        kegg_repo: DatabaseRepository,
        hadeg_repo: DatabaseRepository,
        toxcsm_repo: DatabaseRepository,
    ):
        """
        Initialize the service with the necessary repositories.

        Parameters
        ----------
        biorempp_repo : DatabaseRepository
            BioRemPP repository
        kegg_repo : DatabaseRepository
            KEGG repository
        hadeg_repo : DatabaseRepository
            HADEG repository
        toxcsm_repo : DatabaseRepository
            ToxCSM repository
        """
        self.biorempp_repo = biorempp_repo
        self.kegg_repo = kegg_repo
        self.hadeg_repo = hadeg_repo
        self.toxcsm_repo = toxcsm_repo

        logger.info(
            "MergeService initialized",
            extra={"repositories": ["biorempp", "kegg", "hadeg", "toxcsm"]},
        )

    @log_execution(level=logging.INFO)
    @log_performance(threshold_ms=1000.0)
    def merge_all(self, dataset: Dataset) -> MergedData:
        """
        Execute all merges sequentially.

        Parameters
        ----------
        dataset : Dataset
            Input dataset with samples and KOs

        Returns
        -------
        MergedData
            Entity with all merge results

        Raises
        ------
        ValueError
            If any mandatory merge fails

        Notes
        -----
        The process follows this order:
        1. Merge with BioRemPP (mandatory)
        2. Merge with KEGG (mandatory)
        3. Merge with HADEG (mandatory)
        4. Merge with ToxCSM (optional, depends on compounds)
        """
        logger.info(
            "Starting merge process",
            extra={
                "sample_count": dataset.total_samples,
                "ko_count": dataset.total_kos,
            },
        )

        # Convert dataset to dictionary format
        input_data = dataset.to_dict()

        # Merge 1: BioRemPP (main base)
        logger.debug("Starting BioRemPP merge")
        biorempp_db = self.biorempp_repo.load()
        biorempp_merged = self._merge_by_ko(input_data, biorempp_db)
        logger.debug("BioRemPP merge completed")

        # Merge 2: KEGG
        logger.debug("Starting KEGG merge")
        kegg_db = self.kegg_repo.load()
        kegg_merged = self._merge_by_ko(input_data, kegg_db)
        logger.debug("KEGG merge completed")

        # Merge 3: HADEG
        logger.debug("Starting HADEG merge")
        hadeg_db = self.hadeg_repo.load()
        hadeg_merged = self._merge_by_ko(input_data, hadeg_db)
        logger.debug("HADEG merge completed")

        # Merge 4: ToxCSM (uses compounds from biorempp)
        logger.debug("Starting ToxCSM merge")
        toxcsm_db = self.toxcsm_repo.load()
        toxcsm_merged = self._merge_toxcsm(biorempp_merged, toxcsm_db)
        logger.debug("ToxCSM merge completed")

        # Create MergedData entity
        merged_data = MergedData(
            original_dataset=dataset,
            biorempp_data=biorempp_merged,
            kegg_data=kegg_merged,
            hadeg_data=hadeg_merged,
            toxcsm_data=toxcsm_merged,
        )

        # Validate result
        try:
            merged_data.validate()
            logger.info(
                "Merge process completed successfully",
                extra={"is_fully_merged": merged_data.is_fully_merged},
            )
        except ValueError as e:
            logger.error("Merge validation failed", extra={"error": str(e)})
            raise

        return merged_data

    @log_execution(level=logging.INFO)
    def merge_biorempp(self, dataset: Dataset) -> Dict[str, Any]:
        """
        Execute only the merge with BioRemPP.

        Parameters
        ----------
        dataset : Dataset
            Input dataset

        Returns
        -------
        Dict[str, Any]
            Data merged with BioRemPP

        Notes
        -----
        Useful for partial or incremental processing.
        """
        logger.info(
            "Starting BioRemPP-only merge",
            extra={"sample_count": dataset.total_samples},
        )

        input_data = dataset.to_dict()
        biorempp_db = self.biorempp_repo.load()
        result = self._merge_by_ko(input_data, biorempp_db)

        logger.info("BioRemPP merge completed")
        return result

    @staticmethod
    def _merge_by_ko(
        input_data: Dict[str, Any], database: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Helper for merging using KO as the key.

        Parameters
        ----------
        input_data : Dict[str, Any]
            Input data (samples + KOs)
        database : Dict[str, Any]
            Database data

        Returns
        -------
        Dict[str, Any]
            Merged data

        Notes
        -----
        Simplified implementation. In practice, this would use pandas.merge()
        or similar logic. Here, we only maintain the data structure.
        """
        # Simulate merge - real implementation would use pandas
        # For now, return a combined structure
        merged = {
            "input": input_data,
            "database": database,
            "merge_key": "ko",
        }
        return merged

    @staticmethod
    def _merge_toxcsm(
        biorempp_data: Dict[str, Any], toxcsm_db: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Specific merge for ToxCSM using compounds.

        Parameters
        ----------
        biorempp_data : Dict[str, Any]
            Data already merged with BioRemPP
        toxcsm_db : Dict[str, Any]
            ToxCSM database

        Returns
        -------
        Dict[str, Any]
            Data merged with ToxCSM

        Notes
        -----
        ToxCSM uses compounds (cpd) as the key, not KOs.
        That's why it needs the BioRemPP data first.
        If there are no compounds, it returns empty.
        """
        # Check if there is compound data
        if "database" not in biorempp_data:
            return {}

        # Simulate merge by compound
        merged = {
            "biorempp_base": biorempp_data,
            "toxcsm": toxcsm_db,
            "merge_key": "cpd",
        }
        return merged

    @log_execution(level=logging.DEBUG)
    def get_merge_statistics(self, merged_data: MergedData) -> Dict[str, Any]:
        """
        Calculate statistics about the merges performed.

        Parameters
        ----------
        merged_data : MergedData
            Merged data

        Returns
        -------
        Dict[str, Any]
            Merge statistics
        """
        status = merged_data.get_merge_status()

        stats = {
            "total_databases": 4,
            "successful_merges": sum(status.values()),
            "merge_status": status,
            "is_fully_merged": merged_data.is_fully_merged,
            "total_samples": merged_data.original_dataset.total_samples,
            "total_kos": merged_data.original_dataset.total_kos,
        }

        logger.debug(
            "Merge statistics calculated",
            extra={
                "successful_merges": stats["successful_merges"],
                "is_fully_merged": stats["is_fully_merged"],
            },
        )

        return stats
