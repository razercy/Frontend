import streamlit as st
import sys
from pathlib import Path

# Allow direct execution (python views/category_modules.py).
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from views.module_detail import module_detail

MODULES = {
    "A - Clinical Data": [
        ("A1", "Patient Registration"),
        ("A2", "Medical History"),
        ("A3", "Diagnoses Management"),
        ("A4", "Treatment Plans"),
        ("A5", "Vital Signs Tracking"),
        ("A6", "Clinical Notes")
    ]
}

def category_modules():
    if st.session_state.view == "module_detail":
        module_detail()
        return

    st.markdown(f"### Category A > {st.session_state.selected_category}")
    st.markdown("## Modules")

    cols = st.columns(3)

    for idx, module in enumerate(MODULES[st.session_state.selected_category]):
        with cols[idx % 3]:
            if st.button(f"{module[0]} - {module[1]}"):
                st.session_state.selected_module = module
                st.session_state.view = "module_detail"
                st.rerun()

    st.divider()
    if st.button("⬅ Back to Dashboard"):
        st.rerun()
