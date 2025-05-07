"""
Test of ReportLab correct is geïnstalleerd
"""
import sys

print(f"Python-interpreter pad: {sys.executable}")
print(f"Python-versie: {sys.version}")

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    print("ReportLab is succesvol geïmporteerd!")
    
    # Maak een eenvoudige PDF om te testen
    c = canvas.Canvas("test_reportlab.pdf", pagesize=A4)
    c.drawString(100, 750, "ReportLab werkt correct!")
    c.save()
    print("Test PDF succesvol gemaakt: test_reportlab.pdf")
    
except ImportError as e:
    print(f"Fout bij importeren van ReportLab: {e}")
    print("Controleer of ReportLab is geïnstalleerd met: pip install reportlab")
except Exception as e:
    print(f"Fout bij het maken van de test PDF: {e}") 