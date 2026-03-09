document.addEventListener("DOMContentLoaded", function() {
    // Wait a bit for GLightbox to be fully loaded
    setTimeout(function() {
        if (typeof GLightbox !== 'undefined') {
            console.log('[GLightbox] Initializing GLightbox...');
            var lightbox = GLightbox({
                selector: '.glightbox',
                touchNavigation: true,
                zoomable: true,
                loop: false,
                closeButton: true,
                closeOnOutsideClick: true
            });
            console.log('[GLightbox] Initialized successfully!');
        } else {
            console.error('[GLightbox] GLightbox library not found!');
        }
    }, 100);
});
