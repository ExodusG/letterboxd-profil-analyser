import streamlit as st
from src.constants import WATCHLIST
from src.view.map_view import event_map

def render_watchlist_view(data_handler):
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
        event_map(data_handler, fig, WATCHLIST)