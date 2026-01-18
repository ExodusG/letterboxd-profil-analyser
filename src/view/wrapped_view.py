import streamlit as st
import logging

@st.fragment
def render_wrapped(data_handler):
    if st.button("Prepare your 2025 wrapped 🎬", type="primary"):
        logging.basicConfig(level=logging.INFO)
        logging.info("wrapped 2025")
        st.download_button(
            label="Download your 2025 wrapped",
            data=data_handler.get_wrapped(),
            file_name="wrapped_2025.png",
            mime="image/png",
            icon=":material/download:",
        )