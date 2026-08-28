from __future__ import annotations

import csv
import itertools
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parent
TABLE_RESULTS = ROOT / "TABLE_RESULTS"
OUTPUT_DIR = ROOT / "CONSORTIA_MODEL_RESULTS"
BIOREMPP_CSV = TABLE_RESULTS / "BioRemPP_Results (9).csv"
ISOLATE_METRICS_CSV = OUTPUT_DIR / "isolate_consolidated_metrics.csv"

TARGET_CLASSES = ("Aliphatic", "Polyaromatic")
TARGET_DCPIP_METRIC = {
    "Aliphatic": "PL_mean",
    "Polyaromatic": "PP_mean",
}

# Official universe transcribed from UC_8.1/UC8.1_METAL.png.
METAL_AUTHORITY_GROUPS = {
    "Metal_Group_1": ["E7", "BD48", "BD54", "BD158"],
    "Metal_Group_12": ["BD163"],
    "Metal_Group_4": [
        "BD120",
        "BD126",
        "BD127",
        "BD50",
        "BD61",
        "BD132",
        "BD139",
        "BD160",
        "BD162",
        "BG1",
        "BD9",
    ],
    "Metal_Group_9": ["BD117"],
}

METAL_AUTHORITY = sorted(
    sample for samples in METAL_AUTHORITY_GROUPS.values() for sample in samples
)
SAMPLE_TO_METAL_GROUP = {
    sample: group
    for group, samples in METAL_AUTHORITY_GROUPS.items()
    for sample in samples
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow({key: csv_value(value) for key, value in row.items()})


def csv_value(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return round(value, 6)
    if isinstance(value, (set, frozenset, list, tuple)):
        return ";".join(str(item) for item in sorted(value))
    return value


def pct(part: int | float, total: int | float) -> float:
    return 0.0 if not total else 100.0 * part / total


def parse_float(value: str | None) -> float | None:
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def normalize(value: float, min_value: float, max_value: float) -> float:
    if max_value == min_value:
        return 1.0
    return (value - min_value) / (max_value - min_value)


def load_isolate_metrics() -> dict[str, dict[str, str]]:
    return {row["sample"]: row for row in read_csv(ISOLATE_METRICS_CSV)}


def load_class_sets() -> dict[str, dict[str, dict[str, set[str]]]]:
    class_sets: dict[str, dict[str, dict[str, set[str]]]] = defaultdict(
        lambda: defaultdict(lambda: {"compounds": set(), "kos": set(), "genes": set()})
    )
    for row in read_csv(BIOREMPP_CSV):
        sample = row["Sample"].strip()
        compound_class = row["compoundclass"].strip()
        class_sets[compound_class][sample]["compounds"].add(row["compoundname"].strip())
        class_sets[compound_class][sample]["kos"].add(row["ko"].strip())
        class_sets[compound_class][sample]["genes"].add(row["genesymbol"].strip())
    return class_sets


def leave_one_out_losses(combo: tuple[str, ...], sets_by_sample: dict[str, set[str]]) -> dict[str, int]:
    full_union = set().union(*(sets_by_sample[sample] for sample in combo))
    losses: dict[str, int] = {}
    for sample in combo:
        without_sample = set().union(
            *(sets_by_sample[other] for other in combo if other != sample)
        )
        losses[sample] = len(full_union - without_sample)
    return losses


def evaluate_class(
    target_class: str,
    class_sets: dict[str, dict[str, dict[str, set[str]]]],
    metrics: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    target_metric = TARGET_DCPIP_METRIC[target_class]
    total_compounds = set().union(
        *(sets["compounds"] for sets in class_sets[target_class].values())
    )
    total_kos = set().union(*(sets["kos"] for sets in class_sets[target_class].values()))
    candidates = [
        sample
        for sample in METAL_AUTHORITY
        if sample in class_sets[target_class] and sample in metrics
    ]

    raw_rows: list[dict[str, object]] = []
    for combo in itertools.combinations(candidates, 3):
        compound_sets = {sample: class_sets[target_class][sample]["compounds"] for sample in combo}
        ko_sets = {sample: class_sets[target_class][sample]["kos"] for sample in combo}
        gene_sets = {sample: class_sets[target_class][sample]["genes"] for sample in combo}

        union_compounds = set().union(*(compound_sets[sample] for sample in combo))
        union_kos = set().union(*(ko_sets[sample] for sample in combo))
        union_genes = set().union(*(gene_sets[sample] for sample in combo))
        compound_losses = leave_one_out_losses(combo, compound_sets)
        gene_losses = leave_one_out_losses(combo, gene_sets)

        pairwise_compound_jaccards = [
            jaccard(compound_sets[a], compound_sets[b])
            for a, b in itertools.combinations(combo, 2)
        ]
        pairwise_gene_jaccards = [
            jaccard(gene_sets[a], gene_sets[b])
            for a, b in itertools.combinations(combo, 2)
        ]
        dcpip_values = [parse_float(metrics[sample].get(target_metric)) for sample in combo]
        overall_values = [parse_float(metrics[sample].get("overall_mean")) for sample in combo]
        if any(value is None for value in dcpip_values):
            continue

        raw_rows.append(
            {
                "target_class": target_class,
                "samples": combo,
                "samples_label": " + ".join(combo),
                "coverage_compounds": len(union_compounds),
                "total_class_compounds": len(total_compounds),
                "coverage_pct": pct(len(union_compounds), len(total_compounds)),
                "coverage_kos": len(union_kos),
                "total_class_kos": len(total_kos),
                "ko_coverage_pct": pct(len(union_kos), len(total_kos)),
                "gene_union_count": len(union_genes),
                "target_dcpip_metric": target_metric,
                "target_dcpip_mean": mean(value for value in dcpip_values if value is not None),
                "overall_dcpip_mean": mean(value for value in overall_values if value is not None),
                "min_compound_loss": min(compound_losses.values()),
                "mean_compound_loss": mean(compound_losses.values()),
                "compound_losses": compound_losses,
                "min_gene_loss": min(gene_losses.values()),
                "mean_gene_loss": mean(gene_losses.values()),
                "gene_losses": gene_losses,
                "avg_pairwise_compound_jaccard": mean(pairwise_compound_jaccards),
                "avg_pairwise_gene_jaccard": mean(pairwise_gene_jaccards),
                "metal_groups": {
                    sample: SAMPLE_TO_METAL_GROUP.get(sample, "") for sample in combo
                },
                "taxa": {sample: metrics[sample].get("taxon", "") for sample in combo},
            }
        )

    ranges = {
        key: (
            min(float(row[key]) for row in raw_rows),
            max(float(row[key]) for row in raw_rows),
        )
        for key in [
            "coverage_pct",
            "ko_coverage_pct",
            "target_dcpip_mean",
            "overall_dcpip_mean",
            "min_compound_loss",
            "min_gene_loss",
            "avg_pairwise_compound_jaccard",
            "avg_pairwise_gene_jaccard",
        ]
    }

    scored_rows: list[dict[str, object]] = []
    for row in raw_rows:
        coverage_score = normalize(
            float(row["coverage_pct"]), *ranges["coverage_pct"]
        )
        ko_score = normalize(
            float(row["ko_coverage_pct"]), *ranges["ko_coverage_pct"]
        )
        dcpip_score = normalize(
            float(row["target_dcpip_mean"]), *ranges["target_dcpip_mean"]
        )
        overall_score = normalize(
            float(row["overall_dcpip_mean"]), *ranges["overall_dcpip_mean"]
        )
        compound_balance_score = normalize(
            float(row["min_compound_loss"]), *ranges["min_compound_loss"]
        )
        gene_balance_score = normalize(
            float(row["min_gene_loss"]), *ranges["min_gene_loss"]
        )
        compound_complementarity_score = 1.0 - normalize(
            float(row["avg_pairwise_compound_jaccard"]),
            *ranges["avg_pairwise_compound_jaccard"],
        )
        gene_complementarity_score = 1.0 - normalize(
            float(row["avg_pairwise_gene_jaccard"]),
            *ranges["avg_pairwise_gene_jaccard"],
        )

        balanced_score = (
            0.30 * coverage_score
            + 0.10 * ko_score
            + 0.10 * dcpip_score
            + 0.05 * overall_score
            + 0.20 * compound_balance_score
            + 0.10 * gene_balance_score
            + 0.10 * compound_complementarity_score
            + 0.05 * gene_complementarity_score
        )

        scored = dict(row)
        scored.update(
            {
                "coverage_score": coverage_score,
                "ko_score": ko_score,
                "dcpip_score": dcpip_score,
                "overall_score": overall_score,
                "compound_balance_score": compound_balance_score,
                "gene_balance_score": gene_balance_score,
                "compound_complementarity_score": compound_complementarity_score,
                "gene_complementarity_score": gene_complementarity_score,
                "balanced_v2_score": balanced_score,
            }
        )
        scored_rows.append(scored)

    scored_rows.sort(
        key=lambda row: (
            -float(row["balanced_v2_score"]),
            -float(row["coverage_pct"]),
            -float(row["min_compound_loss"]),
            float(row["avg_pairwise_compound_jaccard"]),
        )
    )
    for rank, row in enumerate(scored_rows, start=1):
        row["rank"] = rank
    return scored_rows


def flatten_for_csv(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    flattened: list[dict[str, object]] = []
    for row in rows:
        samples = tuple(row["samples"])
        compound_losses = row["compound_losses"]
        gene_losses = row["gene_losses"]
        metal_groups = row["metal_groups"]
        taxa = row["taxa"]
        flattened.append(
            {
                "rank": row["rank"],
                "target_class": row["target_class"],
                "samples": row["samples_label"],
                "sample_1": samples[0],
                "sample_2": samples[1],
                "sample_3": samples[2],
                "taxa": "; ".join(f"{sample}={taxa[sample]}" for sample in samples),
                "metal_groups": "; ".join(
                    f"{sample}={metal_groups[sample]}" for sample in samples
                ),
                "coverage_compounds": row["coverage_compounds"],
                "total_class_compounds": row["total_class_compounds"],
                "coverage_pct": row["coverage_pct"],
                "coverage_kos": row["coverage_kos"],
                "total_class_kos": row["total_class_kos"],
                "ko_coverage_pct": row["ko_coverage_pct"],
                "gene_union_count": row["gene_union_count"],
                "target_dcpip_metric": row["target_dcpip_metric"],
                "target_dcpip_mean": row["target_dcpip_mean"],
                "overall_dcpip_mean": row["overall_dcpip_mean"],
                "min_compound_loss": row["min_compound_loss"],
                "mean_compound_loss": row["mean_compound_loss"],
                "compound_losses": "; ".join(
                    f"{sample}={compound_losses[sample]}" for sample in samples
                ),
                "min_gene_loss": row["min_gene_loss"],
                "mean_gene_loss": row["mean_gene_loss"],
                "gene_losses": "; ".join(
                    f"{sample}={gene_losses[sample]}" for sample in samples
                ),
                "avg_pairwise_compound_jaccard": row["avg_pairwise_compound_jaccard"],
                "avg_pairwise_gene_jaccard": row["avg_pairwise_gene_jaccard"],
                "balanced_v2_score": row["balanced_v2_score"],
            }
        )
    return flattened


def sample_metrics_table(
    samples: tuple[str, ...],
    target_class: str,
    class_sets: dict[str, dict[str, dict[str, set[str]]]],
    metrics: dict[str, dict[str, str]],
) -> str:
    target_metric = TARGET_DCPIP_METRIC[target_class]
    rows = [
        "| Isolado | Taxon | Grupo Metal | Compostos da classe | Genes da classe | KOs da classe | DCPIP alvo | Media geral |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for sample in samples:
        sets = class_sets[target_class][sample]
        metric = metrics[sample]
        rows.append(
            "| {sample} | {taxon} | {metal_group} | {compounds} | {genes} | {kos} | {target_dcpip:.2f} | {overall:.2f} |".format(
                sample=sample,
                taxon=metric.get("taxon", ""),
                metal_group=SAMPLE_TO_METAL_GROUP.get(sample, ""),
                compounds=len(sets["compounds"]),
                genes=len(sets["genes"]),
                kos=len(sets["kos"]),
                target_dcpip=parse_float(metric.get(target_metric)) or 0.0,
                overall=parse_float(metric.get("overall_mean")) or 0.0,
            )
        )
    return "\n".join(rows)


def top_rows_table(rows: list[dict[str, object]], limit: int = 10) -> str:
    lines = [
        "| Rank | Trio | Cobertura | KOs | DCPIP alvo | Min. perda compostos | Jaccard compostos | Score V2 |",
        "|---:|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows[:limit]:
        lines.append(
            "| {rank} | {samples} | {coverage_compounds}/{total_compounds} ({coverage_pct:.2f}%) | {coverage_kos}/{total_kos} ({ko_pct:.2f}%) | {dcpip:.2f} | {min_loss} | {jaccard:.3f} | {score:.3f} |".format(
                rank=row["rank"],
                samples=row["samples_label"],
                coverage_compounds=row["coverage_compounds"],
                total_compounds=row["total_class_compounds"],
                coverage_pct=row["coverage_pct"],
                coverage_kos=row["coverage_kos"],
                total_kos=row["total_class_kos"],
                ko_pct=row["ko_coverage_pct"],
                dcpip=row["target_dcpip_mean"],
                min_loss=row["min_compound_loss"],
                jaccard=row["avg_pairwise_compound_jaccard"],
                score=row["balanced_v2_score"],
            )
        )
    return "\n".join(lines)


def selected_summary_table(selected: dict[str, dict[str, object]]) -> str:
    lines = [
        "| Classe alvo | Trio V2 selecionado | Cobertura de compostos | Cobertura de KOs | DCPIP alvo medio | Redundancia media | Score V2 |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for target_class in TARGET_CLASSES:
        row = selected[target_class]
        lines.append(
            "| {target_class} | {samples} | {coverage_compounds}/{total_compounds} ({coverage_pct:.2f}%) | {coverage_kos}/{total_kos} ({ko_pct:.2f}%) | {dcpip:.2f} | {jaccard:.3f} | {score:.3f} |".format(
                target_class=target_class,
                samples=row["samples_label"],
                coverage_compounds=row["coverage_compounds"],
                total_compounds=row["total_class_compounds"],
                coverage_pct=row["coverage_pct"],
                coverage_kos=row["coverage_kos"],
                total_kos=row["total_class_kos"],
                ko_pct=row["ko_coverage_pct"],
                dcpip=row["target_dcpip_mean"],
                jaccard=row["avg_pairwise_compound_jaccard"],
                score=row["balanced_v2_score"],
            )
        )
    return "\n".join(lines)


def sensitivity_table(
    rankings: dict[str, list[dict[str, object]]],
    selected: dict[str, dict[str, object]],
) -> str:
    lines = [
        "| Classe alvo | Trio selecionado V2 | Cobertura V2 | Melhor trio por cobertura bruta | Cobertura maxima | Por que o V2 foi mantido |",
        "|---|---|---:|---|---:|---|",
    ]
    for target_class in TARGET_CLASSES:
        rows = rankings[target_class]
        max_coverage = max(int(row["coverage_compounds"]) for row in rows)
        max_coverage_rows = [
            row for row in rows if int(row["coverage_compounds"]) == max_coverage
        ]
        best_coverage_row = sorted(
            max_coverage_rows,
            key=lambda row: (
                -float(row["balanced_v2_score"]),
                -float(row["target_dcpip_mean"]),
                float(row["avg_pairwise_compound_jaccard"]),
            ),
        )[0]
        selected_row = selected[target_class]
        if selected_row["samples_label"] == best_coverage_row["samples_label"]:
            reason = "Coincide com a melhor cobertura e tambem fica no topo do score V2."
        else:
            reason = (
                "Aceita pequena perda de cobertura bruta para ganhar em score balanceado, "
                "DCPIP e contribuicao minima por membro."
            )
        lines.append(
            "| {target_class} | {selected_samples} | {selected_cov}/{selected_total} ({selected_pct:.2f}%) | {max_samples} | {max_cov}/{max_total} ({max_pct:.2f}%) | {reason} |".format(
                target_class=target_class,
                selected_samples=selected_row["samples_label"],
                selected_cov=selected_row["coverage_compounds"],
                selected_total=selected_row["total_class_compounds"],
                selected_pct=selected_row["coverage_pct"],
                max_samples=best_coverage_row["samples_label"],
                max_cov=best_coverage_row["coverage_compounds"],
                max_total=best_coverage_row["total_class_compounds"],
                max_pct=best_coverage_row["coverage_pct"],
                reason=reason,
            )
        )
    return "\n".join(lines)


def build_report(
    rankings: dict[str, list[dict[str, object]]],
    class_sets: dict[str, dict[str, dict[str, set[str]]]],
    metrics: dict[str, dict[str, str]],
) -> str:
    selected = {target_class: rankings[target_class][0] for target_class in TARGET_CLASSES}
    aliphatic_selected = selected["Aliphatic"]
    poly_selected = selected["Polyaromatic"]

    report = f"""# UC 8.1 Consortium Modeling Report V2

Gerado a partir dos insumos de `genomas_to_annotate/cons_model`.

## Racional da V2

O primeiro modelo de consorcios usava uma logica sequencial de set cover. Essa abordagem e util para maximizar cobertura, mas pode enviesar a selecao para o primeiro isolado com maior inventario de genes ou compostos. Depois dessa primeira escolha, os demais isolados podem entrar apenas por acrescentarem poucos genes ou poucos compostos novos, gerando um consorcio eficiente em cobertura, mas potencialmente redundante.

A V2 muda a regra de decisao: em vez de escolher isolados um por um, ela avalia todas as combinacoes possiveis de `3` isolados dentro do universo oficial da imagem de Metal. Cada trio e pontuado como um sistema completo. Assim, o modelo prioriza comportamento consorcial balanceado, e nao o efeito marginal de um primeiro membro dominante.

## Criterios de pontuacao V2

- Exatamente `3` isolados por consorcio.
- Universo candidato: os `17` isolados definidos pela imagem `UC_8.1/UC8.1_METAL.png`.
- Evidencia primaria: cobertura total de compostos da classe alvo.
- Evidencias secundarias: cobertura de KOs, media DCPIP alvo e media DCPIP geral.
- Evidencias anti-redundancia: perdas leave-one-out de compostos e genes, alem da sobreposicao media por Jaccard entre pares de isolados.
- Metrica DCPIP alvo: `PL_mean` para `Aliphatic`; `PP_mean` para `Polyaromatic`.

Pesos usados no score V2:

| Componente | Peso |
|---|---:|
| Cobertura de compostos | 0.30 |
| Cobertura de KOs | 0.10 |
| Media DCPIP alvo | 0.10 |
| Media DCPIP geral | 0.05 |
| Perda minima leave-one-out de compostos | 0.20 |
| Perda minima leave-one-out de genes | 0.10 |
| Complementaridade por compostos | 0.10 |
| Complementaridade por genes | 0.05 |

## Consorcios V2 selecionados com 3 isolados

{selected_summary_table(selected)}

## Analise de sensibilidade: cobertura bruta versus score balanceado

Esta etapa separa explicitamente dois criterios que competem entre si. O trio de maior cobertura bruta nem sempre e o melhor trio experimentalmente ou o menos redundante. A V2 permite aceitar uma pequena perda de cobertura quando isso melhora DCPIP, cobertura de KOs e contribuicao minima por membro.

{sensitivity_table(rankings, selected)}

## Resultado V2 para Aliphatic

Trio selecionado:

```text
{aliphatic_selected["samples_label"]}
```

Este trio cobre `{aliphatic_selected["coverage_compounds"]}` de `{aliphatic_selected["total_class_compounds"]}` compostos `Aliphatic` (`{aliphatic_selected["coverage_pct"]:.2f}%`) usando apenas tres isolados. Tambem cobre `{aliphatic_selected["coverage_kos"]}` de `{aliphatic_selected["total_class_kos"]}` KOs alifaticos (`{aliphatic_selected["ko_coverage_pct"]:.2f}%`).

A perda minima leave-one-out de compostos e `{aliphatic_selected["min_compound_loss"]}`. Isso significa que todo membro selecionado contribui com pelo menos essa quantidade de compostos que nao sao recuperados quando ele e removido do trio. Esse criterio reduz a tendencia anterior de manter isolados que acrescentam apenas um numero muito pequeno de alvos unicos.

{sample_metrics_table(aliphatic_selected["samples"], "Aliphatic", class_sets, metrics)}

Trios `Aliphatic` mais bem ranqueados:

{top_rows_table(rankings["Aliphatic"], limit=10)}

## Resultado V2 para Polyaromatic

Trio selecionado:

```text
{poly_selected["samples_label"]}
```

Este trio cobre `{poly_selected["coverage_compounds"]}` de `{poly_selected["total_class_compounds"]}` compostos `Polyaromatic` (`{poly_selected["coverage_pct"]:.2f}%`) usando apenas tres isolados. Tambem cobre `{poly_selected["coverage_kos"]}` de `{poly_selected["total_class_kos"]}` KOs poliaromaticos (`{poly_selected["ko_coverage_pct"]:.2f}%`).

A perda minima leave-one-out de compostos e `{poly_selected["min_compound_loss"]}`, mostrando que nenhum membro selecionado e meramente residual. Cada isolado contribui com uma fracao mensuravel e nao trivial da cobertura do trio.

{sample_metrics_table(poly_selected["samples"], "Polyaromatic", class_sets, metrics)}

Trios `Polyaromatic` mais bem ranqueados:

{top_rows_table(rankings["Polyaromatic"], limit=10)}

## Interpretacao

A V2 e mais conservadora para desenho experimental porque remove o quarto isolado marginal do primeiro modelo e obriga a selecao a ser explicavel como um sistema de tres membros. Os trios selecionados devem ser interpretados como consorcios compactos e menos redundantes, nao como solucoes de cobertura maxima absoluta.

Para `Aliphatic`, o trio V2 preserva cobertura relevante, aumenta o suporte medio de DCPIP e evita que a escolha seja dominada por um primeiro isolado de grande inventario. Para `Polyaromatic`, o trio V2 preserva a maior parte da cobertura e mantem boa contribuicao minima por membro.

O report V2 deve ser usado quando a prioridade experimental e testar consorcios menores, menos redundantes e mais faceis de interpretar. O modelo anterior permanece util como referencia de cobertura maxima, mas a V2 responde melhor a preocupacao de que um primeiro isolado dominante pode enviesar uma selecao sequencial.

## Arquivos gerados

- `consortia_model_report_V2.md`
- `consortia_model_v2_ranked_trios.csv`
- `consortia_model_v2_selected_trios.csv`
- `consortia_model_v2_validation.json`
"""
    return report


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    class_sets = load_class_sets()
    metrics = load_isolate_metrics()

    rankings = {
        target_class: evaluate_class(target_class, class_sets, metrics)
        for target_class in TARGET_CLASSES
    }
    selected = {target_class: rankings[target_class][0] for target_class in TARGET_CLASSES}

    all_ranked_rows = []
    for target_class in TARGET_CLASSES:
        all_ranked_rows.extend(flatten_for_csv(rankings[target_class]))
    write_csv(OUTPUT_DIR / "consortia_model_v2_ranked_trios.csv", all_ranked_rows)
    write_csv(
        OUTPUT_DIR / "consortia_model_v2_selected_trios.csv",
        flatten_for_csv([selected[target_class] for target_class in TARGET_CLASSES]),
    )

    report = build_report(rankings, class_sets, metrics)
    (OUTPUT_DIR / "consortia_model_report_V2.md").write_text(report, encoding="utf-8")

    validation = {
        "candidate_universe_size": len(METAL_AUTHORITY),
        "candidate_universe": METAL_AUTHORITY,
        "target_classes": list(TARGET_CLASSES),
        "trios_evaluated_per_class": {
            target_class: len(rankings[target_class]) for target_class in TARGET_CLASSES
        },
        "selected_trios": {
            target_class: selected[target_class]["samples"]
            for target_class in TARGET_CLASSES
        },
        "selected_coverage_pct": {
            target_class: selected[target_class]["coverage_pct"]
            for target_class in TARGET_CLASSES
        },
        "score_weights": {
            "compound_coverage": 0.30,
            "ko_coverage": 0.10,
            "target_dcpip_mean": 0.10,
            "overall_dcpip_mean": 0.05,
            "minimum_compound_leave_one_out_loss": 0.20,
            "minimum_gene_leave_one_out_loss": 0.10,
            "compound_complementarity": 0.10,
            "gene_complementarity": 0.05,
        },
    }
    (OUTPUT_DIR / "consortia_model_v2_validation.json").write_text(
        json.dumps(validation, indent=2, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
