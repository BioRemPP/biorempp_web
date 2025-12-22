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
            return;
        }

        const elementPosition = element.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - CONFIG.scrollOffset;

        // Use native smooth scroll if supported
        if ('scrollBehavior' in document.documentElement.style) {
            window.scrollTo({
                top: offsetPosition,
                behavior: CONFIG.scrollBehavior
            });
        } else {
            // Fallback for older browsers
            window.scrollTo(0, offsetPosition);
        }
    }

    /**
     * Handle navigation link click
     * @param {Event} event - Click event
     */
    function handleNavigationClick(event) {
        const link = event.currentTarget;


        // Extract target ID from href attribute (e.g., "#biorempp-section")
        const href = link.getAttribute('href');

        if (!href || !href.startsWith('#')) {
            return;
        }

        const targetId = href.substring(1); // Remove '#'

        // CRITICAL: Prevent ALL default behaviors
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();

        // Find target element
        const targetElement = document.getElementById(targetId);

        if (targetElement) {

            // Small delay to ensure Dash doesn't interfere
            setTimeout(() => {
                scrollToElement(targetElement);

                // Update URL hash WITHOUT triggering scroll
                // This prevents browser's default hash navigation
                if (history.replaceState) {
                    history.replaceState(null, null, '#' + targetId);
                }
            }, 50);

        } else {
            const allIds = Array.from(document.querySelectorAll('[id]')).map(el => el.id);
            allIds.slice(0, 50).forEach((id, index) => {
            });

            // Check for similar IDs
            const similarIds = allIds.filter(id => id.includes(targetId.split('-')[1]));
            if (similarIds.length > 0) {
            }
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


        let attachedCount = 0;
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href.startsWith('#')) {
                // Remove old listeners to prevent duplicates
                link.removeEventListener('click', handleNavigationClick);

                // Add new listener with capture phase to intercept early
                link.addEventListener('click', handleNavigationClick, true);

                attachedCount++;
            } else {
            }
        });

        return attachedCount;
    }

    /**
     * Attach click handlers to suggestion UC links
     */
    function attachSuggestionHandlers() {
        // Find all suggestion links (they have class "suggestion-uc-link")
        const suggestionLinks = document.querySelectorAll('.suggestion-uc-link');


        let attachedCount = 0;
        suggestionLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && href.startsWith('#')) {
                // Remove old listeners to prevent duplicates
                link.removeEventListener('click', handleNavigationClick);

                // Add new listener with capture phase
                link.addEventListener('click', handleNavigationClick, true);

                attachedCount++;
            }
        });

        return attachedCount;
    }

    function preventDefaultHashScroll() {
        // Intercept all hash changes to prevent auto-scroll
        let isManualScroll = false;

        window.addEventListener('hashchange', function (event) {

            if (!isManualScroll) {
                event.preventDefault();
            }

            isManualScroll = false;
        }, false);

    }

    /**
     * Initialize navigation with retry logic
     */
    function initializeNavigation(attempt = 1) {

        const navLinksFound = attachNavigationHandlers();
        const suggestionLinksFound = attachSuggestionHandlers();
        const totalLinksFound = navLinksFound + suggestionLinksFound;

        if (totalLinksFound > 0) {
            return true;
        }

        if (attempt < CONFIG.retryAttempts) {
            setTimeout(() => initializeNavigation(attempt + 1), CONFIG.retryDelay);
        } else {
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
                setTimeout(() => initializeNavigation(), 100);
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

    }

    // ========================================
    // INITIALIZATION
    // ========================================

    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function () {
            preventDefaultHashScroll();
            initializeNavigation();
            observeDOMChanges();
        });
    } else {
        // DOM already loaded
        preventDefaultHashScroll();
        initializeNavigation();
        observeDOMChanges();
    }

    // Listen for page visibility changes (tab switch)
    document.addEventListener('visibilitychange', function () {
        if (!document.hidden) {
            initializeNavigation();
        }
    });

    // Expose API for manual triggering (useful for debugging)
    window.BioRemPP = window.BioRemPP || {};
    window.BioRemPP.navigation = {
        scrollTo: function (targetId) {
            const element = document.getElementById(targetId);
            if (element) {
                scrollToElement(element);
            } else {
            }
        },
        reinitialize: function () {
            return initializeNavigation();
        },
        getConfig: function () {
            return CONFIG;
        },
        debug: function () {
        }
    };


})();
