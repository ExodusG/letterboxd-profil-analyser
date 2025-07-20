# Account_analysis.py
# Cette classe permet de lancer et structurer l'app via streamlit

# modules externes
import streamlit as st

# modules internes
from src.utils import *
from src.radar_graph import *
import src.DataHandler as data_handler


###

data_handler = data_handler.DataHandler()

st.set_page_config(
    page_title="Letterboxd analysis",
    page_icon="🎥",
    layout="wide",
    menu_items={
        'Report a bug': "mailto:lelan.quentin56@gmail.com",
    }
)

st.markdown("""
# **Letterboxd Profile Analyzer**!

🎬 Welcome to our Letterboxd Profile Analyzer. With just a few clicks, you'll discover your movie habits and get interesting insights about your film preferences, all your [letterboxd](https://letterboxd.com/) statistics !  

🚀 This is just the first version of the project — many improvements are planned, including more Letterboxd stats and a feature to compare two profiles!

---

## 📥 How to get started:

1. **Log into** your Letterboxd account (on pc)
2. Go to **Settings → Data → Export Your Data**
3. **Download** the data file
4. **Upload** the zipfile below and enjoy your personalized analysis!

""")

def general_info():
    """ Affiche les statistiques générales de l'utilisateur"""

    metrics = data_handler.get_general_metrics()
    custom_title = """
    <div style='font-size:2.5em; text-align:center; font-weight:bold;'>
        <span style='color:#83c9ff'>{}</span>{}
    </div>
    """

    st.markdown("---")
    st.title("You have watched...")
    col1, col2, col3 = st.columns(3)
    for col, metric in zip([col1, col2, col3], metrics[:3]):
        with col: 
            st.markdown(custom_title.format(metric[0], metric[1]), unsafe_allow_html=True)

    st.title("You have in your watchlist...")
    col4, col5 = st.columns(2)
    for col, metric in zip([col4, col5], metrics[3:]):
        with col:
            st.markdown(custom_title.format(metric[0], metric[1]), unsafe_allow_html=True)
# fin general_info

if "setup_done" not in st.session_state: # ça évite le spinner à l'upload
    # spinner est utilisé pour afficher un message pendant le chargement des données
    with st.spinner("Setting-up... (this will take a few seconds)", show_time=True):
        data_handler.setup_worksheets_data()
    st.session_state["setup_done"] = True
else:
    data_handler.setup_worksheets_data()

if "uploader_key" not in st.session_state: 
    st.session_state["uploader_key"] = 1


@st.fragment #permet de refresh que cette partie à chaque date selectionnée
def upload():
    uploaded_files = st.file_uploader(
        "Choose your zip file", accept_multiple_files=False, key=st.session_state["uploader_key"]
    )

    if uploaded_files is not None: 
        my_bar = st.progress(0, text="Getting movie data, Please wait. (It's a free project, so there might be data limitations or errors in the dataset)")
        with my_bar: # intérêt du with ?
            data_handler.setup_user_upload(uploaded_files, my_bar) 
        my_bar.empty()  # La barre disparaît après le chargement
    if uploaded_files is not None:
        graph()
upload()

@st.fragment #permet de refresh que cette partie à chaque date selectionnée
def graph():

    selected_year = st.selectbox("Choose a year :", data_handler.get_years())
    data_handler.set_year(selected_year)
    
    ### DEBUT INTERFACE
    general_info()
    tab1, tab2, tab3 = st.tabs(["Watched", "Watchlist","Rating"])

    #WATCHED
    with tab1:
        st.header("Some stats on the movies you've seen", divider='blue')
        st.plotly_chart(data_handler.genre("watched"), use_container_width=True)

        watched_actor_col, watched_director_col = st.columns(2)
        with watched_actor_col:
            fig = data_handler.actor("watched")
            st.plotly_chart(fig)
        with watched_director_col:
            fig = data_handler.director("watched")
            st.plotly_chart(fig)
        
        st.header("Lesser-known and better-known films by number of IMDB votes", divider='blue')

        most_watched_col, less_watched_col = st.columns(2)
        bottom, top = data_handler.famous("watched")

        with less_watched_col:
            st.write("Lesser-known movie watched")
            st.write(bottom)
        with most_watched_col:
            st.write("Better-known movie watched")
            st.write(top)

        fig = data_handler.cinephile("watched")
        st.plotly_chart(fig)
        fig = data_handler.decade("watched")
        st.plotly_chart(fig)
        fig = data_handler.runtime_bar("watched")
        st.plotly_chart(fig)
        fig = data_handler.mapW("watched")
        st.plotly_chart(fig)

    #WATCHLIST
    with tab2:
        st.header("Some stats on the films you want to see", divider='blue')
        st.plotly_chart(data_handler.genre("watchlist"), use_container_width=True)

        watchlist_actor_col, watchlist_director_col = st.columns(2)
        with watchlist_actor_col:
            fig = data_handler.actor("watchlist")
            st.plotly_chart(fig)
        with watchlist_director_col:
            fig = data_handler.director("watchlist")
            st.plotly_chart(fig)

        st.header("Lesser-known and better-known films by number of IMDB votes", divider='blue')
        bottom, top = data_handler.famous("watchlist")

        most_watchlist_col, less_watchlist_col = st.columns(2)
        with less_watchlist_col:
            st.write("Lesser-known movie in your watchlist")
            st.write(bottom)
        with most_watchlist_col:
            st.write("Better-known movie in your watchlist")
            st.write(top)

        fig = data_handler.cinephile("watchlist")
        st.plotly_chart(fig)
        fig = data_handler.decade("watchlist")
        st.plotly_chart(fig)
        fig = data_handler.runtime_bar("watchlist")
        st.plotly_chart(fig)
        fig = data_handler.mapW("watchlist")
        st.plotly_chart(fig)

    #RATING
    with tab3:
        st.header("Some stats on your ratings", divider='blue')
        sur_note, sous_note = data_handler.diff_rating()

        st.write('The movies you rated most compared to IMDB')
        st.write(sur_note)
        st.write('The movies you most underrated compared to IMDB')
        st.write(sous_note)

        fig = data_handler.rating_director()
        st.plotly_chart(fig)
        fig = data_handler.rating_actor()
        st.plotly_chart(fig)
        fig = data_handler.genre_rating()
        st.plotly_chart(fig)
        fig = data_handler.comparaison_rating()
        st.plotly_chart(fig)

        fig = data_handler.generate_wordcloud()
        if fig is not None:
            st.pyplot(fig)

# if uploaded_files is not None:
#     graph()

st.markdown(
    """
    <style>
    div[data-testid="stTabs"]{
        padding-top:30px;
    }
    /* Sélectionner les titres des tabs */
    div[data-baseweb="tab-list"] > button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] {
        font-size: 30px; /* Changer la taille ici */
        min-width:200px;
    }

    @media(max-width:610px) {
        div[data-baseweb="tab-list"] > button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] {
        font-size: inherit; /* Changer la taille ici */
        min-width:inherit;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

data_handler.temp_dir.cleanup()  # Nettoyage du dossier temporaire

st.markdown("---")

#st.sidebar.title("About")
st.info(
    """
    Follow me on Letteboxd : [exodus_](https://letterboxd.com/exodus_/)

    This app is maintained by [Exodus](https://exodusg.github.io/) and [Montro](https://github.com/Montr0-0).
    
    Report a bug : [send a email with your zipfile](mailto:lelan.quentin56@gmail.com) 
"""
)