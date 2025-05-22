/**
 * Enhanced modal handling for admin functionality
 */
console.log("Loading admin modal enhancements...");

// Run when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log("Setting up admin modal handlers");
    
    // First, collect all available roles from the existing modals, ensuring no duplicates
    const availableRoles = [];
    const seenRoleIds = new Set();
    
    document.querySelectorAll('select[id^="role_id"] option').forEach(option => {
        const roleId = option.value;
        // Only add this role if we haven't seen it before
        if (!seenRoleIds.has(roleId)) {
            seenRoleIds.add(roleId);
            availableRoles.push({
                id: roleId,
                name: option.textContent.trim()
            });
        }
    });
    
    console.log("Available roles:", availableRoles);
    
    /**
     * Create a more reliable change role modal
     */
    function createChangeRoleModal(userId, username, formAction, currentRoleId) {
        console.log("Creating custom change role modal for user:", username);
        
        // Get roles data from our stored collection instead of the page
        const roles = availableRoles.length > 0 ? availableRoles : [];
        
        // If no roles found, try to get them from the server via AJAX as a last resort
        if (roles.length === 0) {
            console.warn("No roles found in collection, trying to fetch from server");
            fetch('/admin/get_roles_json')
                .then(response => response.json())
                .then(data => {
                    if (data.roles && data.roles.length > 0) {
                        // Create modal with fetched roles
                        createModalWithRoles(userId, username, formAction, currentRoleId, data.roles);
                    }
                })
                .catch(error => {
                    console.error("Failed to fetch roles:", error);
                    // Create modal with empty roles as fallback
                    createModalWithRoles(userId, username, formAction, currentRoleId, []);
                });
        } else {
            // Create modal with our collected roles
            createModalWithRoles(userId, username, formAction, currentRoleId, roles);
        }
    }
    
    /**
     * Create the actual modal with given roles
     */
    function createModalWithRoles(userId, username, formAction, currentRoleId, roles) {
        // Detect dark mode
        const isDarkMode = document.documentElement.getAttribute('data-bs-theme') === 'dark';
        const bgColor = isDarkMode ? '#1a1d20' : '#fff';
        const textColor = isDarkMode ? '#fff' : '#212529';
        const borderColor = isDarkMode ? '#2c3237' : '#ced4da';
        const inputBgColor = isDarkMode ? '#2c3237' : '#fff';
        
        // Create modal container
        const modalContainer = document.createElement('div');
        modalContainer.id = 'custom-role-modal-container';
        Object.assign(modalContainer.style, {
            position: 'fixed',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            top: '0',
            left: '0',
            width: '100%',
            height: '100%',
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            zIndex: '99999'
        });
        
        // Create modal content with improved styling
        const modalContent = document.createElement('div');
        modalContent.className = 'custom-modal-content';
        Object.assign(modalContent.style, {
            backgroundColor: bgColor,
            color: textColor,
            borderRadius: '8px',
            maxWidth: '500px',
            width: '90%',
            boxShadow: '0 10px 25px rgba(0,0,0,0.4)',
            padding: '0',
            position: 'relative',
            animation: 'modalFadeIn 0.3s ease-out'
        });
        
        // Add animation keyframes
        const styleSheet = document.createElement('style');
        styleSheet.textContent = `
            @keyframes modalFadeIn {
                from { opacity: 0; transform: translateY(-20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            @keyframes buttonHover {
                from { transform: translateY(0); }
                to { transform: translateY(-2px); }
            }
        `;
        document.head.appendChild(styleSheet);
        
        // Create role options HTML
        let roleOptionsHtml = '';
        
        if (roles.length > 0) {
            roles.forEach(role => {
                const isSelected = role.id === currentRoleId ? 'selected' : '';
                roleOptionsHtml += `<option value="${role.id}" ${isSelected}>${role.name}</option>`;
            });
        } else {
            console.error("No roles available to populate modal");
            roleOptionsHtml = '<option value="">Error loading roles</option>';
        }
        
        // Create modal content HTML with improved styling
        modalContent.innerHTML = `
            <div style="background:#1B3B6F; color:white; padding:15px; display:flex; align-items:center; justify-content:space-between; border-bottom:1px solid #0d2b5a; border-top-left-radius:8px; border-top-right-radius:8px;">
                <h5 style="margin:0; font-size:18px; font-weight:600;">Rol wijzigen voor ${username}</h5>
                <button id="custom-modal-close" style="background:transparent; border:none; color:white; font-size:24px; cursor:pointer; padding:0; line-height:1; transition:transform 0.2s ease;">&times;</button>
            </div>
            <form action="${formAction}" method="POST" style="margin:0; padding:20px;">
                <div style="margin-bottom:20px;">
                    <label for="custom-role-select" style="display:block; margin-bottom:8px; font-weight:500;">Selecteer rol</label>
                    <select id="custom-role-select" name="role_id" class="form-select" style="width:100%; padding:10px; border:1px solid ${borderColor}; border-radius:6px; background-color:${inputBgColor}; color:${textColor}; font-size:16px;" required>
                        ${roleOptionsHtml}
                    </select>
                </div>
                
                ${userId === getUserId() ? `
                <div style="margin-bottom:20px; padding:15px; background-color:#fff3cd; color:#856404; border-radius:6px; border:1px solid #ffeeba; display:flex; align-items:center;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:10px;">
                        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                        <line x1="12" y1="9" x2="12" y2="13"></line>
                        <line x1="12" y1="17" x2="12.01" y2="17"></line>
                    </svg>
                    <span><strong>Waarschuwing:</strong> Je kunt je eigen admin rol niet downgraden.</span>
                </div>
                ` : ''}
                
                <div style="margin-top:25px; text-align:right;">
                    <button type="button" id="custom-modal-cancel" style="margin-right:12px; padding:10px 18px; background:#6c757d; color:white; border:none; border-radius:6px; cursor:pointer; font-size:16px; transition:all 0.2s ease;">
                        Annuleren
                    </button>
                    <button type="submit" style="padding:10px 18px; background:#E6007E; color:white; border:none; border-radius:6px; cursor:pointer; font-size:16px; transition:all 0.2s ease;">
                        Rol opslaan
                    </button>
                </div>
            </form>
        `;
        
        // Add to document
        modalContainer.appendChild(modalContent);
        document.body.appendChild(modalContainer);
        
        // Add hover effects to buttons
        const buttons = modalContainer.querySelectorAll('button');
        buttons.forEach(button => {
            button.addEventListener('mouseover', function() {
                this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
                this.style.transform = 'translateY(-2px)';
            });
            
            button.addEventListener('mouseout', function() {
                this.style.boxShadow = 'none';
                this.style.transform = 'translateY(0)';
            });
        });
        
        // Add event listeners
        modalContainer.querySelector('#custom-modal-close').addEventListener('click', function() {
            modalContainer.remove();
        });
        
        modalContainer.querySelector('#custom-modal-cancel').addEventListener('click', function() {
            modalContainer.remove();
        });
        
        // Close on backdrop click
        modalContainer.addEventListener('click', function(e) {
            if (e.target === modalContainer) {
                modalContainer.remove();
            }
        });
    }
    
    // Helper function to get current user ID
    function getUserId() {
        // Try to extract from HTML
        const userIdMeta = document.querySelector('meta[name="user-id"]');
        if (userIdMeta) {
            return userIdMeta.getAttribute('content');
        }
        
        // If no meta tag, try to find from URL or other elements
        const adminUrl = window.location.pathname;
        const urlMatch = adminUrl.match(/\/admin\/users\/(\d+)\//);
        
        return urlMatch ? urlMatch[1] : null;
    }
    
    // Find and set up all role change buttons
    const roleChangeButtons = document.querySelectorAll('[data-bs-toggle="modal"][data-bs-target^="#changeRoleModal"]');
    
    // Store current role IDs before removing the original modals
    const userRoleData = {};
    roleChangeButtons.forEach(button => {
        const userId = button.getAttribute('data-bs-target').replace('#changeRoleModal', '');
        const modalId = button.getAttribute('data-bs-target');
        const modal = document.querySelector(modalId);
        
        if (modal) {
            const roleSelect = modal.querySelector('select[name="role_id"]');
            if (roleSelect) {
                const selectedOption = roleSelect.querySelector('option[selected]');
                if (selectedOption) {
                    userRoleData[userId] = selectedOption.value;
                } else {
                    const selectedValue = Array.from(roleSelect.options)
                        .find(option => option.selected)?.value;
                    if (selectedValue) {
                        userRoleData[userId] = selectedValue;
                    }
                }
            }
        }
    });
    
    console.log("Stored user role data:", userRoleData);
    
    // First, completely remove all Bootstrap role modals to prevent any conflicts
    roleChangeButtons.forEach(button => {
        const modalId = button.getAttribute('data-bs-target');
        const bootstrapModal = document.querySelector(modalId);
        
        if (bootstrapModal) {
            console.log("Removing original Bootstrap modal:", modalId);
            bootstrapModal.remove();
        }
    });
    
    // Now set up our custom modals
    roleChangeButtons.forEach(button => {
        console.log("Setting up role change button:", button);
        
        // Get user data
        const userId = button.getAttribute('data-bs-target').replace('#changeRoleModal', '');
        const userRow = button.closest('tr');
        const username = userRow.cells[1].textContent.trim();
        const formAction = `/admin/users/${userId}/set_role`;
        
        // Use the stored role ID if available
        let currentRoleId = userRoleData[userId] || null;
        
        if (!currentRoleId) {
            // Fallback method: try to get current role from the row's badge
            const roleBadge = userRow.querySelector('td:nth-child(4) .badge');
            if (roleBadge) {
                const roleName = roleBadge.textContent.trim();
                // Find the role ID that matches this name
                currentRoleId = availableRoles.find(role => role.name.includes(roleName))?.id;
            }
        }
        
        console.log(`Setting up button for user ${userId} (${username}) with current role ID: ${currentRoleId}`);
        
        // Remove Bootstrap's data-bs-toggle to prevent the default modal from showing
        button.removeAttribute('data-bs-toggle');
        button.removeAttribute('data-bs-target');
        
        // Replace click behavior
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Create our custom modal instead
            createChangeRoleModal(userId, username, formAction, currentRoleId);
            
            return false;
        });
    });
    
    // Cleanup any existing modals or elements that might cause conflicts
    const cleanupGlitchingModals = function() {
        // Remove any stray backdrop elements
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => backdrop.remove());
        
        // Remove the 'modal-open' class from body if it exists
        document.body.classList.remove('modal-open');
        
        // Reset any inline styles that Bootstrap might have added
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    };
    
    // Run cleanup on page load and after a short delay
    cleanupGlitchingModals();
    setTimeout(cleanupGlitchingModals, 500);
}); 