import streamlit as st
from db import collection

st.title("MongoDB + Streamlit Demo")

name = st.text_input("Enter Name")

if st.button("Save"):
    collection.insert_one({"name": name})
    st.success("Saved!")

if st.button("View Data"):
    data = list(collection.find({}, {"_id": 0}))
    st.write(data)