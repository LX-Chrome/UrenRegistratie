#!/usr/bin/env python3
"""
WSGI entry point for UrenRegistratie with werkzeug fixes
"""
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)
logger.info("Starting WSGI application initialization")

# Configure path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
    logger.debug(f"Added {current_dir} to path")

# Ensure database directory exists
try:
    os.makedirs('instance', exist_ok=True)
    logger.debug("Ensured instance directory exists")
except Exception as e:
    logger.error(f"Failed to create instance directory: {e}")

# Add werkzeug patches directly before any other imports
try:
    logger.debug("Importing and patching werkzeug.urls...")
    import werkzeug.urls
    
    # Add url_decode if needed
    if not hasattr(werkzeug.urls, 'url_decode'):
        logger.debug("Adding url_decode function")
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
                logger.debug(f"Error in url_decode: {e}")
            return result
        
        # Add to werkzeug
        werkzeug.urls.url_decode = simple_url_decode
        sys.modules['werkzeug.urls'].url_decode = simple_url_decode
    
    # Add url_encode if needed
    if not hasattr(werkzeug.urls, 'url_encode'):
        logger.debug("Adding url_encode function")
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
                logger.debug(f"Error in url_encode: {e}")
            return '&'.join(result)
        
        # Add to werkzeug
        werkzeug.urls.url_encode = simple_url_encode
        sys.modules['werkzeug.urls'].url_encode = simple_url_encode
    
    logger.debug("werkzeug.urls patched successfully")
except Exception as e:
    import traceback
    logger.error(f"Failed to patch werkzeug.urls: {e}")
    logger.error(traceback.format_exc())

# Import app
try:
    logger.debug("Importing app...")
    from app import app
    logger.debug("App imported successfully")
    
    logger.debug("Importing routes...")
    import routes
    logger.debug("Routes imported successfully")
    
    logger.debug("Importing invoice routes...")
    import routes_invoices
    logger.debug("Invoice routes imported successfully")
    
    logger.debug("Importing report routes...")
    import routes_reports
    logger.debug("Report routes imported successfully")
    
    logger.info("WSGI application initialized successfully")
except Exception as e:
    import traceback
    error_msg = f"CRITICAL ERROR DURING IMPORT: {e}\n{traceback.format_exc()}"
    logger.error(error_msg)
    # Write to a file as well in case stdout is not captured
    with open("startup_error.log", "w") as f:
        f.write(error_msg)
    # Re-raise to make sure Gunicorn sees the error and logs it
    raise

if __name__ == "__main__":
    # For local development only, not used by Gunicorn
    app.run(host='0.0.0.0', debug=True) 