from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Iterable


ROOT = Path(__file__).resolve().parent
TABLE_RESULTS = ROOT / "TABLE_RESULTS"
DCPIP_DIR = ROOT / "dcpips"
UC81_DIR = ROOT / "UC_8.1"
OUTPUT_DIR = ROOT / "CONSORTIA_MODEL_RESULTS"

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
METAL_AUTHORITY = {
    sample for samples in METAL_AUTHORITY_GROUPS.values() for sample in samples
}
SAMPLE_TO_METAL_GROUP = {
    sample: group
    for group, samples in METAL_AUTHORITY_GROUPS.items()
    for sample in samples
}


@dataclass(frozen=True)
class Guild:
    guild_id: str
    members: tuple[str, ...]
    compounds: frozenset[str]


@dataclass
class Selection:
    order: int
    target_class: str
    model_version: str
    role: str
    guild: Guild
    representative: str
    newly_covered: frozenset[str]
    covered_after: frozenset[str]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: csv_value(row.get(key)) for key in fieldnames})


def csv_value(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, float):
        if math.isnan(value):
            return ""
        return round(value, 6)
    if isinstance(value, (list, tuple, set, frozenset)):
        return ";".join(str(item) for item in sorted(value))
    return value


def pct(part: int | float, total: int | float) -> float:
    return 0.0 if not total else 100.0 * part / total


def safe_mean(values: Iterable[float | None]) -> float | None:
    valid = [value for value in values if value is not None]
    return mean(valid) if valid else None


def parse_ko_subset(path: Path) -> dict[str, set[str]]:
    sample_to_kos: dict[str, set[str]] = defaultdict(set)
    current_sample: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(">"):
            current_sample = line[1:]
            continue
        if current_sample:
            sample_to_kos[current_sample].add(line)
    return dict(sample_to_kos)


def load_dcpip() -> tuple[dict[str, dict[str, object]], list[str]]:
    path = DCPIP_DIR / "dcpips_measurements_by_isolate.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    records: dict[str, dict[str, object]] = {}
    for isolate in data["isolates"]:
        sample = isolate["isolate_code"]
        measurements = isolate["measurements"]
        treatment_means = {
            treatment: safe_mean(values)
            for treatment, values in measurements.items()
        }
        pl_mean = safe_mean([treatment_means.get("PL1"), treatment_means.get("PL2")])
        pp_mean = safe_mean([treatment_means.get("PP1"), treatment_means.get("PP2")])
        overall_mean = safe_mean(
            [
                treatment_means.get("PL1"),
                treatment_means.get("PL2"),
                treatment_means.get("PP1"),
                treatment_means.get("PP2"),
            ]
        )
        missing_values = sum(
            1
            for values in measurements.values()
            for value in values
            if value is None
        )
        records[sample] = {
            "sample": sample,
            "taxon": isolate["taxon"],
            "source_label": isolate["source_label"],
            "PL1_mean": treatment_means.get("PL1"),
            "PL2_mean": treatment_means.get("PL2"),
            "PP1_mean": treatment_means.get("PP1"),
            "PP2_mean": treatment_means.get("PP2"),
            "PL_mean": pl_mean,
            "PP_mean": pp_mean,
            "overall_mean": overall_mean,
            "dcpip_missing_values": missing_values,
        }
    return records, list(records)


def load_raw_uc81_metal_groups() -> dict[str, set[str]]:
    path = UC81_DIR / "UC-8-1_biorempp_df_20260812_203350.csv"
    rows = read_csv(path)
    sample_groups: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        if row.get("Compound_Class") == "Metal":
            sample = row.get("Sample", "").strip()
            group = row.get("Group", "").strip()
            if sample and group:
                sample_groups[sample].add(group)
    return dict(sample_groups)


def index_biorempp(rows: list[dict[str, str]]) -> dict[str, object]:
    sample_compounds: dict[tuple[str, str], set[str]] = defaultdict(set)
    sample_kos_by_class: dict[tuple[str, str], set[str]] = defaultdict(set)
    sample_kos_by_compound: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    sample_compound_kos: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    class_compounds: dict[str, set[str]] = defaultdict(set)
    class_kos: dict[str, set[str]] = defaultdict(set)
    compound_kos: dict[tuple[str, str], set[str]] = defaultdict(set)
    sample_references: dict[str, set[str]] = defaultdict(set)
    sample_enzyme_activities: dict[str, set[str]] = defaultdict(set)
    samples: set[str] = set()

    for row in rows:
        sample = row["Sample"].strip()
        target_class = row["compoundclass"].strip()
        compound = row["compoundname"].strip()
        ko = row["ko"].strip()
        if not sample or not target_class or not compound or not ko:
            continue
        samples.add(sample)
        sample_compounds[(sample, target_class)].add(compound)
        sample_kos_by_class[(sample, target_class)].add(ko)
        sample_kos_by_compound[(sample, target_class, compound)].add(ko)
        sample_compound_kos[(sample, target_class, compound)].add(ko)
        class_compounds[target_class].add(compound)
        class_kos[target_class].add(ko)
        compound_kos[(target_class, compound)].add(ko)
        if row.get("referenceAG"):
            sample_references[sample].add(row["referenceAG"])
        if row.get("enzyme_activity"):
            sample_enzyme_activities[sample].add(row["enzyme_activity"])

    return {
        "samples": samples,
        "sample_compounds": sample_compounds,
        "sample_kos_by_class": sample_kos_by_class,
        "sample_kos_by_compound": sample_kos_by_compound,
        "sample_compound_kos": sample_compound_kos,
        "class_compounds": class_compounds,
        "class_kos": class_kos,
        "compound_kos": compound_kos,
        "sample_references": sample_references,
        "sample_enzyme_activities": sample_enzyme_activities,
    }


def simple_sample_metrics(
    rows: list[dict[str, str]],
    sample_col: str,
    ko_col: str | None = None,
    category_cols: tuple[str, ...] = (),
) -> dict[str, dict[str, set[str]]]:
    metrics: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for row in rows:
        sample = row.get(sample_col, "").strip()
        if not sample:
            continue
        if ko_col and row.get(ko_col):
            metrics[sample][ko_col].add(row[ko_col].strip())
        for col in category_cols:
            if row.get(col):
                metrics[sample][col].add(row[col].strip())
    return metrics


def tox_metrics(rows: list[dict[str, str]]) -> dict[str, dict[str, object]]:
    label_cols = [col for col in rows[0] if col.startswith("label_")] if rows else []
    metrics: dict[str, dict[str, object]] = defaultdict(
        lambda: {
            "tox_unique_compounds": set(),
            "tox_high_toxicity_compounds": set(),
            "tox_high_toxicity_endpoint_hits": 0,
        }
    )
    for row in rows:
        sample = row.get("Sample", "").strip()
        compound = row.get("compoundname", "").strip()
        if not sample or not compound:
            continue
        metrics[sample]["tox_unique_compounds"].add(compound)
        high_hits = sum(1 for col in label_cols if row.get(col) == "High Toxicity")
        if high_hits:
            metrics[sample]["tox_high_toxicity_compounds"].add(compound)
            metrics[sample]["tox_high_toxicity_endpoint_hits"] += high_hits
    return metrics


def group_samples(
    target_class: str,
    universe_samples: Iterable[str],
    sample_compounds: dict[tuple[str, str], set[str]],
    prefix: str,
) -> list[Guild]:
    signature_to_members: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for sample in sorted(set(universe_samples)):
        compounds = sample_compounds.get((sample, target_class), set())
        if compounds:
            signature_to_members[tuple(sorted(compounds))].append(sample)

    sorted_items = sorted(
        signature_to_members.items(),
        key=lambda item: (-len(item[0]), item[1][0], item[0]),
    )
    return [
        Guild(
            guild_id=f"{prefix}_G{index:02d}",
            members=tuple(sorted(members)),
            compounds=frozenset(signature),
        )
        for index, (signature, members) in enumerate(sorted_items, start=1)
    ]


def representative_for_guild(
    guild: Guild,
    target_class: str,
    class_metrics: dict[str, dict[str, object]],
) -> str:
    metric = TARGET_DCPIP_METRIC[target_class]

    def rank(sample: str) -> tuple[float, float, int, str]:
        row = class_metrics[sample]
        dcpip_value = row.get(metric)
        completeness = row.get(f"{target_class}_ko_completeness_pct") or 0.0
        unique_kos = row.get("unique_ko_count") or 0
        return (
            float(dcpip_value) if dcpip_value is not None else -1.0,
            float(completeness),
            int(unique_kos),
            sample,
        )

    return sorted(guild.members, key=rank, reverse=True)[0]


def set_cover(
    target_class: str,
    groups: list[Guild],
    target_compounds: set[str],
    class_metrics: dict[str, dict[str, object]],
    model_version: str,
    role: str,
    start_order: int = 1,
    precovered: set[str] | None = None,
) -> tuple[list[Selection], set[str]]:
    covered = set(precovered or set())
    uncovered = set(target_compounds) - covered
    available = list(groups)
    selections: list[Selection] = []
    order = start_order

    while uncovered:
        candidates = []
        for guild in available:
            gain = guild.compounds & uncovered
            if not gain:
                continue
            representative = representative_for_guild(guild, target_class, class_metrics)
            rep_metrics = class_metrics[representative]
            target_metric = TARGET_DCPIP_METRIC[target_class]
            candidates.append(
                (
                    len(gain),
                    len(guild.compounds),
                    float(rep_metrics.get(f"{target_class}_ko_completeness_pct") or 0.0),
                    float(rep_metrics.get(target_metric) or -1.0),
                    -len(guild.members),
                    guild.members[0],
                    guild,
                    representative,
                    gain,
                )
            )
        if not candidates:
            break
        *_, guild, representative, gain = max(candidates)
        covered.update(gain)
        selections.append(
            Selection(
                order=order,
                target_class=target_class,
                model_version=model_version,
                role=role,
                guild=guild,
                representative=representative,
                newly_covered=frozenset(gain),
                covered_after=frozenset(covered),
            )
        )
        available = [item for item in available if item != guild]
        uncovered = set(target_compounds) - covered
        order += 1

    return selections, set(target_compounds) - covered


def build_class_metrics(
    dcpip_records: dict[str, dict[str, object]],
    dcpip_ids: list[str],
    ko_subset: dict[str, set[str]],
    biorempp_index: dict[str, object],
    h_metrics: dict[str, dict[str, set[str]]],
    k_metrics: dict[str, dict[str, set[str]]],
    t_metrics: dict[str, dict[str, object]],
    raw_uc81_metal_groups: dict[str, set[str]],
) -> dict[str, dict[str, object]]:
    rows: dict[str, dict[str, object]] = {}
    annotated_samples = set(biorempp_index["samples"])
    class_compounds = biorempp_index["class_compounds"]
    class_kos = biorempp_index["class_kos"]
    sample_compounds = biorempp_index["sample_compounds"]
    sample_kos_by_class = biorempp_index["sample_kos_by_class"]
    sample_references = biorempp_index["sample_references"]
    sample_enzyme_activities = biorempp_index["sample_enzyme_activities"]

    for sample in sorted(set(dcpip_ids) | annotated_samples | set(ko_subset)):
        dcpip = dcpip_records.get(sample, {})
        row: dict[str, object] = {
            "sample": sample,
            "taxon": dcpip.get("taxon", ""),
            "source_label": dcpip.get("source_label", ""),
            "dcpip_available": sample in dcpip_records,
            "annotated_in_biorempp": sample in annotated_samples,
            "annotated_in_ko_subset": sample in ko_subset,
            "metal_authority": sample in METAL_AUTHORITY,
            "metal_group_from_image": SAMPLE_TO_METAL_GROUP.get(sample, ""),
            "raw_uc81_metal": sample in raw_uc81_metal_groups,
            "raw_uc81_metal_groups": raw_uc81_metal_groups.get(sample, set()),
            "unique_ko_count": len(ko_subset.get(sample, set())),
            "biorempp_reference_count": len(sample_references.get(sample, set())),
            "enzyme_activity_count": len(sample_enzyme_activities.get(sample, set())),
            "hadeg_ko_count": len(h_metrics.get(sample, {}).get("ko", set())),
            "hadeg_pathway_count": len(h_metrics.get(sample, {}).get("Pathway", set())),
            "hadeg_compound_pathway_count": len(
                h_metrics.get(sample, {}).get("compound_pathway", set())
            ),
            "kegg_ko_count": len(k_metrics.get(sample, {}).get("ko", set())),
            "kegg_pathname_count": len(k_metrics.get(sample, {}).get("pathname", set())),
            "tox_unique_compounds": len(
                t_metrics.get(sample, {}).get("tox_unique_compounds", set())
            ),
            "tox_high_toxicity_compounds": len(
                t_metrics.get(sample, {}).get("tox_high_toxicity_compounds", set())
            ),
            "tox_high_toxicity_endpoint_hits": t_metrics.get(sample, {}).get(
                "tox_high_toxicity_endpoint_hits", 0
            ),
        }
        row.update(dcpip)
        for target_class in TARGET_CLASSES:
            compounds = sample_compounds.get((sample, target_class), set())
            kos = sample_kos_by_class.get((sample, target_class), set())
            row[f"{target_class}_compounds_covered"] = len(compounds)
            row[f"{target_class}_compound_coverage_pct"] = pct(
                len(compounds), len(class_compounds.get(target_class, set()))
            )
            row[f"{target_class}_kos_covered"] = len(kos)
            row[f"{target_class}_ko_completeness_pct"] = pct(
                len(kos), len(class_kos.get(target_class, set()))
            )
        rows[sample] = row
    return rows


def selection_reason(selection: Selection, metrics: dict[str, dict[str, object]]) -> str:
    target_class = selection.target_class
    sample = selection.representative
    row = metrics[sample]
    metric_name = TARGET_DCPIP_METRIC[target_class]
    metric_label = "PL_mean" if target_class == "Aliphatic" else "PP_mean"
    reason_parts = [
        f"covers {len(selection.newly_covered)} new {target_class} compounds",
        f"{metric_label}={row.get(metric_name):.2f}" if row.get(metric_name) is not None else f"{metric_label}=NA",
        f"class_KO_completeness={row.get(f'{target_class}_ko_completeness_pct'):.2f}%",
    ]
    if selection.model_version == "strict_metal":
        reason_parts.append("allowed by official Metal image universe")
    elif selection.role == "relaxed_addition":
        if row.get("raw_uc81_metal"):
            reason_parts.append(
                "outside official Metal image but present in raw UC 8.1 Metal CSV; added to close strict coverage gap"
            )
        else:
            reason_parts.append(
                "relaxed addition required to cover compounds absent from strict Metal coverage"
            )
    return "; ".join(reason_parts)


def build_selection_rows(
    selections_by_key: dict[tuple[str, str], list[Selection]],
    metrics: dict[str, dict[str, object]],
    class_compounds: dict[str, set[str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for (target_class, model_version), selections in selections_by_key.items():
        total_compounds = len(class_compounds[target_class])
        for selection in selections:
            sample = selection.representative
            row = metrics[sample]
            target_metric = TARGET_DCPIP_METRIC[target_class]
            rows.append(
                {
                    "target_class": target_class,
                    "model_version": model_version,
                    "selection_order": selection.order,
                    "role": selection.role,
                    "guild_id": selection.guild.guild_id,
                    "representative_sample": sample,
                    "guild_members": selection.guild.members,
                    "metal_authority": row.get("metal_authority"),
                    "metal_group_from_image": row.get("metal_group_from_image"),
                    "raw_uc81_metal": row.get("raw_uc81_metal"),
                    "raw_uc81_metal_groups": row.get("raw_uc81_metal_groups"),
                    "taxon": row.get("taxon"),
                    "newly_covered_compounds_count": len(selection.newly_covered),
                    "guild_compounds_count": len(selection.guild.compounds),
                    "covered_compounds_after_selection": len(selection.covered_after),
                    "class_total_compounds": total_compounds,
                    "class_coverage_after_selection_pct": pct(
                        len(selection.covered_after), total_compounds
                    ),
                    "target_dcpip_metric": target_metric,
                    "target_dcpip_mean": row.get(target_metric),
                    "PL_mean": row.get("PL_mean"),
                    "PP_mean": row.get("PP_mean"),
                    "overall_mean": row.get("overall_mean"),
                    "class_ko_completeness_pct": row.get(
                        f"{target_class}_ko_completeness_pct"
                    ),
                    "class_compound_coverage_pct": row.get(
                        f"{target_class}_compound_coverage_pct"
                    ),
                    "unique_ko_count": row.get("unique_ko_count"),
                    "hadeg_pathway_count": row.get("hadeg_pathway_count"),
                    "kegg_pathname_count": row.get("kegg_pathname_count"),
                    "tox_high_toxicity_compounds": row.get("tox_high_toxicity_compounds"),
                    "newly_covered_compounds": selection.newly_covered,
                    "reason": selection_reason(selection, metrics),
                }
            )
    return rows


def build_coverage_rows(
    selections_by_key: dict[tuple[str, str], list[Selection]],
    class_compounds: dict[str, set[str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for (target_class, model_version), selections in selections_by_key.items():
        sample_to_compounds = {
            selection.representative: set(selection.guild.compounds)
            for selection in selections
        }
        for compound in sorted(class_compounds[target_class]):
            covering_samples = sorted(
                sample
                for sample, compounds in sample_to_compounds.items()
                if compound in compounds
            )
            rows.append(
                {
                    "target_class": target_class,
                    "model_version": model_version,
                    "compound_name": compound,
                    "covered_by_selected": bool(covering_samples),
                    "covering_selected_samples": covering_samples,
                }
            )
    return rows


def build_guild_rows(
    target_class: str,
    model_version: str,
    guilds: list[Guild],
    selected_guild_ids: set[str],
) -> list[dict[str, object]]:
    return [
        {
            "target_class": target_class,
            "model_version": model_version,
            "guild_id": guild.guild_id,
            "selected": guild.guild_id in selected_guild_ids,
            "member_count": len(guild.members),
            "members": guild.members,
            "compound_count": len(guild.compounds),
            "compounds": guild.compounds,
        }
        for guild in guilds
    ]


def write_report(
    path: Path,
    validation: dict[str, object],
    selections_by_key: dict[tuple[str, str], list[Selection]],
    uncovered_by_key: dict[tuple[str, str], set[str]],
    metrics: dict[str, dict[str, object]],
    class_compounds: dict[str, set[str]],
) -> None:
    lines: list[str] = []
    lines.append("# UC 8.1 Consortium Modeling Report")
    lines.append("")
    lines.append("Generated from `genomas_to_annotate/cons_model` inputs.")
    lines.append("")
    lines.append("## Validation Summary")
    lines.append("")
    lines.extend(
        [
            f"- DCPIP isolates: `{validation['dcpip_isolates']}`",
            f"- Annotated BioRemPP samples: `{validation['annotated_samples']}`",
            f"- KO subset samples: `{validation['ko_subset_samples']}`",
            f"- DCPIP-only isolates excluded from annotation model: `{', '.join(validation['dcpip_only_isolates'])}`",
            f"- Official Metal image universe: `{validation['metal_authority_samples']}` samples",
            "- Authority note: `UC8.1_METAL.png` is used as the official Metal optimized universe, even though the raw UC 8.1 CSV has a divergent Metal sample set.",
        ]
    )
    lines.append("")
    lines.append("## Official Metal Universe")
    lines.append("")
    for group, samples in METAL_AUTHORITY_GROUPS.items():
        lines.append(f"- `{group}`: {', '.join(samples)}")
    lines.append("")
    lines.append("## UC 8.1 Metal Source Reconciliation")
    lines.append("")
    lines.extend(
        [
            f"- Raw UC 8.1 Metal CSV samples: `{validation['raw_uc81_metal_samples']}`",
            f"- Samples in image but not raw CSV: `{', '.join(validation['metal_image_only_samples'])}`",
            f"- Samples in raw CSV but not image: `{', '.join(validation['metal_raw_only_samples'])}`",
            "- The strict model uses only the image universe. The relaxed model may add raw-CSV Metal samples only when they close coverage gaps for the target class.",
        ]
    )
    lines.append("")

    for target_class in TARGET_CLASSES:
        lines.append(f"## {target_class} Consortium Results")
        lines.append("")
        for model_version in ("strict_metal", "relaxed"):
            key = (target_class, model_version)
            selections = selections_by_key[key]
            covered = set()
            for selection in selections:
                covered.update(selection.guild.compounds)
            total = len(class_compounds[target_class])
            uncovered = uncovered_by_key[key]
            representatives = [selection.representative for selection in selections]
            lines.append(f"### {model_version}")
            lines.append("")
            lines.append(f"- Representatives: `{', '.join(representatives)}`")
            lines.append(f"- Coverage: `{len(covered)}/{total}` compounds ({pct(len(covered), total):.2f}%).")
            lines.append(f"- Uncovered compounds: `{len(uncovered)}`")
            if uncovered:
                preview = ", ".join(sorted(uncovered)[:12])
                suffix = " ..." if len(uncovered) > 12 else ""
                lines.append(f"- Uncovered preview: {preview}{suffix}")
            lines.append("")
            lines.append("| Order | Representative | Role | Guild Members | New Compounds | Target DCPIP | KO Completeness | Reason |")
            lines.append("|---:|---|---|---|---:|---:|---:|---|")
            metric = TARGET_DCPIP_METRIC[target_class]
            for selection in selections:
                row = metrics[selection.representative]
                lines.append(
                    "| "
                    f"{selection.order} | "
                    f"{selection.representative} | "
                    f"{selection.role} | "
                    f"{', '.join(selection.guild.members)} | "
                    f"{len(selection.newly_covered)} | "
                    f"{row.get(metric):.2f} | "
                    f"{row.get(f'{target_class}_ko_completeness_pct'):.2f}% | "
                    f"{selection_reason(selection, metrics)} |"
                )
            lines.append("")

    lines.append("## Interpretation Notes")
    lines.append("")
    lines.extend(
        [
            "- `strict_metal` tests the hypothesis that the Metal-optimized guild universe is sufficient for the petroleum target class.",
            "- `relaxed` preserves the strict Metal selections and adds only guilds needed to cover compounds not reached by the strict universe.",
            "- `Aliphatic` selections are interpreted mainly against `PL_mean`; `Polyaromatic` selections are interpreted mainly against `PP_mean`.",
            "- DCPIP values are experimental support, not proof that the annotated compound-specific routes are active in consortium.",
            "- KO, HADEG, KEGG, and toxCSM metrics are annotation-level evidence used to explain breadth, depth, complementarity, and toxicological relevance.",
        ]
    )
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ko_subset = parse_ko_subset(ROOT / "ALL_GENOMES_SEQUENCED_subset_tabela.txt")
    dcpip_records, dcpip_ids = load_dcpip()
    raw_uc81_metal_groups = load_raw_uc81_metal_groups()
    biorempp_rows = read_csv(TABLE_RESULTS / "BioRemPP_Results (9).csv")
    h_metrics = simple_sample_metrics(
        read_csv(TABLE_RESULTS / "HADEG_Results (4).csv"),
        sample_col="Sample",
        ko_col="ko",
        category_cols=("Pathway", "compound_pathway"),
    )
    k_metrics = simple_sample_metrics(
        read_csv(TABLE_RESULTS / "KEGG_Results (1).csv"),
        sample_col="Sample",
        ko_col="ko",
        category_cols=("pathname",),
    )
    t_metrics = tox_metrics(read_csv(TABLE_RESULTS / "toxCSM (3).csv"))

    biorempp_index = index_biorempp(biorempp_rows)
    metrics = build_class_metrics(
        dcpip_records=dcpip_records,
        dcpip_ids=dcpip_ids,
        ko_subset=ko_subset,
        biorempp_index=biorempp_index,
        h_metrics=h_metrics,
        k_metrics=k_metrics,
        t_metrics=t_metrics,
        raw_uc81_metal_groups=raw_uc81_metal_groups,
    )

    annotated_samples = set(biorempp_index["samples"])
    dcpip_only = sorted(set(dcpip_ids) - annotated_samples)
    ko_only_missing_from_dcpip = sorted(set(ko_subset) - set(dcpip_ids))
    raw_uc81_metal = set(raw_uc81_metal_groups)
    metal_image_only = sorted(METAL_AUTHORITY - raw_uc81_metal)
    metal_raw_only = sorted(raw_uc81_metal - METAL_AUTHORITY)
    if len(dcpip_ids) != 53:
        raise RuntimeError(f"Expected 53 DCPIP isolates, found {len(dcpip_ids)}")
    if len(annotated_samples) != 51:
        raise RuntimeError(f"Expected 51 annotated BioRemPP samples, found {len(annotated_samples)}")
    if dcpip_only != ["BD130", "BD78"]:
        raise RuntimeError(f"Unexpected DCPIP-only isolates: {dcpip_only}")
    if ko_only_missing_from_dcpip:
        raise RuntimeError(f"KO subset samples missing from DCPIP: {ko_only_missing_from_dcpip}")

    sample_compounds = biorempp_index["sample_compounds"]
    class_compounds = biorempp_index["class_compounds"]

    selections_by_key: dict[tuple[str, str], list[Selection]] = {}
    uncovered_by_key: dict[tuple[str, str], set[str]] = {}
    guild_rows: list[dict[str, object]] = []

    for target_class in TARGET_CLASSES:
        full_target = set(class_compounds[target_class])
        strict_guilds = group_samples(
            target_class=target_class,
            universe_samples=METAL_AUTHORITY & annotated_samples,
            sample_compounds=sample_compounds,
            prefix=f"{target_class}_STRICT",
        )
        strict_selections, strict_uncovered = set_cover(
            target_class=target_class,
            groups=strict_guilds,
            target_compounds=full_target,
            class_metrics=metrics,
            model_version="strict_metal",
            role="strict_metal_guild",
        )
        if any(not set(selection.guild.members) <= METAL_AUTHORITY for selection in strict_selections):
            raise RuntimeError(f"Strict {target_class} selected samples outside Metal authority")
        selections_by_key[(target_class, "strict_metal")] = strict_selections
        uncovered_by_key[(target_class, "strict_metal")] = strict_uncovered
        guild_rows.extend(
            build_guild_rows(
                target_class,
                "strict_metal",
                strict_guilds,
                {selection.guild.guild_id for selection in strict_selections},
            )
        )

        all_guilds = group_samples(
            target_class=target_class,
            universe_samples=annotated_samples,
            sample_compounds=sample_compounds,
            prefix=f"{target_class}_ALL",
        )
        strict_covered = set()
        for selection in strict_selections:
            strict_covered.update(selection.guild.compounds)
        relaxed_additions, relaxed_uncovered = set_cover(
            target_class=target_class,
            groups=all_guilds,
            target_compounds=full_target,
            class_metrics=metrics,
            model_version="relaxed",
            role="relaxed_addition",
            start_order=len(strict_selections) + 1,
            precovered=strict_covered,
        )
        relaxed_selections = [
            Selection(
                order=selection.order,
                target_class=target_class,
                model_version="relaxed",
                role="strict_metal_seed",
                guild=selection.guild,
                representative=selection.representative,
                newly_covered=selection.newly_covered,
                covered_after=selection.covered_after,
            )
            for selection in strict_selections
        ] + relaxed_additions
        selections_by_key[(target_class, "relaxed")] = relaxed_selections
        uncovered_by_key[(target_class, "relaxed")] = relaxed_uncovered
        guild_rows.extend(
            build_guild_rows(
                target_class,
                "relaxed_all_annotated",
                all_guilds,
                {selection.guild.guild_id for selection in relaxed_additions},
            )
        )

        for selection in relaxed_additions:
            if not selection.newly_covered:
                raise RuntimeError(f"Relaxed {target_class} addition without explicit coverage gain")

    isolate_fieldnames = [
        "sample",
        "taxon",
        "source_label",
        "dcpip_available",
        "annotated_in_biorempp",
        "annotated_in_ko_subset",
        "metal_authority",
        "metal_group_from_image",
        "raw_uc81_metal",
        "raw_uc81_metal_groups",
        "unique_ko_count",
        "PL1_mean",
        "PL2_mean",
        "PP1_mean",
        "PP2_mean",
        "PL_mean",
        "PP_mean",
        "overall_mean",
        "dcpip_missing_values",
        "Aliphatic_compounds_covered",
        "Aliphatic_compound_coverage_pct",
        "Aliphatic_kos_covered",
        "Aliphatic_ko_completeness_pct",
        "Polyaromatic_compounds_covered",
        "Polyaromatic_compound_coverage_pct",
        "Polyaromatic_kos_covered",
        "Polyaromatic_ko_completeness_pct",
        "biorempp_reference_count",
        "enzyme_activity_count",
        "hadeg_ko_count",
        "hadeg_pathway_count",
        "hadeg_compound_pathway_count",
        "kegg_ko_count",
        "kegg_pathname_count",
        "tox_unique_compounds",
        "tox_high_toxicity_compounds",
        "tox_high_toxicity_endpoint_hits",
    ]
    write_csv(
        OUTPUT_DIR / "isolate_consolidated_metrics.csv",
        [metrics[sample] for sample in sorted(metrics)],
        isolate_fieldnames,
    )

    selection_rows = build_selection_rows(selections_by_key, metrics, class_compounds)
    write_csv(
        OUTPUT_DIR / "consortium_representatives.csv",
        selection_rows,
        [
            "target_class",
            "model_version",
            "selection_order",
            "role",
            "guild_id",
            "representative_sample",
            "guild_members",
            "metal_authority",
            "metal_group_from_image",
            "raw_uc81_metal",
            "raw_uc81_metal_groups",
            "taxon",
            "newly_covered_compounds_count",
            "guild_compounds_count",
            "covered_compounds_after_selection",
            "class_total_compounds",
            "class_coverage_after_selection_pct",
            "target_dcpip_metric",
            "target_dcpip_mean",
            "PL_mean",
            "PP_mean",
            "overall_mean",
            "class_ko_completeness_pct",
            "class_compound_coverage_pct",
            "unique_ko_count",
            "hadeg_pathway_count",
            "kegg_pathname_count",
            "tox_high_toxicity_compounds",
            "newly_covered_compounds",
            "reason",
        ],
    )

    coverage_rows = build_coverage_rows(selections_by_key, class_compounds)
    write_csv(
        OUTPUT_DIR / "consortium_coverage_by_compound.csv",
        coverage_rows,
        [
            "target_class",
            "model_version",
            "compound_name",
            "covered_by_selected",
            "covering_selected_samples",
        ],
    )
    write_csv(
        OUTPUT_DIR / "class_guilds_audit.csv",
        guild_rows,
        [
            "target_class",
            "model_version",
            "guild_id",
            "selected",
            "member_count",
            "members",
            "compound_count",
            "compounds",
        ],
    )

    validation = {
        "dcpip_isolates": len(dcpip_ids),
        "annotated_samples": len(annotated_samples),
        "ko_subset_samples": len(ko_subset),
        "dcpip_only_isolates": dcpip_only,
        "metal_authority_samples": len(METAL_AUTHORITY),
        "metal_authority_group_count": len(METAL_AUTHORITY_GROUPS),
        "raw_uc81_metal_samples": len(raw_uc81_metal),
        "metal_image_only_samples": metal_image_only,
        "metal_raw_only_samples": metal_raw_only,
        "target_classes": list(TARGET_CLASSES),
        "outputs": [
            "isolate_consolidated_metrics.csv",
            "consortium_representatives.csv",
            "consortium_coverage_by_compound.csv",
            "class_guilds_audit.csv",
            "uc81_metal_source_reconciliation.csv",
            "consortia_model_report.md",
            "validation_summary.json",
        ],
        "source_divergence_note": (
            "UC8.1_METAL.png is the authority for Metal optimized groups. "
            "UC-8-1_biorempp_df_20260812_203350.csv is retained as source context "
            "but is not used as the authority for the Metal universe."
        ),
    }
    (OUTPUT_DIR / "validation_summary.json").write_text(
        json.dumps(validation, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    reconciliation_rows = []
    for sample in sorted(METAL_AUTHORITY | raw_uc81_metal):
        reconciliation_rows.append(
            {
                "sample": sample,
                "in_official_metal_image": sample in METAL_AUTHORITY,
                "official_metal_image_group": SAMPLE_TO_METAL_GROUP.get(sample, ""),
                "in_raw_uc81_metal_csv": sample in raw_uc81_metal,
                "raw_uc81_metal_groups": raw_uc81_metal_groups.get(sample, set()),
                "source_status": (
                    "both"
                    if sample in METAL_AUTHORITY and sample in raw_uc81_metal
                    else "image_only"
                    if sample in METAL_AUTHORITY
                    else "raw_only"
                ),
            }
        )
    write_csv(
        OUTPUT_DIR / "uc81_metal_source_reconciliation.csv",
        reconciliation_rows,
        [
            "sample",
            "in_official_metal_image",
            "official_metal_image_group",
            "in_raw_uc81_metal_csv",
            "raw_uc81_metal_groups",
            "source_status",
        ],
    )
    write_report(
        OUTPUT_DIR / "consortia_model_report.md",
        validation,
        selections_by_key,
        uncovered_by_key,
        metrics,
        class_compounds,
    )

    print(f"Output directory: {OUTPUT_DIR}")
    print(json.dumps(validation, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
