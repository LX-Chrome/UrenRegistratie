import os
import sys
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

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

# Apply Werkzeug fix first
try:
    logger.debug("Applying Werkzeug compatibility fix...")
    
    # Define a simple url_decode function compatible with what Flask-Login needs
    def url_decode(s, charset='utf-8', decode_keys=False, include_empty=True, errors='replace'):
        """Simple replacement for werkzeug.urls.url_decode"""
        logger.debug(f"Custom url_decode called with: {type(s)}")
        result = {}
        if not s:
            return result
        
        if isinstance(s, bytes):
            s = s.decode(charset, errors)
        
        pairs = s.split('&')
        for pair in pairs:
            if '=' not in pair:
                if include_empty:
                    result[pair] = ''
                continue
            k, v = pair.split('=', 1)
            
            # URL unescape
            try:
                from urllib.parse import unquote_plus
                k = unquote_plus(k, encoding=charset)
                v = unquote_plus(v, encoding=charset)
            except Exception as e:
                logger.debug(f"Error unquoting: {e}")
            
            result[k] = v
        
        return result
    
    # Define a simple url_encode function compatible with what Flask-Login needs
    def url_encode(obj, charset='utf-8', sort=False, key=None, separator='&'):
        """Simple replacement for werkzeug.urls.url_encode"""
        logger.debug(f"Custom url_encode called with: {obj}")
        if not obj:
            return ''
        
        # Ensure we have something iterable
        if not hasattr(obj, 'items'):
            obj = dict(obj)
        
        # Process the items for encoding
        items = list(obj.items())
        if sort:
            items = sorted(items, key=key)
        
        # URL escape the values
        try:
            from urllib.parse import quote_plus
            encoded_items = []
            for k, v in items:
                if v is None:
                    v = ''
                elif not isinstance(v, str):
                    v = str(v)
                encoded_items.append(f"{quote_plus(str(k))}={quote_plus(str(v))}")
            result = separator.join(encoded_items)
        except Exception as e:
            logger.debug(f"Error in quote_plus: {e}")
            # Fallback to simple encoding
            result = separator.join([f"{k}={v}" for k, v in items])
        
        logger.debug(f"Custom url_encode result: {result}")
        return result
    
    # Patch the module before it's imported by Flask-Login
    import werkzeug.urls
    werkzeug.urls.url_decode = url_decode
    werkzeug.urls.url_encode = url_encode
    sys.modules['werkzeug.urls'].url_decode = url_decode
    sys.modules['werkzeug.urls'].url_encode = url_encode
    logger.debug("Successfully patched werkzeug.urls with custom url_decode and url_encode")
except Exception as e:
    logger.error(f"Error applying Werkzeug fix: {e}")
    logger.error(traceback.format_exc())

# Try importing app with error handling
try:
    logger.debug("Importing app...")
    from app import app
    logger.debug("App imported successfully")
    
    logger.debug("Importing routes...")
    import routes  # noqa: F401
    logger.debug("Routes imported successfully")
    
    logger.debug("Importing invoice routes...")
    import routes_invoices  # noqa: F401
    logger.debug("Invoice routes imported successfully")
    
    logger.debug("Importing report routes...")
    import routes_reports  # noqa: F401
    logger.debug("Report routes imported successfully")
    
except Exception as e:
    error_msg = f"CRITICAL ERROR DURING IMPORT: {e}\n{traceback.format_exc()}"
    logger.error(error_msg)
    # Write to a file as well in case stdout is not captured
    with open("startup_error.log", "w") as f:
        f.write(error_msg)
    # Re-raise to make sure Gunicorn sees the error and logs it
    raise

logger.debug("WSGI app initialization completed successfully")

if __name__ == "__main__":
    # For local development only, not used by Gunicorn
    app.run(host='0.0.0.0', debug=True) 