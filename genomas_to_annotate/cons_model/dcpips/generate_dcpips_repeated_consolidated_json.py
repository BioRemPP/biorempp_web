import json
from collections import Counter
from pathlib import Path

from generate_dcpips_json import TREATMENTS


BASE_DIR = Path(__file__).resolve().parent

ROWS = [
    ("BG1", "Bacillus amyloliquefaciens", [70.47, 70.97, 67.27], [85.32, 83.27, 88.08], [71.78, 84.70, 83.61], [69.26, 69.85, 73.30]),
    ("BD5", "Dermacoccus nishinomiyaensis", [70.47, 80.44, 80.14], [83.26, 76.62, 83.42], [79.67, 75.57, 75.41], [63.85, 61.86, 76.46]),
    ("E7", "Acinetobacter", [76.17, 86.09, 76.98], [84.58, 83.46, 90.16], [75.52, 29.91, 29.74], [28.38, 71.39, 67.72]),
    ("BD8", "Rothia", [67.62, 71.17, 72.23], [80.62, 73.95, 81.74], [71.58, 75.11, 69.56], [55.07, 60.31, 57.77]),
    ("CB13", "Enterobacter", [75.91, 72.18, 69.30], [85.61, 72.81, 83.68], [60.79, 56.39, 58.08], [44.59, 45.88, 70.87]),
    ("AP1BH01-1", "Ochrobactrum", [62.18, 75.40, 52.60], [81.06, 84.60, 88.86], [76.56, 37.67, 62.30], [33.11, 48.71, 53.88]),
    ("BD61", "Ochrobactrum", [75.13, 74.19, 81.04], [87.08, 86.12, 86.01], [71.58, 75.11, 69.56], [12.16, 75.52, 53.88]),
    ("BD54", "Acinetobacter", [76.42, 77.82, 78.33], [87.08, 85.36, 88.34], [83.40, 75.34, 80.80], [63.85, 53.35, 61.41]),
    ("BD132", "Bacillus safensis", [78.76, 80.44, 79.23], [84.29, 81.56, 90.03], [85.48, 85.62, 83.61], [76.69, 76.03, 82.52]),
    ("BD72", "Bacillus tropicus", [73.58, 79.03, 97.70], [89.57, 88.21, 84.33], [82.16, 79.22, 77.05], [69.26, 82.22, 81.31]),
    ("BD120", "Bacillus subtilis", [82.12, 85.48, 78.78], [86.05, 80.99, 90.41], [86.51, 85.62, 85.01], [74.66, 76.29, 82.77]),
    ("BD105", "Stutzerimonas frequens", [73.32, 79.23, 78.10], [88.55, 83.27, 89.77], [79.25, 65.75, 74.24], [57.09, 65.21, 65.53]),
    ("BD107", "Stutzerimonas balearica", [76.94, 84.07, 80.36], [88.11, 77.00, 89.51], [80.08, 69.63, 61.12], [-12.16, 76.29, 79.61]),
    ("BD165", "Bacillus paralicheniformis", [67.37, 65.47, 37.84], [34.92, 71.63, 27.03], [77.48, 83.95, 61.00], [80.73, 76.22, 15.44]),
    ("BD147", "Cellulomonas", [79.58, 87.97, 61.00], [87.98, 90.97, 76.45], [80.73, 81.38, 54.83], [86.45, 83.81, 56.76]),
    ("BD107", "Stutzerimonas balearica", [77.86, 85.67, 50.97], [76.53, 91.26, 33.98], [78.82, 84.81, 64.86], [72.14, 82.66, 61.39]),
    ("BD151", "Bacillus", [80.15, 86.25, 63.71], [85.88, 85.53, 69.11], [75.95, 84.96, 61.78], [78.05, 78.65, 23.17]),
    ("BD158", "Salinicola", [66.03, 81.23, 55.60], [69.27, 73.21, 29.73], [84.35, 88.11, 69.88], [78.05, 81.95, 55.60]),
    ("BD152", "Bacillus", [82.25, 85.96, 64.48], [86.83, 99.11, 75.68], [82.82, 84.81, 69.88], [79.96, 81.81, 53.67]),
    ("BD137", "Brevibacillus brevis", [73.47, 78.94, 66.80], [84.54, 88.40, 73.36], [87.02, 90.11, 61.78], [70.42, 69.91, 43.24]),
    ("BD166", "Bacillus megaterium", [45.42, 51.43, 32.05], [82.25, 77.36, 74.13], [80.15, 80.37, 60.23], [86.07, 84.96, 57.30]),
    ("BD139", "Brevibacillus brevis", [76.34, 83.52, 55.98], [84.16, 84.81, 70.27], [78.63, 86.25, 63.32], [85.50, 87.82, 50.58]),
    ("BD117", "Micococcus luteus", [79.58, 87.68, 66.02], [80.53, 88.68, 72.59], [79.20, 84.38, 60.23], [83.40, 85.53, 67.18]),
    ("BD1", "Micococcus luteus", [80.73, 85.39, 55.60], [88.17, 90.97, 72.20], [81.30, 87.97, 68.73], [83.78, 86.25, 63.71]),
]


def experiment_metadata():
    return {
        "name": "validacao_dcpip_petroleos_isolados_repetido_consolidado",
        "assay": "DCPIP",
        "experiment_date": "2025-04-17",
        "metric_name": "percentual",
        "unit": "%",
        "source_label": "DCPIP REPETINDO PRINCIPAIS ISOLADOS - 17/04/25",
        "source_note": "Tabela de repeticao dos principais isolados com resultados consolidados para alguns valores anteriormente faltantes.",
        "missing_value_policy": "Celulas marcadas com '-' na tabela original devem ser registradas como null.",
        "decimal_policy": "Valores com virgula decimal foram convertidos para ponto decimal numerico em JSON.",
        "duplicate_isolate_policy": "Linhas repetidas para o mesmo isolate_code foram preservadas como registros separados por record_id.",
    }


def source_label(isolate_code, taxon):
    return f"{isolate_code} - {taxon}"


def row_records():
    seen = Counter()
    records = []
    for table_row_index, row in enumerate(ROWS, start=1):
        isolate_code, taxon, *treatment_values = row
        seen[isolate_code] += 1
        repeat_index = seen[isolate_code]
        duplicate_suffix = f"_{repeat_index}" if repeat_index > 1 else ""
        records.append(
            {
                "record_id": f"{isolate_code}{duplicate_suffix}",
                "table_row_index": table_row_index,
                "repeat_record_index_for_isolate": repeat_index,
                "isolate_code": isolate_code,
                "taxon": taxon,
                "source_label": source_label(isolate_code, taxon),
                "measurements": {
                    treatment["code"]: values
                    for treatment, values in zip(TREATMENTS, treatment_values)
                },
            }
        )
    return records


def build_grouped():
    return {
        "schema_version": "1.0",
        "document_type": "dcpip_repeated_consolidated_measurements_by_record",
        "experiment": experiment_metadata(),
        "treatments": TREATMENTS,
        "records": row_records(),
    }


def build_normalized(grouped):
    measurements = []
    for record in grouped["records"]:
        for treatment, values in record["measurements"].items():
            for replicate, value in enumerate(values, start=1):
                measurements.append(
                    {
                        "record_id": record["record_id"],
                        "table_row_index": record["table_row_index"],
                        "repeat_record_index_for_isolate": record["repeat_record_index_for_isolate"],
                        "isolate_code": record["isolate_code"],
                        "taxon": record["taxon"],
                        "source_label": record["source_label"],
                        "treatment": treatment,
                        "replicate": replicate,
                        "value": value,
                    }
                )
    return {
        "schema_version": "1.0",
        "document_type": "dcpip_repeated_consolidated_measurements_normalized",
        "experiment": experiment_metadata(),
        "treatments": TREATMENTS,
        "measurements": measurements,
    }


def validate(normalized, grouped):
    expected_measurements = len(ROWS) * len(TREATMENTS) * 3
    if len(grouped["records"]) != len(ROWS):
        raise ValueError("Unexpected grouped record count")
    if len(normalized["measurements"]) != expected_measurements:
        raise ValueError("Unexpected normalized measurement count")

    for record in grouped["records"]:
        if set(record["measurements"]) != {treatment["code"] for treatment in TREATMENTS}:
            raise ValueError(f"Unexpected treatments for {record['record_id']}")
        for values in record["measurements"].values():
            if len(values) != 3:
                raise ValueError(f"Unexpected replicate count for {record['record_id']}")


def write_json(path, payload):
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main():
    grouped = build_grouped()
    normalized = build_normalized(grouped)
    validate(normalized, grouped)
    write_json(BASE_DIR / "dcpips_repeated_consolidated_measurements_normalized.json", normalized)
    write_json(BASE_DIR / "dcpips_repeated_consolidated_measurements_by_record.json", grouped)


if __name__ == "__main__":
    main()
