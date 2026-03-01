"""
Resume store contract for job resume persistence backends.
"""

from abc import ABC, abstractmethod
from typing import Optional


class ResumeStore(ABC):
    """Abstract backend interface for resume payload persistence."""

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Return backend identifier for logging and diagnostics."""

    @abstractmethod
    def set(self, key: str, value: dict, ttl_seconds: int) -> bool:
        """Persist value with TTL. Returns True on success."""

    @abstractmethod
    def get(self, key: str) -> Optional[dict]:
        """Load value by key. Returns None when missing or invalid."""

    @abstractmethod
    def close(self) -> None:
        """Release backend resources."""

