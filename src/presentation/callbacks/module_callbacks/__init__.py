"""
Module Callbacks Initialization.

This module exports module-level callback registration functions for all
application modules.

Functions
---------
register_module1_callbacks
    Register Module 1 callbacks (Database Assessment).
register_module2_callbacks
    Register Module 2 callbacks (Rankings and Compound Analysis).
register_module3_callbacks
    Register Module 3 callbacks (Functional Similarity Analysis).
register_module4_callbacks
    Register Module 4 callbacks (Functional and Genetic Profiling).
register_module5_callbacks
    Register Module 5 callbacks (Interaction Networks).
register_module6_callbacks
    Register Module 6 callbacks.
register_module7_callbacks
    Register Module 7 callbacks.
register_module8_callbacks
    Register Module 8 callbacks (Functional Consortia Assembly).
"""

from src.presentation.callbacks.module_callbacks.module1_callbacks import (
    register_module1_callbacks,
)
from src.presentation.callbacks.module_callbacks.module2_callbacks import (
    register_module2_callbacks,
)
from src.presentation.callbacks.module_callbacks.module3_callbacks import (
    register_module3_callbacks,
)
from src.presentation.callbacks.module_callbacks.module4_callbacks import (
    register_module4_callbacks,
)
from src.presentation.callbacks.module_callbacks.module5_callbacks import (
    register_module5_callbacks,
)
from src.presentation.callbacks.module_callbacks.module6_callbacks import (
    register_module6_callbacks,
)
from src.presentation.callbacks.module_callbacks.module7_callbacks import (
    register_module7_callbacks,
)
from src.presentation.callbacks.module_callbacks.module8_callbacks import (
    register_module8_callbacks,
)

__all__ = [
    "register_module1_callbacks",
    "register_module2_callbacks",
    "register_module3_callbacks",
    "register_module4_callbacks",
    "register_module5_callbacks",
    "register_module6_callbacks",
    "register_module7_callbacks",
    "register_module8_callbacks",
]
