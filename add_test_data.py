"""
Script om testgegevens toe te voegen aan de database
"""
from app import app, db
from models import User, Role, RoleEnum, Klant, Medewerker, Opdracht, Werkzaamheid, TimeEntry, Factuur
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, date
import random
import calendar

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
                aanvraagdatum=start_date,
                benodigde_kennis="Python, Flask, JavaScript, HTML, CSS",
                deadline=min((start_date + timedelta(days=random.randint(30, 90))).date(), datetime.now().date()),
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
        db_time_entries = []
        projects = ["Website Development", "App Development", "Server Maintenance", "UI Design", "Database Optimization"]
        opdracht_per_klant = {}
        for opdracht in db_opdrachten:
            opdracht_per_klant.setdefault(opdracht.klant_id, []).append(opdracht)
        # Maak per klant/opdracht alvast een lijst van tijdsregistraties
        time_entries_per_opdracht = {opdracht.id: [] for opdracht in db_opdrachten}
        if not users:
            print("Geen gebruikers gevonden. Tijdsregistraties kunnen niet worden toegevoegd.")
        else:
            for opdracht in db_opdrachten:
                for _ in range(random.randint(3, 6)):
                    user = random.choice(users)
                    entry_date = opdracht.aanvraagdatum + timedelta(days=random.randint(0, 60))
                    if entry_date > datetime.now().date():
                        entry_date = datetime.now().date()
                    hours = random.randint(2, 8)
                    time_entry = TimeEntry(
                        date=entry_date,
                        hours=hours,
                        description=f"Gewerkte uren aan {opdracht.titel}",
                        project=random.choice(projects),
                        user_id=user.id,
                        opdracht_id=opdracht.id,
                        is_billable=True
                    )
                    db.session.add(time_entry)
                    db_time_entries.append(time_entry)
                    time_entries_per_opdracht[opdracht.id].append(time_entry)
            # Voeg ook wat niet-gefactureerde uren toe
            for _ in range(10):
                opdracht = random.choice(db_opdrachten)
                user = random.choice(users)
                entry_date = opdracht.aanvraagdatum + timedelta(days=random.randint(0, 60))
                if entry_date > datetime.now().date():
                    entry_date = datetime.now().date()
                hours = random.randint(2, 8)
                time_entry = TimeEntry(
                    date=entry_date,
                    hours=hours,
                    description=f"Nog niet gefactureerde uren voor {opdracht.titel}",
                    project=random.choice(projects),
                    user_id=user.id,
                    opdracht_id=opdracht.id,
                    is_billable=True
                )
                db.session.add(time_entry)
                db_time_entries.append(time_entry)
        db.session.commit()
        print(f"{len(db_time_entries)} tijdsregistraties toegevoegd")
        
        # 6. Facturen toevoegen
        print("Facturen toevoegen...")
        admin_user = User.query.filter(User.role_id.in_([3, 4])).first()
        if not admin_user:
            admin_user = User.query.first()
        if not admin_user:
            print("Geen gebruikers gevonden. Facturen kunnen niet worden toegevoegd.")
        else:
            db_facturen = []
            facturen_data = []
            facturen_per_jaar = {now.year: 0, now.year-1: 0}
            for jaar in [now.year, now.year-1]:
                for klant in db_klanten:
                    if klant.id not in opdracht_per_klant or not opdracht_per_klant[klant.id]:
                        continue
                    opdrachten = opdracht_per_klant[klant.id]
                    n_facturen = random.randint(1, 2)
                    for i in range(n_facturen):
                        opdracht = random.choice(opdrachten)
                        maand = random.randint(1, 12)
                        dag = random.randint(1, 28)
                        factuur_date = datetime(jaar, maand, dag).date()
                        if factuur_date > datetime.now().date():
                            factuur_date = datetime.now().date()
                        due_date = min(factuur_date + timedelta(days=30), datetime.now().date())
                        factuur_nummer = f"{jaar}{maand:02d}{klant.id:02d}{i+1:02d}"
                        # Realistisch aantal uren en entries
                        totaal_uren = random.choice([12, 16, 24, 32, 40])
                        n_entries = random.randint(2, 6)
                        uren_per_entry = [totaal_uren // n_entries] * n_entries
                        for j in range(totaal_uren % n_entries):
                            uren_per_entry[j] += 1
                        tarief = opdracht.uurtarief or random.choice([85, 95, 110, 125])
                        omschrijvingen = [
                            "Ontwikkeling module X", "Overleg klant", "Bugfixing sprint", "Code review", "Documentatie", "Testen release"
                        ]
                        first_day = date(jaar, maand, 1)
                        last_day = date(jaar, maand, calendar.monthrange(jaar, maand)[1])
                        werkdagen = [first_day + timedelta(days=x) for x in range((last_day - first_day).days + 1)
                                     if (first_day + timedelta(days=x)).weekday() < 5 and (first_day + timedelta(days=x)) <= datetime.now().date()]
                        if len(werkdagen) < n_entries:
                            werkdagen = [first_day] * n_entries
                        else:
                            werkdagen = random.sample(werkdagen, n_entries)
                        gekoppelde_uren = []
                        for j in range(n_entries):
                            te = None
                            beschikbare_uren = [te for te in time_entries_per_opdracht[opdracht.id] if te.invoice_id is None]
                            if beschikbare_uren:
                                te = beschikbare_uren.pop()
                                te.hours = uren_per_entry[j]
                                te.hourly_rate = tarief
                                te.date = werkdagen[j]
                                te.description = random.choice(omschrijvingen)
                            else:
                                te = TimeEntry(
                                    date=werkdagen[j],
                                    hours=uren_per_entry[j],
                                    description=random.choice(omschrijvingen),
                                    project=opdracht.titel,
                                    user_id=random.choice(users).id,
                                    opdracht_id=opdracht.id,
                                    is_billable=True,
                                    hourly_rate=tarief
                                )
                                db.session.add(te)
                                db_time_entries.append(te)
                                time_entries_per_opdracht[opdracht.id].append(te)
                            gekoppelde_uren.append(te)
                        subtotaal = sum([te.hours * tarief for te in gekoppelde_uren])
                        btw_percentage = 21.0
                        btw_bedrag = subtotaal * (btw_percentage / 100)
                        totaal = subtotaal + btw_bedrag
                        # Minstens 1 factuur per klant per jaar betaald
                        betaald = (i == 0)
                        betaaldatum = factuur_date + timedelta(days=random.randint(5, 25)) if betaald else None
                        factuur = Factuur(
                            factuur_nummer=factuur_nummer,
                            klant_id=klant.id,
                            opdracht_id=opdracht.id,
                            datum=factuur_date,
                            vervaldatum=due_date,
                            btw_percentage=btw_percentage,
                            subtotaal=subtotaal,
                            btw_bedrag=btw_bedrag,
                            totaal=totaal,
                            betaald=betaald,
                            betaaldatum=betaaldatum,
                            betalingsvoorwaarden="Betaling binnen 30 dagen na factuurdatum",
                            notities="Testfactuur voor sprint review.",
                            creator_id=admin_user.id
                        )
                        db.session.add(factuur)
                        db_facturen.append((factuur, gekoppelde_uren))
            db.session.commit()  # Commit zodat factuur.id beschikbaar is
            # Koppel uren aan facturen
            for factuur, gekoppelde_uren in db_facturen:
                for te in gekoppelde_uren:
                    te.invoice_id = factuur.id
            db.session.commit()
            # Herbereken subtotaal, btw en totaal op basis van daadwerkelijk gekoppelde uren
            for factuur, _ in db_facturen:
                gekoppelde_uren = TimeEntry.query.filter_by(invoice_id=factuur.id).all()
                subtotaal = sum([te.hours * (te.hourly_rate or 0) for te in gekoppelde_uren])
                factuur.subtotaal = subtotaal
                factuur.btw_bedrag = subtotaal * (factuur.btw_percentage / 100)
                factuur.totaal = factuur.subtotaal + factuur.btw_bedrag
            db.session.commit()
            print(f"{len(db_facturen)} facturen toegevoegd (5 per jaar, 2 jaar)")
        print("Alle testgegevens succesvol toegevoegd!")

if __name__ == "__main__":
    add_test_data()
