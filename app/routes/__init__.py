from app.routes.routes import (
    index, login, logout, dashboard,
    add_time_entry, time_entries, edit_time_entry, delete_time_entry,
    add_check_in, check_ins, edit_check_in, delete_check_in,
    clients, add_client, edit_client, view_client,
    assignments, add_assignment, edit_assignment, view_assignment,
    reports, api_time_entries
)

from app.routes.routes_invoices import (
    invoices, add_invoice, edit_invoice, view_invoice,
    generate_invoice_pdf
)

from app.routes.routes_reports import (
    monthly_report, yearly_report, client_report,
    export_monthly_report, export_yearly_report, export_client_report
)
