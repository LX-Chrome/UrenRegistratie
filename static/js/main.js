// Global tracker for Feather icons initialization
let featherInitialized = false;

// Optimize Feather initialization - only call when needed
function initializeFeather() {
    if (window.feather && !featherInitialized) {
        feather.replace();
        featherInitialized = true;
        console.log('Feather icons initialized');
    }
}

// Update individual icon - more efficient than replacing all
function updateFeatherIcon(element) {
    if (window.feather && element) {
        feather.replace(element);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons
    initializeFeather();
    
    // Theme toggle functionality
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        const themeIcon = themeToggle.querySelector('i');
        const html = document.documentElement;

        // Check for saved theme preference or use system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        const savedTheme = localStorage.getItem('theme') || (prefersDark ? 'dark' : 'light');
        setTheme(savedTheme);

        themeToggle.addEventListener('click', () => {
            const currentTheme = html.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        });

        function setTheme(theme) {
            html.setAttribute('data-bs-theme', theme);
            localStorage.setItem('theme', theme);
            if (themeIcon) {
                themeIcon.setAttribute('data-feather', theme === 'dark' ? 'sun' : 'moon');
                updateFeatherIcon(themeIcon);
            }
            
            // Fix for search box text colors in light mode
            updateFormControlColors(theme);
        }
        
        // Helper function to update form control colors based on theme
        function updateFormControlColors(theme) {
            console.log('Updating form control colors for theme:', theme);
            const formControls = document.querySelectorAll('.form-control');
            formControls.forEach(input => {
                if (theme === 'light') {
                    input.style.color = '#212529';
                    input.style.borderColor = '#ced4da';
                } else {
                    input.style.color = '#fff';
                    input.style.borderColor = '#495057';
                }
            });
        }
        
        // Initial call to set colors based on current theme
        updateFormControlColors(savedTheme);
    }

    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Set default date
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }
    
    // Set up language toggle
    const languageToggle = document.getElementById('languageToggle');
    const languageCheckbox = document.getElementById('languageCheckbox');
    
    if (languageToggle && languageCheckbox && typeof toggleLanguage === 'function') {
        // Set initial state based on current language
        const currentLanguage = localStorage.getItem('language') || 'nl';
        if (currentLanguage === 'en') {
            languageCheckbox.checked = true;
            languageToggle.classList.add('active');
        } else {
            languageCheckbox.checked = false;
            languageToggle.classList.remove('active');
        }
        
        // Add event listener for the checkbox
        languageCheckbox.addEventListener('change', function() {
            toggleLanguage();
        });
        
        console.log('Language toggle initialized');
    }
    
    // The translation handling is now in translations.js with optimized implementation
    
    // Responsive tables enhancement for mobile
    enhanceResponsiveTables();
    
    // Handle navbar on small screens
    setupMobileNavbar();
    
    // Make all buttons in card headers mobile-friendly
    makeMobileCardButtons();

    // Modal Fix for UI Glitches
    // Modified solution that doesn't block all interactivity
    (function() {
        let scrollPosition;
        const body = document.body;
        
        // Disable all scroll events when modal is open
        function disableScroll() {
            scrollPosition = window.pageYOffset || document.documentElement.scrollTop;
            body.style.overflow = 'hidden';
            // Remove fixed positioning which causes issues with click events
            // body.style.position = 'fixed';
            // body.style.top = `-${scrollPosition}px`;
            body.style.width = '100%';
            
            // Only prevent wheel events on the body, not inside modals
            document.addEventListener('wheel', preventBodyScroll, { passive: false });
            document.addEventListener('touchmove', preventBodyScroll, { passive: false });
        }
        
        // Re-enable scrolling when modal is closed
        function enableScroll() {
            body.style.overflow = '';
            body.style.position = '';
            body.style.top = '';
            body.style.width = '';
            window.scrollTo(0, scrollPosition);
            
            // Remove event listeners
            document.removeEventListener('wheel', preventBodyScroll);
            document.removeEventListener('touchmove', preventBodyScroll);
        }
        
        // Only prevent scroll on body, not in modals
        function preventBodyScroll(e) {
            // Check if the target is inside a modal
            let target = e.target;
            while (target && target !== document.body) {
                if (target.classList.contains('modal') || 
                    target.classList.contains('modal-dialog') || 
                    target.classList.contains('modal-content')) {
                    // Let the scroll happen inside modals
                    return true;
                }
                target = target.parentNode;
            }
            
            // Otherwise prevent scroll on body
            e.preventDefault();
            return false;
        }
        
        // Watch for modals opening and closing using Bootstrap events
        document.body.addEventListener('show.bs.modal', function() {
            disableScroll();
        });
        
        document.body.addEventListener('hidden.bs.modal', function() {
            enableScroll();
        });
        
        // Fix all existing modals
        document.querySelectorAll('.modal').forEach(modal => {
            if (!modal.classList.contains('scroll-fixed')) {
                modal.classList.add('scroll-fixed');
                modal.classList.add('stable-modal');
            }
        });
    })();

    // Remove global wheel event prevention that blocks all interaction
    /* 
    window.addEventListener('wheel', function(e) {
        if (document.body.classList.contains('modal-open')) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    }, { passive: false, capture: true });
    
    // Block touch movements too
    window.addEventListener('touchmove', function(e) {
        if (document.body.classList.contains('modal-open')) {
            e.preventDefault();
            e.stopPropagation();
            return false;
        }
    }, { passive: false, capture: true });
    
    // Disable keyboard scrolling
    window.addEventListener('keydown', function(e) {
        if (document.body.classList.contains('modal-open')) {
            // Prevent arrow keys, page up, page down, home, end
            if ([32, 33, 34, 35, 36, 37, 38, 39, 40].includes(e.keyCode)) {
                e.preventDefault();
                return false;
            }
        }
    }, { capture: true });
    */
});

// Function to enhance responsive tables
function enhanceResponsiveTables() {
    const tables = document.querySelectorAll('.table-responsive table');
    
    tables.forEach(table => {
        // Add data attributes for mobile view
        const headerCells = table.querySelectorAll('thead th');
        const headerTexts = Array.from(headerCells).map(cell => cell.textContent.trim());
        
        const bodyRows = table.querySelectorAll('tbody tr');
        bodyRows.forEach(row => {
            const cells = row.querySelectorAll('td');
            cells.forEach((cell, index) => {
                if (index < headerTexts.length) {
                    cell.setAttribute('data-label', headerTexts[index]);
                }
            });
        });
    });
    
    // Add swipe indicator for mobile users
    const tableResponsives = document.querySelectorAll('.table-responsive');
    tableResponsives.forEach(container => {
        if (window.innerWidth < 768 && !container.querySelector('.swipe-indicator')) {
            const indicator = document.createElement('div');
            indicator.className = 'swipe-indicator d-block d-md-none mb-2 text-muted small';
            indicator.innerHTML = '<i data-feather="chevrons-right"></i> <span data-translate="Swipe to see more">Swipe to see more</span>';
            container.prepend(indicator);
            
            // Update only the newly added icon
            const featherIcon = indicator.querySelector('[data-feather]');
            if (featherIcon) {
                updateFeatherIcon(featherIcon);
            }
            
            // Hide indicator after user has swiped
            container.addEventListener('scroll', function() {
                indicator.style.opacity = '0.2';
                setTimeout(() => {
                    indicator.style.display = 'none';
                }, 1000);
            }, { once: true });
        }
    });
}

// Function to handle mobile navbar
function setupMobileNavbar() {
    const navbar = document.querySelector('.navbar');
    let lastScrollTop = 0;
    
    if (navbar) {
        window.addEventListener('scroll', function() {
            let scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (window.innerWidth < 992) {  // Only for mobile and tablet
                if (scrollTop > lastScrollTop && scrollTop > 100) {
                    // Scrolling down - hide navbar
                    navbar.style.top = '-70px';
                } else {
                    // Scrolling up - show navbar
                    navbar.style.top = '0';
                }
            } else {
                navbar.style.top = '0';  // Always show on desktop
            }
            
            lastScrollTop = scrollTop;
        });
    }
}

function makeMobileCardButtons() {
    if (window.innerWidth < 768) {
        document.querySelectorAll('.card-header .btn-group').forEach(btnGroup => {
            btnGroup.classList.add('d-flex', 'flex-wrap');
            
            btnGroup.querySelectorAll('.btn').forEach(btn => {
                btn.classList.add('flex-grow-1', 'mb-1');
                btn.style.minWidth = '80px';
            });
        });
    }
}
