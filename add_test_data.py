"""
Script om testgegevens toe te voegen aan de database
"""
from app import app, db
from models import User, Role, RoleEnum, Klant, Medewerker, Opdracht, Werkzaamheid, TimeEntry, Factuur
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

def add_test_data():
    with app.app_context():
        print("Testgegevens toevoegen...")
        
        # Check of er al gegevens zijn
        if Klant.query.count() > 0:
            print("Er zijn al klanten in de database. Script afbreken om duplicatie te voorkomen.")
            return
        
        # 1. Testklanten toevoegen
        print("Klanten toevoegen...")
        klanten = [
            {
                'bedrijfsnaam': 'TechSolutions BV',
                'voornaam': 'Jan',
                'tussenvoegsel': 'van',
                'achternaam': 'Bergen',
                'functie': 'CEO',
                'email': 'jan@techsolutions.nl',
                'telefoonnummer': '0612345678',
                'adres': 'Techniekweg 50',
                'postcode': '1234 AB',
                'plaats': 'Amsterdam',
                'btw_nummer': 'NL123456789B01',
                'kvk_nummer': '12345678'
            },
            {
                'bedrijfsnaam': 'Marketing Masters',
                'voornaam': 'Lisa',
                'tussenvoegsel': '',
                'achternaam': 'Jansen',
                'functie': 'Marketing Director',
                'email': 'lisa@marketingmasters.nl',
                'telefoonnummer': '0687654321',
                'adres': 'Mediastraat 25',
                'postcode': '2345 BC',
                'plaats': 'Rotterdam',
                'btw_nummer': 'NL987654321B01',
                'kvk_nummer': '87654321'
            },
            {
                'bedrijfsnaam': 'Bouw & Co',
                'voornaam': 'Peter',
                'tussenvoegsel': 'de',
                'achternaam': 'Vries',
                'functie': 'Projectmanager',
                'email': 'peter@bouwenco.nl',
                'telefoonnummer': '0623456789',
                'adres': 'Constructieweg 10',
                'postcode': '3456 CD',
                'plaats': 'Utrecht',
                'btw_nummer': 'NL456789123B01',
                'kvk_nummer': '45678912'
            },
            {
                'bedrijfsnaam': 'HealthCare Plus',
                'voornaam': 'Sophie',
                'tussenvoegsel': '',
                'achternaam': 'Bakker',
                'functie': 'Directeur',
                'email': 'sophie@healthcareplus.nl',
                'telefoonnummer': '0634567891',
                'adres': 'Zorglaan 75',
                'postcode': '4567 DE',
                'plaats': 'Den Haag',
                'btw_nummer': 'NL789123456B01',
                'kvk_nummer': '78912345'
            },
            {
                'bedrijfsnaam': 'FinanceTeam',
                'voornaam': 'Bart',
                'tussenvoegsel': 'van der',
                'achternaam': 'Meer',
                'functie': 'Financial Advisor',
                'email': 'bart@financeteam.nl',
                'telefoonnummer': '0645678912',
                'adres': 'Geldstraat 30',
                'postcode': '5678 EF',
                'plaats': 'Eindhoven',
                'btw_nummer': 'NL321456789B01',
                'kvk_nummer': '32145678'
            }
        ]
        
        db_klanten = []
        for k in klanten:
            klant = Klant(
                bedrijfsnaam=k['bedrijfsnaam'],
                voornaam=k['voornaam'],
                tussenvoegsel=k['tussenvoegsel'],
                achternaam=k['achternaam'],
                functie=k['functie'],
                email=k['email'],
                telefoonnummer=k['telefoonnummer'],
                adres=k['adres'],
                postcode=k['postcode'],
                plaats=k['plaats'],
                btw_nummer=k['btw_nummer'],
                kvk_nummer=k['kvk_nummer'],
                status='actief'
            )
            db.session.add(klant)
            db_klanten.append(klant)
        
        db.session.commit()
        print(f"{len(db_klanten)} klanten toegevoegd")
        
        # 2. Testmedewerkers toevoegen
        print("Medewerkers toevoegen...")
        medewerkers = [
            {
                'voornaam': 'Floris',
                'tussenvoegsel': 'van',
                'achternaam': 'Dijk',
                'geboortedatum': datetime(1985, 5, 15),
                'functie': 'Senior Developer',
                'werkmail': 'floris@gildedevops.nl',
                'kantoorruimte': 'A1.01'
            },
            {
                'voornaam': 'Emma',
                'tussenvoegsel': '',
                'achternaam': 'Smit',
                'geboortedatum': datetime(1990, 8, 22),
                'functie': 'UI/UX Designer',
                'werkmail': 'emma@gildedevops.nl',
                'kantoorruimte': 'A1.02'
            },
            {
                'voornaam': 'Niels',
                'tussenvoegsel': 'de',
                'achternaam': 'Boer',
                'geboortedatum': datetime(1988, 3, 10),
                'functie': 'Backend Developer',
                'werkmail': 'niels@gildedevops.nl',
                'kantoorruimte': 'A1.03'
            },
            {
                'voornaam': 'Laura',
                'tussenvoegsel': 'van der',
                'achternaam': 'Heijden',
                'geboortedatum': datetime(1992, 11, 5),
                'functie': 'Project Manager',
                'werkmail': 'laura@gildedevops.nl',
                'kantoorruimte': 'B2.01'
            },
            {
                'voornaam': 'Mark',
                'tussenvoegsel': '',
                'achternaam': 'Visser',
                'geboortedatum': datetime(1983, 7, 28),
                'functie': 'DevOps Engineer',
                'werkmail': 'mark@gildedevops.nl',
                'kantoorruimte': 'B2.02'
            }
        ]
        
        db_medewerkers = []
        for m in medewerkers:
            medewerker = Medewerker(
                voornaam=m['voornaam'],
                tussenvoegsel=m['tussenvoegsel'],
                achternaam=m['achternaam'],
                geboortedatum=m['geboortedatum'],
                functie=m['functie'],
                werkmail=m['werkmail'],
                kantoorruimte=m['kantoorruimte']
            )
            db.session.add(medewerker)
            db_medewerkers.append(medewerker)
        
        db.session.commit()
        print(f"{len(db_medewerkers)} medewerkers toegevoegd")
        
        # 3. Testopdrachten toevoegen
        print("Opdrachten toevoegen...")
        now = datetime.now()
        statussen = ['open', 'in-progress', 'completed', 'cancelled']
        db_opdrachten = []
        
        for i in range(15):
            klant = random.choice(db_klanten)
            start_date = now - timedelta(days=random.randint(0, 365))
            
            opdracht = Opdracht(
                klant_id=klant.id,
                titel=f"Opdracht {i+1} voor {klant.bedrijfsnaam}",
                omschrijving=f"Dit is een voorbeeld opdracht voor {klant.bedrijfsnaam}. Het bevat diverse werkzaamheden.",
                aanvraagdatum=start_date.date(),
                benodigde_kennis="Python, Flask, JavaScript, HTML, CSS",
                deadline=(start_date + timedelta(days=random.randint(30, 90))).date(),
                status=random.choice(statussen),
                uurtarief=random.choice([85.0, 95.0, 110.0, 125.0])
            )
            db.session.add(opdracht)
            db_opdrachten.append(opdracht)
        
        db.session.commit()
        print(f"{len(db_opdrachten)} opdrachten toegevoegd")
        
        # 4. Testwerkzaamheden toevoegen
        print("Werkzaamheden toevoegen...")
        db_werkzaamheden = []
        
        for i in range(50):
            medewerker = random.choice(db_medewerkers)
            opdracht = random.choice(db_opdrachten)
            werk_date = opdracht.aanvraagdatum + timedelta(days=random.randint(1, 30))
            
            werkzaamheid = Werkzaamheid(
                medewerker_id=medewerker.id,
                opdracht_id=opdracht.id,
                aantal_uren=random.randint(1, 8),
                omschrijving=f"Werkzaamheid voor {opdracht.titel}",
                datum=werk_date,
                is_declarabel=random.choice([True, True, True, False]),  # 75% declarabel
                uurtarief_override=None if random.random() > 0.2 else opdracht.uurtarief + random.choice([-10.0, 0.0, 10.0])
            )
            db.session.add(werkzaamheid)
            db_werkzaamheden.append(werkzaamheid)
        
        db.session.commit()
        print(f"{len(db_werkzaamheden)} werkzaamheden toegevoegd")
        
        # 5. Tijdsregistraties toevoegen voor bestaande gebruikers
        print("Tijdsregistraties toevoegen...")
        users = User.query.all()
        
        if not users:
            print("Geen gebruikers gevonden. Tijdsregistraties kunnen niet worden toegevoegd.")
        else:
            db_time_entries = []
            projects = ["Website Development", "App Development", "Server Maintenance", "UI Design", "Database Optimization"]
            
            for user in users:
                # Voeg 10-20 tijdsregistraties toe per gebruiker
                for i in range(random.randint(10, 20)):
                    entry_date = now - timedelta(days=random.randint(0, 90))
                    
                    time_entry = TimeEntry(
                        date=entry_date.date(),
                        hours=random.randint(1, 8),
                        description=f"Gewerkt aan {random.choice(projects)}",
                        project=random.choice(projects),
                        user_id=user.id,
                        is_billable=random.choice([True, True, False])  # 66% billable
                    )
                    db.session.add(time_entry)
                    db_time_entries.append(time_entry)
            
            db.session.commit()
            print(f"{len(db_time_entries)} tijdsregistraties toegevoegd")
        
        # 6. Facturen toevoegen
        print("Facturen toevoegen...")
        # Zoek een geschikte gebruiker voor het aanmaken van facturen
        admin_user = User.query.filter(User.role_id.in_([3, 4])).first()  # Zoek een admin of afdelingshoofd
        if not admin_user:
            admin_user = User.query.first()  # Als geen admin, pak dan de eerste gebruiker
        
        if not admin_user:
            print("Geen gebruikers gevonden. Facturen kunnen niet worden toegevoegd.")
        else:
            # Maak facturen aan
            db_facturen = []
            
            for i in range(10):
                # Kies een klant en eventueel een bijbehorende opdracht
                klant = random.choice(db_klanten)
                opdracht = random.choice([None] + [o for o in db_opdrachten if o.klant_id == klant.id])
                
                factuur_date = now - timedelta(days=random.randint(0, 180))
                due_date = factuur_date + timedelta(days=30)
                
                # Genereer factuurnummer (format: YYYYMM0001)
                factuur_nummer = f"{factuur_date.year}{factuur_date.month:02d}{i+1:04d}"
                
                # Bereken factuurbedragen
                subtotaal = random.randint(500, 5000)
                btw_percentage = 21.0
                btw_bedrag = subtotaal * (btw_percentage / 100)
                totaal = subtotaal + btw_bedrag
                
                factuur = Factuur(
                    factuur_nummer=factuur_nummer,
                    klant_id=klant.id,
                    opdracht_id=opdracht.id if opdracht else None,
                    datum=factuur_date.date(),
                    vervaldatum=due_date.date(),
                    btw_percentage=btw_percentage,
                    subtotaal=subtotaal,
                    btw_bedrag=btw_bedrag,
                    totaal=totaal,
                    betaald=random.choice([True, False]),
                    betaaldatum=(factuur_date + timedelta(days=random.randint(5, 25))).date() if random.random() > 0.3 else None,
                    betalingsvoorwaarden="Betaling binnen 30 dagen na factuurdatum",
                    notities="Bedankt voor uw vertrouwen in gildeDevOps Solutions.",
                    creator_id=admin_user.id
                )
                db.session.add(factuur)
                db_facturen.append(factuur)
            
            db.session.commit()
            print(f"{len(db_facturen)} facturen toegevoegd")
            
            # Koppel enkele werkzaamheden aan facturen
            declarabele_items = [w for w in db_werkzaamheden if w.is_declarabel and w.factuur_id is None]
            if declarabele_items:
                for factuur in db_facturen:
                    # Koppel 1-5 werkzaamheden aan elke factuur
                    for _ in range(min(random.randint(1, 5), len(declarabele_items))):
                        item = random.choice(declarabele_items)
                        item.factuur_id = factuur.id
                        declarabele_items.remove(item)
                        
                        if not declarabele_items:
                            break
                
                db.session.commit()
                print("Werkzaamheden gekoppeld aan facturen")
        
        print("Alle testgegevens succesvol toegevoegd!")

if __name__ == "__main__":
    add_test_data()
