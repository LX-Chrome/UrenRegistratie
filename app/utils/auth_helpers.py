"""
Authentication and authorization helper functions for the UrenRegistratie system.
"""
from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from app.models.models import RoleEnum

def role_required(*roles):
    """
    Decorator to restrict access to certain routes based on user role.
    
    Args:
        *roles: Variable list of role names that are allowed to access the route
        
    Usage:
        @app.route('/admin')
        @role_required(RoleEnum.ADMIN)
        def admin_page():
            return "Admin only page"
            
        @app.route('/sales')
        @role_required(RoleEnum.VERKOOP, RoleEnum.AFDELINGSHOOFD)
        def sales_page():
            return "Sales and managers only page"
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Je moet ingelogd zijn om deze pagina te bekijken.', 'warning')
                return redirect(url_for('login'))
                
            if not current_user.role or current_user.role.name not in roles:
                flash('Je hebt geen toegang tot deze pagina.', 'danger')
                return redirect(url_for('dashboard'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Shortcut decorator for admin-only routes"""
    return role_required(RoleEnum.ADMIN)(f)

def view_all_required(f):
    """Decorator for routes that require permission to view all data"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Je moet ingelogd zijn om deze pagina te bekijken.', 'warning')
            return redirect(url_for('login'))
            
        if not current_user.can_view_all():
            flash('Je hebt geen toegang tot deze pagina.', 'danger')
            return redirect(url_for('dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

def edit_all_required(f):
    """Decorator for routes that require permission to edit all data"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Je moet ingelogd zijn om deze pagina te bekijken.', 'warning')
            return redirect(url_for('login'))
            
        if not current_user.can_edit_all():
            flash('Je hebt geen toegang tot deze pagina.', 'danger')
            return redirect(url_for('dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

def invoice_creation_required(f):
    """Decorator for routes that require permission to create invoices"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Je moet ingelogd zijn om deze pagina te bekijken.', 'warning')
            return redirect(url_for('login'))
            
        if not current_user.can_create_invoices():
            flash('Je hebt geen toegang tot deze pagina.', 'danger')
            return redirect(url_for('dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function 