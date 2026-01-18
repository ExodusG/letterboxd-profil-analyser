import streamlit as st
import streamlit_antd_components as sac

def render_selection(data_handler):
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

    return cat