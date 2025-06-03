from waitress import serve 
import os 
import sys 
from app import app 
 
# Configure path for imports 
current_dir = os.path.dirname(os.path.abspath(__file__)) 
if current_dir not in sys.path: 
    sys.path.append(current_dir) 
 
# Configure pdfkit path if wkhtmltopdf is installed 
try: 
    import pdfkit 
    import os.path 
    wkhtmltopdf_paths = [ 
        r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe", 
        r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe" 
    ] 
    for path in wkhtmltopdf_paths: 
        if os.path.exists(path): 
            os.environ['WKHTMLTOPDF_PATH'] = path 
            break 
except ImportError: 
    print("Warning: pdfkit module not found. PDF export will use alternative methods.") 
 
# Import application routes 
try: 
    import routes  # noqa: F401 
    import routes_invoices  # noqa: F401 
    import routes_reports  # noqa: F401 
except ImportError as e: 
    print(f"Error importing routes: {e}") 
    print("Please check that all required packages are installed.") 
    sys.exit(1) 
 
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
