/**
 * Navigation Scroll Handler - BioRemPP v1.2
 *
 * Hash-driven navigation that cooperates with lazy /results module loading.
 * - Supports canonical and legacy UC targets
 * - Retries while module content is mounting
 * - Falls back to module overview target when UC anchor is unavailable
 */

(function () {
    "use strict";

    const CONFIG = {
        scrollBehavior: "smooth",
        scrollOffset: 100,
        retryDelayMs: 100,
        maxAttempts: 50,
    };

    const UC_TARGET_RE = /^#uc-([1-8])-(\d+)-(?:card|info-panel)$/;
    const MODULE_TARGET_RE = /^#module([1-8])-section$/;
    const DB_TARGETS = new Set([
        "#biorempp-section",
        "#hadeg-section",
        "#toxcsm-section",
        "#kegg-section",
    ]);

    let pending = null;
    let lastPathname = window.location.pathname || "";

    function normalizeHash(rawHash) {
        if (typeof rawHash !== "string") {
            return null;
        }
        let value = rawHash.trim();
        if (!value) {
            return null;
        }
        if (!value.startsWith("#")) {
            value = "#" + value;
        }
        const ucMatch = value.match(UC_TARGET_RE);
        if (ucMatch) {
            return "#uc-" + ucMatch[1] + "-" + ucMatch[2] + "-card";
        }
        if (value.match(MODULE_TARGET_RE) || DB_TARGETS.has(value)) {
            return value;
        }
        return null;
    }

    function resolveModuleFromHash(hash) {
        if (typeof hash !== "string") {
            return null;
        }
        const ucMatch = hash.match(UC_TARGET_RE);
        if (ucMatch) {
            return Number.parseInt(ucMatch[1], 10);
        }
        const moduleMatch = hash.match(MODULE_TARGET_RE);
        if (moduleMatch) {
            return Number.parseInt(moduleMatch[1], 10);
        }
        return null;
    }

    function resolveFallbackHash(hash) {
        const moduleIndex = resolveModuleFromHash(hash);
        if (moduleIndex && moduleIndex >= 1 && moduleIndex <= 8) {
            return "#module" + moduleIndex + "-section";
        }
        if (DB_TARGETS.has(hash)) {
            return hash;
        }
        return "#module1-section";
    }

    function scrollToElement(element) {
        if (!element) {
            return;
        }
        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - CONFIG.scrollOffset;
        window.scrollTo({
            top: offsetPosition,
            behavior: CONFIG.scrollBehavior,
        });
    }

    function showFallbackNotice(targetHash, fallbackHash) {
        const node = document.createElement("div");
        node.className = "alert alert-warning shadow-sm";
        node.style.position = "fixed";
        node.style.right = "20px";
        node.style.bottom = "20px";
        node.style.zIndex = "2000";
        node.style.maxWidth = "420px";
        node.style.margin = "0";
        node.style.padding = "10px 14px";
        node.innerText =
            "We couldn't open the exact section yet. You were taken to the related module section.";

        document.body.appendChild(node);
        window.setTimeout(function () {
            if (node.parentNode) {
                node.parentNode.removeChild(node);
            }
        }, 2500);
    }

    function setHashSilently(hash) {
        // Use native hash assignment so Dash dcc.Location consistently detects changes.
        if (window.location.hash !== hash) {
            window.location.hash = hash;
        }
    }

    function clearPending() {
        if (!pending) {
            return;
        }
        if (pending.timerId) {
            window.clearTimeout(pending.timerId);
        }
        pending = null;
    }

    function isResultsPathname(pathname) {
        return typeof pathname === "string" && pathname.indexOf("/results") !== -1;
    }

    function scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: "auto",
        });
    }

    function processPending() {
        if (!pending) {
            return;
        }
        const targetModule = resolveModuleFromHash(pending.hash);
        const targetId = pending.hash.slice(1);
        const target = document.getElementById(targetId);
        if (target) {
            scrollToElement(target);
            clearPending();
            return;
        }

        // If this is a UC target and the module container is still mounting,
        // allow extra retries before fallback.
        if (targetModule !== null) {
            const moduleSectionId = "module" + String(targetModule) + "-section";
            const moduleSection = document.getElementById(moduleSectionId);
            if (!moduleSection && pending.attempt < CONFIG.maxAttempts) {
                pending.attempt += 1;
                pending.timerId = window.setTimeout(processPending, CONFIG.retryDelayMs);
                return;
            }
        }

        pending.attempt += 1;
        if (pending.attempt >= CONFIG.maxAttempts) {
            const fallbackHash = resolveFallbackHash(pending.hash);
            const fallbackTarget = document.getElementById(fallbackHash.slice(1));
            if (fallbackTarget) {
                scrollToElement(fallbackTarget);
            }
            showFallbackNotice(pending.hash, fallbackHash);
            clearPending();
            return;
        }

        pending.timerId = window.setTimeout(processPending, CONFIG.retryDelayMs);
    }

    function queueScroll(hash) {
        const normalized = normalizeHash(hash);
        if (!normalized) {
            return;
        }
        clearPending();
        pending = {
            hash: normalized,
            attempt: 0,
            timerId: null,
        };
        processPending();
    }

    function handleHashChange() {
        queueScroll(window.location.hash || "");
    }

    function handlePathnameChange() {
        const currentPathname = window.location.pathname || "";
        if (currentPathname === lastPathname) {
            return;
        }

        const previousPathname = lastPathname;
        lastPathname = currentPathname;

        if (!isResultsPathname(currentPathname)) {
            clearPending();
            return;
        }

        // Entering /results route:
        // - If hash exists, navigation should be hash-driven.
        // - If hash is empty, force top to avoid carrying old scroll position.
        const activeHash = window.location.hash || "";
        if (activeHash) {
            queueScroll(activeHash);
            return;
        }

        // Avoid unnecessary jumps when already inside /results.
        if (!isResultsPathname(previousPathname)) {
            scrollToTop();
        }
    }

    function handleLinkClick(event) {
        const link = event.target && event.target.closest
            ? event.target.closest("[id^='nav-'], .suggestion-uc-link")
            : null;
        if (!link) {
            return;
        }
        const href = link.getAttribute("href");
        const normalized = normalizeHash(href || "");
        if (!normalized) {
            return;
        }
        event.preventDefault();
        event.stopPropagation();
        setHashSilently(normalized);
        queueScroll(normalized);
    }

    function observeDomUpdates() {
        const observer = new MutationObserver(function () {
            if (pending) {
                processPending();
            }
        });
        observer.observe(document.body, {
            childList: true,
            subtree: true,
        });
    }

    function initialize() {
        document.addEventListener("click", handleLinkClick, true);
        window.addEventListener("hashchange", handleHashChange);
        observeDomUpdates();
        window.setInterval(handlePathnameChange, 120);
        if (window.location.hash) {
            queueScroll(window.location.hash);
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initialize);
    } else {
        initialize();
    }
})();
