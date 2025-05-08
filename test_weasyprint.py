#!/usr/bin/env python
"""
Test script voor WeasyPrint
"""
import os
import tempfile

print("Testen van WeasyPrint installatie...")

try:
    # Importeer WeasyPrint
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    print("WeasyPrint is succesvol geïmporteerd!")

    # Maak een eenvoudige HTML string
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WeasyPrint Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 2cm; }
            h1 { color: navy; }
            .success { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>WeasyPrint Test</h1>
        <p class="success">Dit document werd succesvol gegenereerd met WeasyPrint!</p>
        <p>Datum: 2023-06-15</p>
    </body>
    </html>
    """

    # Maak een tijdelijk bestand
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as pdf_file:
        pdf_file_path = pdf_file.name

    # Genereer de PDF
    font_config = FontConfiguration()
    html_doc = HTML(string=html_content)
    html_doc.write_pdf(pdf_file_path, font_config=font_config)

    print(f"PDF succesvol gegenereerd naar: {pdf_file_path}")
    print(f"Bestandsgrootte: {os.path.getsize(pdf_file_path)} bytes")
    print("WeasyPrint werkt correct!")

except ImportError as e:
    print(f"Fout bij importeren van WeasyPrint: {str(e)}")
    print("Controleer of WeasyPrint correct is geïnstalleerd met: pip install weasyprint")

except Exception as e:
    print(f"Fout bij gebruik van WeasyPrint: {str(e)}") 