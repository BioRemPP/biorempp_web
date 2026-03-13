# How to Cite BioRemPP

Use this page to cite the web service and database consistently in academic publications.

---

## Web Service Citation

**APA:**

```text
Lima Silva, D. F., & Fassarella Agnez-Lima, L. (2026). BioRemPP: A Compound-Centric
Web Server for Bioremediation Potential Profiling (1.0.0). Zenodo.
https://doi.org/10.5281/zenodo.18919675
```

??? note "BibTeX"
    ```bibtex
    @software{limasilva2026biorempp_web,
      author    = {Lima Silva, D. F. and Fassarella Agnez-Lima, L.},
      title     = {BioRemPP: A Compound-Centric Web Server for Bioremediation
                   Potential Profiling},
      year      = {2026},
      publisher = {Zenodo},
      version   = {1.0.0},
      doi       = {10.5281/zenodo.18919675},
      url       = {https://doi.org/10.5281/zenodo.18919675}
    }
    ```

---

## Database Citation

**APA:**

```text
Lima Silva, D. F., & Fassarella Agnez-Lima, L. (2025–2026). BioRemPP Database:
A Curated Compound-Centric Resource for Bioremediation Potential Profiling (1.0.0)
[Data set]. Zenodo. https://doi.org/10.5281/zenodo.18905195
```

??? note "BibTeX"
    ```bibtex
    @dataset{limasilva2025biorempp_db,
      author    = {Lima Silva, D. F. and Fassarella Agnez-Lima, L.},
      title     = {BioRemPP Database: A Curated Compound-Centric Resource for
                   Bioremediation Potential Profiling},
      year      = {2025},
      publisher = {Zenodo},
      version   = {1.0.0},
      doi       = {10.5281/zenodo.18905195},
      url       = {https://doi.org/10.5281/zenodo.18905195}
    }
    ```

---

## When to Cite Each Resource

| Use case | Cite web service | Cite database |
|----------|:---:|:---:|
| Functional analysis via the web interface | ✓ | ✓ |
| Using BioRemPP compound–KO annotations | | ✓ |
| Methods section describing the platform | ✓ | ✓ |
| Data availability statement | | ✓ |

---

## Methods Statement (Recommended)

```text
Functional analyses were performed using the BioRemPP Web Service v1.0.0
(Lima Silva & Fassarella Agnez-Lima, 2026), which integrates the BioRemPP Database
v1.0.0 (Lima Silva & Fassarella Agnez-Lima, 2025–2026) with KEGG, HADEG, and toxCSM
reference resources.
```

---

## Key Points

- Cite both web service and database when using the online platform
- Always specify the version used to ensure reproducibility
- Include the Zenodo DOI for each resource
- Specify KEGG release version when relevant (BioRemPP DB v1.0.0 uses KEGG Release Dec,25)
- A peer-reviewed article is under review; this page will be updated upon publication

---

## Citing Integrated Resources

When results rely on specific integrated databases, cite them directly:

**KEGG:**

```text
Kanehisa, M., & Goto, S. (2000). KEGG: Kyoto Encyclopedia of Genes and Genomes.
Nucleic Acids Research, 28(1), 27–30. https://doi.org/10.1093/nar/28.1.27
```

**HADEG:**

```text
Rojas-Vargas, J. A., et al. HADEG: A curated hydrocarbon and aerobic degradation
enzyme and gene database. GitHub. https://github.com/jarojasva/HADEG
```

**toxCSM:**

```text
Nguyen, D. T., et al. toxCSM: comprehensive prediction of small molecule toxicity
profiles. Briefings in Bioinformatics, 23(5), bbac270.
https://doi.org/10.1093/bib/bbac270
```

---

## License and Attribution

| Component | License |
|-----------|---------|
| **Web Service source code** | Apache License 2.0 |
| **BioRemPP Database content** | CC BY 4.0 |

Third-party resources (KEGG, HADEG, toxCSM) retain their own licensing terms.

---

## Contact

For citation questions, see [Contact](contact.md).
