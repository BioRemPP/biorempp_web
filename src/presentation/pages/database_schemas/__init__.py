"""
Database Schemas Pages Package.

Provides page creation functions for database schema documentation.
Uses YAML-driven rendering for easy maintenance.

Exports
-------
create_schemas_index_page
    Index page with all database schemas overview
create_biorempp_schema_page
    BioRemPP database schema documentation
create_hadeg_schema_page
    HADEG database schema documentation
create_kegg_schema_page
    KEGG degradation database schema documentation
create_toxcsm_schema_page
    ToxCSM database schema documentation
"""

from .schemas_page import (
    create_biorempp_schema_page,
    create_hadeg_schema_page,
    create_kegg_schema_page,
    create_schemas_index_page,
    create_toxcsm_schema_page,
)

__all__ = [
    "create_schemas_index_page",
    "create_biorempp_schema_page",
    "create_hadeg_schema_page",
    "create_kegg_schema_page",
    "create_toxcsm_schema_page",
]
