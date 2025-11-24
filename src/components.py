import streamlit as st
from auth import logout

LOGO_PATH = "assets/temporec_logo.png"


def gradient_header(title: str, subtitle: str = "", page_id: str = ""):
    """
    Ultra-stable header: logo + title + logout button.
    No CSS, no HTML, no images that break, no custom sizing.
    """

    col1, col2, col3 = st.columns([0.08, 0.72, 0.20])

    with col1:
        st.image(LOGO_PATH, width=180)

    with col2:
        st.markdown(f"## {title}")
        if subtitle:
            st.caption(subtitle)

    with col3:
        if st.button("Logout", key=f"logout_{page_id}"):
            logout()
            st.rerun()

    st.write("---")