/**
 * Universal Intro Guide System - Redesigned for Better UX
 * Smooth, automatic, visually appealing guided tours
 */

class UniversalIntroGuide {
    constructor() {
        this.currentPage = this.detectCurrentPage();
        this.isFirstVisit = this.checkFirstVisit();
        this.language = this.detectLanguage();
        this.tourSteps = [];
        this.currentStep = 0;
        this.isActive = false;
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeGuide());
        } else {
            this.initializeGuide();
        }
    }

    initializeGuide() {
        // Re-detect current page after DOM is fully loaded
        this.currentPage = this.detectCurrentPage();
        console.log('Initializing guide for page:', this.currentPage); // Debug log
        
        this.createTourButton();
        this.generateTourSteps();
        if (this.isFirstVisit && this.currentPage === 'dashboard') {
            setTimeout(() => {
                this.showWelcomeModal();
            }, 1000);
        }
        this.setupLanguageListener();
    }

    detectCurrentPage() {
        const path = window.location.pathname.toLowerCase();
        const search = window.location.search.toLowerCase();
        
        console.log('Detecting page for path:', path, 'search:', search); // Debug log
        
        if (path.includes('dashboard') || path === '/' || path === '/dashboard') return 'dashboard';
        if (path.includes('time_entries') || path.includes('uren')) return 'time_entries';
        if (path.includes('klanten')) return 'klanten';
        if (path.includes('medewerkers')) return 'medewerkers';
        if (path.includes('opdrachten')) return 'opdrachten';
        if (path.includes('facturen')) return 'facturen';
        if (path.includes('reports')) return 'reports';
        if (path.includes('admin')) return 'admin';
        if (path.includes('add_klant') || path.includes('edit_klant')) return 'klanten_form';
        if (path.includes('add_medewerker') || path.includes('edit_medewerker')) return 'medewerkers_form';
        if (path.includes('add_opdracht') || path.includes('edit_opdracht')) return 'opdrachten_form';
        
        // Check if we're on a page with specific content that indicates time entries
        if (document.querySelector('button[data-bs-target="#addEntryModal"]')) return 'time_entries';
        
        return 'general';
    }

    detectLanguage() {
        const savedLang = localStorage.getItem('language');
        if (savedLang) return savedLang;
        const langCheckbox = document.getElementById('languageCheckbox');
        if (langCheckbox) return langCheckbox.checked ? 'en' : 'nl';
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
        this.generateTourSteps();
        const tourButton = document.getElementById('universal-tour-btn');
        if (tourButton) {
            const buttonText = tourButton.querySelector('.tour-btn-text');
            if (buttonText) buttonText.textContent = this.getText('help');
            tourButton.title = this.getText('startTourTooltip');
        }
    }

    getText(key) {
        const texts = {
            nl: {
                help: 'Hulp',
                startTourTooltip: 'Start rondleiding - Leer hoe je deze app gebruikt',
                next: 'Volgende',
                prev: 'Vorige',
                done: 'Afronden',
                skip: 'Overslaan',
                welcomeTitle: 'Welkom bij UrenRegistratie!',
                welcomeMessage: 'Deze app helpt je bij het bijhouden van je werkuren, klanten en projecten. Wil je een korte rondleiding?',
                welcomeFeature1: 'Registreer je werkuren eenvoudig',
                welcomeFeature2: 'Beheer klanten en projecten',
                welcomeFeature3: 'Genereer rapporten en facturen',
                welcomeFeature4: 'Check-in systeem voor dagelijkse status',
                welcomeSkip: 'Overslaan',
                welcomeStart: 'Start Rondleiding',
                tourCompleteTitle: 'Rondleiding Voltooid!',
                tourCompleteMessage: 'Je bent nu klaar om de app te gebruiken. Je kunt altijd opnieuw een rondleiding starten via de hulp-knop.',
                tourCompleteButton: 'Aan de slag!',
                // Dashboard
                dashboardTitle: 'Dashboard Overzicht',
                dashboardIntro: 'Dit is je persoonlijke dashboard waar je een overzicht krijgt van je dag.',
                checkinTitle: 'Check-in Systeem',
                checkinIntro: 'Hier kun je je dagelijkse status registreren: aan het werk, pauze of klaar voor vandaag.',
                recentCheckinTitle: 'Recente Check-ins',
                recentCheckinIntro: 'Bekijk en beheer je laatste check-ins. Je kunt ze bewerken of verwijderen.',
                timeEntriesTitle: 'Urenregistraties',
                timeEntriesIntro: 'Hier zie je je recente urenregistraties. Je kunt ze bewerken, verwijderen of nieuwe toevoegen.',
                addEntryTitle: 'Nieuwe Registratie',
                addEntryIntro: 'Klik hier om een nieuwe urenregistratie toe te voegen.',
                // Time Entries
                timeEntriesPageTitle: 'Urenregistratie Pagina',
                timeEntriesPageIntro: 'Op deze pagina beheer je al je urenregistraties. Je kunt zoeken, filteren en exporteren.',
                timeEntriesHeaderTitle: 'Pagina Header',
                timeEntriesHeaderIntro: 'Hier vind je de titel van de pagina en knoppen voor exporteren en nieuwe registraties.',
                timeEntriesFilterTitle: 'Filter Opties',
                timeEntriesFilterIntro: 'Gebruik deze filters om specifieke registraties te vinden op basis van zoekterm, klant of opdracht.',
                timeEntriesTableTitle: 'Registraties Tabel',
                timeEntriesTableIntro: 'Hier zie je al je urenregistraties in een overzichtelijke tabel met datum, klant, project en uren.',
                timeEntriesActionsTitle: 'Acties per Registratie',
                timeEntriesActionsIntro: 'Voor elke registratie kun je deze bewerken, verwijderen of exporteren.',
                timeEntriesSearchTitle: 'Zoeken in Registraties',
                timeEntriesSearchIntro: 'Typ hier om te zoeken in je urenregistraties op project, omschrijving of andere details.',
                timeEntriesClientFilterTitle: 'Filter op Klant',
                timeEntriesClientFilterIntro: 'Selecteer een specifieke klant om alleen registraties voor die klant te zien.',
                timeEntriesAssignmentFilterTitle: 'Filter op Opdracht',
                timeEntriesAssignmentFilterIntro: 'Kies een opdracht om alleen registraties voor dat project te bekijken.',
                timeEntriesExportTitle: 'Export Opties',
                timeEntriesExportIntro: 'Exporteer je urenregistraties naar PDF, Excel of CSV formaat.',
                timeEntriesImportTitle: 'Import Functie',
                timeEntriesImportIntro: 'Importeer urenregistraties vanuit een CSV of Excel bestand.',
                // Clients
                clientsPageTitle: 'Klanten Beheer',
                clientsPageIntro: 'Hier beheer je al je klanten. Je kunt nieuwe klanten toevoegen, bestaande bewerken en zoeken.',
                clientsHeaderTitle: 'Klanten Header',
                clientsHeaderIntro: 'Exporteer je klantenlijst of voeg een nieuwe klant toe via deze knoppen.',
                clientsSearchTitle: 'Klanten Zoeken',
                clientsSearchIntro: 'Zoek snel een specifieke klant op bedrijfsnaam, email of achternaam.',
                clientsTableTitle: 'Klanten Overzicht',
                clientsTableIntro: 'Bekijk alle klantgegevens in deze tabel: bedrijfsnaam, contactpersoon, functie en contactgegevens.',
                clientsActionsTitle: 'Klant Acties',
                clientsActionsIntro: 'Bewerk of verwijder klantgegevens met deze actieknoppen.',
                // Employees
                employeesPageTitle: 'Medewerkers Beheer',
                employeesPageIntro: 'Beheer alle medewerkers van je organisatie. Voeg nieuwe toe, bewerk gegevens of zoek specifieke medewerkers.',
                employeesHeaderTitle: 'Medewerkers Header',
                employeesHeaderIntro: 'Exporteer de medewerkerslijst of voeg een nieuwe medewerker toe.',
                employeesSearchTitle: 'Medewerkers Zoeken',
                employeesSearchIntro: 'Zoek medewerkers op naam of email adres.',
                employeesTableTitle: 'Medewerkers Overzicht',
                employeesTableIntro: 'Overzicht van alle medewerkers met hun functie, contactgegevens en andere details.',
                employeesActionsTitle: 'Medewerker Acties',
                employeesActionsIntro: 'Bewerk medewerkergegevens of verwijder medewerkers uit het systeem.',
                // Assignments
                assignmentsPageTitle: 'Opdrachten Beheer',
                assignmentsPageIntro: 'Beheer alle opdrachten en projecten. Koppel opdrachten aan klanten en houd de voortgang bij.',
                assignmentsHeaderTitle: 'Opdrachten Header',
                assignmentsHeaderIntro: 'Exporteer opdrachten of maak een nieuwe opdracht aan.',
                assignmentsSearchTitle: 'Opdrachten Zoeken',
                assignmentsSearchIntro: 'Zoek opdrachten op titel of omschrijving.',
                assignmentsTableTitle: 'Opdrachten Overzicht',
                assignmentsTableIntro: 'Bekijk alle opdrachten met datum, klant, titel en benodigde kennis.',
                assignmentsActionsTitle: 'Opdracht Acties',
                assignmentsActionsIntro: 'Bewerk opdracht details of verwijder opdrachten.',
                // Invoices
                invoicesPageTitle: 'Facturen Beheer',
                invoicesPageIntro: 'Beheer al je facturen: bekijk status, genereer nieuwe facturen en exporteer overzichten.',
                invoicesSearchTitle: 'Facturen Zoeken',
                invoicesSearchIntro: 'Zoek facturen op nummer of klantnaam.',
                invoicesTableTitle: 'Facturen Overzicht',
                invoicesTableIntro: 'Overzicht van alle facturen met nummer, datum, klant, bedrag en betaalstatus.',
                invoicesActionsTitle: 'Factuur Acties',
                invoicesActionsIntro: 'Bekijk factuur details, bewerk facturen of genereer PDF bestanden.',
                invoicesCreateTitle: 'Nieuwe Factuur',
                invoicesCreateIntro: 'Maak een nieuwe factuur aan voor een klant.',
                // Reports
                reportsPageTitle: 'Rapportages Dashboard',
                reportsPageIntro: 'Genereer verschillende rapporten om inzicht te krijgen in je bedrijfsvoering.',
                reportsCardsTitle: 'Rapport Opties',
                reportsCardsIntro: 'Kies uit verschillende rapporten zoals jaaropbrengst, uren per jaar of opdrachten per klant.',
                // Admin
                adminPageTitle: 'Beheerders Dashboard',
                adminPageIntro: 'Administratieve functies voor systeembeheer en gebruikersbeheer.',
                adminUsersTitle: 'Gebruikersbeheer',
                adminUsersIntro: 'Beheer gebruikersaccounts en hun rollen in het systeem.',
                adminUsersTableTitle: 'Gebruikers Overzicht',
                adminUsersTableIntro: 'Bekijk alle gebruikers met hun rollen, status en aanmaakdatum.',
                adminUsersActionsTitle: 'Gebruiker Acties',
                adminUsersActionsIntro: 'Wijzig gebruikersrollen en beheer toegangsrechten.',
                // Forms
                formTitle: 'Formulier',
                formIntro: 'Vul alle vereiste velden in om de gegevens op te slaan.',
                formFieldsTitle: 'Formulier Velden',
                formFieldsIntro: 'Vul de velden in met de juiste informatie. Velden met een * zijn verplicht.',
                formButtonsTitle: 'Formulier Acties',
                formButtonsIntro: 'Sla je wijzigingen op of ga terug naar het overzicht.',
                // No content messages
                noTourTitle: 'Geen rondleiding beschikbaar',
                noTourMessage: 'Voor deze pagina is momenteel geen rondleiding beschikbaar.',
                noTourButton: 'Begrepen'
            },
            en: {
                help: 'Help',
                startTourTooltip: 'Start tour - Learn how to use this app',
                next: 'Next',
                prev: 'Previous',
                done: 'Finish',
                skip: 'Skip',
                welcomeTitle: 'Welcome to UrenRegistratie!',
                welcomeMessage: 'This app helps you track your work hours, clients, and projects. Would you like a quick tour?',
                welcomeFeature1: 'Register your work hours easily',
                welcomeFeature2: 'Manage clients and projects',
                welcomeFeature3: 'Generate reports and invoices',
                welcomeFeature4: 'Check-in system for daily status',
                welcomeSkip: 'Skip',
                welcomeStart: 'Start Tour',
                tourCompleteTitle: 'Tour Completed!',
                tourCompleteMessage: 'You are now ready to use the app. You can always start a new tour using the help button.',
                tourCompleteButton: 'Get Started!',
                // Dashboard
                dashboardTitle: 'Dashboard Overview',
                dashboardIntro: 'This is your personal dashboard where you get an overview of your day.',
                checkinTitle: 'Check-in System',
                checkinIntro: 'Here you can register your daily status: working, break, or done for today.',
                recentCheckinTitle: 'Recent Check-ins',
                recentCheckinIntro: 'View and manage your latest check-ins. You can edit or delete them.',
                timeEntriesTitle: 'Time Entries',
                timeEntriesIntro: 'Here you see your recent time entries. You can edit, delete, or add new ones.',
                addEntryTitle: 'New Entry',
                addEntryIntro: 'Click here to add a new time entry.',
                // Time Entries
                timeEntriesPageTitle: 'Time Entries Page',
                timeEntriesPageIntro: 'On this page you manage all your time entries. You can search, filter and export.',
                timeEntriesHeaderTitle: 'Page Header',
                timeEntriesHeaderIntro: 'Here you find the page title and buttons for exporting and new entries.',
                timeEntriesFilterTitle: 'Filter Options',
                timeEntriesFilterIntro: 'Use these filters to find specific entries based on search term, client or assignment.',
                timeEntriesTableTitle: 'Entries Table',
                timeEntriesTableIntro: 'Here you see all your time entries in a clear table with date, client, project and hours.',
                timeEntriesActionsTitle: 'Entry Actions',
                timeEntriesActionsIntro: 'For each entry you can edit, delete or export it.',
                timeEntriesSearchTitle: 'Search Entries',
                timeEntriesSearchIntro: 'Type here to search through your time entries by project, description or other details.',
                timeEntriesClientFilterTitle: 'Filter by Client',
                timeEntriesClientFilterIntro: 'Select a specific client to see only entries for that client.',
                timeEntriesAssignmentFilterTitle: 'Filter by Assignment',
                timeEntriesAssignmentFilterIntro: 'Choose an assignment to view only entries for that project.',
                timeEntriesExportTitle: 'Export Options',
                timeEntriesExportIntro: 'Export your time entries to PDF, Excel or CSV format.',
                timeEntriesImportTitle: 'Import Function',
                timeEntriesImportIntro: 'Import time entries from a CSV or Excel file.',
                // Clients
                clientsPageTitle: 'Client Management',
                clientsPageIntro: 'Here you manage all your clients. You can add new clients, edit existing ones and search.',
                clientsHeaderTitle: 'Clients Header',
                clientsHeaderIntro: 'Export your client list or add a new client via these buttons.',
                clientsSearchTitle: 'Search Clients',
                clientsSearchIntro: 'Quickly find a specific client by company name, email or last name.',
                clientsTableTitle: 'Clients Overview',
                clientsTableIntro: 'View all client data in this table: company name, contact person, function and contact details.',
                clientsActionsTitle: 'Client Actions',
                clientsActionsIntro: 'Edit or delete client data with these action buttons.',
                // Employees
                employeesPageTitle: 'Employee Management',
                employeesPageIntro: 'Manage all employees of your organization. Add new ones, edit data or search specific employees.',
                employeesHeaderTitle: 'Employees Header',
                employeesHeaderIntro: 'Export the employee list or add a new employee.',
                employeesSearchTitle: 'Search Employees',
                employeesSearchIntro: 'Search employees by name or email address.',
                employeesTableTitle: 'Employees Overview',
                employeesTableIntro: 'Overview of all employees with their function, contact details and other information.',
                employeesActionsTitle: 'Employee Actions',
                employeesActionsIntro: 'Edit employee data or remove employees from the system.',
                // Assignments
                assignmentsPageTitle: 'Assignment Management',
                assignmentsPageIntro: 'Manage all assignments and projects. Link assignments to clients and track progress.',
                assignmentsHeaderTitle: 'Assignments Header',
                assignmentsHeaderIntro: 'Export assignments or create a new assignment.',
                assignmentsSearchTitle: 'Search Assignments',
                assignmentsSearchIntro: 'Search assignments by title or description.',
                assignmentsTableTitle: 'Assignments Overview',
                assignmentsTableIntro: 'View all assignments with date, client, title and required knowledge.',
                assignmentsActionsTitle: 'Assignment Actions',
                assignmentsActionsIntro: 'Edit assignment details or delete assignments.',
                // Invoices
                invoicesPageTitle: 'Invoice Management',
                invoicesPageIntro: 'Manage all your invoices: view status, generate new invoices and export overviews.',
                invoicesSearchTitle: 'Search Invoices',
                invoicesSearchIntro: 'Search invoices by number or client name.',
                invoicesTableTitle: 'Invoices Overview',
                invoicesTableIntro: 'Overview of all invoices with number, date, client, amount and payment status.',
                invoicesActionsTitle: 'Invoice Actions',
                invoicesActionsIntro: 'View invoice details, edit invoices or generate PDF files.',
                invoicesCreateTitle: 'New Invoice',
                invoicesCreateIntro: 'Create a new invoice for a client.',
                // Reports
                reportsPageTitle: 'Reports Dashboard',
                reportsPageIntro: 'Generate various reports to gain insight into your business operations.',
                reportsCardsTitle: 'Report Options',
                reportsCardsIntro: 'Choose from various reports like annual revenue, hours per year or assignments per client.',
                // Admin
                adminPageTitle: 'Admin Dashboard',
                adminPageIntro: 'Administrative functions for system management and user management.',
                adminUsersTitle: 'User Management',
                adminUsersIntro: 'Manage user accounts and their roles in the system.',
                adminUsersTableTitle: 'Users Overview',
                adminUsersTableIntro: 'View all users with their roles, status and creation date.',
                adminUsersActionsTitle: 'User Actions',
                adminUsersActionsIntro: 'Change user roles and manage access rights.',
                // Forms
                formTitle: 'Form',
                formIntro: 'Fill in all required fields to save the data.',
                formFieldsTitle: 'Form Fields',
                formFieldsIntro: 'Fill in the fields with the correct information. Fields with * are required.',
                formButtonsTitle: 'Form Actions',
                formButtonsIntro: 'Save your changes or go back to the overview.',
                // No content messages
                noTourTitle: 'No tour available',
                noTourMessage: 'No tour is currently available for this page.',
                noTourButton: 'Understood'
            }
        };
        return texts[this.language]?.[key] || texts.nl[key] || key;
    }

    checkFirstVisit() {
        return !localStorage.getItem('intro_guide_completed');
    }

    markTourCompleted() {
        localStorage.setItem('intro_guide_completed', 'true');
        localStorage.setItem('intro_guide_completed_date', new Date().toISOString());
    }

    createTourButton() {
        // Remove any existing tour buttons
        document.querySelectorAll('#tour-btn, #start-tour-btn, #universal-tour-btn').forEach(btn => btn.remove());
        
        const tourButton = document.createElement('button');
        tourButton.id = 'universal-tour-btn';
        tourButton.className = 'universal-tour-button';
        tourButton.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            <span class="tour-btn-text">${this.getText('help')}</span>
        `;
        tourButton.title = this.getText('startTourTooltip');
        tourButton.setAttribute('aria-label', this.getText('startTourTooltip'));
        
        tourButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.startTour();
        });
        
        document.body.appendChild(tourButton);
    }

    generateTourSteps() {
        let steps = [];
        
        console.log('Generating tour steps for page:', this.currentPage); // Debug log
        
        if (this.currentPage === 'dashboard') {
            // Main dashboard overview
            const mainCard = document.querySelector('.card') || document.querySelector('main');
            if (mainCard) {
                steps.push({
                    element: mainCard,
                    title: this.getText('dashboardTitle'),
                    content: this.getText('dashboardIntro'),
                    position: 'bottom'
                });
            }

            // Check-in form
            const checkinForm = document.querySelector('form[action*="check_in"]');
            if (checkinForm) {
                steps.push({
                    element: checkinForm,
                    title: this.getText('checkinTitle'),
                    content: this.getText('checkinIntro'),
                    position: 'right'
                });
            }

            // Recent check-ins
            const recentCheckins = document.querySelector('.list-group');
            if (recentCheckins) {
                steps.push({
                    element: recentCheckins,
                    title: this.getText('recentCheckinTitle'),
                    content: this.getText('recentCheckinIntro'),
                    position: 'left'
                });
            }

            // Time entries table
            const timeEntriesTable = document.querySelector('.table-responsive');
            if (timeEntriesTable) {
                steps.push({
                    element: timeEntriesTable,
                    title: this.getText('timeEntriesTitle'),
                    content: this.getText('timeEntriesIntro'),
                    position: 'top'
                });
            }

            // Add new entry button
            const addButton = document.querySelector('a.btn-primary[href*="time_entries"]');
            if (addButton) {
                steps.push({
                    element: addButton,
                    title: this.getText('addEntryTitle'),
                    content: this.getText('addEntryIntro'),
                    position: 'left'
                });
            }
        }
        
        else if (this.currentPage === 'time_entries') {
            console.log('Setting up time entries tour steps'); // Debug log
            
            // Main page overview - try multiple selectors
            const mainCard = document.querySelector('.card') || 
                            document.querySelector('.row .col-12 .card') || 
                            document.querySelector('main .card');
            if (mainCard) {
                console.log('Found main card:', mainCard); // Debug log
                steps.push({
                    element: mainCard,
                    title: this.getText('timeEntriesPageTitle'),
                    content: this.getText('timeEntriesPageIntro'),
                    position: 'bottom'
                });
            } else {
                console.log('Main card not found'); // Debug log
            }

            // Page header with buttons
            const pageHeader = document.querySelector('.card-header');
            if (pageHeader) {
                console.log('Found page header:', pageHeader); // Debug log
                steps.push({
                    element: pageHeader,
                    title: this.getText('timeEntriesHeaderTitle'),
                    content: this.getText('timeEntriesHeaderIntro'),
                    position: 'bottom'
                });
            }

            // Add entry button - try multiple selectors
            const addButton = document.querySelector('button[data-bs-target="#addEntryModal"]') ||
                             document.querySelector('.btn-primary[data-bs-toggle="modal"]') ||
                             document.querySelector('button:contains("Add Entry")');
            if (addButton) {
                console.log('Found add button:', addButton); // Debug log
                steps.push({
                    element: addButton,
                    title: this.getText('addEntryTitle'),
                    content: this.getText('addEntryIntro'),
                    position: 'left'
                });
            }

            // Export dropdown
            const exportDropdown = document.querySelector('.dropdown') ||
                                 document.querySelector('.card-header .dropdown');
            if (exportDropdown) {
                console.log('Found export dropdown:', exportDropdown); // Debug log
                steps.push({
                    element: exportDropdown,
                    title: this.getText('timeEntriesExportTitle'),
                    content: this.getText('timeEntriesExportIntro'),
                    position: 'bottom'
                });
            }

            // Import button
            const importButton = document.querySelector('.import-entries-btn') ||
                               document.querySelector('button:contains("Import")');
            if (importButton) {
                console.log('Found import button:', importButton); // Debug log
                steps.push({
                    element: importButton,
                    title: this.getText('timeEntriesImportTitle'),
                    content: this.getText('timeEntriesImportIntro'),
                    position: 'bottom'
                });
            }

            // Filter form
            const filterForm = document.querySelector('form[method="GET"]') ||
                              document.querySelector('.card-body form');
            if (filterForm) {
                console.log('Found filter form:', filterForm); // Debug log
                steps.push({
                    element: filterForm,
                    title: this.getText('timeEntriesFilterTitle'),
                    content: this.getText('timeEntriesFilterIntro'),
                    position: 'bottom'
                });
            }

            // Search input
            const searchInput = document.querySelector('input[name="search"]') ||
                              document.querySelector('input[placeholder*="Search"]') ||
                              document.querySelector('input[placeholder*="entries"]');
            if (searchInput) {
                console.log('Found search input:', searchInput); // Debug log
                const searchContainer = searchInput.closest('.input-group') || searchInput;
                steps.push({
                    element: searchContainer,
                    title: this.getText('timeEntriesSearchTitle'),
                    content: this.getText('timeEntriesSearchIntro'),
                    position: 'bottom'
                });
            }

            // Time entries table
            const entriesTable = document.querySelector('.table-responsive table') ||
                                document.querySelector('.table') ||
                                document.querySelector('table');
            if (entriesTable) {
                console.log('Found entries table:', entriesTable); // Debug log
                steps.push({
                    element: entriesTable,
                    title: this.getText('timeEntriesTableTitle'),
                    content: this.getText('timeEntriesTableIntro'),
                    position: 'top'
                });
            }

            // Action buttons in first row (if entries exist)
            const firstRow = document.querySelector('tbody tr');
            if (firstRow) {
                const editButton = firstRow.querySelector('.edit-entry-btn') ||
                                 firstRow.querySelector('button:contains("Edit")') ||
                                 firstRow.querySelector('.btn-group button');
                if (editButton) {
                    console.log('Found edit button:', editButton); // Debug log
                    steps.push({
                        element: editButton,
                        title: this.getText('timeEntriesActionsTitle'),
                        content: this.getText('timeEntriesActionsIntro'),
                        position: 'left'
                    });
                }
            }
            
            console.log('Time entries tour steps created:', steps.length); // Debug log
        }
        
        else if (this.currentPage === 'klanten') {
            // Page header
            const pageHeader = document.querySelector('.card-header');
            if (pageHeader) {
                steps.push({
                    element: pageHeader,
                    title: this.getText('clientsHeaderTitle'),
                    content: this.getText('clientsHeaderIntro'),
                    position: 'bottom'
                });
            }

            // Search form
            const searchForm = document.querySelector('form[method="GET"]');
            if (searchForm) {
                steps.push({
                    element: searchForm,
                    title: this.getText('clientsSearchTitle'),
                    content: this.getText('clientsSearchIntro'),
                    position: 'bottom'
                });
            }

            // Clients table
            const clientsTable = document.querySelector('.table-responsive');
            if (clientsTable) {
                steps.push({
                    element: clientsTable,
                    title: this.getText('clientsTableTitle'),
                    content: this.getText('clientsTableIntro'),
                    position: 'top'
                });
            }

            // Action buttons
            const firstActionButton = document.querySelector('.btn-primary[href*="edit_klant"]');
            if (firstActionButton) {
                steps.push({
                    element: firstActionButton.parentElement,
                    title: this.getText('clientsActionsTitle'),
                    content: this.getText('clientsActionsIntro'),
                    position: 'left'
                });
            }
        }
        
        else if (this.currentPage === 'medewerkers') {
            // Page header
            const pageHeader = document.querySelector('.card-header');
            if (pageHeader) {
                steps.push({
                    element: pageHeader,
                    title: this.getText('employeesHeaderTitle'),
                    content: this.getText('employeesHeaderIntro'),
                    position: 'bottom'
                });
            }

            // Search form
            const searchForm = document.querySelector('#searchForm');
            if (searchForm) {
                steps.push({
                    element: searchForm,
                    title: this.getText('employeesSearchTitle'),
                    content: this.getText('employeesSearchIntro'),
                    position: 'bottom'
                });
            }

            // Employees table
            const employeesTable = document.querySelector('.table-responsive');
            if (employeesTable) {
                steps.push({
                    element: employeesTable,
                    title: this.getText('employeesTableTitle'),
                    content: this.getText('employeesTableIntro'),
                    position: 'top'
                });
            }

            // Action buttons
            const firstActionButton = document.querySelector('.btn-group');
            if (firstActionButton) {
                steps.push({
                    element: firstActionButton,
                    title: this.getText('employeesActionsTitle'),
                    content: this.getText('employeesActionsIntro'),
                    position: 'left'
                });
            }
        }
        
        else if (this.currentPage === 'opdrachten') {
            // Page header
            const pageHeader = document.querySelector('.card-header');
            if (pageHeader) {
                steps.push({
                    element: pageHeader,
                    title: this.getText('assignmentsHeaderTitle'),
                    content: this.getText('assignmentsHeaderIntro'),
                    position: 'bottom'
                });
            }

            // Search form
            const searchForm = document.querySelector('form[method="GET"]');
            if (searchForm) {
                steps.push({
                    element: searchForm,
                    title: this.getText('assignmentsSearchTitle'),
                    content: this.getText('assignmentsSearchIntro'),
                    position: 'bottom'
                });
            }

            // Assignments table
            const assignmentsTable = document.querySelector('.table-responsive');
            if (assignmentsTable) {
                steps.push({
                    element: assignmentsTable,
                    title: this.getText('assignmentsTableTitle'),
                    content: this.getText('assignmentsTableIntro'),
                    position: 'top'
                });
            }

            // Action buttons
            const firstActionButton = document.querySelector('.btn-primary[href*="edit_opdracht"]');
            if (firstActionButton) {
                steps.push({
                    element: firstActionButton.parentElement,
                    title: this.getText('assignmentsActionsTitle'),
                    content: this.getText('assignmentsActionsIntro'),
                    position: 'left'
                });
            }
        }
        
        else if (this.currentPage === 'facturen') {
            // Search card
            const searchCard = document.querySelector('.card.shadow.mb-4');
            if (searchCard) {
                steps.push({
                    element: searchCard,
                    title: this.getText('invoicesSearchTitle'),
                    content: this.getText('invoicesSearchIntro'),
                    position: 'bottom'
                });
            }

            // Invoices table
            const invoicesTable = document.querySelector('.table-responsive');
            if (invoicesTable) {
                steps.push({
                    element: invoicesTable,
                    title: this.getText('invoicesTableTitle'),
                    content: this.getText('invoicesTableIntro'),
                    position: 'top'
                });
            }

            // Action buttons
            const firstActionButton = document.querySelector('.btn-group');
            if (firstActionButton) {
                steps.push({
                    element: firstActionButton,
                    title: this.getText('invoicesActionsTitle'),
                    content: this.getText('invoicesActionsIntro'),
                    position: 'left'
                });
            }

            // New invoice button
            const newInvoiceButton = document.querySelector('.btn-primary[href*="nieuwe_factuur"]');
            if (newInvoiceButton) {
                steps.push({
                    element: newInvoiceButton,
                    title: this.getText('invoicesCreateTitle'),
                    content: this.getText('invoicesCreateIntro'),
                    position: 'left'
                });
            }
        }
        
        else if (this.currentPage === 'reports') {
            // Report cards
            const reportCards = document.querySelectorAll('.card');
            if (reportCards.length > 0) {
                steps.push({
                    element: reportCards[0].parentElement,
                    title: this.getText('reportsCardsTitle'),
                    content: this.getText('reportsCardsIntro'),
                    position: 'bottom'
                });
            }
        }
        
        else if (this.currentPage === 'admin') {
            // Check if it's the main admin dashboard or users page
            const usersTable = document.querySelector('.table-striped');
            if (usersTable) {
                // Admin users page
                const usersCard = document.querySelector('.card');
                if (usersCard) {
                    steps.push({
                        element: usersCard.querySelector('.card-header'),
                        title: this.getText('adminUsersTitle'),
                        content: this.getText('adminUsersIntro'),
                        position: 'bottom'
                    });
                }

                steps.push({
                    element: usersTable,
                    title: this.getText('adminUsersTableTitle'),
                    content: this.getText('adminUsersTableIntro'),
                    position: 'top'
                });

                const firstActionButton = document.querySelector('.btn-outline-primary[data-bs-toggle="modal"]');
                if (firstActionButton) {
                    steps.push({
                        element: firstActionButton,
                        title: this.getText('adminUsersActionsTitle'),
                        content: this.getText('adminUsersActionsIntro'),
                        position: 'left'
                    });
                }
            } else {
                // Main admin dashboard
                const adminCard = document.querySelector('.card');
                if (adminCard) {
                    steps.push({
                        element: adminCard,
                        title: this.getText('adminPageTitle'),
                        content: this.getText('adminPageIntro'),
                        position: 'bottom'
                    });
                }
            }
        }
        
        else if (this.currentPage === 'klanten_form' || this.currentPage === 'medewerkers_form' || this.currentPage === 'opdrachten_form') {
            // Form card
            const formCard = document.querySelector('.card');
            if (formCard) {
                steps.push({
                    element: formCard.querySelector('.card-header'),
                    title: this.getText('formTitle'),
                    content: this.getText('formIntro'),
                    position: 'bottom'
                });
            }

            // Form fields
            const formBody = document.querySelector('.card-body form');
            if (formBody) {
                steps.push({
                    element: formBody,
                    title: this.getText('formFieldsTitle'),
                    content: this.getText('formFieldsIntro'),
                    position: 'right'
                });
            }

            // Form buttons
            const formButtons = document.querySelector('.d-flex.justify-content-between');
            if (formButtons) {
                steps.push({
                    element: formButtons,
                    title: this.getText('formButtonsTitle'),
                    content: this.getText('formButtonsIntro'),
                    position: 'top'
                });
            }
        }

        // If no steps were found, add a generic welcome step
        if (steps.length === 0 && this.currentPage === 'time_entries') {
            console.log('No specific elements found, adding generic time entries step'); // Debug log
            const bodyElement = document.body;
            steps.push({
                element: bodyElement,
                title: this.getText('timeEntriesPageTitle'),
                content: this.getText('timeEntriesPageIntro'),
                position: 'bottom'
            });
        }
        
        console.log('Final tour steps count:', steps.length); // Debug log
        this.tourSteps = steps;
        return steps;
    }

    showWelcomeModal() {
        if (document.querySelector('.welcome-modal-overlay')) return;
        
        const modal = document.createElement('div');
        modal.className = 'welcome-modal-overlay';
        modal.innerHTML = `
            <div class="welcome-modal">
                <div class="welcome-modal-header">
                    <h2>${this.getText('welcomeTitle')}</h2>
                    <button class="welcome-modal-close" aria-label="Close">&times;</button>
                </div>
                <div class="welcome-modal-body">
                    <p>${this.getText('welcomeMessage')}</p>
                    <div class="welcome-features">
                        <div class="feature">
                            <span class="feature-icon">⏰</span>
                            <span>${this.getText('welcomeFeature1')}</span>
                        </div>
                        <div class="feature">
                            <span class="feature-icon">👥</span>
                            <span>${this.getText('welcomeFeature2')}</span>
                        </div>
                        <div class="feature">
                            <span class="feature-icon">📊</span>
                            <span>${this.getText('welcomeFeature3')}</span>
                        </div>
                        <div class="feature">
                            <span class="feature-icon">✅</span>
                            <span>${this.getText('welcomeFeature4')}</span>
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
        
        // Smooth fade in
        modal.style.opacity = '0';
        setTimeout(() => {
            modal.style.transition = 'opacity 0.3s ease';
            modal.style.opacity = '1';
        }, 10);
        
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
        
        // Keyboard navigation
        modal.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeWelcomeModal(modal);
            }
        });
    }

    closeWelcomeModal(modal) {
        modal.style.opacity = '0';
        setTimeout(() => {
            modal.remove();
        }, 300);
    }

    startTour() {
        this.generateTourSteps();
        
        if (this.tourSteps.length === 0) {
            this.showNoContentMessage();
            return;
        }
        
        this.currentStep = 0;
        this.isActive = true;
        this.showStep(this.currentStep);
    }

    showStep(stepIndex) {
        if (stepIndex >= this.tourSteps.length) {
            this.completeTour();
            return;
        }
        
        const step = this.tourSteps[stepIndex];
        if (!step.element) {
            this.nextStep();
            return;
        }
        
        // Remove any existing tooltip
        this.removeTooltip();
        
        // Create highlight overlay
        this.createHighlight(step.element);
        
        // Create tooltip
        this.createTooltip(step, stepIndex);
        
        // Scroll to element
        this.scrollToElement(step.element);
    }

    createHighlight(element) {
        // Remove existing highlights and overlays
        document.querySelectorAll('.tour-highlight, .tour-overlay').forEach(h => h.remove());
        
        // Ensure element is visible and get accurate position
        if (!element || !element.offsetParent) {
            console.warn('Element not visible for highlighting:', element);
            return;
        }
        
        // Wait for any layout changes to complete
        setTimeout(() => {
            const rect = element.getBoundingClientRect();
            
            // Check if element is actually visible
            if (rect.width === 0 || rect.height === 0) {
                console.warn('Element has no dimensions:', element);
                return;
            }
            
            // Create overlay to darken the rest of the page
            const overlay = document.createElement('div');
            overlay.className = 'tour-overlay';
            document.body.appendChild(overlay);
            
            // Create highlight for the specific element
            const highlight = document.createElement('div');
            highlight.className = 'tour-highlight';
            
            // Add some padding around the element
            const padding = 8;
            const borderRadius = Math.min(12, rect.height / 4);
            
            // Detect dark mode for better highlighting
            const isDarkMode = document.documentElement.getAttribute('data-bs-theme') === 'dark';
            const highlightColor = isDarkMode ? '#4dabf7' : '#0d6efd';
            const backgroundColor = isDarkMode ? 'rgba(77, 171, 247, 0.15)' : 'rgba(13, 110, 253, 0.08)';
            const shadowColor = isDarkMode ? 'rgba(77, 171, 247, 0.3)' : 'rgba(13, 110, 253, 0.2)';
            
            highlight.style.cssText = `
                position: fixed;
                top: ${rect.top - padding}px;
                left: ${rect.left - padding}px;
                width: ${rect.width + (padding * 2)}px;
                height: ${rect.height + (padding * 2)}px;
                border: 3px solid ${highlightColor};
                border-radius: ${borderRadius}px;
                background: ${backgroundColor};
                z-index: 9998;
                pointer-events: none;
                animation: tourHighlight 0.3s ease;
                box-shadow: 0 0 0 3px ${shadowColor}, 0 4px 20px ${shadowColor};
            `;
            
            document.body.appendChild(highlight);
            
            // Update highlight position on scroll/resize
            const updatePosition = () => {
                const newRect = element.getBoundingClientRect();
                if (newRect.width > 0 && newRect.height > 0) {
                    highlight.style.top = `${newRect.top - padding}px`;
                    highlight.style.left = `${newRect.left - padding}px`;
                    highlight.style.width = `${newRect.width + (padding * 2)}px`;
                    highlight.style.height = `${newRect.height + (padding * 2)}px`;
                }
            };
            
            // Store update function and overlay for cleanup
            highlight._updatePosition = updatePosition;
            highlight._overlay = overlay;
            window.addEventListener('scroll', updatePosition, { passive: true });
            window.addEventListener('resize', updatePosition, { passive: true });
        }, 100);
    }

    createTooltip(step, stepIndex) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tour-tooltip';
        
        const progress = Math.round(((stepIndex + 1) / this.tourSteps.length) * 100);
        
        tooltip.innerHTML = `
            <div class="tour-tooltip-header">
                <h3>${step.title}</h3>
                <div class="tour-progress">
                    <div class="tour-progress-bar" style="width: ${progress}%"></div>
                </div>
            </div>
            <div class="tour-tooltip-body">
                <p>${step.content}</p>
            </div>
            <div class="tour-tooltip-footer">
                <div class="tour-step-counter">${stepIndex + 1} / ${this.tourSteps.length}</div>
                <div class="tour-buttons">
                    ${stepIndex > 0 ? `<button class="btn btn-secondary tour-prev">${this.getText('prev')}</button>` : ''}
                    <button class="btn btn-outline-secondary tour-skip">${this.getText('skip')}</button>
                    <button class="btn btn-primary tour-next">
                        ${stepIndex === this.tourSteps.length - 1 ? this.getText('done') : this.getText('next')}
                    </button>
                </div>
            </div>
        `;
        
        // Position tooltip
        this.positionTooltip(tooltip, step.element, step.position);
        
        document.body.appendChild(tooltip);
        
        // Add event listeners
        const nextBtn = tooltip.querySelector('.tour-next');
        const prevBtn = tooltip.querySelector('.tour-prev');
        const skipBtn = tooltip.querySelector('.tour-skip');
        
        nextBtn.addEventListener('click', () => this.nextStep());
        if (prevBtn) prevBtn.addEventListener('click', () => this.prevStep());
        skipBtn.addEventListener('click', () => this.skipTour());
        
        // Auto-advance disabled for better user control
        // Users can navigate at their own pace
    }

    positionTooltip(tooltip, element, position = 'bottom') {
        const rect = element.getBoundingClientRect();
        const tooltipRect = { width: 350, height: 200 }; // Estimated size
        
        let top, left;
        
        switch (position) {
            case 'top':
                top = rect.top - tooltipRect.height - 20;
                left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
                break;
            case 'bottom':
                top = rect.bottom + 20;
                left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
                break;
            case 'left':
                top = rect.top + (rect.height / 2) - (tooltipRect.height / 2);
                left = rect.left - tooltipRect.width - 20;
                break;
            case 'right':
                top = rect.top + (rect.height / 2) - (tooltipRect.height / 2);
                left = rect.right + 20;
                break;
            default:
                top = rect.bottom + 20;
                left = rect.left + (rect.width / 2) - (tooltipRect.width / 2);
        }
        
        // Keep tooltip within viewport
        const margin = 20;
        top = Math.max(margin, Math.min(top, window.innerHeight - tooltipRect.height - margin));
        left = Math.max(margin, Math.min(left, window.innerWidth - tooltipRect.width - margin));
        
        tooltip.style.cssText = `
            position: fixed;
            top: ${top}px;
            left: ${left}px;
            z-index: 9999;
            animation: tourTooltipIn 0.3s ease;
        `;
    }

    scrollToElement(element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'center',
            inline: 'center'
        });
    }

    nextStep() {
        this.currentStep++;
        this.showStep(this.currentStep);
    }

    prevStep() {
        if (this.currentStep > 0) {
            this.currentStep--;
            this.showStep(this.currentStep);
        }
    }

    skipTour() {
        this.isActive = false;
        this.removeTooltip();
        this.removeHighlight();
    }

    completeTour() {
        this.isActive = false;
        this.removeTooltip();
        this.removeHighlight();
        this.markTourCompleted();
        this.showCompletionMessage();
    }

    removeTooltip() {
        document.querySelectorAll('.tour-tooltip').forEach(t => t.remove());
    }

    removeHighlight() {
        document.querySelectorAll('.tour-highlight').forEach(h => {
            // Clean up event listeners
            if (h._updatePosition) {
                window.removeEventListener('scroll', h._updatePosition);
                window.removeEventListener('resize', h._updatePosition);
            }
            // Remove associated overlay
            if (h._overlay) {
                h._overlay.remove();
            }
            h.remove();
        });
        
        // Also remove any standalone overlays
        document.querySelectorAll('.tour-overlay').forEach(o => o.remove());
    }

    showCompletionMessage() {
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
        
        message.querySelector('.tour-completion-close').addEventListener('click', () => {
            message.remove();
        });
        
        setTimeout(() => {
            if (message.parentNode) {
                message.remove();
            }
        }, 5000);
    }

    showNoContentMessage() {
        const message = document.createElement('div');
        message.className = 'tour-message';
        message.innerHTML = `
            <div class="tour-message-content">
                <h4>${this.getText('noTourTitle')}</h4>
                <p>${this.getText('noTourMessage')}</p>
                <button class="btn btn-primary tour-message-close">${this.getText('noTourButton')}</button>
            </div>
        `;
        
        document.body.appendChild(message);
        
        message.querySelector('.tour-message-close').addEventListener('click', () => {
            message.remove();
        });
    }

    resetTourStatus() {
        localStorage.removeItem('intro_guide_completed');
        localStorage.removeItem('intro_guide_completed_date');
    }
}

// Initialize the guide
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        try {
            window.universalIntroGuide = new UniversalIntroGuide();
        } catch (error) {
            console.warn('Failed to initialize Universal Intro Guide:', error);
        }
    }, 500);
});

// Global functions for external access
window.resetIntroGuide = function() {
    if (window.universalIntroGuide) {
        window.universalIntroGuide.resetTourStatus();
        location.reload();
    }
};

window.startIntroTour = function() {
    if (window.universalIntroGuide) {
        window.universalIntroGuide.startTour();
    }
};