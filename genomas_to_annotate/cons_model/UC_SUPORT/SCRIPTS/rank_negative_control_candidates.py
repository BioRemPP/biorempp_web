from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean


SCRIPT_PATH = Path(__file__).resolve()
CONS_MODEL_DIR = SCRIPT_PATH.parents[2]
RESULTS_DIR = CONS_MODEL_DIR / "UC_SUPORT" / "RESULTS"
BIOREMPP_CSV = CONS_MODEL_DIR / "TABLE_RESULTS" / "BioRemPP_Results (9).csv"
ISOLATE_METRICS_CSV = CONS_MODEL_DIR / "CONSORTIA_MODEL_RESULTS" / "isolate_consolidated_metrics.csv"

STRICT_CONSORTIA = {
    "Aliphatic": {"BD163", "BD127", "E7", "BD117"},
    "Polyaromatic": {"BD61", "BD120", "BD158", "BD117"},
}

TARGET_CLASSES = {
    "Aliphatic": "PL_mean",
    "Aromatic": "PP_mean",
}


def parse_float(value: str) -> float | None:
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def average_ranks(values: list[float], ascending: bool = True) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1], reverse=not ascending)
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i + 1
        while j < len(indexed) and indexed[j][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + 1 + j) / 2.0
        for k in range(i, j):
            ranks[indexed[k][0]] = avg_rank
        i = j
    return ranks


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    x_bar = mean(xs)
    y_bar = mean(ys)
    numerator = sum((x - x_bar) * (y - y_bar) for x, y in zip(xs, ys))
    x_den = math.sqrt(sum((x - x_bar) ** 2 for x in xs))
    y_den = math.sqrt(sum((y - y_bar) ** 2 for y in ys))
    if x_den == 0 or y_den == 0:
        return None
    return numerator / (x_den * y_den)


def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 3 or len(xs) != len(ys):
        return None
    return pearson(average_ranks(xs), average_ranks(ys))


def fmt(value: float | None, digits: int = 3) -> str:
    if value is None:
        return ""
    return f"{value:.{digits}f}"


def load_biorempp_counts() -> tuple[set[str], dict[str, dict[str, dict[str, set[str] | int]]]]:
    samples: set[str] = set()
    counts: dict[str, dict[str, dict[str, set[str] | int]]] = defaultdict(
        lambda: defaultdict(lambda: {"genes": set(), "kos": set(), "compounds": set(), "rows": 0})
    )
    with BIOREMPP_CSV.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            sample = row["Sample"].strip()
            compound_class = row["compoundclass"].strip()
            samples.add(sample)
            entry = counts[sample][compound_class]
            entry["rows"] = int(entry["rows"]) + 1
            if row.get("genesymbol", "").strip():
                entry["genes"].add(row["genesymbol"].strip())
            if row.get("ko", "").strip():
                entry["kos"].add(row["ko"].strip())
            if row.get("compoundname", "").strip():
                entry["compounds"].add(row["compoundname"].strip())
    return samples, counts


def load_isolate_metrics() -> dict[str, dict[str, str]]:
    with ISOLATE_METRICS_CSV.open(newline="", encoding="utf-8-sig") as handle:
        return {row["sample"].strip(): row for row in csv.DictReader(handle)}


def add_rank_fields(rows: list[dict[str, object]], primary_metric: str) -> list[dict[str, object]]:
    gene_values = [float(row["unique_gene_count"]) for row in rows]
    primary_values = [float(row[primary_metric]) for row in rows]
    gene_ranks = average_ranks(gene_values, ascending=True)
    dcpip_ranks = average_ranks(primary_values, ascending=True)
    for row, gene_rank, dcpip_rank in zip(rows, gene_ranks, dcpip_ranks):
        row["low_gene_rank"] = gene_rank
        row["low_dcpip_rank"] = dcpip_rank
        row["negative_control_score"] = (gene_rank + dcpip_rank) / 2.0
    return sorted(rows, key=lambda row: (row["negative_control_score"], row["unique_gene_count"], row[primary_metric]))


def build_rows() -> tuple[dict[str, list[dict[str, object]]], list[dict[str, object]]]:
    samples, biorempp_counts = load_biorempp_counts()
    metrics = load_isolate_metrics()
    by_class: dict[str, list[dict[str, object]]] = {}

    for target_class, primary_metric in TARGET_CLASSES.items():
        rows: list[dict[str, object]] = []
        for sample in sorted(samples):
            sample_counts = biorempp_counts[sample][target_class]
            metric = metrics.get(sample, {})
            row = {
                "sample": sample,
                "taxon": metric.get("taxon", ""),
                "target_class": target_class,
                "primary_dcpip_metric": primary_metric,
                "unique_gene_count": len(sample_counts["genes"]),
                "unique_ko_count": len(sample_counts["kos"]),
                "unique_compound_count": len(sample_counts["compounds"]),
                "evidence_rows": sample_counts["rows"],
                "PL_mean": parse_float(metric.get("PL_mean", "")),
                "PP_mean": parse_float(metric.get("PP_mean", "")),
                "overall_mean": parse_float(metric.get("overall_mean", "")),
                "metal_authority": metric.get("metal_authority", ""),
                "in_aliphatic_strict": sample in STRICT_CONSORTIA["Aliphatic"],
                "in_polyaromatic_strict": sample in STRICT_CONSORTIA["Polyaromatic"],
            }
            if row["PL_mean"] is None or row["PP_mean"] is None or row["overall_mean"] is None:
                continue
            rows.append(row)
        by_class[target_class] = add_rank_fields(rows, primary_metric)

    combined: list[dict[str, object]] = []
    by_sample = {sample: {} for sample in samples}
    for target_class, rows in by_class.items():
        for row in rows:
            by_sample[row["sample"]][target_class] = row

    for sample, class_rows in sorted(by_sample.items()):
        if "Aliphatic" not in class_rows or "Aromatic" not in class_rows:
            continue
        ali = class_rows["Aliphatic"]
        aro = class_rows["Aromatic"]
        combined.append(
            {
                "sample": sample,
                "taxon": ali["taxon"],
                "aliphatic_gene_count": ali["unique_gene_count"],
                "aromatic_gene_count": aro["unique_gene_count"],
                "aliphatic_low_gene_rank": ali["low_gene_rank"],
                "aromatic_low_gene_rank": aro["low_gene_rank"],
                "PL_mean": ali["PL_mean"],
                "PP_mean": ali["PP_mean"],
                "overall_mean": ali["overall_mean"],
                "combined_negative_control_score": mean(
                    [
                        float(ali["low_gene_rank"]),
                        float(aro["low_gene_rank"]),
                        float(average_ranks([float(r["PL_mean"]) for r in by_class["Aliphatic"]], ascending=True)[
                            [r["sample"] for r in by_class["Aliphatic"]].index(sample)
                        ]),
                        float(average_ranks([float(r["PP_mean"]) for r in by_class["Aromatic"]], ascending=True)[
                            [r["sample"] for r in by_class["Aromatic"]].index(sample)
                        ]),
                    ]
                ),
                "metal_authority": ali["metal_authority"],
                "in_any_strict_consortium": bool(ali["in_aliphatic_strict"] or ali["in_polyaromatic_strict"]),
            }
        )
    combined.sort(key=lambda row: row["combined_negative_control_score"])
    return by_class, combined


def correlation_rows(by_class: dict[str, list[dict[str, object]]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target_class, ranked_rows in by_class.items():
        genes = [float(row["unique_gene_count"]) for row in ranked_rows]
        for metric in ["PL_mean", "PP_mean", "overall_mean"]:
            values = [float(row[metric]) for row in ranked_rows]
            rows.append(
                {
                    "target_class": target_class,
                    "gene_count_metric": "unique_gene_count",
                    "dcpip_metric": metric,
                    "n_samples": len(values),
                    "pearson_r": pearson(genes, values),
                    "spearman_r": spearman(genes, values),
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def markdown_table(rows: list[dict[str, object]], fields: list[str], limit: int = 12) -> str:
    labels = fields
    lines = [
        "| " + " | ".join(labels) + " |",
        "| " + " | ".join("---" for _ in labels) + " |",
    ]
    for row in rows[:limit]:
        values = []
        for field in fields:
            value = row[field]
            if isinstance(value, float):
                if "rank" in field or "score" in field:
                    values.append(f"{value:.2f}")
                else:
                    values.append(f"{value:.2f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def build_report(
    by_class: dict[str, list[dict[str, object]]],
    combined: list[dict[str, object]],
    correlations: list[dict[str, object]],
) -> str:
    top_aliphatic = by_class["Aliphatic"][:12]
    top_aromatic = by_class["Aromatic"][:12]
    top_combined = combined[:12]
    aliphatic_strict_rows = [
        row for row in by_class["Aliphatic"] if row["sample"] in STRICT_CONSORTIA["Aliphatic"]
    ]
    aromatic_positive_rows = [
        row for row in by_class["Aromatic"] if row["sample"] in STRICT_CONSORTIA["Polyaromatic"]
    ]
    bd2 = next((row for row in combined if row["sample"] == "BD2"), None)
    bd147 = next((row for row in combined if row["sample"] == "BD147"), None)

    comparison_rows = []
    if bd2:
        comparison_rows.append(
            {
                "grupo": "Controle negativo prioritario",
                "amostras": "BD2",
                "aliphatic_genes_mean": bd2["aliphatic_gene_count"],
                "aromatic_genes_mean": bd2["aromatic_gene_count"],
                "PL_mean": bd2["PL_mean"],
                "PP_mean": bd2["PP_mean"],
                "overall_mean": bd2["overall_mean"],
            }
        )
    comparison_rows.append(
        {
            "grupo": "Consorcio strict Aliphatic",
            "amostras": ", ".join(sorted(STRICT_CONSORTIA["Aliphatic"])),
            "aliphatic_genes_mean": mean(float(row["unique_gene_count"]) for row in aliphatic_strict_rows),
            "aromatic_genes_mean": "",
            "PL_mean": mean(float(row["PL_mean"]) for row in aliphatic_strict_rows),
            "PP_mean": mean(float(row["PP_mean"]) for row in aliphatic_strict_rows),
            "overall_mean": mean(float(row["overall_mean"]) for row in aliphatic_strict_rows),
        }
    )
    comparison_rows.append(
        {
            "grupo": "Consorcio strict Polyaromatic",
            "amostras": ", ".join(sorted(STRICT_CONSORTIA["Polyaromatic"])),
            "aliphatic_genes_mean": "",
            "aromatic_genes_mean": mean(float(row["unique_gene_count"]) for row in aromatic_positive_rows),
            "PL_mean": mean(float(row["PL_mean"]) for row in aromatic_positive_rows),
            "PP_mean": mean(float(row["PP_mean"]) for row in aromatic_positive_rows),
            "overall_mean": mean(float(row["overall_mean"]) for row in aromatic_positive_rows),
        }
    )

    corr_lines = [
        "| Classe | DCPIP | n | Pearson r | Spearman r | Interpretacao |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in correlations:
        pearson_r = row["pearson_r"]
        spearman_r = row["spearman_r"]
        r = spearman_r if spearman_r is not None else pearson_r
        if r is None:
            interpretation = "Nao calculado."
        elif r >= 0.30:
            interpretation = "Tendencia positiva: mais genes acompanha maior DCPIP."
        elif r <= -0.30:
            interpretation = "Tendencia negativa: mais genes nao acompanha maior DCPIP."
        else:
            interpretation = "Associacao fraca: usar como criterio auxiliar, nao isolado."
        corr_lines.append(
            "| {target_class} | {dcpip_metric} | {n_samples} | {pearson} | {spearman} | {interpretation} |".format(
                target_class=row["target_class"],
                dcpip_metric=row["dcpip_metric"],
                n_samples=row["n_samples"],
                pearson=fmt(row["pearson_r"]),
                spearman=fmt(row["spearman_r"]),
                interpretation=interpretation,
            )
        )

    report = f"""# Ranking de candidatos a controle negativo por baixa contagem genica

## Objetivo

Este report usa `BioRemPP_Results (9).csv` para ranquear isolados com menor numero de genes associados a `Aliphatic` e `Aromatic`. Em seguida, cruza esses rankings com os resultados DCPIP ja consolidados para identificar candidatos que combinam baixo potencial genomico e menor desempenho experimental.

A leitura proposta e conservadora: um bom controle negativo nao deve ser escolhido apenas por ter poucos genes. Ele deve, preferencialmente, tambem apresentar baixo `PL_mean`, `PP_mean` ou `overall_mean`, conforme o eixo experimental de interesse.

## Criterios usados

- Fonte de genes: `genomas_to_annotate/cons_model/TABLE_RESULTS/BioRemPP_Results (9).csv`.
- Unidade principal de ranking: numero de `genesymbol` unicos por `Sample` e `compoundclass`.
- Metricas auxiliares: KOs unicos, compostos unicos e numero de linhas de evidencia.
- Fonte DCPIP: `CONSORTIA_MODEL_RESULTS/isolate_consolidated_metrics.csv`.
- Para `Aliphatic`, o DCPIP primario usado no score foi `PL_mean`.
- Para `Aromatic`, o DCPIP primario usado no score foi `PP_mean`, por ser o eixo mais conservador para compostos aromaticos/pesados.
- O score de controle negativo combina ranking ascendente de genes e ranking ascendente do DCPIP primario. Quanto menor o score, mais forte o candidato como controle negativo.

## Candidatos prioritarios para controle negativo combinado

Estes isolados aparecem como os candidatos mais interessantes quando se exige baixa contagem genica em `Aliphatic` e `Aromatic`, junto com menor desempenho DCPIP.

{markdown_table(top_combined, ["sample", "taxon", "aliphatic_gene_count", "aromatic_gene_count", "PL_mean", "PP_mean", "overall_mean", "combined_negative_control_score", "metal_authority", "in_any_strict_consortium"])}

## Recomendacao pratica

O candidato mais forte para controle negativo e `BD2`. Ele combina baixa contagem de genes em `Aliphatic` (`35`) e `Aromatic` (`23`) com os menores valores DCPIP do ranking combinado (`PL_mean` 28.31, `PP_mean` 11.99, `overall_mean` 22.87). Isso torna `BD2` o isolado mais defensavel para testar a hipotese de que menor repertorio genico nessas classes acompanha menor degradacao experimental.

Como controles negativos adicionais ou secundarios, os melhores candidatos sao `BD161`, `BD106`, `BD83`, `BD96`, `BD95`, `BD67` e `BD108`, dependendo do eixo experimental priorizado. Para `Aromatic`, `BD106` e especialmente interessante porque une baixa contagem de genes aromaticos (`32`) com `PP_mean` baixo (`19.49`). Para `Aliphatic`, `BD161`, `BD95` e `BD96` aparecem como alternativas por combinarem contagem alifatica baixa/intermediaria com `PL_mean` reduzido.

`BD147` merece uma observacao: ele tem a menor contagem genica em ambas as classes (`16` genes alifaticos e `13` aromaticos), mas o DCPIP e alto (`PL_mean` 71.50, `PP_mean` 63.04). Portanto, ele nao e um bom controle negativo principal se o objetivo for demonstrar menor degradacao. Ele e mais util como contraexemplo biologico: baixa contagem anotacional nao garante, sozinha, baixo desempenho experimental.

## Contraste com os consorcios positivos strict

Este contraste ajuda a posicionar o controle negativo frente aos consorcios strict selecionados anteriormente.

{markdown_table(comparison_rows, ["grupo", "amostras", "aliphatic_genes_mean", "aromatic_genes_mean", "PL_mean", "PP_mean", "overall_mean"], limit=10)}

## Ranking por baixa contagem genica em Aliphatic

{markdown_table(top_aliphatic, ["sample", "taxon", "unique_gene_count", "unique_ko_count", "unique_compound_count", "PL_mean", "PP_mean", "overall_mean", "negative_control_score", "metal_authority", "in_aliphatic_strict"])}

## Ranking por baixa contagem genica em Aromatic

{markdown_table(top_aromatic, ["sample", "taxon", "unique_gene_count", "unique_ko_count", "unique_compound_count", "PL_mean", "PP_mean", "overall_mean", "negative_control_score", "metal_authority", "in_polyaromatic_strict"])}

## Correlacao entre contagem genica e DCPIP

{chr(10).join(corr_lines)}

## Interpretacao

Os rankings devem ser usados para selecionar controles negativos de forma argumentativa. Isolados no topo do ranking combinado sao mais defensaveis porque unem duas evidencias: baixa capacidade anotacional nas classes alvo e menor desempenho experimental no DCPIP. Isso permite testar a hipotese de que menor repertorio genico para `Aliphatic` ou `Aromatic` se traduz em menor degradacao observada em bancada.

Se a correlacao global for fraca, isso nao invalida o uso de controles negativos. Significa apenas que a relacao gene-DCPIP nao e linear em todo o conjunto, possivelmente por diferencas de expressao, regulacao, crescimento, metabolismo complementar ou por DCPIP medir petroleo como mistura complexa. Nesse caso, a escolha de controles negativos deve priorizar os isolados que sao baixos em genes e tambem baixos em DCPIP, nao apenas um dos dois criterios.

## Arquivos gerados

- `negative_control_candidates_combined.csv`
- `negative_control_candidates_aliphatic.csv`
- `negative_control_candidates_aromatic.csv`
- `negative_control_gene_dcpip_correlations.csv`
- `negative_control_candidates_report.md`
"""
    return report


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    by_class, combined = build_rows()
    correlations = correlation_rows(by_class)

    write_csv(RESULTS_DIR / "negative_control_candidates_aliphatic.csv", by_class["Aliphatic"])
    write_csv(RESULTS_DIR / "negative_control_candidates_aromatic.csv", by_class["Aromatic"])
    write_csv(RESULTS_DIR / "negative_control_candidates_combined.csv", combined)
    write_csv(RESULTS_DIR / "negative_control_gene_dcpip_correlations.csv", correlations)

    report = build_report(by_class, combined, correlations)
    (RESULTS_DIR / "negative_control_candidates_report.md").write_text(report, encoding="utf-8")

    validation = {
        "source_biorempp": str(BIOREMPP_CSV),
        "source_dcpip_metrics": str(ISOLATE_METRICS_CSV),
        "n_aliphatic_ranked": len(by_class["Aliphatic"]),
        "n_aromatic_ranked": len(by_class["Aromatic"]),
        "n_combined_ranked": len(combined),
        "top_combined_samples": [row["sample"] for row in combined[:10]],
    }
    (RESULTS_DIR / "negative_control_candidates_validation.json").write_text(
        json.dumps(validation, indent=2, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
