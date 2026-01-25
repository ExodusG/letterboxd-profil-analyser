import streamlit as st
from src.render.poster_maker import poster_maker

def render_ratings_view(data_handler):

    if data_handler.rating_empty():
        st.warning("You have no movie in your ratings, please add some to see more data",icon="⚠️")

    else:

        st.subheader("Your most :blue[overrated] watched films (vs. average user ratings)", divider=False, anchor=False)
        div = poster_maker(data_handler, "watched", "diff_rating", "flex", 10, ascending=False, ratings=True)
        st.html(div)

        st.subheader("Your most :blue[underrated] watched films (vs. average user ratings)", divider=False, anchor=False)
        div = poster_maker(data_handler, "watched", "diff_rating", "flex", 10, ascending=True, ratings=True)
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
        st.pyplot(fig)