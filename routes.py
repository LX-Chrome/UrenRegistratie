import pdfkit
import json
from datetime import datetime
from flask import render_template, redirect, url_for, request, flash, make_response, jsonify, send_file
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from models import User, TimeEntry, Klant, Medewerker, Opdracht, Werkzaamheid, CheckIn # Added CheckIn import
import pdfkit
from datetime import datetime
from services.export_service import ExportService
import io

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
    entries = TimeEntry.query.filter_by(user_id=current_user.id).order_by(TimeEntry.date.desc()).limit(5)
    check_ins = CheckIn.query.filter_by(
        user_id=current_user.id,
        check_in_time=datetime.utcnow().date()
    ).order_by(CheckIn.check_in_time.desc()).limit(5)

    return render_template('dashboard.html', entries=entries, check_ins=check_ins)

@app.route('/time-entries', methods=['GET', 'POST'])
@login_required
def time_entries():
    if request.method == 'POST':
        entry = TimeEntry(
            date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
            hours=float(request.form['hours']),
            description=request.form['description'],
            project=request.form['project'],
            user_id=current_user.id
        )
        db.session.add(entry)
        db.session.commit()
        flash('Time entry added successfully')
        return redirect(url_for('time_entries'))

    search = request.args.get('search', '')
    entries = TimeEntry.query.filter_by(user_id=current_user.id)
    if search:
        entries = entries.filter(TimeEntry.description.contains(search) | 
                                  TimeEntry.project.contains(search))
    entries = entries.order_by(TimeEntry.date.desc()).all()
    return render_template('time_entries.html', entries=entries, search=search)

@app.route('/time-entries/<int:entry_id>/edit', methods=['POST'])
@login_required
def edit_time_entry(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('time_entries'))

    try:
        entry.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        entry.hours = float(request.form['hours'])
        entry.description = request.form['description']
        entry.project = request.form['project']
        db.session.commit()
        flash('Time entry updated successfully')
    except Exception as e:
        db.session.rollback()
        flash('Error updating time entry')
        app.logger.error(f"Error updating time entry: {str(e)}")

    return redirect(url_for('time_entries'))

@app.route('/time-entries/<int:entry_id>/delete')
@login_required
def delete_time_entry(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('time_entries'))

    try:
        db.session.delete(entry)
        db.session.commit()
        flash('Time entry deleted successfully')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting time entry')
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
            content, filename, mimetype = export_service.to_pdf('time_entries.html', data, 'time_entries')
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
            content, filename, mimetype = export_service.to_pdf('klanten.html', data, 'klanten')
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
            content, filename, mimetype = export_service.to_pdf('medewerkers.html', data, 'medewerkers')
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
            content, filename, mimetype = export_service.to_pdf('opdrachten.html', data, 'opdrachten')
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