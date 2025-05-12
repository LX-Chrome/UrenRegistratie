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
});
