"""
Vercel serverless entry point.
Vercel's @vercel/python runtime looks for a callable named 'app' in this file.
"""
import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Load .env for local overrides (no-op on Vercel where env vars are injected)
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / '.env')
except ImportError:
    pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ShantiVeer_hms.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402

app = get_wsgi_application()
