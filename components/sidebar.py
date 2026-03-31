# components/sidebar.py
import streamlit as st
from streamlit_option_menu import option_menu

def sidebar(menu_items):
    with st.sidebar:
        st.markdown("## 🏥 MediCare")
        persisted = st.session_state.get("sidebar_selected")
        if persisted not in menu_items:
            persisted = menu_items[0]

        default_icons = [
            "activity", "flask", "capsule", "building", "credit-card",
            "people", "shield", "truck", "bar-chart"
        ]
        # Keep icon list aligned with menu size to avoid index errors.
        if len(default_icons) < len(menu_items):
            icons = default_icons + ["circle"] * (len(menu_items) - len(default_icons))
        else:
            icons = default_icons[: len(menu_items)]

        selected = option_menu(
            "",
            menu_items,
            icons=icons,
            default_index=menu_items.index(persisted),
            key=f"app_sidebar_menu_{st.session_state.get('role', 'guest')}",
        )
        st.session_state.sidebar_selected = selected

        st.divider()
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.page = "login"
            st.session_state.role = None
            st.session_state.view = "main"
            st.session_state.selected_category = None
            st.session_state.selected_module = None
            st.session_state.pop("sidebar_selected", None)
            st.rerun()

    return selected