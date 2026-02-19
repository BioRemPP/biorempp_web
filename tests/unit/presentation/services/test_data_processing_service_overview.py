"""Unit tests for dynamic database overview metadata generation."""

import pandas as pd
import pytest

from src.presentation.services.data_processing_service import DataProcessingService


@pytest.fixture
def mock_database_dir(tmp_path):
    """Create minimal databases for deterministic overview metric tests."""
    biorempp_df = pd.DataFrame(
        [
            {
                "ko": "K00001",
                "cpd": "C00001",
                "compoundname": "Compound A",
                "genesymbol": "GENEA",
                "referenceAG": "EPA",
                "compoundclass": "ClassA",
                "enzyme_activity": "ActA",
            },
            {
                "ko": "K00001",
                "cpd": "C00002",
                "compoundname": "Compound B",
                "genesymbol": "GENEB",
                "referenceAG": "ATSDR",
                "compoundclass": "ClassB",
                "enzyme_activity": "ActB",
            },
            {
                "ko": "K00002",
                "cpd": "C00003",
                "compoundname": "Compound C",
                "genesymbol": "GENEC",
                "referenceAG": "EPA",
                "compoundclass": "ClassA",
                "enzyme_activity": "ActC",
            },
        ]
    )
    biorempp_df.to_csv(tmp_path / "biorempp_db.csv", sep=";", index=False)

    hadeg_df = pd.DataFrame(
        [
            {
                "ko": "K00001",
                "Gene": "GeneA",
                "Pathway": "Pathway 1",
                "compound_pathway": "CategoryA",
            },
            {
                "ko": "K00001",
                "Gene": "GeneB",
                "Pathway": "Pathway 2",
                "compound_pathway": "CategoryB",
            },
            {
                "ko": "K00003",
                "Gene": "GeneC",
                "Pathway": "Pathway 3",
                "compound_pathway": "CategoryA",
            },
        ]
    )
    hadeg_df.to_csv(tmp_path / "hadeg_db.csv", sep=";", index=False)

    kegg_df = pd.DataFrame(
        [
            {"ko": "K00001", "pathname": "KPath 1", "genesymbol": "KG1"},
            {"ko": "K00002", "pathname": "KPath 2", "genesymbol": "KG2"},
            {"ko": "K00002", "pathname": "KPath 3", "genesymbol": "KG3"},
        ]
    )
    kegg_df.to_csv(tmp_path / "kegg_degradation_db.csv", sep=";", index=False)

    toxcsm_df = pd.DataFrame(
        [
            {
                "cpd": "C00001",
                "compoundname": "Compound A",
                "value_NR_AR": 0.1,
                "label_NR_AR": "Low",
                "value_SR_ARE": 0.2,
                "label_SR_ARE": "Low",
                "value_Gen_AMES_Mutagenesis": 0.3,
                "label_Gen_AMES_Mutagenesis": "Medium",
                "value_Env_Avian": 0.4,
                "label_Env_Avian": "High",
                "value_Org_Eye_Irritation": 0.5,
                "label_Org_Eye_Irritation": "High",
            },
            {
                "cpd": "C00002",
                "compoundname": "Compound B",
                "value_NR_AR": 0.1,
                "label_NR_AR": "Low",
                "value_SR_ARE": 0.2,
                "label_SR_ARE": "Low",
                "value_Gen_AMES_Mutagenesis": 0.3,
                "label_Gen_AMES_Mutagenesis": "Medium",
                "value_Env_Avian": 0.4,
                "label_Env_Avian": "High",
                "value_Org_Eye_Irritation": 0.5,
                "label_Org_Eye_Irritation": "High",
            },
            {
                "cpd": "C00003",
                "compoundname": "Compound C",
                "value_NR_AR": 0.1,
                "label_NR_AR": "Low",
                "value_SR_ARE": 0.2,
                "label_SR_ARE": "Low",
                "value_Gen_AMES_Mutagenesis": 0.3,
                "label_Gen_AMES_Mutagenesis": "Medium",
                "value_Env_Avian": 0.4,
                "label_Env_Avian": "High",
                "value_Org_Eye_Irritation": 0.5,
                "label_Org_Eye_Irritation": "High",
            },
            {
                "cpd": "C99999",
                "compoundname": "Compound X",
                "value_NR_AR": 0.1,
                "label_NR_AR": "Low",
                "value_SR_ARE": 0.2,
                "label_SR_ARE": "Low",
                "value_Gen_AMES_Mutagenesis": 0.3,
                "label_Gen_AMES_Mutagenesis": "Medium",
                "value_Env_Avian": 0.4,
                "label_Env_Avian": "High",
                "value_Org_Eye_Irritation": 0.5,
                "label_Org_Eye_Irritation": "High",
            },
        ]
    )
    toxcsm_df.to_csv(tmp_path / "toxcsm_db.csv", sep=";", index=False)

    return tmp_path


def test_process_upload_includes_database_overview(mock_database_dir):
    """Metadata should include database_overview with global+input values."""
    service = DataProcessingService(database_path=mock_database_dir)
    content = ">SampleA\nK00001\n>SampleB\nK00002\n"

    result = service.process_upload(content=content, filename="input.txt")
    aggregate = result["metadata"].get("database_aggregate_overview", {})
    overview = result["metadata"].get("database_overview", {})

    assert "biorempp" in overview
    assert "hadeg" in overview
    assert "toxcsm" in overview
    assert "kegg" in overview
    assert "per_database" in aggregate

    assert overview["biorempp"]["enzyme_compound_relations"]["input_value"] == 3
    assert overview["biorempp"]["enzyme_compound_relations"]["global_value"] == 3
    assert overview["hadeg"]["gene_pathway_relations"]["input_value"] == 2
    assert overview["hadeg"]["gene_pathway_relations"]["global_value"] == 3


def test_database_aggregate_overview_follows_hybrid_rules(mock_database_dir):
    """Aggregate overview should follow total/activation/coverage formulas."""
    service = DataProcessingService(database_path=mock_database_dir)
    content = ">SampleA\nK00001\n>SampleB\nK00002\n"

    result = service.process_upload(content=content, filename="input.txt")
    aggregate = result["metadata"]["database_aggregate_overview"]

    assert aggregate["total_relations_input"] == 11
    assert aggregate["active_databases"] == 4
    assert aggregate["total_databases"] == 4
    assert aggregate["matched_kos"] == 2
    assert aggregate["total_kos"] == 2
    assert aggregate["ko_match_rate_pct"] == 100.0

    per_database = aggregate["per_database"]
    assert per_database["biorempp"]["input_relations"] == 3
    assert per_database["hadeg"]["input_relations"] == 2
    assert per_database["toxcsm"]["input_relations"] == 3
    assert per_database["kegg"]["input_relations"] == 3

    assert per_database["biorempp"]["share_pct"] == 27.27
    assert per_database["hadeg"]["share_pct"] == 18.18
    assert per_database["toxcsm"]["share_pct"] == 27.27
    assert per_database["kegg"]["share_pct"] == 27.27


def test_toxcsm_endpoints_and_categories_follow_value_prefix_rules(mock_database_dir):
    """ToxCSM overview must count endpoints and categories from `value_*` columns."""
    service = DataProcessingService(database_path=mock_database_dir)
    content = ">SampleA\nK00001\n>SampleB\nK00002\n"

    result = service.process_upload(content=content, filename="input.txt")
    toxcsm_stats = result["metadata"]["database_overview"]["toxcsm"]

    assert toxcsm_stats["environmental_compounds"]["input_value"] == 3
    assert toxcsm_stats["environmental_compounds"]["global_value"] == 4
    assert toxcsm_stats["toxicity_endpoints"]["input_value"] == 5
    assert toxcsm_stats["toxicity_endpoints"]["global_value"] == 5
    assert toxcsm_stats["toxicity_categories"]["input_value"] == 5
    assert toxcsm_stats["toxicity_categories"]["global_value"] == 5
