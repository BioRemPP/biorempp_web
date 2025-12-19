"""
Database Repository Interface.

Defines the contract for database repositories following the Repository
Pattern.

Classes
-------
DatabaseRepository
    Protocol defining repository interface for database access
"""

from typing import Any, Dict, Protocol


class DatabaseRepository(Protocol):
    """
    Interface for database repositories.

    Defines the contract that all repository implementations
    must follow, ensuring consistency and allowing substitution.

    Notes
    -----
    This is a Protocol class (PEP 544) that allows structural
    subtyping (duck typing) with type safety. Concrete
    implementations will be in the Infrastructure layer.
    """

    def load(self) -> Dict[str, Any]:
        """
        Load data from the database.

        Returns
        -------
        Dict[str, Any]
            Database data in dictionary format or a structure
            compatible with pandas DataFrame

        Raises
        ------
        FileNotFoundError
            If the database file is not found
        ValueError
            If the data is in an invalid format

        Notes
        -----
        The exact format of the returned data depends on the implementation,
        but it must be compatible with merge operations.
        """
        ...
