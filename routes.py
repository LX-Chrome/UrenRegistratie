import pdfkit
import json
from datetime import datetime
from flask import render_template, redirect, url_for, request, flash, make_response, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from models import User, TimeEntry, Klant, Medewerker, Opdracht, Werkzaamheid
import pdfkit
from datetime import datetime

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
    return render_template('dashboard.html', entries=entries)

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

@app.route('/export-pdf')
@login_required
def export_pdf():
    entries = TimeEntry.query.filter_by(user_id=current_user.id).order_by(TimeEntry.date.desc()).all()
    html = render_template('time_entries.html', entries=entries, export_mode=True)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=time-entries.pdf'
    return response

# New API endpoints for external clients (like PHP)
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

@app.route('/klanten/export-pdf')
@login_required
def export_klanten_pdf():
    klanten = Klant.query.order_by(Klant.bedrijfsnaam).all()
    html = render_template('klanten.html', klanten=klanten, export_mode=True)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=klanten.pdf'
    return response

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

@app.route('/medewerkers/export-pdf')
@login_required
def export_medewerkers_pdf():
    medewerkers = Medewerker.query.order_by(Medewerker.achternaam).all()
    html = render_template('medewerkers.html', medewerkers=medewerkers, export_mode=True)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=medewerkers.pdf'
    return response

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

@app.route('/opdrachten/export-pdf')
@login_required
def export_opdrachten_pdf():
    opdrachten = Opdracht.query.order_by(Opdracht.aanvraagdatum.desc()).all()
    html = render_template('opdrachten.html', opdrachten=opdrachten, export_mode=True)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=opdrachten.pdf'
    return response

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