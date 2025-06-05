#!/usr/bin/env python
"""
Fix for Werkzeug compatibility issues with Flask-Login
This script provides and installs a workaround for the missing url_decode function
"""

import sys
import os
import importlib
import logging
from functools import wraps

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def fix_werkzeug_urls():
    """Add url_decode to werkzeug.urls if it's missing"""
    try:
        import werkzeug.urls
        # Try to import url_decode
        try:
            from werkzeug.urls import url_decode
            logger.debug("url_decode exists in werkzeug.urls")
            return True
        except ImportError:
            logger.warning("url_decode missing from werkzeug.urls, adding a custom implementation")
            
            # Define a simple url_decode function compatible with what Flask-Login needs
            def url_decode(s, charset='utf-8', decode_keys=False, include_empty=True, errors='replace'):
                """Simple replacement for werkzeug.urls.url_decode"""
                logger.debug(f"Custom url_decode called with: {s}")
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
                    except:
                        pass
                    
                    result[k] = v
                
                logger.debug(f"Custom url_decode result: {result}")
                return result
            
            # Patch the module
            werkzeug.urls.url_decode = url_decode
            if hasattr(sys.modules, 'werkzeug.urls'):
                sys.modules['werkzeug.urls'].url_decode = url_decode
            logger.info("Successfully patched werkzeug.urls with custom url_decode")
            return True
            
    except Exception as e:
        logger.error(f"Error fixing werkzeug.urls: {str(e)}")
        return False

def patch_flask_login():
    """Patch Flask-Login to use a different method if needed"""
    try:
        import flask_login
        logger.debug("Flask-Login module loaded, checking for potential issues...")
        
        # Check if the problematic file exists and patch it
        try:
            import flask_login.utils
            logger.debug("Flask-Login utils loaded")
            
            # Check if _create_identifier exists
            if hasattr(flask_login.utils, '_create_identifier'):
                original_func = flask_login.utils._create_identifier
                
                @wraps(original_func)
                def safe_create_identifier(*args, **kwargs):
                    try:
                        return original_func(*args, **kwargs)
                    except ImportError:
                        # Create a simpler identifier that doesn't rely on werkzeug.urls
                        from hashlib import sha512
                        from flask import request
                        h = sha512()
                        h.update(request.headers.get('User-Agent', '').encode())
                        h.update(str(request.remote_addr).encode())
                        return h.hexdigest()
                
                flask_login.utils._create_identifier = safe_create_identifier
                logger.info("Patched flask_login._create_identifier with safer implementation")
                
            return True
        except Exception as e:
            logger.error(f"Error patching Flask-Login: {str(e)}")
            return False
            
    except ImportError:
        logger.warning("Flask-Login not installed, skipping patch")
        return False

if __name__ == "__main__":
    logger.info("Starting Werkzeug compatibility fix")
    
    werkzeug_fixed = fix_werkzeug_urls()
    flask_login_fixed = patch_flask_login()
    
    if werkzeug_fixed and flask_login_fixed:
        logger.info("All fixes successfully applied!")
        sys.exit(0)
    else:
        logger.error("One or more fixes failed. Please check the logs.")
        sys.exit(1) 