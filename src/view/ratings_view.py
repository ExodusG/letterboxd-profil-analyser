import streamlit as st
import src.view.wrapped_view as wrapped_view

def render_ratings_view(data_handler):
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