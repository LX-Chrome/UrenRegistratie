from waitress import serve 
import os 
from app import app 
import routes  # noqa: F401 
import routes_invoices  # noqa: F401 
import routes_reports  # noqa: F401 
 
if __name__ == "__main__": 
    # Get configuration from environment or use defaults 
    host = os.environ.get('HOST', '0.0.0.0') 
    port = int(os.environ.get('PORT', 8080)) 
    threads = int(os.environ.get('THREADS', 4)) 
 
    # Print server information 
    print(f"Starting production server on {host}:{port}") 
    print("Access the application at:") 
    print(f"http://{host}:{port} (from this server)") 
    hostname = os.environ.get('SERVER_NAME', None) 
    if not hostname: 
        import socket 
        try: 
            hostname = socket.gethostname() 
            ip = socket.gethostbyname(hostname) 
            print(f"http://{ip}:{port} (from your network)") 
        except: 
            pass 
 
    # Start production server with waitress 
    serve(app, host=host, port=port, threads=threads) 
