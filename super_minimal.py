#!/usr/bin/env python3
"""
Super minimalist script to run the Flask app with bare essentials
"""
import sys
import os

print("Starting super minimal Flask run...")

# Add werkzeug patches directly before any imports
import werkzeug.urls

# Define the minimal functions needed for Flask-Login
if not hasattr(werkzeug.urls, 'url_decode'):
    print("Adding url_decode function")
    def simple_url_decode(s, **kwargs):
        if not s:
            return {}
        result = {}
        try:
            if isinstance(s, bytes):
                s = s.decode('utf-8')
            pairs = s.split('&')
            for pair in pairs:
                if '=' in pair:
                    k, v = pair.split('=', 1)
                    result[k] = v
                else:
                    result[pair] = ''
        except Exception as e:
            print(f"Error in url_decode: {e}")
        return result
    
    # Add to werkzeug
    werkzeug.urls.url_decode = simple_url_decode
    sys.modules['werkzeug.urls'].url_decode = simple_url_decode

if not hasattr(werkzeug.urls, 'url_encode'):
    print("Adding url_encode function")
    def simple_url_encode(obj, **kwargs):
        if not obj:
            return ''
        result = []
        try:
            if not hasattr(obj, 'items'):
                obj = dict(obj)
            for k, v in obj.items():
                if v is None:
                    v = ''
                result.append(f"{k}={v}")
        except Exception as e:
            print(f"Error in url_encode: {e}")
        return '&'.join(result)
    
    # Add to werkzeug
    werkzeug.urls.url_encode = simple_url_encode
    sys.modules['werkzeug.urls'].url_encode = simple_url_encode

# Create database directory if needed
os.makedirs('instance', exist_ok=True)

try:
    print("Importing app...")
    from app import app
    
    # Set some basic configuration for Flask
    app.config['TESTING'] = True
    app.config['DEBUG'] = True
    app.config['SERVER_NAME'] = None  # Allows connections from any hostname
    
    print("Running Flask app...")
    app.run(host='0.0.0.0', port=8000, debug=True)
except Exception as e:
    import traceback
    print(f"Error starting Flask: {e}")
    print(traceback.format_exc()) 