from datetime import datetime
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Index

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    time_entries = db.relationship('TimeEntry', backref='user', lazy=True, cascade='all, delete-orphan')
    check_ins = db.relationship('CheckIn', backref='user', lazy=True, cascade='all, delete-orphan')

    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class CheckIn(db.Model):
    __tablename__ = 'check_in'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)  # 'working', 'break', 'done'
    note = db.Column(db.String(200))

    __table_args__ = (
        Index('idx_check_in_user_date', 'user_id', 'check_in_time'),
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    opdrachten = db.relationship('Opdracht', backref='klant', lazy=True)

    __table_args__ = (
        Index('idx_klant_email', 'email'),
        Index('idx_klant_naam', 'bedrijfsnaam', 'achternaam'),
    )

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    werkzaamheden = db.relationship('Werkzaamheid', backref='opdracht', lazy=True)

    __table_args__ = (
        Index('idx_opdracht_klant', 'klant_id'),
        Index('idx_opdracht_datum', 'aanvraagdatum'),
    )

class Werkzaamheid(db.Model):
    __tablename__ = 'werkzaamheid'

    id = db.Column(db.Integer, primary_key=True)
    medewerker_id = db.Column(db.Integer, db.ForeignKey('medewerker.id', ondelete='CASCADE'), nullable=False)
    opdracht_id = db.Column(db.Integer, db.ForeignKey('opdracht.id', ondelete='CASCADE'), nullable=False)
    aantal_uren = db.Column(db.Float, nullable=False)
    omschrijving = db.Column(db.Text, nullable=False)
    datum = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_werkzaamheid_medewerker', 'medewerker_id'),
        Index('idx_werkzaamheid_opdracht', 'opdracht_id'),
        Index('idx_werkzaamheid_datum', 'datum'),
    )

class TimeEntry(db.Model):
    __tablename__ = 'time_entry'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    project = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_time_entry_user_date', 'user_id', 'date'),
        Index('idx_time_entry_project', 'project'),
    )