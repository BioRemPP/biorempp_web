"""
Analysis Suggestions Package - BioRemPP v1.0
============================================

Interactive analytical suggestions for guiding users through result exploration.

Exports
-------
create_suggestions_offcanvas
    Main offcanvas component
create_suggestions_trigger_button
    Button to toggle offcanvas
register_suggestions_callbacks
    Register all callbacks

Author: BioRemPP Development Team
Date: 2025-12-05
"""

from .basic_exploration import create_basic_exploration_content
from .callbacks import register_suggestions_callbacks
from .current_trends import create_current_trends_content
from .data_type_exploration import create_data_type_exploration_content
from .guiding_questions import create_guiding_questions_content
from .offcanvas_component import (
    create_suggestions_offcanvas,
    create_suggestions_trigger_button,
)
from .practical_applications import create_practical_applications_content

__all__ = [
    "create_suggestions_offcanvas",
    "create_suggestions_trigger_button",
    "create_guiding_questions_content",
    "create_basic_exploration_content",
    "create_data_type_exploration_content",
    "create_practical_applications_content",
    "create_current_trends_content",
    "register_suggestions_callbacks",
]
