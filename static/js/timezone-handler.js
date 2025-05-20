/**
 * Timezone handler for UrenRegistratie
 * This script handles converting between UTC and local timezones
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize timezone handling
    initializeTimezoneHandling();
    
    // Initialize UTC time inputs with local time values
    setupTimeInputs();
    
    // Set up a MutationObserver to watch for dynamically added time elements
    setupMutationObserver();
});

/**
 * Initialize timezone handling for the application
 */
function initializeTimezoneHandling() {
    console.log("Initializing timezone handling...");
    console.log("Browser timezone:", Intl.DateTimeFormat().resolvedOptions().timeZone);
    console.log("Timezone offset in minutes:", new Date().getTimezoneOffset());
    console.log("UTC time:", new Date().toISOString());
    console.log("Local time:", new Date().toLocaleString());
    
    // Convert all UTC times to local
    convertUTCTimesToLocal();
    
    // Setup event listeners for forms that handle times
    setupTimeFormHandlers();
}

/**
 * Convert all displayed UTC times to local timezone
 */
function convertUTCTimesToLocal() {
    // Get all elements with utc-time class
    const utcTimeElements = document.querySelectorAll('.utc-time');
    
    utcTimeElements.forEach(element => {
        const utcTime = element.getAttribute('data-utc-time');
        if (utcTime) {
            const localTime = convertUTCToLocal(utcTime);
            element.textContent = formatTime(localTime);
            
            // Update title attribute with full local time for tooltip
            const options = { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' };
            element.title = localTime.toLocaleString(undefined, options);
            
            // Also add this data attribute for debugging
            element.setAttribute('data-local-time', localTime.toLocaleString());
        }
    });
    
    // Handle inputs separately
    const utcTimeInputs = document.querySelectorAll('.utc-time-input');
    utcTimeInputs.forEach(input => {
        const utcTime = input.getAttribute('data-utc-time');
        if (utcTime) {
            const localDate = new Date(utcTime);
            input.value = formatTimeInput(localDate);
            input.setAttribute('data-local-time', localDate.toLocaleString());
        }
    });
    
    console.log(`Converted ${utcTimeElements.length} time elements to local timezone`);
}

/**
 * Setup a MutationObserver to watch for dynamically added time elements
 */
function setupMutationObserver() {
    // Create an observer instance
    const observer = new MutationObserver(function(mutations) {
        let shouldProcess = false;
        
        // Check if any mutations involve adding nodes that might contain time elements
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        if (node.classList && node.classList.contains('utc-time')) {
                            shouldProcess = true;
                        } else if (node.querySelectorAll) {
                            const timeElements = node.querySelectorAll('.utc-time');
                            if (timeElements.length > 0) {
                                shouldProcess = true;
                            }
                        }
                    }
                });
            }
        });
        
        // If we found elements that need timezone conversion, process them
        if (shouldProcess) {
            console.log('Detected dynamically added time elements, converting timezone...');
            convertUTCTimesToLocal();
        }
    });
    
    // Start observing the document with the configured parameters
    observer.observe(document.body, { childList: true, subtree: true });
    console.log('MutationObserver set up for dynamic time elements');
}

/**
 * Setup time inputs to properly handle local time
 */
function setupTimeInputs() {
    // Add event handlers to time entry form
    const addEntryForm = document.querySelector('#addEntryModal form');
    if (addEntryForm) {
        // Set the date input to current local date
        const dateInput = addEntryForm.querySelector('#date');
        if (dateInput) {
            const localDate = new Date();
            dateInput.value = formatDate(localDate);
        }
    }
    
    // Handle all time entry date inputs
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        // If the input has a value in UTC, convert to local
        if (input.getAttribute('data-utc-time')) {
            const utcTime = input.getAttribute('data-utc-time');
            const localDate = new Date(utcTime);
            input.value = formatDate(localDate);
        }
    });
}

/**
 * Setup handlers for forms that deal with time data
 */
function setupTimeFormHandlers() {
    // Add entry modal form
    const addEntryForm = document.querySelector('#addEntryModal form');
    if (addEntryForm) {
        addEntryForm.addEventListener('submit', function(e) {
            // The date is submitted in local time, server will convert to UTC
            console.log("Submitting time entry form with local date");
        });
    }
    
    // Edit entry modal forms
    document.querySelectorAll('[id^="editEntryModal"] form').forEach(form => {
        form.addEventListener('submit', function(e) {
            console.log("Submitting edit entry form with local date");
        });
    });
    
    // Edit check-in forms
    document.querySelectorAll('[id^="editCheckinModal"] form').forEach(form => {
        form.addEventListener('submit', function(e) {
            console.log("Submitting edit check-in form");
            // Time inputs are already in local time format
        });
    });
}

/**
 * Convert UTC datetime string to local Date object
 * JavaScript's Date constructor automatically converts UTC to local time
 * when creating a date from an ISO string
 */
function convertUTCToLocal(utcTime) {
    try {
        // Handle timezone conversion properly
        // Date constructor will automatically convert to local time
        const date = new Date(utcTime);
        console.log(`Converting UTC time ${utcTime} to local: ${date.toLocaleString()}`);
        return date;
    } catch (e) {
        console.error(`Error converting time ${utcTime}:`, e);
        return new Date(); // Return current time as fallback
    }
}

/**
 * Format a Date object as HH:MM for display
 */
function formatTime(date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/**
 * Format a Date object as HH:MM for time inputs
 */
function formatTimeInput(date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
}

/**
 * Format a Date object as YYYY-MM-DD for date inputs
 */
function formatDate(date) {
    // This creates local date YYYY-MM-DD format
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}
