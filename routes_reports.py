"""
Routes for reporting functionality in the UrenRegistratie system.
"""
from datetime import datetime
from flask import render_template, request, jsonify
from flask_login import login_required
from sqlalchemy import func, extract
from app import app, db
from models import User, TimeEntry, Klant, Opdracht, Werkzaamheid, Factuur, Medewerker
from auth_helpers import view_all_required

@app.route('/reports')
@login_required
@view_all_required
def reports_dashboard():
    """Main reports dashboard with links to all available reports"""
    # Get current year for default filtering
    current_year = datetime.now().year
    years = range(current_year - 5, current_year + 1)
    
    return render_template('reports/dashboard.html', current_year=current_year, years=years)

@app.route('/reports/hours-per-year')
@login_required
@view_all_required
def report_hours_per_year():
    """Report for hours worked per year"""
    selected_year = request.args.get('year', datetime.now().year, type=int)
    quarter = request.args.get('quarter', None)
    view_type = request.args.get('view', 'all')
    
    # Get hours by sources for the selected year
    try:
        # Define start and end dates based on selected quarter
        start_date = datetime(selected_year, 1, 1)
        end_date = datetime(selected_year, 12, 31, 23, 59, 59)
        
        # Apply quarter filtering if specified
        if quarter:
            if quarter == 'Q1':
                start_date = datetime(selected_year, 1, 1)
                end_date = datetime(selected_year, 3, 31, 23, 59, 59)
            elif quarter == 'Q2':
                start_date = datetime(selected_year, 4, 1)
                end_date = datetime(selected_year, 6, 30, 23, 59, 59)
            elif quarter == 'Q3':
                start_date = datetime(selected_year, 7, 1)
                end_date = datetime(selected_year, 9, 30, 23, 59, 59)
            elif quarter == 'Q4':
                start_date = datetime(selected_year, 10, 1)
                end_date = datetime(selected_year, 12, 31, 23, 59, 59)
        
        # From Werkzaamheid
        werkzaamheid_query = db.session.query(func.sum(Werkzaamheid.aantal_uren)) \
            .filter(Werkzaamheid.datum >= start_date, 
                   Werkzaamheid.datum <= end_date)
                   
        # Apply billable filter
        if view_type == 'billable':
            werkzaamheid_query = werkzaamheid_query.filter(Werkzaamheid.is_declarabel == True)
        elif view_type == 'non-billable':
            werkzaamheid_query = werkzaamheid_query.filter(Werkzaamheid.is_declarabel == False)
            
        werkzaamheid_hours = werkzaamheid_query.scalar() or 0
        
        # From TimeEntry
        time_entry_query = db.session.query(func.sum(TimeEntry.hours)) \
            .filter(TimeEntry.date >= start_date,
                   TimeEntry.date <= end_date)
        
        # Apply billable filter
        if view_type == 'billable':
            time_entry_query = time_entry_query.filter(TimeEntry.is_billable == True)
        elif view_type == 'non-billable':
            time_entry_query = time_entry_query.filter(TimeEntry.is_billable == False)
            
        time_entry_hours = time_entry_query.scalar() or 0
        
        # Calculate billable hours percentage
        billable_hours_query = db.session.query(func.sum(Werkzaamheid.aantal_uren)) \
            .filter(Werkzaamheid.datum >= start_date, 
                   Werkzaamheid.datum <= end_date,
                   Werkzaamheid.is_declarabel == True)
                  
        billable_hours = billable_hours_query.scalar() or 0
        
        # Add billable hours from TimeEntry
        billable_time_entry_hours = db.session.query(func.sum(TimeEntry.hours)) \
            .filter(TimeEntry.date >= start_date,
                   TimeEntry.date <= end_date,
                   TimeEntry.is_billable == True) \
            .scalar() or 0
            
        billable_hours += billable_time_entry_hours
        
        total_hours = time_entry_hours + werkzaamheid_hours
    except Exception as e:
        app.logger.error(f"Error getting hours: {str(e)}")
        total_hours = 0
        billable_hours = 0
    
    # Get hours per month for the selected year
    monthly_hours_time_entries = db.session.query(
        extract('month', TimeEntry.date).label('month'),
        func.sum(TimeEntry.hours).label('hours')
    ).filter(
        TimeEntry.date >= start_date,
        TimeEntry.date <= end_date
    )
    
    # Apply billable filter
    if view_type == 'billable':
        monthly_hours_time_entries = monthly_hours_time_entries.filter(TimeEntry.is_billable == True)
    elif view_type == 'non-billable':
        monthly_hours_time_entries = monthly_hours_time_entries.filter(TimeEntry.is_billable == False)
    
    monthly_hours_time_entries = monthly_hours_time_entries.group_by('month').all()
    
    monthly_hours_werkzaamheden = db.session.query(
        extract('month', Werkzaamheid.datum).label('month'),
        func.sum(Werkzaamheid.aantal_uren).label('hours')
    ).filter(
        Werkzaamheid.datum >= start_date,
        Werkzaamheid.datum <= end_date
    )
    
    # Apply billable filter
    if view_type == 'billable':
        monthly_hours_werkzaamheden = monthly_hours_werkzaamheden.filter(Werkzaamheid.is_declarabel == True)
    elif view_type == 'non-billable':
        monthly_hours_werkzaamheden = monthly_hours_werkzaamheden.filter(Werkzaamheid.is_declarabel == False)
    
    monthly_hours_werkzaamheden = monthly_hours_werkzaamheden.group_by('month').all()
    
    # Combine both sources into a single monthly view
    months = [0] * 12
    
    for month, hours in monthly_hours_time_entries:
        months[int(month)-1] += float(hours)
        
    for month, hours in monthly_hours_werkzaamheden:
        months[int(month)-1] += float(hours)
    
    # Get hours per employee with billable/non-billable split
    employee_hours = Werkzaamheid.get_uren_per_medewerker(
        selected_year, 
        quarter=quarter,
        view_type=view_type
    )
    
    # Get available years from TimeEntry
    try:
        te_years = db.session.query(
            func.extract('year', TimeEntry.date).distinct()
        ).order_by(
            func.extract('year', TimeEntry.date).desc()
        ).all()
        
        te_years = [int(year[0]) for year in te_years if year[0] is not None]
    except Exception as e:
        app.logger.error(f"Error getting TimeEntry years: {str(e)}")
        te_years = []

    # Get available years from Werkzaamheid
    try:
        w_years = db.session.query(
            func.extract('year', Werkzaamheid.datum).distinct()
        ).order_by(
            func.extract('year', Werkzaamheid.datum).desc()
        ).all()
        
        w_years = [int(year[0]) for year in w_years if year[0] is not None]
    except Exception as e:
        app.logger.error(f"Error getting Werkzaamheid years: {str(e)}")
        w_years = []

    # If no years found, use current year
    if not te_years and not w_years:
        years = [datetime.now().year]
    else:
        years = list(set(te_years + w_years))
        years.sort(reverse=True)
    
    return render_template(
        'reports/hours_per_year.html',
        selected_year=selected_year,
        years=years,
        total_hours=total_hours,
        billable_hours=billable_hours,
        monthly_hours=months,
        employee_hours=employee_hours,
        quarter=quarter,
        view_type=view_type
    )

@app.route('/reports/assignments-per-client')
@login_required
@view_all_required
def report_assignments_per_client():
    """Report for number of assignments per client"""
    selected_year = request.args.get('year', datetime.now().year, type=int)
    
    # Get assignments per client for the selected year
    assignments_per_client = Opdracht.get_assignments_per_client(selected_year)
    
    # Get total assignments for the selected year
    try:
        total_assignments = db.session.query(
            func.count(Opdracht.id)
        ).filter(
            func.extract('year', Opdracht.aanvraagdatum) == selected_year
        ).scalar() or 0
    except Exception as e:
        app.logger.error(f"Error getting total assignments: {str(e)}")
        total_assignments = 0
    
    # Get assignments by status
    try:
        assignments_by_status = db.session.query(
            Opdracht.status,
            func.count(Opdracht.id).label('count')
        ).filter(
            func.extract('year', Opdracht.aanvraagdatum) == selected_year
        ).group_by(Opdracht.status).all()
    except Exception as e:
        app.logger.error(f"Error getting assignments by status: {str(e)}")
        assignments_by_status = []
    
    # Get assignments per month for the selected year
    try:
        monthly_assignments = db.session.query(
            func.extract('month', Opdracht.aanvraagdatum).label('month'),
            func.count(Opdracht.id).label('count')
        ).filter(
            func.extract('year', Opdracht.aanvraagdatum) == selected_year
        ).group_by('month').all()
        
        # Format for chart display
        months = [0] * 12  # Initialize with zeros
        for month, count in monthly_assignments:
            if month is not None:
                months[int(month)-1] = int(count)
    except Exception as e:
        app.logger.error(f"Error getting monthly assignments: {str(e)}")
        months = [0] * 12
    
    # Get available years for the filter
    try:
        years = db.session.query(
            func.extract('year', Opdracht.aanvraagdatum).distinct()
        ).order_by(
            func.extract('year', Opdracht.aanvraagdatum).desc()
        ).all()
        
        years = [int(year[0]) for year in years if year[0] is not None]
    except Exception as e:
        app.logger.error(f"Error getting available years: {str(e)}")
        years = []
    
    # If no years found, use current year
    if not years:
        years = [datetime.now().year]
    
    return render_template(
        'reports/assignments_per_client.html',
        selected_year=selected_year,
        years=years,
        total_assignments=total_assignments,
        assignments_per_client=assignments_per_client,
        assignments_by_status=assignments_by_status,
        monthly_assignments=months
    )

@app.route('/reports/annual-revenue')
@login_required
@view_all_required
def report_annual_revenue():
    """Report for annual revenue"""
    selected_year = request.args.get('year', datetime.now().year, type=int)
    quarter = request.args.get('quarter', None)
    sort_by = request.args.get('sort', 'revenue')
    
    # Define start and end dates based on selected quarter
    start_date = datetime(selected_year, 1, 1)
    end_date = datetime(selected_year, 12, 31, 23, 59, 59)
    
    # Apply quarter filtering if specified
    if quarter:
        if quarter == 'Q1':
            start_date = datetime(selected_year, 1, 1)
            end_date = datetime(selected_year, 3, 31, 23, 59, 59)
        elif quarter == 'Q2':
            start_date = datetime(selected_year, 4, 1)
            end_date = datetime(selected_year, 6, 30, 23, 59, 59)
        elif quarter == 'Q3':
            start_date = datetime(selected_year, 7, 1)
            end_date = datetime(selected_year, 9, 30, 23, 59, 59)
        elif quarter == 'Q4':
            start_date = datetime(selected_year, 10, 1)
            end_date = datetime(selected_year, 12, 31, 23, 59, 59)
    
    # Get total revenue for the selected year and date range
    total_revenue_query = db.session.query(func.sum(Factuur.totaal)) \
        .filter(
            Factuur.datum >= start_date,
            Factuur.datum <= end_date,
            Factuur.betaald == True
        )
        
    total_revenue = total_revenue_query.scalar() or 0
    
    # Get monthly revenue for the selected year
    try:
        monthly_revenue = db.session.query(
            func.strftime('%m', Factuur.datum).label('month'),  # Use strftime instead of extract
            func.sum(Factuur.totaal).label('revenue')
        ).filter(
            Factuur.datum >= start_date,
            Factuur.datum <= end_date,
            Factuur.betaald == True
        ).group_by('month').all()
    except Exception as e:
        app.logger.error(f"Error getting monthly revenue: {str(e)}")
        monthly_revenue = []
    
    # Format for chart display
    months = [0] * 12  # Initialize with zeros
    for month, revenue in monthly_revenue:
        months[int(month)-1] = float(revenue)
    
    # Get revenue per client for the selected year and date range
    try:
        revenue_per_client_query = db.session.query(
            Klant.bedrijfsnaam.label('klant_naam'),
            func.coalesce(func.count(Werkzaamheid.id), 0).label('aantal_werkzaamheden'),
            func.coalesce(func.sum(Werkzaamheid.aantal_uren), 0.0).label('totaal_uren'),
            func.coalesce(func.sum(Factuur.totaal), 0.0).label('totaal_opbrengst')
        ).join(
            Factuur, Factuur.klant_id == Klant.id
        ).outerjoin(
            Werkzaamheid, (Werkzaamheid.klant_id == Klant.id) & 
            (Werkzaamheid.datum >= start_date) & 
            (Werkzaamheid.datum <= end_date)
        ).filter(
            Factuur.datum >= start_date,
            Factuur.datum <= end_date,
            Factuur.betaald == True
        ).group_by(Klant.bedrijfsnaam)
        
        # Apply sorting
        if sort_by == 'alpha':
            revenue_per_client_query = revenue_per_client_query.order_by(Klant.bedrijfsnaam)
        elif sort_by == 'hours':
            revenue_per_client_query = revenue_per_client_query.order_by(desc('totaal_uren'))
        else:  # default to revenue
            revenue_per_client_query = revenue_per_client_query.order_by(desc('totaal_opbrengst'))
            
        revenue_per_client = revenue_per_client_query.all()
    except Exception as e:
        app.logger.error(f"Error getting revenue per client: {str(e)}")
        revenue_per_client = []
    
    # Get available years for the filter
    try:
        years = db.session.query(
            func.strftime('%Y', Factuur.datum).distinct()
        ).order_by(
            func.strftime('%Y', Factuur.datum).desc()
        ).all()
        
        years = [int(year[0]) for year in years if year[0]]
    except Exception as e:
        app.logger.error(f"Error getting available years: {str(e)}")
        years = []
    
    # If no years found, use current year
    if not years:
        years = [datetime.now().year]
    
    return render_template(
        'reports/annual_revenue.html',
        selected_year=selected_year,
        years=years,
        total_revenue=total_revenue,
        monthly_revenue=months,
        revenue_per_client=revenue_per_client,
        quarter=quarter,
        sort_by=sort_by
    )

@app.route('/api/reports/dashboard-stats')
@login_required
@view_all_required
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    try:
        # Get current year
        current_year = datetime.now().year
        
        # Get total hours for the current year
        total_hours = TimeEntry.get_hours_per_year(current_year) + \
            db.session.query(func.sum(Werkzaamheid.aantal_uren)) \
            .filter(func.extract('year', Werkzaamheid.datum) == current_year) \
            .scalar() or 0
        
        # Get total revenue for the current year
        total_revenue = Factuur.get_jaaropbrengst(current_year)
        
        # Get total assignments for the current year
        total_assignments = db.session.query(func.count(Opdracht.id)) \
            .filter(func.extract('year', Opdracht.aanvraagdatum) == current_year) \
            .scalar() or 0
        
        # Get total clients
        total_clients = Klant.query.filter_by(status='actief').count()
        
        # Get total employees
        total_employees = Medewerker.query.count()
        
        return jsonify({
            'total_hours': total_hours,
            'total_revenue': total_revenue,
            'total_assignments': total_assignments,
            'total_clients': total_clients,
            'total_employees': total_employees
        })
    except Exception as e:
        app.logger.error(f"Error getting dashboard stats: {str(e)}")
        return jsonify({'error': str(e)}), 500
