import hashlib
import json
import os
import sys
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Ensure we can import settings from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from app.settings import get_settings

def generate_hash(data) -> str:
    """Generate content-based short hash for a given data structure."""
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_str.encode('utf-8')).hexdigest()[:8]

def get_db_engine():
    """Get SQLAlchemy engine."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        database_url = get_settings().DATABASE_URL.get_secret_value()
    return create_async_engine(database_url)

def get_session_maker():
    """Get async session maker."""
    return async_sessionmaker(get_db_engine(), expire_on_commit=False)
