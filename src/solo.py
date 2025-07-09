import pandas as pd
import plotly.express as px
import numpy as np
import requests
import plotly.graph_objects as go
import pycountry
import streamlit as st
from wordcloud import WordCloud
from stop_words import get_stop_words
import matplotlib.pyplot as plt
import string
import unicodedata

def computeRuntime(df):
    df['Runtime']=df['Runtime'].replace('nan', np.nan)
    df = df.dropna(subset=['Runtime'])
    df['Runtime'] = df['Runtime'].astype(str).str.replace(r'[Ss]', '5', regex=True)

    runtimeW=df['Runtime'].str.split(' ').str[0]
    runtimeW = runtimeW.apply(lambda x: int(x) if x not in ['', 'N/A'] else None)
    runtimeW=runtimeW.sum() / 60
    return runtimeW

def get_movie_data_by_title(title,year,base_url,api_key):
    response = requests.get(base_url, params={'apikey': api_key, 't': title, 'y':year})
    return response.json()

def compute_quartile(df):
    quartile=df.copy()
    quartile['imdbVotes'] = quartile['imdbVotes'].replace("N/A", np.nan)
    quartile = quartile.dropna(subset=['imdbVotes'])
    #quartile['imdbVotes'] = quartile['imdbVotes'].str.replace(',', '')
    quartile['imdbVotes'] = quartile['imdbVotes'].astype(str).str.replace(',', '')
    quartile['imdbVotes'] = quartile['imdbVotes'].apply(
        lambda x: float(x) if x not in ['', 'N/A'] else np.nan
    )
    #quartile['imdbVotes'] = quartile['imdbVotes'].apply(lambda x: float(x) if x != '' else np.nan)
    quartile = quartile.dropna(subset=['imdbVotes'])
    quartile=quartile.sort_values(by=['imdbVotes'])

    q1=np.quantile(quartile['imdbVotes'], 0.25)
    q2=np.quantile(quartile['imdbVotes'], 0.50)
    q3=np.quantile(quartile['imdbVotes'], 0.75)
    return q1,q2,q3

def clean_year(df):
    df = df[pd.to_numeric(df['Year'], errors='coerce').notna()]
    df['Year'] = df['Year'].astype(float).astype(int).astype(str)
    return df
def clean_imdbv(df):
    df['imdbVotes'] = df['imdbVotes'].replace("N/A", np.nan)
    df = df.dropna(subset=['imdbVotes'])
    df['imdbVotes'] = df['imdbVotes'].str.replace(',', '').astype(float)
    return df
def clean_imdbr(df):
    df['imdbRating'] = df['imdbRating'].replace("N/A", np.nan)
    df = df.dropna(subset=['imdbRating'])
    df['imdbRating'] = df['imdbRating'].apply(lambda x: float(x) if x != '' else None)
    return df

def movie_per_year(df):
    films_par_annee = df['Year'].value_counts().sort_index()

    df_par_annee = films_par_annee.reset_index()
    df_par_annee.columns = ['Year', 'Number of Movies']

    fig = px.line(df_par_annee, x='Year', y='Number of Movies', title='Number of movie per year')

    st.plotly_chart(fig)

def genre(df):
    df_genres = df['Genre'].dropna().str.split(', ')

    df_genres_exploded = df_genres.explode()
    genre_counts = df_genres_exploded.value_counts().reset_index()
    genre_counts.columns = ['Genre', 'Number of movie']
    fig = px.bar(genre_counts, x='Genre', y='Number of movie', 
                title='Number of films by genre', 
                text='Number of movie')

    fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide', showlegend=False)
    st.plotly_chart(fig)

def director(df):
    # possibilité d'avoir plusieurs réalisateurs, prend le premier ou comtpe les deux séparément ?
    nb_real = df['Director'].dropna().str.split(', ').explode().value_counts().head(25).reset_index()
    nb_real.columns = ['Director', 'Number of Movies']

    fig = px.bar(nb_real, x='Director', y='Number of Movies',
                title='Number of films by director',
                text='Number of Movies')
    return fig

def actor(df):
    nb_actor = df['Actors'].dropna().str.split(', ').explode().value_counts().head(25).reset_index()
    nb_actor.columns = ['Actors', 'Number of Movies']

    fig = px.bar(nb_actor, x='Actors', y='Number of Movies',
                title='Number of films by actor',
                text='Number of Movies')
    return fig

def famous(df):
    movies_rating=df.copy()
    movies_rating['imdbVotes'] = df['imdbVotes'].replace("N/A", np.nan)
    movies_rating['imdbVotes'] = movies_rating['imdbVotes'].replace("", np.nan)
    movies_rating = movies_rating.dropna(subset=['imdbVotes'])
    movies_rating['imdbVotes'] = movies_rating['imdbVotes'].astype(str).str.replace(',', '')
    movies_rating['imdbVotes']=movies_rating['imdbVotes'].astype(float)
    bottom_5_votes = movies_rating.sort_values(by='imdbVotes', ascending=True).head(10)
    bottom=bottom_5_votes[['Title', 'imdbVotes']].reset_index(drop=True)

    top_5_votes = movies_rating.sort_values(by='imdbVotes', ascending=False).head(10)
    top=top_5_votes[['Title', 'imdbVotes']].reset_index(drop=True)
    return bottom,top

def cinephile(df,q1,q2,q3,key):
    habit=df.copy()
    habit['imdbVotes'] = habit['imdbVotes'].replace("N/A", np.nan)
    habit['imdbVotes'] = habit['imdbVotes'].replace("", np.nan)
    habit = habit.dropna(subset=['imdbVotes'])
    #habit['imdbVotes'] = habit['imdbVotes'].str.replace(',', '').astype(float)
    habit['imdbVotes'] = habit['imdbVotes'].apply(
    lambda x: float(x.replace(',', '')) if isinstance(x, str) else x
    )

    # Définir les bornes des intervalles
    intervals = [
        (habit['imdbVotes'] <= q1),             # Intervalle 0 <= Q1
        (habit['imdbVotes'] > q1) & (habit['imdbVotes'] <= q2),  # Intervalle Q1 < Q2
        (habit['imdbVotes'] > q2) & (habit['imdbVotes'] <= q3),  # Intervalle Q2 < Q3
        (habit['imdbVotes'] > q3)               # Intervalle Q3 < inf
    ]

    # Créer un tableau avec les comptages pour chaque intervalle
    counts = [
        len(habit[intervals[0]]), 
        len(habit[intervals[1]]), 
        len(habit[intervals[2]]), 
        len(habit[intervals[3]])
    ]
    result = pd.DataFrame({
        'category': [' Obscure', 'Lesser-known', 'Well-known', 'Mainstream'],
        'number': counts
    })
    fig=px.bar(result,x='category',y='number',title="Popularity of films seen",text='number')
    st.plotly_chart(fig,key=key)

def decade(df):
    years = df['Year'].dropna().explode()
    years = years.astype(int)

    years = pd.cut(years, bins=[1900, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020, 2025], 
                labels=['1900-1950', '1951-1960', '1961-1970', '1971-1980', '1981-1990', 
                        '1991-2000', '2001-2010', '2011-2020', '2021-2025'])
    years = years.value_counts().reset_index()
    years.columns = ['Year', 'Number of Movies']

    years = years.sort_values(by='Year')

    fig=px.bar(years, x='Year', y='Number of Movies', title='Films by decade',text='Number of Movies')
    st.plotly_chart(fig)

def mapW(df):
    df['Country'] = df['Country'].dropna().str.split(', ')

    df_genres_exploded = df.explode('Country')
    genre_counts = df_genres_exploded['Country'].value_counts().reset_index()
    countries = {country.name: country.alpha_3 for country in pycountry.countries}

    genre_counts['code'] = genre_counts['Country'].map(countries)

    fig = px.choropleth(
        genre_counts,
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

    st.plotly_chart(fig, use_container_width=True)

def diff_rating(df):
    sur_note=df.sort_values(by=['diff_rating'],ascending=False)
    sur_note=sur_note.head(10).reset_index(drop=True)

    sous_note=df.sort_values(by=['diff_rating'])
    sous_note=sous_note.head(10).reset_index(drop=True)
    return sur_note[['Name','Rating','imdbRating','diff_rating']],sous_note[['Name','Rating','imdbRating','diff_rating']]

def rating_director(rating_df,watch_df):
    nb_real= watch_df['Director'].value_counts().head(25)
    df_top_directors = rating_df[rating_df['Director'].isin(nb_real.index)]
    nb_films_par_director = df_top_directors['Director'].value_counts().reset_index()
    nb_films_par_director.columns = ['Director', 'Number of movie']
    mean_rating = df_top_directors.groupby('Director')['Rating'].mean().rename('Moyenne_Rating').reset_index()
    mean_rating.columns = ['Director', 'Moyenne_Rating']


    df_plot = pd.merge(nb_films_par_director, mean_rating, on='Director')

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
    st.plotly_chart(fig)

def rating_actor(rating_df):
    nb_actor = rating_df['Actors'].dropna().str.split(', ').explode().value_counts().head(25)
    top_actors = nb_actor.index

    df_exploded = rating_df.dropna(subset=['Actors']).copy()
    df_exploded['Actor'] = df_exploded['Actors'].str.split(', ')
    df_exploded = df_exploded.explode('Actor')

    df_top_actors = df_exploded[df_exploded['Actor'].isin(top_actors)]

    nb_films_par_actor = df_top_actors['Actor'].value_counts().reset_index()
    nb_films_par_actor.columns = ['Actor', 'Nb_Films']

    mean_rating_actor = df_top_actors.groupby('Actor')['Rating'].mean().reset_index()
    mean_rating_actor.columns = ['Actor', 'Moyenne_Rating']

    df_actor_plot = pd.merge(nb_films_par_actor, mean_rating_actor, on='Actor')

    fig = px.bar(
        df_actor_plot,
        x='Actor',
        y='Nb_Films',
        title='Top 25 most viewed actors and their average rating',
        labels={'Director': 'Director', 'Nb_Films': 'Number of movie'},
        text='Nb_Films'
    )
    fig.add_scatter(x=df_actor_plot['Actor'],y=df_actor_plot['Moyenne_Rating'], name='Mean Rating Letterboxd',mode='lines+markers')
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

def genre_rating(rating_df):
    rating_df['Genre'] = rating_df['Genre'].dropna().str.split(', ')
    df_genres_exploded = rating_df.explode('Genre')
    genre_counts = df_genres_exploded['Genre'].value_counts().reset_index()
    genre_counts.columns = ['Genre', 'Nombre de films']

    mean_rating_genre = df_genres_exploded.groupby('Genre')['Rating'].mean().reset_index()
    mean_rating_genre.columns = ['Genre', 'Moyenne_Rating']

    df_genre_plot = pd.merge(genre_counts, mean_rating_genre, on='Genre')

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df_genre_plot['Genre'],
        y=df_genre_plot['Nombre de films'],
        name='Number of movie',
        yaxis='y1',
        text=df_genre_plot['Nombre de films']
    ))

    fig.add_trace(go.Scatter(
        x=df_genre_plot['Genre'],
        y=df_genre_plot['Moyenne_Rating'],
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
            range=[df_genre_plot['Moyenne_Rating'].min() - 0.5, df_genre_plot['Moyenne_Rating'].max() + 0.5]  # échelle personnalisée ici
        ),
        legend=dict(x=1.02, y=0.99),
        height=500
    )
    st.plotly_chart(fig)

def comparaison_rating(rating_df):
     # Groupby pour compter les valeurs dans 'Rating'
    rate=rating_df.copy()
    rate['imdbRating'] = pd.to_numeric(rate['imdbRating'], errors='coerce')
    rate=rate.dropna(subset=['imdbRating'])
    rate['imdbRating']=(rate['imdbRating'] * 2).round() / 2
    rate = rate.groupby('imdbRating').size().reset_index(name='Number of movie')

    fig = px.bar(rate, x='imdbRating', y='Number of movie', title="Breakdown of IMDB ratings and your own ratings",labels={'imdbRating': 'Rating', 'Number of movie': 'Number of movie'},text='Number of movie',)
    fig.data[0].name = "Rating IMDB"

    letterboxd_rate = rating_df.groupby('Rating').size().reset_index(name='Number of movie')
    
    fig.add_bar(x=letterboxd_rate['Rating'], y=letterboxd_rate['Number of movie'], name='Rating Letterboxd',text=letterboxd_rate['Number of movie'])
    fig.update_layout(barmode='group', showlegend=True)

    st.plotly_chart(fig)

def clean_reviews(reviews_df):
    def clean_text(text):
        if not isinstance(text, str):
            return ''
        # Minuscule
        text = text.lower()
        # Remplacer apostrophes et retours à la ligne
        text = text.replace("'", " ").replace("\n", " ")
        # Supprimer ponctuation
        text = text.translate(str.maketrans('', '', string.punctuation))
        # Normaliser et supprimer accents
        text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
        return text.strip()
    
    return reviews_df['Review'].apply(clean_text)

def generate_wordcloud(corpus):
    stopwords = set(get_stop_words('fr')) | set(get_stop_words('en'))
    wordcloud = WordCloud(stopwords=stopwords,width=800, height=400, background_color="black",max_words=150)
    text = " ".join(corpus)
    wc=wordcloud.generate(text)
    fig, ax = plt.subplots(figsize = (20, 10),facecolor='k')
    ax.imshow(wc, interpolation = 'bilinear')
    plt.axis('off')
    st.pyplot(fig)

def runtime_bar(df):
    df['Runtime']=df['Runtime'].str.split(' ').str[0]
    df = df[df['Runtime'].notna() & ~df['Runtime'].str.contains('s', case=False, na=True)] #remove the runtime in seconde
    df['Runtime'] = df['Runtime'].apply(lambda x: int(x) if x not in ['', 'N/A'] else None)
    df = df[(df['Runtime'] >= 20) & (df['Runtime'] <= 230)]
    bins = list(range(20, 241, 10))  # 20 to 240 by 10
    labels = [f'{i}-{i+9}' for i in bins[:-1]]
    df['RuntimeBin'] = pd.cut(df['Runtime'], bins=bins, labels=labels, right=True, include_lowest=True)

 
    runtime_counts = df['RuntimeBin'].value_counts().sort_index().reset_index()
    runtime_counts.columns = ['RuntimeBin', 'Count']

    fig = px.bar(runtime_counts, x='RuntimeBin', y='Count', title='Runtime of movie',
                 labels={'RuntimeBin': 'Runtime (min)', 'Count': 'Number of movie'})
    st.plotly_chart(fig)