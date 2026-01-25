import streamlit as st
from src.view.calendar_view import render_calendar

def render_general_info(data_handler):
    data_handler.set_year("Alltime")

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
    render_calendar(data_handler)