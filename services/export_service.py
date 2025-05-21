import csv
import io
from datetime import datetime
import xlsxwriter
from flask import render_template, current_app
import os
import sys
import subprocess
import tempfile
import logging

# Configureer standaard logging voor gebruik buiten applicatiecontext
logger = logging.getLogger('export_service')

# Import ReportLab first (pure Python PDF generation)
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    REPORTLAB_AVAILABLE = True
    logger.info("ReportLab is available for PDF generation")
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab is NOT available - please run: pip install reportlab")

# Import WeasyPrint if available - DISABLED due to GTK dependencies issues
# try:
#     from weasyprint import HTML, CSS
#     from weasyprint.text.fonts import FontConfiguration
#     WEASYPRINT_AVAILABLE = True
#     logger.info("WeasyPrint is available for PDF generation")
# except ImportError:
if True:  # Force the exception branch
    WEASYPRINT_AVAILABLE = False
    logger.warning("WeasyPrint is NOT available")

# Disable pdfkit since we won't be using wkhtmltopdf
PDFKIT_AVAILABLE = False
logger.info("Using ReportLab for PDF generation instead of pdfkit")

class ExportService:
    @staticmethod
    def to_pdf(template_name, data, title):
        """Generate PDF from template"""
        try:
            # Add the current datetime to the template data
            data['now'] = datetime.now()
            
            # First try with the exact template name
            try:
                html = render_template(template_name, **data)
                logger.info(f"Using template: {template_name}")
            except Exception as template_error:
                logger.warning(f"Template error with {template_name}: {str(template_error)}")
                # Then try PDF-specific template
                pdf_template = f"pdf_{template_name}"
                try:
                    html = render_template(pdf_template, **data)
                    logger.info(f"Using PDF template: {pdf_template}")
                except Exception as pdf_template_error:
                    logger.warning(f"PDF template error: {str(pdf_template_error)}")
                    # Last try factuur_pdf.html which we know exists
                    try:
                        html = render_template("factuur_pdf.html", **data)
                        logger.info(f"Using fallback template: factuur_pdf.html")
                    except Exception as fallback_error:
                        raise Exception(f"Could not find any suitable template: {str(fallback_error)}")

            # Try ReportLab first (direct PDF generation without HTML)
            if REPORTLAB_AVAILABLE and 'factuur' in data:
                try:
                    logger.info("Trying PDF generation with ReportLab")
                    
                    # Create a temporary file for the PDF
                    pdf_file_path = os.path.join(os.getcwd(), 'temp', f"output_reportlab_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
                    
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(pdf_file_path), exist_ok=True)
                    
                    # Get factuur data
                    factuur = data['factuur']
                    
                    # Create the PDF document
                    doc = SimpleDocTemplate(
                        pdf_file_path,
                        pagesize=A4,
                        rightMargin=2*cm,
                        leftMargin=2*cm,
                        topMargin=2*cm,
                        bottomMargin=2*cm
                    )
                    
                    # Container for the 'Flowable' objects
                    elements = []
                    
                    # Styles
                    styles = getSampleStyleSheet()
                    styles.add(ParagraphStyle(name='Center', alignment=1))
                    styles.add(ParagraphStyle(name='Right', alignment=2))
                    
                    # Add company info/logo
                    elements.append(Paragraph("UrenRegistratie", styles['Title']))
                    elements.append(Spacer(1, 0.5*cm))
                    
                    # Create a table for the header with company and client info
                    if hasattr(factuur, 'klant'):
                        klant = factuur.klant
                        bedrijfsnaam = klant.bedrijfsnaam if hasattr(klant, 'bedrijfsnaam') else ""
                        adres = klant.adres if hasattr(klant, 'adres') else ""
                        postcode = klant.postcode if hasattr(klant, 'postcode') else ""
                        plaats = klant.plaats if hasattr(klant, 'plaats') else ""
                        
                        # Client info table
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
                    
                    # Invoice details
                    elements.append(Paragraph("Factuur", styles['Heading1']))
                    
                    # Invoice info table
                    invoice_info = [
                        ["Factuurnummer:", getattr(factuur, 'factuur_nummer', 'N/A')],
                        ["Datum:", getattr(factuur, 'datum', datetime.now()).strftime('%d-%m-%Y')],
                        ["Vervaldatum:", getattr(factuur, 'vervaldatum', datetime.now()).strftime('%d-%m-%Y')],
                    ]
                    
                    invoice_table = Table(invoice_info, colWidths=[4*cm, 10*cm])
                    invoice_table.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ]))
                    elements.append(invoice_table)
                    
                    elements.append(Spacer(1, 1*cm))
                    
                    # Summary of costs
                    summary_data = [
                        ["Omschrijving", "Bedrag"],
                        ["Subtotaal", f"€ {getattr(factuur, 'subtotaal', 0):.2f}"],
                        ["BTW", f"€ {getattr(factuur, 'btw_bedrag', 0):.2f}"],
                        ["Totaal", f"€ {getattr(factuur, 'totaal', 0):.2f}"]
                    ]
                    
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
                    
                    # Payment terms
                    elements.append(Spacer(1, 1*cm))
                    if hasattr(factuur, 'betalingsvoorwaarden'):
                        elements.append(Paragraph(f"Betalingsvoorwaarden: {factuur.betalingsvoorwaarden}", styles['Normal']))
                    
                    # Notes
                    if hasattr(factuur, 'notities') and factuur.notities:
                        elements.append(Spacer(1, 0.5*cm))
                        elements.append(Paragraph("Notities:", styles['Heading3']))
                        elements.append(Paragraph(factuur.notities, styles['Normal']))
                    
                    # Build the PDF
                    doc.build(elements)
                    
                    # Read the PDF content
                    with open(pdf_file_path, 'rb') as pdf_content:
                        pdf_data = pdf_content.read()
                    
                    # Log success
                    logger.info(f"PDF successfully generated with ReportLab: {pdf_file_path}")
                    
                    # Clean up the temporary file
                    try:
                        os.remove(pdf_file_path)
                    except Exception as cleanup_error:
                        logger.warning(f"Could not clean up PDF file: {str(cleanup_error)}")
                    
                    # Return the PDF content
                    return pdf_data, f"{title}_{datetime.now().strftime('%Y%m%d')}.pdf", 'application/pdf'
                except Exception as reportlab_error:
                    logger.warning(f"ReportLab error: {str(reportlab_error)}")
                    # Continue to other approaches
            
            # Try WeasyPrint if available (pure Python solution, no external executable needed)
            if WEASYPRINT_AVAILABLE:
                try:
                    logger.info("Trying PDF generation with WeasyPrint")
                    # Create a PDF with WeasyPrint
                    font_config = FontConfiguration()
                    html_doc = HTML(string=html)
                    
                    # Create a temporary file for the PDF
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
                        pdf_file_path = pdf_file.name
                    
                    # Generate the PDF
                    html_doc.write_pdf(pdf_file_path, font_config=font_config)
                    
                    # Read the PDF content
                    with open(pdf_file_path, 'rb') as pdf_content:
                        pdf_data = pdf_content.read()
                    
                    # Clean up the temporary file
                    os.remove(pdf_file_path)
                    
                    # Return the PDF content
                    return pdf_data, f"{title}_{datetime.now().strftime('%Y%m%d')}.pdf", 'application/pdf'
                except Exception as weasyprint_error:
                    logger.warning(f"WeasyPrint error: {str(weasyprint_error)}")
                    # Continue to wkhtmltopdf approach
            
            # If all Python-based approaches failed, try the wkhtmltopdf approach if pdfkit is available
            if not PDFKIT_AVAILABLE:
                logger.error("Cannot generate PDF: pdfkit is not available and all other methods failed")
                raise Exception("PDF generation failed: pdfkit is not installed and all other methods failed")
                
            # Configure pdfkit options
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': 'UTF-8',
                'no-outline': None,
                'quiet': ''
            }
            
            # On Windows, use direct subprocess approach first
            if os.name == 'nt':
                # Use the known working path from debug info
                wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
                if os.path.exists(wkhtmltopdf_path) and os.access(wkhtmltopdf_path, os.X_OK):
                    logger.info(f"Using hardcoded wkhtmltopdf path with direct subprocess: {wkhtmltopdf_path}")

                    # Use subprocess directly - more reliable than pdfkit on Windows
                    # Use the current working directory for temporary files to avoid permission issues
                    temp_dir = os.path.join(os.getcwd(), 'temp')
                    if not os.path.exists(temp_dir):
                        try:
                            os.makedirs(temp_dir)
                        except:
                            # Fall back to system temp directory if we can't create our own
                            temp_dir = tempfile.gettempdir()
                    
                    # Create temporary HTML file in the directory we can write to
                    html_file_path = os.path.join(temp_dir, f"input_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html")
                    with open(html_file_path, 'w', encoding='utf-8') as html_file:
                        html_file.write(html)
                    
                    # The PDF file also needs to be in a directory we can write to
                    pdf_file_path = os.path.join(temp_dir, f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
                    
                    try:
                        # Try with a simplified command first, with minimal options
                        cmd = [
                            wkhtmltopdf_path,
                            '--quiet',
                            html_file_path, pdf_file_path
                        ]
                        
                        logger.info(f"Running simplified command: {' '.join(cmd)}")
                        
                        # Execute the command
                        subprocess_result = subprocess.run(
                            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30
                        )
                        
                        if subprocess_result.returncode == 0:
                            if os.path.exists(pdf_file_path) and os.path.getsize(pdf_file_path) > 0:
                                with open(pdf_file_path, 'rb') as pdf_content:
                                    pdf_data = pdf_content.read()
                                return pdf_data, f"{title}_{datetime.now().strftime('%Y%m%d')}.pdf", 'application/pdf'
                        
                        # If simplified command failed, try another approach
                        logger.info("Simplified command failed, trying with cmd.exe /c")
                        
                        # Use cmd.exe /c to execute command (helps with Windows permissions sometimes)
                        full_cmd = f'cmd.exe /c "{wkhtmltopdf_path}" --quiet "{html_file_path}" "{pdf_file_path}"'
                        os.system(full_cmd)
                        
                        if os.path.exists(pdf_file_path) and os.path.getsize(pdf_file_path) > 0:
                            with open(pdf_file_path, 'rb') as pdf_content:
                                pdf_data = pdf_content.read()
                            return pdf_data, f"{title}_{datetime.now().strftime('%Y%m%d')}.pdf", 'application/pdf'
                        
                        # If that still fails, give detailed error info
                        stderr_output = subprocess_result.stderr.decode('utf-8', errors='ignore').strip()
                        stdout_output = subprocess_result.stdout.decode('utf-8', errors='ignore').strip()
                        logger.error(f"All wkhtmltopdf approaches failed.")
                        logger.error(f"STDERR: {stderr_output}")
                        logger.error(f"STDOUT: {stdout_output}")
                        
                        # Try one more approach using environment variables for path (important for wkhtmltopdf)
                        logger.info("Trying approach with environment variable PATH")
                        my_env = os.environ.copy()
                        # Add wkhtmltopdf directory to PATH
                        my_env["PATH"] = os.path.dirname(wkhtmltopdf_path) + os.pathsep + my_env.get("PATH", "")
                        
                        # Use direct call to wkhtmltopdf with updated PATH
                        cmd = [
                            os.path.basename(wkhtmltopdf_path),  # Just the executable name
                            '--quiet',
                            html_file_path, pdf_file_path
                        ]
                        
                        logger.info(f"Running with PATH environment: {' '.join(cmd)}")
                        
                        subprocess_result = subprocess.run(
                            cmd, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            timeout=30,
                            env=my_env,
                            cwd=os.path.dirname(wkhtmltopdf_path)  # Run from wkhtmltopdf directory
                        )
                        
                        if subprocess_result.returncode == 0 and os.path.exists(pdf_file_path) and os.path.getsize(pdf_file_path) > 0:
                            with open(pdf_file_path, 'rb') as pdf_content:
                                pdf_data = pdf_content.read()
                            return pdf_data, f"{title}_{datetime.now().strftime('%Y%m%d')}.pdf", 'application/pdf'
                        
                        raise Exception(f"All wkhtmltopdf approaches failed, access denied error. Please run the application with administrator rights.")
                        
                    except Exception as e:
                        logger.error(f"Error running wkhtmltopdf subprocess: {str(e)}")
                        raise
                    finally:
                        # Clean up temporary files
                        if os.path.exists(html_file_path):
                            try:
                                os.remove(html_file_path)
                            except:
                                pass
                        if os.path.exists(pdf_file_path):
                            try:
                                os.remove(pdf_file_path)
                            except:
                                pass
            
            # If we're not on Windows or the hardcoded path didn't work, try the regular approach
            wkhtmltopdf_path = ExportService._find_wkhtmltopdf()
            
            # Generate PDF with configuration if path found, otherwise use default
            if wkhtmltopdf_path:
                logger.info(f"Using wkhtmltopdf from: {wkhtmltopdf_path}")
                config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                pdf = pdfkit.from_string(html, False, options=options, configuration=config)
            else:
                # Try using PATH if we didn't find it explicitly
                logger.info("No explicit path found for wkhtmltopdf, trying from PATH")
                pdf = pdfkit.from_string(html, False, options=options)
                
            return pdf, f"{title}_{datetime.now().strftime('%Y%m%d')}.pdf", 'application/pdf'
            
        except Exception as e:
            logger.error(f"PDF generation error: {str(e)}")
            
            # Get debug info about wkhtmltopdf search paths
            debug_info = "<h3>Debug informatie:</h3><ul>"
            # List paths that were checked
            if os.name == 'nt':  # Windows
                debug_paths = [
                    r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
                    r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
                ]
            elif sys.platform == 'darwin':  # macOS
                debug_paths = [
                    '/usr/local/bin/wkhtmltopdf',
                    '/opt/homebrew/bin/wkhtmltopdf',
                    '/usr/bin/wkhtmltopdf',
                ]
            else:  # Linux/Unix
                debug_paths = [
                    '/usr/bin/wkhtmltopdf',
                    '/usr/local/bin/wkhtmltopdf',
                    '/opt/bin/wkhtmltopdf',
                ]
                
            for path in debug_paths:
                if os.path.exists(path):
                    exists_text = "BESTAAT"
                    if os.access(path, os.X_OK):
                        executable_text = ", UITVOERBAAR"
                    else:
                        executable_text = ", NIET UITVOERBAAR"
                    debug_info += f"<li>{path}: {exists_text}{executable_text}</li>"
                else:
                    debug_info += f"<li>{path}: BESTAAT NIET</li>"
            
            debug_info += "</ul>"
            
            # Add WeasyPrint and ReportLab availability info
            debug_info += f"<p>WeasyPrint beschikbaar: {'JA' if WEASYPRINT_AVAILABLE else 'NEE'}</p>"
            debug_info += f"<p>ReportLab beschikbaar: {'JA' if REPORTLAB_AVAILABLE else 'NEE'}</p>"
            
            # Add available templates info
            debug_info += "<h3>Template debug:</h3><ul>"
            
            # Create dummy test data for template checking
            test_data = data.copy() if data else {}
            if 'factuur' not in test_data:
                # Create a minimal dummy factuur object with required attributes
                class DummyFactuur:
                    def __init__(self):
                        self.factuur_nummer = "TEST123456"
                        self.datum = datetime.now()
                        self.vervaldatum = datetime.now()
                        self.betaald = False
                        self.betaaldatum = None
                        self.subtotaal = 100.0
                        self.btw_percentage = 21.0
                        self.btw_bedrag = 21.0
                        self.totaal = 121.0
                        self.betalingsvoorwaarden = "Betaling binnen 30 dagen"
                        self.notities = "Test notitie"
                        self.klant = DummyKlant()
                
                class DummyKlant:
                    def __init__(self):
                        self.bedrijfsnaam = "Test Bedrijf"
                        self.voornaam = "Test"
                        self.tussenvoegsel = ""
                        self.achternaam = "Klant"
                        self.adres = "Teststraat 123"
                        self.postcode = "1234 AB"
                        self.plaats = "Teststad"
                        self.btw_nummer = "NL123456789B01"
                        self.kvk_nummer = "12345678"
                
                test_data['factuur'] = DummyFactuur()
            
            templates_to_check = ["factuur.html", "factuur_pdf.html", "pdf_factuur.html"]
            for t in templates_to_check:
                try:
                    render_template(t, **test_data)
                    debug_info += f"<li>Template {t}: BESTAAT</li>"
                except Exception as te:
                    debug_info += f"<li>Template {t}: FOUT - {str(te)}</li>"
            
            debug_info += "</ul>"
            
            # If PDF generation fails, return an error page with more helpful instructions
            error_message = str(e)
            access_denied = False
            
            # Check if this is an access denied error
            if "access denied" in error_message.lower() or "access is denied" in error_message.lower() or "WinError 5" in error_message:
                access_denied = True
                access_solution = """
                <h3>Oplossing voor toegangsrechtenprobleem:</h3>
                <ol>
                    <li>Start de applicatie als administrator</li>
                    <li>Of wijzig de rechten van wkhtmltopdf zodat alle gebruikers er toegang toe hebben:
                        <ol>
                            <li>Ga naar <code>C:\\Program Files\\wkhtmltopdf\\bin\\</code></li>
                            <li>Klik met de rechtermuisknop op <code>wkhtmltopdf.exe</code></li>
                            <li>Kies Eigenschappen</li>
                            <li>Ga naar het tabblad Beveiliging</li>
                            <li>Klik op Bewerken</li>
                            <li>Zorg dat de gebruiker waaronder de applicatie draait voldoende rechten heeft (Lezen & Uitvoeren)</li>
                        </ol>
                    </li>
                    <li>Of installeer een van deze Python-pakketten als alternatief voor wkhtmltopdf:
                        <pre>pip install reportlab       # Direct PDF generatie zonder HTML
pip install weasyprint       # HTML naar PDF conversie</pre>
                        Probeer daarna opnieuw, de applicatie zou dan geen wkhtmltopdf meer nodig moeten hebben.
                    </li>
                </ol>
                """
            else:
                access_solution = ""
            
            html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h1 style="color: #d9534f;">PDF Generatie Fout</h1>
                <p><strong>Er is een fout opgetreden bij het genereren van de PDF:</strong> {error_message}</p>
                
                <h2>Oplossing</h2>
                <p>Er kan een probleem zijn met het template of met wkhtmltopdf.</p>
                
                <h3>Mogelijke oorzaken:</h3>
                <ul>
                    <li><strong>Toegangsrechten:</strong> De applicatie heeft onvoldoende rechten om wkhtmltopdf uit te voeren of bestanden te schrijven.</li>
                    <li><strong>wkhtmltopdf niet gevonden:</strong> Controleer of wkhtmltopdf correct is geïnstalleerd.</li>
                    <li><strong>Template probleem:</strong> Controleer of de juiste templates bestaan.</li>
                </ul>
                
                {access_solution if access_denied else ""}
                
                <h3>Installatie instructies voor wkhtmltopdf:</h3>
                <ol>
                    <li><a href="https://wkhtmltopdf.org/downloads.html" target="_blank">Download wkhtmltopdf van de officiële website</a></li>
                    <li>Installeer het programma met de standaard instellingen</li>
                </ol>
                
                {debug_info}
                
                <p><a href="javascript:history.back()">Terug naar vorige pagina</a></p>
            </body>
            </html>
            """
            return html.encode('utf-8'), f"error_{datetime.now().strftime('%Y%m%d')}.html", 'text/html'

    @staticmethod
    def _find_wkhtmltopdf():
        """Find the wkhtmltopdf executable on the system"""
        # Possible paths based on operating system
        if os.name == 'nt':  # Windows
            possible_paths = [
                r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
                r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe',
                # Add more potential Windows paths
            ]
        elif sys.platform == 'darwin':  # macOS
            possible_paths = [
                '/usr/local/bin/wkhtmltopdf',
                '/opt/homebrew/bin/wkhtmltopdf',
                '/usr/bin/wkhtmltopdf',
                # Add more potential macOS paths
            ]
        else:  # Linux/Unix
            possible_paths = [
                '/usr/bin/wkhtmltopdf',
                '/usr/local/bin/wkhtmltopdf',
                '/opt/bin/wkhtmltopdf',
                # Add more potential Linux paths
            ]
        
        # Check existence of each possible path
        for path in possible_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
                
        # Try to find it using the 'where' command on Windows or 'which' on Unix
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['where', 'wkhtmltopdf'], capture_output=True, text=True, check=False)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip().split('\n')[0]
            else:  # Unix/Linux/macOS
                result = subprocess.run(['which', 'wkhtmltopdf'], capture_output=True, text=True, check=False)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
        except Exception as e:
            logger.warning(f"Error finding wkhtmltopdf in PATH: {str(e)}")
            
        return None

    @staticmethod
    def to_excel(data, headers, title):
        """Generate Excel file from data"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # Add headers with formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#2C3E50',
            'font_color': 'white',
            'border': 1
        })
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)

        # Add data
        row_format = workbook.add_format({'border': 1})
        for row_idx, row in enumerate(data, start=1):
            for col_idx, value in enumerate(row):
                worksheet.write(row_idx, col_idx, value, row_format)

        # Auto-adjust columns
        for col_idx in range(len(headers)):
            worksheet.set_column(col_idx, col_idx, 15)

        workbook.close()
        output.seek(0)
        
        return output.getvalue(), f"{title}_{datetime.now().strftime('%Y%m%d')}.xlsx", 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    @staticmethod
    def to_csv(data, headers, title):
        """Generate CSV file from data"""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(headers)
        writer.writerows(data)
        
        return output.getvalue().encode('utf-8'), f"{title}_{datetime.now().strftime('%Y%m%d')}.csv", 'text/csv'
