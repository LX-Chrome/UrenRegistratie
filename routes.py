import json
from datetime import datetime
from flask import render_template, redirect, url_for, request, flash, make_response, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from models import User, TimeEntry, Klant, Medewerker, Opdracht, Werkzaamheid, CheckIn # Added CheckIn import
from services.export_service import ExportService
import io
import pandas as pd
import csv
from werkzeug.utils import secure_filename
import os
from sqlalchemy import func

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

    return render_template('dashboard.html', entries=entries, check_ins=check_ins)

@app.route('/time-entries', methods=['GET', 'POST'])
@login_required
def time_entries():
    if request.method == 'POST':
        try:
            entry = TimeEntry(
                date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
                hours=float(request.form['hours']),
                description=request.form['description'],
                project=request.form['project'],
                user_id=current_user.id
            )
            db.session.add(entry)
            db.session.commit()
            flash('Time entry added successfully', 'success')
            
            # Redirect to dashboard to see the entry in the recent list
            if request.form.get('redirect_to_dashboard') == 'true':
                return redirect(url_for('dashboard'))
            return redirect(url_for('time_entries'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding time entry: {str(e)}', 'danger')
            app.logger.error(f"Error adding time entry: {str(e)}")

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
        entry.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        entry.hours = float(request.form['hours'])
        entry.description = request.form['description']
        entry.project = request.form['project']
        db.session.commit()
        flash('Time entry updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating time entry: ' + str(e), 'danger')
        app.logger.error(f"Error updating time entry: {str(e)}")

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

    if entity == 'time-entries':
        entries = TimeEntry.query.filter_by(user_id=current_user.id).order_by(TimeEntry.date.desc()).all()
        if format == 'pdf':
            data = {'entries': entries}
            # Use the in-memory PDF generation method
            content, filename, mimetype = export_service.simple_pdf(data, 'time_entries')
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
            # Use the in-memory PDF generation method
            content, filename, mimetype = export_service.simple_pdf(data, 'klanten')
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
            # Use the in-memory PDF generation method
            content, filename, mimetype = export_service.simple_pdf(data, 'medewerkers')
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
            # Use the in-memory PDF generation method
            content, filename, mimetype = export_service.simple_pdf(data, 'opdrachten')
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
    check_in = CheckIn(
        user_id=current_user.id,
        status=request.form['status'],
        note=request.form.get('note')
    )
    db.session.add(check_in)
    try:
        db.session.commit()
        flash('Status succesvol bijgewerkt')
    except Exception as e:
        db.session.rollback()
        flash('Er is een fout opgetreden bij het bijwerken van je status')
        app.logger.error(f"Error during check-in: {str(e)}")

    return redirect(url_for('dashboard'))

@app.route('/check-in/<int:checkin_id>/delete')
@login_required
def delete_check_in(checkin_id):
    check_in = CheckIn.query.get_or_404(checkin_id)
    if check_in.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))

    try:
        db.session.delete(check_in)
        db.session.commit()
        flash('Check-in deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting check-in: ' + str(e), 'danger')
        app.logger.error(f"Error deleting check-in: {str(e)}")

    return redirect(url_for('dashboard'))

@app.route('/check-in/<int:checkin_id>/edit', methods=['POST'])
@login_required
def edit_check_in(checkin_id):
    check_in = CheckIn.query.get_or_404(checkin_id)
    if check_in.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard'))

    try:
        check_in.status = request.form['status']
        check_in.note = request.form.get('note', '')
        db.session.commit()
        flash('Check-in updated successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating check-in: ' + str(e), 'danger')
        app.logger.error(f"Error updating check-in: {str(e)}")

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