import csv
import io
from datetime import datetime
import pdfkit
import xlsxwriter
from flask import render_template

class ExportService:
    @staticmethod
    def to_pdf(template_name, data, title):
        """Generate PDF from template"""
        html = render_template(template_name, **data, export_mode=True)
        pdf = pdfkit.from_string(html, False)
        return pdf, f"{title}_{datetime.now().strftime('%Y%m%d')}.pdf", 'application/pdf'

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
