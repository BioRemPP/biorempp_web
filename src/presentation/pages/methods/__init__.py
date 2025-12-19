"""
Methods Page Package

This package contains the implementation of the Methods page,
which displays analytical workflows for all 56 use cases.
"""

# Import callbacks to register them
from . import overview_callbacks
from .methods_service import MethodsService, get_methods_service
from .module_metadata import (
    MODULE_METADATA,
    get_all_modules_metadata,
    get_module_color,
    get_module_icon,
    get_module_metadata,
)

__all__ = [
    "MethodsService",
    "get_methods_service",
    "MODULE_METADATA",
    "get_module_metadata",
    "get_all_modules_metadata",
    "get_module_color",
    "get_module_icon",
]
