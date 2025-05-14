document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons
    feather.replace();
    
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
                feather.replace();
            }
        }
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
            feather.replace();
            
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

// Function to make card header buttons mobile-friendly
function makeMobileCardButtons() {
    if (window.innerWidth < 768) {
        const cardHeaders = document.querySelectorAll('.card-header');
        cardHeaders.forEach(header => {
            const buttonContainer = header.querySelector('.d-flex');
            if (buttonContainer) {
                buttonContainer.classList.add('flex-wrap', 'gap-2');
                
                const buttons = buttonContainer.querySelectorAll('.btn');
                buttons.forEach(button => {
                    if (!button.classList.contains('dropdown-toggle')) {
                        button.classList.add('w-100', 'mb-2');
                    }
                });
            }
        });
    }
}
