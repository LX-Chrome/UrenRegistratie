import json
from datetime import datetime, time
from flask import render_template, redirect, url_for, request, flash, make_response, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from models import User, TimeEntry, Klant, Medewerker, Opdracht, Werkzaamheid, CheckIn, Factuur, Role, RoleEnum
from services.export_service import ExportService
# Import our direct PDF generation function
from routes_invoices import generate_pdf_from_template
import io
# Temporarily comment out pandas to help diagnose startup issues
# import pandas as pd
import csv
from werkzeug.utils import secure_filename
import os
from sqlalchemy import func, extract
from auth_helpers import admin_required

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.check_password(request.form['password']):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        if User.query.filter_by(email=request.form['email']).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(
            username=request.form['username'],
            email=request.form['email']
        )
        user.set_password(request.form['password'])
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Show dashboard with user's time entries and check-ins"""
    # Get 5 most recent time entries
    entries = TimeEntry.query.filter_by(user_id=current_user.id).order_by(TimeEntry.date.desc()).limit(5).all()
    
    # Get today's check-ins for the current user
    # Using local date (not UTC)
    today = datetime.now().date()
    check_ins = CheckIn.query.filter_by(user_id=current_user.id).filter(
        func.date(CheckIn.check_in_time) == today
    ).order_by(CheckIn.check_in_time.desc()).limit(5).all()
    
    # Debug log check-ins
    app.logger.debug(f"Retrieved {len(check_ins)} check-ins for user {current_user.id}")
    for check_in in check_ins:
        app.logger.debug(f"Check-in ID: {check_in.id}, Time: {check_in.check_in_time}, Status: {check_in.status}")
    
    # Get active clients and open assignments for dropdown selectors
    clients = Klant.query.filter_by(status='actief').order_by(Klant.bedrijfsnaam).all()
    
    # If current user has admin or management role, show all assignments
    if current_user.can_view_all():
        opdrachten = Opdracht.query.filter(Opdracht.status.in_(['open', 'in-progress'])).order_by(Opdracht.titel).all()
    else:
        # Otherwise, only show assignments from clients this user has worked with
        user_client_ids = db.session.query(Opdracht.klant_id)\
            .join(TimeEntry, TimeEntry.opdracht_id == Opdracht.id)\
            .filter(TimeEntry.user_id == current_user.id)\
            .distinct().all()
        user_client_ids = [c[0] for c in user_client_ids]
        opdrachten = Opdracht.query.filter(
            Opdracht.status.in_(['open', 'in-progress']),
            Opdracht.klant_id.in_(user_client_ids) if user_client_ids else False
        ).order_by(Opdracht.titel).all()
    
    # Prepare check-ins data for JSON serialization
    check_ins_json = []
    for check_in in check_ins:
        check_in_dict = {
            'id': check_in.id,
            'status': check_in.status,
            'check_in_time': check_in.check_in_time.strftime('%H:%M') if check_in.check_in_time else None,
            'note': check_in.note,
            'opdracht_id': check_in.opdracht_id
        }
        check_ins_json.append(check_in_dict)
    
    return render_template('dashboard.html', entries=entries, check_ins=check_ins, 
                          clients=clients, opdrachten=opdrachten, 
                          check_ins_json=check_ins_json)

@app.route('/time-entries', methods=['GET', 'POST'])
@login_required
def time_entries():
    search = request.args.get('search', '')
    client_id = request.args.get('client_id', '')
    opdracht_id = request.args.get('opdracht_id', '')
    from_dashboard = 'from_dashboard' in request.args
    new = 'new' in request.args
    
    # Get all clients and assignments for the dropdowns
    clients = Klant.query.filter_by(status='actief').order_by(Klant.bedrijfsnaam).all()
    
    # If current user has admin or management role, show all assignments
    if current_user.can_view_all():
        opdrachten = Opdracht.query.filter(Opdracht.status.in_(['open', 'in-progress'])).order_by(Opdracht.titel).all()
    else:
        # Otherwise, only show assignments from clients this user has worked with
        user_client_ids = db.session.query(Opdracht.klant_id)\
            .join(TimeEntry, TimeEntry.opdracht_id == Opdracht.id)\
            .filter(TimeEntry.user_id == current_user.id)\
            .distinct().all()
        user_client_ids = [c[0] for c in user_client_ids]
        opdrachten = Opdracht.query.filter(
            Opdracht.status.in_(['open', 'in-progress']),
            Opdracht.klant_id.in_(user_client_ids) if user_client_ids else False
        ).order_by(Opdracht.titel).all()
    
    if request.method == 'POST':
        date_str = request.form.get('date')
        project = request.form.get('project')
        hours = request.form.get('hours')
        description = request.form.get('description')
        opdracht_id_form = request.form.get('opdracht_id')
        is_billable = 'is_billable' in request.form
        
        # Validate input
        if not date_str or not project or not hours or not description:
            flash('All fields are required!', 'error')
            return redirect(url_for('time_entries'))
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            hours_float = float(hours)
        except ValueError:
            flash('Invalid date or hours format!', 'error')
            return redirect(url_for('time_entries'))
        
        # Create the time entry
        entry = TimeEntry(
            date=date_obj,
            project=project,
            hours=hours_float,
            description=description,
            user_id=current_user.id,
            is_billable=is_billable
        )
        
        # Connect to opdracht if provided
        if opdracht_id_form:
            try:
                entry.opdracht_id = int(opdracht_id_form)
                
                # Get hourly rate from assignment if billable
                if is_billable:
                    opdracht = Opdracht.query.get(int(opdracht_id_form))
                    if opdracht and opdracht.uurtarief:
                        entry.hourly_rate = opdracht.uurtarief
            except ValueError:
                flash('Invalid assignment selected', 'error')
                return redirect(url_for('time_entries'))
        
        db.session.add(entry)
        
        try:
            db.session.commit()
            flash('Time entry added successfully!', 'success')
        except:
            db.session.rollback()
            flash('Error adding time entry!', 'error')
        
        # Redirect to dashboard if coming from there
        if request.form.get('redirect_to_dashboard') == 'true':
            return redirect(url_for('dashboard'))
        
        return redirect(url_for('time_entries'))
    
    # For GET request, fetch time entries
    entries_query = TimeEntry.query.filter_by(user_id=current_user.id)
    
    if search:
        entries_query = entries_query.filter(TimeEntry.description.contains(search) |
                                         TimeEntry.project.contains(search))
                                         
    if client_id:
        entries_query = entries_query.join(Opdracht, TimeEntry.opdracht_id == Opdracht.id)\
                                    .filter(Opdracht.klant_id == int(client_id))
                                    
    if opdracht_id:
        entries_query = entries_query.filter(TimeEntry.opdracht_id == int(opdracht_id))
    
    entries = entries_query.order_by(TimeEntry.date.desc()).all()
    
    return render_template('time_entries.html', 
                           entries=entries, 
                           search=search,
                           client_id=client_id,
                           opdracht_id=opdracht_id,
                           clients=clients,
                           opdrachten=opdrachten,
                           datetime=datetime,
                           from_dashboard=from_dashboard,
                           new=new)
    
@app.route('/time-entries/<int:entry_id>/edit', methods=['POST'])
@login_required
def edit_time_entry(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    
    # Check if this entry belongs to the current user
    if entry.user_id != current_user.id and not current_user.can_edit_all():
        flash('You do not have permission to edit this entry!', 'error')
        return redirect(url_for('time_entries'))
    
    if request.method == 'POST':
        date_str = request.form.get('date')
        project = request.form.get('project')
        hours = request.form.get('hours')
        description = request.form.get('description')
        opdracht_id_form = request.form.get('opdracht_id')
        is_billable = 'is_billable' in request.form
        
        # Validate input
        if not date_str or not project or not hours or not description:
            flash('All fields are required!', 'error')
            return redirect(url_for('time_entries', edit=entry_id))
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            hours_float = float(hours)
        except ValueError:
            flash('Invalid date or hours format!', 'error')
            return redirect(url_for('time_entries', edit=entry_id))
        
        # Update the entry
        entry.date = date_obj
        entry.project = project
        entry.hours = hours_float
        entry.description = description
        entry.is_billable = is_billable
        
        # Update assignment connection
        old_opdracht_id = entry.opdracht_id
        
        if opdracht_id_form:
            try:
                new_opdracht_id = int(opdracht_id_form)
                entry.opdracht_id = new_opdracht_id
                
                # Update hourly rate if assignment changed and entry is billable
                if is_billable and (old_opdracht_id != new_opdracht_id):
                    opdracht = Opdracht.query.get(new_opdracht_id)
                    if opdracht and opdracht.uurtarief:
                        entry.hourly_rate = opdracht.uurtarief
            except ValueError:
                flash('Invalid assignment selected', 'error')
                return redirect(url_for('time_entries', edit=entry_id))
        else:
            entry.opdracht_id = None
        
        try:
            db.session.commit()
            flash('Time entry updated successfully!', 'success')
        except:
            db.session.rollback()
            flash('Error updating time entry!', 'error')
        
        return redirect(url_for('time_entries'))

@app.route('/time-entries/<int:entry_id>/delete')
@login_required
def delete_time_entry(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('time_entries'))

    try:
        db.session.delete(entry)
        db.session.commit()
        flash('Time entry deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting time entry: ' + str(e), 'danger')
        app.logger.error(f"Error deleting time entry: {str(e)}")

    return redirect(url_for('time_entries'))

@app.route('/export/<entity>/<format>')
@login_required
def export_data(entity, format):
    export_service = ExportService()
    year = request.args.get('year', datetime.now().year, type=int)

    if entity == 'time-entries':
        entries = TimeEntry.query.filter_by(user_id=current_user.id).order_by(TimeEntry.date.desc()).all()
        if format == 'pdf':
            data = {'entries': entries}
            # Use direct PDF generation with xhtml2pdf
            content, filename, mimetype = generate_pdf_from_template('pdf_time_entries.html', data, 'time_entries')
            # Check if PDF generation failed
            if not content:
                flash('Fout bij genereren PDF.', 'danger')
                return redirect(url_for('time_entries'))
        else:
            headers = ['Datum', 'Project', 'Uren', 'Omschrijving']
            rows = [[e.date.strftime('%Y-%m-%d'), e.project, e.hours, e.description] for e in entries]
            if format == 'excel':
                content, filename, mimetype = export_service.to_excel(rows, headers, 'time_entries')
            else:  # csv
                content, filename, mimetype = export_service.to_csv(rows, headers, 'time_entries')

    elif entity == 'employee-time-entries':
        # Check if user is admin or manager
        if not current_user.has_role(RoleEnum.ADMIN) and not current_user.has_role(RoleEnum.AFDELINGSHOOFD) and not current_user.has_role(RoleEnum.VERKOOP):
            flash('Je hebt geen toegang tot deze export.', 'danger')
            return redirect(url_for('dashboard'))
            
        # Get employee time entries for export
        entries_query = TimeEntry.query
        
        # Get selected employee filter if present
        selected_employee = request.args.get('employee_id', '')
        if selected_employee:
            # Find users with this employee ID
            user_ids = [user.id for user in User.query.filter_by(medewerker_id=int(selected_employee)).all()]
            if user_ids:
                entries_query = entries_query.filter(TimeEntry.user_id.in_(user_ids))
                
        # Get all entries
        entries = entries_query.order_by(TimeEntry.date.desc()).all()
        
        # Calculate total hours, billable hours, and non-billable hours
        total_hours = 0
        billable_hours = 0
        non_billable_hours = 0
        
        # Prepare data with employee names and assignment details
        formatted_entries = []
        
        # Create a dictionary to track hours per employee
        employee_hours_dict = {}
        
        for entry in entries:
            # Get employee name
            user = User.query.get(entry.user_id)
            employee_name = "Unknown"
            employee_id = None
            
            if user and user.medewerker_id:
                medewerker = Medewerker.query.get(user.medewerker_id)
                if medewerker:
                    employee_name = f"{medewerker.voornaam} {medewerker.tussenvoegsel + ' ' if medewerker.tussenvoegsel else ''}{medewerker.achternaam}"
                    employee_id = medewerker.id
            elif user:
                employee_name = user.username
                employee_id = f"user_{user.id}"
                
            # Get client and assignment info
            client_name = "-"
            assignment_title = "-"
            if entry.opdracht_id:
                opdracht = Opdracht.query.get(entry.opdracht_id)
                if opdracht:
                    assignment_title = opdracht.titel
                    if opdracht.klant:
                        client_name = opdracht.klant.bedrijfsnaam
            
            # Calculate hours
            hours = float(entry.hours)
            total_hours += hours
            
            # Check if entry is billable
            is_billable = entry.is_billable if hasattr(entry, 'is_billable') else False
            if is_billable:
                billable_hours += hours
            else:
                non_billable_hours += hours
                
            # Track hours per employee
            if employee_id not in employee_hours_dict:
                employee_hours_dict[employee_id] = {
                    'name': employee_name,
                    'total_hours': 0,
                    'billable_hours': 0,
                    'non_billable_hours': 0
                }
                
            employee_hours_dict[employee_id]['total_hours'] += hours
            if is_billable:
                employee_hours_dict[employee_id]['billable_hours'] += hours
            else:
                employee_hours_dict[employee_id]['non_billable_hours'] += hours
            
            # Create formatted entry
            formatted_entries.append({
                'employee_name': employee_name,
                'date': entry.date.strftime('%Y-%m-%d'),
                'client': client_name,
                'assignment': assignment_title,
                'project': entry.project,
                'hours': hours,
                'is_billable': is_billable,
                'description': entry.description
            })
        
        # Convert employee hours dictionary to list for the template
        employee_hours = list(employee_hours_dict.values())
        
        if format == 'pdf':
            data = {
                'entries': formatted_entries,
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'total_hours': total_hours,
                'billable_hours': billable_hours,
                'non_billable_hours': non_billable_hours,
                'employee_count': len(employee_hours_dict),
                'employee_hours': employee_hours
            }
            # Use direct PDF generation with xhtml2pdf
            content, filename, mimetype = generate_pdf_from_template('admin/pdf_employee_time_entries.html', data, 'employee_time_entries')
            # Check if PDF generation failed
            if not content:
                flash('Fout bij genereren PDF.', 'danger')
                return redirect(url_for('admin_employee_time_entries'))
        else:
            headers = ['Medewerker', 'Datum', 'Client', 'Opdracht', 'Project', 'Uren', 'Factureerbaar', 'Omschrijving']
            rows = [
                [e['employee_name'], e['date'], e['client'], e['assignment'], e['project'], e['hours'], "Ja" if e['is_billable'] else "Nee", e['description']] 
                for e in formatted_entries
            ]
            if format == 'excel':
                content, filename, mimetype = export_service.to_excel(rows, headers, 'employee_time_entries')
            else:  # csv
                content, filename, mimetype = export_service.to_csv(rows, headers, 'employee_time_entries')

    elif entity == 'klanten':
        klanten = Klant.query.order_by(Klant.bedrijfsnaam).all()
        if format == 'pdf':
            data = {'klanten': klanten}
            # Use direct PDF generation with xhtml2pdf
            content, filename, mimetype = generate_pdf_from_template('pdf_klanten.html', data, 'klanten')
            # Check if PDF generation failed
            if not content:
                flash('Fout bij genereren PDF.', 'danger')
                return redirect(url_for('klanten'))
        else:
            headers = ['Bedrijfsnaam', 'Naam', 'Email', 'Telefoon', 'Functie']
            rows = [[
                k.bedrijfsnaam,
                f"{k.voornaam} {k.tussenvoegsel + ' ' if k.tussenvoegsel else ''}{k.achternaam}".strip(),
                k.email,
                k.telefoonnummer or '-',
                k.functie or '-'
            ] for k in klanten]
            if format == 'excel':
                content, filename, mimetype = export_service.to_excel(rows, headers, 'klanten')
            else:  # csv
                content, filename, mimetype = export_service.to_csv(rows, headers, 'klanten')

    elif entity == 'medewerkers':
        medewerkers = Medewerker.query.order_by(Medewerker.achternaam).all()
        if format == 'pdf':
            data = {'medewerkers': medewerkers}
            # Use direct PDF generation with xhtml2pdf
            content, filename, mimetype = generate_pdf_from_template('pdf_medewerkers.html', data, 'medewerkers')
            # Check if PDF generation failed
            if not content:
                flash('Fout bij genereren PDF.', 'danger')
                return redirect(url_for('medewerkers'))
        else:
            headers = ['Naam', 'Functie', 'Werkmail', 'Kantoorruimte', 'Geboortedatum']
            rows = [[
                f"{m.voornaam} {m.tussenvoegsel + ' ' if m.tussenvoegsel else ''}{m.achternaam}".strip(),
                m.functie or '-',
                m.werkmail,
                m.kantoorruimte or '-',
                m.geboortedatum.strftime('%Y-%m-%d')
            ] for m in medewerkers]
            if format == 'excel':
                content, filename, mimetype = export_service.to_excel(rows, headers, 'medewerkers')
            else:  # csv
                content, filename, mimetype = export_service.to_csv(rows, headers, 'medewerkers')

    elif entity == 'opdrachten':
        opdrachten = Opdracht.query.order_by(Opdracht.aanvraagdatum.desc()).all()
        if format == 'pdf':
            data = {'opdrachten': opdrachten}
            # Use direct PDF generation with xhtml2pdf
            content, filename, mimetype = generate_pdf_from_template('pdf_opdrachten.html', data, 'opdrachten')
            # Check if PDF generation failed
            if not content:
                flash('Fout bij genereren PDF.', 'danger')
                return redirect(url_for('opdrachten'))
        else:
            headers = ['Datum', 'Klant', 'Titel', 'Omschrijving', 'Benodigde Kennis']
            rows = [[
                o.aanvraagdatum.strftime('%Y-%m-%d'),
                o.klant.bedrijfsnaam,
                o.titel,
                o.omschrijving,
                o.benodigde_kennis or '-'
            ] for o in opdrachten]
            if format == 'excel':
                content, filename, mimetype = export_service.to_excel(rows, headers, 'opdrachten')
            else:  # csv
                content, filename, mimetype = export_service.to_csv(rows, headers, 'opdrachten')

    # Report exports
    elif entity == 'hours':
        # Get hours by sources for the selected year
        try:
            # From Werkzaamheid
            werkzaamheid_hours = db.session.query(func.sum(Werkzaamheid.aantal_uren)) \
                .filter(func.extract('year', Werkzaamheid.datum) == year) \
                .scalar() or 0
            
            # From TimeEntry
            time_entry_hours = db.session.query(func.sum(TimeEntry.hours)) \
                .filter(func.extract('year', TimeEntry.date) == year) \
                .scalar() or 0
            
            # Calculate billable hours from Werkzaamheid
            billable_hours_werkzaamheid = db.session.query(func.sum(Werkzaamheid.aantal_uren)) \
                .filter(func.extract('year', Werkzaamheid.datum) == year) \
                .filter(Werkzaamheid.is_declarabel == True) \
                .scalar() or 0
                
            # Calculate billable hours from TimeEntry
            billable_hours_time_entry = db.session.query(func.sum(TimeEntry.hours)) \
                .filter(func.extract('year', TimeEntry.date) == year) \
                .filter(TimeEntry.is_billable == True) \
                .scalar() or 0
            
            # Calculate total billable and non-billable hours
            billable_hours = billable_hours_werkzaamheid + billable_hours_time_entry
            total_hours = time_entry_hours + werkzaamheid_hours
            non_billable_hours = total_hours - billable_hours
            
            # Get hours per month for the selected year
            monthly_hours_time_entries = db.session.query(
                extract('month', TimeEntry.date).label('month'),
                func.sum(TimeEntry.hours).label('hours')
            ).filter(
                extract('year', TimeEntry.date) == year
            ).group_by('month').all()
            
            monthly_hours_werkzaamheden = db.session.query(
                extract('month', Werkzaamheid.datum).label('month'),
                func.sum(Werkzaamheid.aantal_uren).label('hours')
            ).filter(
                extract('year', Werkzaamheid.datum) == year
            ).group_by('month').all()
            
            # Combine both sources into a single monthly view
            monthly_hours = [0] * 12  # Initialize with zeros
            
            for month, hours in monthly_hours_time_entries:
                monthly_hours[int(month)-1] += float(hours)
                
            for month, hours in monthly_hours_werkzaamheden:
                monthly_hours[int(month)-1] += float(hours)
            
            # Get hours per employee
            employee_hours = Werkzaamheid.get_uren_per_medewerker(year)
            
            if format == 'pdf':
                data = {
                    'selected_year': year,
                    'total_hours': total_hours,
                    'billable_hours': billable_hours,
                    'non_billable_hours': non_billable_hours,
                    'monthly_hours': monthly_hours,
                    'employee_hours': employee_hours,
                    'now': datetime.now()
                }
                content, filename, mimetype = generate_pdf_from_template('reports/pdf_hours_per_year.html', data, f'uren_per_jaar_{year}')
                if not content:
                    flash('Fout bij genereren PDF.', 'danger')
                    return redirect(url_for('report_hours_per_year', year=year))
            else:
                headers = ['Maand', 'Aantal Uren']
                months = ['Januari', 'Februari', 'Maart', 'April', 'Mei', 'Juni', 'Juli', 'Augustus', 'September', 'Oktober', 'November', 'December']
                rows = [[months[i], monthly_hours[i]] for i in range(12)]
                if format == 'excel':
                    content, filename, mimetype = export_service.to_excel(rows, headers, f'uren_per_jaar_{year}')
                else:  # csv
                    content, filename, mimetype = export_service.to_csv(rows, headers, f'uren_per_jaar_{year}')
        except Exception as e:
            app.logger.error(f"Error generating hours report: {str(e)}")
            flash('Fout bij genereren rapport.', 'danger')
            return redirect(url_for('report_hours_per_year', year=year))

    elif entity == 'assignments':
        try:
            # Get assignments per client for the selected year
            assignments_per_client = Opdracht.get_assignments_per_client(year)
            
            # Get total assignments for the selected year
            total_assignments = db.session.query(
                func.count(Opdracht.id)
            ).filter(
                func.extract('year', Opdracht.aanvraagdatum) == year
            ).scalar() or 0
            
            # Get assignments by status
            assignments_by_status = db.session.query(
                Opdracht.status,
                func.count(Opdracht.id).label('count')
            ).filter(
                func.extract('year', Opdracht.aanvraagdatum) == year
            ).group_by(Opdracht.status).all()
            
            # Get assignments per month for the selected year
            monthly_assignments = db.session.query(
                func.extract('month', Opdracht.aanvraagdatum).label('month'),
                func.count(Opdracht.id).label('count')
            ).filter(
                func.extract('year', Opdracht.aanvraagdatum) == year
            ).group_by('month').all()
            
            # Format for chart display
            months_data = [0] * 12  # Initialize with zeros
            for month, count in monthly_assignments:
                if month is not None:
                    months_data[int(month)-1] = int(count)
            
            if format == 'pdf':
                data = {
                    'selected_year': year,
                    'total_assignments': total_assignments,
                    'assignments_per_client': assignments_per_client,
                    'assignments_by_status': assignments_by_status,
                    'monthly_assignments': months_data
                }
                content, filename, mimetype = generate_pdf_from_template('reports/pdf_assignments_per_client.html', data, f'opdrachten_per_klant_{year}')
                if not content:
                    flash('Fout bij genereren PDF.', 'danger')
                    return redirect(url_for('report_assignments_per_client', year=year))
            else:
                headers = ['Klant', 'Aantal Opdrachten', 'Open', 'In Uitvoering', 'Afgerond', 'Gemiddeld Uurtarief']
                rows = [
                    [
                        client.bedrijfsnaam,
                        client.assignment_count,
                        client.open_count,
                        client.in_progress_count,
                        client.completed_count,
                        client.average_hourly_rate
                    ] for client in assignments_per_client
                ]
                if format == 'excel':
                    content, filename, mimetype = export_service.to_excel(rows, headers, f'opdrachten_per_klant_{year}')
                else:  # csv
                    content, filename, mimetype = export_service.to_csv(rows, headers, f'opdrachten_per_klant_{year}')
        except Exception as e:
            app.logger.error(f"Error generating assignments report: {str(e)}")
            flash('Fout bij genereren rapport.', 'danger')
            return redirect(url_for('report_assignments_per_client', year=year))

    elif entity == 'revenue':
        try:
            # Get total revenue for the selected year
            total_revenue = Factuur.get_jaaropbrengst(year)
            
            # Get monthly revenue for the selected year
            monthly_revenue = db.session.query(
                func.strftime('%m', Factuur.datum).label('month'),
                func.sum(Factuur.totaal).label('revenue')
            ).filter(
                func.strftime('%Y', Factuur.datum) == str(year),
                Factuur.betaald == True
            ).group_by('month').all()
            
            # Format for chart display
            months_data = [0] * 12  # Initialize with zeros
            for month, revenue in monthly_revenue:
                months_data[int(month)-1] = float(revenue)
            
            # Simplified query for revenue per client
            revenue_per_client = db.session.query(
                Klant.bedrijfsnaam.label('klant_naam'),
                func.count(Factuur.id).label('aantal_werkzaamheden'),
                func.coalesce(func.sum(Werkzaamheid.aantal_uren), 0.0).label('totaal_uren'),
                func.sum(Factuur.totaal).label('totaal_opbrengst')
            ).join(
                Factuur, Factuur.klant_id == Klant.id
            ).outerjoin(
                Werkzaamheid, Werkzaamheid.factuur_id == Factuur.id
            ).filter(
                func.strftime('%Y', Factuur.datum) == str(year),
                Factuur.betaald == True
            ).group_by(Klant.bedrijfsnaam).all()
            
            if format == 'pdf':
                data = {
                    'selected_year': year,
                    'total_revenue': total_revenue,
                    'monthly_revenue': months_data,
                    'revenue_per_client': revenue_per_client
                }
                content, filename, mimetype = generate_pdf_from_template('reports/pdf_annual_revenue.html', data, f'jaaropbrengst_{year}')
                if not content:
                    flash('Fout bij genereren PDF.', 'danger')
                    return redirect(url_for('report_annual_revenue', year=year))
            else:
                headers = ['Klant', 'Aantal Werkzaamheden', 'Totaal Uren', 'Totaal Opbrengst', 'Percentage']
                rows = []
                for client in revenue_per_client:
                    percentage = (client.totaal_opbrengst / total_revenue * 100) if total_revenue > 0 else 0
                    rows.append([
                        client.klant_naam,
                        client.aantal_werkzaamheden,
                        client.totaal_uren,
                        client.totaal_opbrengst,
                        f"{percentage:.1f}%"
                    ])
                if format == 'excel':
                    content, filename, mimetype = export_service.to_excel(rows, headers, f'jaaropbrengst_{year}')
                else:  # csv
                    content, filename, mimetype = export_service.to_csv(rows, headers, f'jaaropbrengst_{year}')
        except Exception as e:
            app.logger.error(f"Error generating revenue report: {str(e)}")
            flash('Fout bij genereren rapport.', 'danger')
            return redirect(url_for('report_annual_revenue', year=year))
    else:
        flash('Onbekend exporttype.', 'danger')
        return redirect(url_for('dashboard'))

    return send_file(
        io.BytesIO(content),
        mimetype=mimetype,
        as_attachment=True,
        download_name=filename
    )

@app.route('/api/time-entries')
@login_required
def api_get_time_entries():
    # Get the user's time entries for the API
    entries = TimeEntry.query.filter_by(user_id=current_user.id)\
        .order_by(TimeEntry.date.desc())\
        .limit(100)\
        .all()
    
    # Convert to JSON serializable format
    results = []
    for entry in entries:
        results.append({
            'id': entry.id,
            'date': entry.date.strftime('%Y-%m-%d'),
            'hours': entry.hours,
            'description': entry.description,
            'project': entry.project
        })
    
    return jsonify(results)

@app.route('/api/dashboard_stats')
@login_required
def dashboard_stats():
    try:
        # Get current month and year
        now = datetime.now()
        current_month = now.month
        current_year = now.year
        
        # Get total hours for current month
        month_entries = TimeEntry.query.filter(
            TimeEntry.user_id == current_user.id,
            extract('month', TimeEntry.date) == current_month,
            extract('year', TimeEntry.date) == current_year
        ).all()
        
        total_hours_month = sum(entry.hours for entry in month_entries)
        
        # Get check-ins for today
        today = now.date()
        checkins_today = CheckIn.query.filter(
            CheckIn.user_id == current_user.id,
            func.date(CheckIn.check_in_time) == today
        ).count()
        
        # Get total projects worked on this month
        projects_this_month = set(entry.project for entry in month_entries)
        
        # Return stats as JSON
        stats = {
            'total_hours_month': total_hours_month,
            'checkins_today': checkins_today,
            'projects_count': len(projects_this_month),
            'last_updated': now.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(stats)
        
    except Exception as e:
        app.logger.error(f"Error generating dashboard stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/projects', methods=['GET'])
def api_get_projects():
    if not request.headers.get('X-API-Key') == app.config.get('API_KEY'):
        return jsonify({"error": "Unauthorized"}), 401

    projects = db.session.query(TimeEntry.project).distinct().all()
    return jsonify([project[0] for project in projects])

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Klanten routes
@app.route('/klanten/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_klant(id):
    klant = Klant.query.get_or_404(id)
    if request.method == 'POST':
        klant.bedrijfsnaam = request.form['bedrijfsnaam']
        klant.voornaam = request.form['voornaam']
        klant.tussenvoegsel = request.form.get('tussenvoegsel')
        klant.achternaam = request.form['achternaam']
        klant.functie = request.form.get('functie')
        klant.email = request.form['email']
        klant.telefoonnummer = request.form.get('telefoonnummer')
        klant.adres = request.form.get('adres')
        
        try:
            db.session.commit()
            flash('Klant succesvol bijgewerkt')
            return redirect(url_for('klanten'))
        except Exception as e:
            db.session.rollback()
            flash('Error bij bijwerken klant')
            app.logger.error(f"Error updating klant: {str(e)}")
            
    return render_template('edit_klant.html', klant=klant)

@app.route('/klanten/<int:id>/delete')
@login_required
def delete_klant(id):
    klant = Klant.query.get_or_404(id)
    try:
        db.session.delete(klant)
        db.session.commit()
        flash('Klant succesvol verwijderd')
    except Exception as e:
        db.session.rollback()
        flash('Error bij verwijderen klant')
        app.logger.error(f"Error deleting klant: {str(e)}")
    return redirect(url_for('klanten'))

@app.route('/opdrachten/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_opdracht(id):
    opdracht = Opdracht.query.get_or_404(id)
    if request.method == 'POST':
        opdracht.klant_id = request.form['klant_id']
        opdracht.titel = request.form['titel']
        opdracht.omschrijving = request.form['omschrijving']
        opdracht.aanvraagdatum = datetime.strptime(request.form['aanvraagdatum'], '%Y-%m-%d')
        opdracht.benodigde_kennis = request.form.get('benodigde_kennis')
        
        try:
            db.session.commit()
            flash('Opdracht succesvol bijgewerkt')
            return redirect(url_for('opdrachten'))
        except Exception as e:
            db.session.rollback()
            flash('Error bij bijwerken opdracht')
            app.logger.error(f"Error updating opdracht: {str(e)}")
            
    klanten = Klant.query.order_by(Klant.bedrijfsnaam).all()
    return render_template('edit_opdracht.html', opdracht=opdracht, klanten=klanten)

@app.route('/opdrachten/<int:id>/delete')
@login_required
def delete_opdracht(id):
    opdracht = Opdracht.query.get_or_404(id)
    try:
        # Eerst verwijder alle gekoppelde werkzaamheden
        Werkzaamheid.query.filter_by(opdracht_id=id).delete()
        # Dan de opdracht zelf
        db.session.delete(opdracht)
        db.session.commit()
        flash('Opdracht succesvol verwijderd')
    except Exception as e:
        db.session.rollback()
        flash('Error bij verwijderen opdracht')
        app.logger.error(f"Error deleting opdracht: {str(e)}")
    return redirect(url_for('opdrachten'))

@app.route('/klanten')
@login_required
def klanten():
    search = request.args.get('search', '')
    query = Klant.query
    if search:
        query = query.filter(
            db.or_(
                Klant.bedrijfsnaam.ilike(f'%{search}%'),
                Klant.email.ilike(f'%{search}%'),
                Klant.achternaam.ilike(f'%{search}%')
            )
        )
    klanten = query.order_by(Klant.bedrijfsnaam).all()
    return render_template('klanten.html', klanten=klanten, search=search)


@app.route('/klanten/add', methods=['GET', 'POST'])
@login_required
def add_klant():
    if request.method == 'POST':
        klant = Klant(
            bedrijfsnaam=request.form['bedrijfsnaam'],
            voornaam=request.form['voornaam'],
            tussenvoegsel=request.form.get('tussenvoegsel'),
            achternaam=request.form['achternaam'],
            functie=request.form.get('functie'),
            email=request.form['email'],
            telefoonnummer=request.form.get('telefoonnummer'),
            adres=request.form.get('adres')
        )
        db.session.add(klant)
        try:
            db.session.commit()
            flash('Klant succesvol toegevoegd')
            return redirect(url_for('klanten'))
        except Exception as e:
            db.session.rollback()
            flash('Error bij toevoegen klant: mogelijk bestaat deze email al')
            app.logger.error(f"Error adding klant: {str(e)}")

    return render_template('add_klant.html')

@app.route('/medewerkers')
@login_required
def medewerkers():
    search = request.args.get('search', '')
    query = Medewerker.query
    if search:
        query = query.filter(
            db.or_(
                Medewerker.voornaam.ilike(f'%{search}%'),
                Medewerker.werkmail.ilike(f'%{search}%'),
                Medewerker.achternaam.ilike(f'%{search}%')
            )
        )
    medewerkers = query.order_by(Medewerker.achternaam).all()
    return render_template('medewerkers.html', medewerkers=medewerkers, search=search)

@app.route('/medewerkers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_medewerker(id):
    medewerker = Medewerker.query.get_or_404(id)
    if request.method == 'POST':
        medewerker.voornaam = request.form['voornaam']
        medewerker.tussenvoegsel = request.form.get('tussenvoegsel')
        medewerker.achternaam = request.form['achternaam']
        medewerker.geboortedatum = datetime.strptime(request.form['geboortedatum'], '%Y-%m-%d')
        medewerker.functie = request.form.get('functie')
        medewerker.werkmail = request.form['werkmail']
        medewerker.kantoorruimte = request.form.get('kantoorruimte')
        
        try:
            db.session.commit()
            flash('Medewerker succesvol bijgewerkt')
            return redirect(url_for('medewerkers'))
        except Exception as e:
            db.session.rollback()
            flash('Error bij bijwerken medewerker')
            app.logger.error(f"Error updating medewerker: {str(e)}")
            
    return render_template('edit_medewerker.html', medewerker=medewerker)

@app.route('/medewerkers/<int:id>/delete')
@login_required
def delete_medewerker(id):
    medewerker = Medewerker.query.get_or_404(id)
    medewerker_name = f"{medewerker.voornaam} {medewerker.achternaam}"
    
    try:
        app.logger.info(f"Starting deletion process for employee ID {id}: {medewerker_name}")
        
        # Check if there are User accounts linked to this employee
        linked_users = User.query.filter_by(medewerker_id=id).all()
        
        if linked_users:
            user_info = [f"{user.username} (ID: {user.id})" for user in linked_users]
            app.logger.info(f"Found {len(linked_users)} linked user accounts: {', '.join(user_info)}")
            
            # Remove the reference to this employee from user accounts
            for user in linked_users:
                user.medewerker_id = None
                app.logger.info(f"Removed medewerker reference from user {user.id} ({user.username})")
            
            db.session.flush()  # Flush changes to ensure references are updated
            
        # Delete related check-ins
        try:
            check_in_count = CheckIn.query.filter(CheckIn.user_id.in_([user.id for user in linked_users])).count() if linked_users else 0
            if check_in_count > 0:
                app.logger.info(f"Deleting {check_in_count} related check-ins")
                CheckIn.query.filter(CheckIn.user_id.in_([user.id for user in linked_users])).delete(synchronize_session=False)
        except Exception as ce:
            app.logger.warning(f"Non-critical error while handling check-ins: {str(ce)}")
        
        # Delete related time entries
        try:
            time_entry_count = TimeEntry.query.filter(TimeEntry.user_id.in_([user.id for user in linked_users])).count() if linked_users else 0
            if time_entry_count > 0:
                app.logger.info(f"Deleting {time_entry_count} related time entries")
                TimeEntry.query.filter(TimeEntry.user_id.in_([user.id for user in linked_users])).delete(synchronize_session=False)
        except Exception as te:
            app.logger.warning(f"Non-critical error while handling time entries: {str(te)}")
            
        # Delete all associated werkzaamheden
        try:
            werkzaamheid_count = Werkzaamheid.query.filter_by(medewerker_id=id).count()
            if werkzaamheid_count > 0:
                app.logger.info(f"Deleting {werkzaamheid_count} related werkzaamheden")
                Werkzaamheid.query.filter_by(medewerker_id=id).delete(synchronize_session=False)
        except Exception as we:
            app.logger.warning(f"Non-critical error while handling werkzaamheden: {str(we)}")
        
        # Then delete the employee record
        db.session.delete(medewerker)
        db.session.commit()
        
        app.logger.info(f"Successfully deleted employee {medewerker_name} (ID: {id})")
        flash(f'Medewerker {medewerker_name} is succesvol verwijderd', 'success')
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Failed to delete employee {medewerker_name} (ID: {id}): {str(e)}", exc_info=True)
        
        # Provide more helpful error message based on error type
        if "foreign key constraint fails" in str(e).lower():
            flash(f'Kan medewerker {medewerker_name} niet verwijderen omdat er nog gerelateerde gegevens aanwezig zijn. Probeer eerst alle urenregistraties te verwijderen.', 'danger')
        else:
            flash(f'Fout bij verwijderen medewerker: {str(e)}', 'danger')
    
    return redirect(url_for('medewerkers'))

@app.route('/medewerkers/add', methods=['GET', 'POST'])
@login_required
def add_medewerker():
    if request.method == 'POST':
        medewerker = Medewerker(
            voornaam=request.form['voornaam'],
            tussenvoegsel=request.form.get('tussenvoegsel'),
            achternaam=request.form['achternaam'],
            geboortedatum=datetime.strptime(request.form['geboortedatum'], '%Y-%m-%d'),
            functie=request.form.get('functie'),
            werkmail=request.form['werkmail'],
            kantoorruimte=request.form.get('kantoorruimte')
        )
        db.session.add(medewerker)
        try:
            db.session.commit()
            flash('Medewerker succesvol toegevoegd')
            return redirect(url_for('medewerkers'))
        except Exception as e:
            db.session.rollback()
            flash('Error bij toevoegen medewerker: mogelijk bestaat deze werkmail al')
            app.logger.error(f"Error adding medewerker: {str(e)}")

    return render_template('add_medewerker.html')

@app.route('/opdrachten')
@login_required
def opdrachten():
    search = request.args.get('search', '')
    query = Opdracht.query
    if search:
        query = query.filter(
            db.or_(
                Opdracht.titel.ilike(f'%{search}%'),
                Opdracht.omschrijving.ilike(f'%{search}%')
            )
        )
    opdrachten = query.order_by(Opdracht.aanvraagdatum.desc()).all()
    return render_template('opdrachten.html', opdrachten=opdrachten, search=search)

@app.route('/opdrachten/add', methods=['GET', 'POST'])
@login_required
def add_opdracht():
    if request.method == 'POST':
        opdracht = Opdracht(
            klant_id=request.form['klant_id'],
            titel=request.form['titel'],
            omschrijving=request.form['omschrijving'],
            aanvraagdatum=datetime.strptime(request.form['aanvraagdatum'], '%Y-%m-%d'),
            benodigde_kennis=request.form.get('benodigde_kennis')
        )
        db.session.add(opdracht)
        try:
            db.session.commit()
            flash('Opdracht succesvol toegevoegd')
            return redirect(url_for('opdrachten'))
        except Exception as e:
            db.session.rollback()
            flash('Error bij toevoegen opdracht')
            app.logger.error(f"Error adding opdracht: {str(e)}")

    klanten = Klant.query.order_by(Klant.bedrijfsnaam).all()
    return render_template('add_opdracht.html', klanten=klanten)

@app.route('/check-in', methods=['POST'])
@login_required
def check_in():
    """Record a check-in for the current user"""
    if request.method == 'POST':
        status = request.form.get('status')
        note = request.form.get('note', '')
        opdracht_id = request.form.get('opdracht_id') 
        
        if not status:
            flash('Status is required!', 'error')
            return redirect(url_for('dashboard'))
        
        # Use local time
        local_now = datetime.now()
        
        # Create the check-in
        check_in = CheckIn(
            user_id=current_user.id,
            status=status,
            note=note,
            check_in_time=local_now  # Explicitly setting local time
        )
        
        # Link to assignment if provided
        if opdracht_id:
            try:
                check_in.opdracht_id = int(opdracht_id)
            except ValueError:
                # Invalid assignment ID, just ignore it
                pass
                
        db.session.add(check_in)
        db.session.commit()
        app.logger.info(f"Check-in created for user {current_user.id} at {check_in.check_in_time} with status {check_in.status}")
        
        flash('Check-in recorded!', 'success')
        return redirect(url_for('dashboard'))
        
    return redirect(url_for('dashboard'))

@app.route('/check-in/<int:checkin_id>/delete')
@login_required
def delete_check_in(checkin_id):
    """Delete a check-in record with proper error handling and logging"""
    try:
        app.logger.debug(f"Starting delete process for check-in {checkin_id}")
        check_in = CheckIn.query.get_or_404(checkin_id)
        
        # Verify ownership
        if check_in.user_id != current_user.id:
            app.logger.warning(f"Unauthorized delete attempt for check-in {checkin_id} by user {current_user.id}")
            flash('Niet toegestaan. Dit is niet jouw check-in.', 'danger')
            return redirect(url_for('dashboard'))

        # Capture info for logging before deletion
        user_id = check_in.user_id
        timestamp = check_in.check_in_time
        status = check_in.status
        
        # Delete the check-in
        db.session.delete(check_in)
        db.session.commit()
        
        app.logger.info(f"Successfully deleted check-in {checkin_id} (user: {user_id}, time: {timestamp}, status: {status})")
        flash('Check-in is verwijderd', 'success')
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting check-in {checkin_id}: {str(e)}", exc_info=True)
        flash(f'Fout bij het verwijderen van de check-in: {str(e)}', 'danger')
    
    # Always return to dashboard after processing
    return redirect(url_for('dashboard'))

@app.route('/check-in/<int:checkin_id>/edit', methods=['POST'])
@login_required
def edit_check_in(checkin_id):
    """Edit an existing check-in"""
    check_in = CheckIn.query.get_or_404(checkin_id)
    if check_in.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Validate values
        status = request.form.get('status')
        if not status:
            flash('Status is required!', 'error')
            return redirect(url_for('dashboard'))
        
        # Update the basic fields
        check_in.status = request.form['status']
        check_in.note = request.form.get('note', '')
        
        # Update assignment
        opdracht_id = request.form.get('opdracht_id')
        if opdracht_id:
            try:
                check_in.opdracht_id = int(opdracht_id)
            except ValueError:
                # Invalid assignment ID, just ignore it
                pass
        else:
            check_in.opdracht_id = None
            
        # Handle time updates
        if 'check_in_time' in request.form and request.form['check_in_time']:
            try:
                # Get current date from the check-in time (preserve the date)
                current_date = check_in.check_in_time.date()
                
                # Get the new time from the form
                time_str = request.form['check_in_time']
                time_parts = time_str.split(':')
                
                if len(time_parts) != 2:
                    raise ValueError("Invalid time format. Expected HH:MM.")
                
                hours = int(time_parts[0])
                minutes = int(time_parts[1])
                
                # Create a new datetime with the current date and new time
                new_datetime = datetime.combine(current_date, time(hours, minutes))
                
                # Update the check-in time
                check_in.check_in_time = new_datetime
            except Exception as e:
                flash(f'Invalid time format: {str(e)}', 'danger')
                return redirect(url_for('dashboard'))
                
        db.session.commit()
        app.logger.debug(f"Updating check-in {checkin_id}: status={check_in.status}, note={check_in.note}, time={check_in.check_in_time}")
        
        flash('Check-in updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating check-in: {str(e)}', 'danger')
        
    return redirect(url_for('dashboard'))

@app.route('/pdf-export-guide')
def pdf_export_guide():
    """Serve the PDF export guide page to help users set up wkhtmltopdf"""
    return app.send_static_file('pdf_export_guide.html')

@app.route('/import_time_entries', methods=['POST'])
@login_required
def import_time_entries():
    if 'import_file' not in request.files:
        flash('No file uploaded', 'danger')
        return redirect(url_for('time_entries'))
    
    file = request.files['import_file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('time_entries'))
    
    # Check file extension
    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1].lower()
    
    entries_added = 0
    entries_failed = 0
    
    try:
        # Process CSV file
        if file_ext == '.csv':
            # Convert CSV to DataFrame
            df = pd.read_csv(file)
            
        # Process Excel file
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file)
        else:
            flash('Unsupported file format. Please upload a CSV or Excel file.', 'danger')
            return redirect(url_for('time_entries'))
        
        # Normalize column names (remove spaces, case-insensitive)
        df.columns = [col.lower().strip() for col in df.columns]
        
        # Check for required columns (case insensitive)
        required_columns = ['date', 'project', 'hours', 'description']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            flash(f"Missing required columns: {', '.join(missing_columns)}", 'danger')
            return redirect(url_for('time_entries'))
        
        # Process each row and add to database
        for _, row in df.iterrows():
            try:
                # Parse the date - support multiple formats
                try:
                    # Try to parse as YYYY-MM-DD first
                    date_val = datetime.strptime(str(row['date']), '%Y-%m-%d').date()
                except ValueError:
                    try:
                        # Try DD-MM-YYYY format
                        date_val = datetime.strptime(str(row['date']), '%d-%m-%Y').date()
                    except ValueError:
                        # Try MM/DD/YYYY format
                        date_val = datetime.strptime(str(row['date']), '%m/%d/%Y').date()
                
                hours = float(row['hours'])
                project = str(row['project'])
                description = str(row['description'])
                
                # Create new time entry
                entry = TimeEntry(
                    date=date_val,
                    hours=hours,
                    project=project,
                    description=description,
                    user_id=current_user.id
                )
                
                db.session.add(entry)
                entries_added += 1
                
            except Exception as e:
                app.logger.error(f"Error importing row: {e}")
                entries_failed += 1
                continue
        
        # Commit all successful entries
        db.session.commit()
        
        if entries_failed > 0:
            flash(f'Import completed: {entries_added} entries added, {entries_failed} entries failed.', 'warning')
        else:
            flash(f'Successfully imported {entries_added} time entries.', 'success')
            
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error importing file: {e}")
        flash(f'Error importing file: {str(e)}', 'danger')
    
    # Redirect back to dashboard if requested
    if request.form.get('redirect_to_dashboard') == 'true':
        return redirect(url_for('dashboard'))
        
    return redirect(url_for('time_entries'))

# Admin routes
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    roles = Role.query.all()
    return render_template('admin/users.html', users=users, roles=roles)

@app.route('/admin/users/<int:user_id>/set_role', methods=['POST'])
@login_required
@admin_required
def admin_set_user_role(user_id):
    user = User.query.get_or_404(user_id)
    
    # Don't allow admins to downgrade themselves
    if user.id == current_user.id and user.has_role(RoleEnum.ADMIN):
        flash('Je kunt je eigen admin rol niet wijzigen.', 'danger')
        return redirect(url_for('admin_users'))
    
    role_id = request.form.get('role_id')
    if not role_id:
        flash('Geen rol geselecteerd', 'danger')
        return redirect(url_for('admin_users'))
    
    role = Role.query.get(role_id)
    if not role:
        flash('Ongeldige rol geselecteerd', 'danger')
        return redirect(url_for('admin_users'))
    
    user.role_id = role.id
    db.session.commit()
    
    flash(f'Gebruiker {user.username} heeft de rol: {role.name} toegewezen gekregen', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/get_roles_json')
@login_required
@admin_required
def get_roles_json():
    """Return all available roles in JSON format"""
    roles = Role.query.all()
    roles_data = [{'id': role.id, 'name': f"{role.name} - {role.description}" if role.description else role.name} for role in roles]
    return jsonify({'roles': roles_data})

@app.route('/admin/employee-time-entries', methods=['GET', 'POST'])
@login_required
def admin_employee_time_entries():
    # Check if user is admin or afdelingshoofd or verkoop
    if not current_user.has_role(RoleEnum.ADMIN) and not current_user.has_role(RoleEnum.AFDELINGSHOOFD) and not current_user.has_role(RoleEnum.VERKOOP):
        flash('Je hebt geen toegang tot deze pagina.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get all employees for the dropdown
    medewerkers = Medewerker.query.order_by(Medewerker.achternaam).all()
    users = User.query.join(Role).filter(Role.name != RoleEnum.ADMIN).all()
    
    # Get all clients and assignments for the dropdowns
    clients = Klant.query.order_by(Klant.bedrijfsnaam).all()
    opdrachten = Opdracht.query.all()
    
    # Load all user and employee IDs for mapping
    user_medewerker_map = {}
    for user in users:
        if user.medewerker_id:
            user_medewerker_map[user.medewerker_id] = user.id
    
    # Handle form submission for adding new entry
    if request.method == 'POST':
        try:
            # Get the user_id or find one based on medewerker_id
            user_id = request.form.get('user_id')
            medewerker_id = request.form.get('medewerker_id')
            
            # If user_id is not provided, try to get it from medewerker_id
            if not user_id and medewerker_id:
                user_id = user_medewerker_map.get(int(medewerker_id))
                
                # If there's no user account for this employee, use the current user's ID
                # and add a note about who it was registered for
                if not user_id:
                    user_id = current_user.id
                    description_prefix = f"[Geregistreerd voor medewerker #{medewerker_id}] "
                    description = description_prefix + request.form['description']
                else:
                    description = request.form['description']
            else:
                user_id = int(user_id)
                description = request.form['description']
                
            # Get the opdracht_id (assignment) if provided
            opdracht_id = request.form.get('opdracht_id')
            if opdracht_id and opdracht_id.strip():
                opdracht_id = int(opdracht_id)
            else:
                opdracht_id = None
                
            # Create the time entry
            entry = TimeEntry(
                date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
                hours=float(request.form['hours']),
                description=description,
                project=request.form['project'],
                user_id=user_id,
                opdracht_id=opdracht_id  # Add the assignment link
            )
            db.session.add(entry)
            db.session.commit()
            
            flash('Time entry toegevoegd voor medewerker', 'success')
            return redirect(url_for('admin_employee_time_entries'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error bij toevoegen time entry: {str(e)}', 'danger')
            app.logger.error(f"Error adding time entry: {str(e)}")
    
    # Get all entries for display - or filter if an employee is selected
    selected_employee = request.args.get('employee_id', '')
    selected_assignment = request.args.get('assignment_id', '')
    
    entries_query = TimeEntry.query
    
    # Apply employee filter if specified
    if selected_employee:
        # Filter by user_id where medewerker_id matches
        user_ids = [user.id for user in users if user.medewerker_id == int(selected_employee)]
        if user_ids:
            entries_query = entries_query.filter(TimeEntry.user_id.in_(user_ids))
    
    # Apply assignment filter if specified
    if selected_assignment:
        entries_query = entries_query.filter(TimeEntry.opdracht_id == int(selected_assignment))
    
    # Join with Opdracht to get assignment and client details
    entries = entries_query.outerjoin(Opdracht, TimeEntry.opdracht_id == Opdracht.id)\
                          .outerjoin(Klant, Opdracht.klant_id == Klant.id)\
                          .order_by(TimeEntry.date.desc())\
                          .all()
    
    # Associate entries with employee names
    entries_with_employee = []
    for entry in entries:
        user = User.query.get(entry.user_id)
        employee_name = "Unknown"
        if user and user.medewerker_id:
            medewerker = Medewerker.query.get(user.medewerker_id)
            if medewerker:
                employee_name = f"{medewerker.voornaam} {medewerker.tussenvoegsel + ' ' if medewerker.tussenvoegsel else ''}{medewerker.achternaam}"
        elif user:
            employee_name = user.username
        
        entries_with_employee.append({
            'entry': entry,
            'employee_name': employee_name
        })
    
    return render_template('admin/employee_time_entries.html', 
                           entries=entries_with_employee, 
                           medewerkers=medewerkers,
                           users=users,
                           clients=clients,  # Pass clients to template
                           opdrachten=opdrachten,  # Pass assignments to template
                           selected_employee=selected_employee,
                           selected_assignment=selected_assignment,
                           datetime=datetime)

# Add route to edit employee time entries
@app.route('/admin/employee-time-entries/<int:entry_id>/edit', methods=['POST'])
@login_required
def admin_edit_employee_time_entry(entry_id):
    # Check if user is admin or afdelingshoofd or verkoop
    if not current_user.has_role(RoleEnum.ADMIN) and not current_user.has_role(RoleEnum.AFDELINGSHOOFD) and not current_user.has_role(RoleEnum.VERKOOP):
        flash('Je hebt geen toegang tot deze pagina.', 'danger')
        return redirect(url_for('dashboard'))
    
    entry = TimeEntry.query.get_or_404(entry_id)
    
    try:
        entry.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        entry.hours = float(request.form['hours'])
        entry.description = request.form['description']
        entry.project = request.form['project']
        
        # Only admin and department heads can change the user assignment
        if (current_user.has_role(RoleEnum.ADMIN) or current_user.has_role(RoleEnum.AFDELINGSHOOFD)) and 'user_id' in request.form:
            entry.user_id = int(request.form['user_id'])
        
        # Handle the assignment link
        opdracht_id = request.form.get('opdracht_id')
        if opdracht_id and opdracht_id.strip():
            entry.opdracht_id = int(opdracht_id)
        else:
            entry.opdracht_id = None
        
        db.session.commit()
        flash('Time entry bijgewerkt', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error bij bijwerken time entry: {str(e)}', 'danger')
        app.logger.error(f"Error updating time entry: {str(e)}")
    
    return redirect(url_for('admin_employee_time_entries'))

# Add route to delete employee time entries
@app.route('/admin/employee-time-entries/<int:entry_id>/delete')
@login_required
def admin_delete_employee_time_entry(entry_id):
    # Check if user is admin or afdelingshoofd (only these roles can delete)
    if not current_user.has_role(RoleEnum.ADMIN) and not current_user.has_role(RoleEnum.AFDELINGSHOOFD):
        flash('Je hebt geen toegang tot deze functie.', 'danger')
        return redirect(url_for('admin_employee_time_entries'))
    
    entry = TimeEntry.query.get_or_404(entry_id)
    
    try:
        db.session.delete(entry)
        db.session.commit()
        flash('Time entry verwijderd', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error bij verwijderen time entry: {str(e)}', 'danger')
        app.logger.error(f"Error deleting time entry: {str(e)}")
    
    return redirect(url_for('admin_employee_time_entries'))