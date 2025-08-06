# Account_analysis.py
# Cette classe permet de lancer et structurer l'app via streamlit

# modules externes
import streamlit as st
import streamlit_antd_components as sac

# modules internes
from src.utils import *
from src.radar_graph import *
import src.DataHandler as data_handler
import streamlit_antd_components as sac

# imports CSS
with open('src/styles/main_interface.css') as f:
    css = f.read()
with open('src/styles/general_metrics.css') as f:
    css += f.read()
with open('src/styles/graph.css') as f:
    css += f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

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
# **Letterboxd Stats Analyzer**

🎬 Welcome to our Letterboxd Profile Analyzer. With just a few clicks, you'll discover your movie habits and get interesting insights about your film preferences, all your [letterboxd](https://letterboxd.com/) statistics !  

🚀 This is just the first version of the project — many improvements are planned, including more Letterboxd stats and a feature to compare two profiles!

---

## 📥 How to get started:

1. **Log into** your Letterboxd account (on pc)
2. Go to **Settings → Data → [Export Your Data](https://letterboxd.com/settings/data/)**
3. **Download** the data file
4. **Upload** the zipfile below and enjoy your personalized analysis!

""")

if "setup_done" not in st.session_state: # ça évite le spinner à l'upload
    # spinner est utilisé pour afficher un message pendant le chargement des données
    with st.spinner("Setting-up... (this will take a few seconds)", show_time=True):
        data_handler.setup_worksheets_data()
    st.session_state["setup_done"] = True
else:
    data_handler.setup_worksheets_data()

if "uploader_key" not in st.session_state: 
    st.session_state["uploader_key"] = 1

if "exemple" not in st.session_state: 
    st.session_state["exemple"] = 0


def upload():
    uploaded_files = st.file_uploader(
        accept_multiple_files=False, key=st.session_state["uploader_key"], type=["zip"],label=" "
    )

    if uploaded_files is not None: 
        my_bar = st.progress(0, text="Getting movie data, Please wait. (It's a free project, so there might be data limitations or errors in the dataset)")
        with my_bar:
            data_handler.setup_user_upload(uploaded_files, my_bar,None) 
        my_bar.empty()  # La barre disparaît après le chargement
    if uploaded_files is not None:
        st.session_state["exemple"] = 1
        general_info()
        main_interface()


# MAIN INTERFACE #

@st.fragment
def calendar():
    col1,col3 = st.columns([3,1], vertical_alignment="center")
    list_year=data_handler.get_years()
    list_year.remove("Alltime")
    with col3:
        year=sac.segmented(
        items = [sac.SegmentedItem(label=str(year)) for year in list_year]
        , label='Select a year', align='center', direction='vertical',color='orange'  
        )
    with col1:
        fig=data_handler.waffle(int(year))
        st.plotly_chart(fig,)

def general_info():
    data_handler.set_year("Alltime")

    st.markdown("""<div class="header", style="margin-top: 5%;"></div>""", unsafe_allow_html=True)
    st.header("LET'S GET :blue[STARTED] - Quick facts", divider="gray", anchor=False)
    st.markdown("""
    <div style='text-align: left; margin-bottom: 3%; font-size: 1.1em;'>
    This first section shows some general metrics in three different ways:
    <ul>
        <li><strong>General metrics</strong>: A quick overview of your Letterboxd profile.</li>
        <li><strong>Radar chart</strong>: A visual representation of your film preferences, activity, uniqueness...</li>
        <li><strong>Waffle plot</strong>: A unique way to visualize your watched films day to day</li>
    </ul>
    Have fun exploring your statistics!
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2, vertical_alignment="center")
    with col1:
        div = data_handler.general_metrics_div()
        st.html(div)
    with col2:
        st.markdown("""
        <div style='text-align: center; font-size: 3em;'>
        RADAR plot coming soon...
        </div>
        """, unsafe_allow_html=True)

    calendar()

@st.fragment
def main_interface():

    st.header("YOUR :blue[PROFILE] ANALYSIS", divider="gray", anchor=False)
    st.markdown("""
    <div style='text-align: justify; font-size: 1.12em; font-family: "Montserrat", Arial, sans-serif; color: #e8e8e8;padding-bottom:20px;'>
        Welcome to your cinema dashboard! Here you can explore a dynamic analysis of your Letterboxd profile — including watched films, your watchlist, and ratings. 
        <br><br>
    </div>
    """, unsafe_allow_html=True)

    years = data_handler.get_years()
    col1, col2 = st.columns([2, 3], gap="large")
    with col1:
        cat = sac.segmented(
            items=[
                sac.SegmentedItem(label="Watched"),
                sac.SegmentedItem(label="Watchlist"),
                sac.SegmentedItem(label="Rating"),
            ],
            align='center',
            size='xl',
            radius='lg',
            color='red',
            use_container_width=True
        )
    with col2:
        year = sac.segmented(
            items=[sac.SegmentedItem(label=str(y)) for y in years],
            align='center',
            size='xl',
            radius='lg',
            color='red',
            use_container_width=True
        )

    st.markdown('<div class="tip-block">🎬 <b>Tip:</b> Use the buttons to switch category or year. All stats update instantly!</div>', unsafe_allow_html=True)
    data_handler.set_year(year)

    match cat:
        case "Watched":
            st.subheader(":blue[Genre] distribution of your watched films", divider=False, anchor=False)
            fig = data_handler.genre("watched")
            st.plotly_chart(fig, use_container_width=True)

            watched_actor_col, watched_director_col = st.columns(2)
            with watched_actor_col:
                st.subheader(":blue[Actors] in your watched films", divider=False, anchor=False)
                fig = data_handler.actor("watched")
                st.plotly_chart(fig, key="actor_watched")
            with watched_director_col:
                st.subheader(":blue[Directors] of your watched films", divider=False, anchor=False)
                fig = data_handler.director("watched")
                st.plotly_chart(fig, key="director_watched")

            st.subheader("Are you a :blue[Explorer] ?", divider=False, anchor=False)
            cinephile_left, cinephile_right = st.columns(2, vertical_alignment="center")
            with cinephile_left:
                st.markdown("""
                <div style='text-align: justify; font-size: 1.1em;'>
                The graph shows the distribution of films across different popularity categories. These categories are based on the number of <strong>IMDB votes</strong>.
                Thus, this may not reflect the Letterboxd community's opinion. The categories are defined as follows:
                <ul>
                    <li><strong>Obscure</strong>: Films that are in the bottom 5% by <strong>number of IMDB votes</strong></li>
                    <li><strong>Lesser-known</strong>: Films that are in the 5% to 20% range by <strong>number of IMDB votes</strong></li>
                    <li><strong>Well-known</strong>: Films that are in the 20% to 50% range by <strong>number of IMDB votes</strong></li>
                    <li><strong>Mainstream</strong>: Films that are in the top 50% by <strong>number of IMDB votes</strong></li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
                fig = data_handler.cinephile_graph("watched")
                st.plotly_chart(fig, key="cinephile_graph_watched")
            with cinephile_right:
                div = data_handler.cinephile_div("watched")
                st.html(div)

            st.subheader("Are you a :blue[Time Traveler]?", divider=False, anchor=False)

            decade_left, decade_right = st.columns(2, vertical_alignment="center")
            with decade_left:
                div = data_handler.decade_div("watched")
                st.html(div)
            with decade_right:
                st.markdown("""
                <div style='text-align: justify; font-size: 1.1em;'>
                The graph shows the distribution of your watched films across different decades.
                </div>
                """, unsafe_allow_html=True)
                fig = data_handler.decade_graph("watched")
                st.plotly_chart(fig, key="decade_watched")

            st.subheader(":blue[Runtime] distribution of your watched films", divider=False, anchor=False)
            fig = data_handler.runtime_bar("watched")
            st.plotly_chart(fig, key="runtime_bar_watched")
            st.subheader(":blue[Locations] distribution of your watched films", divider=False, anchor=False)
            fig = data_handler.mapW("watched")
            
            event_map(fig,"watched")
            #https://github.com/streamlit/streamlit/issues/455#issuecomment-1811044197

        case "Watchlist":
            st.subheader(":blue[Genre] distribution of your watchlist films", divider=False, anchor=False)
            fig = data_handler.genre("watchlist")
            st.plotly_chart(fig, use_container_width=True)

            watchlist_actor_col, watchlist_director_col = st.columns(2)
            with watchlist_actor_col:
                st.subheader(":blue[Actors] in your watchlist films", divider=False, anchor=False)
                fig = data_handler.actor("watchlist")
                st.plotly_chart(fig, key="actor_watchlist")
            with watchlist_director_col:
                st.subheader(":blue[Directors] of your watchlist films", divider=False, anchor=False)
                fig = data_handler.director("watchlist")
                st.plotly_chart(fig, key="director_watchlist")

            st.subheader("Are you an :blue[Explorer]?", divider=False, anchor=False)
            cinephile_left, cinephile_right = st.columns(2, vertical_alignment="center")
            with cinephile_left:
                st.markdown("""
                <div style='text-align: justify; font-size: 1.1em;'>
                The graph shows the distribution of films across different popularity categories. These categories are based on the number of <strong>IMDB votes</strong>.
                Thus, this may not reflect the Letterboxd community's opinion. The categories are defined as follows:
                <ul>
                    <li><strong>Obscure</strong>: Films that are in the bottom 5% by <strong>number of IMDB votes</strong></li>
                    <li><strong>Lesser-known</strong>: Films that are in the 5% to 20% range by <strong>number of IMDB votes</strong></li>
                    <li><strong>Well-known</strong>: Films that are in the 20% to 50% range by <strong>number of IMDB votes</strong></li>
                    <li><strong>Mainstream</strong>: Films that are in the top 50% by <strong>number of IMDB votes</strong></li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
                fig = data_handler.cinephile_graph("watchlist")
                st.plotly_chart(fig, key="cinephile_graph_watchlist")
            with cinephile_right:
                div = data_handler.cinephile_div("watchlist")
                st.html(div)

            st.header("Are you a :blue[Time Traveler]?", divider=False, anchor=False)

            decade_left, decade_right = st.columns(2, vertical_alignment="center")
            with decade_left:
                div = data_handler.decade_div("watchlist")
                st.html(div)
            with decade_right:
                st.markdown("""
                <div style='text-align: justify; font-size: 1.1em;'>
                The graph shows the distribution of your watchlist films across different decades.
                </div>
                """, unsafe_allow_html=True)
                fig = data_handler.decade_graph("watchlist")
                st.plotly_chart(fig, key="decade_watchlist")

            st.subheader(":blue[Runtime] distribution of your watchlist", divider=False, anchor=False)
            fig = data_handler.runtime_bar("watchlist")
            st.plotly_chart(fig, key="runtime_bar_watchlist")

            st.subheader(":blue[Locations] distribution of your watchlist", divider=False, anchor=False)
            fig = data_handler.mapW("watchlist")
            event_map(fig,"watchlist")

        case "Rating":
            
            st.header("Some stats on your ratings", divider='blue')
            #sur_note, sous_note = data_handler.diff_rating()

            # st.write('The movies you rated most compared to IMDB')
            # st.write(sur_note)
            # st.write('The movies you most underrated compared to IMDB')
            # st.write(sous_note)
            div=data_handler.diff_rating_test("overrated")
            st.html(div)
            div=data_handler.diff_rating_test("underrated")
            st.html(div)
            fig = data_handler.rating_director()
            st.plotly_chart(fig, key="rating_director")
            fig = data_handler.rating_actor()
            st.plotly_chart(fig, key="rating_actor")
            fig = data_handler.genre_rating()
            st.plotly_chart(fig, key="genre_rating")
            fig = data_handler.comparaison_rating()
            st.plotly_chart(fig, key="comparaison_rating")

            fig = data_handler.generate_wordcloud()
            if fig is not None:
                st.subheader("A wordcloud with all your reviews")
                st.pyplot(fig)

#


def exemple():

    col_left, col_right = st.columns([1,3], vertical_alignment="center")
    with col_left:
        st.markdown("""
            <div style='text-align: justify; color: #e8e8e8;'>
            📂 <b>Tip</b> - Don't have a zip file yet? You can try the example data!<br>Click the button to load it:
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_right:
        btn = st.button("Load example", key="example_btn")

    if btn:
        if st.session_state.get("exemple") == 1: #on a upload une archive avant / on rerunr tout pour tout clean
            st.session_state["exemple"] = 2 #permet de dire qu'on veut afficher l'exemple
            st.session_state["uploader_key"] += 1 # clean le zip
            st.rerun()
        data_handler.setup_user_upload("", None,"./exemple/")
        general_info()
        main_interface()
    if st.session_state.get("exemple") == 2: # l'app vient de rerun depuis le bouton exemple
        data_handler.setup_user_upload("", None,"./exemple/")
        general_info()
        main_interface()
        st.session_state["exemple"] = 0 # on remet l'état initial


@st.fragment
def event_map(fig,key):
    st.markdown("""
                <div style='text-align: justify; font-size: 1.1em;'>
                Click on a point on the map to see some films.
                </div>
                """, unsafe_allow_html=True,help="The country is determined by the production country of the film")
    #permet de gérer l'événement de sélection sur la carte
    event_dict=st.plotly_chart(fig, key=key,on_select="rerun")
    if len(event_dict.selection.points) >0 :
        div = data_handler.mapW_div(event_dict.selection.points[0]['location'],key)
        st.html(div)


@st.fragment
def app():
    #MAIN
    upload()
    exemple()

app()

data_handler.temp_dir.cleanup()  # Nettoyage du dossier temporaire

st.markdown("---")

#st.sidebar.title("About")
st.info(
    """
    Follow me on Letteboxd : [exodus_](https://letterboxd.com/exodus_/)

    This app is maintained by [Exodus](https://exodusg.github.io/) and [Montro](https://github.com/Montr0-0).
    
    Any feedback or report a bug : [send a email with your zipfile](mailto:lelan.quentin56@gmail.com) 
"""
)