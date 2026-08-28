import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

TREATMENTS = [
    {
        "code": "PL1",
        "petroleum_type": "leve",
        "source_id": 1,
        "source_origin": "nosso",
        "description": "Petroleo leve do grupo/projeto.",
    },
    {
        "code": "PL2",
        "petroleum_type": "leve",
        "source_id": 2,
        "source_origin": "patricia",
        "description": "Petroleo leve obtido pela Patricia.",
    },
    {
        "code": "PP1",
        "petroleum_type": "pesado",
        "source_id": 1,
        "source_origin": "nosso",
        "description": "Petroleo pesado do grupo/projeto.",
    },
    {
        "code": "PP2",
        "petroleum_type": "pesado",
        "source_id": 2,
        "source_origin": "patricia",
        "description": "Petroleo pesado obtido pela Patricia.",
    },
]

ROWS = [
    ("AP1BH01-1", "Ochrobactrum", [62.18, 75.40, 52.60], [81.06, 84.60, 88.86], [76.56, 37.67, 62.30], [33.11, 48.71, 53.88]),
    ("BD1", "Micococcus luteus", [80.73, 85.39, 55.60], [88.17, 90.97, 72.20], [81.30, 87.97, 68.73], [83.78, 86.25, 63.71]),
    ("BD2", "Staphylococcus", [25.90, 26.98, 28.57], [4.75, 41.35, 42.33], [15.66, 8.19, 12.12], [None, None, None]),
    ("BD5", "Dermacoccus nishinomiyaensis", [62.31, 55.52, 58.55], [74.39, 78.72, 73.14], [33.94, 39.13, 60.51], [57.69, 47.37, 44.98]),
    ("BD8", "Rothia", [67.62, 71.17, 72.23], [80.62, 73.95, 81.74], [71.58, 75.11, 69.56], [55.07, 60.31, 57.77]),
    ("BD9", "Bacillus amyloliquefaciens", [66.87, 46.21, 38.03], [76.02, 66.67, 76.00], [13.94, None, 75.36], [60.26, 44.30, 51.09]),
    ("BD48", "Bacillus safensis", [25.54, 58.27, 52.51], [54.11, 59.29, 49.69], [49.40, 49.14, 50.65], [16.11, 18.89, 16.04]),
    ("BD50", "Bacillus safensis", [71.12, 70.34, 70.51], [81.74, 82.82, 81.43], [64.85, 67.93, 79.35], [75.64, 60.53, 75.55]),
    ("BD54", "Acinetobacter", [76.42, 77.82, 78.33], [87.08, 85.36, 88.34], [83.40, 75.34, 80.80], [63.85, 53.35, 61.41]),
    ("BD61", "Ochrobactrum", [75.13, 74.19, 81.04], [87.08, 86.12, 86.01], [71.58, 75.11, 69.56], [12.16, 75.52, 53.88]),
    ("BD67", "Ochrobactrum", [60.49, 62.41, 29.06], [31.61, 80.00, 75.43], [36.97, None, None], [50.00, 37.72, 37.55]),
    ("BD69", "Citrobacter", [67.48, 74.14, 67.09], [80.65, 81.03, 68.86], [None, 57.61, 70.29], [58.55, 16.67, 44.10]),
    ("BD72", "Bacillus tropicus", [69.60, 65.52, 59.40], [83.11, 77.95, 82.29], [40.00, 55.43, 68.84], [68.38, 57.02, 62.45]),
    ("BD73", "Bacillus tropicus", [73.56, 68.62, 72.65], [78.47, 83.85, 82.29], [38.79, 63.04, 46.74], [67.09, 50.88, 55.46]),
    ("BD77", "Stutzerimonas balearica", [63.53, 65.52, 56.41], [61.58, 77.18, 76.00], [45.45, 54.35, None], [58.97, 45.61, 44.98]),
    ("BD78", "Bacillus", [46.76, 67.63, 68.34], [76.27, 76.92, 67.79], [64.26, 62.07, 35.50], [38.89, 42.78, 39.57]),
    ("BD81", "Bacillus", [73.25, 69.31, 58.12], [67.30, 77.18, 76.29], [None, 60.33, 74.64], [26.07, 25.88, 72.05]),
    ("BD83", "Bacillus", [41.73, 32.01, 49.81], [59.18, 57.37, 54.91], [4.82, 44.40, 46.32], [13.89, 18.33, None]),
    ("BD95", "Stutzerimonas frequens", [None, 11.87, 35.91], [51.58, 50.00, 46.93], [None, 45.26, None], [None, None, None]),
    ("BD96", "Stutzerimonas frequens", [5.04, 42.09, 43.63], [53.48, 50.00, 52.15], [52.21, 25.86, None], [None, None, None]),
    ("BD101", "Stutzerimonas balearica", [58.97, 47.59, 41.88], [80.38, 59.23, 61.14], [10.33, 46.38, None], [53.85, 46.05, 52.84]),
    ("BD105", "Stutzerimonas frequens", [73.32, 79.23, 78.10], [88.55, 83.27, 89.77], [79.25, 65.75, 74.24], [57.09, 65.21, 65.53]),
    ("BD106", "Stutzerimonas frequens", [39.21, 25.87, None], [55.38, 54.81, 56.13], [4.82, 44.40, 46.32], [10.00, 4.28, None]),
    ("BD107", "Stutzerimonas balearica", [76.94, 84.07, 80.36], [88.11, 77.00, 89.51], [80.08, 69.63, 61.12], [76.29, 79.61, None]),
    ("BD108", "Stutzerimonas balearica", [44.24, 56.83, 51.35], [69.30, 71.15, 70.25], [4.82, 44.40, 46.32], [39.44, 28.89, 37.97]),
    ("BD117", "Micococcus luteus", [79.58, 87.68, 66.02], [80.53, 88.68, 72.59], [79.20, 84.38, 60.23], [83.40, 85.53, 67.18]),
    ("BD120", "Bacillus subtilis", [82.12, 85.48, 78.78], [86.05, 80.99, 90.41], [86.51, 85.62, 85.01], [74.66, 76.29, 82.77]),
    ("BD121", "Bacillus paralicheniformis", [41.37, 46.04, 39.77], [60.44, 58.65, 60.43], [57.43, 47.41, 40.26], [20.00, None, 16.04]),
    ("BD126", "Bacillus", [64.03, 60.07, 47.49], [63.61, 64.10, 62.27], [65.06, 62.93, 63.20], [8.33, 28.89, 5.88]),
    ("BD127", "Achromobacter", [29.50, 53.96, 65.64], [71.84, 70.19, 64.11], [30.92, 12.50, 41.56], [4.44, None, 27.81]),
    ("BD129", "Bacillus paralicheniformis", [76.26, 70.14, 62.16], [74.37, 73.72, 68.40], [59.44, 59.44, None], [45.00, None, None]),
    ("BD130", "Bacillus licheniformis", [57.91, 60.43, 61.00], [70.25, 69.55, 68.71], [67.07, 65.52, 63.20], [23.89, None, 37.43]),
    ("BD132", "Bacillus safensis", [78.76, 80.44, 79.23], [84.29, 81.56, 90.03], [85.48, 85.62, 83.61], [76.69, 76.03, 82.52]),
    ("BD137", "Brevibacillus brevis", [70.50, 73.38, 69.50], [80.38, 77.88, 78.83], [63.86, 73.28, 67.97], [26.67, 37.22, 33.69]),
    ("BD139", "Brevibacillus brevis", [43.17, 62.95, 62.93], [69.62, 56.73, 23.01], [63.86, 71.98, 94.59], [22.22, 48.33, 39.04]),
    ("BD140", "Brevibacillus brevis", [65.08, 70.34, 28.57], [67.31, 77.69, 46.47], [52.19, 30.39, None], [85.71, 8.82, None]),
    ("BD141", "Brevibacillus brevis", [61.87, 60.43, 56.37], [57.59, 58.65, 59.82], [28.51, 12.50, 41.56], [43.33, 33.89, 28.88]),
    ("BD143", "Bacillus stratosphericus", [80.53, 70.06, 14.67], [62.54, 84.30, 66.78], [74.36, 62.54, 4.44], [91.77, 86.16, 63.70]),
    ("BD145", "Tistrella", [64.12, 56.02, 6.18], [57.07, 74.52, 67.13], [61.20, 8.48, 25.78], [90.69, 85.04, 64.23]),
    ("BD147", "Cellulomonas", [57.25, 84.96, 50.19], [77.21, 82.78, 76.59], [73.90, 53.71, 36.89], [82.65, 77.01, 54.09]),
    ("BD149", "Bacillus stratosphericus", [79.96, 87.82, 61.00], [83.75, 85.81, 89.85], [69.98, 38.16, 54.67], [94.39, 90.74, 86.48]),
    ("BD151", "Bacillus", [80.15, 86.25, 63.71], [85.88, 85.53, 69.11], [75.95, 84.96, 61.78], [78.05, 78.65, 23.17]),
    ("BD152", "Bacillus", [82.25, 85.96, 64.48], [85.88, 85.53, 69.11], [75.95, 84.96, 61.78], [78.05, 78.65, 23.17]),
    ("BD158", "Salinicola", [58.21, 79.80, 16.99], [84.63, 87.05, 74.87], [0.133, 66.74, 49.82], [86.03, 78.57, 69.93]),
    ("BD160", "Bacillus stratosphericus", [82.06, 87.11, 64.86], [80.74, 73.42, 85.89], [79.45, 61.13, 49.33], [94.07, 88.06, 81.49]),
    ("BD161", "Rossellomorea", [12.98, 28.94, None], [32.16, 65.15, 35.80], [26.10, 28.98, None], [59.95, 61.72, 81.14]),
    ("BD162", "Bacillus safensis", [60.66, 37.47, 66.22], [66.22, 78.25, 72.14], [76.81, 71.62, 69.16], [69.16, 78.35, 81.84]),
    ("BD163", "Bacillus megaterium", [61.45, 61.46, None], [59.19, 76.03, 64.72], [64.43, 53.71, 33.33], [86.73, 80.47, 61.92]),
    ("BD165", "Bacillus paralicheniformis", [67.37, 65.47, 37.84], [34.92, 71.63, 27.03], [77.48, 83.95, 61.00], [80.73, 76.22, 15.44]),
    ("BD166", "Bacillus megaterium", [45.42, 51.43, 32.05], [82.25, 77.36, 74.13], [80.15, 80.37, 60.23], [86.07, 84.96, 57.30]),
    ("E7", "Acinetobacter", [76.17, 86.09, 76.98], [84.58, 83.46, 90.16], [57.25, 68.02, 80.19], [75.52, 29.91, 29.74]),
    ("BG1", "Bacillus amyloliquefaciens", [70.47, 70.97, 67.27], [85.32, 83.27, 88.08], [71.78, 84.70, 83.61], [69.26, 69.85, 73.30]),
    ("CB13", "Enterobacter", [75.91, 72.18, 69.30], [85.61, 72.81, 83.68], [60.79, 56.39, 58.08], [44.59, 45.88, 70.87]),
]


def source_label(isolate_code, taxon):
    return f"{isolate_code} - {taxon}"


def experiment_metadata():
    return {
        "name": "validacao_dcpip_petroleos_isolados",
        "assay": "DCPIP",
        "metric_name": "percentual",
        "unit": "%",
        "source_note": "O petroleo leve e pesado 1 e o nosso, o 2 foi o que Patricia conseguiu.",
        "missing_value_policy": "Celulas marcadas com '-' na tabela original foram registradas como null.",
        "decimal_policy": "Valores com virgula decimal foram convertidos para ponto decimal numerico em JSON.",
    }


def build_normalized():
    measurements = []
    for isolate_code, taxon, *treatment_values in ROWS:
        for treatment, values in zip(TREATMENTS, treatment_values):
            for replicate, value in enumerate(values, start=1):
                measurements.append(
                    {
                        "isolate_code": isolate_code,
                        "taxon": taxon,
                        "source_label": source_label(isolate_code, taxon),
                        "treatment": treatment["code"],
                        "replicate": replicate,
                        "value": value,
                    }
                )

    return {
        "schema_version": "1.0",
        "document_type": "dcpip_measurements_normalized",
        "experiment": experiment_metadata(),
        "treatments": TREATMENTS,
        "measurements": measurements,
    }


def build_grouped():
    isolates = []
    for isolate_code, taxon, *treatment_values in ROWS:
        measurements = {
            treatment["code"]: values
            for treatment, values in zip(TREATMENTS, treatment_values)
        }
        isolates.append(
            {
                "isolate_code": isolate_code,
                "taxon": taxon,
                "source_label": source_label(isolate_code, taxon),
                "measurements": measurements,
            }
        )

    return {
        "schema_version": "1.0",
        "document_type": "dcpip_measurements_by_isolate",
        "experiment": experiment_metadata(),
        "treatments": TREATMENTS,
        "isolates": isolates,
    }


def validate(normalized, grouped):
    expected_measurements = len(ROWS) * len(TREATMENTS) * 3
    if len(normalized["measurements"]) != expected_measurements:
        raise ValueError("Unexpected normalized measurement count")

    if len(grouped["isolates"]) != len(ROWS):
        raise ValueError("Unexpected isolate count")

    for isolate in grouped["isolates"]:
        if set(isolate["measurements"]) != {treatment["code"] for treatment in TREATMENTS}:
            raise ValueError(f"Unexpected treatments for {isolate['isolate_code']}")
        for values in isolate["measurements"].values():
            if len(values) != 3:
                raise ValueError(f"Unexpected replicate count for {isolate['isolate_code']}")


def write_json(path, payload):
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main():
    normalized = build_normalized()
    grouped = build_grouped()
    validate(normalized, grouped)
    write_json(BASE_DIR / "dcpips_measurements_normalized.json", normalized)
    write_json(BASE_DIR / "dcpips_measurements_by_isolate.json", grouped)


if __name__ == "__main__":
    main()
