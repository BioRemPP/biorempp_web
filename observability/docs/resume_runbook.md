# Resume Analysis by Job ID - Runbook

## Scope
- Operational monitoring and incident handling for the resume flow (`job_id` restore).
- Covers app callbacks, service/store outcomes, and rate-limit backend behavior.

## Key Signals
- `biorempp_resume_load_attempts_total{outcome=...}`
- `biorempp_resume_save_total{outcome=...}`
- `biorempp_resume_operation_duration_seconds{backend,operation,status}`
- `biorempp_resume_payload_size_bytes{backend}`
- `biorempp_resume_callback_attempts_total{outcome}`
- `biorempp_resume_persist_duration_seconds{outcome}`
- `biorempp_resume_rate_limit_backend_info{backend}`
- `biorempp_resume_rate_limit_errors_total{backend,operation}`

## Alerts to Watch
- `BioRemPPResumeNotFoundSpike`
- `BioRemPPResumeTokenMismatchSpike`
- `BioRemPPResumeSaveFailedSpike`
- `BioRemPPResumeRateLimitedSpike`
- `BioRemPPResumeRateLimitBackendErrors`

## Correlation
- Use `X-Request-ID` from response headers to correlate browser errors with server logs.
- Logs include request correlation (`[req:<id>]`) and redacted refs (`job_ref`, `cache_ref`).
- Raw `job_id`, IP and token are not used as metric labels.

## Runtime Policy
- Redis rate-limit backend failure: `fail-open` (availability first).
- Expected behavior on backend failure:
  - resume request continues
  - backend error counter increases
  - warning/exception logged with redacted refs only

## Incident Checklist
1. Confirm target health (`/health`) and app readiness (`/ready`).
2. Check `/metrics` and alert panel for resume/rate-limit anomalies.
3. Filter logs by `request_id` and inspect `job_ref`/`cache_ref` paths.
4. Validate active rate-limit backend (`biorempp_resume_rate_limit_backend_info`).
5. If Redis degradation is confirmed, decide between:
   - keep `fail-open` temporarily (higher availability),
   - switch to controlled maintenance window for limiter recovery.

## Capacity and Cardinality Notes
- Keep current low-cardinality labels.
- Do not add `job_id`, IP, token, user-agent, or free-text labels.
- Tune retention by environment:
  - dev/staging: shorter retention
  - production: retention based on incident forensics needs
