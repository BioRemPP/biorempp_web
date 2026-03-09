# Troubleshooting Guide

This page provides structured technical guidance for resolving common issues encountered while using BioRemPP.

---

## Purpose of Troubleshooting

This guide addresses **technical errors**, **performance issues**, and **rendering problems** that may occur during file upload, analysis execution, or result visualization.

**Scope:**

- Validation and parsing errors
- Processing timeouts or performance degradation
- Visualization rendering failures
- Download-related issues

**Out of scope:**

- Input format specification (see [Input Format](../getting-started/input-format.md))
- Scientific interpretation of results (see [Interpretation](interpretation.md))
- General usage questions (see [FAQ](../getting-started/faq.md))

---

## Common Processing Errors

### Error: File Must Start with Sample Identifier

**Symptom:**

`ValidationError: File must begin with a sample identifier (>SampleName)`

**Cause:**

The first line of the file is not a sample header starting with `>`.

**Resolution:**

1. Open file in plain text editor
2. Verify first line begins with `>` followed immediately by sample name
3. Move any comments, headers, or metadata to a separate file
4. Ensure no blank lines precede first sample identifier

**Correct first line:**

```
>Sample1
```

**Incorrect first lines:**

```
# Sample annotations
>Sample1
```

```

>Sample1
```

---

### Error: Invalid KO Format

**Symptom:**

`ValidationError: KO identifier does not match K##### pattern`

**Cause:**

KO identifiers do not conform to the required `K` + 5 digits pattern.

**Common formatting errors:**

- **Prefix included:** `ko:K00001` (should be `K00001`)
- **Lowercase:** `k00001` (should be `K00001`)
- **Insufficient digits:** `K001` (should be `K00001`)
- **Excessive digits:** `K000001` (should be `K00001`)
- **Missing K:** `00001` (should be `K00001`)

**Resolution:**

1. Search file for all lines not matching `>` or `K#####` pattern
2. Use regex find-and-replace to fix prefix issues:
    - Find: `ko:K(\d{5})` → Replace: `K$1`
    - Find: `k(\d{5})` → Replace: `K$1`
3. Verify digit count for all KO identifiers
4. Re-annotate sequences if KOs are fundamentally incorrect

---

### Error: Empty Sample Detected

**Symptom:**

`ValidationError: Sample 'SampleName' has no KO identifiers`

**Cause:**

A sample header (`>SampleName`) is followed immediately by another sample header or end-of-file without any KO identifiers.

**Resolution:**

1. Identify empty samples using:
    - Manual inspection for consecutive `>` lines
    - Grep search: `grep -A 1 '^>' file.txt | grep '^>'`
2. Remove empty sample headers or add at least one valid KO identifier per sample
3. Verify sample has associated functional annotations in original annotation output

---

### Error: File Encoding Not Supported

**Symptom:**

`EncodingError: File encoding could not be determined`

**Cause:**

File uses encoding other than UTF-8 or Latin-1, or contains binary data.

**Resolution:**

1. **Re-save as UTF-8:**
    - Open file in text editor (Notepad++, VS Code, Sublime)
    - File → Save As → Encoding: UTF-8
2. **Check for hidden characters:**
    - Use `file` command (Unix/Linux): `file input.txt`
    - Expected: `ASCII text` or `UTF-8 Unicode text`
3. **Verify plain text format:**
    - File should be `.txt` extension
    - No Word documents (`.doc`, `.docx`), PDFs, or Excel files
4. **Remove BOM (Byte Order Mark) if present:**
    - Some editors add BOM to UTF-8 files, which may cause issues
    - Use editor option to "Save as UTF-8 without BOM"

---

### Error: Sample Name Cannot Be Empty

**Symptom:**

`ValidationError: Sample identifier cannot be empty`

**Cause:**

A line contains `>` character without a subsequent sample name.

**Resolution:**

1. Search file for lines matching exactly `>` wit

h no following text
2. Add meaningful sample name immediately after `>` (no space)
3. Ensure sample names are non-empty and alphanumeric-compatible

**Correct:**

```
>Soil_A
```

**Incorrect:**

```
>
```

---

## Validation and Parsing Issues

### File Size Limit Exceeded

**Symptom:**

`FileSizeExceededError: File exceeds maximum size of 5 MB`

**Cause:**

Uploaded file is larger than 5 MB.

**Resolution:**

1. **Split into multiple files:**
    - Divide samples into batches of ≤100 samples per file
    - Process each batch separately
    - Merge results externally if needed
2. **Remove duplicate KO entries:**
    - If same KO appears multiple times per sample, deduplicate beforehand
3. **Compress whitespace:**
    - Remove unnecessary blank lines (not permitted in BioRemPP format)
4. **Verify file is plain text:**
    - Binary files or formatted documents may inflate size

---

### Sample Limit Exceeded

**Symptom:**

`SampleLimitExceededError: File contains more than 100 samples`

**Cause:**

File contains more than 100 sample identifiers (lines starting with `>`).

**Resolution:**

1. **Count samples:**
    - Unix/Linux: `grep -c '^>' file.txt`
    - Manually count lines starting with `>`
2. **Split file:**
    - Create multiple files with ≤100 samples each
    - Maintain sample-KO associations (do not split sample data)
3. **Prioritize samples:**
    - If exploratory, select most relevant subset for initial analysis

---

### KO Limit Exceeded

**Symptom:**

`KOLimitExceededError: Total KO identifiers exceed 500,000`

**Cause:**

Sum of all KO identifiers across all samples exceeds 500,000.

**Resolution:**

1. **Reduce samples:**
    - Process fewer samples per batch
2. **Reduce KO redundancy:**
    - If using metagenomics, consider dereplicated gene catalog instead of all assembled genes
3. **Use representative subsets:**
    - For time-series or replicate datasets, process representative time points first

---

## Performance and Timeout Issues

### Slow Page Load or Response

**Symptoms:**

- Extended loading times (>1 minute)
- Unresponsive interface elements
- Blank charts or tables

**Potential causes:**

1. **Server load:**
    - Multiple concurrent users may temporarily slow response
    - Try during off-peak hours
2. **Browser performance:**
    - Insufficient memory or CPU resources
    - Too many open tabs or extensions

**Resolution:**

1. **Clear browser cache:**
    - Chrome: `Ctrl+Shift+Del` → Clear cached images and files
    - Firefox: `Ctrl+Shift+Del` → Clear Cache
2. **Disable extensions temporarily:**
    - Ad blockers may interfere with JavaScript execution
    - Test in incognito/private mode
3. **Close unused browser tabs:**
    - Free memory for BioRemPP session
4. **Restart browser:**
    - Clear active session state
5. **Check internet connection:**
    - Slow connection affects data transfer
    - Test with speed test tool (>5 Mbps recommended)

---

### Session Timeout During Processing

**Symptom:**

Analysis interrupted with timeout error during long processing jobs.

**Cause:**

Processing time exceeds server-side timeout limit.

**Resolution:**

1. **Reduce dataset size:**
    - Process smaller batches
    - Prioritize most critical samples
2. **Retry during off-peak hours:**
    - Reduced server load may improve processing speed
3. **Verify input quality:**
    - Malformed files may cause infinite loops or excessive processing
    - Validate file format before large uploads

---

### Resume by Job ID Not Working

**Symptoms:**

- Resume returns warning/danger status
- Redirect to `/results` does not happen
- Job ID appears valid but data is unavailable

**Common causes:**

1. **Expired retention window:**
    - Resume payload exceeded TTL (default 4 hours)
2. **Different browser profile/context:**
    - Resume is restricted to the browser profile that created the run
3. **Invalid Job ID format:**
    - Expected pattern: `BRP-YYYYMMDD-HHMMSS-XXXXXX`
4. **Temporary protection block:**
    - Too many failed attempts can trigger short rate-limit backoff

**Resolution:**

1. Copy Job ID directly from the `/results` overview card when possible
2. Retry in the same browser profile used for processing
3. Wait and retry if rate-limited
4. Reprocess input to generate a new Job ID when payload is expired/unavailable

---

## Visualization Rendering Issues

### Charts Not Displaying

**Symptoms:**

- Blank visualization panels
- "Loading..." message persists
- Placeholder graphics instead of charts

**Essential checks:**

1. **JavaScript enabled:**
    - Browser Settings → Privacy/Security → JavaScript: Allow
    - Required for Plotly-based visualizations
2. **Browser version:**
    - Update to latest version
    - Minimum: Chrome 90+, Firefox 88+, Edge 90+, Safari 14+
3. **Zoom level:**
    - Reset browser zoom to 100% (`Ctrl+0`)
    - Non-standard zoom may distort rendering canvas

**Advanced troubleshooting:**

1. **Open browser console:**
    - Press `F12` or `Ctrl+Shift+I`
    - Check Console tab for JavaScript errors
    - Look for errors containing "Plotly" or "WebGL"
2. **Test in incognito mode:**
    - Disables extensions that may interfere
    - Chrome: `Ctrl+Shift+N`
    - Firefox: `Ctrl+Shift+P`
3. **Clear site data:**
    - Chrome: Settings → Privacy → Site Settings → View permissions and data → bioinfo.imd.ufrn.br → Clear data
    - Firefox: Settings → Privacy → Manage Data → Remove site data
4. **Check network restrictions:**
    - Corporate firewalls may block WebGL or specific JavaScript libraries
    - Contact IT administrator if issues persist

---

### Charts Display Incorrectly

**Symptoms:**

- Truncated labels
- Overlapping text
- Missing legend or axes
- Distorted proportions

**Causes and solutions:**

1. **Browser window too small:**
    - Expand browser window to full screen
    - Minimum recommended: 1280×720 resolution
2. **High DPI/scaling settings:**
    - Windows: Set display scaling to 100-125%
    - Plotly rendering may distort at >150% scaling
3. **Font rendering issues:**
    - Update graphics drivers
    - Try different browser
4. **Legitimate data visualization constraint:**
    - If chart contains >50 data points, labels may overlap
    - Use hover tooltips for detailed information
    - Download data table for complete information

---

## Download-Related Issues

### Download Button Unresponsive

**Symptom:**

Clicking "Download Data" button produces no response or error.

**Resolution:**

1. **Check browser pop-up blocker:**
    - Allow pop-ups for bioinfo.imd.ufrn.br
    - Browser address bar usually shows blocked pop-up icon
2. **Try alternative format:**
    - If CSV fails, try Excel or JSON
    - May indicate format-specific export issue
3. **Clear download queue:**
    - Cancel pending downloads in browser
    - Retry export

---

### Downloaded File Empty or Corrupt

**Symptom:**

Downloaded file has 0 bytes or cannot be opened.

**Causes:**

1. **No matching data:**
    - Database query returned no results
    - Expected behavior if no KOs match that database
2. **Incomplete download:**
    - Connection interrupted mid-download
    - Retry download with stable connection
3. **Browser extension interference:**
    - Download manager may corrupt file
    - Disable extensions, retry

**Resolution:**

1. **Verify data exists:**
    - Check corresponding data table in interface
    - If table is empty, download will also be empty
2. **Retry download:**
    - Use different format (CSV vs. Excel vs. JSON)
3. **Check file size after download:**
    - Empty files suggest database query returned no matches
4. **Test with example dataset:**
    - Confirm download functionality with provided example

---

### Chart Export Issues

**Symptom:**

Plotly charts export as blank images or with rendering errors.

**Resolution:**

1. **Wait for chart to fully render:**
    - Ensure chart displays correctly in browser before exporting
    - Hover over chart to confirm interactivity
2. **Export from fullscreen chart:**
    - Expand chart to maximize before export
    - Improves resolution and label visibility
3. **Use Download Data as alternative:**
    - Export data table
    - Recreate chart using R, Python, or Excel

---

## When to Contact Support

### Unresolved Technical Issues

Contact support if:

1. **Systematic validation failures** after verifying file format compliance
2. **Persistent timeout errors** with small datasets (<100,000 KOs)
3. **Widespread visualization failures** across multiple browsers and devices
4. **Data integrity concerns** (e.g., results inconsistent with expectations after multiple runs)

### Information to Provide

For efficient troubleshooting, include:

1. **Error message:** Exact text of error or screenshot
2. **BioRemPP version:** From page footer (e.g., v1.0.0)
3. **Browser and version:** Chrome 120, Firefox 119, etc.
4. **Dataset characteristics:**
    - Number of samples
    - Total KO count
    - File size
5. **Steps to reproduce:** Sequence of actions leading to error
6. **Console logs:** Browser console output (F12 → Console tab)

### Out of Scope

Support does **not** provide assistance with:

- Scientific interpretation of results (see [Interpretation](interpretation.md))
- Input file preparation or KO annotation (see [Input Format](../getting-started/input-format.md))
- Statistical analysis of exported data
- Custom feature requests or software modifications

---

## Related Pages

- [Input Format](../getting-started/input-format.md) — Complete format specification and validation rules
- [FAQ](../getting-started/faq.md) — Common questions and quick solutions
- [Results Page](results-page.md) — Understanding the analytical interface
- [Downloads Guide](downloads.md) — Export troubleshooting
- [Contact](../about/contact.md) — Report bugs and technical issues
