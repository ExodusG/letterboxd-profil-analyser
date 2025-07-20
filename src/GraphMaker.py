import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from wordcloud import WordCloud
from stop_words import get_stop_words
import matplotlib.pyplot as plt

class GraphMaker:
    
    def __init__(self):
        self.PALETTE = {
            'orange' : '#FF8C00',
            'vert' : '#00E054',
            'bleu' : '#40BCF4',
            'blanc' : '#FFFFFF'
        }

    def graph_genre(self,df) :

        fig = px.bar(
            df,
            x='Genre',
            y='Number of movie',
            text='Number of movie',
            color='Genre',
            color_discrete_sequence=[self.PALETTE['orange'], self.PALETTE['vert'], self.PALETTE['bleu']],
            hover_data={"MoviesText": True, "Number of movie": False, "Genre": False, "Movies": False},
            title='🎬 Number of films by genre',
            custom_data=["MoviesText"]
        )

        # Affiche le hover avec la liste des films
        fig.update_traces(
            hovertemplate='<b>%{x}</b><br>Films:<br>%{customdata[0]}<extra></extra>',
            marker_line_width=1.5,
            marker_line_color="#444",
            textfont_size=14
        )

        fig.update_layout(
            showlegend=False,
            uniformtext_minsize=10,
            uniformtext_mode='show',
            title_font_size=22,
            title_x=0.5,
            margin=dict(t=80, b=60),
            xaxis_tickangle=-30,
            xaxis=dict(
                tickfont=dict(size=14),
                title_font=dict(size=16)
            ),
            yaxis=dict(
                title_font=dict(size=16),
                tickfont=dict(size=14)
            ),
        )
        return fig

    def graph_director(self, df):
        fig = px.bar(df, x='Director', y='Number of Movies',
                    title='Number of films by director',
                    text='Number of Movies')
        return fig

    def graph_actor(self, df):
        fig = px.bar(df, x='Actors', y='Number of Movies',
                    title='Number of films by actor',
                    text='Number of Movies')
        return fig

    def graph_cinephile(self, df):
        fig = px.bar(df, x='category', y='number', title="Popularity of films seen", text='number')
        return fig

    def graph_decade(self, df):
        fig = px.bar(df, x='Year', y='Number of Movies', title='Films by decade', text='Number of Movies')
        return fig

    def graph_mapW(self, df):

        fig = px.choropleth(
            df,
            locations="code",
            color="count",
            hover_name="Country",
            color_continuous_scale=px.colors.sequential.Blues,
            projection="natural earth"
        )

        fig.update_geos(
            showcoastlines=False,
            showland=True,
            landcolor="#0E1117",
            showocean=True,
            oceancolor="#0E1117",
            showframe=False,
            showcountries=True,
            countrycolor="gray"
        )

        fig.update_layout(
            title_text="Breakdown of films by country",
            title_font_color="white",
            geo_bgcolor="#0E1117",
            plot_bgcolor="#0E1117",
            paper_bgcolor="#0E1117",
            font=dict(color="white"),
            margin=dict(l=0, r=0, t=40, b=0)
        )

        return fig

    def graph_rating_director(self, df_plot, nb_films_par_director):
        fig = px.bar(
            nb_films_par_director,
            x='Director',
            y='Number of movie',
            title='Top 25 most viewed directors and their average rating',
            labels={'Director': 'Director', 'Number of movie': 'Number of movie'},
            text='Number of movie'
        )
        fig.add_scatter(x=df_plot['Director'],y=df_plot['Moyenne_Rating'], name='Mean Rating Letterboxd',mode='lines+markers')
        fig.update_layout(xaxis_tickangle=-45)
        return fig

    def graph_rating_actor(self, df):
        fig = px.bar(
            df,
            x='Actor',
            y='Nb_Films',
            title='Top 25 most viewed actors and their average rating',
            labels={'Director': 'Director', 'Nb_Films': 'Number of movie'},
            text='Nb_Films'
        )
        fig.add_scatter(x=df['Actor'],y=df['Moyenne_Rating'], name='Mean Rating Letterboxd',mode='lines+markers')
        fig.update_layout(xaxis_tickangle=-45)
        return fig

    def graph_genre_rating(self, df):
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df['Genre'],
            y=df['Nombre de films'],
            name='Number of movie',
            yaxis='y1',
            text=df['Nombre de films']
        ))

        fig.add_trace(go.Scatter(
            x=df['Genre'],
            y=df['Moyenne_Rating'],
            name='Mean rating',
            yaxis='y2',
            mode='lines+markers'
        ))

        fig.update_layout(
            title='Number of films and average rating by genre',
            xaxis=dict(title='Genre', tickangle=-45),
            yaxis=dict(
                title='Number of movie',
                side='left'
            ),
            yaxis2=dict(
                title='Mean rating',
                overlaying='y',
                side='right',
                showgrid=False,
                range=[df['Moyenne_Rating'].min() - 0.5, df['Moyenne_Rating'].max() + 0.5]  # échelle personnalisée ici
            ),
            legend=dict(x=1.02, y=0.99),
            height=500
        )
        return fig

    def graph_comparaison_rating(self, df, rating_df):
        fig = px.bar(df, x='imdbRating', y='Number of movie', title="Breakdown of IMDB ratings and your own ratings",labels={'imdbRating': 'Rating', 'Number of movie': 'Number of movie'},text='Number of movie',)
        fig.data[0].name = "Rating IMDB"

        letterboxd_rate = rating_df.groupby('Rating').size().reset_index(name='Number of movie')
        
        fig.add_bar(x=letterboxd_rate['Rating'], y=letterboxd_rate['Number of movie'], name='Rating Letterboxd',text=letterboxd_rate['Number of movie'])
        fig.update_layout(barmode='group', showlegend=True)

        return fig

    def graph_generate_wordcloud(self, wc):
        fig, ax = plt.subplots(figsize = (20, 10),facecolor='k')
        ax.imshow(wc, interpolation = 'bilinear')
        plt.axis('off')
        return fig

    def graph_runtime_bar(self, df):
        fig = px.bar(df, x='RuntimeBin', y='Count', title='Runtime of movie',
                    labels={'RuntimeBin': 'Runtime (min)', 'Count': 'Number of movie'},text='Count')
        return fig

    def movie_per_year(self, df):
        films_par_annee = df['Year'].value_counts().sort_index()

        df_par_annee = films_par_annee.reset_index()
        df_par_annee.columns = ['Year', 'Number of Movies']

        fig = px.line(df_par_annee, x='Year', y='Number of Movies', title='Number of movie per year')

        st.plotly_chart(fig)
