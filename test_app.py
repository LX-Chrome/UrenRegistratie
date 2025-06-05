#!/usr/bin/env python

"""
Minimal test script to verify the Flask app can be imported and run
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure path is correct
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

def test_import_app():
    """Try to import just the app without routes"""
    try:
        logger.debug("Trying to import app...")
        from app import app
        logger.debug("Successfully imported app")
        return True
    except Exception as e:
        logger.error(f"Error importing app: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def test_minimal_run():
    """Try to run the app with minimal setup"""
    if not test_import_app():
        return False
    
    try:
        logger.debug("Testing app configuration...")
        from app import app
        
        # Check configuration
        logger.debug(f"SECRET_KEY exists: {'secret_key' in app.config}")
        logger.debug(f"SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        
        # Test database
        logger.debug("Testing database connection...")
        with app.app_context():
            from app import db
            db_connected = db.engine.connect()
            db_connected.close()
            logger.debug("Database connection successful")
        
        return True
    except Exception as e:
        logger.error(f"Error configuring app: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    logger.debug("Starting app test")
    success = test_minimal_run()
    if success:
        logger.debug("Basic app test PASSED")
    else:
        logger.error("Basic app test FAILED")
        sys.exit(1) 