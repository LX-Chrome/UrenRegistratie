import json
from datetime import datetime
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
    # Get the most recent time entries for the user
    entries = TimeEntry.query.filter_by(user_id=current_user.id).order_by(TimeEntry.date.desc()).limit(5).all()
    
    # Get today's date for proper comparison
    today = datetime.utcnow().date()
    
    # Use date comparison for check-ins (using imported func for SQL date extraction)
    check_ins = CheckIn.query.filter_by(user_id=current_user.id).filter(
        func.date(CheckIn.check_in_time) == today
    ).order_by(CheckIn.check_in_time.desc()).limit(5).all()
    
    # Log check-ins for debugging
    app.logger.debug(f"Retrieved {len(check_ins)} check-ins for user {current_user.id}")
    for check_in in check_ins:
        app.logger.debug(f"Check-in ID: {check_in.id}, Time: {check_in.check_in_time}, Status: {check_in.status}")

    return render_template('dashboard.html', entries=entries, check_ins=check_ins)

@app.route('/time-entries', methods=['GET', 'POST'])
@login_required
def time_entries():
    if request.method == 'POST':
        try:
            # Get date from form and handle as local date (not UTC)
            local_date = datetime.strptime(request.form['date'], '%Y-%m-%d')
            # Store the date as is - no UTC conversion needed for dates
            # This keeps the date the user selected locally
            entry = TimeEntry(
                date=local_date,
                hours=float(request.form['hours']),
                description=request.form['description'],
                project=request.form['project'],
                user_id=current_user.id
            )
            db.session.add(entry)
            db.session.commit()
            flash('Time entry added successfully', 'success')
            app.logger.info(f"Added time entry for user {current_user.id}: date={local_date}, hours={request.form['hours']}")
            
            # Redirect to dashboard to see the entry in the recent list
            if request.form.get('redirect_to_dashboard') == 'true':
                return redirect(url_for('dashboard'))
            return redirect(url_for('time_entries'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding time entry: {str(e)}', 'danger')
            app.logger.error(f"Error adding time entry: {str(e)}")
            app.logger.error(f"Form data: date={request.form.get('date')}, hours={request.form.get('hours')}, project={request.form.get('project')}")

    search = request.args.get('search', '')
    entries_query = TimeEntry.query.filter_by(user_id=current_user.id)
    if search:
        entries_query = entries_query.filter(TimeEntry.description.contains(search) | 
                                  TimeEntry.project.contains(search))
    entries = entries_query.order_by(TimeEntry.date.desc()).all()
    
    # Debug logging
    app.logger.debug(f"Found {len(entries)} time entries for user {current_user.id}")
    
    # Check if user came from dashboard
    from_dashboard = request.args.get('from_dashboard') == 'true'
    
    # Check if we need to edit a specific entry
    edit_entry_id = request.args.get('edit')
    show_edit_modal = None
    if edit_entry_id:
        try:
            show_edit_modal = int(edit_entry_id)
        except ValueError:
            pass
    
    return render_template('time_entries.html', entries=entries, search=search, 
                          from_dashboard=from_dashboard, datetime=datetime,
                          show_edit_modal=show_edit_modal)

@app.route('/time-entries/<int:entry_id>/edit', methods=['POST'])
@login_required
def edit_time_entry(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('time_entries'))

    try:
        # Get the local date from the form without UTC conversion
        local_date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        entry.date = local_date
        entry.hours = float(request.form['hours'])
        entry.description = request.form['description']
        entry.project = request.form['project']
        db.session.commit()
        flash('Time entry updated successfully', 'success')
        app.logger.info(f"Updated time entry {entry_id} for user {current_user.id}: date={local_date}, hours={request.form['hours']}")
    except Exception as e:
        db.session.rollback()
        flash('Error updating time entry: ' + str(e), 'danger')
        app.logger.error(f"Error updating time entry: {str(e)}")
        app.logger.error(f"Form data: date={request.form.get('date')}, hours={request.form.get('hours')}, project={request.form.get('project')}")

    # Redirect to dashboard if requested
    if request.form.get('redirect_to_dashboard') == 'true':
        return redirect(url_for('dashboard'))
    
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
            
            total_hours = time_entry_hours + werkzaamheid_hours
            
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
                    'monthly_hours': monthly_hours,
                    'employee_hours': employee_hours
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

@app.route('/api/time-entries', methods=['GET'])
def api_get_time_entries():
    if not request.headers.get('X-API-Key') == app.config.get('API_KEY'):
        return jsonify({"error": "Unauthorized"}), 401

    entries = TimeEntry.query.order_by(TimeEntry.date.desc()).all()
    return jsonify([{
        'id': entry.id,
        'date': entry.date.strftime('%Y-%m-%d'),
        'hours': entry.hours,
        'description': entry.description,
        'project': entry.project,
        'user_id': entry.user_id,
        'created_at': entry.created_at.strftime('%Y-%m-%d %H:%M:%S')
    } for entry in entries])

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
    try:
        # Eerst verwijder alle gekoppelde werkzaamheden
        Werkzaamheid.query.filter_by(medewerker_id=id).delete()
        # Dan de medewerker zelf
        db.session.delete(medewerker)
        db.session.commit()
        flash('Medewerker succesvol verwijderd')
    except Exception as e:
        db.session.rollback()
        flash('Error bij verwijderen medewerker')
        app.logger.error(f"Error deleting medewerker: {str(e)}")
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
    # Create a check-in with the current local time, not UTC
    # Get the local time first (already in UTC+2) and don't use model default
    local_now = datetime.now()
    
    # Log the time details for debugging
    app.logger.info(f"Current local time: {local_now}, Current UTC time: {datetime.utcnow()}")
    
    check_in = CheckIn(
        user_id=current_user.id,
        status=request.form['status'],
        note=request.form.get('note'),
        check_in_time=local_now  # Explicitly setting local time
    )
    db.session.add(check_in)
    try:
        db.session.commit()
        app.logger.info(f"Check-in created for user {current_user.id} at {check_in.check_in_time} with status {check_in.status}")
        flash('Status succesvol bijgewerkt', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Er is een fout opgetreden bij het bijwerken van je status', 'danger')
        app.logger.error(f"Error during check-in: {str(e)}")

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
    app.logger.debug(f"Editing check-in {checkin_id}, form data: {request.form}")
    check_in = CheckIn.query.get_or_404(checkin_id)
    if check_in.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))

    try:
        # Validate required fields
        if 'status' not in request.form:
            raise ValueError("Status field is required")
            
        # Update fields
        check_in.status = request.form['status']
        check_in.note = request.form.get('note', '')
        
        # Update check-in time if provided
        if 'check_in_time' in request.form and request.form['check_in_time']:
            try:
                # Get current date
                current_date = check_in.check_in_time.date()
                # Parse time from form
                time_str = request.form['check_in_time']
                hours, minutes = map(int, time_str.split(':'))
                
                # Create new datetime object with current date and new time
                from datetime import datetime, time
                new_time = time(hour=hours, minute=minutes)
                new_datetime = datetime.combine(current_date, new_time)
                
                # Store the time (it's already in UTC in the database)
                check_in.check_in_time = new_datetime
                app.logger.debug(f"Updated check-in time to {new_datetime}")
            except Exception as time_error:
                app.logger.error(f"Error parsing time: {str(time_error)}")
                raise ValueError(f"Invalid time format: {str(time_error)}")
        
        # Log what's being updated
        app.logger.debug(f"Updating check-in {checkin_id}: status={check_in.status}, note={check_in.note}, time={check_in.check_in_time}")
        
        db.session.commit()
        flash('Check-in bijgewerkt', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating check-in {checkin_id}: {str(e)}")
        flash(f'Fout bij bijwerken check-in: {str(e)}', 'danger')

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
                
            # Create the time entry
            entry = TimeEntry(
                date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
                hours=float(request.form['hours']),
                description=description,
                project=request.form['project'],
                user_id=user_id
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
    
    entries_query = TimeEntry.query
    if selected_employee:
        # Filter by user_id where medewerker_id matches
        user_ids = [user.id for user in users if user.medewerker_id == int(selected_employee)]
        if user_ids:
            entries_query = entries_query.filter(TimeEntry.user_id.in_(user_ids))
    
    entries = entries_query.order_by(TimeEntry.date.desc()).all()
    
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
                           selected_employee=selected_employee,
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