/**
 * Time Entry Modal Fix
 * 
 * This script fixes Bootstrap modal issues when adding/editing time entries.
 * It specifically addresses issues that cause crashes when showing modals.
 */
console.log("Loading time entry modal fix...");

document.addEventListener('DOMContentLoaded', function() {
    console.log("Applying time entry modal fixes");
    
    /**
     * Replace Bootstrap modal behavior with more reliable implementation
     * for time entry modals
     */
    function fixTimeEntryModals() {
        // Manage body scrolling and backdrop
        function manageBodyState(isActive) {
            if (isActive) {
                document.body.style.overflow = 'hidden';
                document.body.style.paddingRight = '15px'; // Compensate for scrollbar
                
                // Create backdrop if it doesn't exist
                if (!document.querySelector('.modal-backdrop')) {
                    const backdrop = document.createElement('div');
                    backdrop.className = 'modal-backdrop fade show';
                    document.body.appendChild(backdrop);
                }
                
                // Add modal-open class to body
                document.body.classList.add('modal-open');
            } else {
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
                
                // Remove backdrop
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                }
                
                // Remove modal-open class from body
                document.body.classList.remove('modal-open');
            }
        }
        
        // Get all time entry related modals
        const modals = [
            document.getElementById('addEntryModal'),
            document.getElementById('importEntriesModal'),
            document.getElementById('deleteConfirmModal')
        ].filter(modal => modal !== null);
        
        // Also include all edit modals (which have IDs like editEntryModal1, editEntryModal2, etc.)
        document.querySelectorAll('[id^="editEntryModal"]').forEach(modal => {
            if (!modals.includes(modal)) {
                modals.push(modal);
            }
        });
        
        // Fix each modal
        modals.forEach(modal => {
            if (!modal) return;
            
            const modalId = modal.id;
            console.log(`Fixing modal: ${modalId}`);
            
            // Find all triggers that would open this modal
            document.querySelectorAll(`[data-bs-target="#${modalId}"]`).forEach(trigger => {
                // Remove the Bootstrap data attribute to prevent default behavior
                const target = trigger.getAttribute('data-bs-target');
                trigger.removeAttribute('data-bs-toggle');
                trigger.removeAttribute('data-bs-target');
                
                // Add our own click handler
                trigger.addEventListener('click', function(e) {
                    e.preventDefault();
                    const modalElement = document.querySelector(target);
                    if (modalElement) {
                        // Show modal manually
                        modalElement.style.display = 'block';
                        modalElement.classList.add('show');
                        manageBodyState(true);
                    }
                });
            });
            
            // Handle close buttons within this modal
            modal.querySelectorAll('.btn-close, [data-bs-dismiss="modal"]').forEach(closeButton => {
                // Remove Bootstrap data attribute
                closeButton.removeAttribute('data-bs-dismiss');
                
                // Add our own click handler
                closeButton.addEventListener('click', function() {
                    modal.style.display = 'none';
                    modal.classList.remove('show');
                    manageBodyState(false);
                });
            });
            
            // Escape key to close modal
            document.addEventListener('keydown', function(event) {
                if (event.key === 'Escape' && modal.classList.contains('show')) {
                    modal.style.display = 'none';
                    modal.classList.remove('show');
                    manageBodyState(false);
                }
            });
        });
    }
    
    // Apply the fixes
    fixTimeEntryModals();
    
    // Fix for existing script functions
    if (typeof confirmDelete === 'function') {
        // Override the confirmDelete function to use our custom modal handling
        window.confirmDelete = function(deleteUrl) {
            const modal = document.getElementById('deleteConfirmModal');
            
            // Set the delete button href
            document.getElementById('confirmDeleteBtn').href = deleteUrl;
            
            // Show the modal manually
            modal.style.display = 'block';
            modal.classList.add('show');
            
            // Manage body state
            document.body.style.overflow = 'hidden';
            document.body.style.paddingRight = '15px';
            document.body.classList.add('modal-open');
            
            // Add backdrop if needed
            if (!document.querySelector('.modal-backdrop')) {
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
            }
        };
    }
    
    // Fix for dashboard redirect
    if (document.getElementById('redirect_to_dashboard')) {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('from_dashboard')) {
            document.getElementById('redirect_to_dashboard').value = 'true';
        }
    }
    
    // Apply the fix for "new" modal on load
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('new') && document.getElementById('addEntryModal')) {
        const modal = document.getElementById('addEntryModal');
        modal.style.display = 'block';
        modal.classList.add('show');
        
        // Manage body state
        document.body.style.overflow = 'hidden';
        document.body.style.paddingRight = '15px';
        document.body.classList.add('modal-open');
        
        // Add backdrop if needed
        if (!document.querySelector('.modal-backdrop')) {
            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop fade show';
            document.body.appendChild(backdrop);
        }
    }
    
    // Apply the fix for "edit" modal on load
    if (urlParams.has('edit') && urlParams.get('edit')) {
        const editId = urlParams.get('edit');
        const editModalId = `editEntryModal${editId}`;
        const editModal = document.getElementById(editModalId);
        
        if (editModal) {
            editModal.style.display = 'block';
            editModal.classList.add('show');
            
            // Manage body state
            document.body.style.overflow = 'hidden';
            document.body.style.paddingRight = '15px';
            document.body.classList.add('modal-open');
            
            // Add backdrop if needed
            if (!document.querySelector('.modal-backdrop')) {
                const backdrop = document.createElement('div');
                backdrop.className = 'modal-backdrop fade show';
                document.body.appendChild(backdrop);
            }
        }
    }
}); 