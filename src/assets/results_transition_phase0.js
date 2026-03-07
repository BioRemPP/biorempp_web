/**
 * Results transition diagnostics (phase 0).
 *
 * Captures client-side timings from "View Results" click to route rendering
 * and posts samples to /perf/results-transition for p50/p95 analysis.
 */

(function () {
    "use strict";

    const SESSION_STORAGE_KEY = "biorempp_results_perf_session_id";
    const RESULTS_ROUTE_FRAGMENT = "/results";
    const FINALIZE_POLL_INTERVAL_MS = 100;
    const FINALIZE_TIMEOUT_MS = 30000;

    let pendingTransition = null;
    let fetchPatched = false;

    function nowSeconds() {
        return performance.now() / 1000.0;
    }

    function toFixedSeconds(value) {
        if (typeof value !== "number" || !Number.isFinite(value) || value < 0) {
            return null;
        }
        return Number(value.toFixed(6));
    }

    function safeParseInt(value) {
        const parsed = Number.parseInt(value, 10);
        return Number.isFinite(parsed) && parsed >= 0 ? parsed : null;
    }

    function createSessionId() {
        if (window.crypto && typeof window.crypto.getRandomValues === "function") {
            const bytes = new Uint8Array(16);
            window.crypto.getRandomValues(bytes);
            return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
        }
        return "sess-" + String(Date.now()) + "-" + String(Math.floor(Math.random() * 1e9));
    }

    function getSessionId() {
        try {
            let existing = window.localStorage.getItem(SESSION_STORAGE_KEY);
            if (existing && existing.trim()) {
                return existing.trim();
            }
            existing = createSessionId();
            window.localStorage.setItem(SESSION_STORAGE_KEY, existing);
            return existing;
        } catch (_err) {
            return createSessionId();
        }
    }

    function estimateBodyBytes(body) {
        if (body == null) {
            return null;
        }
        if (typeof body === "string") {
            return new TextEncoder().encode(body).length;
        }
        if (body instanceof URLSearchParams) {
            return new TextEncoder().encode(body.toString()).length;
        }
        if (body instanceof ArrayBuffer) {
            return body.byteLength;
        }
        if (ArrayBuffer.isView(body)) {
            return body.byteLength;
        }
        if (typeof Blob !== "undefined" && body instanceof Blob) {
            return body.size;
        }
        return null;
    }

    function normalizeDashOutput(rawOutput) {
        if (typeof rawOutput !== "string") {
            return null;
        }
        const trimmed = rawOutput.trim();
        if (!trimmed) {
            return null;
        }
        return trimmed.replace(/[^a-zA-Z0-9_.:\-]/g, "_").slice(0, 96);
    }

    function parseDashOutputFromBody(body) {
        if (typeof body !== "string") {
            return null;
        }
        try {
            const parsed = JSON.parse(body);
            if (parsed && typeof parsed === "object") {
                if (typeof parsed.output === "string") {
                    return normalizeDashOutput(parsed.output);
                }
                if (parsed.outputs && typeof parsed.outputs === "object") {
                    const outputs = Array.isArray(parsed.outputs)
                        ? parsed.outputs[0]
                        : parsed.outputs;
                    if (
                        outputs &&
                        typeof outputs === "object" &&
                        typeof outputs.property === "string"
                    ) {
                        const componentId = outputs.id;
                        if (typeof componentId === "string") {
                            return normalizeDashOutput(componentId + "." + outputs.property);
                        }
                    }
                }
            }
        } catch (_err) {
            return null;
        }
        return null;
    }

    function extractRequestUrl(input) {
        if (typeof input === "string") {
            return input;
        }
        if (input && typeof input.url === "string") {
            return input.url;
        }
        return "";
    }

    function isDashUpdateRequest(url) {
        return typeof url === "string" && url.indexOf("/_dash-update-component") !== -1;
    }

    function isResultsPathname(pathname) {
        return typeof pathname === "string" && pathname.indexOf(RESULTS_ROUTE_FRAGMENT) !== -1;
    }

    function hasResultsPageMarker() {
        return Boolean(
            document.getElementById("module1-section") ||
            document.getElementById("results-job-id-copy-target")
        );
    }

    function readJobId() {
        const jobElement = document.getElementById("results-job-id-copy-target");
        if (!jobElement || typeof jobElement.textContent !== "string") {
            return null;
        }
        const value = jobElement.textContent.trim();
        return value && value !== "--" ? value.slice(0, 64) : null;
    }

    function detectBasePath() {
        const scripts = document.querySelectorAll('script[src*="/_dash-component-suites/"]');
        for (const script of scripts) {
            try {
                const url = new URL(script.src, window.location.origin);
                const marker = "/_dash-component-suites/";
                const markerIndex = url.pathname.indexOf(marker);
                if (markerIndex >= 0) {
                    const prefix = url.pathname.slice(0, markerIndex);
                    return prefix === "/" ? "" : prefix.replace(/\/$/, "");
                }
            } catch (_err) {
                // Ignore malformed script URL
            }
        }
        return "";
    }

    function perfEndpointUrl() {
        return detectBasePath() + "/perf/results-transition";
    }

    function postSample(sample) {
        const payload = JSON.stringify(sample);
        const url = perfEndpointUrl();

        if (navigator.sendBeacon) {
            const blob = new Blob([payload], { type: "application/json" });
            navigator.sendBeacon(url, blob);
            return;
        }

        window.fetch(url, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: payload,
            keepalive: true
        }).catch(function () {
            // Best-effort telemetry only.
        });
    }

    function clearPendingTransition() {
        if (!pendingTransition) {
            return;
        }
        if (pendingTransition.pollTimer) {
            window.clearInterval(pendingTransition.pollTimer);
        }
        if (pendingTransition.timeoutTimer) {
            window.clearTimeout(pendingTransition.timeoutTimer);
        }
        pendingTransition = null;
    }

    function finalizeTransition(trigger) {
        if (!pendingTransition) {
            return;
        }
        const pathname = window.location.pathname || "";
        const routeReady = isResultsPathname(pathname) && hasResultsPageMarker();

        if (!routeReady && trigger !== "timeout") {
            return;
        }

        const paintSeconds = nowSeconds();
        const clickToRequest = pendingTransition.requestStartSeconds == null
            ? null
            : toFixedSeconds(pendingTransition.requestStartSeconds - pendingTransition.clickSeconds);
        const requestToPaint = pendingTransition.requestStartSeconds == null
            ? null
            : toFixedSeconds(paintSeconds - pendingTransition.requestStartSeconds);
        const clickToPaint = toFixedSeconds(paintSeconds - pendingTransition.clickSeconds);

        const sample = {
            route: "/results",
            click_to_request_seconds: clickToRequest,
            request_to_paint_seconds: requestToPaint,
            click_to_paint_seconds: clickToPaint,
            request_bytes: pendingTransition.requestBytes,
            response_bytes: pendingTransition.responseBytes,
            dash_output: pendingTransition.dashOutput,
            job_id: readJobId(),
            session_id: getSessionId(),
            client_time_utc: new Date().toISOString(),
            user_agent: (navigator.userAgent || "").slice(0, 256),
            trigger: trigger
        };

        postSample(sample);
        clearPendingTransition();
    }

    function startTransitionTracking() {
        clearPendingTransition();
        pendingTransition = {
            clickSeconds: nowSeconds(),
            requestStartSeconds: null,
            requestBytes: null,
            responseBytes: null,
            dashOutput: null,
            preferredOutputSeen: false,
            pollTimer: null,
            timeoutTimer: null
        };
        pendingTransition.pollTimer = window.setInterval(function () {
            finalizeTransition("poll");
        }, FINALIZE_POLL_INTERVAL_MS);
        pendingTransition.timeoutTimer = window.setTimeout(function () {
            finalizeTransition("timeout");
        }, FINALIZE_TIMEOUT_MS);
    }

    function handleClick(event) {
        if (!event || !event.target || typeof event.target.closest !== "function") {
            return;
        }
        const viewResultsButton = event.target.closest("#view-results-btn");
        if (!viewResultsButton) {
            return;
        }
        startTransitionTracking();
    }

    function patchFetchForDashRequests() {
        if (fetchPatched || typeof window.fetch !== "function") {
            return;
        }
        fetchPatched = true;
        const originalFetch = window.fetch;

        window.fetch = function patchedFetch(input, init) {
            const requestUrl = extractRequestUrl(input);
            const dashUpdateRequest = isDashUpdateRequest(requestUrl);
            const requestBody = init && Object.prototype.hasOwnProperty.call(init, "body")
                ? init.body
                : null;
            const parsedDashOutput = parseDashOutputFromBody(requestBody);
            const preferredOutput = parsedDashOutput === "page-content.children";

            if (
                dashUpdateRequest &&
                pendingTransition &&
                pendingTransition.requestStartSeconds == null
            ) {
                pendingTransition.requestStartSeconds = nowSeconds();
            }

            if (dashUpdateRequest && pendingTransition) {
                if (preferredOutput) {
                    pendingTransition.requestBytes = estimateBodyBytes(requestBody);
                    pendingTransition.dashOutput = parsedDashOutput;
                    pendingTransition.preferredOutputSeen = true;
                } else if (pendingTransition.requestBytes == null) {
                    pendingTransition.requestBytes = estimateBodyBytes(requestBody);
                    pendingTransition.dashOutput = parsedDashOutput;
                }
            }

            return originalFetch.apply(this, arguments).then(function (response) {
                if (
                    dashUpdateRequest &&
                    pendingTransition &&
                    response &&
                    response.headers
                ) {
                    const responseBytes = safeParseInt(response.headers.get("content-length"));
                    if (preferredOutput) {
                        pendingTransition.responseBytes = responseBytes;
                    } else if (
                        pendingTransition.responseBytes == null &&
                        !pendingTransition.preferredOutputSeen
                    ) {
                        pendingTransition.responseBytes = responseBytes;
                    }
                }
                return response;
            });
        };
    }

    patchFetchForDashRequests();
    document.addEventListener("click", handleClick, true);
})();
