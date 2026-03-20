"""
Shared MongoDB connection for the Clinical Decision Support System.
Works in two modes:
  - Streamlit app  : reads MONGO_URI from st.secrets
  - FastAPI / CLI  : reads MONGO_URI from environment variable / .env file
"""
import os
from pymongo import MongoClient

# Load .env when running outside Streamlit
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_client: MongoClient | None = None


def _get_uri() -> str:
    # 1. Try Streamlit secrets (only available when running via `streamlit run`)
    try:
        import streamlit as st
        return st.secrets["MONGO_URI"]
    except Exception:
        pass
    # 2. Fall back to environment variable
    uri = os.getenv("MONGO_URI")
    if not uri:
        raise RuntimeError(
            "MONGO_URI not found. Set it in .streamlit/secrets.toml or as an env variable."
        )
    return uri


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(_get_uri())
    return _client


def get_db(db_name: str = "module26_er"):
    return get_client()[db_name]


def get_collection(name: str, db_name: str = "module26_er"):
    return get_db(db_name)[name]
