#!/usr/bin/env python3
"""
Quick fix for dashboard - directly updates missing JSON templates
"""
import os
import shutil
import time

# Get the full path to the templates directory
base_dir = os.path.dirname(os.path.abspath(__file__))
dashboard_template = os.path.join(base_dir, 'templates', 'dashboard.html')

# Backup the file
backup_path = os.path.join(base_dir, 'templates', f'dashboard.html.bak.{int(time.time())}')
shutil.copy2(dashboard_template, backup_path)
print(f"Created backup at {backup_path}")

# Read the template file
with open(dashboard_template, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if we need to fix the template
if '<!-- JSON data for dashboard -->' in content and '<script id="checkins-data-json"' in content:
    # Find where to add the additional script tags
    checkins_script_tag = '<script id="checkins-data-json" type="application/json">\n{{ check_ins_json | tojson }}\n</script>'
    
    # Fix by adding additional script tags for clients and assignments
    clients_script_tag = '<script id="clients-data-json" type="application/json">\n{{ clients | tojson }}\n</script>'
    assignments_script_tag = '<script id="assignments-data-json" type="application/json">\n{{ opdrachten | tojson }}\n</script>'
    
    # Replace the existing script tag section with all three script tags
    new_script_section = f"""<!-- JSON data for dashboard -->
{checkins_script_tag}
{clients_script_tag}
{assignments_script_tag}"""

    # Replace in the content
    content = content.replace(
        f'<!-- JSON data for dashboard -->\n{checkins_script_tag}', 
        new_script_section
    )
    
    # Write the updated content
    with open(dashboard_template, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Template updated successfully")
else:
    print("No modification needed in the template")

print("Dashboard fix completed.")
print("Next step: Run 'sudo ./restart.sh' to restart the application") 