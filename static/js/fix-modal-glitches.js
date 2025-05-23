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
        // Remove any modal backdrops
        document.querySelectorAll('.modal-backdrop').forEach(backdrop => {
            console.log("Removing stray modal backdrop");
            backdrop.remove();
        });
        
        // Remove modal-open class from body
        if (document.body.classList.contains('modal-open')) {
            console.log("Removing modal-open class from body");
            document.body.classList.remove('modal-open');
        }
        
        // Get saved scroll position
        const scrollY = window.modalScrollY || 0;
        
        // Reset inline styles that Bootstrap might have added
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        document.body.style.position = '';
        document.body.style.width = '';
        document.body.style.height = '';
        document.body.style.top = '';
        
        // Restore scroll position if body was fixed
        if (document.body.style.position === 'fixed') {
            window.scrollTo(0, scrollY);
        }
        
        // Ensure all hidden modals stay hidden
        document.querySelectorAll('.hidden-bootstrap-modal').forEach(modal => {
            modal.style.display = 'none';
            modal.style.visibility = 'hidden';
            modal.style.opacity = '0';
            modal.style.pointerEvents = 'none';
            modal.classList.remove('show');
            
            // Remove any inline styles that Bootstrap might have added
            modal.style.paddingRight = '';
        });
    }
    
    // Run cleanup when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', cleanupModalArtifacts);
    } else {
        cleanupModalArtifacts();
    }
    
    // Also run cleanup when window loads and after a short delay
    window.addEventListener('load', cleanupModalArtifacts);
    setTimeout(cleanupModalArtifacts, 300);
    setTimeout(cleanupModalArtifacts, 1000);
    
    // Monitor for modal events
    document.addEventListener('click', function(e) {
        // If a data-bs-dismiss="modal" element is clicked, run cleanup
        if (e.target.getAttribute('data-bs-dismiss') === 'modal') {
            setTimeout(cleanupModalArtifacts, 50);
        }
    }, true);
    
    // Handle any "shown.bs.modal" events
    document.addEventListener('shown.bs.modal', function(e) {
        console.log("Modal shown event detected, checking if it's one we want to suppress");
        const modal = e.target;
        
        if (modal.classList.contains('hidden-bootstrap-modal')) {
            console.log("Suppressing unwanted modal:", modal.id);
            
            // Get any associated Bootstrap modal instance
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                try {
                    const bootstrapModal = bootstrap.Modal.getInstance(modal);
                    if (bootstrapModal) {
                        console.log("Hiding Bootstrap modal instance");
                        bootstrapModal.hide();
                    }
                } catch (err) {
                    console.error("Error trying to hide modal:", err);
                }
            }
            
            // Force cleanup
            setTimeout(cleanupModalArtifacts, 50);
        }
    });
})(); 