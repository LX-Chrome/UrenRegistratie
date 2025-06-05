#!/usr/bin/env python
"""
Debug script to find exact import issue
"""
import os
import sys
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("=== Starting Debug Import Test ===")

try:
    logger.info("Testing werkzeug import...")
    import werkzeug
    logger.info(f"Werkzeug version: {werkzeug.__version__}")
    
    # Test werkzeug.urls
    logger.info("Testing werkzeug.urls...")
    import werkzeug.urls
    logger.info("werkzeug.urls imported successfully")
    
    # Check for url_decode and url_encode
    functions = []
    if hasattr(werkzeug.urls, 'url_decode'):
        functions.append('url_decode')
    if hasattr(werkzeug.urls, 'url_encode'):
        functions.append('url_encode')
    logger.info(f"Available functions in werkzeug.urls: {functions}")
    
    # Test flask import
    logger.info("Testing Flask import...")
    import flask
    logger.info(f"Flask version: {flask.__version__}")
    
    # Test flask_login import
    logger.info("Testing flask_login import...")
    import flask_login
    logger.info("flask_login imported successfully")

    # Test SQLAlchemy import
    logger.info("Testing SQLAlchemy import...")
    import sqlalchemy
    logger.info(f"SQLAlchemy version: {sqlalchemy.__version__}")
    
    # Test app module import
    logger.info("Testing app import (without initializing routes)...")
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Add custom url_decode and url_encode to werkzeug if needed
    if 'url_decode' not in functions:
        logger.info("Adding custom url_decode to werkzeug.urls")
        from urllib.parse import unquote_plus
        
        def url_decode(s, charset='utf-8', decode_keys=False, include_empty=True, errors='replace'):
            logger.debug(f"Custom url_decode called with: {type(s)}")
            result = {}
            if not s: return result
            
            if isinstance(s, bytes):
                s = s.decode(charset, errors)
            
            pairs = s.split('&')
            for pair in pairs:
                if '=' not in pair:
                    if include_empty: result[pair] = ''
                    continue
                k, v = pair.split('=', 1)
                try:
                    k = unquote_plus(k, encoding=charset)
                    v = unquote_plus(v, encoding=charset)
                except Exception as e:
                    logger.debug(f"Error unquoting: {e}")
                
                result[k] = v
            return result
            
        werkzeug.urls.url_decode = url_decode
        sys.modules['werkzeug.urls'].url_decode = url_decode
        
    if 'url_encode' not in functions:
        logger.info("Adding custom url_encode to werkzeug.urls")
        from urllib.parse import quote_plus
        
        def url_encode(obj, charset='utf-8', sort=False, key=None, separator='&'):
            logger.debug(f"Custom url_encode called with: {obj}")
            if not obj: return ''
            
            if not hasattr(obj, 'items'):
                obj = dict(obj)
            
            items = list(obj.items())
            if sort: items = sorted(items, key=key)
            
            encoded_items = []
            for k, v in items:
                if v is None: v = ''
                elif not isinstance(v, str): v = str(v)
                try:
                    encoded_items.append(f"{quote_plus(str(k))}={quote_plus(str(v))}")
                except Exception as e:
                    logger.debug(f"Error in quote_plus: {e}")
                    encoded_items.append(f"{k}={v}")
            
            return separator.join(encoded_items)
            
        werkzeug.urls.url_encode = url_encode
        sys.modules['werkzeug.urls'].url_encode = url_encode
    
    # Now try importing the app
    logger.info("Now trying to import app...")
    from app import app
    logger.info("Successfully imported app")
    
    # Try importing a minimal set of routes
    logger.info("Trying to import minimal routes...")
    with app.app_context():
        logger.info("Entered app context")
        
        # Test database
        from app import db
        logger.info("Imported db from app")
        
        # Check database file
        if os.path.exists('instance/database.db'):
            logger.info("Database file exists")
        else:
            logger.info("Database file does not exist, will be created")
        
        # Try db operations
        try:
            db.create_all()
            logger.info("Successfully ran db.create_all()")
        except Exception as e:
            logger.error(f"Error with db.create_all(): {e}")
            
    logger.info("=== All Debug Tests Passed Successfully ===")
    
except Exception as e:
    logger.error(f"Error during import testing: {e}")
    logger.error(traceback.format_exc())
    print(f"\nERROR: {e}\n{traceback.format_exc()}")
    sys.exit(1) 