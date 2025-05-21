@echo off 
cd /d "C:\Users\Administrator\Documents\GitHub\UrenRegistratie\" 
call prod_env\Scripts\activate.bat 
prod_env\Scripts\python production_server.py 
