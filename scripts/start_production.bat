@echo off 
echo Starting Time Registrator in production mode (for testing)... 
echo. 
echo This will start the server on port 8080. To access it: 
echo   http://localhost:8080 
echo   http://YOUR-SERVER-IP:8080 (from other computers) 
echo. 
echo Press Ctrl+C to stop the server 
echo. 
call prod_env\Scripts\activate.bat 
REM Fix for missing packages 
pip install pdfkit xhtml2pdf reportlab 
 
prod_env\Scripts\python production_server.py 
pause 
