from flask import render_template, request, redirect, url_for, flash, jsonify, abort, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from app import db, login_manager
from app.models.models import User, TimeEntry, CheckIn, Klant, Opdracht, Werkzaamheid, Factuur
from datetime import datetime, timedelta, date
from sqlalchemy import func, distinct
import json
import calendar
from collections import defaultdict

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Authentication routes
@login_required
def index():
    """Home route, redirects to dashboard"""
    return redirect(url_for('dashboard'))

def login():
    """Login route"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@login_required
def logout():
    """Logout route"""
    logout_user()
    return redirect(url_for('login'))

# Dashboard routes
@login_required
def dashboard():
    """Main dashboard view"""
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
    
    return render_template('dashboard.html', entries=entries, check_ins=check_ins, clients=clients, opdrachten=opdrachten)

# Time entry routes
@login_required
def add_time_entry():
    """Add a new time entry"""
    if request.method == 'POST':
        date_str = request.form['date']
        hours = float(request.form['hours'])
        description = request.form['description']
        project = request.form['project']
        
        # Optional fields
        is_billable = 'is_billable' in request.form
        hourly_rate = request.form.get('hourly_rate', None)
        if hourly_rate and hourly_rate.strip():
            hourly_rate = float(hourly_rate)
        else:
            hourly_rate = None
            
        # Get opdracht_id if selected
        opdracht_id = request.form.get('opdracht_id', None)
        if opdracht_id and opdracht_id.strip():
            opdracht_id = int(opdracht_id)
        else:
            opdracht_id = None
        
        # Convert date string to date object
        try:
            entry_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format', 'danger')
            return redirect(url_for('dashboard'))
        
        # Create new time entry
        entry = TimeEntry(
            date=entry_date,
            hours=hours,
            description=description,
            project=project,
            user_id=current_user.id,
            is_billable=is_billable,
            hourly_rate=hourly_rate,
            opdracht_id=opdracht_id
        )
        
        db.session.add(entry)
        db.session.commit()
        
        flash('Time entry added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('dashboard'))

@login_required
def time_entries():
    """View all time entries"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get date filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query
    query = TimeEntry.query
    
    # Filter by current user unless admin/manager
    if not current_user.can_view_all():
        query = query.filter_by(user_id=current_user.id)
    
    # Apply date filters
    if start_date:
        query = query.filter(TimeEntry.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    
    if end_date:
        query = query.filter(TimeEntry.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    # Get paginated results
    entries = query.order_by(TimeEntry.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # Get all users for filtering (if user has permission)
    users = None
    if current_user.can_view_all():
        users = User.query.all()
    
    # Get list of distinct projects for filtering
    projects = db.session.query(distinct(TimeEntry.project)).order_by(TimeEntry.project).all()
    projects = [p[0] for p in projects]
    
    # Get open assignments for selection in forms
    opdrachten = Opdracht.query.filter(Opdracht.status.in_(['open', 'in-progress'])).order_by(Opdracht.titel).all()
    
    return render_template(
        'time_entries.html', 
        entries=entries,
        users=users, 
        projects=projects,
        opdrachten=opdrachten,
        start_date=start_date,
        end_date=end_date
    )

@login_required
def edit_time_entry(id):
    """Edit a time entry"""
    entry = TimeEntry.query.get_or_404(id)
    
    # Check if user is authorized to edit this entry
    if entry.user_id != current_user.id and not current_user.can_edit_all():
        abort(403)  # Forbidden
    
    if request.method == 'POST':
        entry.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        entry.hours = float(request.form['hours'])
        entry.description = request.form['description']
        entry.project = request.form['project']
        
        # Optional fields
        entry.is_billable = 'is_billable' in request.form
        hourly_rate = request.form.get('hourly_rate', None)
        if hourly_rate and hourly_rate.strip():
            entry.hourly_rate = float(hourly_rate)
        else:
            entry.hourly_rate = None
            
        # Get opdracht_id if selected
        opdracht_id = request.form.get('opdracht_id', None)
        if opdracht_id and opdracht_id.strip():
            entry.opdracht_id = int(opdracht_id)
        else:
            entry.opdracht_id = None
        
        db.session.commit()
        flash('Time entry updated successfully!', 'success')
        
        # Check if we need to redirect to a specific page
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('time_entries'))
    
    # Get open assignments for selection in forms
    opdrachten = Opdracht.query.filter(Opdracht.status.in_(['open', 'in-progress'])).order_by(Opdracht.titel).all()
    
    return render_template('edit_time_entry.html', entry=entry, opdrachten=opdrachten)

@login_required
def delete_time_entry(id):
    """Delete a time entry"""
    entry = TimeEntry.query.get_or_404(id)
    
    # Check if user is authorized to delete this entry
    if entry.user_id != current_user.id and not current_user.can_edit_all():
        abort(403)  # Forbidden
    
    db.session.delete(entry)
    db.session.commit()
    
    flash('Time entry deleted successfully!', 'success')
    
    # Check if we need to redirect to a specific page
    next_page = request.args.get('next')
    if next_page:
        return redirect(next_page)
    return redirect(url_for('time_entries'))

# Check-in routes
@login_required
def add_check_in():
    """Add a new check-in"""
    if request.method == 'POST':
        status = request.form['status']
        note = request.form.get('note', '')
        
        # Get opdracht_id if selected
        opdracht_id = request.form.get('opdracht_id', None)
        if opdracht_id and opdracht_id.strip():
            opdracht_id = int(opdracht_id)
        else:
            opdracht_id = None
        
        # Create new check-in
        check_in = CheckIn(
            user_id=current_user.id,
            status=status,
            note=note,
            opdracht_id=opdracht_id
        )
        
        db.session.add(check_in)
        db.session.commit()
        
        flash('Check-in recorded successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return redirect(url_for('dashboard'))

@login_required
def check_ins():
    """View all check-ins"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Get date filter parameters
    date_str = request.args.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = datetime.now().date()
    else:
        selected_date = datetime.now().date()
    
    # Calculate date range
    start_date = selected_date
    end_date = selected_date + timedelta(days=1)
    
    # Build query
    query = CheckIn.query.filter(
        CheckIn.check_in_time >= start_date,
        CheckIn.check_in_time < end_date
    )
    
    # Filter by current user unless admin/manager
    if not current_user.can_view_all():
        query = query.filter_by(user_id=current_user.id)
    
    # Get paginated results, ordered by check-in time descending
    check_ins = query.order_by(CheckIn.check_in_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    # Get all users for filtering (if user has permission)
    users = None
    if current_user.can_view_all():
        users = User.query.all()
    
    # Get open assignments for selection in forms
    opdrachten = Opdracht.query.filter(Opdracht.status.in_(['open', 'in-progress'])).order_by(Opdracht.titel).all()
    
    return render_template(
        'check_ins.html',
        check_ins=check_ins,
        users=users,
        selected_date=selected_date,
        opdrachten=opdrachten
    )

@login_required
def edit_check_in(id):
    """Edit a check-in"""
    check_in = CheckIn.query.get_or_404(id)
    
    # Check if user is authorized to edit this check-in
    if check_in.user_id != current_user.id and not current_user.can_edit_all():
        abort(403)  # Forbidden
    
    if request.method == 'POST':
        # Only allow editing status and note
        check_in.status = request.form['status']
        check_in.note = request.form.get('note', '')
        
        # Get opdracht_id if selected
        opdracht_id = request.form.get('opdracht_id', None)
        if opdracht_id and opdracht_id.strip():
            check_in.opdracht_id = int(opdracht_id)
        else:
            check_in.opdracht_id = None
        
        db.session.commit()
        flash('Check-in updated successfully!', 'success')
        
        # Check if we need to redirect to a specific page
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        return redirect(url_for('check_ins'))
    
    # Get open assignments for selection in forms
    opdrachten = Opdracht.query.filter(Opdracht.status.in_(['open', 'in-progress'])).order_by(Opdracht.titel).all()
    
    return render_template('edit_check_in.html', check_in=check_in, opdrachten=opdrachten)

@login_required
def delete_check_in(id):
    """Delete a check-in"""
    check_in = CheckIn.query.get_or_404(id)
    
    # Check if user is authorized to delete this check-in
    if check_in.user_id != current_user.id and not current_user.can_edit_all():
        abort(403)  # Forbidden
    
    db.session.delete(check_in)
    db.session.commit()
    
    flash('Check-in deleted successfully!', 'success')
    
    # Check if we need to redirect to a specific page
    next_page = request.args.get('next')
    if next_page:
        return redirect(next_page)
    return redirect(url_for('check_ins'))

# Client routes
@login_required
def clients():
    """View all clients"""
    # Only users with view_all permission can see all clients
    if not current_user.can_view_all():
        flash('You do not have permission to view all clients', 'danger')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filter by status
    status = request.args.get('status', 'all')
    if status != 'all':
        clients = Klant.query.filter_by(status=status).order_by(Klant.bedrijfsnaam).paginate(page=page, per_page=per_page, error_out=False)
    else:
        clients = Klant.query.order_by(Klant.bedrijfsnaam).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('clients.html', clients=clients, status=status)

@login_required
def add_client():
    """Add a new client"""
    # Only users with edit_all permission can add clients
    if not current_user.can_edit_all():
        flash('You do not have permission to add clients', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Create new client
        client = Klant(
            bedrijfsnaam=request.form['bedrijfsnaam'],
            voornaam=request.form['voornaam'],
            achternaam=request.form['achternaam'],
            tussenvoegsel=request.form.get('tussenvoegsel', ''),
            functie=request.form.get('functie', ''),
            email=request.form['email'],
            telefoonnummer=request.form.get('telefoonnummer', ''),
            adres=request.form.get('adres', ''),
            postcode=request.form.get('postcode', ''),
            plaats=request.form.get('plaats', ''),
            land=request.form.get('land', 'Nederland'),
            btw_nummer=request.form.get('btw_nummer', ''),
            kvk_nummer=request.form.get('kvk_nummer', ''),
            status=request.form.get('status', 'actief')
        )
        
        db.session.add(client)
        db.session.commit()
        
        flash('Client added successfully!', 'success')
        return redirect(url_for('clients'))
    
    return render_template('add_client.html')

@login_required
def edit_client(id):
    """Edit a client"""
    # Only users with edit_all permission can edit clients
    if not current_user.can_edit_all():
        flash('You do not have permission to edit clients', 'danger')
        return redirect(url_for('dashboard'))
    
    client = Klant.query.get_or_404(id)
    
    if request.method == 'POST':
        client.bedrijfsnaam = request.form['bedrijfsnaam']
        client.voornaam = request.form['voornaam']
        client.achternaam = request.form['achternaam']
        client.tussenvoegsel = request.form.get('tussenvoegsel', '')
        client.functie = request.form.get('functie', '')
        client.email = request.form['email']
        client.telefoonnummer = request.form.get('telefoonnummer', '')
        client.adres = request.form.get('adres', '')
        client.postcode = request.form.get('postcode', '')
        client.plaats = request.form.get('plaats', '')
        client.land = request.form.get('land', 'Nederland')
        client.btw_nummer = request.form.get('btw_nummer', '')
        client.kvk_nummer = request.form.get('kvk_nummer', '')
        client.status = request.form.get('status', 'actief')
        
        db.session.commit()
        
        flash('Client updated successfully!', 'success')
        return redirect(url_for('clients'))
    
    return render_template('edit_client.html', client=client)

@login_required
def view_client(id):
    """View a client's details and related data"""
    # Only users with view_all permission can view client details
    if not current_user.can_view_all():
        flash('You do not have permission to view client details', 'danger')
        return redirect(url_for('dashboard'))
    
    client = Klant.query.get_or_404(id)
    
    # Get active assignments for this client
    active_assignments = Opdracht.query.filter_by(klant_id=id).filter(
        Opdracht.status.in_(['open', 'in-progress'])
    ).order_by(Opdracht.aanvraagdatum.desc()).limit(5).all()
    
    # Get recent invoices for this client
    recent_invoices = Factuur.query.filter_by(klant_id=id).order_by(Factuur.datum.desc()).limit(5).all()
    
    return render_template(
        'view_client.html',
        client=client,
        active_assignments=active_assignments,
        recent_invoices=recent_invoices
    )

# Assignment routes
@login_required
def assignments():
    """View all assignments"""
    # Only users with view_all permission can see all assignments
    if not current_user.can_view_all():
        flash('You do not have permission to view all assignments', 'danger')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Filter by status
    status = request.args.get('status', 'all')
    if status != 'all':
        assignments = Opdracht.query.filter_by(status=status).order_by(Opdracht.aanvraagdatum.desc()).paginate(page=page, per_page=per_page, error_out=False)
    else:
        assignments = Opdracht.query.order_by(Opdracht.aanvraagdatum.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('assignments.html', assignments=assignments, status=status)

@login_required
def add_assignment():
    """Add a new assignment"""
    # Only users with edit_all permission can add assignments
    if not current_user.can_edit_all():
        flash('You do not have permission to add assignments', 'danger')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        # Parse deadline if provided
        deadline_str = request.form.get('deadline', '')
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid deadline format', 'danger')
                return redirect(url_for('assignments'))
        
        # Parse hourly rate if provided
        uurtarief_str = request.form.get('uurtarief', '')
        uurtarief = None
        if uurtarief_str:
            try:
                uurtarief = float(uurtarief_str)
            except ValueError:
                flash('Invalid hourly rate format', 'danger')
                return redirect(url_for('assignments'))
        
        # Create new assignment
        assignment = Opdracht(
            klant_id=int(request.form['klant_id']),
            titel=request.form['titel'],
            omschrijving=request.form.get('omschrijving', ''),
            aanvraagdatum=datetime.strptime(request.form['aanvraagdatum'], '%Y-%m-%d').date(),
            benodigde_kennis=request.form.get('benodigde_kennis', ''),
            deadline=deadline,
            status=request.form.get('status', 'open'),
            uurtarief=uurtarief
        )
        
        db.session.add(assignment)
        db.session.commit()
        
        flash('Assignment added successfully!', 'success')
        return redirect(url_for('assignments'))
    
    # Get active clients for dropdown
    clients = Klant.query.filter_by(status='actief').order_by(Klant.bedrijfsnaam).all()
    
    return render_template('add_assignment.html', clients=clients)

@login_required
def edit_assignment(id):
    """Edit an assignment"""
    # Only users with edit_all permission can edit assignments
    if not current_user.can_edit_all():
        flash('You do not have permission to edit assignments', 'danger')
        return redirect(url_for('dashboard'))
    
    assignment = Opdracht.query.get_or_404(id)
    
    if request.method == 'POST':
        # Parse deadline if provided
        deadline_str = request.form.get('deadline', '')
        if deadline_str:
            assignment.deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
        else:
            assignment.deadline = None
        
        # Parse hourly rate if provided
        uurtarief_str = request.form.get('uurtarief', '')
        if uurtarief_str:
            assignment.uurtarief = float(uurtarief_str)
        else:
            assignment.uurtarief = None
        
        assignment.klant_id = int(request.form['klant_id'])
        assignment.titel = request.form['titel']
        assignment.omschrijving = request.form.get('omschrijving', '')
        assignment.aanvraagdatum = datetime.strptime(request.form['aanvraagdatum'], '%Y-%m-%d').date()
        assignment.benodigde_kennis = request.form.get('benodigde_kennis', '')
        assignment.status = request.form.get('status', 'open')
        
        db.session.commit()
        
        flash('Assignment updated successfully!', 'success')
        return redirect(url_for('assignments'))
    
    # Get active clients for dropdown
    clients = Klant.query.filter_by(status='actief').order_by(Klant.bedrijfsnaam).all()
    
    return render_template('edit_assignment.html', assignment=assignment, clients=clients)

@login_required
def view_assignment(id):
    """View an assignment's details and related data"""
    assignment = Opdracht.query.get_or_404(id)
    
    # Only users with view_all permission can view assignments they don't work on
    user_works_on_assignment = TimeEntry.query.filter_by(
        user_id=current_user.id, 
        opdracht_id=id
    ).first() is not None
    
    if not user_works_on_assignment and not current_user.can_view_all():
        flash('You do not have permission to view this assignment', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get time entries for this assignment
    time_entries = TimeEntry.query.filter_by(opdracht_id=id).order_by(TimeEntry.date.desc()).limit(10).all()
    
    # Calculate total hours and billable hours
    total_hours = db.session.query(func.sum(TimeEntry.hours)).filter_by(opdracht_id=id).scalar() or 0
    billable_hours = db.session.query(func.sum(TimeEntry.hours)).filter_by(opdracht_id=id, is_billable=True).scalar() or 0
    
    # Get invoices for this assignment
    invoices = Factuur.query.filter_by(opdracht_id=id).order_by(Factuur.datum.desc()).all()
    
    # Calculate total invoiced amount
    total_invoiced = sum(invoice.subtotaal for invoice in invoices)
    
    return render_template(
        'view_assignment.html',
        assignment=assignment,
        time_entries=time_entries,
        total_hours=total_hours,
        billable_hours=billable_hours,
        invoices=invoices,
        total_invoiced=total_invoiced
    )

# Reports and statistics
@login_required
def reports():
    """Reports dashboard"""
    # Only users with view_all permission can see reports
    if not current_user.can_view_all():
        flash('You do not have permission to view reports', 'danger')
        return redirect(url_for('dashboard'))
    
    # Current year for default filters
    current_year = datetime.now().year
    
    # Get available years for filtering
    years = db.session.query(
        func.extract('year', TimeEntry.date).distinct()
    ).order_by(func.extract('year', TimeEntry.date).desc()).all()
    years = [int(y[0]) for y in years if y[0]]
    
    # If no data, add current year
    if not years:
        years = [current_year]
    
    # Get monthly hours for the current year
    monthly_hours = get_monthly_hours(current_year)
    
    # Get total hours per year
    yearly_hours = TimeEntry.get_hours_per_year()
    yearly_hours = {int(item.year): float(item.total_hours) for item in yearly_hours}
    
    # Get assignments per client
    assignments_per_client = Opdracht.get_assignments_per_client(current_year)
    
    # Format data for charts
    monthly_chart_data = {
        'labels': list(calendar.month_name)[1:],
        'datasets': [
            {
                'label': 'Total Hours',
                'data': [monthly_hours.get(i, 0) for i in range(1, 13)],
                'borderColor': 'rgb(75, 192, 192)',
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            }
        ]
    }
    
    yearly_chart_data = {
        'labels': list(yearly_hours.keys()),
        'datasets': [
            {
                'label': 'Total Hours',
                'data': list(yearly_hours.values()),
                'borderColor': 'rgb(153, 102, 255)',
                'backgroundColor': 'rgba(153, 102, 255, 0.2)',
            }
        ]
    }
    
    client_labels = [item.bedrijfsnaam for item in assignments_per_client]
    client_assignment_counts = [item.assignment_count for item in assignments_per_client]
    
    client_chart_data = {
        'labels': client_labels,
        'datasets': [
            {
                'label': 'Assignments',
                'data': client_assignment_counts,
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.2)',
                    'rgba(54, 162, 235, 0.2)',
                    'rgba(255, 206, 86, 0.2)',
                    'rgba(75, 192, 192, 0.2)',
                    'rgba(153, 102, 255, 0.2)',
                    'rgba(255, 159, 64, 0.2)'
                ],
                'borderColor': [
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)',
                    'rgb(255, 206, 86)',
                    'rgb(75, 192, 192)',
                    'rgb(153, 102, 255)',
                    'rgb(255, 159, 64)'
                ],
                'borderWidth': 1
            }
        ]
    }
    
    return render_template(
        'reports.html',
        years=years,
        current_year=current_year,
        monthly_chart_data=json.dumps(monthly_chart_data),
        yearly_chart_data=json.dumps(yearly_chart_data),
        client_chart_data=json.dumps(client_chart_data)
    )

def get_monthly_hours(year):
    """Helper function to get hours worked per month for a given year"""
    data = db.session.query(
        extract('month', TimeEntry.date).label('month'),
        func.sum(TimeEntry.hours).label('total_hours')
    ).filter(
        extract('year', TimeEntry.date) == year
    ).group_by(
        extract('month', TimeEntry.date)
    ).all()
    
    result = {int(item.month): float(item.total_hours) for item in data}
    return result

# API routes
def api_time_entries():
    """API endpoint for time entries"""
    # Require API key
    if request.headers.get('X-API-KEY') != app.config['API_KEY']:
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Handle GET requests
    if request.method == 'GET':
        # Parse filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        user_id = request.args.get('user_id')
        
        # Build query
        query = TimeEntry.query
        
        # Apply filters
        if start_date:
            query = query.filter(TimeEntry.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        
        if end_date:
            query = query.filter(TimeEntry.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        if user_id:
            query = query.filter(TimeEntry.user_id == int(user_id))
        
        # Get results
        entries = query.order_by(TimeEntry.date.desc()).all()
        
        # Format response
        result = []
        for entry in entries:
            result.append({
                'id': entry.id,
                'date': entry.date.strftime('%Y-%m-%d'),
                'hours': entry.hours,
                'description': entry.description,
                'project': entry.project,
                'user_id': entry.user_id,
                'is_billable': entry.is_billable,
                'hourly_rate': entry.hourly_rate,
                'opdracht_id': entry.opdracht_id
            })
        
        return jsonify(result)
    
    return jsonify({'error': 'Method not allowed'}), 405 