import streamlit as st
from src.view.map_view import event_map
from src.view.wrapped_view import render_wrapped
from src.render.bar_chart import bar_chart
from src.render.donut_chart import donut_chart
from src.render.poster_maker import poster_maker

def render_generic_main_view(data_handler, key):
    if data_handler.get_current_year() == 2025:
        render_wrapped(data_handler)

    st.subheader(f":blue[Genre] diversity of your :blue[{key}] films", divider=False, anchor=False)
    st.markdown("""
                <div style='text-align: justify; font-size: 1.1em;'>
                A film can belong to multiple genres, so the total count may exceed the number of films you've logged. Hover over the bars to explore films within each genre!
                </div>
                """, unsafe_allow_html=True)
    fig = bar_chart(data_handler, key, "Genre", with_dots=True)
    st.plotly_chart(fig, key="genre", use_container_width=True)

    watched_actor_col, watched_director_col = st.columns(2)
    with watched_actor_col:
        st.subheader(f"Your top :blue[actors] in your :blue[{key}] films", divider=False, anchor=False)
        st.markdown("""
                    <div style='text-align: justify; font-size: 1.1em;'>
                    Scroll horizontally to see more actors and hover over the bars to explore films featuring each actor.
                    </div>
                    """, unsafe_allow_html=True)
        fig = bar_chart(data_handler, key, "Actors", with_dots=False)
        st.plotly_chart(fig, key="actor")
    with watched_director_col:
        st.subheader(f"Your top :blue[directors] in your :blue[{key}] films", divider=False, anchor=False)
        st.markdown("""
                    <div style='text-align: justify; font-size: 1.1em;'>
                    Scroll horizontally to see more directors and hover over the bars to explore films featuring each director.
                    </div>
                    """, unsafe_allow_html=True)
        fig = bar_chart(data_handler, key, "Director", with_dots=False)
        st.plotly_chart(fig, key="director")
        
    st.subheader(f"Niche vs mainstream: your :blue[{key}] film preferences", divider=False, anchor=False)
    st.markdown(f"""
            <div style='text-align: justify; font-size: 1.1em; margin-bottom: 12px;'>
            The graph shows the distribution of films across different popularity categories. These categories are based on the number of <strong>IMDB votes</strong>. But remember, for now, we're using IMDB votes as a proxy for popularity since Letterboxd doesn't provide this data directly.
            </div>
            """, unsafe_allow_html=True)
    
    niche_left, niche_center, niche_right = st.columns([1, 0.1, 1.2], gap="medium")
    
    with niche_left:
        st.markdown("""
                    <ul style='padding-left: 20px; font-size: 1.1em;'>
                        <li><strong>Niche</strong>: Films that are in the bottom 25%</li>
                        <li><strong>Lesser-known</strong>: Films that are in the 25% to 50%</li>
                        <li><strong>Well-known</strong>: Films that are in the 50% to 75%</li>
                        <li><strong>Mainstream</strong>: Films that are in the top 25%</li>
                    </ul>
                    """, unsafe_allow_html=True)
        fig = donut_chart(data_handler, key)
        st.plotly_chart(fig, key="cinephile_graph", use_container_width=True)
    
    with niche_right:
        least_niche, most_niche = st.columns([1, 1], gap="medium")
        with least_niche:
            div = poster_maker(data_handler, key, "imdbVotes", "grid", 4, ascending=False)
            st.html(div)
            st.markdown(f"<div style='text-align: center; font-size: 1.1em; margin-top: 4px; color: #aaa;'>your most mainstream {key} films</div>", unsafe_allow_html=True)
        with most_niche:
            div = poster_maker(data_handler, key, "imdbVotes", "grid", 4, ascending=True)
            st.html(div)
            st.markdown(f"<div style='text-align: center; font-size: 1.1em; margin-top: 8px; color: #aaa;'>your four most niche {key} films</div>", unsafe_allow_html=True)
    
    st.subheader(f"Do your :blue[{key}] films span different :blue[time periods]?", divider=False, anchor=False)
    st.markdown(f"""
                <div style='text-align: justify; font-size: 1.1em; margin-bottom: 12px;'>
                This section explores the decades from which your {key} films originate. The left side shows the oldest and most recent films, while the right side offers a detailed bar chart. Hover over the bars to explore films from each decade!
                </div>
                """, unsafe_allow_html=True)
    
    decade_left, decade_center, decade_right = st.columns([1, 0.1, 1], gap="medium", vertical_alignment="center")
    with decade_left:
        oldest, newest = st.columns([1, 1], gap="medium")
        with oldest:
            div = poster_maker(data_handler, key, "Year", "grid", 4, ascending=True)
            st.html(div)
            st.markdown(f"<div style='text-align: center; font-size: 0.85em; margin-top: 8px; color: #aaa;'>your four oldest {key} films</div>", unsafe_allow_html=True)
        with newest:
            div = poster_maker(data_handler, key, "Year", "grid", 4, ascending=False)
            st.html(div)
            st.markdown(f"<div style='text-align: center; font-size: 0.85em; margin-top: 8px; color: #aaa;'>your four most recent {key} films</div>", unsafe_allow_html=True)
    with decade_right:
        fig = bar_chart(data_handler, key, "Decade", with_dots=False, reverse=True)
        st.plotly_chart(fig, key="decade", use_container_width=True)

    st.subheader(f":blue[Duration] breakdown of your :blue[{key}] films", divider=False, anchor=False)
    st.markdown(f"""
                <div style='text-align: justify; font-size: 1.1em;'>
                This section analyzes the runtime of your {key} films. Hover over the dots to explore films within each runtime division!
                </div>
                """, unsafe_allow_html=True)
    fig = bar_chart(data_handler, key, "Runtime", with_dots=True)
    st.plotly_chart(fig, key="runtime_bar")

    st.subheader(f":blue[Locations] distribution of your :blue[{key}] films", divider=False, anchor=False)
    st.markdown(f"""
                <div style='text-align: justify; font-size: 1.1em;'>
                This map visualizes the filming locations of your {key} films. Hover over the markers to explore films shot in each location!
                </div>
                """, unsafe_allow_html=True)
    fig = data_handler.mapW(key)
    event_map(data_handler, fig, key="map_generic_main")
    #https://github.com/streamlit/streamlit/issues/455#issuecomment-1811044197