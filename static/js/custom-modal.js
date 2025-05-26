/**
 * Fixed Position Modal Implementation
 * Prevents any positioning conflicts or glitching between positions
 */

// Global variable to track if we've already set up the modal
let modalSetupComplete = false;

document.addEventListener('DOMContentLoaded', function() {
    // Only set up modal once
    if (modalSetupComplete) return;
    modalSetupComplete = true;
    
    console.log("Initializing fixed position modal system...");
    
    // Remove any existing modals
    const existingModal = document.getElementById('static-checkin-modal-container');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Create a fixed-position container that will not move
    const modalContainer = document.createElement('div');
    modalContainer.id = 'static-checkin-modal-container';
    
    // Apply styles directly to the element to avoid CSS conflicts
    Object.assign(modalContainer.style, {
        position: 'fixed',
        display: 'none',
        top: '0',
        left: '0',
        width: '100%',
        height: '100%',
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        zIndex: '99999', // Use a very high z-index
        overflow: 'hidden',
        padding: '0',
        margin: '0',
        border: 'none',
        transition: 'none',
        animation: 'none',
        transform: 'none'
    });
    
    // Create the modal content box with absolute positioning
    const modalBox = document.createElement('div');
    modalBox.id = 'static-checkin-modal-box';
    
    // Apply fixed styles directly to the element
    Object.assign(modalBox.style, {
        position: 'absolute',
        top: '50%',
        left: '50%',
        width: '400px',
        maxWidth: '90%',
        transform: 'translate(-50%, -50%)',
        backgroundColor: document.documentElement.getAttribute('data-bs-theme') === 'dark' ? '#242729' : '#ffffff',
        color: document.documentElement.getAttribute('data-bs-theme') === 'dark' ? '#ffffff' : '#212529',
        borderRadius: '8px',
        boxShadow: '0 5px 15px rgba(0, 0, 0, 0.3)',
        transition: 'none',
        animation: 'none',
        zIndex: '100000',
        overflow: 'hidden'
    });
    
    // Add the box to the container
    modalContainer.appendChild(modalBox);
    
    // Add the container to the body
    document.body.appendChild(modalContainer);
    
    // Create a function to open the modal with the given content
    window.openStaticCheckinModal = function(formAction, status, timeValue, noteValue, opdrachtId) {
        console.log("Opening static check-in modal", { formAction, status, timeValue, noteValue, opdrachtId });
        
        // Get all available clients and assignments
        const clients = window.availableClients || [];
        const opdrachten = window.availableOpdrachten || [];
        
        // Create client options
        let clientOptions = '<option value="">Select Client</option>';
        clients.forEach(client => {
            clientOptions += `<option value="${client.id}">${client.name}</option>`;
        });
        
        // Create assignment options with data-client attributes
        let assignmentOptions = '<option value="">Select Assignment</option>';
        opdrachten.forEach(opdracht => {
            assignmentOptions += `<option value="${opdracht.id}" data-client="${opdracht.klant_id}" ${opdracht.id == opdrachtId ? 'selected' : ''}>${opdracht.titel}</option>`;
        });
        
        // Create the static modal content
        modalBox.innerHTML = `
            <div style="background:#1B3B6F; color:white; padding:15px; display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid #0d2b5a;">
                <h5 style="margin:0; font-size:18px; font-weight:600;">Edit Check-in</h5>
                <button id="static-modal-close" style="background:transparent; border:none; color:white; font-size:24px; cursor:pointer; padding:0; line-height:1;">&times;</button>
            </div>
            <form action="${formAction}" method="POST" id="static-checkin-form" style="margin:0; padding:0;">
                <div style="padding:15px;">
                    <div style="margin-bottom:15px;">
                        <label style="display:block; margin-bottom:5px; font-weight:500;">Status</label>
                        <select name="status" class="form-select" style="width:100%; padding:8px; border:1px solid #ced4da; border-radius:4px;" required>
                            <option value="working" ${status === 'working' ? 'selected' : ''}>Aan het werk</option>
                            <option value="break" ${status === 'break' ? 'selected' : ''}>Pauze</option>
                            <option value="done" ${status === 'done' ? 'selected' : ''}>Klaar voor vandaag</option>
                        </select>
                    </div>
                    <div style="margin-bottom:15px;">
                        <label style="display:block; margin-bottom:5px; font-weight:500;">Tijd</label>
                        <input type="time" name="check_in_time" value="${timeValue}" 
                               style="width:100%; padding:8px; border:1px solid #ced4da; border-radius:4px;">
                    </div>
                    <div style="margin-bottom:15px;">
                        <label style="display:block; margin-bottom:5px; font-weight:500;">Notitie</label>
                        <input type="text" name="note" value="${noteValue || ''}" 
                               style="width:100%; padding:8px; border:1px solid #ced4da; border-radius:4px;"
                               placeholder="Waar ben je mee bezig?">
                    </div>
                    <div style="margin-bottom:15px;">
                        <label style="display:block; margin-bottom:5px; font-weight:500;">Client</label>
                        <select id="client-select" onchange="filterAssignmentsInModal()" 
                                style="width:100%; padding:8px; border:1px solid #ced4da; border-radius:4px;">
                            ${clientOptions}
                        </select>
                    </div>
                    <div style="margin-bottom:15px;">
                        <label style="display:block; margin-bottom:5px; font-weight:500;">Opdracht</label>
                        <select name="opdracht_id" id="opdracht-select"
                                style="width:100%; padding:8px; border:1px solid #ced4da; border-radius:4px;">
                            ${assignmentOptions}
                        </select>
                    </div>
                </div>
                <div style="padding:15px; border-top:1px solid #dee2e6; text-align:right; background-color: ${document.documentElement.getAttribute('data-bs-theme') === 'dark' ? '#1a1d20' : '#f8f9fa'}">
                    <button type="button" id="static-modal-cancel" 
                            style="margin-right:10px; padding:8px 16px; background:#6c757d; color:white; 
                                   border:none; border-radius:4px; cursor:pointer;">
                        Cancel
                    </button>
                    <button type="submit" 
                            style="padding:8px 16px; background:#E6007E; color:white; 
                                   border:none; border-radius:4px; cursor:pointer;">
                        Save Changes
                    </button>
                </div>
            </form>
        `;
        
        // Initialize the client dropdown based on the selected assignment
        if (opdrachtId) {
            const selectedOpdracht = opdrachten.find(o => o.id == opdrachtId);
            if (selectedOpdracht) {
                document.getElementById('client-select').value = selectedOpdracht.klant_id;
            }
        }
        
        // Show the modal
        modalContainer.style.display = 'block';
        
        // Store current scroll position
        const scrollY = window.scrollY;
        
        // Lock body scroll with improved method
        document.body.style.position = 'fixed';
        document.body.style.top = `-${scrollY}px`;
        document.body.style.width = '100%';
        document.body.style.height = '100%';
        document.body.style.overflow = 'hidden';
        
        // Add event listeners
        document.getElementById('static-modal-close').addEventListener('click', closeStaticModal);
        document.getElementById('static-modal-cancel').addEventListener('click', closeStaticModal);
        
        // Close on backdrop click
        modalContainer.addEventListener('click', function(e) {
            if (e.target === modalContainer) {
                closeStaticModal();
            }
        });
        
        // Stop propagation on modal box
        modalBox.addEventListener('click', function(e) {
            e.stopPropagation();
        });
        
        // Prevent any mouse wheel events from propagating
        modalContainer.addEventListener('wheel', function(e) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }, { passive: false });
    };
    
    // Function to close the modal
    window.closeStaticModal = function() {
        console.log("Closing static check-in modal");
        
        // Hide the modal
        modalContainer.style.display = 'none';
        
        // Restore body scroll
        const scrollY = parseInt(document.body.style.top || '0') * -1;
        document.body.style.position = '';
        document.body.style.top = '';
        document.body.style.width = '';
        document.body.style.height = '';
        document.body.style.overflow = '';
        
        // Restore scroll position
        window.scrollTo(0, scrollY);
        
        // Clear content to prevent memory leaks
        modalBox.innerHTML = '';
    };
    
    // Function to filter assignments in the modal based on selected client
    window.filterAssignmentsInModal = function() {
        const clientSelect = document.getElementById('client-select');
        const assignmentSelect = document.getElementById('opdracht-select');
        
        if (!clientSelect || !assignmentSelect) return;
        
        const selectedClientId = clientSelect.value;
        
        // Show/hide assignment options based on client selection
        Array.from(assignmentSelect.options).forEach(option => {
            if (option.value === '') {
                // Always show the default option
                option.style.display = '';
            } else {
                const optionClientId = option.getAttribute('data-client');
                option.style.display = (!selectedClientId || optionClientId === selectedClientId) ? '' : 'none';
            }
        });
        
        // Reset assignment selection if the currently selected option is hidden
        const selectedOption = assignmentSelect.options[assignmentSelect.selectedIndex];
        if (selectedOption && selectedOption.value && selectedOption.style.display === 'none') {
            assignmentSelect.value = '';
        }
    };
    
    // Find and process all check-in edit buttons by multiple selectors
    function setupAllEditButtons() {
        console.log("Setting up all check-in edit buttons");
        
        // Target buttons by class and data attribute
        const buttons = document.querySelectorAll('.edit-checkin-btn, [data-bs-target^="#editCheckinModal"]');
        console.log(`Found ${buttons.length} edit buttons`);
        
        buttons.forEach(function(button) {
            // Get data from the button
            const formAction = button.getAttribute('data-form-action') || '';
            const status = button.getAttribute('data-status') || 'working';
            const timeValue = button.getAttribute('data-time') || '';
            const noteValue = button.getAttribute('data-note') || '';
            const opdrachtId = button.getAttribute('data-opdracht-id') || '';
            
            // Remove all Bootstrap-related attributes to prevent conflicts
            button.removeAttribute('data-bs-toggle');
            
            // Keep data-bs-target for identification but disable Bootstrap behavior
            
            // Prevent the button from being processed again
            if (button.getAttribute('data-static-modal-processed')) {
                return;
            }
            
            button.setAttribute('data-static-modal-processed', 'true');
            
            // Add our own click handler
            button.addEventListener('click', function(e) {
                console.log("Edit button clicked", { formAction, status, timeValue, noteValue, opdrachtId });
                e.preventDefault();
                e.stopPropagation();
                
                // Open our static modal
                window.openStaticCheckinModal(formAction, status, timeValue, noteValue, opdrachtId);
                
                return false;
            });
        });
    }
    
    // Initial setup
    setupAllEditButtons();
    
    // Add mutation observer to handle dynamically added buttons
    const observer = new MutationObserver(function(mutations) {
        for (const mutation of mutations) {
            if (mutation.type === 'childList' && mutation.addedNodes.length) {
                setupAllEditButtons();
            }
        }
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
}); 

// Helper function to set up client and assignment data for the modal
window.setupClientAndAssignmentData = function(clients, opdrachten) {
    window.availableClients = clients;
    window.availableOpdrachten = opdrachten;
}; 