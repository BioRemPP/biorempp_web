"""
Dependency Injection Container - Component Management.

Provides simple DI container for managing application dependencies and
promoting loose coupling between components.

Classes
-------
DIContainer
    Dependency injection container with singleton and factory support
"""

from typing import Any, Callable, Dict, Type

from src.shared.logging import get_logger

logger = get_logger(__name__)


class DIContainer:
    """
    Dependency injection container.

    Manages singleton and factory registrations for application dependencies.
    Supports lazy initialization and dependency resolution.

    Attributes
    ----------
    _singletons : Dict[str, Any]
        Registered singleton instances
    _factories : Dict[str, Callable[[], Any]]
        Registered factory functions
    _types : Dict[str, Type]
        Registered types for lazy instantiation

    Methods
    -------
    register_singleton(name, instance)
        Register a singleton instance
    register_factory(name, factory)
        Register a factory function
    register_type(name, cls)
        Register a type for lazy instantiation
    resolve(name)
        Resolve dependency by name
    is_registered(name)
        Check if dependency is registered
    get_registered_names()
        Get list of registered dependency names
    clear()
        Clear all registrations
    unregister(name)
        Unregister a dependency
    """

    def __init__(self):
        """Initialize DI container."""
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}
        self._types: Dict[str, Type] = {}

        logger.info("Initialized DIContainer")

    def register_singleton(self, name: str, instance: Any) -> None:
        """
        Register a singleton instance.

        Parameters
        ----------
        name : str
            Dependency name
        instance : Any
            Instance to register
        """
        self._singletons[name] = instance

        logger.debug(
            f"Registered singleton: {name}", extra={"type": type(instance).__name__}
        )

    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """
        Register a factory function.

        Factory is called each time dependency is resolved.

        Parameters
        ----------
        name : str
            Dependency name
        factory : Callable[[], Any]
            Factory function that creates instances
        """
        self._factories[name] = factory

        logger.debug(f"Registered factory: {name}")

    def register_type(self, name: str, cls: Type) -> None:
        """
        Register a type for lazy instantiation.

        Type is instantiated (with no-arg constructor) when first resolved.

        Parameters
        ----------
        name : str
            Dependency name
        cls : Type
            Class to instantiate
        """
        self._types[name] = cls

        logger.debug(f"Registered type: {name}", extra={"class": cls.__name__})

    def resolve(self, name: str) -> Any:
        """
        Resolve dependency by name.

        Resolution order: singleton, factory, type.

        Parameters
        ----------
        name : str
            Dependency name

        Returns
        -------
        Any
            Resolved dependency instance

        Raises
        ------
        ValueError
            If dependency not found
        """
        # Try singleton first
        if name in self._singletons:
            return self._singletons[name]

        # Try factory
        if name in self._factories:
            instance = self._factories[name]()
            logger.debug(f"Created instance from factory: {name}")
            return instance

        # Try type (lazy singleton)
        if name in self._types:
            cls = self._types[name]
            instance = cls()
            # Cache as singleton
            self._singletons[name] = instance
            logger.debug(
                f"Created instance from type: {name}", extra={"class": cls.__name__}
            )
            return instance

        # Not found
        available = self.get_registered_names()
        raise ValueError(f"Dependency not found: '{name}'. " f"Available: {available}")

    def is_registered(self, name: str) -> bool:
        """
        Check if dependency is registered.

        Parameters
        ----------
        name : str
            Dependency name.

        Returns
        -------
        bool
            True if registered.
        """
        return (
            name in self._singletons or name in self._factories or name in self._types
        )

    def get_registered_names(self) -> list[str]:
        """
        Get list of registered dependency names.

        Returns
        -------
        list[str]
            List of dependency names.
        """
        return list(
            set(self._singletons.keys())
            | set(self._factories.keys())
            | set(self._types.keys())
        )

    def clear(self) -> None:
        """Clear all registrations."""
        count = len(self.get_registered_names())

        self._singletons.clear()
        self._factories.clear()
        self._types.clear()

        logger.info(f"Cleared DIContainer: {count} registrations removed")

    def unregister(self, name: str) -> bool:
        """
        Unregister a dependency.

        Parameters
        ----------
        name : str
            Dependency name.

        Returns
        -------
        bool
            True if unregistered, False if not found.
        """
        removed = False

        if name in self._singletons:
            del self._singletons[name]
            removed = True

        if name in self._factories:
            del self._factories[name]
            removed = True

        if name in self._types:
            del self._types[name]
            removed = True

        if removed:
            logger.debug(f"Unregistered dependency: {name}")

        return removed
