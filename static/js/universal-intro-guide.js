/**
 * Universal Intro Guide System
 * Provides consistent, user-friendly guided tours across all pages
 * Enhanced for better user experience and universal compatibility
 */

class UniversalIntroGuide {
    constructor() {
        this.currentPage = this.detectCurrentPage();
        this.isFirstVisit = this.checkFirstVisit();
        this.language = this.detectLanguage();
        this.tourSteps = [];
        this.init();
    }

    init() {
        // Wait for page to be fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeGuide());
        } else {
            this.initializeGuide();
        }
    }

    initializeGuide() {
        this.createTourButton();
        this.setupIntroJS();
        this.generateTourSteps();
        
        // Auto-start tour for first-time visitors on dashboard
        if (this.isFirstVisit && this.currentPage === 'dashboard') {
            setTimeout(() => {
                this.showWelcomeModal();
            }, 1500);
        }

        // Listen for language changes
        this.setupLanguageListener();
    }

    detectCurrentPage() {
        const path = window.location.pathname.toLowerCase();
        const pageMap = {
            '/': 'dashboard',
            '/dashboard': 'dashboard',
            '/time_entries': 'time_entries',
            '/klanten': 'klanten',
            '/medewerkers': 'medewerkers',
            '/opdrachten': 'opdrachten',
            '/facturen': 'facturen',
            '/reports': 'reports',
            '/admin': 'admin'
        };
        
        // Check for exact matches first
        if (pageMap[path]) {
            return pageMap[path];
        }
        
        // Check for partial matches
        for (const [route, page] of Object.entries(pageMap)) {
            if (path.includes(route) && route !== '/') {
                return page;
            }
        }
        
        return 'general';
    }

    detectLanguage() {
        // Check localStorage first
        const savedLang = localStorage.getItem('language');
        if (savedLang) return savedLang;
        
        // Check language toggle state
        const langCheckbox = document.getElementById('languageCheckbox');
        if (langCheckbox) {
            return langCheckbox.checked ? 'en' : 'nl';
        }
        
        // Default to Dutch
        return 'nl';
    }

    setupLanguageListener() {
        const langCheckbox = document.getElementById('languageCheckbox');
        if (langCheckbox) {
            langCheckbox.addEventListener('change', () => {
                this.language = langCheckbox.checked ? 'en' : 'nl';
                this.updateTourContent();
            });
        }
    }

    updateTourContent() {
        // Regenerate tour steps with new language
        this.generateTourSteps();
        
        // Update tour button text
        const tourButton = document.getElementById('universal-tour-btn');
        if (tourButton) {
            const buttonText = tourButton.querySelector('.tour-btn-text');
            if (buttonText) {
                buttonText.textContent = this.getText('help');
            }
            tourButton.title = this.getText('startTourTooltip');
        }
        
        // Update intro.js configuration if active
        if (this.introInstance) {
            this.setupIntroJS();
        }
    }

    getText(key) {
        const texts = {
            nl: {
                help: 'Hulp',
                startTourTooltip: 'Start rondleiding - Leer hoe je deze pagina gebruikt',
                next: 'Volgende →',
                prev: '← Vorige',
                done: '✓ Afronden',
                skip: '× Overslaan',
                welcomeTitle: '👋 Welkom bij UrenRegistratie!',
                welcomeMessage: 'Het lijkt erop dat dit je eerste bezoek is. Wil je een rondleiding om te leren hoe alles werkt?',
                welcomeSkip: 'Overslaan',
                welcomeStart: '🚀 Start Rondleiding',
                tourCompleteTitle: '🎉 Rondleiding Voltooid!',
                tourCompleteMessage: 'Je hebt de rondleiding succesvol afgerond. Je kunt altijd opnieuw een rondleiding starten door op de hulp-knop te klikken.',
                tourCompleteButton: 'Geweldig!',
                noTourTitle: 'ℹ️ Geen rondleiding beschikbaar',
                noTourMessage: 'Voor deze pagina is momenteel geen specifieke rondleiding beschikbaar.',
                noTourSuggestion: 'Gebruik de navigatie om naar andere onderdelen te gaan waar wel rondleidingen beschikbaar zijn.',
                noTourButton: 'Begrepen'
            },
            en: {
                help: 'Help',
                startTourTooltip: 'Start tour - Learn how to use this page',
                next: 'Next →',
                prev: '← Previous',
                done: '✓ Finish',
                skip: '× Skip',
                welcomeTitle: '👋 Welcome to UrenRegistratie!',
                welcomeMessage: 'It looks like this is your first visit. Would you like a tour to learn how everything works?',
                welcomeSkip: 'Skip',
                welcomeStart: '🚀 Start Tour',
                tourCompleteTitle: '🎉 Tour Completed!',
                tourCompleteMessage: 'You have successfully completed the tour. You can always start a new tour by clicking the help button.',
                tourCompleteButton: 'Great!',
                noTourTitle: 'ℹ️ No tour available',
                noTourMessage: 'No specific tour is currently available for this page.',
                noTourSuggestion: 'Use the navigation to go to other sections where tours are available.',
                noTourButton: 'Understood'
            }
        };
        
        return texts[this.language]?.[key] || texts.nl[key] || key;
    }

    checkFirstVisit() {
        const hasVisited = localStorage.getItem('intro_guide_completed');
        return !hasVisited;
    }

    markTourCompleted() {
        localStorage.setItem('intro_guide_completed', 'true');
        localStorage.setItem('intro_guide_completed_date', new Date().toISOString());
    }

    createTourButton() {
        // Remove existing tour buttons to prevent duplicates
        document.querySelectorAll('#tour-btn, #start-tour-btn, #universal-tour-btn').forEach(btn => btn.remove());

        const tourButton = document.createElement('button');
        tourButton.id = 'universal-tour-btn';
        tourButton.className = 'universal-tour-button';
        tourButton.innerHTML = `
            <i data-feather="help-circle"></i>
            <span class="tour-btn-text">${this.getText('help')}</span>
        `;
        tourButton.title = this.getText('startTourTooltip');
        tourButton.setAttribute('aria-label', this.getText('startTourTooltip'));
        
        tourButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.startTour();
        });

        // Add keyboard support
        tourButton.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.startTour();
            }
        });

        document.body.appendChild(tourButton);
        
        // Initialize feather icons for the new button
        if (window.feather) {
            window.feather.replace();
        }
    }

    setupIntroJS() {
        if (typeof introJs === 'undefined') {
            console.warn('Intro.js not loaded, tour functionality disabled');
            return;
        }

        // Configure intro.js with consistent settings and current language
        this.introInstance = introJs().setOptions({
            nextLabel: this.getText('next'),
            prevLabel: this.getText('prev'),
            doneLabel: this.getText('done'),
            skipLabel: this.getText('skip'),
            showProgress: true,
            showBullets: false,
            exitOnOverlayClick: false,
            exitOnEsc: true,
            scrollToElement: true,
            scrollTo: 'tooltip',
            disableInteraction: true,
            tooltipClass: 'universal-intro-tooltip',
            highlightClass: 'universal-intro-highlight',
            steps: this.tourSteps
        });

        // Add event listeners
        this.introInstance.oncomplete(() => {
            this.onTourComplete();
        });

        this.introInstance.onexit(() => {
            this.onTourExit();
        });

        // Add error handling
        this.introInstance.onerror((error) => {
            console.warn('Tour error:', error);
            this.showNoContentMessage();
        });
    }

    generateTourSteps() {
        const commonSteps = this.getCommonSteps();
        const pageSpecificSteps = this.getPageSpecificSteps();
        
        this.tourSteps = [...commonSteps, ...pageSpecificSteps];
        
        // Update intro.js steps if instance exists
        if (this.introInstance) {
            this.introInstance.setOptions({ steps: this.tourSteps });
        }
        
        return this.tourSteps;
    }

    getCommonSteps() {
        const steps = [];

        // Navigation bar
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            steps.push({
                element: navbar,
                title: this.language === 'nl' ? '🧭 Navigatie' : '🧭 Navigation',
                intro: this.language === 'nl' 
                    ? 'Dit is de hoofdnavigatie. Hier vind je alle belangrijke onderdelen van de applicatie. Klik op een menu-item om naar die sectie te gaan.'
                    : 'This is the main navigation. Here you can find all important sections of the application. Click on a menu item to go to that section.',
                position: 'bottom'
            });
        }

        // Theme toggle
        const themeToggle = document.querySelector('#themeToggle');
        if (themeToggle) {
            steps.push({
                element: themeToggle,
                title: this.language === 'nl' ? '🌙 Thema' : '🌙 Theme',
                intro: this.language === 'nl' 
                    ? 'Wissel tussen licht en donker thema voor een comfortabele ervaring.'
                    : 'Switch between light and dark theme for a comfortable experience.',
                position: 'bottom-left'
            });
        }

        // Language toggle
        const languageToggle = document.querySelector('#languageToggle');
        if (languageToggle) {
            steps.push({
                element: languageToggle,
                title: this.language === 'nl' ? '🌍 Taal' : '🌍 Language',
                intro: this.language === 'nl' 
                    ? 'Schakel tussen Nederlands en Engels.'
                    : 'Switch between Dutch and English.',
                position: 'bottom-left'
            });
        }

        return steps;
    }

    getPageSpecificSteps() {
        switch (this.currentPage) {
            case 'dashboard':
                return this.getDashboardSteps();
            case 'time_entries':
                return this.getTimeEntriesSteps();
            case 'klanten':
                return this.getKlantenSteps();
            case 'medewerkers':
                return this.getMedewerkersSteps();
            case 'opdrachten':
                return this.getOpdrachtenSteps();
            case 'facturen':
                return this.getFacturenSteps();
            case 'reports':
                return this.getReportsSteps();
            case 'admin':
                return this.getAdminSteps();
            default:
                return this.getGeneralSteps();
        }
    }

    getDashboardSteps() {
        const steps = [];

        // Welcome message - look for main content area
        const mainContent = document.querySelector('.container .row .col-12') || document.querySelector('main');
        if (mainContent) {
            steps.push({
                element: mainContent,
                title: this.language === 'nl' ? '👋 Welkom op het Dashboard' : '👋 Welcome to the Dashboard',
                intro: this.language === 'nl' 
                    ? 'Dit is je persoonlijke dashboard. Hier krijg je een overzicht van je dag en kun je snel belangrijke acties uitvoeren.'
                    : 'This is your personal dashboard. Here you get an overview of your day and can quickly perform important actions.',
                position: 'bottom'
            });
        }

        // Check-in form - more flexible selector
        const checkinForm = document.querySelector('form[action*="check_in"]') || 
                           document.querySelector('form[method="POST"]') ||
                           document.querySelector('.card:has(h5:contains("Check-in"))') ||
                           document.querySelector('[data-intro*="check-in"]');
        if (checkinForm) {
            steps.push({
                element: checkinForm,
                title: this.language === 'nl' ? '⏰ Check-in Systeem' : '⏰ Check-in System',
                intro: this.language === 'nl' 
                    ? 'Hier registreer je je dagelijkse status: aan het werk, pauze, of klaar voor vandaag. Je kunt ook een notitie toevoegen en aangeven aan welk project je werkt.'
                    : 'Here you register your daily status: working, break, or done for today. You can also add a note and indicate which project you are working on.',
                position: 'top'
            });
        }

        // Recent check-ins - more flexible selector
        const recentCheckins = document.querySelector('.list-group') || 
                              document.querySelector('[data-translate*="Check-ins"]')?.closest('.card') ||
                              document.querySelector('h6:contains("Check-ins")')?.closest('.card');
        if (recentCheckins) {
            steps.push({
                element: recentCheckins,
                title: this.language === 'nl' ? '📋 Recente Check-ins' : '📋 Recent Check-ins',
                intro: this.language === 'nl' 
                    ? 'Hier zie je je laatste check-ins. Je kunt ze bewerken of verwijderen door op de knoppen te klikken.'
                    : 'Here you see your latest check-ins. You can edit or delete them by clicking the buttons.',
                position: 'left'
            });
        }

        // Time entries table - more flexible selector
        const timeEntriesTable = document.querySelector('.table-responsive') || 
                                document.querySelector('table') ||
                                document.querySelector('[data-translate*="Urenregistraties"]')?.closest('.card');
        if (timeEntriesTable) {
            steps.push({
                element: timeEntriesTable,
                title: this.language === 'nl' ? '📊 Urenregistraties' : '📊 Time Entries',
                intro: this.language === 'nl' 
                    ? 'Dit overzicht toont je recente urenregistraties. Je kunt ze bewerken, verwijderen of nieuwe toevoegen.'
                    : 'This overview shows your recent time entries. You can edit, delete or add new ones.',
                position: 'top'
            });
        }

        // Add new entry button - more flexible selector
        const addButton = document.querySelector('a[href*="time_entries"].btn-primary') ||
                         document.querySelector('.btn-primary:contains("Nieuwe")') ||
                         document.querySelector('[data-translate*="Nieuwe Registratie"]') ||
                         document.querySelector('a[href*="time_entries"]:has(i[data-feather="plus"])');
        if (addButton) {
            steps.push({
                element: addButton,
                title: this.language === 'nl' ? '➕ Nieuwe Registratie' : '➕ New Entry',
                intro: this.language === 'nl' 
                    ? 'Klik hier om een nieuwe urenregistratie toe te voegen. Dit brengt je naar de uren-pagina.'
                    : 'Click here to add a new time entry. This will take you to the time entries page.',
                position: 'left'
            });
        }

        return steps;
    }

    getTimeEntriesSteps() {
        const steps = [];

        // Page header - more flexible selector
        const pageHeader = document.querySelector('h1, h2, .card-header h5') || 
                          document.querySelector('.container h1, .container h2') ||
                          document.querySelector('[data-translate*="Uren"]');
        if (pageHeader) {
            steps.push({
                element: pageHeader,
                title: this.language === 'nl' ? '⏱️ Urenregistratie' : '⏱️ Time Registration',
                intro: this.language === 'nl' 
                    ? 'Hier beheer je al je geregistreerde uren. Je kunt uren toevoegen, bewerken, verwijderen en exporteren.'
                    : 'Here you manage all your registered hours. You can add, edit, delete and export hours.',
                position: 'bottom'
            });
        }

        // Filter section - more flexible selector
        const filterSection = document.querySelector('.row .col-md-6, .filter-section') ||
                             document.querySelector('select[name*="client"], select[name*="klant"]')?.closest('.row') ||
                             document.querySelector('input[type="search"]')?.closest('.row');
        if (filterSection) {
            steps.push({
                element: filterSection,
                title: this.language === 'nl' ? '🔍 Filteren & Zoeken' : '🔍 Filter & Search',
                intro: this.language === 'nl' 
                    ? 'Gebruik deze filters om specifieke uren te vinden. Je kunt filteren op klant, opdracht, datum of zoeken in beschrijvingen.'
                    : 'Use these filters to find specific hours. You can filter by client, assignment, date or search in descriptions.',
                position: 'bottom'
            });
        }

        // Action buttons - more flexible selector
        const actionButtons = document.querySelector('.btn-group') ||
                             document.querySelector('.d-flex .btn') ||
                             document.querySelector('.btn-success, .btn-primary') ||
                             document.querySelector('[data-translate*="Export"], [data-translate*="Nieuwe"]')?.closest('.d-flex');
        if (actionButtons) {
            steps.push({
                element: actionButtons,
                title: this.language === 'nl' ? '🛠️ Acties' : '🛠️ Actions',
                intro: this.language === 'nl' 
                    ? 'Hier vind je alle acties: exporteren naar Excel/PDF, importeren van uren, en nieuwe registraties toevoegen.'
                    : 'Here you find all actions: export to Excel/PDF, import hours, and add new registrations.',
                position: 'bottom'
            });
        }

        // Time entries table - more flexible selector
        const table = document.querySelector('table') ||
                     document.querySelector('.table-responsive') ||
                     document.querySelector('.card .table');
        if (table) {
            steps.push({
                element: table,
                title: this.language === 'nl' ? '📋 Urenoverzicht' : '📋 Hours Overview',
                intro: this.language === 'nl' 
                    ? 'Dit is je complete urenoverzicht. Klik op de bewerk-knop om uren aan te passen, of op de verwijder-knop om ze te verwijderen.'
                    : 'This is your complete hours overview. Click the edit button to modify hours, or the delete button to remove them.',
                position: 'top'
            });
        }

        return steps;
    }

    getKlantenSteps() {
        const steps = [];

        // Page header
        const pageHeader = document.querySelector('.card-header, h1, h2') || 
                          document.querySelector('.container h1, .container h2') ||
                          document.body;
        steps.push({
            element: pageHeader,
            title: this.language === 'nl' ? '👥 Klantenbeheer' : '👥 Client Management',
            intro: this.language === 'nl' 
                ? 'Hier beheer je al je klanten. Je kunt klantgegevens toevoegen, bewerken, verwijderen en exporteren.'
                : 'Here you manage all your clients. You can add, edit, delete and export client data.',
            position: 'bottom'
        });

        // Search functionality
        const searchBox = document.querySelector('input[type="search"]') ||
                         document.querySelector('input[placeholder*="zoek"]') ||
                         document.querySelector('input[placeholder*="search"]') ||
                         document.querySelector('.form-control[type="text"]');
        if (searchBox) {
            steps.push({
                element: searchBox,
                title: this.language === 'nl' ? '🔍 Klanten Zoeken' : '🔍 Search Clients',
                intro: this.language === 'nl' 
                    ? 'Zoek snel klanten op bedrijfsnaam, email of achternaam.'
                    : 'Quickly search clients by company name, email or last name.',
                position: 'bottom'
            });
        }

        // Add button
        const addButton = document.querySelector('.btn-success') ||
                         document.querySelector('.btn-primary[href*="add"]') ||
                         document.querySelector('.btn[href*="new"]') ||
                         document.querySelector('a:contains("Nieuwe")') ||
                         document.querySelector('a:contains("Add")');
        if (addButton) {
            steps.push({
                element: addButton,
                title: this.language === 'nl' ? '➕ Nieuwe Klant' : '➕ New Client',
                intro: this.language === 'nl' 
                    ? 'Klik hier om een nieuwe klant toe te voegen.'
                    : 'Click here to add a new client.',
                position: 'left'
            });
        }

        // Table
        const table = document.querySelector('table') ||
                     document.querySelector('.table-responsive') ||
                     document.querySelector('.card .table');
        if (table) {
            steps.push({
                element: table,
                title: this.language === 'nl' ? '📊 Klantenlijst' : '📊 Client List',
                intro: this.language === 'nl' 
                    ? 'Overzicht van al je klanten met hun contactgegevens. Gebruik de actieknoppen om klanten te bewerken of verwijderen.'
                    : 'Overview of all your clients with their contact details. Use the action buttons to edit or delete clients.',
                position: 'top'
            });
        }

        return steps;
    }

    getMedewerkersSteps() {
        const steps = [];

        // Page header
        const pageHeader = document.querySelector('.card-header, h1, h2') || 
                          document.querySelector('.container h1, .container h2') ||
                          document.body;
        steps.push({
            element: pageHeader,
            title: this.language === 'nl' ? '👨‍💼 Medewerkerbeheer' : '👨‍💼 Employee Management',
            intro: this.language === 'nl' 
                ? 'Hier beheer je alle medewerkers. Je kunt medewerkergegevens toevoegen, bewerken en hun informatie bijhouden.'
                : 'Here you manage all employees. You can add, edit employee data and track their information.',
            position: 'bottom'
        });

        // Search functionality
        const searchBox = document.querySelector('input[type="search"]') ||
                         document.querySelector('input[placeholder*="zoek"]') ||
                         document.querySelector('input[placeholder*="search"]');
        if (searchBox) {
            steps.push({
                element: searchBox,
                title: this.language === 'nl' ? '🔍 Medewerkers Zoeken' : '🔍 Search Employees',
                intro: this.language === 'nl' 
                    ? 'Zoek medewerkers op naam of email.'
                    : 'Search employees by name or email.',
                position: 'bottom'
            });
        }

        return steps;
    }

    getOpdrachtenSteps() {
        const steps = [];

        const pageHeader = document.querySelector('.card-header, h1, h2') || 
                          document.querySelector('.container h1, .container h2') ||
                          document.body;
        steps.push({
            element: pageHeader,
            title: this.language === 'nl' ? '💼 Opdrachtenbeheer' : '💼 Assignment Management',
            intro: this.language === 'nl' 
                ? 'Hier beheer je alle opdrachten en projecten. Je kunt opdrachten koppelen aan klanten en de status bijhouden.'
                : 'Here you manage all assignments and projects. You can link assignments to clients and track their status.',
            position: 'bottom'
        });

        return steps;
    }

    getFacturenSteps() {
        const steps = [];

        const pageHeader = document.querySelector('.card-header, h1, h2') || 
                          document.querySelector('.container h1, .container h2') ||
                          document.body;
        steps.push({
            element: pageHeader,
            title: this.language === 'nl' ? '🧾 Facturenbeheer' : '🧾 Invoice Management',
            intro: this.language === 'nl' 
                ? 'Hier beheer je alle facturen. Je kunt facturen aanmaken, bewerken en versturen naar klanten.'
                : 'Here you manage all invoices. You can create, edit and send invoices to clients.',
            position: 'bottom'
        });

        return steps;
    }

    getReportsSteps() {
        const steps = [];

        const pageHeader = document.querySelector('.card-header, h1, h2') || 
                          document.querySelector('.container h1, .container h2') ||
                          document.body;
        steps.push({
            element: pageHeader,
            title: this.language === 'nl' ? '📈 Rapportages' : '📈 Reports',
            intro: this.language === 'nl' 
                ? 'Hier vind je alle rapportages en analyses. Genereer overzichten van uren, omzet en productiviteit.'
                : 'Here you find all reports and analytics. Generate overviews of hours, revenue and productivity.',
            position: 'bottom'
        });

        return steps;
    }

    getAdminSteps() {
        const steps = [];

        const pageHeader = document.querySelector('.card-header, h1, h2') || 
                          document.querySelector('.container h1, .container h2') ||
                          document.body;
        steps.push({
            element: pageHeader,
            title: this.language === 'nl' ? '⚙️ Beheer' : '⚙️ Administration',
            intro: this.language === 'nl' 
                ? 'Dit is het beheerdersgedeelte. Hier kun je gebruikers beheren en systeeminstellingen aanpassen.'
                : 'This is the administration section. Here you can manage users and adjust system settings.',
            position: 'bottom'
        });

        return steps;
    }

    getGeneralSteps() {
        return [{
            element: document.body,
            title: this.language === 'nl' ? '📖 Pagina Uitleg' : '📖 Page Guide',
            intro: this.language === 'nl' 
                ? 'Deze pagina bevat specifieke functionaliteit. Gebruik de navigatie om tussen verschillende onderdelen te schakelen.'
                : 'This page contains specific functionality. Use the navigation to switch between different sections.',
            position: 'center'
        }];
    }

    showWelcomeModal() {
        // Prevent multiple modals
        if (document.querySelector('.welcome-modal-overlay')) {
            return;
        }

        const modal = document.createElement('div');
        modal.className = 'welcome-modal-overlay';
        modal.innerHTML = `
            <div class="welcome-modal">
                <div class="welcome-modal-header">
                    <h2>${this.getText('welcomeTitle')}</h2>
                    <button class="welcome-modal-close" aria-label="${this.language === 'nl' ? 'Sluiten' : 'Close'}">&times;</button>
                </div>
                <div class="welcome-modal-body">
                    <p>${this.getText('welcomeMessage')}</p>
                    <div class="welcome-features">
                        <div class="feature">
                            <span class="feature-icon">⏰</span>
                            <span>${this.language === 'nl' ? 'Uren registreren en bijhouden' : 'Register and track hours'}</span>
                        </div>
                        <div class="feature">
                            <span class="feature-icon">👥</span>
                            <span>${this.language === 'nl' ? 'Klanten en projecten beheren' : 'Manage clients and projects'}</span>
                        </div>
                        <div class="feature">
                            <span class="feature-icon">📊</span>
                            <span>${this.language === 'nl' ? 'Rapportages en analyses' : 'Reports and analytics'}</span>
                        </div>
                        <div class="feature">
                            <span class="feature-icon">🧾</span>
                            <span>${this.language === 'nl' ? 'Facturen genereren' : 'Generate invoices'}</span>
                        </div>
                    </div>
                </div>
                <div class="welcome-modal-footer">
                    <button class="btn btn-secondary welcome-skip">${this.getText('welcomeSkip')}</button>
                    <button class="btn btn-primary welcome-start-tour">${this.getText('welcomeStart')}</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Add keyboard navigation
        const focusableElements = modal.querySelectorAll('button');
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        // Focus first element
        setTimeout(() => firstElement.focus(), 100);

        // Trap focus within modal
        modal.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                if (e.shiftKey) {
                    if (document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    }
                } else {
                    if (document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            } else if (e.key === 'Escape') {
                this.closeWelcomeModal(modal);
            }
        });

        // Event listeners
        modal.querySelector('.welcome-modal-close').addEventListener('click', () => {
            this.closeWelcomeModal(modal);
        });

        modal.querySelector('.welcome-skip').addEventListener('click', () => {
            this.closeWelcomeModal(modal);
            this.markTourCompleted();
        });

        modal.querySelector('.welcome-start-tour').addEventListener('click', () => {
            this.closeWelcomeModal(modal);
            setTimeout(() => this.startTour(), 300);
        });

        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeWelcomeModal(modal);
            }
        });
    }

    closeWelcomeModal(modal) {
        modal.classList.add('welcome-modal-closing');
        setTimeout(() => {
            modal.remove();
        }, 300);
    }

    startTour() {
        if (this.introInstance && this.tourSteps.length > 0) {
            this.introInstance.start();
        } else {
            this.showNoContentMessage();
        }
    }

    showNoContentMessage() {
        // Prevent multiple messages
        if (document.querySelector('.tour-message')) {
            return;
        }

        const message = document.createElement('div');
        message.className = 'tour-message';
        message.innerHTML = `
            <div class="tour-message-content">
                <h4>${this.getText('noTourTitle')}</h4>
                <p>${this.getText('noTourMessage')}</p>
                <p>${this.getText('noTourSuggestion')}</p>
                <button class="btn btn-primary tour-message-close">${this.getText('noTourButton')}</button>
            </div>
        `;

        document.body.appendChild(message);

        // Focus the button for accessibility
        const closeButton = message.querySelector('.tour-message-close');
        setTimeout(() => closeButton.focus(), 100);

        // Add keyboard support
        message.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                message.remove();
            }
        });

        closeButton.addEventListener('click', () => {
            message.remove();
        });

        // Auto-remove after 8 seconds
        setTimeout(() => {
            if (message.parentNode) {
                message.remove();
            }
        }, 8000);
    }

    onTourComplete() {
        this.markTourCompleted();
        this.showCompletionMessage();
    }

    onTourExit() {
        // Tour was skipped or exited early
        console.log('Tour exited by user');
    }

    showCompletionMessage() {
        // Prevent multiple messages
        if (document.querySelector('.tour-completion-message')) {
            return;
        }

        const message = document.createElement('div');
        message.className = 'tour-completion-message';
        message.innerHTML = `
            <div class="tour-completion-content">
                <h4>${this.getText('tourCompleteTitle')}</h4>
                <p>${this.getText('tourCompleteMessage')}</p>
                <button class="btn btn-primary tour-completion-close">${this.getText('tourCompleteButton')}</button>
            </div>
        `;

        document.body.appendChild(message);

        // Focus the button for accessibility
        const closeButton = message.querySelector('.tour-completion-close');
        setTimeout(() => closeButton.focus(), 100);

        // Add keyboard support
        message.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                message.remove();
            }
        });

        closeButton.addEventListener('click', () => {
            message.remove();
        });

        // Auto-remove after 6 seconds
        setTimeout(() => {
            if (message.parentNode) {
                message.remove();
            }
        }, 6000);
    }

    // Public method to reset tour status (for testing or admin purposes)
    resetTourStatus() {
        localStorage.removeItem('intro_guide_completed');
        localStorage.removeItem('intro_guide_completed_date');
        console.log('Tour status reset');
    }
}

// Initialize the universal intro guide when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Wait for other scripts and page elements to load
    setTimeout(() => {
        try {
            window.universalIntroGuide = new UniversalIntroGuide();
            console.log('Universal Intro Guide initialized successfully');
        } catch (error) {
            console.warn('Failed to initialize Universal Intro Guide:', error);
        }
    }, 800);
});

// Expose utility functions globally
window.resetIntroGuide = function() {
    if (window.universalIntroGuide) {
        window.universalIntroGuide.resetTourStatus();
        location.reload();
    } else {
        console.warn('Universal Intro Guide not initialized');
    }
};

// Allow manual tour start from anywhere
window.startIntroTour = function() {
    if (window.universalIntroGuide) {
        window.universalIntroGuide.startTour();
    } else {
        console.warn('Universal Intro Guide not initialized');
    }
};

// Check if tour is available for current page
window.isTourAvailable = function() {
    if (window.universalIntroGuide) {
        return window.universalIntroGuide.tourSteps.length > 0;
    }
    return false;
};

// Get current page type
window.getCurrentPageType = function() {
    if (window.universalIntroGuide) {
        return window.universalIntroGuide.currentPage;
    }
    return 'unknown';
};