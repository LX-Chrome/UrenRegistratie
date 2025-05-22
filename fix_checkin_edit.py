import sqlite3
from app import app

def fix_edit_checkin_fields():
    print("Checking database structure for check_in table...")
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()
    
    # Check if the opdracht_id column exists in check_in table
    cursor.execute("PRAGMA table_info(check_in)")
    columns = cursor.fetchall()
    check_in_has_opdracht_id = any(col[1] == 'opdracht_id' for col in columns)
    
    if not check_in_has_opdracht_id:
        print("ERROR: The opdracht_id column is missing from check_in table!")
        print("Please run add_opdracht_columns.py first!")
        return
    else:
        print("✓ check_in table has opdracht_id column")
    
    # Check some sample data
    cursor.execute("""
        SELECT ci.id, ci.status, ci.check_in_time, ci.note, ci.opdracht_id, o.titel 
        FROM check_in ci
        LEFT JOIN opdracht o ON ci.opdracht_id = o.id
        ORDER BY ci.check_in_time DESC LIMIT 5
    """)
    sample_data = cursor.fetchall()
    
    if sample_data:
        print("\nSample check-in data:")
        print("ID | Status | Time | Note | Assignment ID | Assignment Title")
        print("-" * 80)
        for data in sample_data:
            assignment = f"{data[4]} - {data[5]}" if data[4] else "None"
            print(f"{data[0]} | {data[1]} | {data[2]} | {data[3]} | {assignment}")
    
    # Validate the static-modal JS code
    print("\nChecking for potential JavaScript issues...")
    
    # Create a debug version of the dashboard that will add console logs for debugging
    print("\nCreating debug version of templates/dashboard.html...")
    with open('templates/dashboard_debug.html', 'w') as f:
        with open('templates/dashboard.html', 'r') as original:
            content = original.read()
            # Add debug code before </script>
            debug_code = """
    // Debug code for check-in edit buttons
    console.log("Debug mode active for check-in edit buttons");
    
    // Examine all check-in edit buttons
    document.querySelectorAll('.edit-checkin-btn').forEach(function(btn) {
        console.log("Found edit button:", btn);
        console.log("  data-id:", btn.getAttribute('data-id'));
        console.log("  data-status:", btn.getAttribute('data-status'));
        console.log("  data-time:", btn.getAttribute('data-time'));
        console.log("  data-note:", btn.getAttribute('data-note'));
        console.log("  data-opdracht-id:", btn.getAttribute('data-opdracht-id'));
        console.log("  data-form-action:", btn.getAttribute('data-form-action'));
        
        // Add explicit click handler for debugging
        btn.addEventListener('click', function(e) {
            console.log("Edit button clicked:", this);
            console.log("Using form action:", this.getAttribute('data-form-action'));
            console.log("Assignment ID:", this.getAttribute('data-opdracht-id'));
        });
    });
"""
            # Insert before the last </script>
            content = content.replace('</script>', debug_code + '\n</script>')
            f.write(content)
    
    print("\nDebugging file created at templates/dashboard_debug.html")
    print("To debug the issue:")
    print("1. Open your browser's developer console (F12)")
    print("2. Navigate to http://localhost:5000/debug-dashboard")
    print("3. Watch the console as you click the edit buttons")
    
    # Create a route for the debug dashboard
    print("\nAdding debug route to app...")
    
    @app.route('/debug-dashboard')
    def debug_dashboard():
        """Debug version of the dashboard for troubleshooting check-in edit issues"""
        from flask import render_template
        from flask_login import current_user, login_required
        from models import TimeEntry, CheckIn, Klant, Opdracht
        from sqlalchemy import func
        from datetime import datetime
        
        @login_required
        def inner_function():
            # Get 5 most recent time entries
            entries = TimeEntry.query.filter_by(user_id=current_user.id).order_by(TimeEntry.date.desc()).limit(5).all()
            
            # Get today's check-ins for the current user
            today = datetime.now().date()
            check_ins = CheckIn.query.filter_by(user_id=current_user.id).filter(
                func.date(CheckIn.check_in_time) == today
            ).order_by(CheckIn.check_in_time.desc()).limit(5).all()
            
            # Get active clients and open assignments for dropdown selectors
            clients = Klant.query.filter_by(status='actief').order_by(Klant.bedrijfsnaam).all()
            
            # Get assignments
            if current_user.can_view_all():
                opdrachten = Opdracht.query.filter(Opdracht.status.in_(['open', 'in-progress'])).order_by(Opdracht.titel).all()
            else:
                user_client_ids = db.session.query(Opdracht.klant_id)\
                    .join(TimeEntry, TimeEntry.opdracht_id == Opdracht.id)\
                    .filter(TimeEntry.user_id == current_user.id)\
                    .distinct().all()
                user_client_ids = [c[0] for c in user_client_ids]
                opdrachten = Opdracht.query.filter(
                    Opdracht.status.in_(['open', 'in-progress']),
                    Opdracht.klant_id.in_(user_client_ids) if user_client_ids else False
                ).order_by(Opdracht.titel).all()
            
            return render_template('dashboard_debug.html', entries=entries, check_ins=check_ins, clients=clients, opdrachten=opdrachten)
        
        return inner_function()
    
    # Add a simple fix script for the custom modal
    print("\nCreating a fix for custom-modal.js...")
    with open('static/js/fix-custom-modal.js', 'w') as f:
        f.write("""/**
 * Fix for check-in edit modal
 */
console.log("Loading check-in edit modal fix...");

document.addEventListener('DOMContentLoaded', function() {
    // Wait for the page to be fully loaded
    setTimeout(function() {
        console.log("Applying check-in edit button fix...");
        
        // Find all check-in edit buttons
        const editButtons = document.querySelectorAll('.edit-checkin-btn');
        console.log(`Found ${editButtons.length} edit buttons to fix`);
        
        // Ensure they have the correct event handlers
        editButtons.forEach(function(button) {
            // Remove old listeners
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);
            
            // Add new click handler
            newButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const formAction = this.getAttribute('data-form-action') || '';
                const status = this.getAttribute('data-status') || 'working';
                const timeValue = this.getAttribute('data-time') || '';
                const noteValue = this.getAttribute('data-note') || '';
                const opdrachtId = this.getAttribute('data-opdracht-id') || '';
                
                console.log("Edit button clicked with data:", {
                    formAction: formAction,
                    status: status, 
                    timeValue: timeValue,
                    noteValue: noteValue,
                    opdrachtId: opdrachtId
                });
                
                if (typeof window.openStaticCheckinModal === 'function') {
                    window.openStaticCheckinModal(formAction, status, timeValue, noteValue, opdrachtId);
                } else {
                    console.error("openStaticCheckinModal function not found!");
                }
                
                return false;
            });
        });
        
        console.log("Fix applied!");
    }, 500); // Wait 500ms to ensure everything is loaded
});
""")
    
    print("\nCreated fix-custom-modal.js in static/js/")
    print("\nTo apply the fix, add this to your dashboard.html before {% endblock %}:")
    print('<script src="{{ url_for(\'static\', filename=\'js/fix-custom-modal.js\') }}"></script>')
    
    conn.close()
    print("\nDiagnostic complete.")

if __name__ == "__main__":
    with app.app_context():
        fix_edit_checkin_fields() 