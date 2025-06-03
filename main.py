from app import create_app
import argparse
import os

app = create_app()

if __name__ == "__main__":
    # Set up command line arguments for flexible hosting
    parser = argparse.ArgumentParser(description='Time Registrator Application')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    # Get environment variables or use defaults
    host = os.environ.get('HOST', args.host)
    port = int(os.environ.get('PORT', args.port))
    debug = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 't') or args.debug
    
    # Print startup information
    print(f"Starting server on {host}:{port} with debug={debug}")
    print("To access the application, open your browser and go to:")
    
    # If binding to all interfaces (0.0.0.0), suggest localhost
    if host == '0.0.0.0':
        print(f"http://localhost:{port}")
        print(f"http://127.0.0.1:{port}")
    else:
        print(f"http://{host}:{port}")
    
    # Start the Flask app
    app.run(host=host, port=port, debug=debug)
