@echo off 
cd /d "C:\Users\Administrator\Documents\GitHub\UrenRegistratie\" 
call prod_env\Scripts\activate.bat 
REM Fix for missing packages 
pip install pdfkit xhtml2pdf reportlab 
 
prod_env\Scripts\python production_server.py 
