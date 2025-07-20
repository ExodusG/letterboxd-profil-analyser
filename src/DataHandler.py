# modules externes

import zipfile
import pandas as pd
import tempfile
from datetime import datetime
import pycountry
from wordcloud import WordCloud
from stop_words import get_stop_words

# modules internes
import src.ApiHandler as api_handler
import src.GraphMaker as graph_maker
from src.utils import *
from src.radar_graph import compute_radar_stats_for_sheet


class DataHandler:

    def __init__(self):
        self.api_handler = api_handler.ApiHandler()
        self.graph_maker = graph_maker.GraphMaker()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_name = self.temp_dir.name

    def setup_worksheets_data(self):
        """ Configure les données des feuilles de calcul"""
        self.films_data = self.api_handler.get_data_from_sheet("all_movies_data")
        self.profiles_data = self.api_handler.get_data_from_sheet("profiles_stats")

    def get_films(self, all_movies, dfF, my_bar):
        """ Récupère les films manquants dans all_movies à partir de dfF"""
        
        df_errors = pd.DataFrame(columns=["filename", "error", *dfF.columns])
        df_movie = pd.DataFrame()
        existing_movies = set(
            zip(all_movies['Title'].dropna().astype(str), all_movies['Year'].dropna())
        )

        i = 0 # Itérer sur les lignes de dfF pour comparer (Name, Year)
        for _, row in dfF.iterrows():
            title_year = (row['Name'], row['Year'])
            if title_year not in existing_movies:
                try:
                    films_data = self.api_handler.get_movie_data_by_title(row['Name'], row['Year'])
                    if films_data.get('Error') is not None:
                        df_errors.loc[len(df_errors)] = [self.uploaded_files.name, films_data['Error'], *row.values]
                    else:
                        df_movie = pd.concat([df_movie, pd.DataFrame([films_data])], ignore_index=True)
                except Exception as e:
                    # sentry_sdk.capture_message(f"Movie not found: {row.to_dict()}")
                    df_errors.loc[len(df_errors)] = [self.uploaded_files.name, str(e), *row.values]
            my_bar.progress(
                int(100 * i / len(dfF)), 
                text="Getting movie data, Please wait. (It's a free project, so there might be data limitations or errors in the dataset)"
                )
            i += 1

        if not df_errors.empty:
            self.api_handler.add_error_to_sheet(df_errors)

        if not df_movie.empty:
            self.api_handler.add_movies_to_sheet(df_movie)
            self.all_movies = pd.concat([all_movies, df_movie]).drop_duplicates(subset=['Title', 'Year'])

        my_bar.empty()
        return all_movies
    

    def setup_user_upload(self, uploaded_files, my_bar):
        """ Configure les données de l'utilisateur à partir du fichier zip téléchargé"""
        if uploaded_files is not None:
            self.uploaded_files = uploaded_files
            try:
                with zipfile.ZipFile(uploaded_files, 'r') as zip_ref:
                    zip_ref.extractall(self.temp_name)

                self.watchlist = pd.read_csv(self.temp_name + '/watchlist.csv')
                self.watched = pd.read_csv(self.temp_name + '/watched.csv')
                self.rating = pd.read_csv(self.temp_name + '/ratings.csv')
                self.reviews = pd.read_csv(self.temp_name + '/reviews.csv')
                self.profile = pd.read_csv(self.temp_name + '/profile.csv')
                self.comments = pd.read_csv(self.temp_name + '/comments.csv')

                self.watchlist = clean_year(self.watchlist)
                self.watched = clean_year(self.watched)
                self.rating = clean_year(self.rating)

                self.all_movies = pd.DataFrame(self.films_data)
                self.all_movies = clean_year(self.all_movies)
                self.watched_and_watchlist = pd.concat([self.watched, self.watchlist])

                self.all_movies = self.get_films(self.all_movies, self.watched_and_watchlist, my_bar)

                # mg = merge = méga fichier avec tous les films et les données intéressantes
                self.watched_mg = pd.merge(self.watched, self.all_movies, how='inner', left_on=["Name", "Year"], right_on=["Title", "Year"]).drop_duplicates()
                self.watchlist_mg = pd.merge(self.watchlist, self.all_movies, how='inner', left_on=["Name", "Year"], right_on=["Title", "Year"]).drop_duplicates()

                self.rating_mg = pd.merge(self.rating, self.all_movies, how='inner', left_on=["Name", "Year"], right_on=["Title", "Year"]).drop_duplicates()
                self.rating_mg['Rating'] = self.rating_mg['Rating'] * 2
                self.rating_mg = clean_imdbr(self.rating_mg)
                self.rating_mg['diff_rating'] = self.rating_mg['Rating'] - self.rating_mg['imdbRating']

                radar_stats = compute_radar_stats_for_sheet(self.all_movies, self.watched_mg, self.rating_mg, 
                                                            self.reviews, self.comments, 
                                                            self.api_handler.get_data_from_sheet("profiles_stats"))
                self.api_handler.add_profiles_to_stats_sheet(self.profile.iloc[0], radar_stats)

            except zipfile.BadZipFile:
                st.session_state["uploader_key"] += 1
                #trick to remove bad file
                st.warning('This is not a zipfile', icon="⚠️")
                st.rerun()

            except FileNotFoundError:
                st.write(f"File not found.")

    def get_general_metrics(self):
        """ Récupère les stats générales"""
        metrics = [
            (len(self.watched_df.index), " movies"),
            (round(computeRuntime(self.watched_df)), " hours"),
            (len(self.watched_df['Director'].unique()), " directors"),
            (len(self.watchlist_df.index), " movies"),
            (round(computeRuntime(self.watchlist_df)), " hours"),
        ]
        return metrics

    def get_years(self):
        """ Récupère les années de visionnage à partir de la date d'inscription du profil"""
        dateJoined = pd.to_datetime(self.profile['Date Joined'], errors='coerce').dt.year
        dateJoined = int(dateJoined.iloc[0])
        current_year = datetime.now().year
        years = ["Alltime"] + list(sorted(range(dateJoined, current_year + 1), reverse=True))
        return years

    def set_year(self, selected_year):
        """ Définit l'année de visionnage"""
        if selected_year == "Alltime":
            self.watched_df = self.watched_mg
            self.watchlist_df = self.watchlist_mg
            self.rating_df = self.rating_mg
            self.reviews_df = self.reviews
        else:
            self.watched_df = extract_year(self.watched_mg, selected_year)
            self.watchlist_df = extract_year(self.watchlist_mg, selected_year)
            self.rating_df = extract_year(self.rating_mg, selected_year)
            self.reviews_df = extract_year(self.reviews, selected_year)
        self.corpus = clean_reviews(self.reviews_df)
        self.year = selected_year

    def genre(self, key):
        """ Prépare les data pour le GraphMaker et renvoie le graphique à l'interface"""
        match key:
            case "watched":
                df_genres = self.watched_df[['Name', 'Genre']].dropna()
            case "watchlist":
                df_genres = self.watchlist_df[['Name', 'Genre']].dropna()

        df_genres['Genre'] = df_genres['Genre'].str.split(', ')
        df_genres_exploded = df_genres.explode('Genre')

            # Générer une colonne texte pour le hover
        def make_movies_text(movie_list):
            # Limite l'affichage à 10 films max par genre (pour la lisibilité)
            movies = movie_list[:10]
            movies_text = "<br>".join(f"• {m}" for m in movies)
            if len(movie_list) > 10:
                movies_text += f"<br><span style='color:#888; font-size:12px;'>...and {len(movie_list) - 20} more</span>"
            return movies_text
    
        genre_movies = (
            df_genres_exploded
            .groupby('Genre')
            .agg({'Name': lambda x: sorted(set(x)), 'Genre': 'count'})
            .rename(columns={'Genre': 'Number of movie', 'Name': 'Movies'})
            .reset_index()
            .sort_values('Number of movie', ascending=False)
        )
        genre_movies['MoviesText'] = genre_movies['Movies'].apply(make_movies_text)

        return self.graph_maker.graph_genre(genre_movies)
    
    def actor(self, key):
        match key:
            case "watched":
                nb_actor = self.watched_df['Actors'].dropna().str.split(', ').explode().value_counts().head(25).reset_index()
            case "watchlist":
                nb_actor = self.watchlist_df['Actors'].dropna().str.split(', ').explode().value_counts().head(25).reset_index()
        nb_actor.columns = ['Actors', 'Number of Movies']
        return self.graph_maker.graph_actor(nb_actor)

    def director(self, key):
        match key:
            case "watched":
                nb_real = self.watched_df['Director'].dropna().str.split(', ').explode().value_counts().head(25).reset_index()
            case "watchlist":
                nb_real = self.watchlist_df['Director'].dropna().str.split(', ').explode().value_counts().head(25).reset_index()
        nb_real.columns = ['Director', 'Number of Movies']
        return self.graph_maker.graph_director(nb_real)

    def famous(self, key):
        match key:
            case "watched":
                movies_rating = self.watched_df.copy()
            case "watchlist":
                movies_rating = self.watchlist_df.copy()
        movies_rating['imdbVotes'] = movies_rating['imdbVotes'].replace("N/A", np.nan)
        movies_rating['imdbVotes'] = movies_rating['imdbVotes'].replace("", np.nan)
        movies_rating = movies_rating.dropna(subset=['imdbVotes'])
        movies_rating['imdbVotes'] = movies_rating['imdbVotes'].astype(str).str.replace(',', '')
        movies_rating['imdbVotes'] = movies_rating['imdbVotes'].astype(float)
        bottom_5_votes = movies_rating.sort_values(by='imdbVotes', ascending=True).head(10)
        bottom = bottom_5_votes[['Title', 'imdbVotes']].reset_index(drop=True)
        top_5_votes = movies_rating.sort_values(by='imdbVotes', ascending=False).head(10)
        top = top_5_votes[['Title', 'imdbVotes']].reset_index(drop=True)
        return bottom, top
    
    def cinephile(self, key):
        match key:
            case "watched":
                habit = self.watched_df.copy()
            case "watchlist":
                habit = self.watchlist_df.copy()
        result = compute_categories(self.all_movies, habit)
        return self.graph_maker.graph_cinephile(result)

    def decade(self, key):
        match key:
            case "watched":
                years = self.watched_df['Year'].dropna().explode()
            case "watchlist":
                years = self.watchlist_df['Year'].dropna().explode()
        years = years.astype(int)

        years = pd.cut(years, bins=[1900, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020, 2025], 
                    labels=['1900-1950', '1951-1960', '1961-1970', '1971-1980', '1981-1990', 
                            '1991-2000', '2001-2010', '2011-2020', '2021-2025'])
        years = years.value_counts().reset_index()
        years.columns = ['Year', 'Number of Movies']

        years = years.sort_values(by='Year')

        return self.graph_maker.graph_decade(years)
    
    def runtime_bar(self, key):
        match key:
            case "watched":
                df = self.watched_df.copy()
            case "watchlist":
                df = self.watchlist_df.copy()
        df['Runtime']=df['Runtime'].str.split(' ').str[0]
        df = df[df['Runtime'].notna() & ~df['Runtime'].str.contains('s', case=False, na=True)] #remove the runtime in seconde
        df['Runtime'] = df['Runtime'].apply(lambda x: int(x) if x not in ['', 'N/A'] else None)
        df = df[(df['Runtime'] >= 20) & (df['Runtime'] <= 230)]
        bins = list(range(20, 241, 10))  # 20 to 240 by 10
        labels = [f'{i}-{i+9}' for i in bins[:-1]]
        df['RuntimeBin'] = pd.cut(df['Runtime'], bins=bins, labels=labels, right=True, include_lowest=True)
        runtime_counts = df['RuntimeBin'].value_counts().sort_index().reset_index()
        runtime_counts.columns = ['RuntimeBin', 'Count']
        return self.graph_maker.graph_runtime_bar(runtime_counts)

    def mapW(self, key):
        match key:
            case "watched":
                df_country = self.watched_df.copy()
            case "watchlist":
                df_country = self.watchlist_df.copy()
        df_country['Country'] = df_country['Country'].dropna().str.split(', ')
        df_genres_exploded = df_country.explode('Country')
        genre_counts = df_genres_exploded['Country'].value_counts().reset_index()
        countries = {country.name: country.alpha_3 for country in pycountry.countries}
        genre_counts['code'] = genre_counts['Country'].map(countries)
        return self.graph_maker.graph_mapW(genre_counts)

    def diff_rating(self):
        sur_note = self.rating_df.sort_values(by=['diff_rating'],ascending=False)
        sur_note = sur_note.head(10).reset_index(drop=True)

        sous_note = self.rating_df.sort_values(by=['diff_rating'])
        sous_note = sous_note.head(10).reset_index(drop=True)
        return sur_note[['Name','Rating','imdbRating','diff_rating']], sous_note[['Name','Rating','imdbRating','diff_rating']]
    
    def rating_director(self):
        nb_real = self.rating_df['Director'].value_counts().head(25)
        df_top_directors = self.rating_df[self.rating_df['Director'].isin(nb_real.index)]
        nb_films_par_director = df_top_directors['Director'].value_counts().reset_index()
        nb_films_par_director.columns = ['Director', 'Number of movie']
        mean_rating = df_top_directors.groupby('Director')['Rating'].mean().rename('Moyenne_Rating').reset_index()
        mean_rating.columns = ['Director', 'Moyenne_Rating']
        df_plot = pd.merge(nb_films_par_director, mean_rating, on='Director')
        return self.graph_maker.graph_rating_director(df_plot, nb_films_par_director)

    def rating_actor(self):
        nb_actor = self.rating_df['Actors'].dropna().str.split(', ').explode().value_counts().head(25)
        top_actors = nb_actor.index

        df_exploded = self.rating_df.dropna(subset=['Actors']).copy()
        df_exploded['Actor'] = df_exploded['Actors'].str.split(', ')
        df_exploded = df_exploded.explode('Actor')

        df_top_actors = df_exploded[df_exploded['Actor'].isin(top_actors)]

        nb_films_par_actor = df_top_actors['Actor'].value_counts().reset_index()
        nb_films_par_actor.columns = ['Actor', 'Nb_Films']

        mean_rating_actor = df_top_actors.groupby('Actor')['Rating'].mean().reset_index()
        mean_rating_actor.columns = ['Actor', 'Moyenne_Rating']

        df_actor_plot = pd.merge(nb_films_par_actor, mean_rating_actor, on='Actor')
        return self.graph_maker.graph_rating_actor(df_actor_plot)

    def genre_rating(self):
        rating_local=self.rating_df.copy()
        rating_local['Genre'] = rating_local['Genre'].dropna().str.split(', ')
        df_genres_exploded = rating_local.explode('Genre')
        genre_counts = df_genres_exploded['Genre'].value_counts().reset_index()
        genre_counts.columns = ['Genre', 'Nombre de films']

        mean_rating_genre = df_genres_exploded.groupby('Genre')['Rating'].mean().reset_index()
        mean_rating_genre.columns = ['Genre', 'Moyenne_Rating']

        df_genre_plot = pd.merge(genre_counts, mean_rating_genre, on='Genre')
        return self.graph_maker.graph_genre_rating(df_genre_plot)

    def comparaison_rating(self):
        # Groupby pour compter les valeurs dans 'Rating'
        rate = self.rating_df.copy()
        rate['imdbRating'] = pd.to_numeric(rate['imdbRating'], errors='coerce')
        rate = rate.dropna(subset=['imdbRating'])
        rate['imdbRating'] = (rate['imdbRating'] * 2).round() / 2
        rate = rate.groupby('imdbRating').size().reset_index(name='Number of movie')
        return self.graph_maker.graph_comparaison_rating(rate, self.rating_df)

    # TODO: séparer la logique de génération de wordcloud
    def generate_wordcloud(self):
        if not self.corpus.empty:
            stopwords = set(get_stop_words('fr')) | set(get_stop_words('en'))
            wordcloud = WordCloud(stopwords=stopwords,width=800, height=400, background_color="black",max_words=120)
            text = " ".join(self.corpus)
            wc=wordcloud.generate(text)
            return self.graph_maker.graph_generate_wordcloud(wc)