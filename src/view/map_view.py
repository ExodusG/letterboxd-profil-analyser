
import streamlit as st

@st.fragment
def event_map(data_handler, fig, key):
    st.markdown("""
                <div style='text-align: justify; font-size: 1.1em;'>
                Click on a point on the map to see some films.
                </div>
                """, unsafe_allow_html=True,help="The country is determined by the production country of the film")
    #permet de gérer l'événement de sélection sur la carte
    event_dict=st.plotly_chart(fig, key=key,on_select="rerun")
    if event_dict["selection"] and len(event_dict["selection"]["points"]) > 0:
        div = data_handler.mapW_div(event_dict["selection"]["points"][0]['location'],key)
        st.html(div)