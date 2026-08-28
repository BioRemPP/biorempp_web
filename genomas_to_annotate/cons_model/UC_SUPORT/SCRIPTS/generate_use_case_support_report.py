from __future__ import annotations

import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable


SCRIPT_PATH = Path(__file__).resolve()
CONS_MODEL_DIR = SCRIPT_PATH.parents[2]
REPO_ROOT = CONS_MODEL_DIR.parents[1]
UC_SUPPORT_DIR = CONS_MODEL_DIR / "UC_SUPORT"
RESULTS_DIR = UC_SUPPORT_DIR / "RESULTS"
USE_CASES_DIR = REPO_ROOT / "docs" / "use_cases"
CONSORTIA_RESULTS_DIR = CONS_MODEL_DIR / "CONSORTIA_MODEL_RESULTS"

EXPECTED_UC_COUNT = 56
CENTRAL_REFERENCE_UC = "UC 8.1"


SUPPORT_CLASSIFICATION = {
    "UC 1.1": {
        "tier": "Complementary support",
        "role": "Compara concordancia e contribuicoes unicas entre BioRemPP, HADEG e KEGG, ajudando a qualificar a confiabilidade multi-banco das evidencias usadas nos consorcios.",
        "aliphatic": "Media: reforca se as anotacoes de classe tambem aparecem em bancos complementares.",
        "polyaromatic": "Media: reforca se as anotacoes de classe tambem aparecem em bancos complementares.",
        "metal": "Baixa a media: apoia a interpretacao geral da restricao Metal, mas nao testa diretamente o universo da imagem.",
        "rank": 31,
    },
    "UC 1.4": {
        "tier": "Complementary support",
        "role": "Quantifica a contribuicao relativa de cada amostra ao pool total de KOs, apoiando a distincao entre isolados generalistas e especialistas.",
        "aliphatic": "Media: ajuda a explicar candidatos com grande repertorio funcional.",
        "polyaromatic": "Media: ajuda a explicar candidatos com grande repertorio funcional.",
        "metal": "Media: permite verificar se o universo Metal concentra amostras funcionalmente amplas.",
        "rank": 30,
    },
    "UC 1.5": {
        "tier": "Complementary support",
        "role": "Avalia sobreposicao entre repertorio de compostos das amostras e agencias regulatorias, adicionando relevancia regulatoria a escolha.",
        "aliphatic": "Media: indica se compostos alifaticos cobertos tambem tem relevancia regulatoria.",
        "polyaromatic": "Media: indica se compostos poliaromaticos cobertos tambem tem relevancia regulatoria.",
        "metal": "Media: pode reforcar o peso regulatorio dos compostos Metal.",
        "rank": 27,
    },
    "UC 1.6": {
        "tier": "Complementary support",
        "role": "Mede amplitude de KOs por amostra e agencia regulatoria, conectando potencial funcional a escopos regulatorios.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 28,
    },
    "UC 2.1": {
        "tier": "Strong support",
        "role": "Compara riqueza funcional dos candidatos entre BioRemPP, HADEG e KEGG; bom reforco para escolher representantes com suporte multi-banco.",
        "aliphatic": "Alta: qualifica candidatos do consorcio alifatico por riqueza funcional.",
        "polyaromatic": "Alta: qualifica candidatos do consorcio poliaromatico por riqueza funcional.",
        "metal": "Media: testa se candidatos da imagem Metal sao funcionalmente ricos em bancos distintos.",
        "rank": 17,
    },
    "UC 2.2": {
        "tier": "Strong support",
        "role": "Ranqueia amostras por diversidade quimica, reforcando se candidatos cobrem amplo espectro de compostos.",
        "aliphatic": "Alta: contextualiza cobertura ampla para compostos alifaticos.",
        "polyaromatic": "Alta: contextualiza cobertura ampla para compostos poliaromaticos.",
        "metal": "Media: avalia se universo Metal contem candidatos quimicamente diversos.",
        "rank": 18,
    },
    "UC 2.3": {
        "tier": "Complementary support",
        "role": "Identifica compostos mais compartilhados por classe, ajudando a separar compostos comuns de compostos que exigem membros especificos.",
        "aliphatic": "Alta.",
        "polyaromatic": "Alta.",
        "metal": "Baixa.",
        "rank": 25,
    },
    "UC 2.4": {
        "tier": "Complementary support",
        "role": "Ranqueia compostos por diversidade de genes, apoiando a priorizacao de compostos com maior complexidade funcional.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Baixa.",
        "rank": 26,
    },
    "UC 2.5": {
        "tier": "Complementary support",
        "role": "Fornece estatisticas descritivas de KOs por banco, util para auditar se os candidatos estao acima ou abaixo da distribuicao geral.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 29,
    },
    "UC 3.1": {
        "tier": "Complementary support",
        "role": "PCA por perfil funcional, util para ver se candidatos selecionados ocupam espacos funcionais distintos.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 24,
    },
    "UC 3.2": {
        "tier": "Complementary support",
        "role": "PCA por perfil quimico, util para avaliar separacao dos candidatos conforme compostos co-anotados.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 23,
    },
    "UC 3.3": {
        "tier": "Complementary support",
        "role": "Clustering hierarquico por perfil KO, reforcando analise de redundancia ou distancia funcional entre membros.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 22,
    },
    "UC 3.4": {
        "tier": "Strong support",
        "role": "Mede similaridade entre amostras por KOs, diretamente util para evitar consorcios redundantes demais.",
        "aliphatic": "Alta: valida complementaridade funcional dos membros.",
        "polyaromatic": "Alta: valida complementaridade funcional dos membros.",
        "metal": "Alta: compara membros do universo Metal oficial.",
        "rank": 9,
    },
    "UC 3.5": {
        "tier": "Strong support",
        "role": "Mede similaridade entre amostras por compostos, diretamente alinhado a perfis de cobertura do UC 8.1.",
        "aliphatic": "Alta: valida se membros alifaticos cobrem perfis quimicos distintos.",
        "polyaromatic": "Alta: valida se membros poliaromaticos cobrem perfis quimicos distintos.",
        "metal": "Media: compara diversidade quimica dentro/fora do universo Metal.",
        "rank": 10,
    },
    "UC 4.1": {
        "tier": "Complementary support",
        "role": "Perfila KOs por pathways KEGG para cada amostra, ajudando a interpretar profundidade funcional dos candidatos.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 32,
    },
    "UC 4.2": {
        "tier": "Complementary support",
        "role": "Ranqueia amostras por riqueza em pathway KEGG especifico, util quando um pathway alvo for priorizado.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Baixa a media.",
        "rank": 33,
    },
    "UC 4.3": {
        "tier": "Complementary support",
        "role": "Mostra footprint funcional de um pathway entre amostras, apoiando comparacoes pathway-level.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Baixa a media.",
        "rank": 34,
    },
    "UC 4.4": {
        "tier": "Complementary support",
        "role": "Mostra fingerprint de pathways por amostra, util para explicar a especializacao de membros selecionados.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 35,
    },
    "UC 4.5": {
        "tier": "Complementary support",
        "role": "Mapa de presenca de genes por pathway KEGG, util para validar genes especificos em candidatos.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Baixa a media.",
        "rank": 36,
    },
    "UC 4.6": {
        "tier": "Strong support",
        "role": "Avalia potencial funcional por composto e classe, conectando diretamente candidatos aos compostos de Aliphatic/Polyaromatic.",
        "aliphatic": "Alta: evidencia KO por composto alifatico.",
        "polyaromatic": "Alta: evidencia KO por composto poliaromatico.",
        "metal": "Media: pode comparar compostos Metal como restricao secundaria.",
        "rank": 11,
    },
    "UC 4.7": {
        "tier": "Complementary support",
        "role": "Explora associacoes gene-composto e quais amostras carregam essas co-anotacoes.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 37,
    },
    "UC 4.8": {
        "tier": "Complementary support",
        "role": "Inventario de genes por amostra, util para investigacao manual de genes de interesse nos candidatos.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 38,
    },
    "UC 4.9": {
        "tier": "Strong support",
        "role": "Perfil de atividades enzimaticas por amostra; reforca plausibilidade funcional dos membros escolhidos.",
        "aliphatic": "Alta: verifica atividades enzimas associadas a hidrocarbonetos alifaticos.",
        "polyaromatic": "Alta: verifica atividades enzimas associadas a compostos aromaticos/poliaromaticos.",
        "metal": "Media.",
        "rank": 12,
    },
    "UC 4.10": {
        "tier": "Strong support",
        "role": "Diversity de atividades enzimaticas por amostra, apoiando escolha de representantes com maior variedade funcional.",
        "aliphatic": "Alta.",
        "polyaromatic": "Alta.",
        "metal": "Media.",
        "rank": 13,
    },
    "UC 4.11": {
        "tier": "Complementary support",
        "role": "Hierarquia da diversidade genetica em HADEG, util para contextualizar quais classes/pathways sao mais diversos.",
        "aliphatic": "Media se HADEG Alkanes for alvo.",
        "polyaromatic": "Media se HADEG Aromatics for alvo.",
        "metal": "Baixa.",
        "rank": 39,
    },
    "UC 4.12": {
        "tier": "Complementary support",
        "role": "Distribuicao de pathways HADEG por amostra, util para detalhar membros selecionados individualmente.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 40,
    },
    "UC 4.13": {
        "tier": "Complementary support",
        "role": "Perfil genetico por classe de degradacao HADEG, especialmente util para Alkanes/Aromatics.",
        "aliphatic": "Alta se mapeado para Alkanes.",
        "polyaromatic": "Alta se mapeado para Aromatics.",
        "metal": "Baixa.",
        "rank": 21,
    },
    "UC 5.1": {
        "tier": "Strong support",
        "role": "Matriz amostra x classe quimica, diretamente util para mostrar associacao dos candidatos com Aliphatic, Polyaromatic e Metal.",
        "aliphatic": "Alta.",
        "polyaromatic": "Alta.",
        "metal": "Alta.",
        "rank": 14,
    },
    "UC 5.2": {
        "tier": "Strong support",
        "role": "Similaridade por perfil quimico, alternativa/confirmacao ao UC 3.5 para avaliar redundancia quimica.",
        "aliphatic": "Alta.",
        "polyaromatic": "Alta.",
        "metal": "Media.",
        "rank": 15,
    },
    "UC 5.3": {
        "tier": "Complementary support",
        "role": "Relevancia regulatoria por amostra, adicionando contexto de prioridade ambiental aos candidatos.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Alta se regulacoes incluem metais relevantes.",
        "rank": 41,
    },
    "UC 5.4": {
        "tier": "Complementary support",
        "role": "Rede gene-composto para identificar hubs funcionais associados aos compostos cobertos.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 42,
    },
    "UC 5.5": {
        "tier": "Context only",
        "role": "Rede gene-gene baseada em compostos compartilhados; mais util para mecanismo geral do que para decidir membros do consorcio.",
        "aliphatic": "Baixa a media.",
        "polyaromatic": "Baixa a media.",
        "metal": "Baixa.",
        "rank": 50,
    },
    "UC 5.6": {
        "tier": "Context only",
        "role": "Rede composto-composto baseada em genes compartilhados; ajuda a entender estrutura quimica, mas nao seleciona isolados diretamente.",
        "aliphatic": "Baixa a media.",
        "polyaromatic": "Baixa a media.",
        "metal": "Baixa.",
        "rank": 51,
    },
    "UC 6.1": {
        "tier": "Complementary support",
        "role": "Fluxo agencia -> amostra -> gene -> composto, conectando candidatos a contexto regulatorio e molecular.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 43,
    },
    "UC 6.2": {
        "tier": "Complementary support",
        "role": "Fluxo amostra -> classe -> atividade enzimatica, alinhado ao racional funcional dos consorcios.",
        "aliphatic": "Alta.",
        "polyaromatic": "Alta.",
        "metal": "Media.",
        "rank": 20,
    },
    "UC 6.3": {
        "tier": "Complementary support",
        "role": "Hierarquia quimica por classe, composto, amostra e gene; boa sintese para explicar contribuicoes por classe.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 44,
    },
    "UC 6.4": {
        "tier": "Complementary support",
        "role": "Hierarquia enzimatica por atividade, classe e genes; reforca quais funcoes sustentam a cobertura.",
        "aliphatic": "Media.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 45,
    },
    "UC 6.5": {
        "tier": "Complementary support",
        "role": "Hierarquia quimico-enzimatica por classe, atividade e genes; bom suporte mecanistico agregado.",
        "aliphatic": "Alta.",
        "polyaromatic": "Alta.",
        "metal": "Media.",
        "rank": 19,
    },
    "UC 7.1": {
        "tier": "Complementary support",
        "role": "Perfil toxicologico dos compostos, util para explicar prioridade dos compostos cobertos.",
        "aliphatic": "Media.",
        "polyaromatic": "Alta.",
        "metal": "Alta.",
        "rank": 46,
    },
    "UC 7.2": {
        "tier": "Complementary support",
        "role": "Concordancia entre risco predito e escopo regulatorio, adicionando peso ambiental aos alvos.",
        "aliphatic": "Media.",
        "polyaromatic": "Alta.",
        "metal": "Alta.",
        "rank": 47,
    },
    "UC 7.3": {
        "tier": "Strong support",
        "role": "Mapeia resposta genetica a compostos de alto risco, priorizando candidatos com KOs ligados a ameaças toxicologicas.",
        "aliphatic": "Media a alta.",
        "polyaromatic": "Alta.",
        "metal": "Alta.",
        "rank": 16,
    },
    "UC 7.4": {
        "tier": "Context only",
        "role": "Distribuicao de scores toxicológicos por endpoint; informa risco geral dos compostos, mas sem foco em amostras.",
        "aliphatic": "Baixa.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 52,
    },
    "UC 7.5": {
        "tier": "Context only",
        "role": "Distribuicoes probabilisticas de scores toxicológicos; util para contexto de risco, pouco decisivo para membros.",
        "aliphatic": "Baixa.",
        "polyaromatic": "Media.",
        "metal": "Media.",
        "rank": 53,
    },
    "UC 7.6": {
        "tier": "Strong support",
        "role": "Avalia amplitude de mitigacao de risco por amostra, diretamente util para validar candidatos contra compostos de alto risco.",
        "aliphatic": "Media a alta.",
        "polyaromatic": "Alta.",
        "metal": "Alta.",
        "rank": 7,
    },
    "UC 7.7": {
        "tier": "Strong support",
        "role": "Avalia profundidade de mitigacao de risco por KOs, complementando cobertura com intensidade anotacional.",
        "aliphatic": "Media a alta.",
        "polyaromatic": "Alta.",
        "metal": "Alta.",
        "rank": 8,
    },
    "UC 8.1": {
        "tier": "Central reference",
        "role": "Caso central ja usado para modelar cobertura minima e guildas funcionais dos consorcios.",
        "aliphatic": "Referencia central.",
        "polyaromatic": "Referencia central.",
        "metal": "Referencia central para restricao pela imagem UC8.1_METAL.png.",
        "rank": 0,
    },
    "UC 8.2": {
        "tier": "Strong support",
        "role": "Mede completude KO por classe quimica, validando profundidade funcional para Aliphatic e Polyaromatic.",
        "aliphatic": "Alta: mede completude da classe.",
        "polyaromatic": "Alta: mede completude da classe.",
        "metal": "Alta: pode confirmar completude dos membros Metal.",
        "rank": 1,
    },
    "UC 8.3": {
        "tier": "Strong support",
        "role": "Mede completude KO por composto, validando compostos cobertos por cada consorcio.",
        "aliphatic": "Alta: identifica lacunas por composto alifatico.",
        "polyaromatic": "Alta: identifica lacunas por composto poliaromatico.",
        "metal": "Media a alta: aplica-se aos compostos Metal da restricao.",
        "rank": 2,
    },
    "UC 8.4": {
        "tier": "Strong support",
        "role": "Mede completude por pathways HADEG, reforcando suporte de degradacao especializado.",
        "aliphatic": "Alta quando mapeado para Alkanes.",
        "polyaromatic": "Alta quando mapeado para Aromatics.",
        "metal": "Media.",
        "rank": 3,
    },
    "UC 8.5": {
        "tier": "Strong support",
        "role": "Mede completude por pathways KEGG, reforcando consistencia metabolica em banco externo.",
        "aliphatic": "Alta.",
        "polyaromatic": "Alta.",
        "metal": "Media.",
        "rank": 4,
    },
    "UC 8.6": {
        "tier": "Strong support",
        "role": "Analisa cobertura e complementaridade de KOs por pathway, diretamente alinhada a desenho de consorcios.",
        "aliphatic": "Alta: valida complementaridade para pathways de hidrocarbonetos.",
        "polyaromatic": "Alta: valida complementaridade para pathways aromaticos.",
        "metal": "Media a alta.",
        "rank": 5,
    },
    "UC 8.7": {
        "tier": "Strong support",
        "role": "Quantifica intersecoes, KOs compartilhados e KOs unicos entre candidatos, validando redundancia e complementaridade.",
        "aliphatic": "Alta.",
        "polyaromatic": "Alta.",
        "metal": "Alta.",
        "rank": 6,
    },
}


DEFAULT_BY_MODULE = {
    "module1": ("Context only", "Contexto regulatorio e comparativo geral.", 60),
    "module2": ("Complementary support", "Exploracao de riqueza funcional/quimica.", 40),
    "module3": ("Complementary support", "Estrutura, similaridade e co-ocorrencia.", 40),
    "module4": ("Complementary support", "Perfil funcional e genetico.", 40),
    "module5": ("Complementary support", "Interacoes entre amostras, genes e compostos.", 45),
    "module6": ("Complementary support", "Analise hierarquica e fluxos funcionais.", 45),
    "module7": ("Complementary support", "Avaliacao toxicologica.", 45),
    "module8": ("Strong support", "Montagem e validacao de consorcios.", 20),
}


def natural_key(path: Path) -> list[object]:
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", str(path))]


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$", text, flags=re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    next_heading = re.search(r"^## ", text[start:], flags=re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def extract_question(scientific_section: str) -> str:
    match = re.search(
        r"\*\*Question:\*\*\s*(.*?)(?:\n\s*\n|$)",
        scientific_section,
        flags=re.DOTALL,
    )
    if match:
        return normalize_space(match.group(1))
    return normalize_space(scientific_section.splitlines()[0]) if scientific_section else ""


def extract_primary_inputs(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("**Primary inputs:**"):
            return normalize_space(line.replace("**Primary inputs:**", ""))
    return ""


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return normalize_space(line.lstrip("#").strip())
    return fallback


def uc_id_from_path(path: Path) -> str:
    match = re.search(r"uc_(\d+)\.(\d+)", path.stem)
    if not match:
        return path.stem.upper().replace("_", " ")
    return f"UC {match.group(1)}.{match.group(2)}"


def module_from_path(path: Path) -> str:
    return path.parent.name.replace("module", "Module ")


def clean_data_inputs(data_section: str, limit: int = 900) -> str:
    cleaned = normalize_space(re.sub(r"---.*$", "", data_section, flags=re.DOTALL))
    return cleaned[:limit].rstrip()


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_consortia_context() -> dict[str, object]:
    representatives = load_csv(CONSORTIA_RESULTS_DIR / "consortium_representatives.csv")
    validation_path = CONSORTIA_RESULTS_DIR / "validation_summary.json"
    validation = {}
    if validation_path.exists():
        validation = json.loads(validation_path.read_text(encoding="utf-8"))

    by_target: dict[str, dict[str, list[str]]] = {}
    for row in representatives:
        target = row.get("target_class", "")
        version = row.get("model_version", "")
        sample = row.get("representative_sample", "")
        if not target or not version or not sample:
            continue
        by_target.setdefault(target, {}).setdefault(version, []).append(sample)

    return {
        "validation": validation,
        "representatives": representatives,
        "by_target": by_target,
    }


def classify_uc(uc_id: str, module_name: str) -> dict[str, object]:
    if uc_id in SUPPORT_CLASSIFICATION:
        item = SUPPORT_CLASSIFICATION[uc_id]
    else:
        module_key = module_name.lower().replace(" ", "")
        tier, role, rank = DEFAULT_BY_MODULE.get(
            module_key,
            ("Context only", "Contexto metodologico geral.", 70),
        )
        item = {
            "tier": tier,
            "role": role,
            "aliphatic": "Baixa a media.",
            "polyaromatic": "Baixa a media.",
            "metal": "Baixa.",
            "rank": rank,
        }

    recommended = item["tier"] in {"Strong support", "Complementary support"}
    if item["tier"] == "Central reference":
        recommended = False

    return {
        "support_tier": item["tier"],
        "decision_support_role": item["role"],
        "relevance_to_aliphatic": item["aliphatic"],
        "relevance_to_polyaromatic": item["polyaromatic"],
        "relevance_to_metal_constraint": item["metal"],
        "recommended_for_report": recommended,
        "priority_rank": item["rank"],
    }


def collect_use_cases() -> tuple[list[dict[str, object]], list[dict[str, str]]]:
    rows: list[dict[str, object]] = []
    missing_sections: list[dict[str, str]] = []
    paths = sorted(USE_CASES_DIR.glob("module*/uc_*.md"), key=natural_key)

    for path in paths:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        uc_id = uc_id_from_path(path)
        module_name = module_from_path(path)
        title = extract_title(text, fallback=uc_id)
        scientific_section = section(text, "Scientific Question and Rationale")
        data_section = section(text, "Data and Inputs")
        primary_inputs = extract_primary_inputs(text)
        question = extract_question(scientific_section)
        classification = classify_uc(uc_id, module_name)

        if not scientific_section:
            missing_sections.append({"use_case": uc_id, "missing_section": "Scientific Question and Rationale"})
        if not data_section:
            missing_sections.append({"use_case": uc_id, "missing_section": "Data and Inputs"})

        row: dict[str, object] = {
            "use_case": uc_id,
            "module": module_name,
            "title": title,
            "scientific_question": question,
            "primary_inputs": primary_inputs,
            "data_inputs_summary": clean_data_inputs(data_section),
            "source_path": str(path.relative_to(REPO_ROOT)),
        }
        row.update(classification)
        rows.append(row)

    rows.sort(key=lambda row: (int(row["priority_rank"]), str(row["use_case"])))
    return rows, missing_sections


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: csv_value(row.get(field)) for field in fieldnames})


def csv_value(value: object) -> object:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (list, tuple, set)):
        return ";".join(str(item) for item in sorted(value))
    return value


def rows_by_tier(rows: Iterable[dict[str, object]], tier: str) -> list[dict[str, object]]:
    return [row for row in rows if row["support_tier"] == tier]


def markdown_table(rows: list[dict[str, object]], columns: list[tuple[str, str]]) -> list[str]:
    output = []
    output.append("| " + " | ".join(label for label, _ in columns) + " |")
    output.append("|" + "|".join("---" for _ in columns) + "|")
    for row in rows:
        values = [str(row.get(key, "")).replace("\n", " ").replace("|", "\\|") for _, key in columns]
        output.append("| " + " | ".join(values) + " |")
    return output


def write_report(
    path: Path,
    rows: list[dict[str, object]],
    missing_sections: list[dict[str, str]],
    consortia_context: dict[str, object],
) -> None:
    validation = consortia_context.get("validation", {})
    by_target = consortia_context.get("by_target", {})
    strong = rows_by_tier(rows, "Strong support")
    complementary = rows_by_tier(rows, "Complementary support")
    context = rows_by_tier(rows, "Context only")
    not_recommended = rows_by_tier(rows, "Not recommended")
    central = rows_by_tier(rows, "Central reference")

    lines: list[str] = []
    lines.append("# Report de suporte por casos de uso")
    lines.append("")
    lines.append("## Resumo executivo")
    lines.append("")
    lines.append(
        "Este report identifica quais casos de uso em `docs/use_cases` podem reforcar a decisao dos consorcios "
        "`Aliphatic` e `Polyaromatic` modelados a partir do UC 8.1."
    )
    lines.append("")
    lines.extend(
        [
            f"- Casos de uso inspecionados: `{len(rows)}`.",
            f"- Casos `Strong support`: `{len(strong)}`.",
            f"- Casos `Complementary support`: `{len(complementary)}`.",
            f"- Casos `Context only`: `{len(context)}`.",
            f"- Casos `Not recommended`: `{len(not_recommended)}`.",
            f"- Referencia central: `{CENTRAL_REFERENCE_UC}`.",
        ]
    )
    if validation:
        lines.extend(
            [
                f"- DCPIP isolates na modelagem anterior: `{validation.get('dcpip_isolates', 'NA')}`.",
                f"- Amostras anotadas na modelagem anterior: `{validation.get('annotated_samples', 'NA')}`.",
                f"- Universo oficial Metal da imagem: `{validation.get('metal_authority_samples', 'NA')}` amostras.",
            ]
        )
    lines.append("")
    lines.append("## Contexto dos consorcios")
    lines.append("")
    if by_target:
        for target, versions in by_target.items():
            lines.append(f"- `{target}`:")
            for version, samples in versions.items():
                lines.append(f"  - `{version}`: {', '.join(samples)}")
    else:
        lines.append("- Contexto de consorcios nao encontrado em `CONSORTIA_MODEL_RESULTS`.")
    lines.append("")
    lines.append("## Ranking dos UCs recomendados")
    lines.append("")
    recommended = [row for row in rows if row["recommended_for_report"]]
    lines.extend(
        markdown_table(
            recommended,
            [
                ("UC", "use_case"),
                ("Tier", "support_tier"),
                ("Titulo", "title"),
                ("Papel na decisao", "decision_support_role"),
            ],
        )
    )
    lines.append("")

    lines.append("## Referencia central")
    lines.append("")
    for row in central:
        append_uc_detail(lines, row)

    lines.append("## Strong support")
    lines.append("")
    for row in strong:
        append_uc_detail(lines, row)

    lines.append("## Complementary support")
    lines.append("")
    for row in complementary:
        append_uc_detail(lines, row)

    lines.append("## Context only")
    lines.append("")
    if context:
        lines.extend(
            markdown_table(
                context,
                [
                    ("UC", "use_case"),
                    ("Titulo", "title"),
                    ("Papel", "decision_support_role"),
                ],
            )
        )
    else:
        lines.append("Nenhum UC classificado como `Context only`.")
    lines.append("")

    lines.append("## Not recommended")
    lines.append("")
    if not_recommended:
        lines.extend(
            markdown_table(
                not_recommended,
                [
                    ("UC", "use_case"),
                    ("Titulo", "title"),
                    ("Papel", "decision_support_role"),
                ],
            )
        )
    else:
        lines.append("Nenhum UC classificado como `Not recommended` nesta rodada.")
    lines.append("")

    lines.append("## Limitacoes")
    lines.append("")
    lines.extend(
        [
            "- Esta etapa classifica e documenta UCs de suporte; ela nao recalcula todos os graficos ou metricas originais.",
            "- A classificacao e metodologica e deve ser usada como roteiro para analises subsequentes por UC.",
            "- `UC 8.1` foi mantido como referencia central porque ja fundamenta a modelagem dos consorcios.",
            "- A interpretacao experimental DCPIP deve permanecer complementar as evidencias anotacionais.",
        ]
    )
    lines.append("")

    lines.append("## Validacao da extracao")
    lines.append("")
    if missing_sections:
        lines.append("Secoes ausentes detectadas:")
        for item in missing_sections:
            lines.append(f"- `{item['use_case']}`: `{item['missing_section']}`")
    else:
        lines.append("Todos os UCs inspecionados possuem as secoes esperadas de pergunta cientifica e dados de entrada.")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_uc_detail(lines: list[str], row: dict[str, object]) -> None:
    lines.append(f"### {row['use_case']} - {row['title']}")
    lines.append("")
    lines.append(f"- **Tier:** `{row['support_tier']}`")
    lines.append(f"- **Pergunta cientifica:** {row['scientific_question'] or 'Nao localizada.'}")
    lines.append(f"- **Primary inputs:** {row['primary_inputs'] or 'Nao localizado.'}")
    lines.append(f"- **Data inputs:** {row['data_inputs_summary'] or 'Nao localizado.'}")
    lines.append(f"- **Como reforca a decisao:** {row['decision_support_role']}")
    lines.append(f"- **Relevancia para Aliphatic:** {row['relevance_to_aliphatic']}")
    lines.append(f"- **Relevancia para Polyaromatic:** {row['relevance_to_polyaromatic']}")
    lines.append(f"- **Relevancia para Metal:** {row['relevance_to_metal_constraint']}")
    lines.append("- **Limitacao interpretativa:** fornece suporte anotacional/metodologico; nao substitui validacao experimental.")
    lines.append("")


def write_validation(
    path: Path,
    rows: list[dict[str, object]],
    missing_sections: list[dict[str, str]],
    generated_files: list[str],
) -> None:
    docs_modified_check = {
        "docs_use_cases_written_by_script": False,
        "note": "The script reads docs/use_cases and writes only under UC_SUPORT/RESULTS.",
    }
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "use_cases_inspected": len(rows),
        "expected_use_cases": EXPECTED_UC_COUNT,
        "expected_count_match": len(rows) == EXPECTED_UC_COUNT,
        "central_reference_uc": CENTRAL_REFERENCE_UC,
        "tiers": {
            tier: len(rows_by_tier(rows, tier))
            for tier in [
                "Central reference",
                "Strong support",
                "Complementary support",
                "Context only",
                "Not recommended",
            ]
        },
        "missing_sections": missing_sections,
        "generated_files": generated_files,
        "docs_modified_check": docs_modified_check,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rows, missing_sections = collect_use_cases()
    consortia_context = load_consortia_context()

    matrix_path = RESULTS_DIR / "use_case_support_matrix.csv"
    report_path = RESULTS_DIR / "use_case_support_report.md"
    validation_path = RESULTS_DIR / "use_case_support_validation.json"

    matrix_fields = [
        "use_case",
        "module",
        "title",
        "scientific_question",
        "primary_inputs",
        "data_inputs_summary",
        "support_tier",
        "decision_support_role",
        "relevance_to_aliphatic",
        "relevance_to_polyaromatic",
        "relevance_to_metal_constraint",
        "recommended_for_report",
        "priority_rank",
        "source_path",
    ]
    write_csv(matrix_path, rows, matrix_fields)
    write_report(report_path, rows, missing_sections, consortia_context)
    write_validation(
        validation_path,
        rows,
        missing_sections,
        [
            str(matrix_path.relative_to(UC_SUPPORT_DIR)),
            str(report_path.relative_to(UC_SUPPORT_DIR)),
            str(validation_path.relative_to(UC_SUPPORT_DIR)),
        ],
    )

    print(f"use_cases_inspected={len(rows)}")
    print(f"expected_count_match={len(rows) == EXPECTED_UC_COUNT}")
    print(f"missing_sections={len(missing_sections)}")
    print(f"matrix={matrix_path}")
    print(f"report={report_path}")
    print(f"validation={validation_path}")


if __name__ == "__main__":
    main()
