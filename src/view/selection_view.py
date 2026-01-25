import streamlit as st
import streamlit_antd_components as sac
from src.constants import WATCHED, WATCHLIST, RATINGS

def render_selection(data_handler):
    st.header("YOUR :blue[PROFILE] ANALYSIS", divider="gray", anchor=False)

    st.markdown("""
    <div style='background-color: #1e1e1e; padding: 10px; border-radius: 8px; margin-top: 20px;'>
        <span style='font-size: 1.1em; color: #e8e8e8;'>🎬 <b>Tip:</b> Use the buttons to switch category or year. All stats update instantly!</span>
    </div>
    """, unsafe_allow_html=True)
    
    years = data_handler.get_years()

    col1, col2 = st.columns([1.5, 2.5], gap="large")
    with col1:
        cat = sac.segmented(
            items=[
                sac.SegmentedItem(label=f"{WATCHED}"),
                sac.SegmentedItem(label=f"{WATCHLIST}"),
                sac.SegmentedItem(label=f"{RATINGS}"),
            ],
            align='center',
            size='xl',
            radius='lg',
            color='blue',
            use_container_width=True
        )
    
    with col2:
        if cat != RATINGS:
            year = sac.segmented(
                items=[sac.SegmentedItem(label=f"{y}") for y in years],
                align='center',
                size='lg',
                radius='lg',
                color='blue',
                use_container_width=True
            )
        else:
            year = None


    if year:
        data_handler.set_year(year)

    return cat