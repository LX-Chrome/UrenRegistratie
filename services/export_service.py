import csv
import io
from datetime import datetime
import pdfkit
import xlsxwriter
from flask import render_template
import os

class ExportService:
    @staticmethod
    def to_pdf(template_name, data, title):
        """Generate PDF from template"""
        try:
            # Add the current datetime to the template data
            data['now'] = datetime.now()
            
            # Use a PDF-specific template
            pdf_template = f"pdf_{template_name}"
            
            # Check if PDF template exists, otherwise use the regular template
            html = render_template(pdf_template, **data)
            
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
            
            # Check if wkhtmltopdf is installed in system path or in the expected location for Windows
            wkhtmltopdf_path = None
            if os.name == 'nt':  # Windows
                possible_paths = [
                    r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe',
                    r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        wkhtmltopdf_path = path
                        break
            
            # Generate PDF with configuration if path found, otherwise use default
            if wkhtmltopdf_path:
                config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                pdf = pdfkit.from_string(html, False, options=options, configuration=config)
            else:
                pdf = pdfkit.from_string(html, False, options=options)
                
            return pdf, f"{title}_{datetime.now().strftime('%Y%m%d')}.pdf", 'application/pdf'
            
        except Exception as e:
            # If PDF generation fails, return an error page
            html = f"""
            <html>
            <body>
                <h1>Error Generating PDF</h1>
                <p>There was an error generating the PDF: {str(e)}</p>
                <p>Please check if wkhtmltopdf is installed on the server.</p>
                <p><a href="/pdf-export-guide">View PDF Export Setup Guide</a></p>
            </body>
            </html>
            """
            return html.encode('utf-8'), f"error_{datetime.now().strftime('%Y%m%d')}.html", 'text/html'

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
