import streamlit as st
from db import get_collection

st.title("MongoDB + Streamlit Demo")

try:
    collection = get_collection("users", db_name="mydatabase")
except Exception as exc:
    st.error(f"Database is not configured: {exc}")
    st.info("Set MONGO_URI in Streamlit secrets before using this demo.")
    st.stop()

name = st.text_input("Enter Name")

if st.button("Save"):
    collection.insert_one({"name": name})
    st.success("Saved!")

if st.button("View Data"):
    data = list(collection.find({}, {"_id": 0}))
    st.write(data)