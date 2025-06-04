from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Index, func, extract, case
from enum import Enum

# Define roles as an Enum for type safety
class RoleEnum(str, Enum):
    MEDEWERKER = 'medewerker'  # Regular employee
    VERKOOP = 'verkoop'        # Sales staff
    AFDELINGSHOOFD = 'afdelingshoofd'  # Department head
    ADMIN = 'admin'            # System administrator

# Role model for user permissions
class Role(db.Model):
    __tablename__ = 'role'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, nullable=False)
    description = db.Column(db.String(200))
    
    # Relationship with users
    users = db.relationship('User', backref='role', lazy=True)
    
    def __repr__(self):
        return f'<Role {self.name}>'

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False, default=1)  # Default to basic employee role
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    medewerker_id = db.Column(db.Integer, db.ForeignKey('medewerker.id'), nullable=True)  # Link to employee record if exists
    
    # Relationships
    time_entries = db.relationship('TimeEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    check_ins = db.relationship('CheckIn', backref='user', lazy=True, cascade='all, delete-orphan')
    facturen = db.relationship('Factuur', backref='creator', lazy=True)

    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
        Index('idx_user_role', 'role_id'),
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def has_role(self, role_name):
        """Check if user has a specific role"""
        if self.role:
            return self.role.name == role_name
        return False
        
    def can_view_all(self):
        """Check if user has permission to view all data (verkoop or afdelingshoofd)"""
        if self.role:
            return self.role.name in [RoleEnum.VERKOOP, RoleEnum.AFDELINGSHOOFD, RoleEnum.ADMIN]
        return False
        
    def can_edit_all(self):
        """Check if user has permission to edit all data"""
        if self.role:
            return self.role.name in [RoleEnum.AFDELINGSHOOFD, RoleEnum.ADMIN]
        return False
        
    def can_create_invoices(self):
        """Check if user has permission to create invoices"""
        if self.role:
            return self.role.name in [RoleEnum.VERKOOP, RoleEnum.AFDELINGSHOOFD, RoleEnum.ADMIN]
        return False

class CheckIn(db.Model):
    __tablename__ = 'check_in'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)  # 'working', 'break', 'done'
    note = db.Column(db.String(200))
    opdracht_id = db.Column(db.Integer, db.ForeignKey('opdracht.id'), nullable=True)  # Link to assignment/task

    __table_args__ = (
        Index('idx_check_in_user_date', 'user_id', 'check_in_time'),
        Index('idx_check_in_opdracht', 'opdracht_id'),
    )

class Klant(db.Model):
    __tablename__ = 'klant'

    id = db.Column(db.Integer, primary_key=True)
    bedrijfsnaam = db.Column(db.String(100), nullable=False)
    voornaam = db.Column(db.String(50), nullable=False)
    tussenvoegsel = db.Column(db.String(20))
    achternaam = db.Column(db.String(50), nullable=False)
    functie = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefoonnummer = db.Column(db.String(20))
    adres = db.Column(db.String(200))
    postcode = db.Column(db.String(10))
    plaats = db.Column(db.String(100))
    land = db.Column(db.String(100), default='Nederland')
    btw_nummer = db.Column(db.String(50))
    kvk_nummer = db.Column(db.String(50))
    status = db.Column(db.String(50), default='actief')  # actief, inactief, prospect
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    opdrachten = db.relationship('Opdracht', backref='klant', lazy=True)
    facturen = db.relationship('Factuur', backref='klant', lazy=True)

    __table_args__ = (
        Index('idx_klant_email', 'email'),
        Index('idx_klant_naam', 'bedrijfsnaam', 'achternaam'),
        Index('idx_klant_status', 'status'),
    )
    
    def get_fullname(self):
        """Return the full name of the client contact person"""
        if self.tussenvoegsel:
            return f"{self.voornaam} {self.tussenvoegsel} {self.achternaam}"
        return f"{self.voornaam} {self.achternaam}"

class Medewerker(db.Model):
    __tablename__ = 'medewerker'

    id = db.Column(db.Integer, primary_key=True)
    voornaam = db.Column(db.String(50), nullable=False)
    tussenvoegsel = db.Column(db.String(20))
    achternaam = db.Column(db.String(50), nullable=False)
    geboortedatum = db.Column(db.Date, nullable=False)
    functie = db.Column(db.String(100))
    werkmail = db.Column(db.String(120), unique=True, nullable=False)
    kantoorruimte = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    werkzaamheden = db.relationship('Werkzaamheid', backref='medewerker', lazy=True)

    __table_args__ = (
        Index('idx_medewerker_werkmail', 'werkmail'),
        Index('idx_medewerker_naam', 'voornaam', 'achternaam'),
    )

class Opdracht(db.Model):
    __tablename__ = 'opdracht'

    id = db.Column(db.Integer, primary_key=True)
    klant_id = db.Column(db.Integer, db.ForeignKey('klant.id', ondelete='CASCADE'), nullable=False)
    titel = db.Column(db.String(200), nullable=False)
    omschrijving = db.Column(db.Text)
    aanvraagdatum = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    benodigde_kennis = db.Column(db.String(500))
    deadline = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='open')  # open, in-progress, completed, cancelled
    uurtarief = db.Column(db.Float, nullable=True)  # Hourly rate for this assignment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    werkzaamheden = db.relationship('Werkzaamheid', backref='opdracht', lazy=True)
    facturen = db.relationship('Factuur', backref='opdracht', lazy=True)
    time_entries = db.relationship('TimeEntry', backref='opdracht', lazy=True)  # Link to time entries
    check_ins = db.relationship('CheckIn', backref='opdracht', lazy=True)  # Link to check-ins

    __table_args__ = (
        Index('idx_opdracht_klant', 'klant_id'),
        Index('idx_opdracht_datum', 'aanvraagdatum'),
        Index('idx_opdracht_status', 'status'),
    )
    
    @classmethod
    def get_opdrachten_per_client(cls, year=None):
        """Get count of assignments per client, optionally for a specific year"""
        query = db.session.query(
            Klant.bedrijfsnaam,
            func.count(cls.id).label('aantal_opdrachten')
        ).join(Klant)
        
        if year:
            query = query.filter(func.extract('year', cls.aanvraagdatum) == year)
            
        return query.group_by(Klant.bedrijfsnaam).all()

    @classmethod
    def get_assignments_per_client(cls, year=None):
        """Get assignments per client with total hours and revenue"""
        query = db.session.query(
            Klant.bedrijfsnaam,
            func.count(cls.id).label('assignment_count'),
            func.sum(case((cls.status == 'open', 1), else_=0)).label('open_count'),
            func.sum(case((cls.status == 'in-progress', 1), else_=0)).label('in_progress_count'),
            func.sum(case((cls.status == 'completed', 1), else_=0)).label('completed_count'),
            func.avg(cls.uurtarief).label('average_hourly_rate')
        ).join(Klant)
        
        if year:
            query = query.filter(func.extract('year', cls.aanvraagdatum) == year)
            
        return query.group_by(Klant.bedrijfsnaam).all()

class Werkzaamheid(db.Model):
    __tablename__ = 'werkzaamheid'

    id = db.Column(db.Integer, primary_key=True)
    medewerker_id = db.Column(db.Integer, db.ForeignKey('medewerker.id', ondelete='CASCADE'), nullable=False)
    opdracht_id = db.Column(db.Integer, db.ForeignKey('opdracht.id', ondelete='CASCADE'), nullable=False)
    aantal_uren = db.Column(db.Float, nullable=False)
    omschrijving = db.Column(db.Text, nullable=False)
    datum = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    is_declarabel = db.Column(db.Boolean, default=True)  # Billable flag
    uurtarief_override = db.Column(db.Float, nullable=True)  # Override default rate if needed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    factuur_id = db.Column(db.Integer, db.ForeignKey('factuur.id'), nullable=True)  # Link to invoice if billed

    __table_args__ = (
        Index('idx_werkzaamheid_medewerker', 'medewerker_id'),
        Index('idx_werkzaamheid_opdracht', 'opdracht_id'),
        Index('idx_werkzaamheid_datum', 'datum'),
        Index('idx_werkzaamheid_factuur', 'factuur_id'),
    )
    
    def get_effective_tarief(self):
        """Get the effective hourly rate for this activity"""
        # Use override if available
        if self.uurtarief_override:
            return self.uurtarief_override
        # Otherwise use the rate from the assignment
        elif self.opdracht and self.opdracht.uurtarief:
            return self.opdracht.uurtarief
        # Default fallback rate
        return 85.00  # Standard default hourly rate
    
    @classmethod
    def get_uren_per_medewerker(cls, year=None):
        """Get hours worked per employee, optionally for a specific year"""
        query = db.session.query(
            Medewerker.voornaam,
            Medewerker.achternaam,
            func.sum(cls.aantal_uren).label('totaal_uren')
        ).join(Medewerker)
        
        if year:
            query = query.filter(func.extract('year', cls.datum) == year)
            
        return query.group_by(Medewerker.voornaam, Medewerker.achternaam).all()

class Factuur(db.Model):
    __tablename__ = 'factuur'
    
    id = db.Column(db.Integer, primary_key=True)
    factuur_nummer = db.Column(db.String(50), unique=True, nullable=False)
    klant_id = db.Column(db.Integer, db.ForeignKey('klant.id', ondelete='CASCADE'), nullable=False)
    opdracht_id = db.Column(db.Integer, db.ForeignKey('opdracht.id'), nullable=True)  # Optional link to assignment
    datum = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    vervaldatum = db.Column(db.Date, nullable=False)  # Due date
    btw_percentage = db.Column(db.Float, default=21.0)  # VAT percentage
    subtotaal = db.Column(db.Float, nullable=False)  # Subtotal before VAT
    btw_bedrag = db.Column(db.Float, nullable=False)  # VAT amount
    totaal = db.Column(db.Float, nullable=False)  # Total including VAT
    betaald = db.Column(db.Boolean, default=False)  # Payment status
    betaaldatum = db.Column(db.Date, nullable=True)  # Date of payment
    betalingsvoorwaarden = db.Column(db.String(500), default='Betaling binnen 30 dagen')  # Payment terms
    notities = db.Column(db.Text, nullable=True)  # Additional notes
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # User who created the invoice
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Creation timestamp
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # Last update
    
    # Relationships
    werkzaamheden = db.relationship('Werkzaamheid', backref='factuur', lazy=True)  # Activities included in invoice
    time_entries = db.relationship('TimeEntry', backref='factuur', lazy=True)  # Time entries included in invoice
    
    __table_args__ = (
        Index('idx_factuur_klant', 'klant_id'),
        Index('idx_factuur_datum', 'datum'),
        Index('idx_factuur_nummer', 'factuur_nummer'),
        Index('idx_factuur_betaald', 'betaald'),
    )
    
    @classmethod
    def get_jaaropbrengst(cls, year=None):
        """Get total revenue per year"""
        query = db.session.query(
            func.extract('year', cls.datum).label('jaar'),
            func.sum(cls.subtotaal).label('omzet_ex_btw'),
            func.sum(cls.totaal).label('omzet_inc_btw')
        )
        
        if year:
            query = query.filter(func.extract('year', cls.datum) == year)
            
        return query.group_by(func.extract('year', cls.datum)).all()

class TimeEntry(db.Model):
    __tablename__ = 'time_entry'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    project = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_billable = db.Column(db.Boolean, default=True)
    hourly_rate = db.Column(db.Float, nullable=True)  # For custom rates
    invoice_id = db.Column(db.Integer, db.ForeignKey('factuur.id'), nullable=True)  # Link to invoice if billed
    opdracht_id = db.Column(db.Integer, db.ForeignKey('opdracht.id'), nullable=True)  # Link to assignment/task

    __table_args__ = (
        Index('idx_time_entry_user', 'user_id'),
        Index('idx_time_entry_date', 'date'),
        Index('idx_time_entry_project', 'project'),
        Index('idx_time_entry_invoice', 'invoice_id'),
        Index('idx_time_entry_opdracht', 'opdracht_id'),
    )
    
    @classmethod
    def get_hours_per_year(cls, year=None):
        """Get total hours per year"""
        query = db.session.query(
            func.extract('year', cls.date).label('year'),
            func.sum(cls.hours).label('total_hours')
        )
        
        if year:
            query = query.filter(func.extract('year', cls.date) == year)
            
        return query.group_by(func.extract('year', cls.date)).all()
    
    @classmethod
    def get_billable_hours_per_project(cls, project_name=None):
        """Get billable hours per project"""
        query = db.session.query(
            cls.project,
            func.sum(cls.hours).label('billable_hours')
        ).filter_by(is_billable=True)
        
        if project_name:
            query = query.filter_by(project=project_name)
            
        return query.group_by(cls.project).all()
    
    @classmethod
    def get_billable_hours_per_client(cls, client_id=None):
        """Get billable hours per client"""
        query = db.session.query(
            Klant.bedrijfsnaam,
            func.sum(cls.hours).label('billable_hours')
        ).join(Opdracht, cls.opdracht_id == Opdracht.id)\
         .join(Klant, Opdracht.klant_id == Klant.id)\
         .filter_by(is_billable=True)
        
        if client_id:
            query = query.filter(Klant.id == client_id)
            
        return query.group_by(Klant.bedrijfsnaam).all() 