"""
UC User Guide Package - Interactive Module Demonstration.

Centralized package for User Guide interactive demo components.
All layouts, callbacks, and configurations are contained here.

Exports
-------
create_interactive_demo_section
    Main layout function for demo section
register_demo_callbacks
    Callback registration function

Author: BioRemPP Development Team
Date: 2025-12-05
"""

from .demo_callbacks import register_demo_callbacks
from .demo_layout import create_interactive_demo_section

__all__ = ["create_interactive_demo_section", "register_demo_callbacks"]
