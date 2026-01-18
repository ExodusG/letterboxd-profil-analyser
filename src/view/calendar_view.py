import streamlit as st
import streamlit_antd_components as sac

@st.fragment
def render_calendar(data_handler):
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
