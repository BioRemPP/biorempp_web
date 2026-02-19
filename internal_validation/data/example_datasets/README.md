# Example KO Annotation Datasets

This directory contains example KO annotation datasets for internal validation testing.

## Purpose

These datasets are used by:

- **Script 05 (Example Roundtrip Regression)**: Demonstrates deterministic mapping behavior
- **Script 06 (Use Case Invariants)**: Validates logical invariants on merged outputs

## File Format

- **Format**: Tab-separated values (TSV)
- **Encoding**: UTF-8
- **Required columns**:
  - `Sample`: Sample identifier (non-empty string)
  - `KO`: KEGG Orthology identifier (format: `K\d{5}`)

## Example Files

### Example_A.txt

- **Samples**: 3 (Sample_A1, Sample_A2, Sample_A3)
- **Unique KOs**: 8
- **Total annotations**: 10
- **Description**: Small dataset with basic KO identifiers present in BioRemPP

### Example_B.txt

- **Samples**: 3 (Sample_B1, Sample_B2, Sample_B3)
- **Unique KOs**: 10
- **Total annotations**: 12
- **Description**: Medium dataset with diverse KO identifiers

### Example_C.txt

- **Samples**: 4 (Sample_C1, Sample_C2, Sample_C3, Sample_C4)
- **Unique KOs**: 11
- **Total annotations**: 13
- **Description**: Larger dataset with some KOs not present in databases (for testing absence handling)

## Expected Behavior

- **BioRemPP matches**: Subset of KOs will match (K00001-K00010 are expected to match)
- **KEGG matches**: Some KOs may match KEGG degradation pathways
- **HADEG matches**: Fewer matches expected (specialized hydrocarbon degradation)
- **ToxCSM matches**: Compounds from matched KOs may have toxicity predictions

## Coverage Testing

- **K00001-K00010**: Likely to match BioRemPP (alcohol dehydrogenases, glycerol metabolism)
- **K00100+**: May or may not match (testing absence handling)
- **K00200+**: May or may not match (testing absence handling)
- **K00300+**: May or may not match (testing absence handling)
- **K00400+**: May or may not match (testing absence handling)

## Usage

These datasets are automatically discovered and processed by validation scripts:

```bash
python internal_validation/scripts/run_all_gx.py --checkpoint biorempp_full_validation
```

Or run the full suite:

```bash
python internal_validation/scripts/run_all_gx.py --checkpoint biorempp_full_validation
```

## Reproducibility

- **Input checksums**: SHA256 checksums are computed for each file
- **Output checksums**: Merged outputs are checksummed for regression testing
- **Version control**: These files should be committed to Git for reproducibility

## Creating Custom Examples

To create custom example datasets:

1. Create a `.txt` file in this directory
2. Use tab-separated format with `Sample` and `KO` columns
3. Include realistic KO identifiers (format: `K\d{5}`)
4. Run validation scripts to generate outputs

Example format:

```
>Sample1
K00031
K00032
K00090
K00042
K00052
```

## Notes

- These are **example datasets only** and do not represent real-world data
- KO identifiers are selected from KEGG database for testing purposes
- Some KOs may not match any databases (expected behavior for testing)
- Validation scripts handle missing matches gracefully (left join behavior)
