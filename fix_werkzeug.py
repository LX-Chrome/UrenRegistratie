#!/usr/bin/env python
"""
Fix for Werkzeug compatibility issues with Flask-Login
This script provides and installs a workaround for the missing url functions
"""

import sys
import os
import importlib
import logging
from functools import wraps

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def fix_werkzeug_urls():
    """Add url_decode and url_encode to werkzeug.urls if missing"""
    try:
        import werkzeug.urls
        
        # Check and add url_decode if missing
        try:
            from werkzeug.urls import url_decode
            logger.debug("url_decode exists in werkzeug.urls")
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
                    except Exception as e:
                        logger.debug(f"Error in unquote_plus: {e}")
                    
                    result[k] = v
                
                logger.debug(f"Custom url_decode result: {result}")
                return result
            
            # Patch the module
            werkzeug.urls.url_decode = url_decode
            if 'werkzeug.urls' in sys.modules:
                sys.modules['werkzeug.urls'].url_decode = url_decode
            logger.info("Successfully patched werkzeug.urls with custom url_decode")

        # Check and add url_encode if missing
        try:
            from werkzeug.urls import url_encode
            logger.debug("url_encode exists in werkzeug.urls")
        except ImportError:
            logger.warning("url_encode missing from werkzeug.urls, adding a custom implementation")
            
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
                        encoded_items.append(f"{quote_plus(k)}={quote_plus(v)}")
                    result = separator.join(encoded_items)
                except Exception as e:
                    logger.debug(f"Error in quote_plus: {e}")
                    # Fallback to simple encoding
                    result = separator.join([f"{k}={v}" for k, v in items])
                
                logger.debug(f"Custom url_encode result: {result}")
                return result
            
            # Patch the module
            werkzeug.urls.url_encode = url_encode
            if 'werkzeug.urls' in sys.modules:
                sys.modules['werkzeug.urls'].url_encode = url_encode
            logger.info("Successfully patched werkzeug.urls with custom url_encode")
        
        return True
            
    except Exception as e:
        logger.error(f"Error fixing werkzeug.urls: {str(e)}")
        logger.error(f"Traceback: {__import__('traceback').format_exc()}")
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
                    except ImportError as e:
                        logger.warning(f"Using fallback identifier due to import error: {e}")
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
            logger.error(f"Traceback: {__import__('traceback').format_exc()}")
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