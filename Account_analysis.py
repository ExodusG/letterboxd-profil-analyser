# account_analysis.py

# modules externes
import streamlit as st

# modules internes
from src.assets import load_css, load_html

from src.data import DataHandler

from src.view.watched_view import render_watched_view
from src.view.watchlist_view import render_watchlist_view
from src.view.ratings_view import render_ratings_view
from src.view.selection_view import render_selection
from src.view.general_info import render_general_info


# init functions 
def initialize_session_state():
    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = 1
    if "example_data" not in st.session_state:
        st.session_state["example_data"] = 0
    if "setup_done" not in st.session_state:
        st.session_state["setup_done"] = False

def configure_app():
    st.set_page_config(
        page_title="Letterboxd analysis",
        page_icon="🎥",
        layout="wide",
        menu_items={
            'Report a bug': "mailto:movieboxdanalysis@gmail.com",
            'About': "We are not affiliated with Letterboxd. This is a personal project to analyze your Letterboxd data."
        }
    )
#


def get_user_choice(data_handler):
    uploaded_files = st.file_uploader(
        accept_multiple_files=False,
        key=st.session_state["uploader_key"],
        type=["zip"],
        label=" "
    )

    # user upload
    if uploaded_files is not None:
        my_bar = st.progress(0, text="Processing your data...")
        with my_bar:
            data_handler.setup_user_upload(False, uploaded_files, my_bar)
        my_bar.empty()
        return True

    # example data
    if st.button("📂 Try example data", key="example_btn"):
        my_bar = st.progress(0, text="Loading example data...")
        with my_bar:
            data_handler.setup_user_upload(True, None, my_bar)
        my_bar.empty()
        return True

    return False


@st.fragment
def detailed_profile_analysis(data_handler):
    cat = render_selection(data_handler)
    match cat:
        case "Watched":
            render_watched_view(data_handler)
        case "Watchlist":
            render_watchlist_view(data_handler)
        case "Rating":
            render_ratings_view(data_handler)

@st.fragment
def app(data_handler):
    if get_user_choice(data_handler):
        render_general_info(data_handler)
        detailed_profile_analysis(data_handler)


def main():
    initialize_session_state()
    configure_app()
    
    st.markdown(f'<style>{load_css()}</style>', unsafe_allow_html=True)
    html_content = load_html()
    st.markdown(html_content["main_title_and_instructions"], unsafe_allow_html=True)

    data_handler = DataHandler()

    if not st.session_state["setup_done"]:
        with st.spinner("SETTING UP (this may take a few seconds)...", show_time=True):
            data_handler.setup_worksheets_data()
        st.session_state["setup_done"] = True

    app(data_handler)

    st.markdown("---")
    st.markdown(html_content["bottom_bar"], unsafe_allow_html=True)



if __name__ == "__main__":
    main()


