# Frequently Asked Questions

Common questions about BioRemPP usage, results, and operations.

---

## General

### What is BioRemPP?

BioRemPP is a web service for functional inference of bioremediation potential from KEGG Orthology (KO) identifiers.

### Do I need an account?

No. BioRemPP is open and does not require login.

### Is BioRemPP free?

Yes. The service is free for scientific and educational use.

It is not usable for commercial product claims without experimental confirmation.

---

## Input and Validation

### What input format is accepted?

A plain text (`.txt`) file:

```text
>Sample1
K00001
K00002
```

Rules:

- sample header starts with `>`
- KO format must be `K#####`
- no blank lines between sample blocks

### What are the default limits?

- max samples: 100
- max KO identifiers: 500,000
- max upload size: 5 MB

These limits can be tuned per deployment.

### Can I use an example file?

Yes.

- Homepage card **Need a KO Input Example? -> Download Example**
- or **Use Example Data** in the upload section

---

## Processing and Job ID

### What is the Job ID generated after processing?

A unique identifier for each processing execution in the format:

`BRP-YYYYMMDD-HHMMSS-XXXXXX`

It lets you restore the same processed result without reprocessing.

### Where can I find and copy my Job ID?

- After processing success (Step 2 feedback)
- In `/results` overview card, with copy action/icon

### How long is a Job ID resumable?

By default, up to 4 hours after processing (TTL-based, configurable by deployment).

---

## Resume by Job ID

### How does Resume Analysis by Job ID work?

From the homepage panel:

1. enter your Job ID
2. click **Resume**
3. app restores payload and redirects to `/results`

### Why does resume require the same browser profile?

For security isolation, resume ownership is bound to the browser context that created the job.

### Why does Resume by Job ID fail?

Common causes:

- invalid Job ID format
- expired TTL window
- different browser profile/context
- temporary block after many failed attempts (rate limit)

If resume is unavailable, reprocess the file to generate a new Job ID.

---

## Results and Interpretation

### What do BioRemPP results represent?

They represent genetic potential inferred from KO presence.

They do not directly prove:

- gene expression
- enzyme activity
- in situ degradation performance

### Are empty database results an error?

Not necessarily. Empty sections can happen when uploaded KOs do not map to that specific database scope.

---

## Data Retention and Privacy

### Is data stored permanently?

No. BioRemPP uses temporary server-side cache for processing and resume.

### What is retained and for how long?

Processed payloads are retained temporarily (default 4h) and purged automatically after expiration.

### Is data shared between users?

No. Resume access is isolated by browser-bound ownership token and validation checks.

---

## Technical Stack and Reliability

### Is resume always backed by Redis?

Not necessarily. Deployments can use different cache backends while keeping the same user-facing behavior.

### What if I close the tab/browser?

You may still recover the run within TTL using Job ID in the same browser profile.

### What browsers are supported?

Recent versions of Chrome, Firefox, Edge, and Safari are recommended.

---

## Citation and Licensing

### How do I cite BioRemPP?

Use the current citation templates in [How to Cite](../about/how-to-cite.md).

### Can I use BioRemPP commercially?

Software and data licenses define permitted reuse, but commercial product claims require independent experimental confirmation.

See [Terms of Use](../about/terms-of-use.md) and [License](../about/license.md).

---

## Downloads

### What can I export?

- integrated database tables (CSV, Excel, JSON)
- use-case-level tables
- chart images (PNG, SVG, JPEG)

### Does export filename include Job ID?

Current naming is timestamp-based. Job ID is shown in the UI for tracking/resume.

---

## Help and Troubleshooting

- [Quickstart](quickstart.md)
- [Input Format](input-format.md)
- [Results Page](../user-guide/results-page.md)
- [Troubleshooting](../user-guide/troubleshooting.md)
- [Contact](../about/contact.md)
