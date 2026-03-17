"""
Shared MongoDB connection for the Clinical Decision Support System.
Uses Streamlit secrets for the connection URI.
"""
from pymongo import MongoClient
import streamlit as st


@st.cache_resource
def get_client():
    return MongoClient(st.secrets["MONGO_URI"])


def get_db(db_name: str = "module26_er"):
    return get_client()[db_name]


def get_collection(name: str, db_name: str = "module26_er"):
    return get_db(db_name)[name]
