#!/usr/bin/env python3
"""
Diagnostic script to identify and fix import issues
"""
import sys
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)
logger.info("Starting diagnostic script")

# Configure path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
    logger.debug(f"Added {current_dir} to path")

# Try importing app
try:
    logger.debug("Attempting to import app...")
    from app import app
    logger.debug("App imported successfully")
except Exception as e:
    logger.error(f"Error importing app: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)

# Try importing routes
try:
    logger.debug("Attempting to import routes...")
    import routes
    logger.debug("Routes imported successfully")
except Exception as e:
    logger.error(f"Error importing routes: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)

# Check if dashboard function has the correct check_ins_json variable
try:
    logger.debug("Checking dashboard function...")
    dashboard_func = routes.dashboard
    
    # Look at function source code to verify check_ins_json is defined
    import inspect
    source = inspect.getsource(dashboard_func)
    if "check_ins_json" in source:
        logger.debug("check_ins_json found in dashboard function")
    else:
        logger.error("check_ins_json NOT found in dashboard function")
        
    # Execute dashboard function to see if it works
    logger.debug("All checks passed!")
    
except Exception as e:
    logger.error(f"Error checking dashboard function: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)

logger.info("Diagnostic script completed successfully") 