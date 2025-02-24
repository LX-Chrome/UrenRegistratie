import pdfkit
import json
from datetime import datetime
from flask import render_template, redirect, url_for, request, flash, make_response, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db, login_manager
from models import User, TimeEntry

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