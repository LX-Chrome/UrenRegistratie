"""
Routes for invoice management in the UrenRegistratie system.
"""
from datetime import datetime, timedelta
import uuid
import os
from flask import render_template, redirect, url_for, request, flash, make_response, jsonify, send_file
from flask_login import login_required, current_user
from app import app, db
from models import Factuur, Klant, Opdracht, Werkzaamheid, TimeEntry
from auth_helpers import invoice_creation_required, view_all_required, edit_all_required
import pdfkit
from io import BytesIO
from sqlalchemy import func
from services.export_service import ExportService
import io
import xhtml2pdf.pisa as pisa

# Direct PDF generation function using xhtml2pdf
def generate_pdf_from_template(template_name, data, filename):
    """Generate PDF directly using xhtml2pdf"""
    try:
        # Add datetime for templates that need it
        if 'now' not in data:
            data['now'] = datetime.now()
            
        # Try to render the template
        html = render_template(template_name, **data)
        
        # Create a BytesIO object to store the PDF
        result = BytesIO()
        
        # Generate the PDF using xhtml2pdf
        pdf = pisa.CreatePDF(html, dest=result)
        
        if pdf.err:
            app.logger.error(f"Error generating PDF with xhtml2pdf: {pdf.err}")
            return html, f"{filename}.html", "text/html"
        
        # Get the PDF from the BytesIO object
        pdf_data = result.getvalue()
        result.close()
        
        return pdf_data, f"{filename}.pdf", 'application/pdf'
    except Exception as e:
        app.logger.error(f"Error in PDF generation: {str(e)}")
        return None, None, "text/html"

# Invoice routes
@app.route('/facturen')
@login_required
@view_all_required
def facturen():
    """List all invoices"""
    search = request.args.get('search', '')
    facturen_query = Factuur.query
    
    if search:
        facturen_query = facturen_query.join(Klant).filter(
            Factuur.factuur_nummer.contains(search) | 
            Klant.bedrijfsnaam.contains(search)
        )
    
    facturen = facturen_query.order_by(Factuur.datum.desc()).all()
    
    # Add today's date for template comparison (to show overdue invoices)
    today = datetime.now().date()
    
    return render_template('facturen.html', facturen=facturen, search=search, today=today)

@app.route('/factuur/nieuw', methods=['GET', 'POST'])
@login_required
@invoice_creation_required
def nieuwe_factuur():
    """Create a new invoice"""
    if request.method == 'POST':
        try:
            # Generate invoice number (year + month + sequential number)
            now = datetime.now()
            current_year = now.year
            current_month = now.month
            
            # Format: YYYYMMxxxx (e.g., 2025060001)
            base_number = f"{current_year}{current_month:02d}"
            
            # Find the last invoice number with this prefix
            last_invoice = Factuur.query.filter(
                Factuur.factuur_nummer.like(f"{base_number}%")
            ).order_by(Factuur.factuur_nummer.desc()).first()
            
            if last_invoice:
                # Extract the sequence number and increment
                seq_num = int(last_invoice.factuur_nummer[-4:]) + 1
            else:
                seq_num = 1
                
            factuur_nummer = f"{base_number}{seq_num:04d}"
            
            # Calculate due date (usually 30 days from invoice date)
            invoice_date = datetime.strptime(request.form['datum'], '%Y-%m-%d').date()
            due_days = int(request.form.get('payment_terms_days', 30))
            due_date = invoice_date + timedelta(days=due_days)
            
            # Get the client and assignment
            klant_id = int(request.form['klant_id'])
            opdracht_id = request.form.get('opdracht_id')
            if opdracht_id:
                opdracht_id = int(opdracht_id)
            
            # Calculate invoice amounts
            subtotal = float(request.form['subtotaal'])
            vat_percentage = float(request.form['btw_percentage'])
            vat_amount = subtotal * (vat_percentage / 100)
            total = subtotal + vat_amount
            
            # Create the invoice
            new_invoice = Factuur(
                factuur_nummer=factuur_nummer,
                klant_id=klant_id,
                opdracht_id=opdracht_id,
                datum=invoice_date,
                vervaldatum=due_date,
                btw_percentage=vat_percentage,
                subtotaal=subtotal,
                btw_bedrag=vat_amount,
                totaal=total,
                betalingsvoorwaarden=request.form.get('betalingsvoorwaarden', 'Betaling binnen 30 dagen'),
                notities=request.form.get('notities'),
                creator_id=current_user.id
            )
            
            db.session.add(new_invoice)
            db.session.commit()
            
            # Get selected billable items
            if 'werkzaamheid_ids' in request.form:
                werkzaamheid_ids = request.form.getlist('werkzaamheid_ids')
                for w_id in werkzaamheid_ids:
                    werkzaamheid = Werkzaamheid.query.get(int(w_id))
                    if werkzaamheid:
                        werkzaamheid.factuur_id = new_invoice.id
                        
            if 'time_entry_ids' in request.form:
                time_entry_ids = request.form.getlist('time_entry_ids')
                for te_id in time_entry_ids:
                    time_entry = TimeEntry.query.get(int(te_id))
                    if time_entry:
                        time_entry.invoice_id = new_invoice.id
            
            db.session.commit()
            flash('Factuur succesvol aangemaakt', 'success')
            return redirect(url_for('bekijk_factuur', factuur_id=new_invoice.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Fout bij aanmaken factuur: {str(e)}', 'danger')
            app.logger.error(f"Error creating invoice: {str(e)}")
    
    # Get all clients and assignments for the form
    klanten = Klant.query.filter_by(status='actief').order_by(Klant.bedrijfsnaam).all()
    opdrachten = Opdracht.query.filter_by(status='open').order_by(Opdracht.aanvraagdatum.desc()).all()
    
    # Get unbilled activities and time entries
    unbilled_werkzaamheden = Werkzaamheid.query.filter_by(factuur_id=None, is_declarabel=True).all()
    unbilled_time_entries = TimeEntry.query.filter_by(invoice_id=None, is_billable=True).all()
    
    return render_template(
        'factuur_form.html', 
        klanten=klanten, 
        opdrachten=opdrachten,
        werkzaamheden=unbilled_werkzaamheden,
        time_entries=unbilled_time_entries,
        factuur=None,
        today=datetime.now().date()
    )

@app.route('/factuur/<int:factuur_id>')
@login_required
@view_all_required
def bekijk_factuur(factuur_id):
    """View a specific invoice"""
    factuur = Factuur.query.get_or_404(factuur_id)
    # Add today's date for template comparison (to show overdue invoices)
    today = datetime.now().date()
    return render_template('factuur_detail.html', factuur=factuur, today=today)

@app.route('/factuur/<int:factuur_id>/bewerk', methods=['GET', 'POST'])
@login_required
@edit_all_required
def bewerk_factuur(factuur_id):
    """Edit an existing invoice"""
    factuur = Factuur.query.get_or_404(factuur_id)
    
    # Don't allow editing paid invoices
    if factuur.betaald:
        flash('Betaalde facturen kunnen niet gewijzigd worden', 'warning')
        return redirect(url_for('bekijk_factuur', factuur_id=factuur.id))
    
    if request.method == 'POST':
        try:
            # Update invoice details
            factuur.datum = datetime.strptime(request.form['datum'], '%Y-%m-%d').date()
            
            # Recalculate due date based on payment terms
            due_days = int(request.form.get('payment_terms_days', 30))
            factuur.vervaldatum = factuur.datum + timedelta(days=due_days)
            
            # Update other fields
            factuur.btw_percentage = float(request.form['btw_percentage'])
            factuur.subtotaal = float(request.form['subtotaal'])
            factuur.btw_bedrag = factuur.subtotaal * (factuur.btw_percentage / 100)
            factuur.totaal = factuur.subtotaal + factuur.btw_bedrag
            factuur.betalingsvoorwaarden = request.form.get('betalingsvoorwaarden')
            factuur.notities = request.form.get('notities')
            
            # Update payment status if provided
            if 'betaald' in request.form:
                factuur.betaald = request.form['betaald'] == 'true'
                if factuur.betaald and not factuur.betaaldatum:
                    factuur.betaaldatum = datetime.now().date()
            
            db.session.commit()
            flash('Factuur succesvol bijgewerkt', 'success')
            return redirect(url_for('bekijk_factuur', factuur_id=factuur.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Fout bij bijwerken factuur: {str(e)}', 'danger')
            app.logger.error(f"Error updating invoice: {str(e)}")
    
    # Add today's date for template comparison
    today = datetime.now().date()
    
    # Get all clients and assignments for the form
    klanten = Klant.query.order_by(Klant.bedrijfsnaam).all()
    opdrachten = Opdracht.query.order_by(Opdracht.aanvraagdatum.desc()).all()
    
    # Get all billable items, both billed to this invoice and unbilled
    werkzaamheden = Werkzaamheid.query.filter(
        (Werkzaamheid.factuur_id == factuur.id) | 
        (Werkzaamheid.factuur_id == None)
    ).filter_by(is_declarabel=True).all()
    
    time_entries = TimeEntry.query.filter(
        (TimeEntry.invoice_id == factuur.id) |
        (TimeEntry.invoice_id == None)
    ).filter_by(is_billable=True).all()
    
    return render_template(
        'factuur_form.html', 
        factuur=factuur,
        klanten=klanten, 
        opdrachten=opdrachten,
        werkzaamheden=werkzaamheden,
        time_entries=time_entries,
        today=today
    )

@app.route('/factuur/<int:factuur_id>/delete', methods=['POST'])
@login_required
@edit_all_required
def delete_factuur(factuur_id):
    """Delete an invoice"""
    factuur = Factuur.query.get_or_404(factuur_id)
    
    # Don't allow deleting paid invoices
    if factuur.betaald:
        flash('Betaalde facturen kunnen niet verwijderd worden', 'warning')
        return redirect(url_for('bekijk_factuur', factuur_id=factuur.id))
    
    try:
        # Unlink all related billable items
        for werkzaamheid in factuur.werkzaamheden:
            werkzaamheid.factuur_id = None
            
        for time_entry in factuur.time_entries:
            time_entry.invoice_id = None
        
        db.session.delete(factuur)
        db.session.commit()
        flash('Factuur succesvol verwijderd', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fout bij verwijderen factuur: {str(e)}', 'danger')
        app.logger.error(f"Error deleting invoice: {str(e)}")
    
    return redirect(url_for('facturen'))

@app.route('/factuur/<int:factuur_id>/pdf')
@login_required
@view_all_required
def factuur_pdf(factuur_id):
    """Generate a PDF of the invoice"""
    factuur = Factuur.query.get_or_404(factuur_id)
    
    try:
        # Prepare data for the template
        data = {'factuur': factuur}
        
        # Generate PDF directly using xhtml2pdf
        pdf_data, filename, mime_type = generate_pdf_from_template("factuur_pdf.html", data, f"Factuur_{factuur.factuur_nummer}")
            
        # If we failed to generate a PDF, show an error
        if not pdf_data:
            flash('Fout bij genereren PDF.', 'danger')
            return redirect(url_for('bekijk_factuur', factuur_id=factuur.id))
            
        # Prepare response
        response = make_response(pdf_data)
        response.headers['Content-Type'] = mime_type
        response.headers['Content-Disposition'] = f'inline; filename={filename}'
        
        return response
    except Exception as e:
        flash(f'Fout bij genereren PDF: {str(e)}', 'danger')
        return redirect(url_for('bekijk_factuur', factuur_id=factuur.id))

@app.route('/factuur/<int:factuur_id>/mark_paid', methods=['POST'])
@login_required
@edit_all_required
def mark_invoice_paid(factuur_id):
    """Mark an invoice as paid"""
    factuur = Factuur.query.get_or_404(factuur_id)
    
    try:
        factuur.betaald = True
        factuur.betaaldatum = datetime.now().date()
        db.session.commit()
        flash('Factuur gemarkeerd als betaald', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fout bij markeren factuur als betaald: {str(e)}', 'danger')
        app.logger.error(f"Error marking invoice as paid: {str(e)}")
    
    return redirect(url_for('bekijk_factuur', factuur_id=factuur.id))

@app.route('/api/facturen/stats')
@login_required
@view_all_required
def api_facturen_stats():
    """API endpoint for invoice statistics"""
    try:
        # Calculate total invoiced amount this year
        current_year = datetime.now().year
        yearly_revenue = Factuur.get_jaaropbrengst(current_year)
        
        # Calculate total unpaid amount
        unpaid_total = db.session.query(
            func.sum(Factuur.totaal)
        ).filter(Factuur.betaald == False).scalar() or 0
        
        # Count invoices by status
        total_invoices = Factuur.query.count()
        paid_invoices = Factuur.query.filter_by(betaald=True).count()
        unpaid_invoices = total_invoices - paid_invoices
        
        # Get monthly revenue for the current year
        monthly_revenue = db.session.query(
            func.extract('month', Factuur.datum).label('month'),
            func.sum(Factuur.totaal).label('revenue')
        ).filter(
            func.extract('year', Factuur.datum) == current_year,
            Factuur.betaald == True
        ).group_by('month').all()
        
        # Format for chart display
        months = [0] * 12  # Initialize with zeros
        for month, revenue in monthly_revenue:
            months[int(month)-1] = float(revenue)
        
        return jsonify({
            'yearly_revenue': yearly_revenue,
            'unpaid_total': unpaid_total,
            'total_invoices': total_invoices,
            'paid_invoices': paid_invoices,
            'unpaid_invoices': unpaid_invoices,
            'monthly_revenue': months
        })
    except Exception as e:
        app.logger.error(f"Error getting invoice stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/facturen/export/<format>')
@login_required
@view_all_required
def export_facturen(format):
    """Export invoices data in various formats"""
    try:
        facturen = Factuur.query.order_by(Factuur.datum.desc()).all()
        
        if format == 'pdf':
            # Use the PDF template for invoices
            data = {
                'facturen': facturen,
                'title': 'Facturen Overzicht',
                'now': datetime.now(),
            }
            
            # Use direct PDF generation with xhtml2pdf
            content, filename, mimetype = generate_pdf_from_template("reports/pdf_facturen.html", data, 'facturen_overzicht')
            
            # Check if PDF generation failed
            if not content:
                flash('Fout bij genereren PDF.', 'danger')
                return redirect(url_for('facturen'))
        else:
            # For Excel and CSV, prepare the data rows
            headers = ['Nummer', 'Datum', 'Vervaldatum', 'Klant', 'Bedrag', 'BTW', 'Totaal', 'Status']
            rows = []
            
            for factuur in facturen:
                status = "Betaald" if factuur.betaald else "Onbetaald"
                rows.append([
                    factuur.factuur_nummer,
                    factuur.datum.strftime('%d-%m-%Y'),
                    factuur.vervaldatum.strftime('%d-%m-%Y'),
                    factuur.klant.bedrijfsnaam,
                    f"{factuur.subtotaal:.2f}",
                    f"{factuur.btw_bedrag:.2f}",
                    f"{factuur.totaal:.2f}",
                    status
                ])
            
            if format == 'excel':
                content, filename, mimetype = ExportService.to_excel(rows, headers, 'facturen')
            else:  # csv
                content, filename, mimetype = ExportService.to_csv(rows, headers, 'facturen')
        
        # Prepare response
        return send_file(
            io.BytesIO(content),
            mimetype=mimetype,
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f'Fout bij exporteren facturen: {str(e)}', 'danger')
        return redirect(url_for('facturen'))
