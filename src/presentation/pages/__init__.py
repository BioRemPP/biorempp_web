"""
Pages Package - BioRemPP v1.0.

Page layouts for the application.
"""

from .contact_page import create_contact_page
from .documentation import create_documentation_page
from .faq_page import create_faq_page
from .home_page import create_home_layout
from .home_page import get_layout as get_home_layout
from .methods_page import create_methods_page
from .regulatory_page import create_regulatory_page
from .results_page import get_results_layout
from .scientific_methods_page import create_scientific_methods_page
from .user_guide_page import create_user_guide_page

__all__ = [
    "create_home_layout",
    "get_home_layout",
    "get_results_layout",
    "create_faq_page",
    "create_regulatory_page",
    "create_contact_page",
    "create_user_guide_page",
    "create_methods_page",
    "create_scientific_methods_page",
    "create_documentation_page",
]
