import streamlit as st

def module_tabs():
    return st.radio(
        "Module Detail Tabs",
        ["Home", "ER Diagram", "Tables", "SQL Query", "Triggers", "Output"],
        horizontal=True,
        label_visibility="collapsed",
    )
