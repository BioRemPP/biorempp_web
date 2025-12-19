/**
 * Navigation Scroll Handler - BioRemPP v1.0
 * ==========================================
 * 
 * Implements smooth scroll navigation for offcanvas navigation links.
 * Works around Dash's hash-based navigation limitations by intercepting
 * clicks and scrolling programmatically.
 * 
 * Features:
 * - Smooth scroll to target sections
 * - Respects header offset (scroll-padding-top)
 * - Keeps offcanvas open during navigation
 * - Works with Dash's dynamic rendering
 * 
 * @version 1.1.0
 * @date 2025-11-17
 */

(function () {
    'use strict';

    console.log('[SCROLL-NAV] 🚀 Navigation scroll handler v1.1.0 loaded');

    // Configuration
    const CONFIG = {
        scrollBehavior: 'smooth',
        scrollOffset: 100,  // Offset for fixed header (matches CSS scroll-padding-top)
        scrollDuration: 800, // Fallback duration in ms
        retryAttempts: 10,   // How many times to retry finding elements
        retryDelay: 500      // Delay between retries in ms
    };

    /**
     * Smooth scroll to element with offset
     * @param {HTMLElement} element - Target element to scroll to
     */
    function scrollToElement(element) {
        if (!element) {
            console.error('[SCROLL-NAV] ❌ Target element not found');
            return;
        }

        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - CONFIG.scrollOffset;

        console.log('[SCROLL-NAV] 📍 Scroll calculation:', {
            elementId: element.id,
            currentScroll: window.pageYOffset,
            elementTop: elementPosition,
            targetScroll: offsetPosition,
            offset: CONFIG.scrollOffset
        });

        // Use native smooth scroll if supported
        if ('scrollBehavior' in document.documentElement.style) {
            window.scrollTo({
                top: offsetPosition,
                behavior: CONFIG.scrollBehavior
            });
            console.log('[SCROLL-NAV] ✅ Smooth scroll initiated to:', offsetPosition);
        } else {
            // Fallback for older browsers
            window.scrollTo(0, offsetPosition);
            console.log('[SCROLL-NAV] ✅ Fallback scroll to:', offsetPosition);
        }
    }

    /**
     * Handle navigation link click
     * @param {Event} event - Click event
     */
    function handleNavigationClick(event) {
        const link = event.currentTarget;

        console.log('='.repeat(80));
        console.log('[SCROLL-NAV] 🖱️ CLICK EVENT DETAILS:');
        console.log('[SCROLL-NAV]   - Element ID:', link.id || '(no id)');
        console.log('[SCROLL-NAV]   - Element class:', link.className);
        console.log('[SCROLL-NAV]   - Element tag:', link.tagName);

        // Extract target ID from href attribute (e.g., "#biorempp-section")
        const href = link.getAttribute('href');
        console.log('[SCROLL-NAV]   - href attribute:', href);

        if (!href || !href.startsWith('#')) {
            console.warn('[SCROLL-NAV] ⚠️ No valid href attribute found');
            console.log('='.repeat(80));
            return;
        }

        const targetId = href.substring(1); // Remove '#'
        console.log('[SCROLL-NAV] 🎯 TARGET EXTRACTION:');
        console.log('[SCROLL-NAV]   - Raw href:', href);
        console.log('[SCROLL-NAV]   - Extracted target ID:', targetId);

        // CRITICAL: Prevent ALL default behaviors
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();
        console.log('[SCROLL-NAV] 🛑 Default behavior prevented');

        // Find target element
        const targetElement = document.getElementById(targetId);

        if (targetElement) {
            console.log('[SCROLL-NAV] ✓ TARGET ELEMENT FOUND:');
            console.log('[SCROLL-NAV]   - Element ID:', targetElement.id);
            console.log('[SCROLL-NAV]   - Element tag:', targetElement.tagName);
            console.log('[SCROLL-NAV]   - Element class:', targetElement.className);
            console.log('[SCROLL-NAV]   - Element position:', targetElement.getBoundingClientRect());

            // Small delay to ensure Dash doesn't interfere
            setTimeout(() => {
                console.log('[SCROLL-NAV] ⏱️ Executing scroll after delay...');
                scrollToElement(targetElement);

                // Update URL hash WITHOUT triggering scroll
                // This prevents browser's default hash navigation
                if (history.replaceState) {
                    history.replaceState(null, null, '#' + targetId);
                    console.log('[SCROLL-NAV] 📝 URL hash updated to:', '#' + targetId);
                }
                console.log('='.repeat(80));
            }, 50);

        } else {
            console.error('[SCROLL-NAV] ❌ TARGET ELEMENT NOT FOUND:');
            console.error('[SCROLL-NAV]   - Looking for ID:', targetId);
            console.log('[SCROLL-NAV] 🔍 AVAILABLE IDs ON PAGE (first 50):');
            const allIds = Array.from(document.querySelectorAll('[id]')).map(el => el.id);
            console.log('[SCROLL-NAV]   Total IDs found:', allIds.length);
            allIds.slice(0, 50).forEach((id, index) => {
                console.log(`[SCROLL-NAV]   ${index + 1}. ${id}`);
            });

            // Check for similar IDs
            const similarIds = allIds.filter(id => id.includes(targetId.split('-')[1]));
            if (similarIds.length > 0) {
                console.log('[SCROLL-NAV] 💡 SIMILAR IDs FOUND:');
                similarIds.forEach(id => console.log(`[SCROLL-NAV]   - ${id}`));
            }
            console.log('='.repeat(80));
        }

        // Return false to ensure no default action
        return false;
    }

    /**
     * Attach click handlers to all navigation links
     */
    function attachNavigationHandlers() {
        // Find all navigation links (they have IDs starting with "nav-")
        const navLinks = document.querySelectorAll('[id^="nav-"]');

        console.log(`[SCROLL-NAV] 🔍 Found ${navLinks.length} navigation link(s)`);

        let attachedCount = 0;
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href.startsWith('#')) {
                // Remove old listeners to prevent duplicates
                link.removeEventListener('click', handleNavigationClick);

                // Add new listener with capture phase to intercept early
                link.addEventListener('click', handleNavigationClick, true);

                console.log('[SCROLL-NAV] ✓ Handler attached to:', link.id, '→', href);
                attachedCount++;
            } else {
                console.log('[SCROLL-NAV] ⊘ Skipped (no hash href):', link.id);
            }
        });

        console.log(`[SCROLL-NAV] 📊 Handlers attached: ${attachedCount}/${navLinks.length}`);
        return attachedCount;
    }

    /**
     * Attach click handlers to suggestion UC links
     */
    function attachSuggestionHandlers() {
        // Find all suggestion links (they have class "suggestion-uc-link")
        const suggestionLinks = document.querySelectorAll('.suggestion-uc-link');

        console.log(`[SCROLL-NAV] 🔍 Found ${suggestionLinks.length} suggestion link(s)`);

        let attachedCount = 0;
        suggestionLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href.startsWith('#')) {
                // Remove old listeners to prevent duplicates
                link.removeEventListener('click', handleNavigationClick);

                // Add new listener with capture phase
                link.addEventListener('click', handleNavigationClick, true);

                console.log('[SCROLL-NAV] ✓ Suggestion handler attached:', href);
                attachedCount++;
            }
        });

        console.log(`[SCROLL-NAV] 📊 Suggestion handlers attached: ${attachedCount}/${suggestionLinks.length}`);
        return attachedCount;
    }

    function preventDefaultHashScroll() {
        // Intercept all hash changes to prevent auto-scroll
        let isManualScroll = false;

        window.addEventListener('hashchange', function (event) {
            console.log('[SCROLL-NAV] 🔔 Hash change event detected');

            if (!isManualScroll) {
                console.log('[SCROLL-NAV] 🛑 Preventing default hash scroll');
                event.preventDefault();
            }

            isManualScroll = false;
        }, false);

        console.log('[SCROLL-NAV] 🛡️ Global hash scroll prevention active');
    }

    /**
     * Initialize navigation with retry logic
     */
    function initializeNavigation(attempt = 1) {
        console.log(`[SCROLL-NAV] 🔄 Initializing navigation (attempt ${attempt}/${CONFIG.retryAttempts})...`);

        const navLinksFound = attachNavigationHandlers();
        const suggestionLinksFound = attachSuggestionHandlers();
        const totalLinksFound = navLinksFound + suggestionLinksFound;

        if (totalLinksFound > 0) {
            console.log('[SCROLL-NAV] ✅ Navigation initialized successfully');
            return true;
        }

        if (attempt < CONFIG.retryAttempts) {
            console.log(`[SCROLL-NAV] ⏳ No links found, retrying in ${CONFIG.retryDelay}ms...`);
            setTimeout(() => initializeNavigation(attempt + 1), CONFIG.retryDelay);
        } else {
            console.warn('[SCROLL-NAV] ⚠️ Failed to find navigation links after all retries');
        }

        return false;
    }

    /**
     * Monitor DOM changes to catch Dash re-renders
     */
    function observeDOMChanges() {
        const observer = new MutationObserver((mutations) => {
            // Check if offcanvas was added/modified
            const offcanvasAdded = mutations.some(mutation => {
                return Array.from(mutation.addedNodes).some(node => {
                    return node.id === 'navigation-offcanvas' ||
                        node.id === 'suggestions-offcanvas' ||
                        (node.querySelector && (
                            node.querySelector('#navigation-offcanvas') ||
                            node.querySelector('#suggestions-offcanvas')
                        ));
                });
            });

            // Check if suggestions tab content changed (tab switch)
            const tabContentChanged = mutations.some(mutation => {
                // Check if mutation affects suggestions-tab-content or its children
                if (mutation.target.id === 'suggestions-tab-content') {
                    return true;
                }
                // Check if any added nodes are inside suggestions-tab-content
                return Array.from(mutation.addedNodes).some(node => {
                    if (node.nodeType === 1) { // Element node
                        return node.closest && node.closest('#suggestions-tab-content');
                    }
                    return false;
                });
            });

            if (offcanvasAdded || tabContentChanged) {
                console.log('[SCROLL-NAV] 🔄 Content change detected, re-initializing...');
                setTimeout(() => initializeNavigation(), 100);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        console.log('[SCROLL-NAV] 👀 DOM observer started');
    }

    // ========================================
    // INITIALIZATION
    // ========================================

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            console.log('[SCROLL-NAV] 📄 DOM ready, initializing...');
            preventDefaultHashScroll();
            initializeNavigation();
            observeDOMChanges();
        });
    } else {
        // DOM already loaded
        console.log('[SCROLL-NAV] 📄 DOM already ready, initializing...');
        preventDefaultHashScroll();
        initializeNavigation();
        observeDOMChanges();
    }

    // Listen for page visibility changes (tab switch)
    document.addEventListener('visibilitychange', function () {
        if (!document.hidden) {
            console.log('[SCROLL-NAV] 👁️ Page visible, checking navigation...');
            initializeNavigation();
        }
    });

    // Expose API for manual triggering (useful for debugging)
    window.BioRemPP = window.BioRemPP || {};
    window.BioRemPP.navigation = {
        scrollTo: function (targetId) {
            console.log('[SCROLL-NAV] 🎯 Manual scroll requested to:', targetId);
            const element = document.getElementById(targetId);
            if (element) {
                scrollToElement(element);
            } else {
                console.error('[SCROLL-NAV] ❌ Element not found:', targetId);
            }
        },
        reinitialize: function () {
            console.log('[SCROLL-NAV] 🔄 Manual reinitialization requested');
            return initializeNavigation();
        },
        getConfig: function () {
            return CONFIG;
        },
        debug: function () {
            console.log('[SCROLL-NAV] 🐛 Debug info:');
            console.log('- Navigation links:', document.querySelectorAll('[id^="nav-"]').length);
            console.log('- All IDs on page:', Array.from(document.querySelectorAll('[id]')).map(el => el.id));
            console.log('- Current scroll:', window.pageYOffset);
            console.log('- Config:', CONFIG);
        }
    };

    console.log('[SCROLL-NAV] 🎮 API available at window.BioRemPP.navigation');
    console.log('[SCROLL-NAV] 💡 Try: window.BioRemPP.navigation.debug()');

})();
