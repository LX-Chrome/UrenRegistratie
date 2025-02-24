
const translations = {
    en: {
        "Dashboard": "Dashboard",
        "Tijdregistratie": "Time Registration",
        "Klanten": "Clients",
        "Medewerkers": "Employees",
        "Opdrachten": "Assignments",
        "Bewerken": "Edit",
        "Verwijderen": "Delete",
        "Zoeken": "Search",
        "Annuleren": "Cancel",
        "Nieuwe Medewerker": "New Employee",
        "Voornaam": "First Name",
        "Tussenvoegsel": "Middle Name",
        "Achternaam": "Last Name",
        "Geboortedatum": "Date of Birth",
        "Functie": "Function",
        "Werkmail": "Work Email",
        "Kantoorruimte": "Office Space"
    }
};

let currentLang = 'nl';

function toggleLanguage() {
    currentLang = currentLang === 'nl' ? 'en' : 'nl';
    translatePage();
}

function translatePage() {
    if (currentLang === 'nl') return; // Dutch is default

    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        if (translations.en[key]) {
            element.textContent = translations.en[key];
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    translatePage();
});
