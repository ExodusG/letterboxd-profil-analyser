import streamlit as st
from src.constants import WATCHED
from src.view.map_view import event_map
from src.view.wrapped_view import render_wrapped

def render_watched_view(data_handler):
    if data_handler.get_current_year() == 2025:
        render_wrapped(data_handler)
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
    
    event_map(data_handler, fig, WATCHED)
    #https://github.com/streamlit/streamlit/issues/455#issuecomment-1811044197