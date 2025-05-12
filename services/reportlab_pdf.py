"""
ReportLab PDF Generator Module
"""
import sys
import os
from datetime import datetime
import tempfile
import logging

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

# Configureer een logger
logger = logging.getLogger(__name__)

# Controleer of ReportLab beschikbaar is
REPORTLAB_AVAILABLE = False
try:
    # Import ReportLab
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    
    # Check if all dependencies are available
    if not hasattr(colors, 'black') or not hasattr(colors, 'lightgrey'):
        raise ImportError("ReportLab colors not available")
    if not hasattr(canvas, 'Canvas'):
        raise ImportError("ReportLab Canvas not available")
    
    REPORTLAB_AVAILABLE = True
    logger.info("ReportLab is beschikbaar voor PDF generatie")
except ImportError as e:
    logger.warning(f"ReportLab is niet beschikbaar: {str(e)}")
    logger.warning("Installeer het met: pip install reportlab")

def generate_factuur_pdf(factuur, title="Factuur"):
    """
    Genereert een factuur PDF met ReportLab
    
    Args:
        factuur: Het factuur object
        title: Titel voor het PDF-bestand
        
    Returns:
        tuple: (pdf_data, filename, mimetype)
    """
    # Controleer of ReportLab beschikbaar is
    if not REPORTLAB_AVAILABLE:
        error_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <h1 style="color: #d9534f;">PDF Generatie Fout</h1>
            <p><strong>ReportLab is niet geïnstalleerd. Installeer het met:</strong><br>pip install reportlab</p>
            <p>Installeer het in dezelfde Python-omgeving waarin de applicatie draait.</p>
            <p><a href="javascript:history.back()">Terug naar vorige pagina</a></p>
        </body>
        </html>
        """
        return error_html.encode('utf-8'), f"error_{datetime.now().strftime('%Y%m%d')}.html", 'text/html'
    
    try:
        # Maak een tijdelijke bestandsnaam in de huidige map
        os.makedirs('temp', exist_ok=True)
        pdf_file_path = os.path.join('temp', f"factuur_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        
        # Maak het PDF-document
        doc = SimpleDocTemplate(
            pdf_file_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Container voor de 'Flowable' objecten
        elements = []
        
        # Stijlen
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Center', alignment=1))
        styles.add(ParagraphStyle(name='Right', alignment=2))
        
        # Voeg bedrijfsinfo/logo toe
        elements.append(Paragraph("UrenRegistratie", styles['Title']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Maak een tabel voor de header met bedrijfs- en klantinfo
        if hasattr(factuur, 'klant'):
            klant = factuur.klant
            bedrijfsnaam = klant.bedrijfsnaam if hasattr(klant, 'bedrijfsnaam') else ""
            adres = klant.adres if hasattr(klant, 'adres') else ""
            postcode = klant.postcode if hasattr(klant, 'postcode') else ""
            plaats = klant.plaats if hasattr(klant, 'plaats') else ""
            
            # Klantinfo tabel
            client_data = [
                ["Factuur voor:"],
                [bedrijfsnaam],
                [f"{adres}"],
                [f"{postcode} {plaats}"]
            ]
            
            client_table = Table(client_data, colWidths=[8*cm])
            client_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ]))
            elements.append(client_table)
        
        elements.append(Spacer(1, 1*cm))
        
        # Factuurdetails
        elements.append(Paragraph("Factuur", styles['Heading1']))
        
        # Factuurinfo tabel
        invoice_info = [
            ["Factuurnummer:", getattr(factuur, 'factuur_nummer', 'N/A')],
            ["Datum:", (getattr(factuur, 'datum', datetime.now()) or datetime.now()).strftime('%d-%m-%Y')],
            ["Vervaldatum:", (getattr(factuur, 'vervaldatum', datetime.now()) or datetime.now()).strftime('%d-%m-%Y')],
            ["Betaaldatum:", (getattr(factuur, 'betaaldatum', None) or datetime.now()).strftime('%d-%m-%Y') if factuur.betaald else "-"]
        ]
        
        invoice_table = Table(invoice_info, colWidths=[4*cm, 10*cm])
        invoice_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ]))
        elements.append(invoice_table)
        
        elements.append(Spacer(1, 1*cm))
        
        # Samenvatting van kosten
        summary_data = [
            ["Omschrijving", "Bedrag"],
            ["Subtotaal", f"€ {getattr(factuur, 'subtotaal', 0):.2f}"],
            ["BTW", f"€ {getattr(factuur, 'btw_bedrag', 0):.2f}"],
            ["Totaal", f"€ {getattr(factuur, 'totaal', 0):.2f}"]
        ]
        
        # Add work activities and time entries if available
        if hasattr(factuur, 'werkzaamheden') and factuur.werkzaamheden:
            for werkzaamheid in factuur.werkzaamheden:
                summary_data.append([
                    werkzaamheid.omschrijving,
                    f"€ {werkzaamheid.aantal_uren * werkzaamheid.get_effective_tarief():.2f}"
                ])
        
        if hasattr(factuur, 'time_entries') and factuur.time_entries:
            for entry in factuur.time_entries:
                summary_data.append([
                    entry.description,
                    f"€ {entry.hours * (getattr(factuur.opdracht, 'uurtarief', 0) if hasattr(factuur, 'opdracht') else 0):.2f}"
                ])
        
        summary_table = Table(summary_data, colWidths=[10*cm, 4*cm])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        elements.append(summary_table)
        
        # Betalingsvoorwaarden
        elements.append(Spacer(1, 1*cm))
        betalingsvoorwaarden = getattr(factuur, 'betalingsvoorwaarden', 'Betaling binnen 30 dagen')
        elements.append(Paragraph(f"Betalingsvoorwaarden: {betalingsvoorwaarden}", styles['Normal']))
        
        # Notities
        notities = getattr(factuur, 'notities', '')
        if notities:
            elements.append(Spacer(1, 0.5*cm))
            elements.append(Paragraph("Notities:", styles['Heading3']))
            elements.append(Paragraph(notities, styles['Normal']))
        
        # Bouw de PDF
        doc.build(elements)
        
        # Lees de PDF-inhoud
        with open(pdf_file_path, 'rb') as pdf_content:
            pdf_data = pdf_content.read()
        
        # Ruim het tijdelijke bestand op
        try:
            os.remove(pdf_file_path)
        except:
            pass
        
        # Return de PDF-inhoud
        return pdf_data, f"{title}_{datetime.now().strftime('%Y%m%d')}.pdf", 'application/pdf'
    except Exception as e:
        logger.error(f"Fout bij genereren PDF met ReportLab: {str(e)}")
        # Toon een foutmelding als HTML
        error_html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <h1 style="color: #d9534f;">PDF Generatie Fout</h1>
            <p><strong>Er is een fout opgetreden bij het genereren van de PDF:</strong> {str(e)}</p>
            <p>Controleer of de 'temp' map schrijfbaar is, en of ReportLab correct is geïnstalleerd.</p>
            <p><a href="javascript:history.back()">Terug naar vorige pagina</a></p>
        </body>
        </html>
        """
        return error_html.encode('utf-8'), f"error_{datetime.now().strftime('%Y%m%d')}.html", 'text/html' 