/**
 * Direct fix for check-in edit buttons
 */
console.log("Loading check-in edit direct fix...");

// Get the original modal functions from the main script
// Ensure the openStaticCheckinModal function is available globally
if (typeof window.openStaticCheckinModal !== 'function') {
    console.log("Creating backup modal function");
    
    // Create a simpler version of the openStaticCheckinModal function
    window.openStaticCheckinModal = function(formAction, status, timeValue, noteValue, opdrachtId) {
        console.log("Opening modal with:", { formAction, status, timeValue, noteValue, opdrachtId });
        
        // Check if the original function exists
        if (typeof window.originalOpenStaticCheckinModal === 'function') {
            return window.originalOpenStaticCheckinModal(formAction, status, timeValue, noteValue, opdrachtId);
        }
        
        // Detect dark mode
        const isDarkMode = document.documentElement.getAttribute('data-bs-theme') === 'dark';
        const bgColor = isDarkMode ? '#1a1d20' : '#fff';
        const textColor = isDarkMode ? '#fff' : '#212529';
        const borderColor = isDarkMode ? '#2c3237' : '#ced4da';
        const inputBgColor = isDarkMode ? '#2c3237' : '#fff';
        
        // Create a fixed position container
        const modalContainer = document.createElement('div');
        modalContainer.id = 'emergency-modal-container';
        Object.assign(modalContainer.style, {
            position: 'fixed',
            display: 'block',
            top: '0',
            left: '0',
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            zIndex: '99999'
        });
        
        // Create the modal content
        const modalContent = document.createElement('div');
        modalContent.className = 'modal-content';
        Object.assign(modalContent.style, {
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            backgroundColor: bgColor,
            color: textColor,
            padding: '0',
            borderRadius: '5px',
            maxWidth: '500px',
            width: '90%',
            boxShadow: '0 5px 15px rgba(0,0,0,0.3)'
        });
        
        // Create the form
        modalContent.innerHTML = `
            <div style="background:#1B3B6F; color:white; padding:15px; display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid #0d2b5a; border-top-left-radius:5px; border-top-right-radius:5px;">
                <h5 style="margin:0; font-size:18px; font-weight:600;">Edit Check-in</h5>
                <button id="static-modal-close" style="background:transparent; border:none; color:white; font-size:24px; cursor:pointer; padding:0; line-height:1;">&times;</button>
            </div>
            <form action="${formAction}" method="POST" style="margin:0; padding:15px;">
                <div style="margin-bottom:15px;">
                    <label style="display:block; margin-bottom:5px; font-weight:500;">Status</label>
                    <select name="status" class="form-select" style="width:100%; padding:8px; border:1px solid ${borderColor}; border-radius:4px; background-color:${inputBgColor}; color:${textColor};">
                        <option value="working" ${status === 'working' ? 'selected' : ''}>Aan het werk</option>
                        <option value="break" ${status === 'break' ? 'selected' : ''}>Pauze</option>
                        <option value="done" ${status === 'done' ? 'selected' : ''}>Klaar voor vandaag</option>
                    </select>
                </div>
                <div style="margin-bottom:15px;">
                    <label style="display:block; margin-bottom:5px; font-weight:500;">Tijd</label>
                    <input type="time" name="check_in_time" value="${timeValue}" 
                           style="width:100%; padding:8px; border:1px solid ${borderColor}; border-radius:4px; background-color:${inputBgColor}; color:${textColor};">
                </div>
                <div style="margin-bottom:15px;">
                    <label style="display:block; margin-bottom:5px; font-weight:500;">Notitie</label>
                    <input type="text" name="note" value="${noteValue || ''}" 
                           style="width:100%; padding:8px; border:1px solid ${borderColor}; border-radius:4px; background-color:${inputBgColor}; color:${textColor};"
                           placeholder="Waar ben je mee bezig?">
                </div>
                ${opdrachtId ? `<input type="hidden" name="opdracht_id" value="${opdrachtId}">` : ''}
                <div style="margin-top:20px; text-align:right;">
                    <button type="button" onclick="document.getElementById('emergency-modal-container').remove();" 
                            style="margin-right:10px; padding:8px 16px; background:#6c757d; color:white; 
                                   border:none; border-radius:4px; cursor:pointer;">
                        Cancel
                    </button>
                    <button type="submit" 
                            style="padding:8px 16px; background:#E6007E; color:white; 
                                   border:none; border-radius:4px; cursor:pointer;">
                        Save
                    </button>
                </div>
            </form>
        `;
        
        // Add the modal to the page
        modalContainer.appendChild(modalContent);
        document.body.appendChild(modalContainer);
        
        // Close on backdrop click
        modalContainer.addEventListener('click', function(e) {
            if (e.target === modalContainer) {
                modalContainer.remove();
            }
        });
    };
}

// Wait for page load and add direct click handlers
document.addEventListener('DOMContentLoaded', function() {
    console.log("Setting up direct click handlers for check-in edit buttons");
    
    // Directly attach click handlers
    document.querySelectorAll('.edit-checkin-btn').forEach(function(btn) {
        console.log("Found edit button:", btn);
        
        // Replace with a new button to avoid any previous handlers
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);
        
        // Add new click handler
        newBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const formAction = this.getAttribute('data-form-action') || '';
            const status = this.getAttribute('data-status') || 'working';
            const timeValue = this.getAttribute('data-time') || '';
            const noteValue = this.getAttribute('data-note') || '';
            const opdrachtId = this.getAttribute('data-opdracht-id') || '';
            
            console.log("Button clicked with data:", {
                formAction, status, timeValue, noteValue, opdrachtId
            });
            
            if (typeof window.openStaticCheckinModal === 'function') {
                window.openStaticCheckinModal(formAction, status, timeValue, noteValue, opdrachtId);
            } else {
                console.error("openStaticCheckinModal function not available!");
            }
            
            return false;
        });
    });
});
