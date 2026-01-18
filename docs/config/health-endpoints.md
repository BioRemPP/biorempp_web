# Health and Readiness Endpoints

BioRemPP Web Service provides HTTP endpoints for health monitoring and readiness checks. These endpoints support container orchestration, load balancers, and uptime monitoring systems.

---

## Scope

**This page covers:**

- Purpose and usage of health endpoints
- Endpoint responses and status codes
- Recommended monitoring patterns

---

## Available Endpoints

### `/health` — Liveness Check

**Purpose:** Indicates whether the service process is running and responsive.

**Use cases:**

- Container orchestration liveness probes (Docker, Kubernetes)
- Load balancer health checks
- Uptime monitoring

**Request:**
```bash
curl http://localhost:8080/health
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "service": "BioRemPP",
  "version": "1.0.0",
  "environment": "production"
}
```

**Interpretation:**

- `200 OK` → Service is alive and responding
- Non-200 or timeout → Service is down or unresponsive

---

### `/ready` — Readiness Check

**Purpose:** Indicates whether the service is ready to accept requests.

**Use cases:**

- Container orchestration readiness probes
- Deployment validation (wait for service to be fully initialized)
- Graceful startup coordination

**Request:**
```bash
curl http://localhost:8080/ready
```

**Response (200 OK):**
```json
{
  "status": "ready",
  "checks": {
    "app": "ok",
    "settings": "ok",
    "logging": "ok"
  }
}
```

**Response (503 Service Unavailable):**
```json
{
  "status": "not ready",
  "error": "description of failure"
}
```

**Interpretation:**

- `200 OK` → Service is fully initialized and ready to process requests
- `503 Service Unavailable` → Service is running but dependencies are not ready

---

## Differences Between Endpoints

| Aspect | `/health` | `/ready` |
|--------|-----------|----------|
| **Purpose** | Is the process alive? | Can it handle requests? |
| **Checks** | Basic responsiveness | Dependency availability |
| **Container Use** | Liveness probe | Readiness probe |
| **Failure Action** | Restart container | Remove from load balancer |

---

## Response Time Expectations

| Endpoint | Expected Response Time |
|----------|------------------------|
| `/health` | < 100ms |
| `/ready` | < 200ms |

Slow responses may indicate:
- High server load
- Resource contention
- Imminent service degradation

---

## Common Pitfalls

1. **Using `/ready` for liveness probes:** Readiness failures should remove instances from load balancer rotation, not restart them

2. **Too-short timeout values:** Network latency and server load require timeout ≥ 3s

3. **Too-aggressive failure thresholds:** Single transient failures should not trigger restarts; use `failureThreshold ≥ 3`

4. **Not setting `initialDelaySeconds`:** Application startup requires initialization time; set appropriate delay to avoid premature failures

5. **Monitoring internal Dash endpoints directly:** Use `/health` and `/ready` for external monitoring; `/_dash-update-component` is internal

---

## See Also

- [Gunicorn Configuration](gunicorn.md) — Production server settings
- [Environment Variables](environment-variables.md) — Runtime configuration
- [Logging Configuration](logging.md) — Log profiles for debugging health issues
- [Nginx Integration](nginx-integration.md) — Load balancer health check configuration
- [Docker Integration](docker-integration.md) — Container health check configuration
