from app import app, db
from models import Factuur, TimeEntry

with app.app_context():
    facturen = Factuur.query.all()
    for factuur in facturen:
        entries = TimeEntry.query.filter_by(invoice_id=factuur.id).all()
        print(f"Factuur {factuur.factuur_nummer} heeft {len(entries)} gekoppelde urenregistraties.")
        for entry in entries:
            print(f"  - {entry.date} | {entry.description} | {entry.hours} uur | user_id={entry.user_id}")
    print("Klaar.") 