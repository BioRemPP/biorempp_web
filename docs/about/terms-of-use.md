# Terms of Use

By using the BioRemPP web service, you acknowledge and agree to the following terms. Please read carefully before proceeding.

---

## 1. Scope and Purpose

BioRemPP (Bioremediation Potential Profile) is a **scientific research tool** designed exclusively for exploratory functional analysis of bioremediation-related data. The platform integrates curated databases (BioRemPP, KEGG, HADEG, toxCSM) with regulatory frameworks to support hypothesis generation and methodological development in environmental bioinformatics.

BioRemPP is an **academic web service** provided on a best-effort basis without performance guarantees or service level agreements.

---

## 2. Intended Use

### Permitted Uses

- Academic research and hypothesis generation
- Educational purposes and training
- Exploratory analysis of functional genomic data
- Methodological development and validation

### Prohibited Uses

!!! danger "Important Restriction"
    BioRemPP outputs must **NOT** be used as the sole basis for:

    - Clinical diagnostics or medical decisions
    - Regulatory submissions or compliance
    - Environmental remediation decisions without independent validation
    - Commercial product claims without experimental confirmation

---

## 3. User Responsibilities

Users are solely responsible for:

- **Data ownership and legitimacy:** Ensuring uploaded data does not violate third-party rights or confidentiality agreements.
- **Scientific interpretation:** Results must be critically evaluated within appropriate biological and methodological context.
- **Citation and attribution:** Properly citing BioRemPP web service and database in publications and reports (see [How to Cite](how-to-cite.md)).
- **Compliance with third-party licenses:** Respecting KEGG, HADEG, and toxCSM licensing terms.

---

## 4. Data Submission and Privacy

BioRemPP operates under a **privacy-by-design philosophy**:

- **No user accounts:** The service requires no authentication or registration.
- **No persistent storage:** Uploaded data is processed in-memory only during the active session.
- **Session-based processing:** Data and results are automatically deleted when the browser session ends or after 6 hours of inactivity.
- **Minimal technical logging:** Server logs contain only IP addresses (rate limiting), user-agent strings (compatibility), and error messages (debugging). **No biological data is logged.**

---

## 5. Availability and Service Limitations

BioRemPP is provided as a **best-effort service** without guaranteed uptime or performance commitments:

- **No Service Level Agreement (SLA):** Availability, response time, and throughput are not guaranteed.
- **Maintenance windows:** Service may be temporarily unavailable for updates, database refreshes, or infrastructure maintenance.
- **Resource constraints:** Upload limits (100 samples, 500K KO entries, 5 MB file size) are enforced to ensure fair access.

!!! info "Support and Custom SLA"
    For institutional deployments, high-throughput analyses, or customized service agreements, contact [biorempp@gmail.com](mailto:biorempp@gmail.com) with a detailed description of your requirements. Response time: up to 5 business days.

---

## 6. Licensing and Intellectual Property

### BioRemPP Components

- **Web Service Source Code:** [Apache License 2.0](https://opensource.org/licenses/Apache-2.0) — Commercial and private use permitted with attribution.
- **BioRemPP Database Content:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — Free to share and adapt with proper citation.

### Third-Party Resources

- **KEGG:** Academic use free; commercial use requires license ([KEGG License](https://www.kegg.jp/kegg/legal.html)).
- **HADEG:** Open access ([GitHub](https://github.com/jarojasva/HADEG)).
- **toxCSM:** Open access for academic use ([toxCSM License](https://biosig.lab.uq.edu.au/toxcsm/)).

!!! warning "User Compliance Obligation"
    Users are responsible for ensuring their use complies with all applicable third-party licenses.

---

## 7. Citation and Attribution

Use of BioRemPP in academic publications, reports, or presentations **requires proper citation** of both the web service and the BioRemPP database.

Please refer to the [How to Cite](how-to-cite.md) page for detailed citation guidelines, including provisional formats (pending DOI assignment via Zenodo) and recommended language for Methods sections.

---

## 8. Disclaimer of Warranty

!!! danger "AS IS Provision"
    BioRemPP is provided **"as is" and "as available"** without warranty of any kind, either express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, or non-infringement.

    The authors and contributors make no representations regarding the accuracy, reliability, completeness, or timeliness of the service, database content, or analytical results.

---

## 9. Limitation of Liability

The authors, contributors, and hosting institutions **shall not be liable** for any direct, indirect, incidental, special, consequential, or exemplary damages arising from:

- Use or inability to use the service
- Errors, omissions, or inaccuracies in results or database content
- Decisions or actions taken based on service outputs
- Data loss or service interruptions
- Reliance on third-party database annotations (KEGG, HADEG, toxCSM)

**User Acknowledgment:** By using BioRemPP, you acknowledge that interpretation and application of results are solely your responsibility.

---

## 10. Modifications to the Terms

We reserve the right to modify these Terms of Use at any time. Changes will be posted on this page with an updated revision date.

**Continued use** of the service after modifications constitutes acceptance of the updated terms. Users are encouraged to review this page periodically.

---

## 11. Contact Information

For questions, clarifications, or institutional support requests regarding these Terms of Use:

- **Email:** [biorempp@gmail.com](mailto:biorempp@gmail.com)
- **GitHub Repository:** [github.com/biorempp/biorempp_web](https://github.com/biorempp/biorempp_web)
- **Response Time:** Up to 5 business days

---

!!! success "Thank You"
    Thank you for using BioRemPP responsibly. Your adherence to these terms ensures the continued availability of this resource for the scientific community.
