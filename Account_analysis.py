# Account_analysis.py
# Cette classe permet de lancer et structurer l'app via streamlit

# modules externes
import streamlit as st
import streamlit_antd_components as sac
import logging

# modules internes
from src.utils import *
from src.radar_graph import *
import src.DataHandler as data_handler
import streamlit_antd_components as sac
from src.constants import WATCHED, WATCHLIST, PALETTE

# imports CSS

with open('src/styles/main_interface.css') as f:
    css = f.read()
with open('src/styles/general_metrics.css') as f:
    css += f.read()
with open('src/styles/graph.css') as f:
    css += f.read()
with open('src/styles/background.css') as f:
    css += f.read()
with open('src/styles/example.css') as f:
    css += f.read()
st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# imports html
with open("src/html/bottom_bar.html") as f:
    bottom_bar = f.read()
with open("src/html/main_title_and_instructions.html") as f:
    main_title_and_instructions = f.read()

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

st.markdown(main_title_and_instructions, unsafe_allow_html=True)

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
    list_year = data_handler.get_years()
    list_year.remove("Alltime")

    col1, col2, col3, col4 = st.columns([3,1,1,10], vertical_alignment="center")

    with col1:
        st.markdown("""
        <div style='text-align: justify; font-size: 1.1em;'>
        This calendar visualizes your film-watching activity for the selected year. Each square represents a day, with the color intensity indicating the number of films you watched on that day.
        </div>
        """, unsafe_allow_html=True)

    with col3:
        year = sac.segmented(
        items = [sac.SegmentedItem(label=str(year)) for year in list_year], 
        align='center', direction='vertical', color="#FF8C00",
        divider = False, size='lg', radius=8, use_container_width=False, key="calendar_year"  
        )

    with col4:
        fig = data_handler.waffle(int(year))
        st.plotly_chart(fig)
    
    st.html("<div class='spacer', style='margin-bottom: 5%;'></div>")
    

def general_info():
    data_handler.set_year("Alltime")

    st.markdown("""<div class="header", style="margin-top: 5%;"></div>""", unsafe_allow_html=True)
    st.header("LET'S GET :blue[STARTED] - Quick facts", divider="gray", anchor=False)

    st.info("""
    For better visualization, we decided to establish certain criteria to exclude specific data :
    - We do not include TV series or episodes
    - We do not include movies shorter than 5 minutes
    - We do not include movies under 20 minutes with fewer than 1,000 IMDb votes
    """, icon="ℹ️")

    div = data_handler.general_metrics_div()
    st.html(div)
    st.html("<div class='spacer', style='margin-bottom: 5%;'></div>")

    st.subheader("Your :blue[cinematic personality]", divider=False, anchor=False)
    col1, col2 = st.columns([1,1], vertical_alignment="center")
    with col1:
        st.markdown("""
        <div style='text-align: justify; font-size: 1.1em;'>
        BAM! Your cinematic soul, mapped in technicolor! This radar chart shows your film-watching personality across five dimensions. Each score is amped up on a 0-100 scale, so let's break down your profile:
        <ul>
            <li><strong>Consensus</strong>: Measures how much your ratings align with the average Letterboxd user.</li>
            <li><strong>Explorer</strong>: Shows your willingness to watch small indie films and lesser-known titles.</li>
            <li><strong>Consumer</strong>: Assesses your overall engagement with films, i.e. the number of films watched.</li>
            <li><strong>Active</strong>: Reflects your activity level on the platform, such as reviews and ratings.</li>
            <li><strong>Eclectic</strong>: Measures your willingness to explore different genres and styles compared to the average user.</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        st.info("Note: Hover over the dots for detailed insights!", icon="ℹ️")
    with col2:
        fig = data_handler.radar_graph()
        st.plotly_chart(fig)
    st.html("<div class='spacer', style='margin-bottom: 5%;'></div>")

    st.subheader("Your :blue[diary]", divider=False, anchor=False, help="Almost all the charts display elements when you hover your mouse over them!")
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
    if year=='2025':
           prepare_wrapped()
    match cat:
        case "Watched":
            st.subheader(":blue[Genre] distribution of your watched films", divider=False, anchor=False)
            fig = data_handler.genre(WATCHED)
            st.plotly_chart(fig, width='stretch')

            watched_actor_col, watched_director_col = st.columns(2)
            with watched_actor_col:
                st.subheader(":blue[Actors] in your watched films", divider=False, anchor=False)
                fig = data_handler.actor(WATCHED)
                st.plotly_chart(fig, key="actor_watched")
            with watched_director_col:
                st.subheader(":blue[Directors] of your watched films", divider=False, anchor=False)
                fig = data_handler.director(WATCHED)
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
                fig = data_handler.cinephile_graph(WATCHED)
                st.plotly_chart(fig, key="cinephile_graph_watched")
            with cinephile_right:
                div = data_handler.cinephile_div(WATCHED)
                st.html(div)

            st.subheader("Are you a :blue[Time Traveler]?", divider=False, anchor=False)

            decade_left, decade_right = st.columns(2, vertical_alignment="center")
            with decade_left:
                div = data_handler.decade_div(WATCHED)
                st.html(div)
            with decade_right:
                st.markdown("""
                <div style='text-align: justify; font-size: 1.1em;'>
                The graph shows the distribution of your watched films across different decades.
                </div>
                """, unsafe_allow_html=True)
                fig = data_handler.decade_graph(WATCHED)
                st.plotly_chart(fig, key="decade_watched")

            st.subheader(":blue[Runtime] distribution of your watched films", divider=False, anchor=False)
            fig = data_handler.runtime_bar(WATCHED)
            st.plotly_chart(fig, key="runtime_bar_watched")
            st.subheader(":blue[Locations] distribution of your watched films", divider=False, anchor=False)
            fig = data_handler.mapW(WATCHED)
            
            event_map(fig,WATCHED)
            #https://github.com/streamlit/streamlit/issues/455#issuecomment-1811044197

        case "Watchlist":
            if data_handler.watchlist_empty() :
                st.warning("You have no movie in your watchlist, please add some to see more data",icon="⚠️")
            else:
                st.subheader(":blue[Genre] distribution of your watchlist films", divider=False, anchor=False)
                fig = data_handler.genre(WATCHLIST)
                st.plotly_chart(fig, width='stretch')

                watchlist_actor_col, watchlist_director_col = st.columns(2)
                with watchlist_actor_col:
                    st.subheader(":blue[Actors] in your watchlist films", divider=False, anchor=False)
                    fig = data_handler.actor(WATCHLIST)
                    st.plotly_chart(fig, key="actor_watchlist")
                with watchlist_director_col:
                    st.subheader(":blue[Directors] of your watchlist films", divider=False, anchor=False)
                    fig = data_handler.director(WATCHLIST)
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
                    fig = data_handler.cinephile_graph(WATCHLIST)
                    st.plotly_chart(fig, key="cinephile_graph_watchlist")
                with cinephile_right:
                    div = data_handler.cinephile_div(WATCHLIST)
                    st.html(div)

                st.header("Are you a :blue[Time Traveler]?", divider=False, anchor=False)

                decade_left, decade_right = st.columns(2, vertical_alignment="center")
                with decade_left:
                    div = data_handler.decade_div(WATCHLIST)
                    st.html(div)
                with decade_right:
                    st.markdown("""
                    <div style='text-align: justify; font-size: 1.1em;'>
                    The graph shows the distribution of your watchlist films across different decades.
                    </div>
                    """, unsafe_allow_html=True)
                    fig = data_handler.decade_graph(WATCHLIST)
                    st.plotly_chart(fig, key="decade_watchlist")

                st.subheader(":blue[Runtime] distribution of your watchlist", divider=False, anchor=False)
                fig = data_handler.runtime_bar(WATCHLIST)
                st.plotly_chart(fig, key="runtime_bar_watchlist")

                st.subheader(":blue[Locations] distribution of your watchlist", divider=False, anchor=False)
                fig = data_handler.mapW(WATCHLIST)
                event_map(fig,WATCHLIST)

        case "Rating":
            
            if data_handler.rating_empty():
                st.warning("You have no movie in your ratings, please add some to see more data",icon="⚠️")
            else:
                col11,col22, col33 = st.columns([1,1,1], vertical_alignment="center",gap="large")
                with col22:
                    st.subheader("The 10 films you have most :blue[overrated]", divider=False, anchor=False)
                div=data_handler.diff_rating_test("overrated")
                st.html(div)
                col111,col222, col333 = st.columns([1,1,1], vertical_alignment="center",gap="large")
                with col222:
                    st.subheader("The 10 films you have most :blue[underrated]", divider=False, anchor=False)
                div=data_handler.diff_rating_test("underrated")
                st.html(div)
                st.subheader("Top 25 most rated :blue[directors] and their average rating ", divider=False, anchor=False)
                fig = data_handler.rating_director()
                st.plotly_chart(fig, key="rating_director")
                st.subheader("Top 25 most rated :blue[actors] and their average rating ", divider=False, anchor=False)
                fig = data_handler.rating_actor()
                st.plotly_chart(fig, key="rating_actor")
                st.subheader("Number of films and average rating by :blue[genre]", divider=False, anchor=False)
                fig = data_handler.genre_rating()
                st.plotly_chart(fig, key="genre_rating")

                st.subheader(":blue[Breakdown] of IMDB ratings and your own ratings", divider=False, anchor=False)
                fig = data_handler.comparaison_rating()
                st.plotly_chart(fig, key="comparaison_rating")

            fig = data_handler.generate_wordcloud()
            if fig is not None:
                st.subheader("A wordcloud with all your :blue[reviews]", divider=False, anchor=False)
                #col1, col2, col3 = st.columns([1, 2, 1])
                #with col2:
                st.pyplot(fig,width="content")

#

# TODO: intégrer le bouton d'upload dans le file_uploader (impossible mais à creuser)
def exemple():

    col1, col2 = st.columns([9,1], gap="small", vertical_alignment="top")
    if st.session_state.get("exemple") != 1: #on affiche pas le bouton exemple si on a upload une archive
        with col2:
            btn = st.button(
                "📂 Try example data",
                key="example_btn", 
                type="secondary",
                width='content'
            )

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

@st.fragment
def prepare_wrapped():
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
app()

data_handler.temp_dir.cleanup()  # Nettoyage du dossier temporaire

st.markdown("---")

#st.sidebar.title("About")
st.html(bottom_bar)