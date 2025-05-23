/**
 * Modal Glitch Fixer
 * 
 * This utility script fixes issues with glitching modals by:
 * 1. Cleaning up any orphaned backdrops
 * 2. Removing classes that might cause body scroll issues
 * 3. Ensuring modals don't appear unexpectedly
 */

(function() {
    console.log("Initializing modal glitch fixer...");
    
    // Function to clean up any modal-related artifacts
    function cleanupModalArtifacts() {
        // Only remove orphaned backdrops (ones without an active modal)
        const activeModals = document.querySelectorAll('.modal.show');
        if (activeModals.length === 0) {
            document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
                console.log("Removing stray modal backdrop");
                backdrop.remove();
            });
            
            // Remove modal-open class from body only if no modal is active
            if (document.body.classList.contains('modal-open')) {
                console.log("Removing modal-open class from body");
                document.body.classList.remove('modal-open');
            }
            
            // Reset body styles only when no modal is active
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
        }
        
        // These should always be reset to avoid position:fixed issues
        document.body.style.position = '';
        document.body.style.width = '';
        document.body.style.height = '';
        document.body.style.top = '';
        
        // Restore scroll position if body was fixed
        if (document.body.style.position === 'fixed') {
            const scrollY = window.modalScrollY || 0;
            window.scrollTo(0, scrollY);
        }
        
        // Ensure all hidden modals stay hidden
        document.querySelectorAll('.modal:not(.show)').forEach(modal => {
            modal.style.display = 'none';
        });
    }
    
    // Run cleanup when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', cleanupModalArtifacts);
    } else {
        cleanupModalArtifacts();
    }
    
    // Also run cleanup when window loads
    window.addEventListener('load', cleanupModalArtifacts);
    
    // Run cleanup with delay only once to avoid potential conflicts
    setTimeout(cleanupModalArtifacts, 1000);
    
    // Monitor for modal events
    document.addEventListener('click', function(e) {
        // If a data-bs-dismiss="modal" element is clicked, run cleanup
        if (e.target.getAttribute('data-bs-dismiss') === 'modal') {
            setTimeout(cleanupModalArtifacts, 100);
        }
    });
    
    // Handle any "shown.bs.modal" events
    document.addEventListener('shown.bs.modal', function(e) {
        console.log("Modal shown event detected");
    });
    
    // Handle modal hidden events
    document.addEventListener('hidden.bs.modal', function(e) {
        console.log("Modal hidden event detected");
        setTimeout(cleanupModalArtifacts, 100);
    });
})(); 