# UC 8.1 Consortium Modeling Report

Generated from `genomas_to_annotate/cons_model` inputs.

## Validation Summary

- DCPIP isolates: `53`
- Annotated BioRemPP samples: `51`
- KO subset samples: `51`
- DCPIP-only isolates excluded from annotation model: `BD130, BD78`
- Official Metal image universe: `17` samples
- Authority note: `UC8.1_METAL.png` is used as the official Metal optimized universe, even though the raw UC 8.1 CSV has a divergent Metal sample set.

## Official Metal Universe

- `Metal_Group_1`: E7, BD48, BD54, BD158
- `Metal_Group_12`: BD163
- `Metal_Group_4`: BD120, BD126, BD127, BD50, BD61, BD132, BD139, BD160, BD162, BG1, BD9
- `Metal_Group_9`: BD117

## UC 8.1 Metal Source Reconciliation

- Raw UC 8.1 Metal CSV samples: `14`
- Samples in image but not raw CSV: `BD120, BD126, BD127, BD132, BD139, BD158, BD162, BD50, BD9, BG1`
- Samples in raw CSV but not image: `AP1BH01-1, BD143, BD145, BD149, BD67, BD69, CB13`
- The strict model uses only the image universe. The relaxed model may add raw-CSV Metal samples only when they close coverage gaps for the target class.

## Aliphatic Consortium Results

### strict_metal

- Representatives: `BD163, BD127, E7, BD117`
- Coverage: `56/59` compounds (94.92%).
- Uncovered compounds: `3`
- Uncovered preview: 2,4-Hexadienal, N,N-Dimethylformamide, N-Nitrosomorpholine

| Order | Representative | Role | Guild Members | New Compounds | Target DCPIP | KO Completeness | Reason |
|---:|---|---|---|---:|---:|---:|---|
| 1 | BD163 | strict_metal_guild | BD163 | 43 | 64.05 | 41.83% | covers 43 new Aliphatic compounds; PL_mean=64.05; class_KO_completeness=41.83%; allowed by official Metal image universe |
| 2 | BD127 | strict_metal_guild | BD127 | 7 | 59.21 | 36.60% | covers 7 new Aliphatic compounds; PL_mean=59.21; class_KO_completeness=36.60%; allowed by official Metal image universe |
| 3 | E7 | strict_metal_guild | BD48, BD54, E7 | 4 | 82.91 | 39.22% | covers 4 new Aliphatic compounds; PL_mean=82.91; class_KO_completeness=39.22%; allowed by official Metal image universe |
| 4 | BD117 | strict_metal_guild | BD117 | 2 | 79.18 | 25.49% | covers 2 new Aliphatic compounds; PL_mean=79.18; class_KO_completeness=25.49%; allowed by official Metal image universe |

### relaxed

- Representatives: `BD163, BD127, E7, BD117, BD145, BD67, CB13`
- Coverage: `59/59` compounds (100.00%).
- Uncovered compounds: `0`

| Order | Representative | Role | Guild Members | New Compounds | Target DCPIP | KO Completeness | Reason |
|---:|---|---|---|---:|---:|---:|---|
| 1 | BD163 | strict_metal_seed | BD163 | 43 | 64.05 | 41.83% | covers 43 new Aliphatic compounds; PL_mean=64.05; class_KO_completeness=41.83% |
| 2 | BD127 | strict_metal_seed | BD127 | 7 | 59.21 | 36.60% | covers 7 new Aliphatic compounds; PL_mean=59.21; class_KO_completeness=36.60% |
| 3 | E7 | strict_metal_seed | BD48, BD54, E7 | 4 | 82.91 | 39.22% | covers 4 new Aliphatic compounds; PL_mean=82.91; class_KO_completeness=39.22% |
| 4 | BD117 | strict_metal_seed | BD117 | 2 | 79.18 | 25.49% | covers 2 new Aliphatic compounds; PL_mean=79.18; class_KO_completeness=25.49% |
| 5 | BD145 | relaxed_addition | BD145 | 1 | 54.17 | 46.41% | covers 1 new Aliphatic compounds; PL_mean=54.17; class_KO_completeness=46.41%; outside official Metal image but present in raw UC 8.1 Metal CSV; added to close strict coverage gap |
| 6 | BD67 | relaxed_addition | BD67 | 1 | 56.50 | 33.99% | covers 1 new Aliphatic compounds; PL_mean=56.50; class_KO_completeness=33.99%; outside official Metal image but present in raw UC 8.1 Metal CSV; added to close strict coverage gap |
| 7 | CB13 | relaxed_addition | CB13 | 1 | 76.58 | 38.56% | covers 1 new Aliphatic compounds; PL_mean=76.58; class_KO_completeness=38.56%; outside official Metal image but present in raw UC 8.1 Metal CSV; added to close strict coverage gap |

## Polyaromatic Consortium Results

### strict_metal

- Representatives: `BD61, BD120, BD158, BD117`
- Coverage: `43/44` compounds (97.73%).
- Uncovered compounds: `1`
- Uncovered preview: Phenytoin

| Order | Representative | Role | Guild Members | New Compounds | Target DCPIP | KO Completeness | Reason |
|---:|---|---|---|---:|---:|---:|---|
| 1 | BD61 | strict_metal_guild | BD61 | 29 | 59.63 | 40.96% | covers 29 new Polyaromatic compounds; PP_mean=59.63; class_KO_completeness=40.96%; allowed by official Metal image universe |
| 2 | BD120 | strict_metal_guild | BD120, BD126 | 7 | 81.81 | 48.19% | covers 7 new Polyaromatic compounds; PP_mean=81.81; class_KO_completeness=48.19%; allowed by official Metal image universe |
| 3 | BD158 | strict_metal_guild | BD158 | 4 | 58.54 | 37.35% | covers 4 new Polyaromatic compounds; PP_mean=58.54; class_KO_completeness=37.35%; allowed by official Metal image universe |
| 4 | BD117 | strict_metal_guild | BD117 | 3 | 76.65 | 22.89% | covers 3 new Polyaromatic compounds; PP_mean=76.65; class_KO_completeness=22.89%; allowed by official Metal image universe |

### relaxed

- Representatives: `BD61, BD120, BD158, BD117, CB13`
- Coverage: `44/44` compounds (100.00%).
- Uncovered compounds: `0`

| Order | Representative | Role | Guild Members | New Compounds | Target DCPIP | KO Completeness | Reason |
|---:|---|---|---|---:|---:|---:|---|
| 1 | BD61 | strict_metal_seed | BD61 | 29 | 59.63 | 40.96% | covers 29 new Polyaromatic compounds; PP_mean=59.63; class_KO_completeness=40.96% |
| 2 | BD120 | strict_metal_seed | BD120, BD126 | 7 | 81.81 | 48.19% | covers 7 new Polyaromatic compounds; PP_mean=81.81; class_KO_completeness=48.19% |
| 3 | BD158 | strict_metal_seed | BD158 | 4 | 58.54 | 37.35% | covers 4 new Polyaromatic compounds; PP_mean=58.54; class_KO_completeness=37.35% |
| 4 | BD117 | strict_metal_seed | BD117 | 3 | 76.65 | 22.89% | covers 3 new Polyaromatic compounds; PP_mean=76.65; class_KO_completeness=22.89% |
| 5 | CB13 | relaxed_addition | CB13 | 1 | 56.10 | 55.42% | covers 1 new Polyaromatic compounds; PP_mean=56.10; class_KO_completeness=55.42%; outside official Metal image but present in raw UC 8.1 Metal CSV; added to close strict coverage gap |

## Interpretation Notes

- `strict_metal` tests the hypothesis that the Metal-optimized guild universe is sufficient for the petroleum target class.
- `relaxed` preserves the strict Metal selections and adds only guilds needed to cover compounds not reached by the strict universe.
- `Aliphatic` selections are interpreted mainly against `PL_mean`; `Polyaromatic` selections are interpreted mainly against `PP_mean`.
- DCPIP values are experimental support, not proof that the annotated compound-specific routes are active in consortium.
- KO, HADEG, KEGG, and toxCSM metrics are annotation-level evidence used to explain breadth, depth, complementarity, and toxicological relevance.

