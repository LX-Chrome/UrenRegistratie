#!/bin/bash

echo "=== Starting UrenRegistratie in minimal debug mode ==="

# Activate virtual environment
source venv/bin/activate || { echo "Failed to activate venv"; exit 1; }

# Run the debug test first
echo "Running import diagnosis..."
python debug_import.py
IMPORT_RESULT=$?

# Try a minimal Flask run regardless of debug test result
echo "Trying direct Flask run..."
export FLASK_APP=main.py
export FLASK_ENV=development
export FLASK_DEBUG=1

# Create a minimal app runner that adds the patches
cat > minimal_run.py << 'EOF'
import os
import sys
import logging
from urllib.parse import unquote_plus, quote_plus

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Patch werkzeug.urls
try:
    import werkzeug.urls
    
    # Add url_decode if missing
    if not hasattr(werkzeug.urls, 'url_decode'):
        def url_decode(s, charset='utf-8', decode_keys=False, include_empty=True, errors='replace'):
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
                    pass
                result[k] = v
            return result
            
        werkzeug.urls.url_decode = url_decode
        sys.modules['werkzeug.urls'].url_decode = url_decode
        print("Added custom url_decode")
    
    # Add url_encode if missing
    if not hasattr(werkzeug.urls, 'url_encode'):
        def url_encode(obj, charset='utf-8', sort=False, key=None, separator='&'):
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
                    encoded_items.append(f"{k}={v}")
            
            return separator.join(encoded_items)
            
        werkzeug.urls.url_encode = url_encode
        sys.modules['werkzeug.urls'].url_encode = url_encode
        print("Added custom url_encode")
        
except Exception as e:
    print(f"Error patching werkzeug: {e}")

# Import and run the app
try:
    from app import app
    print("Starting Flask app...")
    app.run(host='0.0.0.0', port=8000, debug=True)
except Exception as e:
    import traceback
    print(f"Error starting Flask: {e}")
    print(traceback.format_exc())
EOF

# Run the minimal app
python minimal_run.py 