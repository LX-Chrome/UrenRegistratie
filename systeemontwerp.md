# UrenRegistratie - Systeemontwerp Document

## Wireframes (design)

### Login Scherm
- Username/email invoerveld
- Wachtwoord invoerveld
- Login knop
- Wachtwoord vergeten link

### Dashboard
- Overzicht van recente urenregistraties
- Totaaloverzicht uren per project/klant
- Snelle invoermogelijkheid voor nieuwe registraties
- Navigatie naar andere secties

### Tijdregistratie Beheer
- Kalenderweergave van ingevoerde uren
- Lijstweergave met filteropties
- Formulieren voor toevoegen/bewerken/verwijderen tijdregistraties
- Factureerbaar vs. niet-factureerbaar markeren

### Klantbeheer
- Klantenlijst met zoek- en filterfuncties
- Klantdetails weergave
- Formulieren voor toevoegen/bewerken klant
- Opdrachten per klant overzicht

### Facturen Genereren
- Factuur aanmaken formulier
- Factuur voorbeeldweergave
- Tijdregistraties koppelen aan facturen
- Factuurstatus bijhouden

### Beheerdersdashboard
- Gebruikersbeheer
- Roltoewijzing
- Systeeminstellingen

## Ontwerpkeuzes

### Architectuur
De applicatie volgt een typisch Flask MVC (Model-View-Controller) patroon:
- **Models**: SQLAlchemy ORM voor database-interacties
- **Views**: Flask templates voor het renderen van de gebruikersinterface
- **Controllers**: Flask routes voor het afhandelen van requests

### Technologie Stack
- **Backend**: Python met Flask framework
- **Database**: SQLite (eenvoudig upgradebaar naar PostgreSQL/MySQL voor productie)
- **ORM**: SQLAlchemy voor database-abstractie
- **Authenticatie**: Flask-Login voor gebruikerssessiebeheer
- **Frontend**: Bootstrap of vergelijkbaar voor responsive design

### Belangrijke Ontwerpbeslissingen
1. **Rolgebaseerde toegangscontrole**: Het systeem implementeert een uitgebreid RBAC-systeem met vier rollen: Admin, Afdelingshoofd, Verkoop en Medewerker
2. **Gescheiden Gebruiker- en Medewerkermodellen**: Het ontwerp scheidt gebruikersaccounts van medewerkerprofielen, wat flexibiliteit biedt in accountbeheer
3. **Klant-Opdracht-Tijdregistratie Relatie**: Hiërarchische structuur voor het organiseren van werk
4. **Facturatie**: Ingebouwde facturatiecapaciteiten gekoppeld aan tijdregistraties

## Datamodel (ERD)

```
+----------------+     +----------------+     +----------------+
|      User      |     |      Role      |     |   Medewerker   |
+----------------+     +----------------+     +----------------+
| id             |     | id             |     | id             |
| username       |     | name           |     | voornaam       |
| email          |     | description    |     | tussenvoegsel  |
| password_hash  |     +----------------+     | achternaam     |
| role_id        |            ↑               | geboortedatum  |
| is_active      |            |               | functie        |
| created_at     |            |               | werkmail       |
| medewerker_id  |------------+               | kantoorruimte  |
+----------------+                            | created_at     |
       ↑                                      +----------------+
       |                                             ↑
       |                                             |
       +---------------------------------------------+
       |
       |     +----------------+     +----------------+
       |     |   TimeEntry    |     |    Factuur     |
       |     +----------------+     +----------------+
       +---->| id             |     | id             |
       |     | date           |     | factuur_nummer |
       |     | hours          |     | klant_id       |
       |     | description    |     | opdracht_id    |
       |     | project        |     | datum          |
       |     | user_id        |     | vervaldatum    |
       |     | created_at     |     | btw_percentage |
       |     | is_billable    |     | subtotaal      |
       |     | hourly_rate    |     | btw_bedrag     |
       |     | invoice_id     |---->| totaal         |
       |     +----------------+     | betaald        |
       |                            | betaaldatum    |
       |                            | creator_id     |
       +--------------------------->| created_at     |
                                    | updated_at     |
                                    +----------------+
                                           ↑
                                           |
+----------------+     +----------------+  |
|    CheckIn     |     |   Werkzaamheid |  |
+----------------+     +----------------+  |
| id             |     | id             |  |
| user_id        |     | medewerker_id  |  |
| check_in_time  |     | datum          |  |
| status         |     | uren           |  |
| note           |     | beschrijving   |  |
+----------------+     | opdracht_id    |  |
                       | factuur_id     |--+
                       | created_at     |
                       +----------------+
                              ↑
                              |
+----------------+     +----------------+
|     Klant      |     |    Opdracht    |
+----------------+     +----------------+
| id             |     | id             |
| bedrijfsnaam   |     | klant_id       |
| voornaam       |     | titel          |
| tussenvoegsel  |     | omschrijving   |
| achternaam     |     | aanvraagdatum  |
| functie        |     | benodigde_kennis|
| email          |     | deadline       |
| telefoonnummer |     | status         |
| adres          |     | uurtarief      |
| postcode       |     | created_at     |
| plaats         |     +----------------+
| land           |            ↑
| btw_nummer     |            |
| kvk_nummer     |            |
| status         |            |
| created_at     |------------+
+----------------+
```

## Klassendiagram

De applicatie volgt een object-georiënteerde aanpak met SQLAlchemy-modellen. De belangrijkste klassen zijn:

```
+------------------+
|      Model       |
+------------------+
| __tablename__    |
+------------------+
        ↑
        |
 +------+------+------+------+------+------+
 |      |      |      |      |      |      |
 ↓      ↓      ↓      ↓      ↓      ↓      ↓
+------+  +--------+  +----------+  +--------+  +---------+  +----------+  +------------+
| User |  |  Role  |  | Medewerker|  | CheckIn|  | Klant   |  | Opdracht |  | Werkzaamheid|
+------+  +--------+  +----------+  +--------+  +---------+  +----------+  +------------+
| id   |  | id     |  | id       |  | id     |  | id      |  | id       |  | id         |
| ...  |  | ...    |  | ...      |  | ...    |  | ...     |  | ...      |  | ...        |
+------+  +--------+  +----------+  +--------+  +---------+  +----------+  +------------+
   |           ↑           ↑            |           |             ↑              |
   +-----------+-----------+            |           +-------------+              |
                |                       |                         |              |
                v                       v                         v              v
           +----------+           +-----------+             +-----------+
           | TimeEntry|           |  Factuur  |             |  Factuur  |
           +----------+           +-----------+             +-----------+
           | id       |           | id        |             | id        |
           | ...      |           | ...       |             | ...       |
           +----------+           +-----------+             +-----------+
```

## Organogram

Het organogram is beschikbaar als SVG-bestand (`organogram.svg`) en illustreert de hiërarchie van gebruikersrollen in het systeem:

1. **Admin (System Administrator)** - Hoogste niveau met volledige systeemtoegang
2. **Afdelingshoofd (Department Head)** - Rapporteert aan Admin, beheert zowel verkoop als medewerkers
3. **Verkoop (Sales Staff)** - Rapporteert aan Afdelingshoofd, beheert klantrelaties
4. **Medewerker (Regular Employee)** - Rapporteert aan Afdelingshoofd, voert reguliere taken uit

## Use case diagram

```
+---------------------------------------------+
|                UrenRegistratie              |
+---------------------------------------------+
|                                             |
|   +--------+        +---------+             |
|   |        |        |         |             |
|   | Admin  +--------+ Beheer  |             |
|   |        |        | Gebruikers           |
|   +--------+        +---------+             |
|       |                                     |
|       |              +---------+            |
|       +--------------+ Systeem- |            |
|                      | beheer   |            |
|                      +---------+            |
|                                             |
|   +----------------+  +-----------------+   |
|   |                |  |                 |   |
|   | Afdelingshoofd +--+ Medewerkers    |   |
|   |                |  | beheren        |   |
|   +----------------+  +-----------------+   |
|       |                                     |
|       |              +----------------+     |
|       +--------------+ Rapporten      |     |
|       |              | genereren      |     |
|       |              +----------------+     |
|       |                                     |
|       |              +----------------+     |
|       +--------------+ Facturen       |     |
|                      | goedkeuren     |     |
|                      +----------------+     |
|                                             |
|   +--------+        +----------------+      |
|   |        |        |                |      |
|   | Verkoop+--------+ Facturen       |      |
|   |        |        | aanmaken       |      |
|   +--------+        +----------------+      |
|       |                                     |
|       |              +----------------+     |
|       +--------------+ Klanten        |     |
|                      | beheren        |     |
|                      +----------------+     |
|                                             |
|   +------------+    +----------------+      |
|   |            |    |                |      |
|   | Medewerker +----+ Uren           |      |
|   |            |    | registreren    |      |
|   +------------+    +----------------+      |
|       |                                     |
|       |              +----------------+     |
|       +--------------+ Checkin/out    |     |
|                      | registreren    |     |
|                      +----------------+     |
|                                             |
+---------------------------------------------+
```

## Activiteitendiagrammen

### Tijdregistratie Activiteit
```
+----------------+     +----------------+     +----------------+
| Gebruiker logt |     | Selecteer      |     | Vul uren en   |
|     in         |---->| datum/project  |---->| beschrijving  |
+----------------+     +----------------+     +----------------+
                                                     |
                                                     v
+----------------+     +----------------+     +----------------+
| Tijdregistratie|     | Valideer       |     | Controleer als |
| opgeslagen     |<----| invoer         |<----| factureerbaar |
+----------------+     +----------------+     +----------------+
```

### Factuur Genereren Activiteit
```
+----------------+     +----------------+     +----------------+
| Selecteer      |     | Selecteer niet-|     | Definieer     |
| klant/opdracht |---->| gefactureerde  |---->| factuurdetails|
+----------------+     | uren           |     +----------------+
                       +----------------+            |
                                                     v
+----------------+     +----------------+     +----------------+
| Factuur        |     | Genereer       |     | Preview        |
| opgeslagen     |<----| PDF            |<----| factuur        |
+----------------+     +----------------+     +----------------+
```

## Onderbouwing systeemontwerp

### Haalbaarheid

1. **Technische Haalbaarheid**
   - Flask is een bewezen framework voor web-applicaties van deze omvang
   - SQLAlchemy biedt een robuuste ORM-laag die eenvoudig schaalt
   - De gekozen database (SQLite) is perfect voor ontwikkeling en kan later worden gemigreerd naar een robuustere oplossing

2. **Operationele Haalbaarheid**
   - Het systeem is ontworpen om gemakkelijk te onderhouden te zijn met duidelijke scheiding van verantwoordelijkheden
   - De modulaire opbouw maakt toekomstige uitbreidingen eenvoudig
   - Automatisering van facturatie en tijdregistratie vermindert administratieve lasten

3. **Economische Haalbaarheid**
   - Gebruik van open-source technologieën verlaagt de kosten
   - Efficiëntieverbeteringen in urenregistratie en facturatie leiden tot tijdsbesparing
   - Schaalbaar ontwerp maakt groei mogelijk zonder volledige herbouw

### Privacy by Design

1. **Gegevensminimalisatie**
   - Het systeem verzamelt alleen noodzakelijke informatie voor de betreffende functionaliteit
   - Gebruikersgegevens zijn gescheiden van medewerkergegevens voor betere privacy-controle

2. **Toegangscontrole**
   - Rolgebaseerde toegang beperkt informatie tot alleen die gebruikers die het nodig hebben
   - De methodes `can_view_all()`, `can_edit_all()` en `can_create_invoices()` zorgen voor nauwkeurige toegangsrechten

3. **Transparantie**
   - Het systeem houdt bij wie wijzigingen heeft aangebracht (`created_at`, `updated_at`, `creator_id`)
   - Gebruikers kunnen hun eigen gegevens inzien en beheren

### Security by Design

1. **Authenticatie en Autorisatie**
   - Wachtwoorden worden gehasht opgeslagen met Werkzeug's security functies
   - Gebruikerstoegang is beperkt op basis van rollen en specifieke toestemmingen

2. **Data-integriteit**
   - Foreign key constraints zorgen voor referentiële integriteit
   - Indexen verbeteren zowel de prestaties als de gegevensintegriteit

3. **Bescherming tegen veelvoorkomende aanvallen**
   - Flask biedt ingebouwde bescherming tegen CSRF-aanvallen
   - SQLAlchemy's ORM biedt bescherming tegen SQL-injectie
   - Sessie-beheer via Flask-Login voor veilige gebruikerssessies

4. **Audit Trails**
   - Systeem houdt belangrijke acties bij met timestamps
   - Facturen hebben een duidelijke audit trail met creator_id en timestamps voor creatie en wijziging

Door deze principes te volgen, is het UrenRegistratie-systeem ontworpen om betrouwbaar, veilig en privacy-respecterend te zijn, terwijl het tegelijkertijd de functionaliteit biedt die nodig is voor effectief tijd- en factuurbeheer.
